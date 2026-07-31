# P2-R Operational Report and Freeze Prerequisite — BUILD Evidence Receipt

- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Role: `REPAIR_WORKER` — this is the **fourth** bounded repair round, all
  within the original exact 59-path Work Order ceiling; no Amendment used
  or needed at any round.
- Parent (repair start and end): `HEAD == origin/main == 6b2d014d5f3be2a91f209e7d33c176216e5b5a50`
- Independent review dispositions consumed:
  1. `REVIEW_FINDINGS P2R_BUILD_REPAIR_AUTHORIZED_WITHIN_EXISTING_59_PATH_CEILING`
  2. Second-round review: three residual gaps (F5 canonicality still open,
     F6 write-reservation over-broad, PostgreSQL runner/receipt claims
     inaccurate) — closed in an earlier revision of this receipt.
  3. Third-round review: canonical `ReportContent` still accepted four
     probes it should reject, the SQLite write-reservation marker leaked
     through pool reuse, and PostgreSQL readiness was proven only by an
     internal heuristic — closed in the prior revision of this receipt.
  4. **Fourth-round review (this revision)**: two further residual gaps —
     the canonical model *over-rejected* valid domain data (empty-string
     `title`, a legal `0 -> 1` Correction) while still *under-validating*
     evidence-list order, and the PostgreSQL failure-sanitization path still
     emitted/stored a database URL (redacted-password form) that R32
     prohibits outright, plus a prior receipt's false "no database URL was
     printed or stored" claim.
- Status: `READY_FOR_INDEPENDENT_P2R_BUILD_FINAL_REVIEW`

This worker did not stage, commit, push, review, or FREEZE. All facts below
are worker-observed at repair time and are subject to independent re-review.

## Fourth-round findings closed in this revision

### Finding 1 — canonical validation over-rejected valid domain data and under-validated evidence order

Three independent defects, all in
`packages/operations-domain/src/operations_domain/report_models.py`:

1. **`_is_str` required `v != ""`.** `Task.title`, `OperationalEvent.title`,
   and every other plain `str` domain field allow empty strings (no
   `min_length` on any owning Pydantic model, no NOT-NULL-but-nonempty DB
   constraint, no JSON Schema `minLength`). A genuine
   `Task(title="")` → `build_snapshot(...)` was rejected by `ReportSection`
   validation — a stricter rule than the model it exists to mirror.
2. **`_INT` (integer >= 1) was reused for `Correction.previous_version`/
   `new_version`.** The actual persisted invariant
   (`database/migrations/001_foundation.sql:76`,
   `CHECK (new_version > previous_version)`) has no lower bound at all — a
   genuine, domain/persistence-valid `0 -> 1` Correction was rejected.
3. **Evidence-list canonical ordering was never enforced.** R7's canonical
   evidence order — `(evidence_id, source_type, source_id, sha256 or "")` —
   was checked nowhere: a reversed evidence list with a correctly
   recomputed `source_digest` still validated
   (`REVERSED_EVIDENCE_ORDER=ACCEPTED`).

Fixed:

- `_is_str` no longer excludes the empty string; it still requires
  `isinstance(v, str)` (dict/list/int/bool are still rejected). Every
  `_STR`/`_OPT_STR`-tagged field across all six record schemas now accepts
  every value its owning domain/API/DB contract accepts, nothing stricter.
- Split the integer predicate in two: `_INT` (`isinstance(int) and not bool
  and >= 1`) remains reserved for `ReportSourceRef.source_version` and the
  six record types' own `version` fields (SPEC-required, unchanged
  semantics); a new `_CORRECTION_VERSION` (`isinstance(int) and not bool`,
  no lower bound) is used for `Correction.previous_version`/`new_version`
  only, matching the actual CHECK constraint.
- Added a cross-field check inside `_check_dict_shape`: when the schema is
  `Correction`'s, `new_version <= previous_version` now raises — closing
  the gap where a bad Correction (e.g. `2 -> 2`) would otherwise validate
  once the integer predicate alone stopped requiring `>= 1`.
