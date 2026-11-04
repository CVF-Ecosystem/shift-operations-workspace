# P5-A2 source API BUILD worker return

Status: COMPLETE_PENDING_REVIEW
Self-declared worker-return artifact: yes
Date: 2026-10-26
Role: IMPLEMENTATION_WORKER
Risk: R2
Core: `../.Controlled-Vibe-Framework-CVF@aa672d11910ae1982557e4810a2a8002a611e9e6` (read-only)
Dispatch: `846acf0e695372d6d3596eda4a7fbdf9fbf61b38`
Dedicated dispatch continuity: `7f3c63ddedf700f09fe57a6feb5f51b994b6ed5c`

## Product Milestone Binding

P5-A2 full observable outcome remains integrated authorized scheduled signals,
forecasts, history, freshness, uncertainty, abstention and lineage, with exact
human run/version/source approval before a durable recommendation or action.
This worker slice implements bounded source-read G06/G11 and HTTP G13 cases:
the authenticated assigned caller receives a native source receipt or an exact
nonleaking refusal. It does not close the whole gap or milestone; Phase 5 is
0/5. Normal composition has blank server instance and no coverage authority,
so operational READY remains unavailable. Positive cases are synthetic test
injection only. The finite product return is the G11 source-inspection UI.

| Gap | Remaining truth, owner and destination |
|---|---|
| G01/A7 | Retained provider 401; blocked. Root/operator, P5-A A7 then P5-A2. |
| G02 | Operational RAG/context/index/citations blocked. Backend/Root, P5-A2 context. |
| G03 | Business and cohort fit open. Backend/operator, P5-A2 method. |
| G04 | Operational source integration open. Backend/Root, P5-A2 source. |
| G05 | Production mode/authority/coverage/retention and SQLite positive unknown. Backend/Root/operator, P5-A2 coverage. |
| G06 | Bounded API identity/release built, independent acceptance pending; later use-time access open. Backend/Root, P5-A2 API and approval. |
| G07 | Scheduler/claim/recovery open. Backend/Root, P5-A2 runtime. |
| G08 | Operational signal quality open. Backend/operator, P5-A2 signals. |
| G09 | Operational forecast accuracy open. Backend/operator, P5-A2 forecasting. |
| G10 | Monitoring/display open. Backend/UI/Root, P5-A2 quality and P5-B. |
| G11 | Source-read route built, independent acceptance pending; UI open. Backend/UI/Root, P5-A2 application. |
| G12 | Exact human approval open. Backend/UI/operator, P5-A2 approval. |
| G13 | HTTP auth/release/transport cases built, integrated drills open. Backend/Root, P5-A2 drills. |
| G14 | Real-provider AI-governance proof held. Root/operator, separately admitted P5-A2 REVIEW. |

P5-B dashboard/search/observability remains with backend/UI/Root; P5-C
backup/resilience/security/performance with backend/Root/operator; P5-D
deployment/Shadow Mode/release with Root/operator. No provider, Docker,
credential, `.env`, CSV, package install, browser, deployment or production
effect occurred in this worker scope.

## Source and tests

- `GET /proactive/source` mounts read-only with real signed JWT verification,
  token expiry, current stored user/role and canonical viewer-bar action.
  Auth/permission denial is fixed 401/403 before request diagnostics.
- Server-only single-instance scope uses UTF-8 canonical JSON and the
  accepted SHA-256 self-scope recipe. Blank instance and default coverage
  refuse. A native metadata cohort probe precedes coverage/body reads;
  authoritative `query_source` remains unchanged. Current full membership and
  identity/expiry are checked after bounded encoding and before HTTP release.
- The response is exactly the validated native bare receipt. Native shape
  fields project to OpenAPI; three structural query parameters are documented
  without enabling framework validation before auth. 1 MiB actual UTF-8
  encoding is incremental and emits no success prefix on overflow. Every
  200/401/403/422 branch has no-store/no-cache.
- New tests use actual TestClient, actual signing/verification/current users,
  native memory fixture ports and the independently frozen full API receipts.
  Dependency injection is limited to server context/clock; no principal or
  native outcome bypass. No old fixture/oracle, token, selector or source
  validator was changed.

## Evidence

