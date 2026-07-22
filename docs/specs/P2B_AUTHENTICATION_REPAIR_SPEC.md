# SPEC: P2-B Authentication Repair

- Tranche: P2B-AUTHENTICATION-REPAIR
- Control-chain phase: SPEC (follows `docs/decisions/ADR_2026-07-22_P2B_AUTHENTICATION_REPAIR.md`)
- Risk: R2
- Author role: SPEC_AUTHOR (transitioned from ORCHESTRATOR, 2026-07-22)
- Precedes: `docs/work_orders/P2B_AUTHENTICATION_REPAIR_WORK_ORDER.md`

## 0. Current implementation truth vs. desired behavior (read this first)

This SPEC repairs commit `cd36b27`, which already exists on `main`. Every
requirement below is phrased as **desired behavior after repair**. Where
current behavior differs, it is stated explicitly as **CURRENT** so the two
are never conflated.

| Area | CURRENT (cd36b27, as of this SPEC) | DESIRED (after this tranche) |
|---|---|---|
| `jwt_secret_key` | Any non-empty string accepted, including `"x"` | Rejected unless ≥32 UTF-8 bytes, not blank, not on the placeholder denylist |
| `LoginInput.password` | Unbounded `str`; >72 UTF-8 bytes crashes bcrypt (uncaught 500) | Rejected at the request boundary (422) if >72 UTF-8 bytes, for any username |
| Migration `003_users.sql` on an existing Postgres volume | Never applied (initdb.d is first-init-only); no runner/runbook exists | A documented, idempotent runner/runbook applies it; a static test guards the idempotency property that makes this safe |
| `cvf_runtime/identity.py` docstring | Says "header-based principal, not full authentication" | Describes the current JWT-bearer-token mechanism accurately |
| `CVF_CONTROL_MAPPING.md` identity row | Cites 4 login tests | Cites the actual current test count |
| `CVF_CONTROL_MAPPING.md` permission row | Says permission depends on identity that is "chưa xác thực" (not yet authenticated) | Reflects that identity is JWT-verified, while still not claiming an approved/load-bearing governance disposition beyond what REVIEW+live-evidence establish |
| Governance disposition of `identity`/P2-B | REVIEW_CHANGES_REQUIRED — UNAUTHORIZED BUILD CANDIDATE (per INTAKE of this tranche) | Unchanged by this SPEC alone — disposition upgrades only after this tranche's REVIEW passes AND live Alibaba evidence passes (see §7) |

## 1. Intended behavior

1.1. The application must refuse to start (fail closed, at `Settings`
construction time, before serving any request) if `JWT_SECRET_KEY` is
missing, blank, shorter than 32 UTF-8 bytes, or exactly matches a value on
the placeholder denylist (§3).

1.2. `POST /auth/login` must reject (422) any request whose `password`
field exceeds 72 UTF-8 bytes, before the request reaches the database
lookup or any `bcrypt` call, for both existing and non-existing usernames.

1.3. A documented, idempotent path must exist to apply
`database/migrations/003_users.sql` to an already-running PostgreSQL
database that only has migrations 001 and 002 applied (i.e. a pre-existing
`postgres_data` volume from before this tranche).

1.4. `cvf_runtime/identity.py`, `docs/cvf/CVF_CONTROL_MAPPING.md` (identity
row test count, permission row wording), and any other surface named in
`docs/decisions/ADR_2026-07-22_P2B_AUTHENTICATION_REPAIR.md`'s T4 finding
must describe the current JWT mechanism accurately, without claiming an
approved/load-bearing governance disposition this SPEC does not itself
grant.

1.5. A standalone, sanitized-evidence-producing script must exist that (a)
exercises the real identity gate in-process with a valid and an
invalid/forged token, and (b) — only after (a)'s valid-token case succeeds
— makes one real, minimal Alibaba API call via the parallel
`PROVIDER-ALIBABA-LIVE-CONFIG` tranche's selector, recording a sanitized
receipt. This script's successful run, with a real Alibaba response
recorded, is the live-evidence artifact required before any
REVIEW_PASS/FREEZE/DONE claim for this tranche.

## 2. Non-goals (explicit scope boundaries — do not silently expand)

This tranche does not:

- Reconcile `known-principals.yaml` with the `users` table, or otherwise
  touch approval quorum / High Finding #4.
- Add refresh tokens, token revocation, self-service registration, password
  reset, or login rate limiting.
