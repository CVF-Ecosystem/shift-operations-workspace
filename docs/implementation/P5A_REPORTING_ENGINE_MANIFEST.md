# P5-A Reporting Engine — Implementation Manifest

Status: COMMITTED_REVIEWED_LOCAL_MATERIAL / A7_LIVE_HELD
Risk: R2
Product Milestone Binding: docs/decisions/P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md, A0-A7 and Phase 5 remainder.
Authority: docs/work_orders/P5A_REPORTING_ENGINE_WORK_ORDER.md activated at dispatch142052f and marker14ae8e7.

## Product outcome and current gap set

The assigned operator/supervisor downloads four views of an existing P2-R
END_SHIFT report as readable PDF or XLSX through the authenticated workspace.
This assignment receives A1-A7. A0 is accepted P2-R input. A1-A7 remain open
until independently accepted integrated evidence; a package or route alone does
not complete the milestone. P5-A2 forecasting, P5-B observability, P5-C
resilience and P5-D pilot/release retain the roadmap owners and destinations
in the canonical binding. Unknown implementation coverage blocks activation.

## Exact planned product paths

Existing files: `packages/reporting-engine/README.md`, root `pyproject.toml`,
`apps/workspace-api/src/workspace_api/application/report_snapshot.py`,
`apps/workspace-api/src/workspace_api/api/reports/router.py`,
`apps/workspace-web/src/features/operator-actions/ReportActions.tsx`,
`apps/workspace-web/src/services/api.ts`, and the existing P2-R golden/OpenAPI
contract only if the intentionally added route requires an exact delta.

New files: `packages/operations-domain/src/operations_domain/report_digest.py`,
`packages/reporting-engine/pyproject.toml`,
`packages/reporting-engine/src/reporting_engine/__init__.py`,
`packages/reporting-engine/src/reporting_engine/model.py`,
`packages/reporting-engine/src/reporting_engine/validation.py`,
`packages/reporting-engine/src/reporting_engine/views.py`,
`packages/reporting-engine/src/reporting_engine/pdf.py`,
`packages/reporting-engine/src/reporting_engine/xlsx.py`,
`packages/reporting-engine/src/reporting_engine/limits.py`,
`packages/reporting-engine/src/reporting_engine/worker.py`,
`apps/workspace-api/src/workspace_api/application/report_export.py`,
`apps/workspace-web/src/services/reportExport.ts`, and
`apps/workspace-web/src/features/operator-actions/ReportDownload.tsx`.
An export subrouter or app registration file needs an orchestrator manifest
amendment if source inspection shows it is necessary; no implicit catch-all.

Font asset/notice paths:
`packages/reporting-engine/src/reporting_engine/assets/DejaVuSans.ttf` and
`packages/reporting-engine/src/reporting_engine/assets/LICENSE_DEJAVU`.
The source is the existing local Matplotlib data inventory in the intake/design;
required font SHA-256 is `3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22`
and license SHA-256 is `d75938dec098f06f0ac3c00853065d94f020be1c3c62ef1dc2975ba15b4d9b0e`.
The worker verifies hashes before and after copying and includes the source
license notice in package data. Readiness inventory found 134 tested Vietnamese
code points plus seven combining marks; runtime still checks all input glyphs.

Dependency/install paths: root `pyproject.toml`, new `.python-version`, and
new `uv.lock`. Pin `reportlab==4.4.4` and `openpyxl==3.1.5` in root project
dependencies and add the reporting source path to pytest discovery. Use
CPython 3.13.12 from the existing local runtime, resolve and commit one
`uv.lock` including `dev` extras, then create a disposable project `.venv`
with `uv sync --python 3.13.12 --extra dev --frozen`. A global Python 3.11
installation is inventory only, not implementation proof. The lock and
installed environment are verified by exact imports and focused tests. Add
`PyMuPDF==1.27.2.2` as a dev dependency for independent PDF text extraction
and page raster inspection under that same locked 3.13.12 environment; no
global-Python parser counts as evidence. Actual browser proof uses the existing
web `@playwright/test==1.62.1` package and its project lock, with no Python
Playwright dependency. The web test lives under `src/tests` so the existing
`vitest run src/tests` script executes it.

Readiness setup on 2026-10-23: `uv lock --python 3.13.12` resolved 53 packages;
`uv sync --python 3.13.12 --extra dev --frozen` installed 51 into ignored
`.venv`. Exact imports report CPython 3.13.12, reportlab 4.4.4, openpyxl 3.1.5,
PyMuPDF 1.27.2.2, FastAPI 0.118.3 and Pydantic 2.10.6. Focused baseline
`tests/unit/test_report_snapshot.py` plus
`tests/unit/test_report_openapi_contract.py` passed 31 tests. This proves local
dependency readiness only; it does not prove a renderer, API or browser download.

