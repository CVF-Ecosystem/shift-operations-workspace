# Specification — P4-A2 Governed RAG

- Tranche: `P4A2-GOVERNED-RAG-2026-08-21`
- Phase: `SPEC`
- Risk: `R2`
- Parent: approved P4-A2 DESIGN
- Status: `AUTHORIZATION_REVIEW_PASS`
- Role transition: `DESIGN_AUTHOR → SPEC_AUTHOR`

## Requirements

- `R1` — `governed_rag` is importable on Python >=3.12 with exact Pydantic
  2.10.6 and depends only on standard library, `governed-retrieval`,
  `retrieval-contracts` and `ai-gateway`. It imports no provider implementation,
  SDK, HTTP client, database, app, environment, secret or hidden-Core module.
- `R2` — All request, policy, index, score, minimization, context, answer,
  result and receipt models are strict/frozen, reject unknown fields, use
  immutable defaults and enforce closed enums/bounds. Every JSON schema and
  model reject unsupported or ambiguous shapes fail-closed.
- `R3` — `workspace_api.application.governed_rag.execute_governed_rag` is the
  sole application composition owner. It invokes P4-A1 with the same validated
  query, consumes only `EvidenceAvailableV1`, and never opens an HTTP route or
  persists output/index state.
- `R4` — Every one of P4-A1's nine negative variants short-circuits before
  P4-A2 indexing/context/gateway work as appropriate and yields exactly zero
  gateway/provider attempts. A forged or structurally inconsistent positive
  result fails before gateway invocation.
- `R5` — P4-A2 recomputes positive projection citation ids, content/snippet/
  evidence/receipt/handoff bindings and requires one corpus and the exact
  immutable granted projection set. It never widens corpus, authorization
  scope, source, record, chunk, citation, truth class or field selector.
- `R6` — `PROJECT_CONCEPT_FEATURE_VECTOR_V1` is deterministic, versioned and
  dependency-free. Its lexicon and encoder have canonical digests. At least
  one test proves a reviewed synonym pair with zero exact-token overlap
  changes semantic ranking; the claim is bounded to the project lexicon.
- `R7` — Lexical and semantic component scores are fixed integers from zero to
  one million. Fusion is exactly 45/55 using integer arithmetic. Descending
  fused score then ascending citation id is the sole ordering. Component
  scores, policy id and ordered citation ids are receipt-bound.
- `R8` — Every immutable ephemeral index entry binds the DESIGN identity set.
  Index validation rejects missing/extra/duplicate/partial/altered entries,
  evidence or authorization mismatch, unknown encoder/version/lexicon, or
  index-build digest mismatch as `STALE_INDEX`, with zero attempts. No stale
  path silently falls back to lexical-only behavior.
- `R9` — Injection detection is deterministic and versioned. Controls, role/
  delimiter/tool/secret-exfiltration patterns are detected before context
  assembly. Contaminated projections are omitted with safe codes; an empty
  remainder is `INJECTION_BLOCKED`, zero attempts. Evidence never writes the
  fixed instruction contract.
- `R10` — `MINIMIZATION_EXTRACTIVE_V1` enforces the DESIGN field, sentence,
  pattern and size allowlists. Its proof binds input/output/ruleset/context
  digests, exact counts and omissions and is independently recomputable.
  P4-A1's `NOT_PROVEN` fact is preserved. External INTERNAL placement is
  impossible unless P4-A2's proof is positive and non-empty.
- `R11` — Context construction includes only a fixed instruction contract,
  safe task/query metadata and minimized evidence records. The declared
  `ContextFacts.context_digest` equals the actual context passed to P4-A.
  Context budgets are no wider than both P4-A1 handoff limits and P4-A policy.
- `R12` — `governed_rag.GovernedRAG.execute` receives an injected concrete
  `AIGateway` object and calls that object's `execute` method zero or one time.
  Object-identity/dependency tests prove there is no provider dispatch or
  network client elsewhere in P4-A2 source.
- `R13` — The exact strict answer schema is closed and bounded as in DESIGN.
  Post-gateway validation enforces ANSWER/ABSTAIN invariants, claim bounds,
  duplicate-free citations and exact membership in the post-omission granted
  set. Unknown citations, uncited claims, free-form top-level fields or altered
  answer lineage are never accepted.