- Build a production admin user-provisioning flow (`scripts/seed_dev_users.py`
  remains dev/test-only).
- Perform or claim PostgreSQL production/live-round-trip verification
  beyond the static idempotency-guard test in §5.
- Add runtime callers for `data_scope`/`cost`/`termination`, or implement
  refusal routing/recording.
- Implement the Phase 4 AI Gateway, or any production HTTP endpoint that
  wraps an AI provider call. The live-evidence script in §7 is a
  standalone script, not a new router/endpoint.
- Modify, re-implement, or take ownership of the parallel
  `WO-PROVIDER-ALIBABA-LIVE-CONFIG-2026-07-22` tranche's authorized changed
  set (`packages/ai-providers/alibaba/*`, its own ADR/SPEC/WORK_ORDER). This
  tranche only *consumes* that tranche's output (the `ALIBABA_API_KEY`
  environment variable and `select_model.py`) once it is committed.
- Rewrite, squash, amend, or force-push `cd36b27`.

## 3. Security invariants

- SI-1: No governed action may ever resolve a `Principal` from anything
  other than a signature-and-expiry-verified JWT claim. (Already true after
  `cd36b27`; this tranche must not regress it.)
- SI-2: `jwt_secret_key` must never appear in logs, error messages,
  exceptions, or test output — including validation-failure messages.
- SI-3: The Alibaba API key must never be committed, logged, echoed in
  command output, or written to any evidence artifact this tranche
  produces. Only `ALIBABA_API_KEY`'s *presence* (boolean) may be checked
  and reported.
- SI-4: The password-length rejection (§1.2) must not reintroduce a timing
  or response-shape side-channel distinguishing an existing username from
  an unknown one — the 422 path must be identical (status, body, and
  control flow up to the point of rejection) regardless of username.
