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
Edge boundary. P4-D reached `FREEZE / CLOSED_BOUNDED` on 2026-08-28 after
independent `FINAL_REVIEW_PASS`, findings/waivers `NONE/NONE`, for its bounded deterministic work:
frozen typed SDK contracts, a digest-only generic webhook adapter with
fail-closed endpoint/DNS/peer/TLS authorization and audience-bound HMAC, total
mapping back to P4-C-owned receipts, and zero-I/O `CONFORMANCE_ONLY`
Zalo/WhatsApp mocks. Independent audit verified exact 54, focused 74,
invariant 37/2 plus guard, full 2898/132/1 and doctor 24 plus the bounded
legacy-catalog note. This proves no live send, vendor
protocol conformance, receiver replay enforcement, CVF governance behavior,
P4-E implementation, production readiness or deployment. P4-E is now at
`FREEZE / CLOSED_BOUNDED`. Amendment 1 repair is independently technically
accepted; all product findings including `P4E-AM1-REV-F1` are closed without
waiver, focused tests passed 219/2, disposable PostgreSQL passed 12 with
cleanup, and the module catalog is canonical. Amendment 2 independently passed
authorization; commits `c82d9e0` and `9809852` resolve the catalog-to-Project-
Knowledge phase-order cycle and bind terminal review evidence ownership.
Material commit `131a38b0c817903df2148107078c25dbe50d5f38` records the exact
accepted product/review/catalog packet; post-material complete gates, terminal
review and continuity commit close the tranche. Public workspace Core remains pinned at
`aa672d119`. Operator-authorized Core-only binding correction has independent source/config acceptance:
reuse its native closeability checker and integrity-check installed controls;
private provenance/shared packs/framework continuity are no project dependency.
CVF references remain read-only. P5-A is in REVIEW with bounded local acceptance of
A1-A6: renderer, authenticated API, current/history UI, exact artifact lineage,
Vietnamese PDF layout and packaged font/wheel proof. Actual browser10/10,
frontend128 tests/build and backend221 tests passed; independent corpus13/13
passed. The full material gate passed. A7 source passed3199tests; its one real canary returned401invalid_api_key,
retained in committed failed receipt3b569639. The operator defers further live
runs and key/model updates, and resumes source-verified whole-milestone P5-A2
reviewed pure supplied-input history/numeric functions without closing P5-A A7. Reporting-engine remains partial, P5-A open, Phase5 0/5.
P5-A2/B/C/D retain their roadmap owners; no support successor, production,
deployment or general CVF-governance behavior claim. Absorption, catalog
migration and XR1 remain parked. Active handoff/status carry current truth.

Plans state intent. Implementation status, source, tests, and independent
review evidence determine implemented truth. A future reader must re-open the
canonical files instead of treating this summary as fresh continuity.


P5-A2 pure-input subset25focused/48withsnapshot and7independent numeric oracles
passed after consolidated repair. Actual scoped ledger, scheduler/API/UI/RAG,
exact human approval and operational-quality/live evidence remain open.
Prior2026-10-25 private binding refreshes are historical, not current startup
authority. Current operator direction is installed pinned Core only.
The canonical active handoff records actual material SHA, normal full hook and
continuity receipts; source review alone does not close material completion.
Upstream/private repository movement does not invalidate intact installed Core;
explicit reviewed Core update is separate from ordinary project operations.

G04-G06 source audit pins20source surfaces and4existing test excerpts. Current
query/cohort/retention/snapshot gaps remain; synthetic data with actual backend
is proposed for the next reviewed SPEC/WO. This audit changes no runtime source
or acceptance and does not require operational data before fixture development.
Live holds and all14milestone remainders remain; active handoff owns current truth.

Docker synthetic backend actualdisposablePG16.15 rehearsal independently passed:
36shifts37versions, awaretime/immutablecontent/asof-lineage/analysis against
frozenoracle, migrations001–011twice and exactownedcleanup. Originalpipfailure
retained; committedAM1 oneuv3.3.4 recovery succeeded. No standingbackend or
operationalcoverageclaim. Core-only correction and carriedSQL now CLOSED_BOUNDED at3de6c50/7134f9e,
normal3253testsPASS and exact29+5cleanrange. G04–G06 source contract/staticfamily
accepted bc25/814d; native source Stage A now independently accepted after repair2:
source+generic91PASS2skip/84native mutation rejections, fulloracle receipts/lineage/
analysis, native500/501 zero-bodycopy, fresh access and strict receipt semantics.
StageB now independently accepts synthetic physical PostgreSQL query proof:
onePG16.15 target1PASS31.18s, frozen contexts/caps/RR/writer races and ownedcleanup.
StageB closure cad8ffc/0b7f870 is settled; the active handoff owns new planning.
Production coverage/retention, API/UI/scheduler/context/approval and operational
quality remain OPEN/UNKNOWN; all14gap owners, providerhold and Phase5 0/5 retained.



Current2026-10-26: source API a141156/355ff93 and G11 source UI a637e96/674d98e closed bounded; frontend145PASS/typecheck/build, normal3397PASS148skip. G04/G05 DESIGN complete; synthetic Stage A dispatch0e232d0/0654c2e independently clean; source accepted64focusedPASS/full608/profileVitebuild, F1 repaired; normal material/continuity pending. No physical effect admitted. Operational coverage UNKNOWN; all14gaps/owners and Phase5 0/5 retained.

Sources: `IMPLEMENTATION_STATUS.json`; `docs/catalog/MODULE_REGISTRY.json`; `docs/implementation/EXECUTION_ROADMAP.md`
