from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import ValidationError
from refinery_bridge.canonical import source_fingerprint
from refinery_bridge.enums import StageOutcome
from refinery_bridge.input_models import CandidateFingerprintV1, RefineryEnvelopeV1
from refinery_bridge.output_models import ContextCandidateV1, RefineryResultV1
from operations_domain.models import (
    CustomerRequest, DataState, Handover, HandoverStatus, Incident, IncidentStatus,
    Message, OperationalEvent, Report, ReportStatus, Task,
)

from .contract_models import (
    RetrievalContractInputV1, RetentionAssertionV1, VersionBindingV1,
)
from .enums import (
    NonAdmissionReason, RecordType, RetentionDisposition, TruthClass, VersionKind,
)
from .source_models import ProjectKnowledgeSourceV1


@dataclass(frozen=True)
class SourceFacts:
    record_type: RecordType
    record_id: str | None
    truth_class: TruthClass
    version: VersionBindingV1
    status: str
    shift_ids: tuple[str, ...]
    text: str
    digest: str | None


def p3a_binding_state(payload: Any) -> bool | None:
    """Return None for structural parse failure, else binding equality."""
    try:
        if isinstance(payload, RetrievalContractInputV1):
            envelope = payload.envelope
            result = payload.refinery_result
            candidate = payload.candidate
            fingerprint = payload.candidate_fingerprint
        else:
            envelope = RefineryEnvelopeV1.model_validate(payload.get("envelope"))
            result = RefineryResultV1.model_validate(payload.get("refinery_result"))
            candidate = ContextCandidateV1.model_validate(payload.get("candidate"))
            fingerprint = CandidateFingerprintV1.model_validate(
                payload.get("candidate_fingerprint")
            )
    except (ValidationError, ValueError, TypeError, UnicodeError):
        return None
    return (
        candidate == result.context_candidate
        and fingerprint == result.candidate_fingerprint
        and envelope.source_id == candidate.source_id
        and envelope.source_version == candidate.source_version
        and envelope.source_owner_id == candidate.source_owner_id == result.source_owner_id
        and envelope.source_link == candidate.source_link == result.source_link
        and envelope.source_fingerprint == candidate.source_fingerprint == result.source_fingerprint
        and source_fingerprint(envelope.raw_text) == envelope.source_fingerprint
        and all(receipt.outcome == StageOutcome.PASS for receipt in result.stage_receipts)
    )


def _is_utc(value: Any) -> bool:
    return (
        isinstance(value, datetime)
        and value.tzinfo is not None
        and value.utcoffset() == timezone.utc.utcoffset(value)
    )


def retention_issue(value: Any) -> NonAdmissionReason | None:
    if isinstance(value, RetentionAssertionV1):
        values = value.model_dump()
    elif isinstance(value, Mapping) and set(value) == set(RetentionAssertionV1.model_fields):
        values = value
    else:
        return None
    try:
        disposition = RetentionDisposition(values.get("disposition"))
    except (TypeError, ValueError):
        return None
    checked = values.get("checked_at_utc")
    expires = values.get("expires_at_utc")
    erased = values.get("erased_at_utc")
    if not _is_utc(checked) or (expires is not None and not _is_utc(expires)) \
            or (erased is not None and not _is_utc(erased)):
        return None
    if (disposition == RetentionDisposition.OWNER_NOT_FOUND
            or not values.get("owner_id")
            or not values.get("policy_version")
            or not values.get("source_evidence_id")):
        return NonAdmissionReason.RETENTION_OWNER_NOT_FOUND
    if disposition != RetentionDisposition.OWNER_ASSERTED_ACTIVE:
        return NonAdmissionReason.RETENTION_NOT_ACTIVE
    if erased is not None or (expires is not None and expires <= checked):
        return NonAdmissionReason.RETENTION_NOT_ACTIVE
    return None


def validation_payload(payload: Mapping[str, Any], issue):
    repaired = dict(payload)
    if issue is not None:
        raw = payload.get("retention")
        checked = raw.get("checked_at_utc") if isinstance(raw, Mapping) else None
        if not _is_utc(checked):
            return repaired
        repaired["retention"] = RetentionAssertionV1(
            disposition=RetentionDisposition.OWNER_ASSERTED_ACTIVE,
            owner_id="validation-only-owner",
            policy_version="validation-only-policy",
            checked_at_utc=checked,
            source_evidence_id="validation-only-evidence",
        )
    return repaired


