from __future__ import annotations

from threading import RLock
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from .protocol import QuarantineRecord, ReservationResult, StoredEnvelope
from .tables import metadata, outbound_attempts, proposals, quarantines, rate_counters, raw_envelopes, reservations


class SqlEdgeStore:
    """SQLAlchemy store. Callers own the engine; production schema is migration-owned."""

    def __init__(self, engine, *, create_schema: bool = False, quarantine_available: bool = True):
        self.engine = engine
        self.quarantine_available = quarantine_available
        self._lock = RLock()
        if create_schema:
            metadata.create_all(engine)

    def consume_rate(self, budget: str, key: str, limit: int) -> tuple[bool, int]:
        with self._lock, self.engine.begin() as conn:
            row = conn.execute(select(rate_counters.c.count).where(rate_counters.c.budget == budget, rate_counters.c.counter_key == key)).scalar_one_or_none()
            count = int(row or 0)
            if count >= limit:
                return False, count
            if row is None:
                conn.execute(insert(rate_counters).values(budget=budget, counter_key=key, count=1))
            else:
                conn.execute(update(rate_counters).where(rate_counters.c.budget == budget, rate_counters.c.counter_key == key).values(count=count + 1))
            return True, count + 1

    def reserve(self, envelope: StoredEnvelope) -> ReservationResult:
        values=envelope.__dict__.copy(); values.pop("tombstoned");
        with self._lock, self.engine.begin() as conn:
            prior=conn.execute(select(reservations).where(reservations.c.channel==envelope.channel,reservations.c.external_id==envelope.external_id)).mappings().first()
            if prior and prior["payload_digest"]==envelope.payload_digest:
                return ReservationResult("DUPLICATE", self.get_envelope(prior["envelope_id"]), prior["envelope_id"])
            try: conn.execute(insert(raw_envelopes).values(**values))
            except IntegrityError as exc: raise ValueError("AEAD nonce already used for key") from exc
            if prior:
                if not self.quarantine_available: raise RuntimeError("quarantine sink unavailable")
                q=QuarantineRecord(str(uuid4()),envelope.envelope_id,"KEY_COLLISION",prior["envelope_id"])
                conn.execute(insert(quarantines).values(**q.__dict__))
                return ReservationResult("COLLISION",envelope,prior["envelope_id"],q)
            conn.execute(insert(reservations).values(channel=envelope.channel,external_id=envelope.external_id,payload_digest=envelope.payload_digest,envelope_id=envelope.envelope_id))
            return ReservationResult("NEW",envelope)

    def quarantine(self,envelope_id:str,reason:str,*,original_envelope_id:str|None=None)->QuarantineRecord:
        if not self.quarantine_available: raise RuntimeError("quarantine sink unavailable")
        q=QuarantineRecord(str(uuid4()),envelope_id,reason,original_envelope_id)
        with self.engine.begin() as conn: conn.execute(insert(quarantines).values(**q.__dict__))
        return q

    def save_proposal(self,proposal:dict[str,Any])->None:
        value={"proposal_id":str(proposal["proposal_id"]),"envelope_id":proposal["envelope_id"],"channel":proposal["channel"],"external_id":proposal["external_id"],"proposal_json":proposal,"trust_class":"UNTRUSTED_EXTERNAL","content_class":"RAW"}
        with self.engine.begin() as conn: conn.execute(insert(proposals).values(**value))

    def save_outbound(self,receipt:dict[str,Any],prerequisite_digest:str)->None:
        value={"command_id":receipt["command_id"],"prerequisite_digest":prerequisite_digest,"outcome":receipt["outcome"],"reason":receipt.get("reason"),"delivery_id":receipt.get("delivery_id"),"delivery_attempts":receipt["delivery_attempts"],"receipt_json":receipt}
        with self.engine.begin() as conn: conn.execute(insert(outbound_attempts).values(**value))

    def tombstone(self,envelope_id:str)->None:
        from datetime import datetime,timezone
        with self.engine.begin() as conn: conn.execute(update(raw_envelopes).where(raw_envelopes.c.envelope_id==envelope_id).values(ciphertext=None,tag=None,tombstoned_at=datetime.now(timezone.utc)))

    def get_envelope(self,envelope_id:str)->StoredEnvelope|None:
        with self.engine.connect() as conn: row=conn.execute(select(raw_envelopes).where(raw_envelopes.c.envelope_id==envelope_id)).mappings().first()
        if not row:return None
        return StoredEnvelope(envelope_id=row["envelope_id"],channel=row["channel"],endpoint=row["endpoint"],external_id=row["external_id"],payload_digest=row["payload_digest"],key_id=row["key_id"],nonce=bytes(row["nonce"]),ciphertext=None if row["ciphertext"] is None else bytes(row["ciphertext"]),tag=None if row["tag"] is None else bytes(row["tag"]),aad=bytes(row["aad"]),tombstoned=row["tombstoned_at"] is not None)
