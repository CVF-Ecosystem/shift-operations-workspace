# Message Admission and Trust Repair — BUILD Evidence Receipt

Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
Role: `IMPLEMENTATION_WORKER` → `REPAIR_WORKER` (first OpenAPI golden-proof
repair round) → bounded `REPAIR_WORKER` (Amendment 2 round) → bounded
`REPAIR_WORKER` (F2/F4 re-repair round) → bounded `REPAIR_WORKER` (this
round, no Amendment 3: one further F2 branch found and closed) (Claude)
Status: `READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_FINAL_REVIEW`

**This receipt replaces the prior BUILD evidence receipt in full.** Nothing
here is inherited unverified from that receipt. History of F2 across rounds:
Amendment 2 covered numeric out-of-range ports and malformed IPv6 inside
`call_provider`; the next round closed a non-numeric secret-bearing port
whose `ValueError` embedded the secret verbatim; **this round** closes a
third branch: `runner.main()` calls `safe_endpoint_description(endpoint)`
*before* `call_provider` runs at all, and that function had no failure
boundary of its own, so a malformed IPv6 (or any other endpoint the operator
configures via `DASHSCOPE_BASE_URL`/`ALIBABA_BASE_URL`) raised a raw
`ValueError` straight out of `main()`, entirely bypassing `call_provider`'s
sanitized boundary. F4 remains closed as verified in the prior round; not
reopened here.

## 1. Continuity and G6 facts (independently re-verified this round)

- `HEAD == origin/main == 11e1d36b0d6b4774605978ae19532dcce0abbb72` (post
  Amendment 2 commit `8d5c085`) throughout this entire round — no stage/
  commit/push at any point.
- Dirty BUILD set at round start: exactly 29 paths, zero staged — verified
  before any edit.
- Final C3 ceiling: exactly 30 paths (unchanged this round; no Amendment 3
  required).
- Docker daemon (stopped mid Amendment-2-round, started by the operator per
  this repository's established convention of the worker never starting it
  itself) was confirmed already responsive (`docker version` succeeded) at
  the start of this round — no new stop/start cycle needed.
- Provider credential candidate present: `True` (value never read, printed,
  or logged).

## 2. Findings closed without waiver

### `MAR-BUILD-REV-F1 FULL_REGRESSION_AND_CEILING_GAP` — closed

`tests/unit/test_shift_create_openapi_contract.py` (path 30, the sole
addition to the ceiling) now reverses the **complete** later
message-admission SPEC R13 delta — `security` on `POST /messages`, plus
`MessageInput.required` restored to `["shift_id", "sender_id", "text"]`,
`sender_id` restored to `{"title": "Sender Id", "type": "string"}`, `source`
restored to `{"default": "INTERNAL", "title": "Source", "type": "string"}`
— asserting the current authorized shape before reversal, before hashing
its own unchanged `PRE_SHIFT_CREATE_OPENAPI_SHA`. No historical baseline
digest was refreshed. The same complete-reversal logic was applied to the
two other authorized OpenAPI chain files
(`tests/unit/test_p2b_openapi_contract.py`,
`tests/unit/test_p2c_read_openapi_contract.py`), which had the same gap.

### `MAR-BUILD-REV-F2 ENDPOINT_PORT_SECRET_LEAK` — closed (three branches, all rounds)

**Branch 1 (Amendment 2):** numeric out-of-range port and malformed IPv6,
both raising at `urlsplit`/`.port` time inside `call_provider` before its
`try`/`except` existed — fixed by moving `_clean_endpoint` inside the
boundary.

**Branch 2 (prior round):** a non-numeric port such as
`:PORT_SECRET_7c6b5a493827` makes `urlsplit(...).port` raise `ValueError`
with the raw offending fragment embedded verbatim in the message text
(`Port could not be cast to integer value as 'PORT_SECRET_7c6b5a493827'`),
which the generic `except Exception` handler had no `endpoint_secrets` list
to redact — fixed in `_clean_endpoint` by capturing `parts.netloc` as a
secret fragment before `.port` is accessed, and re-raising any port-access
`ValueError` as a `_EndpointParseError` with a static, secret-free message.

