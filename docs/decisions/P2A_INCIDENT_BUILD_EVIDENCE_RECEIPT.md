# P2-A Incident Vertical — BUILD Evidence Receipt

Tranche: `P2A-INCIDENT-VERTICAL-2026-07-26`
Role: REPAIR_WORKER (Claude), repairing INC-REV-F6 (post second independent
repair re-review)
Status: `READY_FOR_INDEPENDENT_INCIDENT_BUILD_RE_RE_REVIEW`

This receipt **replaces** the prior BUILD evidence receipt in full. The
second independent repair re-review confirmed INC-REV-F1..F5 closed and the
39-path/gate/PostgreSQL/provider evidence sound, but stopped on one
independently reproduced defect in the already-authorized R15-A/F5 scope:

- `INC-REV-F6 ENDPOINT_CREDENTIAL_FAILURE_LEAK`: a transport exception
  embedding `req.full_url` could carry URL-only credential material
  (userinfo/query/fragment) past `sanitize_secret_text`, because that
  function only ever knew about the API key, not about secrets smuggled into
  the endpoint URL itself. Independent probe: `ENDPOINT_SENTINEL_LEAK=True`.

This document reports only the post-F6-repair, freshly re-verified state.
Nothing here is inherited unverified from either earlier receipt.

## 1. G6 preconditions (verified fresh, before this repair)

- `HEAD == origin/main == eb4597169dee176c62284c198ae375cbfc3511a8` (the
  pushed finding-record commit; unchanged throughout this repair — no stage/
  commit/push occurred at any point).
- Staged area empty; tracked tree clean at G6 (only this tranche's own
  uncommitted BUILD/repair changes present).
