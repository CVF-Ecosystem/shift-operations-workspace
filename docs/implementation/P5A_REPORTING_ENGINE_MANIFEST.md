# P5-A Reporting Engine — Implementation Manifest

Status: DRAFT_READINESS
Risk: R2
Product Milestone Binding: docs/decisions/P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md, A0-A7 and Phase 5 remainder.
Authority: docs/work_orders/P5A_REPORTING_ENGINE_WORK_ORDER.md after activation only.

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
