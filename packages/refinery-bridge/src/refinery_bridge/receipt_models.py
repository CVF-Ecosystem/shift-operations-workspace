from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator, model_validator

from .controls import ControlBundleV1
from .enums import (
    DedupeStatus,
    FallbackReason,
    QuarantineReason,
    Stage,
    StageOutcome,
    StageReason,
)
from .input_models import (
    QuarantineRouteV1,
    SafeId,
    SafeLink,
    SourceFingerprintV1,
    StrictModel,
    validate_safe_string,
)


FAIL_REASONS: dict[Stage, frozenset[StageReason]] = {
    Stage.ENVELOPE: frozenset(
        {StageReason.PROVENANCE_MISMATCH, StageReason.STAGE_UNAVAILABLE,
         StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.NORMALIZATION: frozenset(
        {StageReason.UNSUPPORTED_TRANSFORM, StageReason.POLICY_DRIFT,
         StageReason.STAGE_UNAVAILABLE, StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.TERMINOLOGY: frozenset(
        {StageReason.UNSUPPORTED_TRANSFORM, StageReason.POLICY_DRIFT,
         StageReason.STAGE_UNAVAILABLE, StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.CLASSIFICATION: frozenset(
        {StageReason.POLICY_DRIFT, StageReason.STAGE_UNAVAILABLE,
         StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.CONFLICT: frozenset(
        {StageReason.AMBIGUOUS_LOCAL_TIME, StageReason.AMBIGUOUS_ACTION_STATE,
         StageReason.CONFLICT_DETECTED, StageReason.UNSUPPORTED_TRANSFORM,
         StageReason.STAGE_UNAVAILABLE, StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.REDACTION: frozenset(
        {StageReason.REDACTION_FAILED, StageReason.REDACTION_RESIDUE,
         StageReason.POLICY_DRIFT, StageReason.STAGE_UNAVAILABLE,
         StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.DEDUPE: frozenset(
        {StageReason.DEDUPE_CONTEXT_INVALID, StageReason.EXACT_SOURCE_MATCH,
         StageReason.DIGEST_COLLISION_SUSPECTED, StageReason.INSUFFICIENT_CONTEXT,
         StageReason.STAGE_UNAVAILABLE, StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.QUALITY: frozenset(
        {StageReason.QUALITY_INCOMPLETE, StageReason.STAGE_UNAVAILABLE,
         StageReason.STAGE_INVARIANT_ERROR}
    ),
    Stage.CANDIDATE_ADMISSION: frozenset(
        {StageReason.STAGE_UNAVAILABLE, StageReason.STAGE_INVARIANT_ERROR}
    ),
}


class StageReceiptV1(StrictModel):
    stage: Stage
    control_version: SafeId
    outcome: StageOutcome
    reason_codes: tuple[StageReason, ...] = Field(min_length=1, max_length=1)
    dedupe_status: DedupeStatus | None = None
    safe_counts: dict[SafeId, Annotated[int, Field(ge=0, strict=True)]] = Field(
        default_factory=dict, max_length=64
    )
    safe_offsets: tuple[tuple[int, int], ...] = ()
    safe_ids: tuple[SafeId, ...] = Field(default=(), max_length=64)

    @field_validator("control_version")
    @classmethod
    def safe_version(cls, value: str) -> str:
        return validate_safe_string(value)

    @field_validator("safe_counts")
    @classmethod
    def safe_count_keys(cls, value: dict[str, int]) -> dict[str, int]:
        for key in value:
            validate_safe_string(key)
        return value

    @field_validator("safe_offsets")
    @classmethod
    def valid_offsets(
        cls, value: tuple[tuple[int, int], ...]
    ) -> tuple[tuple[int, int], ...]:
        if len(value) > 64:
            raise ValueError("too many offsets")
        previous_end = -1
        for start, end in value:
            if start < 0 or end <= start or end > 65536 or start < previous_end:
                raise ValueError("invalid safe offsets")
            previous_end = end
        return value

    @model_validator(mode="after")
    def legal_tuple(self) -> "StageReceiptV1":
        reason = self.reason_codes[0]
        if self.outcome == StageOutcome.PASS and reason != StageReason.STAGE_PASS:
            raise ValueError("PASS requires STAGE_PASS")
        if self.outcome == StageOutcome.NOT_RUN:
            if reason != StageReason.PRIOR_STAGE_FAILED:
                raise ValueError("NOT_RUN requires PRIOR_STAGE_FAILED")
            if self.safe_counts or self.safe_offsets or self.safe_ids or self.dedupe_status:
                raise ValueError("NOT_RUN cannot contain execution data")
        if self.outcome == StageOutcome.FAIL and reason not in FAIL_REASONS[self.stage]:
            raise ValueError("illegal stage failure reason")
        self._validate_dedupe(reason)
        for safe_id in self.safe_ids:
            validate_safe_string(safe_id)
        if tuple(sorted(self.safe_ids)) != self.safe_ids or len(set(self.safe_ids)) != len(self.safe_ids):
            raise ValueError("safe ids must be sorted unique")
        return self

    def _validate_dedupe(self, reason: StageReason) -> None:
        if self.stage != Stage.DEDUPE or self.outcome == StageOutcome.NOT_RUN:
            if self.dedupe_status is not None:
                raise ValueError("dedupe status forbidden")
            return
        allowed = {
            (StageOutcome.PASS, StageReason.STAGE_PASS): {
                DedupeStatus.UNIQUE, DedupeStatus.REDACTED_TEXT_MATCH
            },
            (StageOutcome.FAIL, StageReason.EXACT_SOURCE_MATCH): {
                DedupeStatus.EXACT_SOURCE_MATCH
            },
            (StageOutcome.FAIL, StageReason.DIGEST_COLLISION_SUSPECTED): {
                DedupeStatus.DIGEST_COLLISION_SUSPECTED
            },
            (StageOutcome.FAIL, StageReason.INSUFFICIENT_CONTEXT): {
                DedupeStatus.INSUFFICIENT_CONTEXT
            },
            (StageOutcome.FAIL, StageReason.DEDUPE_CONTEXT_INVALID): {None},
            (StageOutcome.FAIL, StageReason.STAGE_UNAVAILABLE): {None},
            (StageOutcome.FAIL, StageReason.STAGE_INVARIANT_ERROR): {None},
        }
        if self.dedupe_status not in allowed.get((self.outcome, reason), set()):
            raise ValueError("illegal dedupe status tuple")


class QualityReceiptV1(StrictModel):
    rules_version: SafeId
    provenance: Annotated[int, Field(strict=True)]
    normalization: Annotated[int, Field(strict=True)]
    protection: Annotated[int, Field(strict=True)]
    integrity: Annotated[int, Field(strict=True)]
    total: Annotated[int, Field(ge=0, le=100, strict=True)]
    threshold: Annotated[int, Field(strict=True)] = 100

    @model_validator(mode="after")
    def exact_components(self) -> "QualityReceiptV1":
        values = (self.provenance, self.normalization, self.protection, self.integrity)
        if any(value not in (0, 25) for value in values):
            raise ValueError("quality components must be 0 or 25")
        if self.total != sum(values) or self.threshold != 100:
            raise ValueError("invalid quality total")
        return self


class DuplicateReceiptV1(StrictModel):
    dedupe_status: DedupeStatus
    selected_prior_source_id: SafeId
    match_ids: tuple[SafeId, ...]
    match_count: Annotated[int, Field(ge=1, strict=True)]

    @model_validator(mode="after")
    def exact_duplicate(self) -> "DuplicateReceiptV1":
        if self.dedupe_status != DedupeStatus.EXACT_SOURCE_MATCH:
            raise ValueError("duplicate receipt requires exact source match")
        if (
            tuple(sorted(self.match_ids)) != self.match_ids
            or len(set(self.match_ids)) != len(self.match_ids)
            or self.match_count != len(self.match_ids)
        ):
            raise ValueError("invalid match ids")
        validate_safe_string(self.selected_prior_source_id)
        for match_id in self.match_ids:
            validate_safe_string(match_id)
        if self.selected_prior_source_id not in self.match_ids:
            raise ValueError("selected id missing")
        return self


class QuarantineReceiptV1(StrictModel):
    reason: QuarantineReason
    source_owner_id: SafeId
    source_link: SafeLink
    source_fingerprint: SourceFingerprintV1
    route: QuarantineRouteV1

    @model_validator(mode="after")
    def safe_provenance(self) -> "QuarantineReceiptV1":
        validate_safe_string(self.source_owner_id)
        validate_safe_string(self.source_link)
        return self


class FallbackReceiptV1(StrictModel):
    reason: FallbackReason
    caller_action: str = "USE_EXISTING_NON_AI_RULE_WORKFLOW"

    @model_validator(mode="after")
    def exact_action(self) -> "FallbackReceiptV1":
        if self.caller_action != "USE_EXISTING_NON_AI_RULE_WORKFLOW":
            raise ValueError("invalid caller action")
        return self


def make_receipt(
    controls: ControlBundleV1,
    stage: Stage,
    outcome: StageOutcome,
    reason: StageReason,
    *,
    status: DedupeStatus | None = None,
    counts: dict[str, int] | None = None,
    offsets: tuple[tuple[int, int], ...] = (),
    ids: tuple[str, ...] = (),
) -> StageReceiptV1:
    if tuple(sorted(ids)) != ids or len(set(ids)) != len(ids):
        raise ValueError("receipt ids must be sorted unique")
    return StageReceiptV1(
        stage=stage,
        control_version=controls.version_for(stage),
        outcome=outcome,
        reason_codes=(reason,),
        dedupe_status=status,
        safe_counts=counts or {},
        safe_offsets=offsets,
        safe_ids=ids,
    )


def complete_receipts(
    controls: ControlBundleV1, receipts: list[StageReceiptV1]
) -> tuple[StageReceiptV1, ...]:
    from .enums import STAGE_ORDER

    for stage in STAGE_ORDER[len(receipts):]:
        receipts.append(
            make_receipt(
                controls, stage, StageOutcome.NOT_RUN, StageReason.PRIOR_STAGE_FAILED
            )
        )
    return tuple(receipts)


def quality_receipt(
    controls: ControlBundleV1, receipts: list[StageReceiptV1]
) -> QualityReceiptV1:
    passed = {receipt.stage for receipt in receipts if receipt.outcome == StageOutcome.PASS}
    conflict_ok = Stage.CONFLICT in passed
    provenance = 25 if Stage.ENVELOPE in passed else 0
    normalization = 25 if {Stage.NORMALIZATION, Stage.TERMINOLOGY}.issubset(passed) and conflict_ok else 0
    protection = 25 if {Stage.CLASSIFICATION, Stage.CONFLICT, Stage.REDACTION}.issubset(passed) else 0
    integrity = 25 if Stage.DEDUPE in passed and conflict_ok else 0
    return QualityReceiptV1(
        rules_version=controls.quality_rules_version,
        provenance=provenance,
        normalization=normalization,
        protection=protection,
        integrity=integrity,
        total=provenance + normalization + protection + integrity,
    )
