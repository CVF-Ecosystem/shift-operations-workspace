"""Row <-> domain-model mappers for P4-E identity/conversation-routing.

Split out of ``p4e_store.py`` for the same reason ``_rows.py`` is split out
of ``sql_ledger.py`` (file-size guard, one obvious place per domain).
Unlike every other ``_rows``/``*_records`` mapper, these ``row_to_*``
functions import ``identity_mapping``/``conversation_routing`` directly
rather than taking an injected ``models`` namespace: those two packages are
provider-neutral P4-E owners, not the ``workspace_api.domain.models`` shim
(SPEC R18 - Operations Ledger owns persistence only and never becomes a
second contract owner for their result types).

SQLite's ``DateTime(timezone=True)`` column type does not round-trip
``tzinfo`` (the driver always returns a naive value); every timestamp is
stored as UTC by SPEC R19's injected-clock discipline, so ``_utc`` reattaches
UTC on read rather than weakening the model's own aware-timestamp contract."""

from __future__ import annotations

from datetime import timezone


def _utc(value):
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _parse_received_at(value):
    """``sender_evidence`` arrives here as the JSON-mode dump of a closed
    Pydantic model (persisted as JSON/JSONB), so ``received_at`` is an ISO
    string, not a ``datetime`` - unlike every other row builder in this
    module, which receives live model instances. Accept either shape."""
    from datetime import datetime as _dt

    if isinstance(value, str):
        return _dt.fromisoformat(value)
    return value


def observation_row(observation) -> dict:
    return {
        "observation_id": observation.observation_id,
        "external_key_digest": observation.external_key_digest,
        "workspace_digest": observation.workspace_digest,
        "endpoint_id": observation.endpoint_id,
        "channel_id": observation.channel_id,
        "provider_account_digest": observation.provider_account_digest,
        "subject_kind": observation.subject_kind,
        "extraction_policy_id": observation.extraction_policy_id,
        "extraction_policy_version": observation.extraction_policy_version,
        "raw_envelope_id": observation.raw_envelope_id,
        "external_message_id": observation.external_message_id,
        "received_at": observation.received_at,
    }


def row_to_observation(row):
    from identity_mapping import SenderObservationV1

    return SenderObservationV1(
        observation_id=row["observation_id"],
        external_key_digest=row["external_key_digest"],
        workspace_digest=row["workspace_digest"],
        endpoint_id=row["endpoint_id"],
        channel_id=row["channel_id"],
        provider_account_digest=row["provider_account_digest"],
        subject_kind=row["subject_kind"],
        extraction_policy_id=row["extraction_policy_id"],
        extraction_policy_version=row["extraction_policy_version"],
        raw_envelope_id=row["raw_envelope_id"],
        external_message_id=row["external_message_id"],
        received_at=_utc(row["received_at"]),
    )


def mapping_row(mapping, *, is_current: bool) -> dict:
    return {
        "mapping_id": mapping.mapping_id,
        "external_key_digest": mapping.external_key_digest,
        "target_kind": str(mapping.target_kind),
        "target_user_id": mapping.target_user_id,
        "proposal_evidence_digest": mapping.proposal_evidence_digest,
        "proposer_id": mapping.proposer_id,
        "status": str(mapping.status),
        "version": mapping.version,
        "created_at": mapping.created_at,
        "updated_at": mapping.updated_at,
        "confirmer_id": mapping.confirmer_id,
        "rejector_id": mapping.rejector_id,
        "revoker_id": mapping.revoker_id,
        "successor_mapping_id": mapping.successor_mapping_id,
        "predecessor_mapping_id": mapping.predecessor_mapping_id,
        "is_current": is_current,
    }


def row_to_mapping(row):
    from identity_mapping import IdentityMappingV1

    return IdentityMappingV1(
        mapping_id=row["mapping_id"],
        external_key_digest=row["external_key_digest"],
        target_user_id=row["target_user_id"],
        proposal_evidence_digest=row["proposal_evidence_digest"],
        proposer_id=row["proposer_id"],
        status=row["status"],
        version=row["version"],
        created_at=_utc(row["created_at"]),
        updated_at=_utc(row["updated_at"]),
        confirmer_id=row["confirmer_id"],
        rejector_id=row["rejector_id"],
        revoker_id=row["revoker_id"],
        successor_mapping_id=row["successor_mapping_id"],
        predecessor_mapping_id=row["predecessor_mapping_id"],
    )


def binding_row(binding, *, is_current: bool) -> dict:
    return {
        "binding_id": binding.binding_id,
        "mapping_id": binding.mapping_id,
        "mapping_version": binding.mapping_version,
        "target_kind": str(binding.target_kind),
        "target_id": binding.target_id,
        "target_version": binding.target_version,
        "creator_id": binding.creator_id,
        "status": str(binding.status),
        "version": binding.version,
        "created_at": binding.created_at,
        "successor_binding_id": binding.successor_binding_id,
        "is_current": is_current,
    }


def row_to_binding(row):
    from conversation_routing import RouteBindingV1

    return RouteBindingV1(
        binding_id=row["binding_id"],
        mapping_id=row["mapping_id"],
        mapping_version=row["mapping_version"],
        target_kind=row["target_kind"],
        target_id=row["target_id"],
        target_version=row["target_version"],
        creator_id=row["creator_id"],
        status=row["status"],
        version=row["version"],
        created_at=_utc(row["created_at"]),
        successor_binding_id=row["successor_binding_id"],
    )


