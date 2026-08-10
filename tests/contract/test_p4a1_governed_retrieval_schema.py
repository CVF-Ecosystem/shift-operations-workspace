"""SPEC R1/R9 - governed_retrieval.schema.json committed-vs-fresh-generation
byte parity and structural closed-schema proofs (AC-01, AC-09, AC-11). Also
covers F7 (binding rejects empty/tampered construction), RR2-F1 (coordinated
tampering), and F10 (N/N+1 boundaries without silent truncation)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from governed_retrieval.evidence_models import CitationV1
from governed_retrieval.receipt_models import FutureContextHandoffV1, RetrievalReceiptV1
from governed_retrieval.request_models import GovernedRetrievalRequestV1
from governed_retrieval.result_models import AccessDeniedV1, EvidenceAvailableV1, GovernedRetrievalResultV1, NoEvidenceV1

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "packages" / "governed-retrieval" / "contracts" / "governed_retrieval.schema.json"

class _SchemaRoot(BaseModel):
    request: GovernedRetrievalRequestV1
    result: GovernedRetrievalResultV1
    receipt: RetrievalReceiptV1

def generated_schema_bytes() -> bytes:
    schema = _SchemaRoot.model_json_schema()
    schema["title"] = "GovernedRetrievalV1"
    return (json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")

def test_committed_schema_matches_fresh_generation_byte_for_byte() -> None:
    assert SCHEMA.read_bytes() == generated_schema_bytes()

def test_schema_is_valid_json_with_expected_title() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["title"] == "GovernedRetrievalV1"
    assert "$defs" in schema

def test_every_object_definition_forbids_additional_properties() -> None:
    """Closed-schema proof: every V1 model rejects unknown fields."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    offenders = [
        name for name, d in schema["$defs"].items()
        if d.get("type") == "object" and "properties" in d and d.get("additionalProperties") is not False
    ]
    assert offenders == [], f"open object schemas found: {offenders}"

def test_result_union_defs_include_all_ten_variants() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    expected = {
        "EvidenceAvailableV1", "NoEvidenceV1", "AccessDeniedV1", "CorpusUnavailableV1", "StaleEvidenceV1",
        "RetrievalLimitExceededV1", "RetrievalStoppedV1", "ContextBudgetExceededV1", "InvalidRequestV1",
        "InvariantFailureV1",
    }
    assert expected <= set(schema["$defs"].keys())

_EXACT_FIELD_SETS = {
    "GovernedRetrievalRequestV1": {"contract_version", "query", "corpus_id", "filters", "result_limit", "context_budget"},
    "RetrievalReceiptV1": {
        "contract_version", "receipt_id", "retrieval_correlation_id", "started_at_utc", "finished_at_utc",
        "source_cutoff_utc", "elapsed_ms", "corpus_id", "authorization_scope_digest_sha256", "stages",
        "final_outcome", "requested_limits", "applied_limits", "counts", "termination", "citation_ids",
        "evidence_set_hash_sha256", "receipt_hash_sha256",
    },
    "CitationV1": {
        "chunk_id", "content_digest_sha256", "source_digest_sha256", "version", "truth_class", "record_type",
        "record_id", "source_id", "field_selector", "revalidation_token", "source_cutoff_utc",
        "snippet_digest_sha256", "snippet_start_codepoint", "snippet_end_codepoint",
    },
    "EvidenceProjectionV1": {
        "citation", "truth_class", "field_selector", "sensitivity", "content_snippet", "snippet_start_codepoint",
        "snippet_end_codepoint", "snippet_digest_sha256", "projection_complete",
    },
    "FutureContextHandoffV1": {
        "retrieval_receipt_hash_sha256", "evidence_set_hash_sha256", "citation_ids", "classifications",
        "sensitivities", "serialized_context_bytes", "snippet_codepoints", "projection_count",
        "estimated_input_tokens", "token_estimate_method", "applied_limits", "elapsed_ms", "configured_timeout_ms",
        "timed_out", "cancelled", "minimization_evidence_status", "placement_enforcement_status",
        "runtime_caller_status", "provider_attempt_authorized", "provider_attempts",
    },
}

