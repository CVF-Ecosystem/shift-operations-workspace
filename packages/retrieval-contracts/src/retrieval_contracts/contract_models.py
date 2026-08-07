from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, TypeAlias

from pydantic import Field, field_validator, model_validator
from refinery_bridge.input_models import (
    CandidateFingerprintV1, RefineryEnvelopeV1, SourceFingerprintV1,
)
from refinery_bridge.output_models import ContextCandidateV1, RefineryResultV1
from refinery_bridge.receipt_models import StageReceiptV1
from operations_domain.models import (
    Correction, CustomerRequest, Handover, Incident, Message, OperationalEvent, Report, Task,
)

from .common import Digest, SafeId, SafeIdentifierModel, StrictModel, utc_datetime
from .enums import (
    DataScopeStatus, NonAdmissionReason, RecordType, RetentionDisposition,
    TenantScopeStatus, TruthClass, VersionKind,
)
from .source_models import ProjectKnowledgeSourceV1, ScopeInputV1

SourceValue: TypeAlias = (
    OperationalEvent | Task | CustomerRequest | Incident | Handover | Report |
    Message | ProjectKnowledgeSourceV1
)


class VersionBindingV1(StrictModel):
    kind: VersionKind
    integer_version: Annotated[int, Field(ge=1, strict=True)] | None = None
    source_version_string: SafeId | None = None

    @model_validator(mode="after")
    def exactly_one_form(self) -> "VersionBindingV1":
        expected = {
            VersionKind.INTEGER_VERSION: (True, False),
            VersionKind.SOURCE_VERSION_STRING: (False, True),
            VersionKind.UNVERSIONED: (False, False),
        }[self.kind]
        actual = (self.integer_version is not None, self.source_version_string is not None)
        if actual != expected:
            raise ValueError("version binding fields contradict kind")
        return self


class CorrectionLineageV1(SafeIdentifierModel):
    correction_id: SafeId
    record_type: RecordType
    record_id: SafeId
    previous_version: Annotated[int, Field(ge=1, strict=True)]
    new_version: Annotated[int, Field(ge=2, strict=True)]

    @model_validator(mode="after")
    def forward(self) -> "CorrectionLineageV1":
        if self.new_version <= self.previous_version:
            raise ValueError("correction must advance version")
        return self


class SourceReferenceV1(SafeIdentifierModel):
    source_class: TruthClass
    record_type: RecordType
    record_id: SafeId | None
    source_digest_sha256: Digest
    version: VersionBindingV1
    observed_at_utc: datetime
    source_cutoff_utc: datetime
    correction_lineage: CorrectionLineageV1 | None
    source_id: SafeId
    source_version: SafeId
    source_fingerprint: SourceFingerprintV1
    candidate_fingerprint: CandidateFingerprintV1
    normalization_rules_version: SafeId
    terminology_rules_version: SafeId
    classification_rules_version: SafeId
    redaction_rules_version: SafeId
    quality_rules_version: SafeId

    @model_validator(mode="after")
    def valid_time_and_record(self) -> "SourceReferenceV1":
        utc_datetime(self.observed_at_utc)
        utc_datetime(self.source_cutoff_utc)
        if self.source_cutoff_utc > self.observed_at_utc:
            raise ValueError("cutoff after observation")
        if self.record_type != RecordType.PROJECT_KNOWLEDGE and self.record_id is None:
            raise ValueError("record id required")
        if self.record_type == RecordType.PROJECT_KNOWLEDGE and self.record_id is not None:
            raise ValueError("project knowledge has no record id")
        return self


class ScopeV1(StrictModel):
    workspace_scope: Literal["shift-operations-workspace"] = "shift-operations-workspace"
    tenant_scope_status: Literal[TenantScopeStatus.NOT_MODELED] = TenantScopeStatus.NOT_MODELED
    shift_ids: tuple[SafeId, ...] = Field(max_length=2)
    effective_from_utc: datetime | None
    effective_to_utc: datetime | None
    observed_at_utc: datetime

    @model_validator(mode="after")
    def valid_scope(self) -> "ScopeV1":
        if tuple(sorted(self.shift_ids)) != self.shift_ids or len(set(self.shift_ids)) != len(self.shift_ids):
            raise ValueError("shift_ids must be sorted unique")
        for value in (self.effective_from_utc, self.effective_to_utc, self.observed_at_utc):
            if value is not None:
                utc_datetime(value)
        if (self.effective_from_utc is not None and self.effective_to_utc is not None
                and self.effective_from_utc > self.effective_to_utc):
            raise ValueError("effective window inverted")
        return self


class LifecycleObservationV1(StrictModel):
    source_status: SafeId
    source_version: VersionBindingV1
    parent_shift_id: SafeId | None
    parent_shift_version: Annotated[int, Field(ge=1, strict=True)] | None
    parent_shift_status: SafeId | None
    report_status: SafeId | None
    report_snapshot_digest: Digest | None
    correction_lineage: CorrectionLineageV1 | None
    requires_use_time_revalidation: Literal[True] = True
    revalidation_token: Digest


