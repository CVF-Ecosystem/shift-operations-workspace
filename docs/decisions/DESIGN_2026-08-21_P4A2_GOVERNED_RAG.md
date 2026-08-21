# DESIGN — P4-A2 Governed RAG

- Tranche: `P4A2-GOVERNED-RAG-2026-08-21`
- Phase: `DESIGN`
- Risk: `R2`
- Parent: `INTAKE_REVIEW_PASS`
- Status: `APPROVED_FOR_SPEC`
- Execution base: `4016fc6708844ecea1dedc4e76dfccf2ae314c9e`
- Role transition: `ORCHESTRATOR → DESIGN_AUTHOR`
- Provider-neutral: `YES`
- Deployment/push authority: `NONE/NONE`

## Decision

Build a new pure package, `packages/governed-rag`, and one application-layer
composition function under `workspace_api.application`. The application owner
calls the reviewed P4-A1 retrieval function and immediately passes only its
positive `EvidenceAvailableV1` result into the new package. The package may
call only an injected, already-configured `AIGateway` instance; it may not
import a provider implementation, SDK, HTTP client, environment credential,
database or hidden CVF Core.

No HTTP route is added. This is a callable application boundary, not a public
API, background service, durable index, production provider adapter or
deployment.

## Mandatory execution order

1. Validate the strict RAG request, policy and execution facts.
2. Execute P4-A1 governed retrieval using the original normalized query.
3. If the result is not `EvidenceAvailableV1`, return the corresponding
   fail-closed RAG result with zero gateway/provider attempts.
4. Recompute and verify the P4-A1 receipt, handoff, projection, citation and
   evidence-set bindings; accept no caller relabeling of classification,
   minimization, placement or provider authority.
5. Build or validate an ephemeral semantic index whose entries are a strict
   subset of the granted projections.
6. Detect stale/mismatched index identity against the current immutable
   projection set; fail closed with zero provider attempts.
7. Compute deterministic lexical and semantic component scores, fuse and
   rerank using fixed integer arithmetic and a stable citation-id tie break.
8. Detect prompt-injection/control-text patterns in each evidence projection;
   omit contaminated projections and fail closed if none remain.
9. Apply deterministic extractive minimization to INTERNAL evidence and emit
   independently recomputable minimization facts. Never mutate or relabel the
   P4-A1 handoff itself.
10. Assemble a structured instruction/data-separated context, strict answer
    schema and `GatewayRequest`; bind the exact context digest and require
    positive minimization evidence for external placement.
11. Invoke the injected instance's `AIGateway.execute` exactly once at most.
12. For an accepted gateway result, validate answer/abstention invariants and
    every returned citation against the exact post-omission granted set.
13. Emit a sanitized end-to-end RAG receipt. Invalid citations, uncited
    claims, schema drift, lineage mismatch or gateway failure never become an
    accepted answer and never trigger a retry.

## Composition and dependency direction

```text
workspace_api.application.governed_rag
  ├─ calls workspace_api.application.governed_retrieval
  ├─ passes positive EvidenceAvailableV1 only
  └─ calls governed_rag.GovernedRAG.execute
         └─ calls injected ai_gateway.AIGateway.execute at most once
                └─ owns the only provider dispatch
```

`governed-rag` depends on the public contracts of `governed-retrieval` and
`ai-gateway`. Neither parent imports `governed-rag`; no cycle is permitted.
The application function owns the query/result continuity so an unrelated
positive retrieval result cannot be substituted for another query.

## Semantic substrate and hybrid reranking

The semantic substrate is local, deterministic and dependency-free:
`PROJECT_CONCEPT_FEATURE_VECTOR_V1`. It produces a sparse binary feature
vector from normalized tokens, bounded character trigrams and a small,
versioned project-domain concept lexicon. The lexicon maps reviewed operations
synonyms to canonical concepts and has a canonical SHA-256 digest.

This is deliberately not a general-purpose embedding claim. Acceptance must
include a zero-exact-token-overlap fixture whose reviewed synonym mapping
changes semantic ranking, proving that the semantic component is not merely a
duplicate lexical score.

- lexical and semantic scores are integers in `[0, 1_000_000]`;
- fusion is `45% lexical + 55% semantic`, using integer arithmetic only;
- descending fused score is followed by ascending citation id;
- duplicate citation ids or duplicate projection identities fail closed;
- reranking can reorder or narrow only the granted P4-A1 projections and can
  never introduce a new corpus, source, record, chunk or citation.

## Ephemeral index and stale detection

No database or persistent vector store is introduced. Each index entry binds:

- corpus id and authorization-scope digest;
- citation id, source/content/snippet/chunk digests and version binding;
- field selector, truth class and source cutoff;
- semantic encoder id/version and lexicon digest;
- sparse feature-vector digest;
- index-build digest and ordered evidence-set hash.