**Branch 3 (this round, closed for real):** `runner.main()` calls
`safe_endpoint_description(endpoint)` at line 256, *before* `call_provider`
is ever invoked at line 258 — and `safe_endpoint_description` itself had no
failure boundary: it called `urlsplit(endpoint)` and `.hostname` directly.
A malformed IPv6 endpoint (or any other operator-configured
`DASHSCOPE_BASE_URL`/`ALIBABA_BASE_URL` that fails to parse) raised a raw
`ValueError` straight out of `main()` — never reaching `call_provider`'s
sanitized boundary at all, regardless of how well-sanitized that boundary
now is. Reproduced independently before the fix: calling
`safe_endpoint_description` directly on a malformed-IPv6 endpoint containing
a sentinel raised `ValueError: Invalid IPv6 URL` (the sentinel itself is not
embedded in *that* particular message, but the crash still escaped `main()`
as an unhandled traceback with no sanitized failure outcome at all).

Fixed: `safe_endpoint_description` now wraps its body in
`try`/`except ValueError`, returning the fixed literal
`"<unparseable-endpoint>"` on any parse failure — it never raises and never
returns anything derived from the unparsed endpoint. Since it can no longer
raise, `main()`'s existing control flow naturally proceeds to
`call_provider`, which already fails closed (branches 1/2 above) and returns
a sanitized `FAIL` result; `render_receipt` then runs and `main()` returns a
non-zero exit code — a clean sanitized failure outcome, not a traceback.

