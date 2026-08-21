"""Closed receipt enums/models plus sanitized end-to-end RAG receipt
construction (SPEC R15).

Builds :class:`GovernedRagReceiptV1` from safe ids, hashes, versions,
counts, outcomes and reason codes only - never a query, prompt, evidence/
minimized/output body, raw exception, endpoint credential, token,
authorization header or secret. ``receipt_hash_sha256`` is computed here
from the canonical dump of every OTHER field, exactly mirroring
``governed_retrieval.receipt_models.RetrievalReceiptV1``'s own pattern, so a
test can independently recompute and cross-check it rather than trust it.

The receipt enums/models live in this module (rather than ``models.py``) to
keep every file under the repository's file-size ceiling; every other
module imports ``RagStage``/``RagFinalOutcome``/etc. from here.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, SafeId, StrictModel

from .hashing import receipt_hash
from .injection import InjectionOmissionV1
from .models import ENCODER_ID_LITERAL, NonNegInt

# ---------------------------------------------------------------------------
# Closed enums (SPEC R2)
# ---------------------------------------------------------------------------


class RagFinalOutcome(StrEnum):
    """The exact closed set of P4-A2 terminal outcomes."""

    ANSWERED = "ANSWERED"
    ABSTAINED = "ABSTAINED"
    RETRIEVAL_NOT_POSITIVE = "RETRIEVAL_NOT_POSITIVE"
    BINDING_MISMATCH = "BINDING_MISMATCH"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    SCOPE_WIDENING_REJECTED = "SCOPE_WIDENING_REJECTED"
    STALE_INDEX = "STALE_INDEX"
    INJECTION_BLOCKED = "INJECTION_BLOCKED"
    MINIMIZATION_FAILED = "MINIMIZATION_FAILED"
    CONTEXT_BUDGET_EXCEEDED = "CONTEXT_BUDGET_EXCEEDED"
    PLACEMENT_REFUSED = "PLACEMENT_REFUSED"
    GATEWAY_NOT_ACCEPTED = "GATEWAY_NOT_ACCEPTED"
    OUTPUT_VALIDATION_FAILED = "OUTPUT_VALIDATION_FAILED"
    REQUEST_INVALID = "REQUEST_INVALID"


class RagStage(StrEnum):
    """The exact nine ordered P4-A2 pipeline stages (receipt appendix)."""

    REQUEST_VALIDATED = "REQUEST_VALIDATED"
    RETRIEVAL_BOUND = "RETRIEVAL_BOUND"
    INDEX_VALIDATED = "INDEX_VALIDATED"
    RANKED = "RANKED"
    INJECTION_SCREENED = "INJECTION_SCREENED"
    MINIMIZED = "MINIMIZED"
    CONTEXT_ASSEMBLED = "CONTEXT_ASSEMBLED"
    GATEWAY_DISPATCHED = "GATEWAY_DISPATCHED"
    ANSWER_VALIDATED = "ANSWER_VALIDATED"


RAG_STAGE_ORDER: tuple[RagStage, ...] = tuple(RagStage)

# P4A2-REV-F6 - the exact stage at which each non-positive outcome's single
# FAIL entry must appear, mirroring the DESIGN mandatory execution order
# (RETRIEVAL_BOUND covers both P4-A1 non-positive short-circuit AND the
# independent binding/scope re-verification of DESIGN step 4).
_OUTCOME_TERMINAL_STAGE: dict["RagFinalOutcome", "RagStage"] = {
    RagFinalOutcome.RETRIEVAL_NOT_POSITIVE: RagStage.RETRIEVAL_BOUND,
    RagFinalOutcome.BINDING_MISMATCH: RagStage.RETRIEVAL_BOUND,
    RagFinalOutcome.SCOPE_MISMATCH: RagStage.RETRIEVAL_BOUND,
    RagFinalOutcome.SCOPE_WIDENING_REJECTED: RagStage.RETRIEVAL_BOUND,
    RagFinalOutcome.STALE_INDEX: RagStage.INDEX_VALIDATED,
    RagFinalOutcome.INJECTION_BLOCKED: RagStage.INJECTION_SCREENED,
    RagFinalOutcome.MINIMIZATION_FAILED: RagStage.MINIMIZED,
    RagFinalOutcome.CONTEXT_BUDGET_EXCEEDED: RagStage.CONTEXT_ASSEMBLED,
    RagFinalOutcome.PLACEMENT_REFUSED: RagStage.CONTEXT_ASSEMBLED,
    RagFinalOutcome.GATEWAY_NOT_ACCEPTED: RagStage.GATEWAY_DISPATCHED,
    RagFinalOutcome.OUTPUT_VALIDATION_FAILED: RagStage.ANSWER_VALIDATED,
    RagFinalOutcome.REQUEST_INVALID: RagStage.REQUEST_VALIDATED,
}


class RagStageOutcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"


# ---------------------------------------------------------------------------
# Receipt models (SPEC R15)
# ---------------------------------------------------------------------------


class RagStageReceiptV1(StrictModel):
    """One stage's outcome in the fixed nine-stage order (receipt appendix)."""

    stage: RagStage
    outcome: RagStageOutcome
    reason_code: str = Field(default="", max_length=64)

    @model_validator(mode="after")
    def _reason_matches_outcome(self) -> "RagStageReceiptV1":
        if self.outcome is RagStageOutcome.PASS or self.outcome is RagStageOutcome.NOT_RUN:
            if self.reason_code:
                raise ValueError("reason_code must be empty for PASS/NOT_RUN")
        elif not self.reason_code:
            raise ValueError("reason_code required for FAIL")
        return self