## Exact planned proof paths

`tests/unit/test_report_export_views.py`,
`tests/unit/test_report_export_renderers.py`,
`tests/unit/test_report_digest.py`,
`tests/integration/test_report_export_api.py`,
`tests/cvf/test_report_export_outcomes.py`,
`apps/workspace-web/src/tests/reportDownload.test.tsx`,
`apps/workspace-web/src/tests/reportDownloadHistory.test.tsx` (bounded A5 proof split),
`tests/unit/test_report_openapi_contract.py` (intentional export-route delta only),
`tests/unit/test_operations_domain_boundary.py` (local CPython 3.13 `.venv`
source-isolation compatibility only),
and a dated `docs/decisions/P5A_REPORTING_ENGINE_BUILD_REVIEW_2026-10-23.md`.
The independent contract already resides in
`docs/specs/P5A_REPORTING_ENGINE_SPEC.md`,
`docs/cvf/invariants/p5a-export-outcomes.json`,
`docs/cvf/invariants/registry.json`, and
`docs/specs/p5a_export_invariant_pin.py`.
The isolation test permits only the active interpreter's exact runtime prefix
and site paths while preserving forbidden import and reverse-import probes;
negative cases inject the repository root and API source root. This is a
direct prerequisite of the locked local P5-A build environment.
Browser/download and rendered PDF/XLSX evidence belongs in a dated review
artifact; no raw customer data or credentials may be copied into it.

The renderer worker is a killable isolated process with a 10-second deadline.
One non-queued render slot per API process returns 503 EXPORT_BUSY when occupied;
this makes no cross-process/global capacity claim.
PDF limits: 512 pages, 8 MiB output. XLSX limits: 20,000 total rows,
32,767 UTF-16 code units per cell, 8 MiB output. At/over boundary fixtures,
plus a forced stalled worker, prove refusal has zero attachment bytes and
the timed-out child has exited. A completed-output elapsed-time measurement
does not satisfy the deadline contract. Non-mutation
proof compares persisted-state digests before and after; membership and R3
lineage proof parses actual PDF/XLSX bytes and compares independent expected
digests, including a same-count substitution negative case.

## Bounded split policy and change control

The Python 300-line and TypeScript 200-line guards make file splits foreseeable.
If a planned renderer, API, or UI module reaches its cap, only a sibling under
`packages/reporting-engine/src/reporting_engine/`,
`apps/workspace-api/src/workspace_api/application/report_export*.py`, or
`apps/workspace-web/src/features/operator-actions/ReportDownload*.tsx` may be
added, with an updated exact worker manifest before review. No split grants
permission to change canonical P2-R status/schema, authorization, assignment,
provider, Core, provenance, database migrations, or unrelated routes.
Any such need returns to the orchestrator for a reviewed scope amendment.

## Review and terminal evidence

Worker returns exact changed paths and focused proof. Independent REVIEWER
checks source, bytes, actual browser download, matrix mutations, row/reference
membership, refusal precedence, and complete A1-A7 reconciliation.
COMMIT_STEWARD commits only reviewed material. SESSION_SYNC_STEWARD records
the real material SHA in the active P5-A handoff and makes a separate
continuity commit. REVIEWER then checks clean committed ranges before CLOSER
may decide FREEZE. Provider-governance claims require separately admitted
real provider evidence and are held by this manifest.

## A5 history proof split amendment

Root permits exact `apps/workspace-web/src/tests/reportDownloadHistory.test.tsx`
for history-only cases split from the original download test under the hard
200-line cap. The new ReportDownloadHistory.tsx product sibling already falls
within the approved ReportDownload*.tsx family. Full gap ownership unchanged.

## Independent browser evidence paths

Root REVIEWER owns `tests/integration/test_report_export_browser.py` and
`tests/integration/test_report_export_browser_support.py`, within the already
approved test_report_export*.py family. These replay disposable real-API/UI
proof explicitly from the project root; pytest import runs no server/browser.
The split keeps each Python file below300 lines. Outputs are synthetic and
ignored, selected source hashes bind each run, and committed review records
carry the accepted receipt. No provider credential/read/call is included.

The retained sanitized receipt is
`docs/decisions/P5A_REPORTING_ENGINE_LOCAL_EVIDENCE_2026-10-23.json`.
It records actual browser/download hashes, nonmutation and local artifact/wheel
proof, with no live-governance or milestone-completion claim.

