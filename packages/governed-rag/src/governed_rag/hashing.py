"""Canonical governed-RAG digests (SPEC R6/R7/R8/R10/R11/R15).

All hashes reuse ``retrieval_contracts.canonical.canonical_json_bytes`` -
enums become values, UUIDs lowercase, UTC datetimes use ``Z``, NFC strings
and tuple order are preserved, map keys sort, and floats are forbidden - so
every digest here is byte-deterministic and independently recomputable by
tests from the same explicit preimage helpers the service uses. This module
performs no clock/id creation and no I/O; every input is supplied by the
caller.
"""

from __future__ import annotations

from typing import Any

from retrieval_contracts.canonical import canonical_json_bytes, sha256_bytes


def lexicon_digest(lexicon: dict[str, tuple[str, ...]]) -> str:
    """SPEC R6 - canonical digest of the versioned concept lexicon mapping."""
    preimage = {"lexicon": {concept: list(terms) for concept, terms in lexicon.items()}}
    return sha256_bytes(canonical_json_bytes(preimage))


def feature_vector_digest(feature_ids: tuple[str, ...]) -> str:
    """SPEC R6/R8 - digest of one sparse binary feature vector's active
    feature-id set, order-independent (features are sorted before hashing)."""
    preimage = {"features": sorted(feature_ids)}
    return sha256_bytes(canonical_json_bytes(preimage))


def index_entry_digest(
    *,
    citation_id: str,
    content_digest_sha256: str,
    source_digest_sha256: str,
    version_dump: dict[str, Any],
    field_selector: str,
    truth_class: str,
    source_cutoff_utc: str,
    encoder_id: str,
    encoder_version: str,
    lexicon_digest_sha256: str,
    feature_vector_digest_sha256: str,
) -> str:
    """SPEC R8 - digest of one ephemeral index entry's identity-binding
    fields (the exact DESIGN identity set)."""
    preimage = {
        "citation_id": citation_id,
        "content_digest_sha256": content_digest_sha256,
        "source_digest_sha256": source_digest_sha256,
        "version": version_dump,
        "field_selector": field_selector,
        "truth_class": truth_class,
        "source_cutoff_utc": source_cutoff_utc,
        "encoder_id": encoder_id,
        "encoder_version": encoder_version,
        "lexicon_digest_sha256": lexicon_digest_sha256,
        "feature_vector_digest_sha256": feature_vector_digest_sha256,
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def index_build_digest(
    *, authorization_scope_digest_sha256: str, corpus_id: str, entry_digests: tuple[str, ...]
) -> str:
    """SPEC R8 - digest binding the whole ephemeral index to the exact
    authorization scope, corpus and ordered set of entry digests."""
    preimage = {
        "authorization_scope_digest_sha256": authorization_scope_digest_sha256,
        "corpus_id": corpus_id,
        "entry_digests": list(entry_digests),
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def ordered_evidence_set_hash(citation_ids: tuple[str, ...]) -> str:
    """SPEC R8 - digest of the ordered evidence-set citation ids the index
    was built against (order-preserving, unlike ``lexicon_digest``)."""
    preimage = {"citation_ids": list(citation_ids)}
    return sha256_bytes(canonical_json_bytes(preimage))


def score_policy_digest(*, lexical_weight: int, semantic_weight: int, policy_id: str) -> str:
    """SPEC R7 - digest of the deterministic fusion policy in force."""
    preimage = {
        "policy_id": policy_id,
        "lexical_weight": lexical_weight,
        "semantic_weight": semantic_weight,
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def minimization_input_digest(*, citation_id: str, source_snippet: str) -> str:
    """SPEC R10 - digest of one record's minimization input (citation id plus
    the exact clean source snippet text minimization reads from)."""
    preimage = {"citation_id": citation_id, "source_snippet": source_snippet}
    return sha256_bytes(canonical_json_bytes(preimage))


def minimization_output_digest(*, citation_id: str, minimized_text: str) -> str:
    """SPEC R10 - digest of one record's minimization output text."""
    preimage = {"citation_id": citation_id, "minimized_text": minimized_text}
    return sha256_bytes(canonical_json_bytes(preimage))


def minimization_ruleset_digest(*, ruleset_id: str, version: str) -> str:
    """SPEC R10 - digest of the fixed minimization ruleset identity."""
    preimage = {"ruleset_id": ruleset_id, "version": version}
    return sha256_bytes(canonical_json_bytes(preimage))


def aggregate_minimization_digest(record_digests: tuple[str, ...]) -> str:
    """P4A2-REV-F6 - digest of the ORDERED set of individual per-record
    minimization proof digests (input or output, by whichever tuple the
    caller passes). The receipt's aggregate
    minimization_input/output_digest_sha256 fields are derived from this,
    never caller-supplied directly, so a forged aggregate digest that does
    not correspond to the actual per-record proofs is independently
    detectable by recomputing this same function from those records."""
    preimage = {"record_digests": list(record_digests)}
    return sha256_bytes(canonical_json_bytes(preimage))


def gateway_request_safe_digest(
    *,
    context_digest_sha256: str,
    provider_id: str,
    model_id: str,
    placement: str,
    output_schema_digest_sha256: str,
    per_request_token_limit: int,
    terminate_when: tuple[str, ...],
    timeout_seconds: int,
    max_output_tokens: int,
) -> str:
    """P4A2-REV-F6 - digest binding a canonical SAFE projection of the real
    dispatched ``GatewayRequest``: context, provider/model, placement,
    output schema, budget (token-limit facts only, never spend/cost), the
    termination stop-condition set, timeout and output-token facts. Never
    just the context digest alone - a caller that changed provider_id,
    placement, schema, budget, termination or timeout while keeping the
    same context would previously go undetected."""
    preimage = {
        "context_digest_sha256": context_digest_sha256,
        "provider_id": provider_id,
        "model_id": model_id,
        "placement": placement,
        "output_schema_digest_sha256": output_schema_digest_sha256,
        "per_request_token_limit": per_request_token_limit,
        "terminate_when": list(terminate_when),
        "timeout_seconds": timeout_seconds,
        "max_output_tokens": max_output_tokens,
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def context_digest(
    *, instruction_contract_dump: dict[str, Any], evidence_record_dumps: list[dict[str, Any]]
) -> str:
    """SPEC R11 - digest of the exact assembled context object (instruction
    contract plus ordered minimized evidence records) dispatched to the
    gateway. Recomputed independently rather than trusted from any caller
    value, and cross-checked against ``ContextFacts.context_digest``."""
    preimage = {
        "instruction_contract": instruction_contract_dump,
        "evidence_records": evidence_record_dumps,
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def normalized_query_digest(normalized_query: str) -> str:
    """SPEC R15 - digest of the normalized query text (never the raw text
    itself, which the receipt must not carry)."""
    preimage = {"normalized_query": normalized_query}
    return sha256_bytes(canonical_json_bytes(preimage))


def output_schema_digest(schema: dict[str, Any]) -> str:
    """SPEC R15 - digest of the exact strict answer JSON schema dispatched."""
    return sha256_bytes(canonical_json_bytes({"schema": schema}))


def answer_digest(answer_dump: dict[str, Any]) -> str:
    """SPEC R13/R15 - digest of the validated answer object."""
    return sha256_bytes(canonical_json_bytes({"answer": answer_dump}))


def receipt_hash(receipt_dump_without_hash: dict[str, Any]) -> str:
    """SPEC R15 - receipt hash covers the entire receipt dump with only
    ``receipt_hash_sha256`` omitted (caller must have already omitted it)."""
    return sha256_bytes(canonical_json_bytes(receipt_dump_without_hash))