The default index is rebuilt in memory for each execution. Tests and callers
may inject a prebuilt immutable index only through the strict contract; the
service recomputes all identities against the current P4-A1 projections before
ranking. Missing, partial, extra, altered, incompatible or stale entries
return `STALE_INDEX` with zero provider attempts. There is no silent lexical
fallback after stale detection. A clean explicitly configured `LEXICAL_ONLY`
mode may be tested as a separate no-semantic outcome, but cannot satisfy or be
reported as P4-A2 hybrid-RAG acceptance.

## Prompt-injection isolation

Retrieved text is untrusted evidence data. A versioned detector rejects
control characters and marks bounded prompt/control phrases, role-marker
patterns, delimiter escapes and tool/secret-exfiltration instructions. Marked
projections are omitted before minimization and context construction; their
citation ids and safe reason codes are recorded. If all evidence is omitted,
the result is `INJECTION_BLOCKED` and the gateway is not called.

The dispatched context is a closed object with separate
`instruction_contract` and `evidence_records` fields. Evidence text can never
populate or alter the instruction field. The output contract contains no
free-form top-level prose.

## Minimization and placement

P4-A1's `NOT_PROVEN` handoff remains immutable. P4-A2 independently produces
`MINIMIZATION_EXTRACTIVE_V1` evidence by:

- allowing only citation id plus bounded extractive sentences from a clean
  projection;
- selecting only sentences containing query or semantic-concept features;
- applying fixed per-record and total codepoint/UTF-8/token ceilings;
- rejecting secret/credential/PII-like patterns and Unicode controls;
- recording input/output digests, algorithm version, ruleset digest,
  omitted citations and byte/token counts without recording bodies.

External placement is allowed only when this proof recomputes successfully
and at least one minimized record remains. LOCAL/ENTERPRISE placement still
passes through the real gateway data-scope gate. The composition does not
change canonical operational truth and does not persist generated output.

## Answer and citation contract

The only provider-accepted output is a closed object:

- `status`: `ANSWER` or `ABSTAIN`;
- `claims`: zero to eight objects containing only a bounded `text` and one to
  four duplicate-free `citation_ids`;
- `abstention_reason`: bounded string, empty for `ANSWER`.

`ANSWER` requires at least one claim and every claim requires at least one
citation. `ABSTAIN` requires no claims and a non-empty reason. Every citation
must be a member of the exact post-injection/minimization granted set. Unknown,
duplicate or omitted citations and uncited claims return
`OUTPUT_VALIDATION_FAILED`. The raw provider output is never a canonical
record and is not persisted by this tranche.

## Receipt and lineage design

The sanitized receipt binds, without bodies or secrets:

- normalized-query digest;
- P4-A1 retrieval receipt and evidence-set hashes;
- authorization-scope and corpus identity;
- index-build, encoder, lexicon and score-policy digests;
- ordered pre/post-injection citation sets and omission reason codes;
- minimization input/output/ruleset/context digests and size counts;
- output-schema, gateway request/receipt and provider-response digests;
- validated answer digest, final outcome and physical attempt count.

Pre-gateway failures record zero attempts. Once the gateway is invoked, its
receipt is authoritative for zero/one attempt; a post-gateway RAG rejection
preserves that count and never retries.

## Live-evidence design

Component tests may use deterministic fakes only for mechanics and must label
them non-proof. A later BUILD governance claim requires one fresh live run
through the real application composition, P4-A1 positive retrieval, P4-A2
index/injection/minimization/context path and the real P4-A gateway.

The runner first proves negative/stale/injection/minimization/citation setup
branches have zero physical attempts, then may make exactly one HTTPS POST for
a harmless synthetic Project Knowledge fixture. Local semantic/index work
makes no provider call. The previously accepted P4-A receipt is pattern
evidence only and cannot be reused as P4-A2 proof. Failure is retained as
`LIVE_EVIDENCE_BLOCKED`; no retry is authorized.

## Alternatives rejected

- External embeddings, rerankers and vector databases add network,
  credential, persistence, deletion and deployment boundaries.
- A second LLM/reranker call violates the one-attempt ceiling.
- Client-side RAG or a direct provider SDK bypasses P4-A1/P4-A ownership.
- Passing raw P4-A1 INTERNAL snippets with `minimization_proven=True` would
  falsify the accepted handoff.
- Prompt-only requests for citations are insufficient without strict schema
  and post-dispatch membership validation.
- Persisting the index or answer would require separate lifecycle, correction,
  deletion, audit and database authority.

## Rollback and claim boundary

All BUILD artifacts are ordinary tracked edits plus one irreversible provider
attempt recorded in a sanitized receipt. On failure, preserve the worktree and
evidence for review; do not reset, delete, commit or push.

This design may prove a bounded application-layer governed-RAG composition
over synthetic/local Project Knowledge with an ephemeral deterministic
semantic index. It does not prove general embeddings, operational-corpus RAG,
durable indexes/audit/memory, a public API/UI, P4-B production adapter,
deployment or production readiness.

## Design disposition

`APPROVED_FOR_SPEC`. DESIGN grants SPEC and Work Order authoring only. BUILD
requires a separate authorization review and must be performed by an external
`IMPLEMENTATION_WORKER`.
