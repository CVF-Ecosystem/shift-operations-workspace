from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError
from refinery_bridge.canonical import source_fingerprint
from refinery_bridge.enums import Disposition, SourceType
from refinery_bridge.output_models import RefineryResultV1
from operations_domain.models import (
    Correction,
    CustomerRequest,
    Handover,
    Incident,
    Message,
    OperationalEvent,
    Report,
    Shift,
    Task,
)

from .canonical import (
    SourceFacts, canonical_sha256, chunk_digest_preimage, content_digest,
    expected_selector, p3a_binding_state, retention_issue,
    revalidation_digest_preimage, source_facts, validation_payload,
)
from .contract_models import (
    CorrectionLineageV1, DataScopeEvidenceV1, LifecycleObservationV1, ProvenanceV1,
    RetrievalContractInputV1, RetrievalNonAdmissionV1, RetrievalReadyV1,
    ScopeV1, SourceReferenceV1,
)
from .enums import NonAdmissionReason, RecordType, RetentionDisposition, TruthClass, VersionKind
from .source_models import ProjectKnowledgeSourceV1, ScopeInputV1


_SOURCE_TYPES = (
    OperationalEvent,
    Task,
    CustomerRequest,
    Incident,
    Handover,
    Report,
    Message,
    ProjectKnowledgeSourceV1,
)
_SOURCE_KEYS = frozenset({
    "event_id", "task_id", "request_id", "incident_id", "handover_id", "report_id",
    "message_id", "source_pin",
})
def _reject(reason: NonAdmissionReason) -> RetrievalNonAdmissionV1:
    # Nullable identifiers are deliberately omitted. Arbitrary host payloads are
    # not an authenticated disclosure surface, even when a string looks ID-like.
    return RetrievalNonAdmissionV1(reason=reason)
def _trusted_value(payload: Any, name: str) -> Any:
    if isinstance(payload, RetrievalContractInputV1):
        return getattr(payload, name)
    if isinstance(payload, Mapping):
        return payload.get(name)
    return None


def _raw_disposition(value: Any) -> Any:
    if isinstance(value, RefineryResultV1):
        return value.disposition
    if isinstance(value, Mapping):
        return value.get("disposition")
    return None


def _source_classification(value: Any) -> NonAdmissionReason | None:
    if isinstance(value, (Correction, Shift)):
        return NonAdmissionReason.SOURCE_NOT_ELIGIBLE
    if isinstance(value, _SOURCE_TYPES):
        return None
    if isinstance(value, Mapping) and _SOURCE_KEYS.intersection(value.keys()):
        return None
    return NonAdmissionReason.UNKNOWN_SOURCE_TYPE


def _lineage(item: RetrievalContractInputV1, facts: SourceFacts):
    correction = item.correction
    if correction is None:
        return None
    expected = facts.record_type.value
    if (correction.record_type != expected or str(correction.record_id) != facts.record_id
            or facts.version.integer_version is None
            or correction.new_version != facts.version.integer_version
            or correction.previous_version >= correction.new_version):
        raise ValueError("invalid correction lineage")
    return CorrectionLineageV1(
        correction_id=str(correction.correction_id), record_type=facts.record_type,
        record_id=str(correction.record_id), previous_version=correction.previous_version,
        new_version=correction.new_version,
    )


def construct_retrieval_contract(payload: Any):
    """Return a closed result for every ordinary host-language payload."""
    try:
        return _construct_retrieval_contract(payload)
    except Exception:
        return _reject(NonAdmissionReason.INVARIANT_VIOLATION)