class RetentionAssertionV1(SafeIdentifierModel):
    disposition: RetentionDisposition
    owner_id: SafeId | None
    policy_version: SafeId | None
    checked_at_utc: datetime
    expires_at_utc: datetime | None = None
    erased_at_utc: datetime | None = None
    source_evidence_id: SafeId | None

    @model_validator(mode="after")
    def valid_assertion(self) -> "RetentionAssertionV1":
        for value in (self.checked_at_utc, self.expires_at_utc, self.erased_at_utc):
            if value is not None:
                utc_datetime(value)
        if self.disposition == RetentionDisposition.OWNER_ASSERTED_ACTIVE:
            if self.erased_at_utc is not None:
                raise ValueError("active retention cannot be erased")
            if self.expires_at_utc is not None and self.expires_at_utc <= self.checked_at_utc:
                raise ValueError("active retention must be unexpired")
        elif self.disposition == RetentionDisposition.OWNER_ASSERTED_EXPIRED:
            if (self.expires_at_utc is None
                    or self.expires_at_utc > self.checked_at_utc
                    or self.erased_at_utc is not None):
                raise ValueError("expired retention requires a completed expiry only")
        elif self.disposition == RetentionDisposition.OWNER_ASSERTED_ERASED:
            if (self.erased_at_utc is None
                    or self.erased_at_utc > self.checked_at_utc
                    or self.expires_at_utc is not None):
                raise ValueError("erased retention requires a completed erasure only")
        elif self.expires_at_utc is not None or self.erased_at_utc is not None:
            raise ValueError("owner-not-found retention has no lifecycle assertion")
        return self


class DataScopeEvidenceV1(StrictModel):
    status: Literal[DataScopeStatus.NOT_EVALUATED] = DataScopeStatus.NOT_EVALUATED
    minimization_evidence_status: Literal["NOT_PROVEN"] = "NOT_PROVEN"
    placement_enforcement_status: Literal["NOT_EVALUATED"] = "NOT_EVALUATED"
    runtime_caller_status: Literal["NO_LOAD_BEARING_CALLER"] = "NO_LOAD_BEARING_CALLER"


class ProvenanceV1(StrictModel):
    source_fingerprint: SourceFingerprintV1
    candidate_fingerprint: CandidateFingerprintV1
    stage_receipts: tuple[StageReceiptV1, ...] = Field(min_length=9, max_length=9)
    normalization_rules_version: SafeId
    terminology_rules_version: SafeId
    classification_rules_version: SafeId
    redaction_rules_version: SafeId
    quality_rules_version: SafeId
    source_reference_digest: Digest
    source_reference_version: VersionBindingV1
    field_selector: SafeId
    retention_evidence_id: SafeId
    retention_policy_version: SafeId
    contract_version: Literal["1.0"] = "1.0"


class RetrievalContractInputV1(StrictModel):
    contract_version: Literal["1.0"] = "1.0"
    envelope: RefineryEnvelopeV1
    refinery_result: RefineryResultV1
    candidate: ContextCandidateV1
    candidate_fingerprint: CandidateFingerprintV1
    source: SourceValue
    field_selector: SafeId
    source_cutoff_utc: datetime
    observed_at_utc: datetime
    correction: Correction | None
    scope: ScopeInputV1
    retention: RetentionAssertionV1
    data_scope_evidence: DataScopeEvidenceV1
    tenant_required: bool

    @model_validator(mode="after")
    def valid_observation_time(self) -> "RetrievalContractInputV1":
        utc_datetime(self.source_cutoff_utc)
        utc_datetime(self.observed_at_utc)
        if self.source_cutoff_utc > self.observed_at_utc:
            raise ValueError("cutoff after observation")
        return self


class RetrievalReadyV1(StrictModel):
    kind: Literal["RETRIEVAL_READY"] = "RETRIEVAL_READY"
    contract_version: Literal["1.0"] = "1.0"
    truth_class: TruthClass
    field_selector: SafeId
    redacted_normalized_text: Annotated[str, Field(min_length=1, max_length=65536)]
    content_digest_sha256: Digest
    chunk_id: Digest
    source_reference: SourceReferenceV1
    scope: ScopeV1
    lifecycle: LifecycleObservationV1
    retention: RetentionAssertionV1
    provenance: ProvenanceV1
    data_scope_evidence: DataScopeEvidenceV1


class RetrievalNonAdmissionV1(StrictModel):
    kind: Literal["NOT_ADMITTED"] = "NOT_ADMITTED"
    contract_version: Literal["1.0"] = "1.0"
    reason: NonAdmissionReason
    safe_source_id: SafeId | None = None
    safe_record_id: SafeId | None = None


RetrievalContractResultV1: TypeAlias = RetrievalReadyV1 | RetrievalNonAdmissionV1