- Added `_evidence_sort_key`/an ordering check inside `_check_list`,
  triggered whenever `schema is _EVIDENCE_SCHEMA`: every evidence list —
  OperationalEvent's, Task's, Incident's, and every Handover item's nested
  evidence list (all route through the same `_EVIDENCE_T` tag and therefore
  the same `_check_list` call) — must be in exact R7 tuple order
  `(evidence_id, source_type, source_id, sha256 or "")`.
- File held at exactly 300 lines after these additions (condensed
  docstrings/comments; no logic removed).

**No new business rule was invented and no field was made stricter than its
owning model** — `_check_dict_shape`'s field-set/type/enum/UUID/datetime
checks, `_manifest_matches_records_exactly`'s manifest cross-checks
(membership, order, `source_version` equality, `source_digest` equality),
and `ReportSection`'s R7 per-section record ordering are all unchanged.

Tests (all in-ceiling, no new path):

- `tests/cvf/test_report_freeze.py` (held at exactly 300 lines): added
  `test_task_record_with_empty_string_title_is_accepted` (positive:
  `title=""` now validates), `test_correction_zero_to_one_is_accepted`
  (positive: a real `0 -> 1` Correction record validates),
  `test_correction_new_version_not_greater_than_previous_rejected`
  (negative: `2 -> 2` raises), `test_reversed_task_evidence_order_rejected`
  (negative: two evidence items in the wrong order raise),
  `test_sorted_task_evidence_order_accepted` (positive: correctly ordered
  evidence still validates).
- `tests/integration/test_schema_parity_reports.py` (held at exactly 300
  lines): added `test_reversed_nested_handover_item_evidence_order_rejected`
  — proves the R7 evidence check also fires one level deeper, inside a
  Handover item's own nested `evidence` list, not just a top-level record's.
- The four previously repaired probes
  (`test_probe_wrong_field_types_rejected`,
  `test_probe_source_version_mismatch_rejected`,
  `test_probe_source_digest_mismatch_rejected`,
  `test_probe_reversed_canonical_order_rejected`) and the genuine-snapshot
  positive control
  (`test_build_snapshot_output_is_accepted_by_the_canonical_model`) in
  `tests/cvf/test_report_approval.py` are unchanged and still pass —
  verified by direct re-run, not merely "should still pass" reasoning.

### Finding 2 — PostgreSQL failure sanitization still emitted/stored a database URL

An independent timeout probe against `wait_ready_via_database` returned:

```text
connection to <redacted-database-url> refused
```

i.e. a connection-refused failure whose message embedded a complete
PostgreSQL connection string (scheme, username, host, port, database name)
with only the password masked. SPEC R32 prohibits any database
credential/URL from being printed or stored at all — a redacted-password
URL is still a complete database URL. Separately, the prior revision's
BUILD receipt itself recorded that same URL-shaped string from a failed
run while claiming "no database URL was printed or stored" — that specific
claim was false in that revision; it is retracted here, and no
scheme/user/host/port/database value from that run is reproduced in this
document.

Fixed in `scripts/run_postgres_live_roundtrip.py` (held at exactly 299
lines):

- `wait_ready_via_database`'s failure path no longer builds its message
  from `str(exc)` (or any sanitized-but-still-URL-shaped derivative of it)
  at all. It now retains only `type(exc).__name__` across retries and
  raises a fixed-shape message —
  `f"database not reachable on the mapped port within {timeout_s}s
  ({last_error_class})"` — which cannot contain a username, password,
  scheme, host, port, or database name because none of that data is ever
  read into the message in the first place.
- `run_once`'s public summary dropped the `database_url_redacted` field
  entirely (it was a complete PostgreSQL URI with only the password
  masked, in violation of R32). `host_port`/`container_name` remain (a bare
  port number and a container name are not a database URL and cannot
  reconstruct one).