def test_every_v1_schema_has_the_exact_declared_field_set() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    for name, expected in _EXACT_FIELD_SETS.items():
        assert set(schema["$defs"][name]["properties"]) == expected, name

# --- F7: evidence/receipt/result binding rejects empty/tampered/mismatched
# construction ---

def test_evidence_available_rejects_empty_projections_tuple() -> None:
    """F7: at least one positive projection is required."""
    receipt = _minimal_negative_receipt("EVIDENCE_AVAILABLE", with_evidence=True)
    with pytest.raises(ValidationError):
        EvidenceAvailableV1(receipt=receipt, projections=(), future_context_handoff=_minimal_handoff())

def test_no_evidence_variant_structurally_omits_projections_field() -> None:
    """F7: NoEvidenceV1 has no projections/handoff field; smuggling one in
    is rejected by strict extra-field forbidding."""
    with pytest.raises(ValidationError):
        NoEvidenceV1(receipt=_minimal_negative_receipt("NO_EVIDENCE"), projections=())

def test_access_denied_cannot_be_constructed_from_a_no_evidence_receipt_type() -> None:
    """F7: every negative variant's `outcome` literal is fixed by its own
    schema - a caller cannot construct AccessDeniedV1 with NO_EVIDENCE."""
    with pytest.raises(ValidationError):
        AccessDeniedV1.model_validate({"outcome": "NO_EVIDENCE", "receipt": _minimal_negative_receipt("NO_EVIDENCE")})

def _consistent_evidence_available():
    """RR2-F1/RR2-F6: a self-consistent EvidenceAvailableV1 so callers can
    tamper one field and prove every OTHER cross-check still catches it."""
    import hashlib
    from governed_retrieval.evidence_models import EvidenceProjectionV1
    from governed_retrieval.hashing import citation_id, evidence_set_hash, receipt_hash
    from governed_retrieval.projection import estimate_tokens, serialized_projection_bytes

    snippet = "hello"
    citation = _citation(snippet_digest_sha256=hashlib.sha256(snippet.encode("utf-8")).hexdigest())
    projection = EvidenceProjectionV1(
        citation=citation, truth_class=citation.truth_class, field_selector=citation.field_selector,
        sensitivity="INTERNAL", content_snippet=snippet, snippet_start_codepoint=0,
        snippet_end_codepoint=len(snippet), snippet_digest_sha256=citation.snippet_digest_sha256,
        projection_complete=True,
    )
    c_dump, p_dump = citation.model_dump(mode="python"), projection.model_dump(mode="python")
    cid = citation_id(c_dump)
    ev_hash = evidence_set_hash([c_dump], [p_dump])
    serialized_bytes = serialized_projection_bytes([p_dump])
    tokens = estimate_tokens(serialized_bytes)
    fields = _minimal_negative_receipt("EVIDENCE_AVAILABLE", with_evidence=True).model_dump(mode="python")
    fields.update(citation_ids=(cid,), evidence_set_hash_sha256=ev_hash)
    fields["counts"] = dict(fields["counts"], projections_emitted=1)
    fields.pop("receipt_hash_sha256")
    fields["receipt_hash_sha256"] = receipt_hash(fields)
    receipt = RetrievalReceiptV1(**fields)
    handoff = FutureContextHandoffV1(
        retrieval_receipt_hash_sha256=receipt.receipt_hash_sha256, evidence_set_hash_sha256=ev_hash,
        citation_ids=(cid,), classifications=("INTERNAL",), sensitivities=("INTERNAL",),
        serialized_context_bytes=serialized_bytes, snippet_codepoints=len(snippet), projection_count=1,
        estimated_input_tokens=tokens, applied_limits=_limits(), elapsed_ms=receipt.elapsed_ms,
        configured_timeout_ms=1000, timed_out=False, cancelled=False,
    )
    return receipt, projection, handoff

