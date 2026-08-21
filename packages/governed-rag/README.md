# governed-rag

Pure P4-A2 governed RAG composition layer (tranche
`P4A2-GOVERNED-RAG-2026-08-21`).

Consumes only a positive P4-A1 `EvidenceAvailableV1` result (never a raw
query, corpus or credential) and calls an injected, already-configured
`ai_gateway.service.AIGateway` instance's `execute` method zero or one time.
Depends only on the standard library, Pydantic, `governed-retrieval`,
`retrieval-contracts` and `ai-gateway` - see `pyproject.toml`. Imports no
provider SDK, HTTP client, environment, secret, database or hidden CVF Core.

## What this package does

1. Recomputes and verifies every P4-A1 receipt/handoff/projection/citation/
   evidence-set binding (never trusts caller relabeling).
2. Builds and validates an ephemeral, in-memory semantic index over exactly
   the granted P4-A1 projections; a stale/altered/partial index fails closed
   as `STALE_INDEX` with zero gateway attempts.
3. Computes deterministic lexical and semantic component scores using the
   local, dependency-free `PROJECT_CONCEPT_FEATURE_VECTOR_V1` substrate, and
   fuses them 45%/55% with integer arithmetic, ranking by descending fused
   score then ascending citation id.
4. Detects and omits prompt-injection/control-text contaminated evidence
   projections; if every projection is omitted, fails closed as
   `INJECTION_BLOCKED` with zero gateway attempts.
5. Applies `MINIMIZATION_EXTRACTIVE_V1` deterministic extractive
   minimization to the clean evidence, with an independently recomputable
   proof.
6. Assembles a structured, instruction/data-separated context bound to a
   recomputed `context_digest`, and dispatches the injected `AIGateway`
   exactly once.
7. Validates the returned answer's strict schema and citation membership
   against the exact post-omission granted set.
8. Emits a sanitized end-to-end receipt containing only safe ids, hashes,
   versions, counts, outcomes and reason codes.

## What this package does not do

It does not call P4-A1 itself (that is
`workspace_api.application.governed_rag.execute_governed_rag`'s job), does
not open an HTTP route, does not persist any index/answer/audit state, and
does not implement a provider adapter of its own. See
`docs/specs/P4A2_GOVERNED_RAG_SPEC.md` and
`docs/decisions/DESIGN_2026-08-21_P4A2_GOVERNED_RAG.md` for the full
requirement and architecture set this package satisfies.

## Claim boundary

This package proves a bounded application-layer governed-RAG composition
over synthetic/local Project Knowledge with an ephemeral deterministic
semantic index. It does not prove general embeddings, operational-corpus
RAG, durable indexes/audit/memory, a public API/UI, a production provider
adapter, deployment or production readiness.