- `sanitize_output`/`redact` no longer rely solely on an exact-string match
  against one known `database_url` value (which missed psycopg's own
  `postgresql://` DSN form — the `+psycopg` suffix is stripped before
  `psycopg.connect()`, so a raw driver exception's embedded DSN never
  byte-matches the original SQLAlchemy-style URL). A new module-level regex
  `_PG_URI = re.compile(r"postgresql(?:\+psycopg)?://[^\s'\"]*")` scrubs
  **any** `postgresql://` or `postgresql+psycopg://` URI found anywhere in
  output text, in addition to (not instead of) the existing exact-match and
  password substitution.
- Bounded timeout, the mapped-host-port `psycopg.connect()` + `SELECT 1`
  check, cleanup-on-failure, and BEGIN IMMEDIATE/deferred-BEGIN transaction
  behavior are all unchanged.

Verified directly: with the generic `_PG_URI` regex temporarily reverted to
exact-match-only (scratchpad-only comparison, never left in the
repository), a failure embedding the plain `postgresql://` DSN (not the
original `+psycopg` URL) leaked the username, host, port and database name
into `run_once`'s JSON summary — reproducing exactly the class of gap this
finding describes. With the fix restored, the same scenario produces zero
leakage.

Tests (all in-ceiling, no new path) in
`tests/integration/test_postgres_live_runner.py` (held at exactly 299
lines):

- `test_wait_ready_via_database_never_leaks_dsn_on_timeout`: a fake
  `psycopg.connect` raises with the full DSN embedded in its message;
  asserts the raised `LiveRoundTripError` contains none of
  password/username/either URL scheme/host/port/database name/either
  complete URL, and does contain the exception class name.
- `test_run_once_summary_never_contains_a_database_url`: a full successful
  `run_once` run; asserts `"database_url_redacted"` is absent from the
  summary dict entirely and no secret/URI fragment appears in its JSON
  serialization.
- `test_run_once_sanitizes_sentinel_when_an_ordinary_exception_is_raised`
  (extended, not duplicated): the existing PG-REV-F6 test's injected
  `RuntimeError` now embeds the **plain** `postgresql://` DSN (psycopg's
  own form) instead of only the `+psycopg` one, and additionally asserts
  `"database_url_redacted"` is absent and `"postgresql://"` does not appear
  anywhere in the summary's JSON serialization — this is the test that
  caught the regression described above when the generic-regex fix was
  temporarily reverted for verification.
- `test_sanitize_output_scrubs_sentinel_password_and_full_url` (extended):
  now also asserts a `postgresql://` (non-`+psycopg`) variant embedded in
  the same text is scrubbed and that `"<redacted-database-url>"` appears in
  the cleaned output.

## First three rounds' findings — summary, unchanged from prior revisions

The original eight findings (F1-F8), the second round's three residual
gaps, and the third round's three residual gaps (canonical model value/
type/format + manifest cross-check closure, SQLite write-reservation
scoping, PostgreSQL mapped-port readiness) were repaired in earlier
revisions of this receipt and remain repaired. This round's two findings
are further, narrower gaps in exactly the same two areas the third round
closed (canonical validation, PostgreSQL runner sanitization) — not a
reopening of anything closed in rounds one through three.

## Changed-set: exactly 59 paths (unchanged ceiling)

Every path below is one of the original Work Order's 59 authorized paths.
No path outside this list was touched, and no Amendment was used or needed
in this fourth repair round. `git status --porcelain` confirms exactly 59
entries, both immediately before this revision began and after all work
completed; zero paths are staged.

### Domain, persistence, application and contract (25)