`tests/integration/test_message_admission_live_evidence_runner.py` gained:
`test_safe_endpoint_description_fails_closed_on_malformed_ipv6` (direct
unit-level call proving no leak) and
`test_main_facade_never_leaks_sentinel_for_malformed_configured_endpoint`
(facade-level: drives the real `runner.main()` — not a direct
support-module call — with a malformed IPv6 `DASHSCOPE_BASE_URL` containing
a sentinel and a fake `select_model`, asserting a non-zero return with the
sentinel absent from `capsys`'s `out`, `err`, and the rendered receipt file).
The existing parametrized `test_call_provider_endpoint_parse_failure_returns_sanitized_failure`
(numeric out-of-range port, non-numeric secret-bearing port, malformed
IPv6) and `test_clean_endpoint_strips_userinfo_query_and_fragment` (loosened
to a subset check for the `parts.netloc` defense-in-depth fragment) remain
from the prior round, unchanged.

### `MAR-BUILD-REV-F3 REFUSAL_AUDIT_FALSE_PASS` — closed

`scripts/run_message_admission_live_governance_evidence.py::check_message_admission_refusal_gate`
previously only checked `res.status_code == expected and ledger.messages ==
{}` — never inspecting the audit log. A reviewer adversarial probe injected
seven refusal audits and all seven cases still reported PASS. The gate now
snapshots `len(ledger.messages)` and `len(ledger._audit.all())`
**immediately after test setup** (setup's own legitimate `shift.create`
audit must not be misread as a leak — this was the first bug found while
implementing the fix, caught by rerunning the dry-run and seeing 6/7 cases
flip to FAIL) and requires both counts to be unchanged after the request. A
new negative test
(`test_refusal_gate_detects_an_injected_refusal_audit`) monkeypatches
`_with_ledger` to append one audit after every case and proves all seven
cases now report FAIL.

### `MAR-BUILD-REV-F4 ROLLBACK_AND_POSTGRES_ASSERTION_GAPS` — closed

- `tests/cvf/test_message_admission.py`'s InMemory/SQLite audit-failure
  tests now assert exact unchanged state after the exception (`ledger.messages
  == {}` and no `message.create` audit action for InMemory; zero matching
  rows in `messages`/`audit_records` for SQLite), not just that the
  exception was raised.
- `tests/integration/test_message_postgres_live.py`:
  - `test_create_persists_message_and_actor_bound_audit` and
    `test_message_and_audit_survive_reconnect` now verify every exact R6
    audit field (`actor_id`, `actor_role`, `action`, `target_type`,
    `target_id`, `control_chain`, `before_state`, `after_state`) via a
    shared `_assert_exact_r6_audit` helper, not just `action`/`actor_id`.
  - `test_frozen_shift_refusal_leaves_no_partial_rows` now asserts zero new
    message rows for the shift and an unchanged `message.create` audit
    count (delta-based — `audit_records` has no `shift_id` column and this
    live database is cumulative across the whole PostgreSQL test session,
    so a global post-hoc count would false-fail on unrelated messages
    already created by earlier tests in the same run; this was the second
    bug found and fixed, caught by the fresh live PostgreSQL rerun), plus
    connection usability.
  - `test_duplicate_message_id_refusal_leaves_no_partial_rows` — the
    Amendment 2 round asserted exactly the original row remains
    (`message_id`, `text_content`) and the connection is usable after the
    refusal, but never asserted the `message.create` audit count, so a
    hypothetical extra-audit-on-refusal bug in this exact case would have
    passed silently. This round adds the same delta-based audit-count
    snapshot pattern used in `test_frozen_shift_refusal_leaves_no_partial_rows`:
    `audits_before` snapshotted immediately before the duplicate
    `add_message` attempt, `audits_after` after, asserting
    `len(audits_after) == len(audits_before)`.

### `MAR-BUILD-REV-F5 RECEIPT_AND_CATALOG_TRUTH_DRIFT` — closed

- This receipt replaces the prior one in full, including its now-superseded
  F2 closure claim (branch 3 above). No content is inherited unverified.
- `docs/catalog/MODULE_REGISTRY.json`/`MODULE_CATALOG.md` were not touched
  this round either — no new files, module descriptions, or test-path lists
  changed; `--check` reconfirms PASS unchanged (§5).
- The prior live-evidence receipt was regenerated fresh this round by a real
  (non-dry-run) invocation after the F2-branch-3 fix, so its content
  reflects the fully fixed sanitization code end-to-end.

## 3. Final changed set (30 authorized paths, no 31st)

No Amendment 3 was required; this round stayed entirely within the existing
30-path ceiling. This round's edits, both within already-authorized paths:

- `scripts/_message_admission_live_evidence_support.py` — F2 branch 3 (this
  round: `safe_endpoint_description` now catches `ValueError` internally and
  returns `"<unparseable-endpoint>"` instead of raising).
- `tests/integration/test_message_admission_live_evidence_runner.py` — F2
  branch 3 (this round: added
  `test_safe_endpoint_description_fails_closed_on_malformed_ipv6` and
  `test_main_facade_never_leaks_sentinel_for_malformed_configured_endpoint`;
  merged the two `call_provider` sanitize-failure tests into one
  parametrized test, and folded `test_render_receipt_end_to_end_never_leaks_sentinel_from_a_failing_call`
  into a synthetic-result form, both to stay within the 300-line file-size
  guard while adding the two new tests).
- `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_BUILD_EVIDENCE_RECEIPT.md`,
  `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_LIVE_EVIDENCE_RECEIPT.md` —
  F5 (this round: truthful update / fresh regeneration).
- `tests/integration/test_message_postgres_live.py` — untouched this round;
  F4's prior-round fix stands unchanged, evidence retained truthfully (§6).

All other paths from the 30-path ceiling remain as established in prior
rounds (see Work Order Amendment 2 §2 for the full list).

`git status --porcelain` at the end of this round shows exactly 30 paths.
No 31st path was touched, staged, or committed.

## 4. Focused verification (this round)

```text
python -m pytest -q tests/integration/test_message_admission_live_evidence_runner.py tests/integration/test_message_postgres_live.py tests/cvf/test_message_admission.py tests/unit/test_message_openapi_contract.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/integration/test_message_sqlite.py
-> 82 passed, 7 skipped (the 7 skips are the opt-in PostgreSQL suite,
   correctly skipping without LIVE_POSTGRES_DATABASE_URL)
```

`test_message_admission_live_evidence_runner.py` now has 23 tests (net +2
over the prior round's 21: two new tests added, two merged into one to stay
within the 300-line file-size guard); `test_message_postgres_live.py`
remains 7 tests, unchanged this round.

## 5. Full non-live suite and repository gates

```text
python -m pytest -q
-> 789 passed, 76 skipped, 0 failed
```

**Zero failures**, two more passes than the prior round's 787 (net +2 new
tests in the runner test file), same 76 skips (opt-in PostgreSQL/live
suites), same zero failures.

```text
python scripts/testing/validate_repository.py
-> repository validation passed (catalog + session state + file-size checks)

python scripts/generate_catalog.py --check -> CATALOG VERIFY: PASS (20 modules)
python scripts/check_session_state.py     -> SESSION STATE: PASS
python scripts/check_file_size.py         -> FILE SIZE GUARD: PASS
git diff --check                          -> exit 0 (only non-failing
                                              Windows LF/CRLF warnings)
```

Every touched/new Python file is at or below the 300-line hard limit (see
§3 for the full list; the tightest are exactly 300:
`tests/cvf/test_message_admission.py`,
`tests/integration/test_message_admission_live_evidence_runner.py`).

