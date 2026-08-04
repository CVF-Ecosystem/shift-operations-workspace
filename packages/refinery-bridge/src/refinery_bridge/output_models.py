from __future__ import annotations

from typing import Annotated, Any, Literal, TypeAlias

from pydantic import Field, ValidationError, model_validator

from .enums import (
    Disposition,
    SafeErrorCode,
    Sensitivity,
    StageOutcome,
    STAGE_ORDER,
)
from .input_models import (
    CandidateFingerprintV1,
    SafeId,
    SafeLink,
    SourceFingerprintV1,
    StrictModel,
    validate_safe_string,
)
from .receipt_models import (
    DuplicateReceiptV1,
    FallbackReceiptV1,
    QualityReceiptV1,
    QuarantineReceiptV1,
    StageReceiptV1,
)
from .protection import candidate_is_bound, failure_is_bound, result_quality_is_bound

FIELD_CODES = {
    "schema_version": SafeErrorCode.INVALID_SCHEMA_VERSION,
    "source_id": SafeErrorCode.INVALID_SOURCE_ID,
    "source_version": SafeErrorCode.INVALID_SOURCE_VERSION,
    "source_link": SafeErrorCode.INVALID_SOURCE_LINK,
    "source_type": SafeErrorCode.INVALID_SOURCE_TYPE,
    "raw_text": SafeErrorCode.INVALID_RAW_TEXT,
    "received_at": SafeErrorCode.INVALID_RECEIVED_AT,
    "declared_sensitivity": SafeErrorCode.INVALID_DECLARED_SENSITIVITY,
    "source_owner_id": SafeErrorCode.INVALID_SOURCE_OWNER_ID,
    "source_fingerprint": SafeErrorCode.INVALID_SOURCE_FINGERPRINT,
}


