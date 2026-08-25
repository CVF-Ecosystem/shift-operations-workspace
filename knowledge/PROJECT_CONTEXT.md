# Project Context

This document is advisory orientation. `IMPLEMENTATION_STATUS.json`, the
machine module registry, and the execution roadmap remain authoritative.

## Current bounded context

Shift Operations Workspace is a modular operations application organized
around shift records, messages, events, tasks, customer requests, incidents,
handovers, reports, approvals, corrections, and audit evidence. The module
registry distinguishes real runtime behavior from partial, contract-only, and
stub surfaces; those labels must not be rounded up into production readiness.

Phase 1 is complete under its reviewed local/disposable infrastructure
boundary. Phase 2 is closed bounded for the reviewed start-to-freeze lineage.
The Project Operations Skill and Project Knowledge Pack are closed bounded.
P3-A Refinery is `CLOSED_BOUNDED` at independently reviewed BUILD `a6cf978`.
P3-C retrieval-ready contracts are `CLOSED_BOUNDED` at independently reviewed
BUILD `4cc0691`. These close only deterministic local contract boundaries and
do not complete Phase 3. P4-A1 governed retrieval is `CLOSED_BOUNDED` after
exact36 independent rereview: verified identity, permission and assignment
precede local deterministic retrieval; evidence projections, citations,
source/version hashes and ephemeral receipts are bounded. Only Project
Knowledge INTERNAL/LOCAL_ONLY is positive; both operational corpora remain
dependency-blocked. This proves no provider/LLM answer, API/UI, durable audit
or persistence, restricted/confidential or full-document access, vector/
semantic RAG, deployment, production readiness or confirmed truth. P4-A AI
Gateway is `CLOSED_BOUNDED` after independent final `REVIEW_PASS`: its
pure-library `AIGateway.execute` calls the real `cvf_runtime` data_scope/cost/
termination gates before dispatch, and replacement live PUBLIC-canary evidence
passed through Alibaba DashScope. P3-B and Phase 3 are closed only for this
reviewed library call-site boundary (`6/6`); there is still no application/API
caller, durable usage accounting, production provider adapter or RAG. The
separately governed `LPCI1-REF` lane remains parked and is not a downstream
runtime dependency. P4-B remains parked behind fresh authority.

P4-A2 governed-RAG completed INTAKE, DESIGN, SPEC, exact Work Order,
authorization review and BUILD on 2026-08-21. The implemented design is a new
pure package (`packages/governed-rag`) plus one no-route application
composition function (`execute_governed_rag` in the workspace-api application
layer): P4-A1 positive evidence only, local deterministic project-concept feature
vectors, ephemeral index with stale-detection fail-closed, fixed 45/55 hybrid
reranking, prompt-injection omission with fail-closed block, independently
recomputable extractive minimization, sole P4-A gateway dispatch and strict
citation membership. Independent review and repair produced green focused/
full repository suites, but a later rereview proved residual placement
binding, positive ABSTAINED receipt grammar and P4-A1 stage-11 revalidation
defects plus a receipt-hash labeling error, returning
`REVIEW_COST_ESCALATION_REQUIRED`. The operator approved consolidated
Amendment 1 on 2026-08-21; a separate REPAIR_WORKER executed round 3 under
its exact 66-path/no-provider-call Work Order, resolving the registry-owned
placement binding and P4-A1 eleven-stage/hash-labeling defects and confirming
the ABSTAINED receipt grammar was already generic. Independent review then
returned `REVIEW_PASS_NONCONSUMING` without waiver after exact adversarial,
focused, full-suite and repository-gate reruns. A separately authorized live
run then proved six zero-call refusals plus exactly one HTTP 200 external call;
independent post-call review returned `FINAL_REVIEW_PASS`. Status is `FREEZE /
CLOSED_BOUNDED` within the synthetic/local Project Knowledge, ephemeral-index,
no-route application-composition boundary. No database, public API/UI route, deployment,
commit or push occurred; operational corpora and `LPCI1-REF` remain parked.

P4-A3 application memory is `FREEZE / CLOSED_BOUNDED` at base `422661f`.
Independent review closed all findings without waiver; separately authorized
live proof recorded seven memory and six P4-A2 zero-call refusals followed by
exactly one HTTP 200 P4-A3-gated P4-A2/AIGateway call (`1/1/1`, ABSTAINED,
nine stages PASS, secret scan NONE). Post-call focused 182 and full 2494/128
passed; exact 52 paths, staged zero. Implemented truth remains process-local,
advisory SESSION/WORKING memory with explicit recall only. One exact local
closure commit is authorized; no amend/push. No durable memory, public route,
production adapter, install, database or deployment.

P4-B AI provider foundation is `FREEZE / CLOSED_BOUNDED`, base `319c6a8`.
All findings closed without waiver. The first HTTP 200 attempt remains retained
BLOCKED after prompt/schema drift; after independent repair review, four fresh
refusals were zero-call and exactly one replacement call returned HTTP 200
`EXTERNAL_ACCEPTED` with `1/1/1/1` counters and secret scan NONE. Verification
20/237/2732 passed. Boundary excludes production adapter/routing, durable
usage/audit, public API/UI and deployment. Cross-agent invariant learning is
its governed successor and is now closed bounded as described below.

`CROSS-AGENT-INVARIANT-LEARNING-2026-08-22` is `FREEZE / CLOSED_BOUNDED`.
Amendment 2 ratified the exact-30 worker union; independent rereview round 10
returned `REVIEW_PASS_ROUND_10`, findings/waivers `NONE/NONE`. The accepted
boundary is a repository-native invariant standard, closed schemas/matrices,
independent mutation obligations, ownership/provenance binding, synthetic
emitter, deterministic guard and shared agent-routing guidance. Focused
`77 passed, 2 skipped`; full `2809 passed, 130 skipped`; repository and doctor
gates passed with the retained bounded legacy-catalog note. No provider call,
credential, install, database or deployment occurred. This does not prove that
any AI agent consumed, remembered or complied with the guidance. P4-C later
reached `FREEZE / CLOSED_BOUNDED` on 2026-08-25 within its local Integration
Edge boundary; roadmap-next P4-D requires fresh INTAKE and no authority carries
forward. XR1 sibling historical-object debt remains unresolved.

Plans state intent. Implementation status, source, tests, and independent
review evidence determine implemented truth. A future reader must re-open the
canonical files instead of treating this summary as fresh continuity.

Sources: `IMPLEMENTATION_STATUS.json`; `docs/catalog/MODULE_REGISTRY.json`; `docs/implementation/EXECUTION_ROADMAP.md`