def _construct_retrieval_contract(payload: Any):
    if not isinstance(payload, (Mapping, RetrievalContractInputV1)):
        return _reject(NonAdmissionReason.INVARIANT_VIOLATION)
    version = _trusted_value(payload, "contract_version")
    if version != "1.0":
        return _reject(NonAdmissionReason.CONTRACT_VERSION_UNSUPPORTED)
    if isinstance(payload, Mapping) and set(payload) != set(RetrievalContractInputV1.model_fields):
        return _reject(NonAdmissionReason.INVARIANT_VIOLATION)
    raw_result = _trusted_value(payload, "refinery_result")
    if _raw_disposition(raw_result) not in (None, Disposition.CANDIDATE_READY,
                                             Disposition.CANDIDATE_READY.value):
        return _reject(NonAdmissionReason.REFINERY_RESULT_NOT_READY)
    binding_state = p3a_binding_state(payload)
    if binding_state is None:
        return _reject(NonAdmissionReason.INVARIANT_VIOLATION)
    if not binding_state:
        return _reject(NonAdmissionReason.CANDIDATE_BINDING_MISMATCH)
    raw_source = _trusted_value(payload, "source")
    source_issue = _source_classification(raw_source)
    if source_issue is not None:
        return _reject(source_issue)
    raw_retention = _trusted_value(payload, "retention")
    retention_issue_value = retention_issue(raw_retention)
    payload_for_validation = (
        validation_payload(payload, retention_issue_value)
        if isinstance(payload, Mapping) else payload
    )
    data_scope_invalid = False
    try:
        item = (payload if isinstance(payload, RetrievalContractInputV1)
                else RetrievalContractInputV1.model_validate(payload_for_validation))
    except (ValidationError, ValueError, TypeError, UnicodeError):
        if isinstance(payload_for_validation, Mapping) and "data_scope_evidence" in payload_for_validation:
            repaired = dict(payload_for_validation)
            repaired["data_scope_evidence"] = DataScopeEvidenceV1()
            try:
                RetrievalContractInputV1.model_validate(repaired)
            except (ValidationError, ValueError, TypeError, UnicodeError):
                pass
            else:
                item = RetrievalContractInputV1.model_validate(repaired)
                data_scope_invalid = True
        if not data_scope_invalid:
            return _reject(NonAdmissionReason.INVARIANT_VIOLATION)
    if item.refinery_result.disposition != Disposition.CANDIDATE_READY:
        return _reject(NonAdmissionReason.REFINERY_RESULT_NOT_READY)
    candidate = item.candidate
    result = item.refinery_result
    try:
        facts = source_facts(item.source, item.field_selector)
    except (ValidationError, ValueError, TypeError):
        return _reject(NonAdmissionReason.SOURCE_VERSION_INVALID)
    if isinstance(facts, NonAdmissionReason):
        return _reject(facts)
    if not expected_selector(facts.record_type, item.field_selector):
        return _reject(NonAdmissionReason.SOURCE_PROJECTION_MISMATCH)
    if facts.record_type == RecordType.PROJECT_KNOWLEDGE:
        if candidate.source_id != item.source.source_id or candidate.source_owner_id != item.source.source_owner_id:
            return _reject(NonAdmissionReason.CANDIDATE_BINDING_MISMATCH)
        if candidate.source_version != item.source.source_pin:
            return _reject(NonAdmissionReason.SOURCE_VERSION_INVALID)
        facts = SourceFacts(facts.record_type, None, facts.truth_class, facts.version,
                             facts.status, (), item.envelope.raw_text,
                             candidate.source_fingerprint.sha256)
    else:
        expected_id = facts.record_id
        if candidate.source_id != expected_id:
            return _reject(NonAdmissionReason.CANDIDATE_BINDING_MISMATCH)
        expected_version = ("UNVERSIONED" if facts.version.kind == VersionKind.UNVERSIONED
                            else str(facts.version.integer_version))
        if candidate.source_version != expected_version:
            return _reject(NonAdmissionReason.SOURCE_VERSION_INVALID)
    if facts.text != item.envelope.raw_text or source_fingerprint(facts.text) != candidate.source_fingerprint:
        return _reject(NonAdmissionReason.SOURCE_PROJECTION_MISMATCH)
    if facts.truth_class == TruthClass.CANONICAL_OPERATIONAL_RECORD:
        if item.envelope.source_type != SourceType.CANONICAL_OPERATIONAL_RECORD:
            return _reject(NonAdmissionReason.CANDIDATE_BINDING_MISMATCH)
        return _reject(NonAdmissionReason.SOURCE_DIGEST_OWNER_MISSING)
    expected_type = SourceType.INTERNAL_MESSAGE if facts.record_type == RecordType.MESSAGE else SourceType.PROJECT_KNOWLEDGE
    if item.envelope.source_type != expected_type:
        return _reject(NonAdmissionReason.CANDIDATE_BINDING_MISMATCH)
    try:
        return _build_ready(item, facts, retention_issue_value, data_scope_invalid)
    except (ValidationError, ValueError, TypeError, UnicodeError):
        return _reject(NonAdmissionReason.INVARIANT_VIOLATION)


