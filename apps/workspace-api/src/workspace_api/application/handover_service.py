"""Handover application service (P2A-HANDOVER-VERTICAL).

Three governed actions plus the freeze-readiness check `ShiftService.freeze`
consumes:

* create       — identity -> permission -> domain_lock(shift_handover) ->
                  derive server-owned snapshot -> persist aggregate/items/
                  evidence atomically -> audit. The caller supplies only
                  ``from_shift_id``/``to_shift_id`` (ADR section 3.2); items,
                  digests, status and actor identity are never caller input.
* review       — identity -> permission -> revalidate snapshot -> lifecycle
                  DRAFT->REVIEWED -> persist -> audit. The sender's step.
* acknowledge  — identity -> permission -> distinct receiver -> revalidate
                  snapshot -> lifecycle REVIEWED->ACKNOWLEDGED -> persist ->
                  audit. The receiver must differ from the reviewer.

``assert_freeze_ready`` is the real ``open_handover_items_linked`` freeze
prerequisite (ADR section 3.6): at least one ACKNOWLEDGED handover from the
shift whose source snapshot still exactly matches current open work.

Digest construction (SPEC R3) is canonical, UTF-8 JSON with sorted keys and
compact separators, hashed with SHA-256 - byte-identical across backends
because it only ever consumes already-reconstructed domain objects, never
raw SQL rows.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

from cvf_runtime.audit import AuditRecord
from cvf_runtime.domain_lock import assert_domain_allowed
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_handover_transition
from operations_domain.models import EvidenceRef, Handover, HandoverItem, HandoverStatus, RiskClass, ShiftStatus

_CREATE_CHAIN = ["identity", "permission", "domain_lock", "audit"]
_REVIEW_CHAIN = ["identity", "permission", "lifecycle", "audit"]
_ACKNOWLEDGE_CHAIN = ["identity", "permission", "lifecycle", "audit"]

_HANDOVER_DOMAIN = "shift_handover"
_RECORD_TYPE = "Handover"
_SOURCE_ORDER = ("Task", "CustomerRequest", "Incident")


def _iso(value) -> str | None:
    return value.astimezone(timezone.utc).isoformat() if value else None


def _evidence_payload(evidence) -> list[dict]:
    return sorted(
        (
            {
                "evidence_id": str(e.evidence_id),
                "source_type": e.source_type,
                "source_id": e.source_id,
                "sha256": e.sha256,
            }
            for e in evidence
        ),
        key=lambda e: (e["evidence_id"], e["source_type"], e["source_id"], e["sha256"] or ""),
    )


def _task_payload(task) -> dict:
    return {
        "record_type": "Task", "record_id": str(task.task_id), "shift_id": str(task.shift_id),
        "title": task.title, "description": task.description, "status": str(task.status),
        "owner_id": task.owner_id, "due_at": _iso(task.due_at), "risk_class": str(task.risk_class),
        "evidence": _evidence_payload(task.evidence),
    }


def _customer_request_payload(request) -> dict:
    return {
        "record_type": "CustomerRequest", "record_id": str(request.request_id),
        "shift_id": str(request.shift_id) if request.shift_id else None,
        "customer_id": request.customer_id, "summary": request.summary, "details": request.details,
        "status": str(request.status),
        "source_message_id": str(request.source_message_id) if request.source_message_id else None,
        "received_at": _iso(request.received_at), "promised_at": _iso(request.promised_at),
        "owner_id": request.owner_id, "risk_class": "R1",
    }


def _incident_payload(incident) -> dict:
    return {
        "record_type": "Incident", "record_id": str(incident.incident_id), "shift_id": str(incident.shift_id),
        "risk_class": str(incident.risk_class), "summary": incident.summary,
        "description": incident.description, "status": str(incident.status), "owner_id": incident.owner_id,
        "version": incident.version, "created_at": _iso(incident.created_at),
        "evidence": _evidence_payload(incident.evidence),
    }


_PAYLOAD_BUILDERS = {
    "Task": _task_payload, "CustomerRequest": _customer_request_payload, "Incident": _incident_payload,
}


def compute_source_digest(record_type: str, record) -> str:
    """SPEC R3: canonical UTF-8 JSON (sorted keys, compact separators), lowercase SHA-256 hex."""
    payload = _PAYLOAD_BUILDERS[record_type](record)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _clone_evidence(evidence) -> list:
    """Fresh EvidenceRef copies (new evidence_id) for the HandoverItem's own
    evidence_links rows - the source record's own evidence rows already own
    their evidence_id as that table's primary key, so a HandoverItem persisting
    the SAME evidence_id under a different (record_type, record_id) would
    collide on it. The digest itself still consumes the source's original
    evidence objects directly (see _task_payload/_incident_payload), never
    these clones - only persistence needs a distinct identity."""
    return [EvidenceRef(source_type=e.source_type, source_id=e.source_id, sha256=e.sha256) for e in evidence]


def _build_item(handover_id: UUID, record_type: str, record, digest: str) -> HandoverItem:
    if record_type == "Task":
        return HandoverItem(
            handover_id=handover_id, source_record_type=record_type, source_record_id=record.task_id,
            source_digest=digest, summary=record.title, owner_id=record.owner_id, due_at=record.due_at,
            risk_class=record.risk_class, evidence=_clone_evidence(record.evidence),
        )
    if record_type == "CustomerRequest":
        return HandoverItem(
            handover_id=handover_id, source_record_type=record_type, source_record_id=record.request_id,
            source_digest=digest, summary=record.summary, owner_id=record.owner_id,
            due_at=record.promised_at, risk_class=RiskClass.R1, evidence=[],
        )
    return HandoverItem(
        handover_id=handover_id, source_record_type=record_type, source_record_id=record.incident_id,
        source_digest=digest, summary=record.summary, owner_id=record.owner_id, due_at=None,
        risk_class=record.risk_class, evidence=_clone_evidence(record.evidence),
    )


def _current_items(ledger: Ledger, shift_id: UUID, handover_id: UUID, *, unit=None) -> list[HandoverItem]:
    snapshot = ledger.open_work_snapshot(shift_id, unit=unit)
    items: list[HandoverItem] = []
    for record_type in _SOURCE_ORDER:
        for record in snapshot.get(record_type, []):
            digest = compute_source_digest(record_type, record)
            items.append(_build_item(handover_id, record_type, record, digest))
    return items


def _membership(items) -> set[tuple[str, str, str]]:
    return {(i.source_record_type, str(i.source_record_id), i.source_digest) for i in items}


def _assert_snapshot_matches(ledger: Ledger, handover: Handover, *, unit=None) -> None:
    current = _current_items(ledger, handover.from_shift_id, handover.handover_id, unit=unit)
    if _membership(current) != _membership(handover.items):
        raise CvfDenied(
            control="lifecycle",
            reason="handover source snapshot no longer matches current open work; create a new draft",
            http_status=409,
        )


def _assert_shift_pair_ready(from_shift, to_shift) -> None:
    if from_shift.status == ShiftStatus.FROZEN:
        raise CvfDenied(control="freeze", reason="source shift is frozen", http_status=409)
    if to_shift.status != ShiftStatus.OPEN:
        raise CvfDenied(
            control="lifecycle",
            reason=f"destination shift is {to_shift.status}, expected OPEN",
            http_status=409,
        )


def assert_freeze_ready(ledger: Ledger, shift_id: UUID, *, unit=None) -> None:
    """The real `open_handover_items_linked` freeze prerequisite (ADR 3.6):
    at least one ACKNOWLEDGED handover from ``shift_id`` whose destination
    shift is still OPEN and whose source snapshot still exactly matches
    current mandatory open work - both rechecked here, not trusted from
    acknowledgement time (ADR 3.4: a state change invalidates readiness).
    Never overridable - the report-approved override covers only
    `report_approved`."""
    for handover in ledger.list_handovers_for_shift(shift_id, unit=unit):
        if handover.status != HandoverStatus.ACKNOWLEDGED:
            continue
        try:
            destination = ledger.get_shift(handover.to_shift_id, unit=unit)
        except KeyError:
            continue
        if destination.status != ShiftStatus.OPEN:
            continue
        current = _current_items(ledger, shift_id, handover.handover_id, unit=unit)
        if _membership(current) == _membership(handover.items):
            return
    raise CvfDenied(
        control="freeze",
        reason=(
            "freeze requires an ACKNOWLEDGED handover whose source snapshot exactly "
            "matches current open work (open_handover_items_linked)"
        ),
        http_status=409,
    )


class HandoverService:
    def __init__(self, ledger: Ledger, profile: CvfProfile | None = None):
        self.ledger = ledger
        self.profile = profile or load_profile()

    def create(self, from_shift_id: UUID, to_shift_id: UUID, principal: Principal) -> Handover:
        require_action(principal, "handover.create")
        assert_domain_allowed(self.profile, _HANDOVER_DOMAIN)
        if from_shift_id == to_shift_id:
            raise CvfDenied(control="lifecycle", reason="from_shift_id and to_shift_id must differ", http_status=409)

        with self.ledger.transaction() as unit:
            from_shift = self.ledger.get_shift(from_shift_id, unit=unit)
            to_shift = self.ledger.get_shift(to_shift_id, unit=unit)
            _assert_shift_pair_ready(from_shift, to_shift)

            handover = Handover(from_shift_id=from_shift_id, to_shift_id=to_shift_id, created_by=principal.user_id)
            handover.items = _current_items(self.ledger, from_shift_id, handover.handover_id, unit=unit)

            stored = self.ledger.add_handover(handover, unit=unit)
            self._audit(principal, "handover.create", stored.handover_id, _CREATE_CHAIN, None, str(stored.status), unit=unit)
        return stored

    def review(self, handover_id: UUID, principal: Principal) -> Handover:
        with self.ledger.transaction() as unit:
            handover = self.ledger.get_handover(handover_id, unit=unit)
            require_action(principal, "handover.review")
            _assert_shift_pair_ready(
                self.ledger.get_shift(handover.from_shift_id, unit=unit),
                self.ledger.get_shift(handover.to_shift_id, unit=unit),
            )
            if handover.status != HandoverStatus.DRAFT:
                raise CvfDenied(control="lifecycle", reason=f"handover is {handover.status}, expected DRAFT", http_status=409)
            assert_handover_transition(handover.status, HandoverStatus.REVIEWED)
            _assert_snapshot_matches(self.ledger, handover, unit=unit)

            before = str(handover.status)
            handover.status = HandoverStatus.REVIEWED
            handover.reviewed_by = principal.user_id
            handover.reviewed_at = datetime.now(timezone.utc)
            handover.version += 1

            stored = self.ledger.put_handover(handover, unit=unit)
            self._audit(principal, "handover.review", handover_id, _REVIEW_CHAIN, before, str(stored.status), unit=unit)
        return stored

    def acknowledge(self, handover_id: UUID, principal: Principal) -> Handover:
        with self.ledger.transaction() as unit:
            handover = self.ledger.get_handover(handover_id, unit=unit)
            require_action(principal, "handover.acknowledge")
            if handover.reviewed_by is not None and handover.reviewed_by == principal.user_id:
                raise CvfDenied(control="lifecycle", reason="receiver must differ from reviewer", http_status=409)
            _assert_shift_pair_ready(
                self.ledger.get_shift(handover.from_shift_id, unit=unit),
                self.ledger.get_shift(handover.to_shift_id, unit=unit),
            )
            if handover.status != HandoverStatus.REVIEWED:
                raise CvfDenied(control="lifecycle", reason=f"handover is {handover.status}, expected REVIEWED", http_status=409)
            assert_handover_transition(handover.status, HandoverStatus.ACKNOWLEDGED)
            _assert_snapshot_matches(self.ledger, handover, unit=unit)

            before = str(handover.status)
            handover.status = HandoverStatus.ACKNOWLEDGED
            handover.received_by = principal.user_id
            handover.acknowledged_at = datetime.now(timezone.utc)
            handover.version += 1

            stored = self.ledger.put_handover(handover, unit=unit)
            self._audit(principal, "handover.acknowledge", handover_id, _ACKNOWLEDGE_CHAIN, before, str(stored.status), unit=unit)
        return stored

    def _audit(self, principal, action, record_id, chain, before, after, *, unit=None) -> None:
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action=action,
                record_type=_RECORD_TYPE,
                record_id=str(record_id),
                control_chain=chain,
                before_state=before,
                after_state=after,
            ),
            unit=unit,
        )