def insert_proposal_admission(c, proposal: dict, lineage_digest: str, *, uuid4):
    """SPEC R11/completion-review F3: the transaction-A insert body -
    proposal row, derived observation when sender evidence is present, and
    exactly one pending work item - factored out of ``p4e_store.py`` for
    the file-size guard. ``uuid4`` is passed in rather than imported here
    so this stays a pure persistence helper with no id-generation policy
    of its own."""
    from sqlalchemy import insert
    from sqlalchemy.exc import IntegrityError

    from operations_ledger.tables import external_identity_observations, p4e_placement_work, p4e_proposals

    try:
        c.execute(insert(p4e_proposals).values(**proposal, lineage_digest=lineage_digest))
    except IntegrityError as exc:
        raise ValueError("lineage collision: proposal/envelope identity reused") from exc
    if proposal.get("sender_evidence"):
        observation_row = observation_from_sender_evidence(str(uuid4()), proposal["sender_evidence"])
        try:
            c.execute(insert(external_identity_observations).values(**observation_row))
        except IntegrityError as exc:
            raise ValueError("duplicate observation lineage on proposal admission") from exc
    c.execute(insert(p4e_placement_work).values(
        work_item_id=str(uuid4()), proposal_id=proposal["proposal_id"],
        state="PENDING", attempt_count=0, version=1, lineage_digest=lineage_digest,
    ))


_KNOWN_WORK_STATES = ("PENDING", "CLAIMED", "COMPLETE")


def claimable_decision(row, *, now) -> str:
    """SPEC R12/completion-review F6: pure decision function factored out
    of ``p4e_store.py`` for the file-size guard. Returns ``"UNKNOWN_STATE"``
    (a state outside the closed PENDING/CLAIMED/COMPLETE set - never
    silently treated as claimable), ``"COMPLETE"`` (already terminal),
    ``"NOT_YET"`` (a fresh CLAIMED claim another processor still holds),
    ``"EXHAUSTED"`` (attempt_count already at the exact 3-attempt
    boundary - returned unclaimed, no version bump, so the caller's own
    exhaustion check fires deterministically), or ``"CLAIM"`` (PENDING, or
    a CLAIMED row stale for more than 5 minutes - claimable now)."""
    from datetime import timedelta

    if row["state"] not in _KNOWN_WORK_STATES:
        return "UNKNOWN_STATE"
    if row["state"] == "COMPLETE":
        return "COMPLETE"
    claimed_at = _utc(row["claimed_at"])
    stale = row["state"] == "CLAIMED" and claimed_at is not None and (now - claimed_at > timedelta(minutes=5))
    if row["state"] == "CLAIMED" and not stale:
        return "NOT_YET"
    if row["attempt_count"] >= 3:
        return "EXHAUSTED"
    return "CLAIM"


def proposal_lineage_digest(row: dict) -> str:
    """SPEC R11/completion-review F3: binds the COMPLETE non-disclosing
    semantic lineage of an admitted proposal - envelope, channel, external
    message id, candidate, provenance digest, and (when present) the
    closed sender-evidence object's own fields. Reuse of an idempotency
    key with any of these changed must be a lineage collision, not an
    idempotent replay. Sender evidence is already the closed, secret-free
    ``SenderEvidenceV1`` shape (no raw sender, no raw token-key bytes), so
    hashing its full field set discloses nothing beyond what that carrier
    already permits."""
    import hashlib
    import json

    canonical = {
        "envelope_id": row["envelope_id"],
        "channel": row["channel"],
        "external_id": row["external_id"],
        "candidate": row["candidate"],
        "provenance_digest": row["provenance_digest"],
        "sender_evidence": row.get("sender_evidence"),
    }
    body = json.dumps(canonical, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def decision_row(decision: dict) -> dict:
    """completion-rereview R3: filters a decision dict to only this
    table's actual columns - shared by every placement-work completion
    path so ``decision_count``/``work_complete`` receipt-only metadata is
    never sent to the INSERT."""
    from operations_ledger.tables import p4e_placement_decisions

    return {k: v for k, v in decision.items() if k in p4e_placement_decisions.c}


def observation_from_sender_evidence(observation_id: str, sender_evidence: dict):
    """SPEC R5/completion-review F3: derives the immutable
    SenderObservationV1 row from a persisted proposal's closed
    sender-evidence object, using identity_mapping's own key-digest
    function so the stored ``external_key_digest`` matches exactly what
    ``get_current_mapping``/resolution will later look up by."""
    from identity_mapping.models import ExternalIdentityKeyV1

    key = ExternalIdentityKeyV1(
        workspace_digest=sender_evidence["workspace_digest"],
        endpoint_id=sender_evidence["endpoint_id"],
        channel_id=sender_evidence["channel_id"],
        provider_account_digest=sender_evidence["provider_account_digest"],
        subject_kind=sender_evidence["subject_kind"],
        extraction_policy_id=sender_evidence["extraction_policy_id"],
        extraction_policy_version=sender_evidence["extraction_policy_version"],
        verification_scheme=sender_evidence["verification_scheme"],
        verification_version=sender_evidence["verification_version"],
        sender_token=sender_evidence["sender_token"],
        token_key_id=sender_evidence["token_key_id"],
        token_key_version=sender_evidence["token_key_version"],
    )
    return {
        "observation_id": observation_id,
        "external_key_digest": key.digest(),
        "workspace_digest": sender_evidence["workspace_digest"],
        "endpoint_id": sender_evidence["endpoint_id"],
        "channel_id": sender_evidence["channel_id"],
        "provider_account_digest": sender_evidence["provider_account_digest"],
        "subject_kind": sender_evidence["subject_kind"],
        "extraction_policy_id": sender_evidence["extraction_policy_id"],
        "extraction_policy_version": sender_evidence["extraction_policy_version"],
        "raw_envelope_id": sender_evidence["raw_envelope_id"],
        "external_message_id": sender_evidence["external_message_id"],
        "received_at": _parse_received_at(sender_evidence["received_at"]),
    }