- Only the preserved assessment was untracked, SHA-256
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2` — verified
  unchanged after this repair.
- CVF core HEAD == core origin/main == manifest `cvfCoreCommit`
  `27137db4d9aa2aea931ddd2507185d5c24943080`; core worktree clean.
- Workspace doctor: `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` before
  and after — sole warning is the bounded legacy catalog-kit note, unchanged.
- Docker daemon responded; no pre-existing `cvf-pg-live-*` container/volume.
- Provider credential present as an environment-only check (value never
  printed/read into evidence or chat).

## 2. Authorized changed set (exactly 39 paths, no 40th)

This finding modifies only the four paths the handoff explicitly permits,
all already within the amended 39-path ceiling:

1. `scripts/_incident_live_evidence_support.py`
2. `tests/integration/test_incident_live_evidence_runner.py`
3. `docs/decisions/P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md`
4. `docs/decisions/P2A_INCIDENT_BUILD_EVIDENCE_RECEIPT.md` (this file)

`git status --porcelain` shows exactly 23 modified + 16 new +
1 preserved-untracked-assessment = 39 non-assessment entries, identical in
membership to the prior repair round — no path was added or removed.
Protected paths (migrations 001-004, the existing PostgreSQL live test
module, task/event/customer-request services and routers, auth/JWT code,
approval storage schema and migration 004, file-size debt baseline/exception
registry/guard implementation, ADR/SPEC/WORK_ORDER, CVF core and `.cvf/**`,
the preserved assessment) all show **zero diff** (verified via
`git diff --stat`).

## 3. Repair of INC-REV-F6

The fix is structural, not another regex layer. `_clean_endpoint(endpoint)`
(new, in `_incident_live_evidence_support.py`) strips userinfo, query and
fragment from the endpoint **before** any `Request`/`urlopen` call is ever
constructed, returning both the cleaned URL and the list of stripped secret
fragments. `call_provider` now:

- builds `req = urllib.request.Request(clean_endpoint, ...)` from the cleaned
  URL only, so `req.full_url` can never carry embedded credential material
  regardless of what a later exception stringifies;
- moved `Request(...)` construction itself inside the same `try`/`except` as
  `urlopen`, so request-construction failures are sanitized identically to
  transport failures (previously only the latter were inside the guarded
  block);
- scrubs the stripped endpoint secret fragments from any error text as a
  second, defense-in-depth layer, in addition to the existing API-key/
  bearer/JWT scrubbing.

Four new tests in `tests/integration/test_incident_live_evidence_runner.py`
use `_ENDPOINT_SENTINEL`, a value distinct from the existing `_SENTINEL_KEY`,
embedded in the endpoint's userinfo, query and fragment simultaneously:

- `test_clean_endpoint_strips_userinfo_query_and_fragment` — unit-level proof
  of the split.
- `test_call_provider_transport_exception_embedding_full_url_never_leaks_endpoint_sentinel`
  — a fake `urlopen(req, ...)` raises using the exact `req.full_url` it
  received, proving the absence is structural (the URL was already clean by
  construction time), not incidental.
- `test_call_provider_request_construction_failure_never_leaks_endpoint_sentinel`
  — a fake `Request()` constructor raises using the `url` argument it
  received, covering construction failures distinctly from transport ones.
- `test_endpoint_sentinel_absent_from_summary_stdout_stderr_and_receipt` — full
  pipeline: `call_provider` → printed stdout/stderr lines → `render_receipt`
  → asserts the sentinel is absent from the returned summary (JSON-dumped),
  captured stdout, captured stderr, and the written receipt file, all in one
  test.

## 4. Focused test results (post-F6-repair)

| Suite | Result |
|---|---|
| `tests/integration/test_incident_live_evidence_runner.py` | 17 passed |
| `tests/cvf/test_incident_vertical.py` | 25 passed |
| `tests/integration/test_schema_parity_incidents.py` | 9 passed |
| `tests/integration/test_sql_ledger_incidents.py` | 11 passed |
| `tests/unit/test_incident_openapi_contract.py` | 2 passed |
| `tests/unit/test_p2b_openapi_contract.py` | 3 passed |
| `tests/unit/test_operations_domain_shim_identity.py` | 23 passed |
| `tests/unit/test_operations_domain_serialization.py` | 53 passed |
| `apps/workspace-api/src/workspace_api/tests/test_lifecycle.py` | 4 passed |
| `tests/cvf/test_ledger_protocol.py` | 3 passed |
| `tests/integration/test_evidence_persistence.py` | 7 passed |
| `tests/integration/test_postgres_live_runner.py` | 14 passed |

## 5. Full non-live suite (post-F6-repair)

`python -m pytest -q` → **511 passed, 44 skipped, 0 failed, 1 warning.**

Zero failures, zero errors. The pre-existing `InsecureKeyLengthWarning` (an
unrelated, pre-existing test fixture's short HMAC key) is the only warning.
`scripts/run_incident_live_governance_evidence.py --dry-run` re-verified
separately: all 5 refusal cases still PASS, genuine acknowledgement
construction still succeeds, stopping before any provider call as designed.

## 6. Disposable PostgreSQL 16 round-trip (rerun after this repair)

`python scripts/run_postgres_live_roundtrip.py --json`:

- `docker_server_version`: 29.6.2; `image`: `postgres:16-alpine`.
- Migrations: first attempt **18 applied / 0 skipped**; reapply **15 applied /
  3 skipped**.
- Live suite (`test_sql_ledger_postgres_live.py` +
  `test_incident_postgres_live.py`): **44 passed**, 0 failed.
- Cleanup: `container_absent_after_cleanup: true`;
  `anonymous_volumes_still_present: []`. Independently confirmed with
  `docker ps -a` / `docker volume ls` before and after — no `cvf-pg-live-*`
  residue at any point.

## 7. Real provider-bound incident governance evidence (rerun after this repair)

`python scripts/run_incident_live_governance_evidence.py`:

- 5 refusal cases (insufficient evidence, fabricated approval, self-approval,
  inactive approver, stale version) — all **PASS**, **0 provider calls each**
  (observed via the fresh `ProviderCallCounter`, not asserted).
- Genuine authenticated acknowledgement (distinct approver + confirmer, both
  via minted JWT + real HTTP through the FastAPI route chain) — **PASS**.
- Real provider call: **exactly 1**, outcome **PASS**, HTTP 200, model
  `qwen3.7-max`, endpoint (host only) `https://dashscope-intl.aliyuncs.com`.
  Fresh sanitized receipt:
  `docs/decisions/P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md` — contains no API
  key, Authorization header, JWT, raw secret, or URL userinfo/query/fragment;
  this fully replaces the prior receipt as required (a repair invalidates
  the previous live receipt as closure evidence).

## 8. File line counts (every touched/created Python file, hard limit 300)

```
packages/operations-domain/src/operations_domain/models.py            236
packages/operations-domain/src/operations_domain/lifecycle.py          93
apps/workspace-api/src/workspace_api/domain/models.py                  91
apps/workspace-api/src/workspace_api/domain/lifecycle.py               27
packages/cvf-runtime/src/cvf_runtime/permission.py                     87
packages/operations-ledger/src/operations_ledger/ledger.py            123
packages/operations-ledger/src/operations_ledger/tables.py            285
packages/operations-ledger/src/operations_ledger/_incident_tables.py   48
packages/operations-ledger/src/operations_ledger/sql_ledger.py        298
packages/operations-ledger/src/operations_ledger/_incident_store.py   118
apps/workspace-api/.../infrastructure/repository.py                   264
apps/workspace-api/.../infrastructure/_incident_repository.py          53
apps/workspace-api/.../application/incident_service.py                154
apps/workspace-api/.../api/incidents/router.py                        115
apps/workspace-api/src/workspace_api/main.py                           33
apps/workspace-api/.../application/approval_receipts.py               198
apps/workspace-api/.../tests/test_lifecycle.py                         22
tests/cvf/test_ledger_protocol.py                                      44
tests/cvf/test_incident_vertical.py                                   300
tests/integration/test_schema_parity_incidents.py                     121
tests/integration/test_sql_ledger_incidents.py                        201
tests/integration/test_evidence_persistence.py                        212
tests/integration/test_incident_postgres_live.py                      163
tests/unit/test_incident_openapi_contract.py                           69
tests/unit/test_operations_domain_shim_identity.py                    129
tests/unit/test_operations_domain_serialization.py                    287
scripts/run_incident_live_governance_evidence.py                      253
tests/integration/test_incident_live_evidence_runner.py               271
scripts/run_postgres_live_roundtrip.py                                300
tests/integration/test_postgres_live_runner.py                        217
tests/unit/test_p2b_openapi_contract.py                                165
scripts/_incident_live_evidence_support.py                             190
```

All within the 300-line hard limit (none compressed to fit —
`tests/cvf/test_incident_vertical.py` and `scripts/run_postgres_live_roundtrip.py`
sit exactly at 300 with normal formatting, unchanged by this finding). Only
`scripts/_incident_live_evidence_support.py` (149 → 190) and
`tests/integration/test_incident_live_evidence_runner.py` (186 → 271) grew in
this repair round; every other file's line count is unchanged from the prior
receipt. `tables.py`, `sql_ledger.py`, and `repository.py` remain wiring
surfaces only. Debt baseline and exception registry were not touched.

## 9. Repository gates (post-F6-repair)

- `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`.
- `python scripts/generate_catalog.py --check` (and `--write`, since LOC
  changed) → `CATALOG VERIFY: PASS` (20 modules, metrics/Markdown
  regenerated and verified in sync).
- `python scripts/check_session_state.py` → `SESSION STATE: PASS`.
- `python scripts/testing/validate_repository.py` → PASS (catalog + session +
  file-size).
- Workspace doctor → `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))`,
  unchanged bounded legacy note.
- `git diff --stat` against every protected path → zero diff.

## 10. Statement

No stage, commit, or push occurred at any point during this repair. Exactly
the 39 authorized paths were touched or created; no 40th path was modified;
only the four paths this finding permits were edited. Claude stops here at:

`READY_FOR_INDEPENDENT_INCIDENT_BUILD_RE_RE_REVIEW`

## 11. Independent reviewer disposition

Reviewer: Codex
Disposition: `REVIEW_PASS`
Date: 2026-07-26

The reviewer independently rehydrated the amended authorization and verified
the exact 39-path candidate. `INC-REV-F1` through `INC-REV-F6` close without
waiver.

Independent evidence:

- F6 adversarial probes forced both transport and request-construction
  exceptions to include the URL passed to them. A URL-only sentinel distinct
  from the API-key sentinel was absent from returned summaries, stdout,
  stderr and rendered receipt; focused F5/F6 suite: 17 passed.
- Full non-live suite: 511 passed, 44 skipped, 1 pre-existing warning.
- Repository validator, catalog, session-state, file-size, diff and workspace
  doctor gates passed; doctor retained only the bounded legacy catalog note.
- PostgreSQL evidence remained applicable because F6 changed only provider
  support/test/receipts: the reviewer-owned run on the byte-identical database
  changed set passed 44 live tests, migrations 18/0 then 15/3, with exact
  container and captured-volume cleanup.
- Fresh post-F6 real-provider rerun passed five observed-zero-call refusal
  cases, the authenticated R2 acknowledgement, and exactly one
  `qwen3.7-max` call with HTTP 200. The live receipt was regenerated.
- AC-18 rollback rehearsal scoped-stashed exactly the 39 BUILD paths in the
  current working tree, leaving only the preserved assessment. C3 parent
  `eb4597169dee176c62284c198ae375cbfc3511a8` passed 427 tests with 36 skips
  and the validator/catalog/session/file-size gates. The candidate restored
  to the same 39-path membership, zero staged paths and exact raw blobs for
  all 16 untracked BUILD files; no temporary stash or worktree remained.

Two preliminary detached-worktree attempts were explicitly rejected as
AC-18 evidence because Windows checkout line-ending conversion invalidated
legacy debt hashes. Both temporary worktrees were removed. The successful
current-worktree rehearsal above is the sole AC-18 evidence used for this
disposition.

Claim boundary remains the ADR/SPEC boundary: one governed incident vertical
on InMemoryLedger, SQLite and disposable local PostgreSQL 16, with a real
provider-bound governance receipt. It does not close handovers, reports, UI,
managed/production PostgreSQL readiness, or production API provider routing.