class GovernedRagReceiptV1(StrictModel):
    """SPEC R15 - the sanitized end-to-end receipt. Only safe ids, hashes,
    versions, counts, outcomes and reason codes - no query, prompt, evidence/
    minimized/output body, raw exception, endpoint credential, token,
    authorization header or secret. Every digest here is recomputed by tests
    rather than trusted from caller input."""

    contract_version: str = Field(default="1.0", pattern=r"^1\.0$")
    normalized_query_digest_sha256: Digest
    retrieval_receipt_hash_sha256: Digest
    retrieval_evidence_set_hash_sha256: Digest
    authorization_scope_digest_sha256: Digest
    corpus_id: SafeId
    index_build_digest_sha256: Digest | None
    encoder_id: str = Field(default=ENCODER_ID_LITERAL, pattern=rf"^{ENCODER_ID_LITERAL}$")
    encoder_version: SafeId
    lexicon_digest_sha256: Digest
    score_policy_digest_sha256: Digest
    pre_injection_citation_ids: tuple[Digest, ...]
    post_injection_citation_ids: tuple[Digest, ...]
    injection_omissions: tuple[InjectionOmissionV1, ...] = Field(max_length=4)
    minimization_ruleset_digest_sha256: Digest | None
    minimization_input_digest_sha256: Digest | None
    minimization_output_digest_sha256: Digest | None
    minimization_retained_count: NonNegInt
    minimization_omitted_count: NonNegInt
    context_digest_sha256: Digest | None
    output_schema_digest_sha256: Digest | None
    gateway_request_digest_sha256: Digest | None
    gateway_receipt_output_digest_sha256: Digest | None
    provider_response_digest_sha256: Digest | None
    validated_answer_digest_sha256: Digest | None
    stages: tuple[RagStageReceiptV1, ...] = Field(min_length=9, max_length=9)
    final_outcome: RagFinalOutcome
    reason_code: str = Field(default="", max_length=64)
    physical_attempt_count: Annotated[int, Field(ge=0, le=1, strict=True)]
    receipt_hash_sha256: Digest

    @model_validator(mode="after")
    def _stage_order(self) -> "GovernedRagReceiptV1":
        names = tuple(s.stage for s in self.stages)
        if names != RAG_STAGE_ORDER:
            raise ValueError("stages must appear in the exact nine-stage order")
        if len(set(self.pre_injection_citation_ids)) != len(self.pre_injection_citation_ids):
            raise ValueError("pre_injection_citation_ids must be duplicate-free")
        if len(set(self.post_injection_citation_ids)) != len(self.post_injection_citation_ids):
            raise ValueError("post_injection_citation_ids must be duplicate-free")
        if not set(self.post_injection_citation_ids) <= set(self.pre_injection_citation_ids):
            raise ValueError("post_injection_citation_ids must be a subset of pre_injection_citation_ids")
        # Amendment 1 / A1-F6 - BOTH positive outcomes (ANSWERED and
        # ABSTAINED) require the full lineage/terminal grammar below, never
        # just ANSWERED. The reviewer's exact probe (an ABSTAINED receipt
        # with physical_attempt_count=0, null minimization/validated-answer
        # digests, and a non-empty positive reason_code) is rejected by every
        # branch here - each check applies to the SET, not to ANSWERED alone.
        POSITIVE_OUTCOMES = (RagFinalOutcome.ANSWERED, RagFinalOutcome.ABSTAINED)
        if self.final_outcome in POSITIVE_OUTCOMES:
            if self.reason_code != "":
                raise ValueError(f"{self.final_outcome} requires an empty receipt reason_code")
            if self.physical_attempt_count != 1:
                raise ValueError(f"{self.final_outcome} requires exactly one physical attempt")
            if (
                self.minimization_ruleset_digest_sha256 is None
                or self.minimization_input_digest_sha256 is None
                or self.minimization_output_digest_sha256 is None
            ):
                raise ValueError(
                    f"{self.final_outcome} requires non-null minimization ruleset/input/output digests"
                )
            if self.minimization_retained_count <= 0:
                raise ValueError(f"{self.final_outcome} requires minimization_retained_count > 0")
            if self.index_build_digest_sha256 is None or self.context_digest_sha256 is None:
                raise ValueError(f"{self.final_outcome} requires a non-null index/context digest")
            if self.gateway_request_digest_sha256 is None or self.output_schema_digest_sha256 is None:
                raise ValueError(f"{self.final_outcome} requires non-null gateway-request/output-schema digests")
            if (
                self.gateway_receipt_output_digest_sha256 is None
                or self.provider_response_digest_sha256 is None
                or self.validated_answer_digest_sha256 is None
            ):
                raise ValueError(
                    f"{self.final_outcome} requires non-null gateway-receipt-output/provider-response/"
                    "validated-answer digests"
                )
        elif self.final_outcome is RagFinalOutcome.OUTPUT_VALIDATION_FAILED:
            if self.physical_attempt_count != 1:
                raise ValueError("OUTPUT_VALIDATION_FAILED must preserve exactly one physical attempt")
        elif self.final_outcome is RagFinalOutcome.GATEWAY_NOT_ACCEPTED:
            if self.physical_attempt_count not in (0, 1):
                raise ValueError("GATEWAY_NOT_ACCEPTED must preserve zero or one physical attempts")
        elif self.physical_attempt_count != 0:
            raise ValueError(f"{self.final_outcome} requires zero physical attempts")
        self._terminal_stage_matches_final_outcome()
        self._hash_matches_canonical_body()
        return self

    def _terminal_stage_matches_final_outcome(self) -> None:
        """P4A2-REV-F6 - full terminal grammar consistency: exactly the
        stages up to and including the true terminal stage may be non-PASS,
        every stage after it must be NOT_RUN, and (for a non-positive
        outcome) the terminal FAIL stage's mapped outcome must match
        ``final_outcome`` exactly - so a caller cannot construct e.g. an
        ANSWERED outcome alongside a FAIL stage, or a stage history whose
        real terminal stage disagrees with the declared outcome."""
        fail_indices = [i for i, s in enumerate(self.stages) if s.outcome is RagStageOutcome.FAIL]
        if self.final_outcome in (RagFinalOutcome.ANSWERED, RagFinalOutcome.ABSTAINED):
            if fail_indices:
                raise ValueError(f"{self.final_outcome} must not carry any FAIL stage")
            if any(s.outcome is not RagStageOutcome.PASS for s in self.stages):
                raise ValueError(f"{self.final_outcome} requires every stage PASS")
            return
        if len(fail_indices) != 1:
            raise ValueError("a non-positive outcome requires exactly one FAIL stage")
        idx = fail_indices[0]
        if any(s.outcome is not RagStageOutcome.PASS for s in self.stages[:idx]):
            raise ValueError("every stage before the terminal FAIL must be PASS")
        if any(s.outcome is not RagStageOutcome.NOT_RUN for s in self.stages[idx + 1 :]):
            raise ValueError("every stage after the terminal FAIL must be NOT_RUN")
        expected_stage = _OUTCOME_TERMINAL_STAGE.get(self.final_outcome)
        if expected_stage is not None and self.stages[idx].stage is not expected_stage:
            raise ValueError(f"{self.final_outcome} terminal stage must be {expected_stage}")
        if self.stages[idx].reason_code != self.reason_code:
            raise ValueError("the terminal stage's reason_code must equal the receipt's own reason_code")

    def _hash_matches_canonical_body(self) -> None:
        """P4A2-REV-F6 - the model itself recomputes ``receipt_hash_sha256``
        from the canonical dump of every OTHER field and rejects any
        mismatch, so a direct-constructed forged hash (or a ``model_construct``
        bypass that skips the builder) is caught here rather than trusted
        from the builder alone."""
        dump = self.model_dump(mode="python")
        dump.pop("receipt_hash_sha256")
        if receipt_hash(dump) != self.receipt_hash_sha256:
            raise ValueError("receipt_hash_sha256 must equal the recomputed canonical receipt hash")