Protected boundary: zero diff confirmed for
`database/migrations/**`, `packages/operations-domain/**`,
`packages/workspace-contracts/**`, `apps/integration-edge/**`,
`packages/channel-sdk/**`, `packages/channel-adapters/**`,
`packages/identity-mapping/**`, `packages/conversation-routing/**`,
auth/JWT/token implementation, frontend, dependency manifests/locks.

## 6. Disposable PostgreSQL 16 evidence (retained truthfully, not rerun)

No PostgreSQL-related file was touched this round (§3 confirms
`tests/integration/test_message_postgres_live.py` was not modified). Per
the required order, PostgreSQL evidence need not change unless its files
are modified, so the prior round's already-fresh passing evidence stands
as-is:

`python scripts/run_postgres_live_roundtrip.py --json` (prior round):

- `docker_server_version`: 29.6.2; `image`: `postgres:16-alpine`.
- Migrations: first attempt **21 applied / 0 skipped**; reapply
  **17 applied / 4 skipped** (idempotent).
- Live suite: **66 passed, 0 failed**, including the F4-strengthened
  `test_duplicate_message_id_refusal_leaves_no_partial_rows`.
- Cleanup: `container_absent_after_cleanup: true`,
  `anonymous_volumes_still_present: []` — zero `cvf-pg-live-*` residue.

## 7. Real provider-bound message-admission governance evidence (fresh)

`python scripts/run_message_admission_live_governance_evidence.py --dry-run`
first (sanity check: all 7 refusals PASS at 0 calls, genuine admitted create
construction PASS, provider credential present), then the real invocation:

- 7 refusal cases (anonymous, malformed token, viewer role, sender
  mismatch, non-INTERNAL source, unknown shift, frozen shift) — all
  **PASS**, **0 provider calls each**, through the real HTTP/JWT route
  chain, with the repaired F3 audit-delta check confirming zero new
  message AND audit writes for every case.
- Genuine operator-JWT create (minted token, real HTTP request) — **PASS**,
  verified against the exact-field-matched assertion set (mirrors the
  predecessor shift-create tranche's SCR-BUILD-REV-F2 repair): exactly one
  persisted message matching the created id, and every audit field exactly
  matching the expected values.
- Real provider call: **exactly 1**, outcome **PASS**, HTTP 200, model
  `qwen3.7-max`, endpoint (host only)
  `https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com`.
- Fresh sanitized receipt:
  `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_LIVE_EVIDENCE_RECEIPT.md` —
  grepped for `Bearer`, `sk-`, `eyJ`, `api_key`, `Authorization:` and full
  endpoint path/query — none found. Regenerated fresh this round after the
  F2-branch-3 fix; no output from before this round was reused.
- Production `POST /messages` does not import or invoke any provider-facing
  code from either evidence script; the provider call is external release
  evidence only.

## 8. Secret and resource discipline

No provider API key, JWT signing secret, bearer token, PostgreSQL password,
or full database URL was printed, read back, or committed at any point in
this round. The live-evidence script resets a fresh `ProviderCallCounter`
per invocation. No new Docker/PostgreSQL activity occurred this round (§6);
the prior round's cleanup evidence stands as recorded there.

## 9. Statement

No stage, commit, or push occurred at any point during this round. No
self-approval, FREEZE, or next-tranche (external Integration Edge) work was
performed. No Amendment 3 was required. Exactly the 30 authorized paths
were touched or created (across all rounds combined); no 31st path.
Migrations, `packages/operations-domain/**`, `apps/integration-edge/**`,
`packages/channel-sdk/**`, `packages/channel-adapters/**`,
`packages/identity-mapping/**`, `packages/conversation-routing/**`,
`packages/workspace-contracts/**`, auth/JWT/token implementation, frontend,
dependency manifests/lockfiles, and the file-size guard/debt registry were
not touched.

`READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_FINAL_REVIEW`

## 10. Claim boundary (SPEC R19, unchanged)

Only the following is claimed:

> Internal `POST /messages` requires a verified JWT, derives sender/source
> authority server-side, enforces `message.create`, and atomically persists
> a shift-bound internal Message with an actor-bound audit record on the
> proven backends.

Not claimed: external/channel message ingestion is implemented or durable;
the Canonical Message Contract is implemented by operations-domain;
signature verification, raw-envelope persistence, replay, identity mapping,
fallback, quarantine, or attachment handling is end-to-end; all mutation
routes are authenticated; tenant/assignment/`data_scope` authorization;
message content is confirmed operational truth; PostgreSQL production
readiness; or P2-C/P4-C/P4-E/Phase 2/4 completion.