- SI-5: The JWT-secret denylist (§4) must not include this repository's own
  test-only secret (`conftest.py`'s `"test-only-secret-do-not-use-in-production"`)
  — the denylist and the test fixture must not collide, or the test suite
  itself would fail to boot.

## 4. API / configuration contracts

### 4.1 `Settings.jwt_secret_key` (config.py)

```
Input: JWT_SECRET_KEY environment variable (str)
Validation, in order:
  1. Reject if empty or whitespace-only.
  2. Reject if len(value.encode("utf-8")) < 32.
  3. Reject if value is exactly one of the denylist entries (exact match,
     case-sensitive): {"replace-me-with-a-real-secret", "changeme",
     "change-me", "secret", "password"}.
Failure mode: raise at Settings construction (pydantic ValidationError),
before the app can serve any request. Error message must not include the
rejected value.
```

### 4.2 `LoginInput.password` (auth/router.py)

```
Input: JSON body field "password" (str)
Validation: reject if len(password.encode("utf-8")) > 72.
Failure mode: HTTP 422 (FastAPI/Pydantic request-validation error), before
the route handler body runs — i.e. before ledger lookup or any bcrypt call.
Applies identically whether "username" identifies an existing user or not.
```

## 5. Migration / upgrade contract

```
Given: a PostgreSQL database with migrations 001_foundation.sql and
       002_tasks_customers_reports.sql already applied (pre-existing
       postgres_data volume, predating 003_users.sql).
When:  003_users.sql (or the full 001+002+003 sequence) is (re-)applied
       via the documented runbook/runner.
Then:  the users table exists; no error occurs; re-running the same
       apply step again is a no-op (idempotent).
```

Static guard (portable, no live Postgres required): every `CREATE TABLE`
statement across `database/migrations/*.sql` must be of the form
`CREATE TABLE IF NOT EXISTS` — this is the structural property the
idempotency claim rests on. A test must assert this over all three current
migration files and fail if a future migration drops the guard.

**Explicitly not claimed:** a live execution of this contract against a
running PostgreSQL instance. No Docker/Postgres is available in this
environment (standing project-wide limitation). The runbook/script must be
written to be correct for real use, but its live execution remains a
pre-ship gate, stated as such wherever this tranche's status is recorded.

## 6. Testable acceptance criteria

- AC-1 (T1 positive): `Settings(jwt_secret_key=<32+ random bytes, not on
  denylist>)` constructs successfully.
- AC-2 (T1 negative — blank): `Settings(jwt_secret_key="")` raises.
- AC-3 (T1 negative — too short): `Settings(jwt_secret_key="short")`
  raises.
- AC-4 (T1 negative — placeholder): `Settings(jwt_secret_key="replace-me-with-a-real-secret")`
  and `Settings(jwt_secret_key="changeme")` both raise.
- AC-5 (T1 — no secret leakage): the exception raised by AC-2/AC-3/AC-4
  does not contain the rejected value in its string representation.
- AC-6 (T2 positive — existing login still works): a login with a
  password ≤72 UTF-8 bytes for a real seeded user still returns 200 with a
  usable token (regression guard — this repair must not break the
  legitimate path).
- AC-7 (T2 negative — ASCII >72 bytes, existing username): login with a
  73-byte ASCII password for an existing username returns 422, not 500.
- AC-8 (T2 negative — ASCII >72 bytes, unknown username): same as AC-7 but
  for a username that does not exist — also 422, not 500.
- AC-9 (T2 negative — multibyte >72 bytes): a password with fewer than 72
  *characters* but more than 72 UTF-8 *bytes* (e.g. multibyte characters)
  returns 422, not 200/500.
- AC-10 (T2 — timing/shape invariant, SI-4): AC-7 and AC-8's responses have
  identical status code and body shape (differing only in whatever is
  username-independent) — proves the length check does not leak username
  existence.
- AC-11 (T3 — static idempotency guard): every `CREATE TABLE` statement in
  every file under `database/migrations/*.sql` is `CREATE TABLE IF NOT
  EXISTS` — this test must fail if run against a synthetic migration file
  lacking the guard (negative-tested, matching this project's established
  practice of proving a check actually catches drift, not just that it
  passes today).
- AC-12 (T4 — doc accuracy): `docs/cvf/CVF_CONTROL_MAPPING.md`'s identity
  row cites the actual current login-test count (verified by counting test
  functions in `tests/cvf/test_auth_login.py` at repair time, not
  hand-typed); `cvf_runtime/identity.py`'s docstring no longer claims
  header-based/non-authenticated identity.
- AC-13 (full regression): `python -m pytest -q`,
  `python scripts/testing/validate_repository.py`,
  `python scripts/check_session_state.py`, and
  `python scripts/generate_catalog.py --check` all pass after the repair.
- AC-14 (live evidence, gates disposition only — see §7): the live-evidence
  script (§1.5) runs successfully end-to-end at least once, with a real
  (non-mocked) Alibaba response recorded in a sanitized receipt, before any
  REVIEW_PASS/FREEZE/DONE/"identity load-bearing" claim is written anywhere.

## 7. Live-evidence requirement (Mandatory Governance Proof)

Per `AGENTS.md`, any claim that `identity` (a CVF-governed control) is
load-bearing requires a real provider API call, not a mock or a
`TestClient`-only probe. This SPEC requires:

1. The evidence script described in §1.5 exists and is runnable.
2. It depends on `ALIBABA_API_KEY` being present in the environment and on
   the separate `PROVIDER-ALIBABA-LIVE-CONFIG` tranche being committed —
   this SPEC does not authorize re-implementing that tranche's scope.
3. Until the script has been run successfully with a real Alibaba response
   recorded, this tranche's disposition may only be recorded as
   `READY_FOR_LIVE_EVIDENCE` (once §1.1-§1.4 and REVIEW otherwise pass) —
   never `REVIEW_PASS`, `FREEZE`, `DONE`, or "identity load-bearing".
4. If the live call fails (auth, quota, model-not-found, or any other
   error), the tranche remains open at its current disposition; the
   failure is recorded plainly, not reframed as success.
5. The evidence artifact contains: timestamp, provider name, model used,
   HTTP outcome, a truncated response excerpt. It never contains the raw
   API key or an `Authorization` header value.

## 8. Documentation / continuity requirements

On completion of BUILD + REVIEW + live evidence (not before), the following
must be brought into agreement — this SPEC does not authorize doing so
prematurely:

- `docs/cvf/CVF_CONTROL_MAPPING.md` (identity row status/test-count,
  permission row wording)
- `docs/catalog/MODULE_REGISTRY.json` + regenerated `MODULE_CATALOG.md`
- `docs/implementation/EXECUTION_ROADMAP.md`
- `IMPLEMENTATION_STATUS.json`
- `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json` (drift-checked via
  `scripts/check_session_state.py`)
- A closing handoff under `SESSION/handoffs/`

None of these may claim DONE/load-bearing/FREEZE until §7's live evidence
and an independent REVIEW both pass.
