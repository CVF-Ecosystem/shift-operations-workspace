"""Strict answer schema plus post-dispatch citation-membership validation
(SPEC R13), plus :class:`ReceiptContext` (SPEC R15).

The gateway's own ``validate_output`` (SPEC R9 of the ai-gateway SPEC)
already enforces the JSON-schema shape declared in :data:`ANSWER_JSON_SCHEMA`
before this module ever runs; this module additionally builds/validates the
strict :class:`~governed_rag.models.GovernedRagAnswerV1` Pydantic model from
that accepted output and enforces the one invariant a JSON Schema alone
cannot express: every cited id must be an exact member of the precise
post-injection/minimization granted citation-id set for THIS execution.
Unknown, duplicate or omitted citations and uncited claims all raise
:class:`~governed_rag.errors.OutputValidationFailedError` fail-closed.

:class:`ReceiptContext` lives here (rather than ``receipts.py``, its more
obvious home) purely to keep every file in this package under the
repository's file-size ceiling - it has no answer-validation logic of its
own, only receipt assembly, exactly like ``receipts.py``'s own documented
rationale for colocating its models away from ``models.py``.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field, ValidationError, model_validator
from retrieval_contracts.common import Digest, StrictModel

from .errors import OutputValidationFailedError
from .hashing import aggregate_minimization_digest, gateway_request_safe_digest
from .models import (
    MAX_ABSTENTION_REASON_CODEPOINTS,
    MAX_CITATIONS_PER_CLAIM,
    MAX_CLAIM_TEXT_CODEPOINTS,
    MAX_CLAIMS,
)
from .receipts import GovernedRagReceiptV1, RagFinalOutcome, RagStage, build_receipt, build_stages


class AnswerStatus(StrEnum):
    ANSWER = "ANSWER"
    ABSTAIN = "ABSTAIN"


class ClaimV1(StrictModel):
    """SPEC R13 - one bounded, cited claim."""

    text: Annotated[str, Field(min_length=1, max_length=MAX_CLAIM_TEXT_CODEPOINTS)]
    citation_ids: tuple[Digest, ...] = Field(min_length=1, max_length=MAX_CITATIONS_PER_CLAIM)

    @model_validator(mode="after")
    def _citations_duplicate_free(self) -> "ClaimV1":
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("citation_ids must be duplicate-free")
        return self


class GovernedRagAnswerV1(StrictModel):
    """SPEC R13 - the exact strict, closed answer schema the gateway output
    must satisfy. Post-dispatch validation additionally enforces citation
    membership against the exact post-omission granted set (done by
    :func:`validate_citation_membership`, not this model, since the granted
    set is execution-scoped)."""

    status: AnswerStatus
    claims: tuple[ClaimV1, ...] = Field(max_length=MAX_CLAIMS)
    abstention_reason: str = Field(max_length=MAX_ABSTENTION_REASON_CODEPOINTS, default="")

    @model_validator(mode="after")
    def _status_invariants(self) -> "GovernedRagAnswerV1":
        if self.status is AnswerStatus.ANSWER:
            if not self.claims:
                raise ValueError("ANSWER requires at least one claim")
            if self.abstention_reason:
                raise ValueError("ANSWER must not carry an abstention_reason")
        else:
            if self.claims:
                raise ValueError("ABSTAIN must carry no claims")
            if not self.abstention_reason:
                raise ValueError("ABSTAIN requires a non-empty abstention_reason")
        return self


ANSWER_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "claims", "abstention_reason"],
    "properties": {
        "status": {"type": "string", "enum": ["ANSWER", "ABSTAIN"]},
        "claims": {
            "type": "array",
            "maxItems": MAX_CLAIMS,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "citation_ids"],
                "properties": {
                    "text": {"type": "string", "minLength": 1, "maxLength": 512},
                    "citation_ids": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": MAX_CITATIONS_PER_CLAIM,
                        "items": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    },
                },
            },
        },
        "abstention_reason": {"type": "string", "maxLength": 256},
    },
}


def parse_answer(output: dict[str, Any]) -> GovernedRagAnswerV1:
    """Build the strict model from accepted gateway JSON output.

    ``output`` is always plain JSON (already schema-validated by the
    gateway's own dependency-free ``validate_output`` against
    ``ANSWER_JSON_SCHEMA`` before this ever runs): a bare string status and
    list-typed arrays, never a Python enum or tuple. ``strict=False`` here
    permits exactly that JSON-shape coercion (string -> enum member,
    list -> tuple) while every other field still enforces its own bounds
    (length, pattern, closed enum membership) and every cross-field
    ANSWER/ABSTAIN/duplicate-citation invariant in
    :class:`~governed_rag.models.GovernedRagAnswerV1` still runs
    unconditionally - this is JSON-shape leniency only, never a widening of
    what content is accepted.

    Raises :class:`OutputValidationFailedError` on any structural or
    invariant violation (unknown/missing fields, bad status/claim shape,
    ANSWER/ABSTAIN invariant violation, duplicate citation ids).
    """
    try:
        return GovernedRagAnswerV1.model_validate(output, strict=False)
    except ValidationError as exc:
        raise OutputValidationFailedError(f"answer schema/invariant violation: {exc.error_count()} error(s)") from exc


def validate_citation_membership(answer: GovernedRagAnswerV1, granted_citation_ids: tuple[str, ...]) -> None:
    """SPEC R13 - every citation id referenced by every claim must be an
    exact member of ``granted_citation_ids`` (the precise post-injection/
    minimization granted set for this execution). Fail-closed on any unknown
    citation; uncited claims are already rejected by the model itself
    (``citation_ids`` has ``min_length=1``)."""
    granted = set(granted_citation_ids)
    for claim in answer.claims:
        unknown = [cid for cid in claim.citation_ids if cid not in granted]
        if unknown:
            raise OutputValidationFailedError("answer cited an id outside the granted citation set")


class ReceiptContext:
    """Collapses ``GovernedRAG``'s negative/positive receipt-building paths
    into one shared builder so ``service.py`` never repeats the same
    dozen-plus ``build_receipt`` keyword arguments three times over (once
    for a pre-index failure, once for a post-index failure, once for the
    final positive receipt)."""

    __slots__ = ("nq_digest", "retrieval_result")

    def __init__(self, *, nq_digest: str, retrieval_result) -> None:
        self.nq_digest = nq_digest
        self.retrieval_result = retrieval_result

    def build(
        self, *, index=None, pre_injection_ids: tuple[str, ...] = (),
        post_injection_ids: tuple[str, ...] = (), injection_omissions: tuple = (),
        minimization_proof=None, assembled=None, gateway_request=None,
        terminal_stage: RagStage | None, final_outcome: RagFinalOutcome, reason_code: str,
        physical_attempt_count: int = 0, gateway_receipt_output_digest_sha256: str | None = None,
        provider_response_digest_sha256: str | None = None, validated_answer_digest_sha256: str | None = None,
        encoder_version: str, lexicon_digest_sha256: str, score_policy_digest_sha256: str,
        output_schema_digest_sha256_fn=None,
    ) -> GovernedRagReceiptV1:
        rr = self.retrieval_result
        auth_scope = (
            index.authorization_scope_digest_sha256 if index is not None
            else (getattr(rr.receipt, "authorization_scope_digest_sha256", None) or "0" * 64)
        )
        output_schema_digest = output_schema_digest_sha256_fn() if output_schema_digest_sha256_fn else None
        return build_receipt(
            normalized_query_digest_sha256=self.nq_digest,
            retrieval_receipt_hash_sha256=rr.receipt.receipt_hash_sha256,
            retrieval_evidence_set_hash_sha256=rr.receipt.evidence_set_hash_sha256 or ("0" * 64),
            authorization_scope_digest_sha256=auth_scope,
            corpus_id=str(rr.receipt.corpus_id or "UNKNOWN"),
            index_build_digest_sha256=index.index_build_digest_sha256 if index is not None else None,
            encoder_version=encoder_version,
            lexicon_digest_sha256=lexicon_digest_sha256,
            score_policy_digest_sha256=score_policy_digest_sha256,
            pre_injection_citation_ids=pre_injection_ids,
            post_injection_citation_ids=post_injection_ids,
            injection_omissions=injection_omissions,
            minimization_ruleset_digest_sha256=(
                minimization_proof.ruleset_digest_sha256 if minimization_proof is not None else None
            ),
            # P4A2-REV-F6 - derive the aggregate ordered minimization input/
            # output digests FROM the individual per-record proofs
            # (recomputed here, never caller-supplied), over the exact
            # per-record digest order minimize_all produced.
            minimization_input_digest_sha256=(
                aggregate_minimization_digest(tuple(r.input_digest_sha256 for r in minimization_proof.records))
                if minimization_proof is not None and minimization_proof.records else None
            ),
            minimization_output_digest_sha256=(
                aggregate_minimization_digest(
                    tuple(r.output_digest_sha256 for r in minimization_proof.records if r.output_digest_sha256 is not None)
                )
                if minimization_proof is not None
                and any(r.output_digest_sha256 is not None for r in minimization_proof.records)
                else None
            ),
            minimization_retained_count=minimization_proof.retained_count if minimization_proof is not None else 0,
            minimization_omitted_count=minimization_proof.omitted_count if minimization_proof is not None else 0,
            context_digest_sha256=assembled.facts.context_digest_sha256 if assembled is not None else None,
            output_schema_digest_sha256=output_schema_digest,
            # P4A2-REV-F6 - bind a canonical safe projection of the REAL
            # dispatched request (context, provider/model, placement,
            # schema, budget, termination, timeout, output-token facts),
            # not just the context digest alone.
            gateway_request_digest_sha256=(
                gateway_request_safe_digest(
                    context_digest_sha256=gateway_request.context_facts.context_digest,
                    provider_id=gateway_request.provider_id,
                    model_id=gateway_request.model_id,
                    placement=gateway_request.placement.value,
                    output_schema_digest_sha256=output_schema_digest or "",
                    per_request_token_limit=gateway_request.budget_facts.per_request_token_limit,
                    terminate_when=gateway_request.termination_facts.terminate_when,
                    timeout_seconds=gateway_request.timeout_seconds,
                    max_output_tokens=gateway_request.max_output_tokens,
                )
                if gateway_request is not None else None
            ),
            gateway_receipt_output_digest_sha256=gateway_receipt_output_digest_sha256,
            provider_response_digest_sha256=provider_response_digest_sha256,
            validated_answer_digest_sha256=validated_answer_digest_sha256,
            stages=build_stages(terminal_stage=terminal_stage, terminal_reason=reason_code),
            final_outcome=final_outcome,
            reason_code=reason_code,
            physical_attempt_count=physical_attempt_count,
        )