1. `database/migrations/007_report_history_constraints.sql`
2. `packages/operations-domain/src/operations_domain/report_models.py` — Finding 1 (empty-string strings, Correction version split + ordering, R7 evidence ordering)
3. `packages/operations-domain/src/operations_domain/models.py`
4. `packages/operations-domain/src/operations_domain/lifecycle.py`
5. `apps/workspace-api/src/workspace_api/domain/models.py`
6. `apps/workspace-api/src/workspace_api/domain/lifecycle.py`
7. `packages/cvf-runtime/src/cvf_runtime/permission.py`
8. `packages/operations-ledger/src/operations_ledger/ledger.py`
9. `packages/operations-ledger/src/operations_ledger/_report_tables.py`
10. `packages/operations-ledger/src/operations_ledger/tables.py`
11. `packages/operations-ledger/src/operations_ledger/_report_store.py`
12. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
13. `apps/workspace-api/src/workspace_api/infrastructure/_report_repository.py`
14. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
15. `apps/workspace-api/src/workspace_api/application/report_snapshot.py`
16. `apps/workspace-api/src/workspace_api/application/report_service.py`
17. `apps/workspace-api/src/workspace_api/application/report_freeze.py`
18. `apps/workspace-api/src/workspace_api/application/shift_service.py`
19. `apps/workspace-api/src/workspace_api/application/approval_receipts.py`
20. `apps/workspace-api/src/workspace_api/api/reports/router.py`
21. `apps/workspace-api/src/workspace_api/api/shifts/router.py`
22. `apps/workspace-api/src/workspace_api/main.py`
23. `packages/workspace-contracts/reports/shift-report.schema.json`
24. `docs/domain/REPORT_MODEL.md`
25. `docs/workflows/END_SHIFT_REPORT.md`

### Unit, CVF and integration tests (25)

26. `tests/unit/test_report_snapshot.py`
27. `tests/unit/test_report_openapi_contract.py`
28. `tests/unit/test_operations_domain_shim_identity.py`
29. `tests/unit/test_operations_domain_serialization.py`
30. `tests/unit/test_p2b_openapi_contract.py`
31. `tests/unit/test_p2c_read_openapi_contract.py`
32. `tests/unit/test_shift_create_openapi_contract.py`
33. `tests/unit/test_message_openapi_contract.py`
34. `tests/cvf/test_report_vertical.py`
35. `tests/cvf/test_report_approval.py`
36. `tests/cvf/test_report_freeze.py` — Finding 1 (5 new tests: empty title, Correction 0->1, bad Correction order, reversed/sorted evidence)
37. `tests/cvf/test_ledger_protocol.py`
38. `tests/cvf/test_freeze_invariant.py`
39. `tests/cvf/test_atomic_mutation_audit.py`
40. `tests/cvf/test_customer_request_vertical.py`
41. `tests/cvf/test_shift_close_freeze_interaction.py`
42. `tests/integration/test_report_ledger_parity.py`
43. `tests/integration/test_schema_parity_reports.py` — Finding 1 (nested Handover-item evidence ordering test)
44. `tests/integration/test_schema_parity.py`
45. `tests/integration/_schema_parity_parsing.py`
46. `tests/integration/test_report_postgres_live.py`
47. `tests/integration/test_handover_postgres_live.py`
48. `tests/integration/test_postgres_live_runner.py` — Finding 2 (DSN-leak/summary tests, extended existing F6/F2 tests)
49. `tests/integration/test_report_live_evidence_runner.py`
50. `tests/integration/test_handover_live_evidence_runner.py`

### Live runners (4)

51. `scripts/run_postgres_live_roundtrip.py` — Finding 2 (fixed safe failure message, dropped `database_url_redacted`, generic URI-scrub regex)
52. `scripts/run_report_live_governance_evidence.py`
53. `scripts/_report_live_evidence_support.py`
54. `scripts/run_handover_live_governance_evidence.py`

### Receipts and implementation-truth surfaces (5)

55. `docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_BUILD_EVIDENCE_RECEIPT.md` — this file, rewritten again
56. `docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_LIVE_EVIDENCE_RECEIPT.md` — retained from the prior round (see Provider evidence section below; not stale)
57. `docs/cvf/CVF_CONTROL_MAPPING.md`
58. `docs/catalog/MODULE_REGISTRY.json`
59. `docs/catalog/MODULE_CATALOG.md`

Every one of the 59 paths above carries a meaningful diff. Verified:
`git status --porcelain | wc -l` = 59, both immediately before this
revision began and after all work completed; `git diff --cached --name-only`
is empty (zero staged).

## File-size discipline this round

