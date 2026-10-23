# P5-A Reporting Engine — Approved Execution Scope

Status: APPROVED_FOR_EXECUTION
Risk: R2

## Product Milestone Binding

Canonical current source and full gap set:
docs/decisions/P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md,
section Product Milestone Binding. Assign A1-A7 after local readiness activation;
A0 reused. All remaining Phase5 milestones keep the owners/destinations there.
Acceptance: docs/specs/P5A_REPORTING_ENGINE_SPEC.md R1-R13.

## Authority and readiness

Operator authorized autonomous roadmap execution and independent review under
the existing R2 scope. This DRAFT awaits local readiness and activation;
provider/credential/public/deployment authority is not included. Before activation:
1. ORCHESTRATOR records the already accepted product scope and exact
   local-only external-effect boundary in the active handoff.
2. Verify the local DejaVu font and license bytes against the SHA-256 values
   in SPEC R8; copy into the package only during BUILD. Pin `reportlab==4.4.4`
   and `openpyxl==3.1.5` with a CPython 3.13.12 `uv.lock` and frozen dev install.
   Lock `PyMuPDF==1.27.2.2` as a dev-only PDF parser/raster proof dependency;
   use existing web `@playwright/test==1.62.1` for browser proof.
3. Enforce SPEC R9 caps: PDF 512 pages/8 MiB, XLSX 20,000 aggregate rows/
   32,767 UTF-16 units per cell/8 MiB, and a 10-second killable renderer
   process. One non-queued slot per API process returns 503 EXPORT_BUSY;
   no global concurrency guarantee. Deadline proof includes child termination.
4. Independently review registered export invariant family and contract-source
   hash before renderer implementation; use docs/cvf/INVARIANT_FAMILY_STANDARD.md.
5. If governance proof is to be claimed, admit exact provider/model/endpoint,
   secret source, current quota/cost ceiling and one-call/64-token/no-retry envelope.
6. Review the exact implementation manifest and gate-to-role graph below,
   record activation SHA in active handoff before any product BUILD.

Implementation manifest: docs/implementation/P5A_REPORTING_ENGINE_MANIFEST.md.
Foreseeable file splits are bounded to the path families in that manifest and
must be itemized in the worker return. Product implementation remains held
until the readiness ledger has no unresolved local prerequisite.

Readiness evidence: local CPython 3.13.12 `uv.lock` and frozen dev sync complete;
imports verify reportlab 4.4.4, openpyxl 3.1.5 and PyMuPDF 1.27.2.2; focused
P2-R snapshot/OpenAPI baseline 31 passed. The manifest records exact commands
and path ownership. The font/license remain source-hash-pinned BUILD inputs;
their asset copy and full glyph/render proof occur only after activation.
The locked 3.13 `.venv` exposed an existing isolation test assumption: it
treated the active interpreter's own runtime directory as a forbidden repo
source root. Same-scope readiness repair may edit only
`tests/unit/test_operations_domain_boundary.py` to allow exact interpreter
runtime/site paths and add negative repo/API source contamination probes;
all forbidden imports and static reverse-import checks remain mandatory.

## Invariant-Family Proof

Applicability: `P5A-EXPORT-OUTCOMES`, required by the shared outcome/refusal
response and cross-format membership contract. Matrix canonical digest:
`9e076aed6aded4e6c4d9f1b1bcd8923cd1e760d6ac823f9e79dccd644f1db9df`.
Independent contract source: `docs/specs/P5A_REPORTING_ENGINE_SPEC.md` at
canonical digest `5192379129cb88601496a6768d487d81779e487c4efb187a6a255b8cc06e84c8`.
Static ownership consumer: `docs/specs/p5a_export_invariant_pin.py`.
Real adapter and evidence test: `apps/workspace-api/src/workspace_api/application/report_export.py`
and `tests/cvf/test_report_export_outcomes.py`; these must be added in BUILD.
Declared `RECURSE_NESTED_OBJECTS` exclusions cover only flat abstract receipts;
REVIEWER must acknowledge these and independently inspect actual PDF/XLSX
content. Run `python scripts/check_invariant_families.py` and focused pytest
for the real adapter, including generated mutation corpus. IMPLEMENTATION_WORKER
owns returned conformance evidence; independent REVIEWER recomputes matrix
digest, reruns corpus, samples one raw emitted positive per outcome, and confirms
expected values came from persisted snapshot plus SPEC before renderer execution.
The reviewer parses emitted bytes to compare exact record/reference membership
and metadata digests, including same-count substitution, and checks before/after
persisted-state digests for non-mutation. A receipt echo cannot satisfy these.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/P5A_REPORTING_ENGINE_WORK_ORDER.md;docs/implementation/P5A_REPORTING_ENGINE_MANIFEST.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A_REPORTING_ENGINE_WORK_ORDER.md;docs/cvf/invariants/p5a-export-outcomes.json;docs/specs/p5a_export_invariant_pin.py | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A_REPORTING_ENGINE_2026-10-23.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | packages/reporting-engine/src/reporting_engine/;apps/workspace-api/src/workspace_api/application/report_export*.py;tests/unit/test_report_export*.py;tests/integration/test_report_export*.py;tests/cvf/test_report_export*.py | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/cvf/invariants/p5a-export-outcomes.json;docs/specs/p5a_export_invariant_pin.py | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/P5A_REPORTING_ENGINE_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A_REPORTING_ENGINE_2026-10-23.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A_REPORTING_ENGINE_BUILD_REVIEW_2026-10-23.md;tests/cvf/test_report_export*.py | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity,pre_implementation_autorun |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A_REPORTING_ENGINE_BUILD_REVIEW_2026-10-23.md;docs/implementation/P5A_REPORTING_ENGINE_MANIFEST.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | pyproject.toml;.python-version;uv.lock;packages/reporting-engine/src/reporting_engine/;packages/reporting-engine/pyproject.toml;packages/reporting-engine/README.md;packages/operations-domain/src/operations_domain/report_digest.py;apps/workspace-api/src/workspace_api/application/report_snapshot.py;apps/workspace-api/src/workspace_api/application/report_export*.py;apps/workspace-api/src/workspace_api/api/reports/router.py;apps/workspace-web/src/services/api.ts;apps/workspace-web/src/services/reportExport.ts;apps/workspace-web/src/features/operator-actions/ReportActions.tsx;apps/workspace-web/src/features/operator-actions/ReportDownload*.tsx;apps/workspace-web/src/tests/reportDownload.test.tsx;tests/unit/test_report_export*.py;tests/unit/test_report_digest.py;tests/unit/test_report_openapi_contract.py;tests/unit/test_operations_domain_boundary.py;tests/integration/test_report_export*.py;tests/cvf/test_report_export*.py;docs/decisions/P5A_REPORTING_ENGINE_BUILD_REVIEW_2026-10-23.md | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A_REPORTING_ENGINE_BUILD_REVIEW_2026-10-23.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A_REPORTING_ENGINE_2026-10-23.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A_REPORTING_ENGINE_2026-10-23.md;docs/decisions/P5A_REPORTING_ENGINE_BUILD_REVIEW_2026-10-23.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |

## Bounded proposed mutation families

- packages/reporting-engine/src/reporting_engine/**: pure rendering, metadata,
  validation, formats and bounded file splits under Python 300-line hard guard.
- packages/reporting-engine/pyproject.toml and package README; approved font/license
  under that package only, digest-pinned after source/license verification.
- packages/operations-domain/src/operations_domain/report_digest.py and
  apps/workspace-api/src/workspace_api/application/report_snapshot.py only to
  extract/reuse identical aggregate digest algorithm; no selection/schema/lifecycle
  change. Existing byte-equivalence regressions and new mismatch tests required.
- apps/workspace-api/src/workspace_api/application/report_export*.py;
  apps/workspace-api/src/workspace_api/api/reports/export*.py and router.py;
  apps/workspace-api/src/workspace_api/main.py only for router registration if needed.
- apps/workspace-web/src/features/operator-actions/ReportActions.tsx plus bounded
  ReportDownload*.tsx split; services/reportExport.ts; existing session/error owners
  only if an exact approved manifest proves necessary, not a blanket rewrite.
- packages/workspace-contracts/reports/**: binary/export contract documentation;
  no changes to canonical P2-R Report fields or status values.
- tests/unit/test_report_export*.py; tests/integration/test_report_export*.py;
  tests/cvf/test_report_export*.py; `tests/unit/test_report_openapi_contract.py`
  for exact intended route delta; `apps/workspace-web/src/tests/reportDownload.test.tsx`;
  bounded browser evidence fixtures; synthetic inputs only.
- pyproject.toml, `.python-version`, `uv.lock`: reporting path, exact pins,
  CPython 3.13.12 and reproducible frozen dev environment only.
- Invariant family/matrix/adapter/tests exact paths determined by readiness,
  no new generic framework or unrelated guard changes.
- Product evidence/catalog/status/roadmap/index/knowledge and canonical continuity
  as required for truthful changes. Existing core/provenance/policies read-only.

## Evidence, failure and ownership

IMPLEMENTATION_WORKER changes authorized paths only, returns without commit.
Independent REVIEWER checks full milestone coverage and returned artifacts;
COMMIT_STEWARD owns material commits; SESSION_SYNC_STEWARD records actual SHAs in
separate continuity commit; CLOSER closes only after clean committed-range checks.
R2 independent review cannot be replaced by implementation worker self-approval.

Stop on unresolved readiness, scope/risk/external-effect expansion, unknown
coverage needed by implementation, changed source authority or failed mandatory
gates. Same-scope repairs obey consolidated-review/round-three escalation rules.
Do not weaken P2-R validators, golden contracts, permissions, assignment or tests.

Required proof: focused format/contract/authorization/browser tests, meaningful
PDF visual and XLSX structure inspection, P2-R regressions, invariant family gate,
repository/catalog/knowledge/session/file-size gates, full configured pre-commit,
independent final review and admitted live receipt for governance claims.
No pure unit/mock results may be promoted to governance proof.

## Planning checkpoint and return

This draft is reviewable scope only; build activation is pending the local
readiness items above. Product milestone remains 0 completed criteria newly
proved by this packet. Readiness belongs to the same P5-A work. After exact
local readiness review, activate bounded BUILD and return to user-downloadable
reporting.

## Orchestrator activation

Operator autonomous scope/delegation authority recorded in active handoff.
Independent readiness inventory/review by p5a_readiness (Luna/max) and root
REVIEWER accepted the consolidated repairs: exact paths, eight status/history
shapes, artifact lineage/membership/nonmutation proof and locked Python3.13.12.
Frozen sync/import proof and 31 P2-R baseline tests PASS. Root authorizes bounded
local product BUILD after dispatch material and continuity marker commits.
No provider/credential/public/deploy authority; governance proof remains A7 held.
Sol/medium implementation lane: package/digest/backend/tests/dependency paths.
Luna/max UI lane: ReportDownload.tsx, ReportActions.tsx, services/reportExport.ts,
services/api.ts only for required binary helper, src/tests/reportDownload.test.tsx.
Workers must not overlap lanes or commit; root reviews integrated results.