def _build_ready(item: RetrievalContractInputV1, facts: SourceFacts,
                 retention_issue: NonAdmissionReason | None,
                 data_scope_invalid: bool):
    parent_ids = tuple(sorted(str(shift.shift_id) for shift in item.scope.parent_shifts))
    scope_invalid = (
        item.scope.shift_ids != facts.shift_ids
        or tuple(sorted(item.scope.shift_ids)) != item.scope.shift_ids
        or len(set(item.scope.shift_ids)) != len(item.scope.shift_ids)
        or len(item.scope.shift_ids) > 2
        or parent_ids != item.scope.shift_ids
        or len(parent_ids) != len(set(parent_ids))
        or (
            item.scope.effective_from_utc is not None
            and item.scope.effective_to_utc is not None
            and item.scope.effective_from_utc > item.scope.effective_to_utc
        )
    )
    if scope_invalid:
        return _reject(NonAdmissionReason.SCOPE_INVALID)
    if item.tenant_required:
        return _reject(NonAdmissionReason.TENANT_SCOPE_NOT_MODELED)
    try:
        lineage = _lineage(item, facts)
    except ValueError:
        return _reject(NonAdmissionReason.LIFECYCLE_INVALID)
    retention = item.retention
    if retention_issue is not None:
        return _reject(retention_issue)
    if (retention.disposition == RetentionDisposition.OWNER_NOT_FOUND or not retention.owner_id
            or not retention.policy_version or not retention.source_evidence_id):
        return _reject(NonAdmissionReason.RETENTION_OWNER_NOT_FOUND)
    if (retention.disposition != RetentionDisposition.OWNER_ASSERTED_ACTIVE
            or retention.erased_at_utc is not None
            or (retention.expires_at_utc is not None and retention.expires_at_utc <= retention.checked_at_utc)):
        return _reject(NonAdmissionReason.RETENTION_NOT_ACTIVE)
    if data_scope_invalid:
        return _reject(NonAdmissionReason.DATA_SCOPE_EVIDENCE_INVALID)
    parent_id = (str(item.source.from_shift_id) if isinstance(item.source, Handover)
                 else facts.shift_ids[0] if facts.shift_ids else None)
    parent = next((shift for shift in item.scope.parent_shifts
                   if str(shift.shift_id) == parent_id), None)
    source_ref = SourceReferenceV1(
        source_class=facts.truth_class, record_type=facts.record_type, record_id=facts.record_id,
        source_digest_sha256=facts.digest, version=facts.version,
        observed_at_utc=item.observed_at_utc, source_cutoff_utc=item.source_cutoff_utc,
        correction_lineage=lineage, source_id=item.candidate.source_id,
        source_version=item.candidate.source_version,
        source_fingerprint=item.candidate.source_fingerprint,
        candidate_fingerprint=item.candidate_fingerprint,
        normalization_rules_version=item.candidate.normalization_rules_version,
        terminology_rules_version=item.candidate.terminology_rules_version,
        classification_rules_version=item.candidate.classification_rules_version,
        redaction_rules_version=item.candidate.redaction_rules_version,
        quality_rules_version=item.candidate.quality_rules_version,
    )
    scope = ScopeV1(shift_ids=facts.shift_ids,
                    effective_from_utc=item.scope.effective_from_utc,
                    effective_to_utc=item.scope.effective_to_utc,
                    observed_at_utc=item.observed_at_utc)
    lifecycle = LifecycleObservationV1(
        source_status=facts.status, source_version=facts.version,
        parent_shift_id=str(parent.shift_id) if parent else None,
        parent_shift_version=parent.version if parent else None,
        parent_shift_status=parent.status.value if parent else None,
        report_status=None, report_snapshot_digest=None, correction_lineage=lineage,
        revalidation_token="0" * 64,
    )
    digest = content_digest(item.candidate.redacted_normalized_text)
    chunk = canonical_sha256(chunk_digest_preimage(
        contract_version="1.0", truth_class=facts.truth_class.value,
        source_reference=source_ref, field_selector=item.field_selector,
        candidate_fingerprint=item.candidate_fingerprint, scope=scope,
        lifecycle=lifecycle, content_digest_sha256=digest,
    ))
    token = canonical_sha256(revalidation_digest_preimage(
        chunk_id=chunk, source_digest=facts.digest, source_version=facts.version,
        lifecycle=lifecycle, retention=retention,
    ))
    lifecycle = lifecycle.model_copy(update={"revalidation_token": token})
    provenance = ProvenanceV1(
        source_fingerprint=item.candidate.source_fingerprint,
        candidate_fingerprint=item.candidate_fingerprint,
        stage_receipts=item.refinery_result.stage_receipts,
        normalization_rules_version=item.candidate.normalization_rules_version,
        terminology_rules_version=item.candidate.terminology_rules_version,
        classification_rules_version=item.candidate.classification_rules_version,
        redaction_rules_version=item.candidate.redaction_rules_version,
        quality_rules_version=item.candidate.quality_rules_version,
        source_reference_digest=facts.digest, source_reference_version=facts.version,
        field_selector=item.field_selector, retention_evidence_id=retention.source_evidence_id,
        retention_policy_version=retention.policy_version, contract_version="1.0",
    )
    return RetrievalReadyV1(
        truth_class=facts.truth_class, field_selector=item.field_selector,
        redacted_normalized_text=item.candidate.redacted_normalized_text,
        content_digest_sha256=digest, chunk_id=chunk, source_reference=source_ref,
        scope=scope, lifecycle=lifecycle, retention=retention, provenance=provenance,
        data_scope_evidence=item.data_scope_evidence,
    )
