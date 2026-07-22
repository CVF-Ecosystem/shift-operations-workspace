# ADR: P2-B real authentication — JWT bearer tokens replace header-trusting identity

- Status: Accepted
- Decision owner: session agent (Claude), operator-selected lane per `SESSION/ACTIVE_SESSION_STATE.json` `next_allowed_move` (2026-07-22)
- Affected phase/modules: Phase 2 (P2-B), `apps/workspace-api` (new `auth/` module, `dependencies.py`, `config.py`), `packages/operations-ledger` (new `users` table/methods), `database/migrations/003_users.sql`

## Context

`dependencies.py::get_principal` built a `Principal` (user_id + role) directly
from client-supplied `X-User-Id`/`X-User-Role` HTTP headers, with no
verification at all. Any caller could claim any role, including
`authorized_executive`. This was tracked as the `identity` CVF control's
status: **not verified server-side** (`docs/cvf/CVF_CONTROL_MAPPING.md`), a
shared limitation across all five governed verticals (Event/Correction/Task/
Shift/CustomerRequest). The roadmap (`docs/implementation/EXECUTION_ROADMAP.md`,
P2-B) calls for replacing this with real authentication. The operator selected
this lane over P2-A(remaining: incidents/handovers) and P2-C(frontend UI)
after `next_allowed_move` allowed opening any one of the three.

## Decision

Issue short-lived, signed JWT access tokens (HS256) via a new
`POST /auth/login` endpoint, backed by a new `users` table (bcrypt-hashed
passwords). `get_principal` now requires a valid `Authorization: Bearer`
token, decodes it via `workspace_api/auth/tokens.py`, and constructs
`Principal` only from the verified `sub`/`role` claims — never from a
client-supplied header. Every router keeps
`principal: Principal = Depends(get_principal)` unchanged; only
`get_principal`'s implementation changed, so the blast radius is contained to
`dependencies.py`, the new `auth/` module, `config.py`, and persistence
additions.

`JWT_SECRET_KEY` has no default in `Settings` — the app fails closed at
startup without one, rather than repeating the `WEBHOOK_SHARED_SECRET`
"replace-me" fallback the EA review flagged as unsafe.

## Alternatives considered

- **Server-side sessions (cookie + session store):** rejected. This repo has
  no existing session-store infrastructure, and
  `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md` requires all cross-boundary
  state to cross as plain HTTP (`VITE_API_URL`) with governance enforced
  entirely backend-side — a stateless bearer token fits that contract with the
  least new infrastructure. Sessions would also need CSRF handling that
  bearer tokens in an `Authorization` header do not.
- **`passlib`/`argon2-cffi` for password hashing:** rejected in favor of
  `bcrypt` directly — `passlib` is effectively unmaintained, and `bcrypt` ships
  maintained prebuilt wheels on every platform this repo targets, including
  Windows dev machines, for the simple `hashpw`/`checkpw` API this module
  needs.
- **Reconciling `known-principals.yaml` with the new `users` table in the same
  tranche:** rejected — kept as a separate, still-open follow-up. The EA
  review already treats approval-fabrication (High Finding #4) as distinct
  from identity; folding it in here would have widened this tranche's blast
  radius and mixed two different governance surfaces (who you are vs. who may
  approve a given quorum seat) in one change.

## Consequences

- `identity` moves from **not verified server-side** to **load-bearing** in
  `docs/cvf/CVF_CONTROL_MAPPING.md`.
- Every existing HTTP-level test that authenticated via literal
  `X-User-Id`/`X-User-Role` headers (`tests/cvf/test_shift_close_governance.py`,
  `tests/cvf/test_customer_request_vertical.py`,
  `tests/cvf/test_customer_request_repair.py`) now mints a real signed token
  via a shared test helper (`tests/cvf/_auth_test_helpers.py`) instead.
- User provisioning has no admin flow yet — `scripts/seed_dev_users.py` is
  dev/test-only, documented as such, and reuses `known-principals.yaml`'s ids
  purely for fixture legibility (the two registries remain independent
  stores).
- No refresh tokens or revocation: an issued access token is valid for its
  full TTL (`JWT_ACCESS_TOKEN_TTL_MINUTES`, default 60) and cannot be
  invalidated early. Acceptable for this tranche's scope; a follow-up if a
  real incident-response need for token revocation emerges.

## Security/data/CVF impact

- Removes the ability for any caller to self-assert a role via headers — the
  original vulnerability class this ADR closes.
- Passwords are bcrypt-hashed, never stored or logged in plaintext.
- `decode_access_token` pins `algorithms=["HS256"]` explicitly, so a forged
  token claiming `alg: none` (a classic JWT bypass) or claiming a role outside
  `cvf_runtime.identity.KNOWN_ROLES` is rejected, not silently accepted (see
  `tests/cvf/test_auth_tokens.py`).
- Login failure responses (unknown username, wrong password, inactive
  account) are identical to avoid username enumeration
  (`tests/cvf/test_auth_login.py::test_unknown_username_is_401_with_same_message_as_wrong_password`).
  **Found by independent review (2026-07-22) and fixed in this same tranche:**
  the response body/status were identical, but `verify_password` (bcrypt) was
  skipped entirely when the username didn't exist (Python's `or`
  short-circuit), making that response ~18x faster than a wrong-password
  response - a timing side-channel that still enumerates valid usernames.
  Fixed by always running `verify_password` against a precomputed
  `DUMMY_PASSWORD_HASH` (`workspace_api/auth/passwords.py`) when no user is
  found, so the bcrypt cost is paid on every path regardless of whether the
  username exists. Test:
  `tests/cvf/test_auth_login.py::test_unknown_username_still_runs_password_verification`
  (spy-based, not wall-clock timing, to stay CI-reliable).