- `R14` — Gateway refusals/fallbacks remain non-accepted RAG outcomes with the
  gateway's zero-attempt facts. Provider error, timeout, invalid schema,
  identity mismatch or RAG membership failure after dispatch preserves one
  physical attempt, produces a sanitized failed result and never retries.
- `R15` — The RAG receipt contains only safe ids, hashes, versions, counts,
  outcomes and reason codes listed in DESIGN. It contains no query, prompt,
  evidence/minimized/output body, raw exception, endpoint credential, token,
  authorization header or secret. Every digest is recomputed by tests rather
  than trusted from caller input.
- `R16` — The application function and package never write audit, ledger
  domain state, memory, index or answer persistence. The only ledger mutation
  is P4-A's existing process-local usage reservation/settlement. Generated
  output is advisory and never canonical operational truth.
- `R17` — Operational P4-A1 corpora remain dependency-blocked. Positive BUILD
  and live proof use only an isolated harmless `PROJECT_KNOWLEDGE_LOCAL_V1`
  fixture; no real operational record or secret is transmitted.
- `R18` — Focused tests cover model adversaries, query/result continuity,
  negative union variants, scope widening, semantic synonym behavior,
  deterministic ties, stale index, partial rebuild, injection omission,
  minimization proof, context digest/budget, gateway identity/count, answer
  membership, receipt sanitation and no-network/no-persistence boundaries.
- `R19` — Fakes test mechanics only and are labeled non-proof. A fresh live
  run first demonstrates at least six representative pre-gateway refusals
  with zero physical calls, then executes the full admitted application path
  and makes exactly one provider HTTPS POST through `AIGateway.execute`.
- `R20` — The live runner reads an existing credential from environment only,
  uses the already reviewed model-selection mechanism and evidence-only
  adapter, performs no install/health check/telemetry/retry, and writes one
  sanitized receipt. Missing prerequisites or any failure is
  `LIVE_EVIDENCE_BLOCKED`; no replacement call is allowed without amendment.
- `R21` — Focused, full, JSON, catalog, Project Knowledge, session/mirror,
  file-size, repository, diff, staged-zero, secret-scan and doctor gates pass.
  The stable Python 3.13/Pydantic 2.10.6 environment may be reused but no
  package installation is authorized.
- `R22` — Worker changes only the exact Work Order ceiling, preserves the
  authorization packet, records every command/exit code and returns
  `READY_FOR_REVIEW` or a named blocked disposition. The worker does not create
  the reviewer-owned completion review, commit, push or deploy.
- `R23` — Catalog, roadmap, status, CVF mappings, Project Knowledge and
  continuity report only bounded truth. P4-A2 may become `CLOSED_BOUNDED` only
  after independent REVIEW/FREEZE; P4-B, P4-A3, durable storage/audit,
  operational-corpus RAG, API/UI, deployment and production remain open.
- `R24` — Final BUILD status is the exact authorization-packet paths plus the
  exact worker ceiling, staged set empty. Any unexpected path, changed
  authorization artifact, secret-like diff, second provider call or need for
  a new dependency/external effect stops work.

## Required focused commands

The worker must run the exact P4-A2 focused files named in the Work Order, the
P4-A1 and P4-A parent suites, then the complete repository suite. It must also
run:

```powershell
python scripts/run_p4a2_governed_rag_live_evidence.py
python scripts/generate_catalog.py --check
python scripts/check_session_state.py
python scripts/check_project_knowledge.py
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File "..\.Controlled-Vibe-Framework-CVF\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "."
git diff --check
git diff --cached --name-only
git status --short
```

Every changed JSON file must parse with `json.loads`. The live command is run
only after all non-consuming tests and gates pass and may consume one physical
provider attempt total.

## Acceptance and claim

All R1–R24 must pass without waiver. Acceptance proves only the bounded
application-layer P4-A1 → deterministic ephemeral hybrid/index/minimization →
P4-A gateway → strict citation-validated answer composition described in
DESIGN. It does not prove a public endpoint, general semantic embeddings,
operational-corpus RAG, durability, production provider integration,
deployment or production readiness.