def source_facts(value, selector: str) -> SourceFacts | NonAdmissionReason:
    canonical = TruthClass.CANONICAL_OPERATIONAL_RECORD
    integer = lambda version: VersionBindingV1(
        kind=VersionKind.INTEGER_VERSION, integer_version=version
    )
    if isinstance(value, OperationalEvent):
        if value.state not in {DataState.CONFIRMED, DataState.CORRECTED, DataState.FROZEN}:
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        facts = (RecordType.OPERATIONAL_EVENT, value.event_id, integer(value.version),
                 value.state.value, (str(value.shift_id),), value.title)
    elif isinstance(value, Task):
        if value.state not in {DataState.CONFIRMED, DataState.CORRECTED, DataState.FROZEN}:
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        facts = (RecordType.TASK, value.task_id, integer(value.version), value.state.value,
                 (str(value.shift_id),), value.title)
    elif isinstance(value, CustomerRequest):
        if value.shift_id is None:
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        facts = (RecordType.CUSTOMER_REQUEST, value.request_id, integer(value.version),
                 value.status.value, (str(value.shift_id),), value.summary)
    elif isinstance(value, Incident):
        allowed = {IncidentStatus.ACKNOWLEDGED, IncidentStatus.MITIGATING,
                   IncidentStatus.RESOLVED, IncidentStatus.CLOSED}
        if value.status not in allowed:
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        facts = (RecordType.INCIDENT, value.incident_id, integer(value.version),
                 value.status.value, (str(value.shift_id),), value.summary)
    elif isinstance(value, Handover):
        if value.status not in {HandoverStatus.REVIEWED, HandoverStatus.ACKNOWLEDGED}:
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        parts = selector.split("/")
        matches = [] if len(parts) != 3 or parts[0] != "items" or parts[2] != "summary" else [
            item for item in value.items if str(item.item_id) == parts[1]
        ]
        if len(matches) != 1:
            return NonAdmissionReason.SOURCE_PROJECTION_MISMATCH
        shifts = tuple(sorted((str(value.from_shift_id), str(value.to_shift_id))))
        facts = (RecordType.HANDOVER, value.handover_id, integer(value.version),
                 value.status.value, shifts, matches[0].summary)
    elif isinstance(value, Report):
        if value.status not in {ReportStatus.APPROVED, ReportStatus.FROZEN} or not value.is_current:
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        text = canonical_json_bytes(value.content.model_dump(mode="json")).decode("utf-8")
        facts = (RecordType.REPORT, value.report_id, integer(value.version), value.status.value,
                 (str(value.shift_id),), text)
    elif isinstance(value, Message):
        if value.source != "INTERNAL":
            return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
        version = VersionBindingV1(kind=VersionKind.UNVERSIONED)
        return SourceFacts(RecordType.MESSAGE, str(value.message_id),
                           TruthClass.ADVISORY_SOURCE_EVIDENCE, version, value.state.value,
                           (str(value.shift_id),), value.text, content_digest(value.text))
    elif isinstance(value, ProjectKnowledgeSourceV1):
        if value.source_pin != value.current_source_pin:
            return NonAdmissionReason.STALE_SOURCE
        version = VersionBindingV1(kind=VersionKind.SOURCE_VERSION_STRING,
                                   source_version_string=value.source_pin)
        return SourceFacts(RecordType.PROJECT_KNOWLEDGE, None,
                           TruthClass.ADVISORY_SOURCE_EVIDENCE, version, "CURRENT", (), "", None)
    else:
        return NonAdmissionReason.UNKNOWN_SOURCE_TYPE
    return SourceFacts(facts[0], str(facts[1]), canonical, facts[2], facts[3], facts[4], facts[5], None)


def expected_selector(record_type: RecordType, selector: str) -> bool:
    exact = {
        RecordType.OPERATIONAL_EVENT: "title", RecordType.TASK: "title",
        RecordType.CUSTOMER_REQUEST: "summary", RecordType.INCIDENT: "summary",
        RecordType.REPORT: "content", RecordType.MESSAGE: "text",
        RecordType.PROJECT_KNOWLEDGE: "document",
    }
    return selector.startswith("items/") if record_type == RecordType.HANDOVER else exact[record_type] == selector


def _json_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _json_value(value.model_dump(mode="json"))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, UUID):
        return str(value).lower()
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
            raise ValueError("UTC datetime required")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("NFC string required")
        return value
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        raise ValueError("float forbidden")
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("non-string map key")
        return {key: _json_value(item) for key, item in value.items()}
    raise ValueError("unsupported canonical value")


def canonical_json_bytes(preimage: dict[str, Any]) -> bytes:
    value = _json_value(preimage)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha256(preimage: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(preimage))


def content_digest(text: str) -> str:
    return sha256_bytes(text.encode("utf-8", errors="strict"))


def chunk_digest_preimage(
    *, contract_version: str, truth_class: str, source_reference,
    field_selector: str, candidate_fingerprint, scope, lifecycle,
    content_digest_sha256: str,
) -> dict[str, Any]:
    lifecycle_value = lifecycle.model_dump(mode="json", exclude={"revalidation_token"})
    return {
        "contract_version": contract_version,
        "truth_class": truth_class,
        "source_reference": source_reference,
        "field_selector": field_selector,
        "candidate_fingerprint": candidate_fingerprint,
        "scope": scope,
        "lifecycle": lifecycle_value,
        "content_digest_sha256": content_digest_sha256,
    }


def revalidation_digest_preimage(
    *, chunk_id: str, source_digest: str, source_version, lifecycle,
    retention,
) -> dict[str, Any]:
    return {
        "chunk_id": chunk_id,
        "source_digest": source_digest,
        "source_version": source_version,
        "source_lifecycle": lifecycle.source_status,
        "parent_shift_id": lifecycle.parent_shift_id,
        "parent_shift_version": lifecycle.parent_shift_version,
        "parent_shift_status": lifecycle.parent_shift_status,
        "report_status": lifecycle.report_status,
        "report_snapshot_digest": lifecycle.report_snapshot_digest,
        "correction_lineage": lifecycle.correction_lineage,
        "retention_disposition": retention.disposition,
        "retention_owner_id": retention.owner_id,
        "retention_policy_version": retention.policy_version,
        "retention_evidence_id": retention.source_evidence_id,
    }