## Final returned topology and local disposition

Historical local disposition: A1-A6 accepted bounded; full hooks subsequently
passed and the exact A7 call was admitted below; its source/effect/receipt remain.
Planned validation.py was not created: model.py owns validation. Planned
unit/test_report_digest.py and integration/test_report_export_api.py were not
created: digest equivalence is in test_report_export_renderers.py and actual
InMemory/SQLite API proof is in tests/cvf/test_report_export_outcomes.py.
No acceptance or proof was dropped by that placement reconciliation.
Bounded actual siblings: reporting_engine/xlsx_xml.py for CR-safe XML;
ReportDownloadHistory.tsx and reportDownloadHistory.test.tsx for explicit lazy
history reads and capped proof. Other final product files are the exact paths
above; no app-registration, migration, provider or canonical lifecycle edits.
All code stays within Python300/TypeScript200 lines. Root-owned browser harness
is298 lines; its support module remains below300. Font/license remain exact.
Sanitized local evidence JSON is an approved product evidence artifact; the
full changed-set is reviewed before normal material commit, excluding ignored
build/wheel/browser outputs and generated tsbuildinfo. Existing package build/
egg-info outputs were reversibly moved beneath ignored .venv proof storage.
Reporting-engine status stays partial; local acceptance is not P5-A closure.

## Consolidated OpenAPI chain proof repair

Exact added proof: `tests/unit/test_report_export_openapi.py` under the approved
test_report_export*.py family. Minimal latest-delta linkage is authorized in
`tests/unit/test_c3b2_mutation_openapi_contract.py` and
`tests/unit/test_p2b_openapi_contract.py`. Restore unchanged P2-R path ownership
in test_report_openapi_contract.py. Historical SHA constants remain untouched;
only the exact new export delta may be stripped before the historical chain.
Both full-document golden checks and all shared earlier callers must pass,
with negative unrelated-change checks preserved. No application source change.

Material 56b4c2729b56c3094d69c141b9ee918026d3cb5a passed normal full hook 3173 passed, 146 skipped, 4 warnings in 175.82s. Final exact51 paths and reviewed source hashes were checked post-material; actual-SHA continuity follows. At that local checkpoint A7 was held; the subsequent user grant below admits
one call. Its source/effect/receipt remain pending; no FREEZE.

## A7 admitted continuation — finite one-call evidence

User grant is now explicit in LIVE_ADMISSION_2026-10-23.json. Remaining A7 scope
is the complete contract/source/review/commit/one-call/receipt/final-review/
closure chain in the amended Work Order; all other Phase5 owners unchanged.
Exact planned sources: scripts/run_p5a_live_governance_evidence.py and bounded
scripts/_p5a_live_*.py (each itemized on return); structural-only tests under
tests/unit/test_p5a_live_canary*.py. Exact new contract/matrix/pin and admission/
attempt/evidence artifact paths are listed in the Work Order. These are direct
P5-A evidence dependencies; no framework/provider library or production route.
Both historical CVF repositories remain read-only. No existing local accepted
product source, older live receipt or expired quota record may be changed.

A7 source commit precedes the root-owned one-use effect. Independent receipt
review owner is Luna/max p5a_readiness, then normal evidence commit and
terminal/continuity/range closure. The immutable admission is read-only for
workers and is bound with the registry at pre-BUILD review. A failed attempt
remains disclosed and cannot satisfy closure.

## Exact A7 returned source topology

- scripts/run_p5a_live_governance_evidence.py
- scripts/_p5a_live_contract.py
- scripts/_p5a_live_preflight.py
- scripts/_p5a_live_transport.py
- tests/unit/test_p5a_live_canary_contract.py
- tests/unit/test_p5a_live_canary_preflight.py

Root independent source REVIEW_PASS_BOUNDED after cost-basis metadata repair.
All source files stay below300lines; original product source, frozen SPECs,
matrices and immutable admission/local evidence remain unchanged. Source
material commit must pass normal full hook before the one root-owned effect.

## Actual A7 failed-call disposition

Exact generated LIVE_ATTEMPT/LIVE_EVIDENCE paths in the Work Order are now
retained, with independent RESULT_REVIEW_PASS_FAILURE_RECORDED. Real one call
returned401invalid_api_key, accepted0; no retry, usage/cost invented or source
repair. Grant spent, marker immutable. Normal failed-evidence commit and
actual-SHA blocked continuity do not close P5-A/A7. Product/caller source intact.