def test_coordinated_evidence_hash_tampering_rejected_even_with_correct_receipt_hash() -> None:
    """RR2-F1/RR2-F6/Amendment 4 5.5.6-7: tampering one field, even with a
    correct OUTER receipt hash, is still rejected - every Amendment 3
    handoff mismatch class (serialized bytes, token estimate, projection
    count, classification, sensitivity, applied limit, elapsed, termination,
    evidence hash) and the receipt hash itself are independently
    cross-checked; a coordinated attacker who fixes only one side still
    fails on every other check."""
    from governed_retrieval.hashing import receipt_hash

    receipt, projection, handoff = _consistent_evidence_available()
    EvidenceAvailableV1(receipt=receipt, projections=(projection,), future_context_handoff=handoff)  # sanity
    updates = (
        {"serialized_context_bytes": handoff.serialized_context_bytes + 1},
        {"estimated_input_tokens": handoff.estimated_input_tokens + 1},
        {"evidence_set_hash_sha256": "b" * 64},
        {"projection_count": 2},
        {"classifications": ("PUBLIC",)},
        {"sensitivities": ("PUBLIC",)},
        {"elapsed_ms": handoff.elapsed_ms + 1},
        {"configured_timeout_ms": handoff.configured_timeout_ms + 1},
        {"timed_out": True},
        {"retrieval_receipt_hash_sha256": "c" * 64},
    )
    for update in updates:
        bad_handoff = handoff.model_copy(update=update)
        with pytest.raises(ValidationError):
            EvidenceAvailableV1(receipt=receipt, projections=(projection,), future_context_handoff=bad_handoff)
    bad_applied_limits = handoff.applied_limits.model_copy(update={"result_limit": handoff.applied_limits.result_limit + 1})
    with pytest.raises(ValidationError):
        EvidenceAvailableV1(
            receipt=receipt, projections=(projection,),
            future_context_handoff=handoff.model_copy(update={"applied_limits": bad_applied_limits}),
        )
    fields = receipt.model_dump(mode="python")
    fields["counts"] = dict(fields["counts"], projections_emitted=0)
    fields.pop("receipt_hash_sha256")
    fields["receipt_hash_sha256"] = receipt_hash(fields)  # attacker recomputes ONLY this
    bad_receipt = RetrievalReceiptV1(**fields)
    with pytest.raises(ValidationError):
        EvidenceAvailableV1(receipt=bad_receipt, projections=(projection,), future_context_handoff=handoff)

def test_citation_id_recomputed_not_caller_supplied() -> None:
    """F7: citation_id always recomputes from canonical bytes."""
    from governed_retrieval.hashing import citation_id

    dump = _citation().model_dump(mode="python")
    assert citation_id(dict(dump, chunk_id="b" * 64)) != citation_id(dump)

def _citation(**overrides) -> CitationV1:
    from retrieval_contracts.contract_models import VersionBindingV1
    from retrieval_contracts.enums import RecordType, TruthClass, VersionKind

    fields = dict(
        chunk_id="a" * 64, content_digest_sha256="a" * 64, source_digest_sha256="a" * 64,
        version=VersionBindingV1(kind=VersionKind.UNVERSIONED), truth_class=TruthClass.ADVISORY_SOURCE_EVIDENCE,
        record_type=RecordType.PROJECT_KNOWLEDGE, source_id="doc-1", field_selector="document",
        revalidation_token="a" * 64, source_cutoff_utc=datetime(2026, 8, 10, tzinfo=timezone.utc),
        snippet_digest_sha256="a" * 64, snippet_start_codepoint=0, snippet_end_codepoint=5,
    )
    fields.update(overrides)
    return CitationV1(**fields)