Both semantically-changed Python files were driven back to their exact
caps after each round of edits:

- `packages/operations-domain/src/operations_domain/report_models.py`:
  Finding 1's three fixes initially pushed the file to 317 lines;
  condensed (docstring/comment trims, no logic removed) back to exactly
  300.
- `scripts/run_postgres_live_roundtrip.py`: Finding 2's fixes initially
  pushed the file to 308 lines; condensed back to exactly 299 (one line
  under cap, matching its pre-existing state).
- `tests/cvf/test_report_freeze.py`: the 5 new Finding 1 tests initially
  pushed the file to 331 lines; two tests were relocated to
  `tests/integration/test_schema_parity_reports.py` (which had headroom)
  and the remainder condensed to land at exactly 300.
- `tests/integration/test_schema_parity_reports.py`: received the
  relocated nested-Handover-evidence test; condensed to exactly 300.
- `tests/integration/test_postgres_live_runner.py`: Finding 2's 4 new
  tests initially pushed the file to 351 lines; consolidated by extending
  existing PG-REV-F6 tests instead of duplicating `run_once` scenarios,
  and by broadening the shared `_stub_ready` helper to cover more common
  setup — landed at exactly 299, with all 21 tests (down from a
  transient 22 during consolidation, since one standalone test was merged
  into an existing one rather than kept separate) passing.

`python scripts/check_file_size.py` → **PASS** after every fix in this
round.

## Test commands and exact counts (rerun after all semantic changes above)

### Focused (Work Order section 7 command, exact documented order)

```
python -m pytest -q tests/unit/test_report_snapshot.py tests/unit/test_report_openapi_contract.py tests/unit/test_operations_domain_shim_identity.py tests/unit/test_operations_domain_serialization.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_message_openapi_contract.py tests/cvf/test_report_vertical.py tests/cvf/test_report_approval.py tests/cvf/test_report_freeze.py tests/cvf/test_ledger_protocol.py tests/cvf/test_freeze_invariant.py tests/cvf/test_atomic_mutation_audit.py tests/cvf/test_customer_request_vertical.py tests/cvf/test_shift_close_freeze_interaction.py tests/integration/test_report_ledger_parity.py tests/integration/test_schema_parity_reports.py tests/integration/test_schema_parity.py tests/integration/test_postgres_live_runner.py tests/integration/test_report_live_evidence_runner.py tests/integration/test_handover_live_evidence_runner.py
```

Result: **385 passed**, zero failures, zero collection errors.

### Full non-live

```
python -m pytest -q
```

Result: **998 passed, 87 skipped, 0 failed** (skips are the opt-in live
PostgreSQL suites, correctly skipped without `LIVE_POSTGRES_DATABASE_URL`).

### Repository gates

- `python scripts/testing/validate_repository.py` → **PASS**
- `python scripts/generate_catalog.py --check` → **PASS** (20 modules, all
  paths exist, statuses valid, metrics and Markdown up to date — no
  regeneration was needed this round)
- `python scripts/check_session_state.py` → **PASS**
- `python scripts/check_file_size.py` → **PASS**
- `git diff --check` → exit 0 (one benign LF/CRLF line-ending notice on
  `tests/integration/test_postgres_live_runner.py`, not a whitespace error)
- JSON validity: `docs/catalog/MODULE_REGISTRY.json` and
  `packages/workspace-contracts/reports/shift-report.schema.json` both
  parse cleanly via `json.load`
- Path/staging check: `git status --porcelain | wc -l` = 59;
  `git diff --cached --name-only` empty

### Workspace doctor

Run via CVF core's `check_cvf_workspace_agent_enforcement.ps1` against this
project path:

```
RESULT: PASS WITH NOTE (24 passed, 1 warning(s))
```

The sole warning is the pre-existing, bounded legacy note: `Governed
downstream catalog kit not present` → `LEGACY_PROJECT: no governed-catalog
manifest marker or surface found; skipping governed catalog check for
bounded legacy compatibility.` No new FAIL or WARN was introduced.