First combined focused run after the independent family materialization gate:
`142 passed, 2 skipped in 12.03s`, no failures. Root's three in-scope
observations were then addressed: non-ASCII actor canonical UTF-8 scope,
structural three-key OpenAPI query projection, and exact 1 MiB/multibyte
overflow. New-only targeted run: `53 passed in 2.21s`. Final ten-path focused
run: `144 passed, 2 skipped in 10.23s`; skips are existing physical SQL tests,
not new xfails/deselection. `scripts/check_invariant_families.py` PASS; Core
inheritance/closeability guard 0 violations; `git diff --check` PASS. Root
owns the full normal pre-commit suite, catalog and commit.

The new HTTP test compares `response.content` byte-for-byte with the two
complete pre-BUILD fixture receipts in
`tests/fixtures/p5a2_source_api_oracle.json`, not just digest or selected
fields. Raw positive body `initial_asof36`: 58,234 UTF-8 bytes, SHA-256
`2597ffa32350b4446341ee9f26507f4518edbd920de856d7b919cdfbb339752e`.
Raw positive body `later_asof38`: 59,509 bytes, SHA-256
`cee802eefe09731a999abd1f543c976ea735518d3055f6afaa6b53e94c40bd05`.
The full literal bodies are those fixture `cases[].expected_receipt` JSON
objects serialized with UTF-8 `ensure_ascii=False` and compact separators;
the test asserts the actual HTTP bytes equal those independently frozen bytes.
Raw normal refusal body is exactly:

```json
{"receipt_version":"P5A2-SOURCE-RECEIPT-1","cohort_policy_version":"P5A2-COHORT-ENDS-1","numeric_policy_version":"P5A2-INITIAL-1","outcome":"SOURCE_REFUSED","reason":"COVERAGE_UNKNOWN"}
```

That body is 185 bytes, SHA-256
`061f04ac199e4bb89e2707d8152b65bbc40825aa7d57efce00791e46f246e6d8`.
The native/HTTP response consumer test uses the registered matrix digest
`3c565239318753f0c12f218b4a6517435a78cf2e7b74f60d0d61226da01e6b6a`:
54 generated READY and 30 REFUSED mutations, all 84 rejected by the native
validator and converted to the closed HTTP SOURCE_UNAVAILABLE receipt. The
legacy native corpus remains in the combined focused run. Test-only threshold
checks and a separate actual 1,048,576-byte UTF-8 boundary check passed.

## Exact worker manifest

SHA-256 is over actual file bytes; line count is current text lines. Only
these 14 admitted source/test paths and this worker return were changed by
the worker. Root's matrix, two old pin literals, catalog, admission/review and
continuity edits are separately owned.

| Path | Lines | SHA-256 |
|---|---:|---|
| `apps/workspace-api/src/workspace_api/application/proactive_source_access.py` | 71 | `77d360f388d6ca34e47409b700a1f72cf6ae94cecf30318dc48748f0f35cabff` |
| `apps/workspace-api/src/workspace_api/application/proactive_source_preview.py` | 79 | `ae670a2db1afc767b204aab04f85bfa90bc58bcecd836d2586a6c1c040a52f41` |
| `apps/workspace-api/src/workspace_api/api/proactive/__init__.py` | 1 | `220a14413ae4bc58c5aeb3623f122ccb7ab5529fcd92814403c990755e0c3fb3` |
| `apps/workspace-api/src/workspace_api/api/proactive/router.py` | 107 | `cd81b735eedcc8ecb440c9e7426c9c67038c4a09ffbe181d89b6878e5bd9b4cc` |
| `apps/workspace-api/src/workspace_api/api/proactive/response.py` | 71 | `5403b251506e6535432760f2372aead5ee3c6fc7faa2d962472eb72bc3a0018d` |
| `apps/workspace-api/src/workspace_api/main.py` | 117 | `162e059655a8c93720ba78f685d126c314dfcd3f6561c5ea8aea9740bd533fb4` |
| `apps/workspace-api/src/workspace_api/config.py` | 119 | `cd168eafbe0bc1eae125693c6bcd357953fef48944b4e43e08a94a2f1628f94d` |
| `apps/workspace-api/src/workspace_api/dependencies.py` | 124 | `efa6d998dd4f344d04c02dfedd24d7964fd2bbea3d8cc8fe03bba4470bbf56f3` |
| `packages/cvf-runtime/src/cvf_runtime/permission.py` | 155 | `fcc9b04d8348a14db13986d86514b2158897c20514c0f5960ddd1d5c1e66e745` |
| `tests/unit/p5a2_source_api_helpers.py` | 116 | `b18346d4fe683b99daaddd1f54523fb8f59aab86f8f6f073a1c063ad3e961f6b` |
| `tests/integration/test_p5a2_source_api_identity.py` | 119 | `f84f6d4d8bb405ef0b88cd2d194b5c6db55cc58d13fcfc97c734e02ea6fbbde2` |
| `tests/integration/test_p5a2_source_api_receipts.py` | 87 | `98f522c41f9da6a0391ff9cf94ccf89a1464561e3d61a2667acca0052a0a32e5` |
| `tests/integration/test_p5a2_source_api_release.py` | 147 | `46667ed5f9efdd401ecf4ace5a2d6b27857fae27bdb8ec30c5638857723b09b6` |
| `tests/unit/test_p5a2_source_api_transport.py` | 123 | `6cbfdedf0b506f074869b0738d0d113647c22d64a002bdc8909723f6de47e4c2` |