- Does **not** address High Finding #4 (approval quorum accepts any
  `known-principals.yaml`-registered id/role, itself not tied to a real
  session) — that remains open and is explicitly called out as unaffected
  wherever this tranche touches `docs/cvf/CVF_CONTROL_MAPPING.md`.
- `known_remaining_defects` still open after this tranche: no refresh/
  revocation; user provisioning is seed-script-only, not a real admin flow;
  `known-principals.yaml` reconciliation with `users` is unaddressed;
  identity's move to load-bearing does not itself change `data_scope`/`cost`/
  `termination` (still no runtime caller) or refusal routing (still not
  implemented).

## Migration and rollback

- New migration `database/migrations/003_users.sql` (additive: one new
  `users` table, no changes to existing tables). Rollback is a `DROP TABLE
  users` plus reverting the `tables.py`/`Ledger` Protocol additions and the
  `get_principal` change back to header-based — no destructive change to
  existing data.
- `JWT_SECRET_KEY` must be set in every environment running `workspace-api`
  from this commit forward (dev, test, CI, prod); `.env.example` documents it.
  The root `conftest.py` sets a test-only default so the test suite does not
  require a local `.env`.

## Evidence

- `tests/cvf/test_auth_tokens.py` (8 tests): round-trip, tampered signature,
  expiry, wrong signing key, malformed token, `alg: none`, unknown role
  claim, TTL sourced from settings.
- `tests/cvf/test_auth_login.py` (5 tests): valid login, wrong password,
  unknown username (same response as wrong password), inactive user, and
  (added after independent review) unknown-username still runs password
  verification against the dummy hash.
- `tests/cvf/test_shift_close_governance.py::test_old_header_impersonation_no_longer_grants_any_identity`:
  regression proof that claiming `authorized_executive` via the old headers
  alone, with no bearer token, is still refused with 401.
- `tests/integration/test_schema_parity_users.py`: two-directional
  verification that the migration's `users.role` CHECK matches
  `cvf_runtime.identity.KNOWN_ROLES` exactly.
- Manual HTTP smoke test (login → bearer token → `POST /shifts/{id}/close`
  succeeds; same call with only the old headers → 401; tampered token → 401).
- Full suite: `python -m pytest -q` and
  `python scripts/testing/validate_repository.py` both pass at tranche close
  (171 tests).
- Independent review (fresh agent context, no memory of this implementation,
  per `AGENTS.md`'s REVIEWER-independent-from-IMPLEMENTATION_WORKER rule for
  R2+ changes): ran its own standalone probes (old-header impersonation,
  `alg: none`, wrong signing key, expired token, forged unknown-role claim,
  real login round-trip) against a live `TestClient`, independently
  confirmed no bypass in any of those vectors, confirmed `jwt_secret_key` has
  no default, confirmed every governed router endpoint still depends on
  `get_principal` unchanged, and confirmed `known-principals.yaml`/
  `approval.py` were not touched. It found the login timing side-channel
  documented above, which was fixed in this same tranche before commit.
