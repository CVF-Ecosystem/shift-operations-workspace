"""Deterministic Report snapshot/digest engine (P2R-OPERATIONAL-REPORT-
FREEZE-PREREQUISITE).

The single R3-R9 source-selection/normalization/digest/limit implementation
used at generate/submit-review/approve/freeze (WO section 3.4). Digest
construction (SPEC R7) is canonical, UTF-8 JSON with sorted keys and compact
separators, hashed with SHA-256 - byte-identical across backends because it
only ever consumes already-reconstructed domain objects, never raw SQL rows
(the same idiom ``handover_service.compute_source_digest`` established).

``build_snapshot`` is pure with respect to persistence: it takes already-read
domain objects and returns a ``ReportContent`` plus the exact
``ReportSourceRef`` manifest. Callers (``report_service``/``report_freeze``)
own reading fresh state from the ledger and passing it in - this module never
talks to the ledger itself, so it stays trivially unit-testable and there is
exactly one place per state family that decides membership/order/encoding.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

from cvf_runtime.errors import CvfDenied

from operations_domain.models import ReportContent, ReportSection, ReportSourceRef

SCHEMA_VERSION = "1.0"
REPORT_TYPE = "END_SHIFT"

# SPEC R3: exactly six entries, this fixed order.
_SECTION_ORDER = (
    "operational_events",
    "corrections",
    "tasks",
    "customer_requests",
    "incidents",
    "handovers",
)

# SPEC R8: fail-closed limits. Overflow is a defect, not a truncation.
_MAX_RECORDS_PER_SECTION = 500
_MAX_CONTENT_BYTES = 2_097_152

# SPEC R6: only these OperationalEvent states are eligible.
_EVENT_INCLUDED_STATES = {"CONFIRMED", "CORRECTED", "FROZEN"}


def _iso(value) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


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


def _event_payload(event) -> dict:
    return {
        "record_type": "OperationalEvent", "record_id": str(event.event_id),
        "shift_id": str(event.shift_id), "event_type": event.event_type, "title": event.title,
        "description": event.description, "risk_class": str(event.risk_class), "state": str(event.state),
        "starts_at": _iso(event.starts_at), "ends_at": _iso(event.ends_at), "owner_id": event.owner_id,
        "version": event.version, "evidence": _evidence_payload(event.evidence),
    }


def _correction_payload(correction) -> dict:
    return {
        "record_type": "Correction", "record_id": str(correction.correction_id),
        "target_record_type": correction.record_type, "target_record_id": str(correction.record_id),
        "reason": correction.reason, "requested_by": correction.requested_by,
        "previous_version": correction.previous_version, "new_version": correction.new_version,
        "created_at": _iso(correction.created_at),
    }


def _task_payload(task) -> dict:
    return {
        "record_type": "Task", "record_id": str(task.task_id), "shift_id": str(task.shift_id),
        "title": task.title, "description": task.description, "status": str(task.status),
        "owner_id": task.owner_id, "due_at": _iso(task.due_at), "risk_class": str(task.risk_class),
        "state": str(task.state), "version": task.version, "created_at": _iso(task.created_at),
        "evidence": _evidence_payload(task.evidence),
    }


def _customer_request_payload(request) -> dict:
    return {
        "record_type": "CustomerRequest", "record_id": str(request.request_id),
        "customer_id": request.customer_id,
        "shift_id": str(request.shift_id) if request.shift_id else None,
        "summary": request.summary, "details": request.details, "status": str(request.status),
        "source_message_id": str(request.source_message_id) if request.source_message_id else None,
        "received_at": _iso(request.received_at), "promised_at": _iso(request.promised_at),
        "owner_id": request.owner_id,
    }


def _incident_payload(incident) -> dict:
    return {
        "record_type": "Incident", "record_id": str(incident.incident_id), "shift_id": str(incident.shift_id),
        "risk_class": str(incident.risk_class), "summary": incident.summary,
        "description": incident.description, "status": str(incident.status), "owner_id": incident.owner_id,
        "version": incident.version, "created_at": _iso(incident.created_at),
        "evidence": _evidence_payload(incident.evidence),
    }


def _handover_item_payload(item) -> dict:
    return {
        "item_id": str(item.item_id), "source_record_type": item.source_record_type,
        "source_record_id": str(item.source_record_id), "source_digest": item.source_digest,
        "summary": item.summary, "owner_id": item.owner_id, "due_at": _iso(item.due_at),
        "risk_class": str(item.risk_class), "evidence": _evidence_payload(item.evidence),
    }


def _handover_payload(handover) -> dict:
    return {
        "record_type": "Handover", "record_id": str(handover.handover_id),
        "from_shift_id": str(handover.from_shift_id), "to_shift_id": str(handover.to_shift_id),
        "status": str(handover.status), "created_by": handover.created_by,
        "reviewed_by": handover.reviewed_by, "reviewed_at": _iso(handover.reviewed_at),
        "received_by": handover.received_by, "acknowledged_at": _iso(handover.acknowledged_at),
        "version": handover.version, "created_at": _iso(handover.created_at),
        "items": [_handover_item_payload(i) for i in handover.items],
    }


_PAYLOAD_BUILDERS = {
    "OperationalEvent": _event_payload,
    "Correction": _correction_payload,
    "Task": _task_payload,
    "CustomerRequest": _customer_request_payload,
    "Incident": _incident_payload,
    "Handover": _handover_payload,
}

_VERSIONED_TYPES = {"OperationalEvent", "Task", "Incident", "Handover"}


def compute_source_digest(record_type: str, record) -> str:
    """SPEC R7: canonical UTF-8 JSON (sorted keys, compact separators),
    lowercase SHA-256 hex - the same idiom every vertical in this repo uses."""
    payload = _PAYLOAD_BUILDERS[record_type](record)
    return _sha256(payload)


def _source_ref(record_type: str, record_id: UUID, digest: str, *, version: int | None) -> ReportSourceRef:
    return ReportSourceRef(
        record_type=record_type,
        record_id=record_id,
        source_version=version if record_type in _VERSIONED_TYPES else None,
        source_digest=digest,
    )


def _section(section_type: str, record_type: str, records: list, *, id_attr: str, version_attr: str | None) -> tuple[ReportSection, list[ReportSourceRef]]:
    if len(records) > _MAX_RECORDS_PER_SECTION:
        raise CvfDenied(
            control="lifecycle",
            reason=(
                f"section {section_type!r} has {len(records)} records, "
                f"exceeding the maximum of {_MAX_RECORDS_PER_SECTION}"
            ),
            http_status=422,
        )
    payloads: list[dict] = []
    manifest: list[ReportSourceRef] = []
    for record in records:
        payload = _PAYLOAD_BUILDERS[record_type](record)
        digest = _sha256(payload)
        payloads.append(payload)
        record_id = getattr(record, id_attr)
        version = getattr(record, version_attr) if version_attr else None
        manifest.append(_source_ref(record_type, record_id, digest, version=version))
    return ReportSection(section_type=section_type, records=payloads), manifest


def build_snapshot(
    *,
    shift_id: UUID,
    events: list,
    corrections: list,
    tasks: list,
    customer_requests: list,
    incidents: list,
    handovers: list,
) -> ReportContent:
    """Builds the strict SPEC R2-R4 ``ReportContent`` from already-read,
    already-filtered domain objects. Callers own filtering
    (`_EVENT_INCLUDED_STATES` membership, corrections-for-included-events,
    shift-bound task/request/incident/handover selection) and ordering
    (R7's exact per-type sort key) BEFORE calling this - this function only
    serializes/hashes/limits what it is given, so a caller passing an
    unfiltered or unordered list produces a wrong-but-deterministic digest,
    never a silently "corrected" one."""
    sections: list[ReportSection] = []
    manifest: list[ReportSourceRef] = []

    section_specs = (
        ("operational_events", "OperationalEvent", events, "event_id", "version"),
        ("corrections", "Correction", corrections, "correction_id", None),
        ("tasks", "Task", tasks, "task_id", "version"),
        ("customer_requests", "CustomerRequest", customer_requests, "request_id", None),
        ("incidents", "Incident", incidents, "incident_id", "version"),
        ("handovers", "Handover", handovers, "handover_id", "version"),
    )
    for section_type, record_type, records, id_attr, version_attr in section_specs:
        section, refs = _section(section_type, record_type, records, id_attr=id_attr, version_attr=version_attr)
        sections.append(section)
        manifest.extend(refs)

    seen: set[tuple[str, str]] = set()
    for ref in manifest:
        key = (ref.record_type, str(ref.record_id))
        if key in seen:
            raise CvfDenied(control="lifecycle", reason=f"duplicate source manifest entry: {key}", http_status=422)
        seen.add(key)

    digest = _sha256({
        "schema_version": SCHEMA_VERSION, "shift_id": str(shift_id), "report_type": REPORT_TYPE,
        "sections": [s.model_dump(mode="json") for s in sections],
        "source_manifest": [m.model_dump(mode="json") for m in manifest],
    })
    content = ReportContent(schema_version=SCHEMA_VERSION, sections=sections, source_manifest=manifest, snapshot_digest=digest)
    size = len(_canonical_bytes(content.model_dump(mode="json")))
    if size > _MAX_CONTENT_BYTES:
        raise CvfDenied(control="lifecycle", reason=f"serialized report content is {size} bytes, exceeding the maximum of {_MAX_CONTENT_BYTES}", http_status=422)
    return content


def filter_eligible_events(events: list) -> list:
    """SPEC R6: only CONFIRMED/CORRECTED/FROZEN OperationalEvents are
    included; RAW/NORMALIZED/PROPOSED/REJECTED are excluded."""
    return [e for e in events if str(e.state) in _EVENT_INCLUDED_STATES]


def filter_corrections_for_events(corrections: list, event_ids: set[UUID]) -> list:
    """SPEC R6: every Correction whose record_id is an included
    OperationalEvent id - corrections for excluded/other-type records never
    enter the report."""
    return [c for c in corrections if c.record_type == "OperationalEvent" and c.record_id in event_ids]


def sort_events(events: list) -> list:
    return sorted(events, key=lambda e: (e.starts_at is None, e.starts_at or datetime.min.replace(tzinfo=timezone.utc), str(e.event_id)))


def sort_corrections(corrections: list) -> list:
    return sorted(corrections, key=lambda c: (c.created_at, str(c.correction_id)))


def sort_tasks(tasks: list) -> list:
    return sorted(tasks, key=lambda t: (t.created_at, str(t.task_id)))


def sort_customer_requests(requests: list) -> list:
    return sorted(requests, key=lambda r: (r.received_at, str(r.request_id)))


def sort_incidents(incidents: list) -> list:
    return sorted(incidents, key=lambda i: (i.created_at, str(i.incident_id)))


def sort_handovers(handovers: list) -> list:
    return sorted(handovers, key=lambda h: (h.created_at, str(h.handover_id)))