def _all_stages(outcome=None):
    """RR2-F5 - all-PASS for a positive outcome; else MATCHED_AND_RANKED=
    FAIL/NO_EVIDENCE then NOT_RUN (this helper's negative-caller grammar)."""
    from governed_retrieval.enums import FinalOutcome, RetrievalStage, StageOutcome, StageReasonCode
    from governed_retrieval.evidence_models import RetrievalCountsV1, RetrievalStageReceiptV1

    counts = RetrievalCountsV1(
        source_records_read=0, candidates_admitted=0, matches_ranked=0,
        selected_for_revalidation=0, stale_omitted=0, projections_emitted=0, projections_budget_omitted=0,
    )
    negative = outcome is not None and FinalOutcome(outcome) != FinalOutcome.EVIDENCE_AVAILABLE
    seen, stages = False, []
    for s in RetrievalStage:
        if negative and s == RetrievalStage.MATCHED_AND_RANKED:
            out, reason, seen = StageOutcome.FAIL, StageReasonCode.NO_EVIDENCE, True
        elif negative and seen and s != RetrievalStage.RECEIPT_EMITTED:
            out, reason = StageOutcome.NOT_RUN, None
        else:
            out, reason = StageOutcome.PASS, None
        stages.append(RetrievalStageReceiptV1(stage=s, outcome=out, reason_code=reason, safe_counts=counts))
    return tuple(stages)

def _limits():
    from governed_retrieval.evidence_models import RetrievalLimitsV1

    return RetrievalLimitsV1(
        result_limit=10, max_projection_records=4, max_snippet_codepoints=1024,
        max_snippet_utf8_bytes=3072, max_serialized_utf8_bytes=16384, max_estimated_input_tokens=4096,
    )

def _minimal_negative_receipt(outcome: str, with_evidence: bool = False) -> RetrievalReceiptV1:
    from governed_retrieval.enums import FinalOutcome
    from governed_retrieval.evidence_models import RetrievalCountsV1, TerminationFactsV1
    from governed_retrieval.hashing import receipt_hash

    now = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
    counts = RetrievalCountsV1(
        source_records_read=0, candidates_admitted=0, matches_ranked=0,
        selected_for_revalidation=0, stale_omitted=0, projections_emitted=0, projections_budget_omitted=0,
    )
    fields = dict(
        contract_version="1.0", receipt_id=uuid4(), retrieval_correlation_id=uuid4(),
        started_at_utc=now, finished_at_utc=now, source_cutoff_utc=None, elapsed_ms=0,
        corpus_id=None, authorization_scope_digest_sha256=None, stages=_all_stages(outcome),
        final_outcome=FinalOutcome(outcome), requested_limits=None,
        applied_limits=_limits() if with_evidence else None, counts=counts,
        termination=TerminationFactsV1(configured_timeout_ms=1000, timed_out=False, cancelled=False),
        citation_ids=("a" * 64,) if with_evidence else (),
        evidence_set_hash_sha256=("a" * 64) if with_evidence else None,
    )
    dump = RetrievalReceiptV1.model_construct(**fields, receipt_hash_sha256="0" * 64).model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    fields["receipt_hash_sha256"] = receipt_hash(dump)
    return RetrievalReceiptV1(**fields)

def _minimal_handoff() -> FutureContextHandoffV1:
    return FutureContextHandoffV1(
        retrieval_receipt_hash_sha256="a" * 64, evidence_set_hash_sha256="a" * 64,
        citation_ids=("a" * 64,), classifications=("INTERNAL",), sensitivities=("INTERNAL",),
        serialized_context_bytes=10, snippet_codepoints=5, projection_count=1, estimated_input_tokens=5,
        applied_limits=_limits(), elapsed_ms=0, configured_timeout_ms=1000, timed_out=False, cancelled=False,
    )

# --- F10: manifest-entry and document-length boundaries at N/N+1, never a
# silent truncation - see test_p4a1_governed_retrieval_source_limits.py ---