Manifest delta: NONE outside the admitted worker path and worker-return set.
No executable exceeds 300 lines; the maximum is 155. No source/API acceptance,
operational READY, P5-A2 completion, public release or AI governance claim is
made by this self-declared return.

## Agent Operation Trace Block

| Field | Evidence |
|---|---|
| Actor | IMPLEMENTATION_WORKER |
| Provider or surface | local project workspace |
| Session or invocation | P5A2-SOURCE-API-BUILD-20261026 |
| Working directory | project root |
| Command or tool surface | exact source/test edits, inert AST parse, focused pytest, native guards |
| Target paths | exact 14-path worker manifest and this return |
| Allowed scope source | accepted BUILD SPEC, admitted Work Order, independent family materialization gate |
| Before status evidence | dispatch/continuity clean; no API route |
| After status evidence | real mounted route and focused 144 passed/2 existing skipped, pending independent review |
| Approval boundary | existing R2 bounded source HTTP authority only |
| Claim boundary | synthetic fixture HTTP composition; no operational coverage or AI governance proof |
| Agent type | implementation worker |
| Invocation ID | P5A2-SOURCE-API-BUILD-20261026 |
| Expected manifest | 14 exact worker source/test paths and this return |
| Actual changed set | same worker path set; Root edits separately owned |
| Manifest delta | NONE |

## Amendment 1 repair return

Role transition: Root's ORCHESTRATOR assignment to REPAIR_WORKER for the
same-scope AM1 repair. The earlier source BUILD return above remains preserved
under its original IMPLEMENTATION_WORKER role. Current worker status remains
`COMPLETE_PENDING_REVIEW`; no implementation or material commit is self-approved.

The retained normal material hook failure was **15 historical OpenAPI
assertions failed, 3,370 passed, 148 existing skipped, 4 warnings in 437.50s**
(`.venv/p5a2-api-source-material-20261026.log`). No material commit was made;
the source API change remains the sole historical OpenAPI-chain root cause
identified in `API-OPENAPI-F1`. This repair did not rerun or overwrite that
full-hook failure. The AM1 authorization remains `AM1_AUTHORIZATION_PASS_BOUNDED`
and limits this worker to the two test paths below plus this return; the frozen
fixture is Root-owned and read-only here.

The source delta fixture raw SHA-256 was rechecked as
`64b5123445e1e9a6f6ac123c809d57414a511412fe0b1ea575c2bf5fecf27dbf`. The
new source leaf checks that pin, the complete fixture root/path/method shape,
the full GET operation, bearer security, all three exact query parameters,
the four response cases, and the exact READY/REFUSED schema field sets and
objects before it mutates the OpenAPI document. It then removes only
`/proactive/source`, `P5A2ReadyReceipt`, and `P5A2RefusedReceipt`. The old
export leaf invokes this source leaf before its existing export verification.
Negative tests cover missing path, extra method, changed security, query,
response, and each schema; each proves the input remains unchanged on helper
failure. An unrelated path and schema survive source removal, while the
existing historical chain rejects added unrelated paths, schemas and legacy
operation changes by its unchanged digest. Removing both admitted leaves
restores the unchanged historical golden
`a85bd8909ca88aba97d57825f3457ce9e5ef52979234db71b08a5ad05a20d211`.

Focused evidence:

- New contract module run standalone with its test-only JWT environment setup:
  **11 passed in 1.06s**.
- All ten historical OpenAPI modules plus the new contract module: **74
  passed in 1.74s**.
- Combined original ten-path source corpus and all eleven OpenAPI modules:
  **218 passed, 2 skipped, 1 existing Starlette deprecation warning in 9.35s**.
  The skips remain the existing physical SQL skips; no new skip or xfail was
  added. The historical golden-chain assertion passed.
- The normal full pre-commit hook remains Root-owned and has not been rerun by
  this worker. The original failed attempt above remains part of the evidence.

AM1 worker manifest (raw file SHA-256; line count):

| Path | Lines | SHA-256 |
|---|---:|---|
| `tests/unit/test_report_export_openapi.py` | 121 | `9c7bda56d1f33c4112117c6fd864f561f10eafabe59bdb1d07a60d44ed810f77` |
| `tests/unit/test_p5a2_source_openapi_contract.py` | 149 | `f8695ca9d83d135b8b12360a01aeb859bb25316db14d71d89ff4dc4efdfe08e0` |

The only worker-owned changes in this AM1 return are those exact two test files
and this worker-return artifact. The Root-frozen fixture remains unchanged at
its admitted SHA. All 14 original source/API modules remain byte-for-byte
unchanged. No provider call, Docker/database operation, package install,
credential or `.env` access, runtime change, production data, browser, release,
deployment or other external effect occurred. No commit was created.

### Product milestone binding and remaining work

The full P5-A2 outcome remains integrated authorized scheduled signals,
forecasts, history, freshness, uncertainty, abstention and lineage, followed by
exact human run/version/source approval before a durable recommendation or
action. This repair only reconnects the admitted source OpenAPI delta to the
existing historical golden chain so Root can complete normal material closure;
it closes no gap or milestone. Phase 5 remains **0/5**.

| Gap | Remaining requirement after this repair | Owner and roadmap destination |
|---|---|---|
| G01/A7 | One provider 401 is spent; accepted A7 proof is blocked. | Root/operator, P5-A A7 then P5-A2. |
| G02 | Operational RAG, context, index and citations are blocked. | Backend/Root, P5-A2 context. |
| G03 | Business and cohort fit remain open. | Backend/operator, P5-A2 method. |
| G04 | Operational source integration remains open. | Backend/Root, P5-A2 source. |
| G05 | Production mode, coverage and retention plus positive SQLite remain unknown. | Backend/Root/operator, P5-A2 coverage. |
| G06 | Bounded source API was source-reviewed; AM1 integration review and Root's normal material gate remain, and later use-time access/approval is open. | Backend/Root, P5-A2 API and approval. |
| G07 | Scheduler, claim and recovery remain open. | Backend/Root, P5-A2 runtime. |
| G08 | Operational signal quality remains open. | Backend/operator, P5-A2 signals. |
| G09 | Operational forecast accuracy remains open. | Backend/operator, P5-A2 forecasting. |
| G10 | Monitoring and display remain open. | Backend/UI/Root, P5-A2 quality and P5-B. |
| G11 | The source route is bounded; the UI and application fit remain open. | Backend/UI/Root, P5-A2 application. |
| G12 | Exact human run/version/source approval remains open. | Backend/UI/operator, P5-A2 approval. |
| G13 | Bounded HTTP auth/release/transport was source-reviewed; integrated drills remain open. | Backend/Root, P5-A2 drills. |
| G14 | Live AI-governance proof remains held. | Root/operator, separately admitted P5-A2 REVIEW. |

P5-B dashboard/search/observability remains with backend/UI/Root; P5-C
backup/restore, resilience, security and performance with backend/Root/operator;
P5-D deployment, Shadow Mode and release with Root/operator. After independent
AM1 acceptance and Root-owned normal material closure, the finite product return
is the separately bound G11 UI tranche. No further support audit is authorized
by this repair.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: REVIEWER_LOCAL_REPAIR
workerRedispatchAllowed: YES

The source and test paths fit the exact manifest and size limits. Family
binding was independently materialized before focused tests; there is no
outside-authority repair need known at return. Independent REVIEWER must
assess source, tests, actual path set, complete milestone coverage and claim
limits before the Root commit steward proceeds. Same-scope findings may be
redispatched under the current Work Order; a new path/effect/risk boundary
requires consolidated amendment and review.