def build_stages(
    *, terminal_stage: RagStage | None, terminal_reason: str = ""
) -> tuple[RagStageReceiptV1, ...]:
    """Build the exact nine-stage grammar: every stage up to and including
    ``terminal_stage`` is PASS/FAIL (FAIL only at the terminal stage itself,
    with a non-empty reason), every later stage is NOT_RUN. ``terminal_stage
    is None`` means every stage passed (the full positive ANSWERED path)."""
    stages: list[RagStageReceiptV1] = []
    seen_terminal = False
    for stage in RAG_STAGE_ORDER:
        if terminal_stage is not None and stage == terminal_stage:
            stages.append(RagStageReceiptV1(stage=stage, outcome=RagStageOutcome.FAIL, reason_code=terminal_reason))
            seen_terminal = True
        elif seen_terminal:
            stages.append(RagStageReceiptV1(stage=stage, outcome=RagStageOutcome.NOT_RUN))
        else:
            stages.append(RagStageReceiptV1(stage=stage, outcome=RagStageOutcome.PASS))
    return tuple(stages)


def build_receipt(**fields) -> GovernedRagReceiptV1:
    """Construct the sanitized receipt, recomputing ``receipt_hash_sha256``
    from the canonical dump of every other field (never caller-trusted).
    The model's own ``_hash_matches_canonical_body`` validator (P4A2-REV-F6)
    independently re-verifies this on every construction, including this
    one - this builder is a convenience, not the sole source of truth."""
    dump_fields = dict(fields)
    dump_fields["receipt_hash_sha256"] = "0" * 64
    model = GovernedRagReceiptV1.model_construct(**dump_fields)
    dump = model.model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    final_fields = dict(fields)
    final_fields["receipt_hash_sha256"] = receipt_hash(dump)
    return GovernedRagReceiptV1(**final_fields)


__all__ = [
    "build_stages",
    "build_receipt",
    "ENCODER_ID_LITERAL",
    "RagFinalOutcome",
    "RagStage",
    "RAG_STAGE_ORDER",
    "RagStageOutcome",
    "RagStageReceiptV1",
    "GovernedRagReceiptV1",
]