class PreAdmissionRejectionV1(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    kind: Literal["PRE_ADMISSION_REJECTION"] = "PRE_ADMISSION_REJECTION"
    reason: Literal["INVALID_ENVELOPE"] = "INVALID_ENVELOPE"
    safe_error_codes: tuple[SafeErrorCode, ...] = Field(min_length=1)
    caller_action: Literal["USE_EXISTING_NON_AI_RULE_WORKFLOW"] = (
        "USE_EXISTING_NON_AI_RULE_WORKFLOW"
    )

    @model_validator(mode="after")
    def sorted_codes(self) -> "PreAdmissionRejectionV1":
        if tuple(sorted(self.safe_error_codes)) != self.safe_error_codes:
            raise ValueError("error codes must be sorted")
        if len(set(self.safe_error_codes)) != len(self.safe_error_codes):
            raise ValueError("error codes must be unique")
        return self


def pre_admit(payload: Any) -> "RefineryEnvelopeV1 | PreAdmissionRejectionV1":
    from .input_models import RefineryEnvelopeV1

    codes: set[SafeErrorCode] = set()
    if not isinstance(payload, dict):
        codes.add(SafeErrorCode.FIELD_SET_MISMATCH)
    else:
        if set(payload) != set(FIELD_CODES):
            codes.add(SafeErrorCode.FIELD_SET_MISMATCH)
        try:
            return RefineryEnvelopeV1.model_validate(payload)
        except (ValidationError, ValueError, TypeError, UnicodeError) as exc:
            if isinstance(exc, ValidationError):
                for error in exc.errors(include_input=False, include_url=False):
                    field = str(error["loc"][0]) if error["loc"] else ""
                    codes.add(FIELD_CODES.get(field, SafeErrorCode.FIELD_SET_MISMATCH))
            else:
                codes.add(SafeErrorCode.INVALID_RAW_TEXT)
    return PreAdmissionRejectionV1(safe_error_codes=tuple(sorted(codes)))


class ContextCandidateV1(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    redacted_normalized_text: Annotated[str, Field(min_length=1, max_length=65536)]
    sensitivity: Sensitivity
    topic_labels: tuple[SafeId, ...] = Field(max_length=64)
    source_id: SafeId
    source_version: SafeId
    source_owner_id: SafeId
    source_link: SafeLink
    source_fingerprint: SourceFingerprintV1
    normalization_rules_version: SafeId
    terminology_rules_version: SafeId
    classification_rules_version: SafeId
    redaction_rules_version: SafeId
    quality_rules_version: SafeId
    quality_score: Annotated[int, Field(ge=0, le=100, strict=True)]
    provenance: Annotated[int, Field(strict=True)]
    normalization: Annotated[int, Field(strict=True)]
    protection: Annotated[int, Field(strict=True)]
    integrity: Annotated[int, Field(strict=True)]

    @model_validator(mode="after")
    def exact_candidate(self) -> "ContextCandidateV1":
        if tuple(sorted(self.topic_labels)) != self.topic_labels:
            raise ValueError("topics must be sorted")
        if len(set(self.topic_labels)) != len(self.topic_labels):
            raise ValueError("topics must be unique")
        components = (self.provenance, self.normalization, self.protection, self.integrity)
        if any(value not in (0, 25) for value in components):
            raise ValueError("invalid quality component")
        if self.quality_score != 100 or sum(components) != 100:
            raise ValueError("candidate requires 100 quality")
        safe_values = (
            self.source_id,
            self.source_version,
            self.source_owner_id,
            self.source_link,
            self.normalization_rules_version,
            self.terminology_rules_version,
            self.classification_rules_version,
            self.redaction_rules_version,
            self.quality_rules_version,
            *self.topic_labels,
        )
        for value in safe_values:
            validate_safe_string(value)
        self.redacted_normalized_text.encode("utf-8", errors="strict")
        return self

    def fingerprint_preimage(self) -> dict[str, object]:
        return self.model_dump(mode="json")


class RefineryResultV1(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    disposition: Disposition
    source_owner_id: SafeId
    source_link: SafeLink
    source_fingerprint: SourceFingerprintV1
    stage_receipts: tuple[StageReceiptV1, ...] = Field(min_length=9, max_length=9)
    quality_receipt: QualityReceiptV1
    context_candidate: ContextCandidateV1 | None = None
    candidate_fingerprint: CandidateFingerprintV1 | None = None
    duplicate_receipt: DuplicateReceiptV1 | None = None
    quarantine_receipt: QuarantineReceiptV1 | None = None
    fallback_receipt: FallbackReceiptV1 | None = None

    @model_validator(mode="after")
    def valid_result(self) -> "RefineryResultV1":
        validate_safe_string(self.source_owner_id)
        validate_safe_string(self.source_link)
        if tuple(receipt.stage for receipt in self.stage_receipts) != STAGE_ORDER:
            raise ValueError("invalid stage order")
        failed = False
        for receipt in self.stage_receipts:
            if failed and receipt.outcome != StageOutcome.NOT_RUN:
                raise ValueError("later stage must be NOT_RUN")
            if not failed and receipt.outcome == StageOutcome.NOT_RUN:
                raise ValueError("orphan NOT_RUN")
            if receipt.outcome == StageOutcome.FAIL:
                failed = True
        first_failure = next(
            (item for item in self.stage_receipts if item.outcome == StageOutcome.FAIL),
            None,
        )
        if not result_quality_is_bound(self):
            raise ValueError("quality receipt is not bound to stage receipts")
        self._validate_disposition(first_failure)
        return self

    def _validate_disposition(self, first_failure: StageReceiptV1 | None) -> None:
        candidate = self.context_candidate is not None and self.candidate_fingerprint is not None
        receipts = (
            self.duplicate_receipt is not None,
            self.quarantine_receipt is not None,
            self.fallback_receipt is not None,
        )
        if self.disposition == Disposition.CANDIDATE_READY:
            if not candidate or any(receipts) or first_failure is not None:
                raise ValueError("invalid ready result")
            if any(item.outcome != StageOutcome.PASS for item in self.stage_receipts):
                raise ValueError("ready requires nine PASS receipts")
            if not candidate_is_bound(self):
                raise ValueError("candidate is not bound to result receipts")
        else:
            if self.context_candidate is not None or self.candidate_fingerprint is not None:
                raise ValueError("no-candidate disposition contains candidate")
            expected = {
                Disposition.NO_CANDIDATE_DUPLICATE: (True, False, False),
                Disposition.NO_CANDIDATE_QUARANTINED: (False, True, False),
                Disposition.NO_CANDIDATE_FALLBACK: (False, False, True),
            }[self.disposition]
            if receipts != expected:
                raise ValueError("wrong no-candidate receipt")
            if first_failure is None:
                raise ValueError("no-candidate result requires a failed stage")
            if not failure_is_bound(self, first_failure):
                raise ValueError("no-candidate disposition mismatch")


RefineryBoundaryOutputV1: TypeAlias = PreAdmissionRejectionV1 | RefineryResultV1