## PostgreSQL 16 disposable-local evidence (automated, re-run after Finding 2)

`scripts/run_postgres_live_roundtrip.py --json`, fully automated, no manual
container management, run once this round (Docker daemon confirmed
available first):

- `docker_server_version` 29.6.2, `psycopg_version` 3.3.4; migrations first
  attempt **22 applied, 0 skipped**, reapply **18 applied, 4 skipped**;
  live suite **77 passed**, `live_suite_returncode: 0`, `failure: null`;
  `container_absent_after_cleanup: true`,
  `anonymous_volumes_still_present: []`.
- The public summary this round contains **no `database_url_redacted`
  field and no PostgreSQL URI of any kind** — directly confirming
  Finding 2's fix in real (not simulated) output.

Live suite (`test_sql_ledger_postgres_live.py`, `test_incident_postgres_live.py`,
`test_handover_postgres_live.py`, `test_shift_create_postgres_live.py`,
`test_message_postgres_live.py`, `test_report_postgres_live.py`) covers all
six coherent modules per SPEC R30.

Independently re-verified after the run via `docker ps -a --filter
name=cvf-pg-live-` (empty) and a direct volume-name lookup for the captured
anonymous volume `f1793249c3a5915b3d65cfa2e9e720e5194762c38fc463554c72b70cf7f098f3`
(not found — confirmed removed). No bind mount or named volume was ever
passed to `docker run`.

**This is the primary and only PostgreSQL evidence for this round** — no
manual container fallback was used or is claimed as evidence.

## Provider evidence: retained, not rerun

`docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_LIVE_EVIDENCE_RECEIPT.md` is
**retained from the prior (third) round**, generated
2026-07-31T08:17:39Z, and is **not stale**: this round changed only the
canonical validator (`report_models.py`), the PostgreSQL runner and its
tests, and receipt wording — no production/report semantic route, no
report generate/submit-review/approve/freeze code path, and no provider
call path changed. The retained receipt's seven refusal cases (zero
provider calls each) and its one genuine provider call (Alibaba
`qwen3.7-max`, HTTP 200, `CVF_REPORT_EVIDENCE_OK`) are unaffected by this
round's changes and remain accurate. **Provider evidence was NOT rerun
this round**; this is an explicit statement of why the retained receipt is
still valid, not a claim that it was regenerated.

## Sanitization and secret discipline

No API key, JWT secret/token, Authorization header, database credential/URL,
raw provider body, or other machine-local secret was printed, stored, or
committed anywhere in this revision's output, test code, receipts, or this
document. Finding 2's database-URL leak (redacted-password form) was found
by independent review, reproduced under controlled test conditions (see
Finding 2 above), fixed, and re-verified with real automated PostgreSQL
evidence (see above) whose actual summary output contains no PostgreSQL URI
of any kind — not merely a claim that it should not.

## Preserved nonclaims

This repair does not claim, and this receipt does not assert:

- P5-A report rendering/export/PDF/Excel generation
- AI-generated operational truth or provider-authored report content
- production or managed-PostgreSQL readiness (disposable local PostgreSQL
  16 only; "durable readiness" is not claimed — only that the mapped
  host port/database was reachable at the moment this round's run passed)
- assignment/tenant/data-scope authorization
- P2-C mutation/full UI, P2-D offline/realtime, or the full-shift exit gate
- Phase 2 completion
- support for any report type other than the fixed `END_SHIFT`
- production concurrency/load/HA beyond the tested SERIALIZABLE-with-retry
  transaction boundary
- that provider evidence was regenerated this round (explicitly retained,
  as stated above)

## Worker declaration

This worker did not stage, commit, push, self-review, or FREEZE. All 59
paths above are the complete, final changed set; no path outside it was
touched, and no Amendment was used or needed. Every one of the 59 paths
carries a meaningful diff. Migrations 001-006 have zero-byte diff (only
migration 007 exists, unchanged from the prior BUILD).

READY_FOR_INDEPENDENT_P2R_BUILD_FINAL_REVIEW
