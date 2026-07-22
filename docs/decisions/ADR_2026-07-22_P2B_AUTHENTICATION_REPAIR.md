# ADR: P2-B authentication repair — corrective control-chain tranche

- Status: Proposed (DESIGN phase output; not yet SPEC, WORK_ORDER, or approved)
- Risk: R2 — changes the authentication/security boundary and the `identity` CVF control
- Decision owner: operator-directed corrective tranche, 2026-07-22
- Tranche: P2B-AUTHENTICATION-REPAIR
- Supersedes in disposition only (not in text): `docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md` remains as historical record of commit `cd36b27`'s own stated rationale. This ADR does not rewrite that file.

## Context

Commit `cd36b27` ("P2-B: real authentication") replaced this project's
header-trusting `get_principal` dependency with a JWT-bearer-token
mechanism, added a `users` table, `POST /auth/login`, and a fresh-context
agent's functional review. All of that — ADR, implementation, tests, review
claim, and closure — landed in a single commit, in a single continuous
session, with no recorded DESIGN artifact independent of the ADR embedded in
that same commit, no discrete testable SPEC, no operator-approved
WORK_ORDER preceding BUILD, and no recorded role transitions (`AGENTS.md`'s
seven-step control chain: `INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD ->
REVIEW -> FREEZE`). The "independent review" that ran inside that same
session used FastAPI `TestClient` and local mocks only — real for what it
tested, but not a live provider call, so it does not satisfy this project's
Mandatory Governance Proof rule (`AGENTS.md`) for a claim that a CVF control
(`identity`) is load-bearing.

This ADR is the DESIGN step of a corrective tranche that runs `cd36b27`'s
changes back through the control chain properly. Per the operator's
instruction, this design **independently evaluates the existing
implementation** rather than assuming `cd36b27`'s code is correct-as-is or
that its own ADR's claims are settled fact.

## Independent evaluation of the existing implementation (not assumed correct)

Re-reading and re-probing `cd36b27`'s code directly (not reusing the prior
session's own test suite as the source of truth) found:

- **Confirmed correct, by direct re-probe:** `get_principal`
  (`dependencies.py`) no longer accepts `X-User-Id`/`X-User-Role` headers as
  identity; `decode_access_token` pins `algorithms=["HS256"]`, rejecting an
  `alg: none` forged token; a token signed with a different secret is
  rejected; an expired token is rejected; a role outside
  `cvf_runtime.identity.KNOWN_ROLES` is rejected at decode time because
  `Principal`'s own validator runs; the login-timing side-channel fix
  (`DUMMY_PASSWORD_HASH`) does run `verify_password` unconditionally. These
  match what `cd36b27`'s own review claimed, independently re-verified here,
  not merely re-cited.
- **Confirmed broken, by direct re-probe (T1):** `Settings.jwt_secret_key:
  str` in `config.py` has no strength validation.
  `Settings(jwt_secret_key="x")` constructs without error, and a token
  forged with the guessed one-character secret `"x"` decodes successfully
  and grants `role="authorized_executive"` — reproduced directly, not
  assumed from the finding text.
- **Confirmed broken, by direct re-probe (T2):** `LoginInput.password: str`
  has no length bound. `bcrypt.hashpw`/`bcrypt.checkpw` on bcrypt 5.0.0
  raise `ValueError` for inputs over 72 UTF-8 bytes. A live `TestClient`
  call to `POST /auth/login` with a 73-byte password returns an uncaught
  HTTP 500 for **both** an existing username and an unknown username (the
  latter because the login-timing fix's `DUMMY_PASSWORD_HASH` comparison
  also calls `bcrypt.checkpw` with the same over-length password) —
  reproduced directly against a live `TestClient`, not assumed.
- **Confirmed by direct reading (T3):** `docker-compose.yml` mounts
  `./database/migrations:/docker-entrypoint-initdb.d:ro`. PostgreSQL only
  executes files under that mount point when the data directory is
  initialized for the first time. An existing `postgres_data` volume
  created before `003_users.sql` existed will never pick it up
  automatically; there is no migration-runner or upgrade tooling in this
  repository today (`scripts/` has no such script).
- **Confirmed by direct reading (T4):** `cvf_runtime/identity.py`'s
  docstring still reads "This is a header-based principal, not full
  authentication" — now false for how `workspace_api` actually resolves a
  `Principal`, though the module's own `Principal`/`KNOWN_ROLES` code is
  unaffected. `docs/cvf/CVF_CONTROL_MAPPING.md`'s identity row cites 4 login
  tests where 5 exist. Its permission row still says permission "phụ thuộc
  identity chưa xác thực ở trên" (depends on identity not yet
  authenticated), which is now inaccurate given the identity row's own
  claimed fix.

None of T1-T4 are novel design opinions; they are reproducible defects,
verified directly in this DESIGN pass.

## Process failure analysis (G1, G2)

The seven-step chain exists specifically so that a SPEC (discrete, testable
requirements, separated from current-implementation truth) and a WORK_ORDER
(bounded changed set, explicit stop conditions, independent reviewer
requirement, evidence plan) exist **before** code is written — not so that
they can be reconstructed after the fact from a finished commit. Writing an
ADR in the same commit as the implementation, tests, and closure claim
collapses DESIGN into BUILD and removes the only point in the chain where a
second party (or a deliberately independent later pass) could have caught
T1-T3 before merge. That an independent-context review pass *did* happen
inside that commit and *did* catch one real defect (the timing
side-channel) shows the review step has value — it does not retroactively
constitute a SPEC or WORK_ORDER, and it explains why T1-T3 were still
missed: the review's own probe list was whatever the implementing session
thought to ask for, not a requirement set written independently beforehand.

This ADR does not propose new tooling to "prevent this from happening
again" beyond following the chain properly this time — that would be scope
creep beyond an authentication repair. The repair is: do DESIGN, SPEC,
WORK_ORDER properly for the T1-T4 fixes and the live-evidence gap, in that
order, with an operator approval gate before BUILD.

## Decision

### Secret validation (T1)

Add fail-closed validation to `Settings.jwt_secret_key` at construction
time (a Pydantic `field_validator`, so the app refuses to start — not a
runtime check that only fires on first request):

- Reject an empty/blank secret.
- Require at least 32 bytes measured as `len(value.encode("utf-8"))` — byte
  length, not character count, because HMAC-SHA256 key strength is a byte
  quantity (this matches the `InsecureKeyLengthWarning` PyJWT itself already
  emits, which this project's test run already surfaces and has so far
  ignored).
- Reject a small, explicit, testable denylist of known example/placeholder
  values (starting with `.env.example`'s own
  `"replace-me-with-a-real-secret"`, plus a short list of commonly-seen
  tutorial placeholders such as `"changeme"`, `"change-me"`, `"secret"`,
  `"password"`). The denylist is exact-match, not a heuristic, and does not
  include this repo's own test-only conftest secret (a distinct, sufficiently
  long, non-placeholder-looking string) — the two must not collide, and the
  SPEC will state both values explicitly to make this checkable.
- The validator's error message must not echo the rejected value back
  (avoids logging/echoing a near-miss secret).

### Password boundary (T2)

Add a Pydantic-level constraint on `LoginInput.password` that rejects (422,
at the request-parsing boundary, before the route handler or any bcrypt
call runs) any password whose **UTF-8 byte length** exceeds 72 — not
character count, so a multibyte string under 72 characters but over 72
bytes is still rejected. Because this is a Pydantic field validator, FastAPI
rejects the request before the handler body (and therefore before
`verify_password`/`DUMMY_PASSWORD_HASH`) ever runs, for **any** username —
the 422 path is identical regardless of whether the username exists, so it
does not reopen the timing side-channel the prior tranche closed (that
side-channel was specifically about the *existing* code path skipping
`bcrypt` only for unknown usernames; a boundary-validation rejection skips
`bcrypt` for every username uniformly, which is not an oracle because it
carries no information about username existence).

### Migration upgrade path (T3)

No Docker/live PostgreSQL is available in this environment (a standing,
already-documented limitation for this entire project — see
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md` and every
schema-parity test's own module docstring). The design must therefore
produce the strongest available non-live guarantee, stated honestly as
such, not a claim of live verification that cannot be made here:

1. A documented runbook/script (`scripts/apply_migrations.py`) that applies
   `database/migrations/*.sql` files, in lexical order, against whatever
   `DATABASE_URL` is configured — usable for real against a live Postgres
   instance when the operator has one. Every migration file already uses
   `CREATE TABLE IF NOT EXISTS` exclusively (verified by reading all three
   files), which is what makes "just reapply everything in order" safe and
   non-destructive in the first place, rather than requiring a new
   migration-tracking table.
2. A **static safety-net test**, portable without Postgres: parse every
   `database/migrations/*.sql` file and assert every `CREATE TABLE`
   statement is guarded by `IF NOT EXISTS` — this is the structural property
   that makes reapplication of 001+002+003 against an existing 001+002
   database safe, and it is checkable today with the same regex-based
   parsing infrastructure `tests/integration/_schema_parity_parsing.py`
   already provides. If a future migration ever drops this guard, the test
   fails before that migration can break the upgrade story.
3. **Explicitly not claimed:** a live round-trip proving `003_users.sql`
   applies cleanly to a *running* Postgres 001+002 database. That remains a
   pre-ship gate, identical in nature to every other "PostgreSQL round-trip
   never run live" caveat already standing in this project's continuity
   files — this repair does not manufacture a false claim of having done
   that test.

### Live governance evidence strategy (G3)

`identity` is one of this project's twelve CVF-governed controls
(`cvf_control_vocabulary` in `docs/catalog/MODULE_REGISTRY.json`), so
`AGENTS.md`'s Mandatory Governance Proof rule applies to any claim that it
is load-bearing — even though JWT authentication has no intrinsic technical
dependency on an LLM provider. A generic "provider canary" (this repo's
sibling `.Controlled-Vibe-Framework-CVF/scripts/run_cvf_provider_live_canary.py`
and `run_cvf_multi_provider_live_smoke.py`) only proves an Alibaba API key
and lane work at all — it exercises the **CVF core's own** web product
(`EXTENSIONS/CVF_v1.6_AGENT_PLATFORM/cvf-web`), not this downstream
project's `identity` control, and the operator's own instruction says a
bare canary "không được coi là toàn bộ governance proof". Reusing it
unmodified as identity's proof would be a non-sequitur (an unrelated
provider responding proves nothing about JWT verification).

Design instead: a small, standalone evidence script (not a new production
HTTP endpoint — that would expand the API surface beyond an authentication
repair) that:

1. In-process, exercises the real `create_access_token`/`decode_access_token`/
   `get_principal` path with (a) a validly-signed token for a permitted
   role and (b) a forged/invalid token, asserting the identity gate
   behaves correctly for both — this is the actual control under review.
2. Only after (a) succeeds, makes exactly one real, minimal Alibaba API
   call via the parallel `PROVIDER-ALIBABA-LIVE-CONFIG` tranche's
   `packages/ai-providers/alibaba/select_model.py` and the
   `ALIBABA_API_KEY` current-user environment variable that tranche
   establishes (this repair does **not** re-implement credential handling
   or model selection — it is an authorized consumer of that separate,
   already-scoped tranche's output once it is committed).
3. Records one sanitized evidence artifact (timestamp, provider, model,
   HTTP outcome, truncated response — never the key or an `Authorization`
   header) under `docs/decisions/`.

The causal link the evidence proves: a real JWT-authenticated request path
is what gates a real, non-mocked external call in this evidence script —
satisfying "must use a real provider API call" for a governance claim about
`identity`, without fabricating a technical dependency between JWT
authentication and an LLM provider that does not otherwise exist, and
without building the Phase 4 AI Gateway this project has not reached yet.

**This evidence step has an external dependency this ADR cannot resolve
unilaterally:** it requires the separate `WO-PROVIDER-ALIBABA-LIVE-CONFIG-2026-07-22`
tranche (observed in-progress in the working tree during this DESIGN pass,
not authored by this tranche) to be committed and `ALIBABA_API_KEY` to be
present in the environment. Until then, this tranche may record only
`READY_FOR_LIVE_EVIDENCE`, never `REVIEW_PASS`/`FREEZE`/`DONE`/"identity
load-bearing".

## Alternatives considered

- **T1 — reject any secret under some length vs. a full entropy check
  (character-class diversity, dictionary check):** rejected the stronger
  entropy check as disproportionate for an internal HS256 signing secret;
  byte-length + a placeholder denylist matches this project's existing
  precedent (`WEBHOOK_SHARED_SECRET`'s "replace-me" critique) without
  inventing a password-strength subsystem.
- **T2 — truncate the password to 72 bytes silently vs. reject it:**
  rejected silent truncation. Silently accepting a truncated password means
  a user's actual full password is not what is checked, which is a subtle
  correctness/security surprise a caller cannot observe; rejecting with 422
  is explicit and matches this project's own established pattern of
  rejecting malformed input at the request boundary (`CustomerRequestInput.promised_at`'s
  earlier `str` → `datetime` fix, in `docs/cvf/CVF_CONTROL_MAPPING.md`'s
  customer_request row).
- **T3 — a full migration-tracking table (e.g. `schema_migrations` with
  applied-hash bookkeeping) vs. relying on existing `IF NOT EXISTS`
  idempotency:** rejected the tracking-table approach as disproportionate
  new infrastructure for the immediate need (one existing volume missing
  one new table); every migration file already uses the idempotent form, so
  "reapply everything in order" is sufficient and lower-risk than
  introducing new schema/tooling this tranche would then also need to keep
  correct.
- **Evidence — reuse the generic CVF-core provider canary as-is vs. design
  a project-specific identity-gated evidence script:** rejected reusing the
  canary unmodified; per reasoning above, it does not exercise this
  project's `identity` control at all, so passing it would be governance
  theater, not proof.

## Consequences

- `jwt_secret_key` becomes a stricter required setting; any existing `.env`
  with a short/placeholder secret will fail to start after this repair —
  intentional (fail-closed), and the SPEC will require this be tested
  positively and negatively, not just asserted.
- `LoginInput` gains a request-boundary rejection path (422) that did not
  exist before; any caller currently sending an over-length password
  (unlikely given no real users exist yet outside `scripts/seed_dev_users.py`)
  will see 422 instead of a 500 crash — a strict improvement, not a
  behavior a real caller could have been relying on.
- Operators with an existing `postgres_data` volume gain a documented,
  idempotent path to acquire the `users` table; operators without one
  (fresh volumes) are unaffected, since `docker-entrypoint-initdb.d` already
  picks up `003_users.sql` on first init.
- `identity`'s CVF-control status remains **not an approved load-bearing
  claim** until this tranche's REVIEW and live evidence both pass — this
  ADR does not itself change that status.

## Migration and rollback

All T1-T3 changes are additive/stricter, not schema- or data-destructive:
tighter Pydantic validation (T1, T2) and a new, optional, idempotent
migration-runner script (T3) that does not alter existing migration files.
Rollback, if needed, is reverting the specific commit(s) this repair
produces — `cd36b27` is untouched either way and remains available as a
rollback floor on its own.

## Evidence

Defined in full by the SPEC and WORK_ORDER that follow this ADR. At minimum:
positive/negative tests for T1 (weak/placeholder secret rejected, valid
secret accepted, no secret logged), T2 (ASCII >72 bytes and multibyte >72
bytes rejected for both existing and unknown usernames, timing-equalization
preserved, existing valid-login tests still pass), T3 (idempotency-guard
test over all migration files, runbook documented), T4 (doc/continuity
corrections), and the live-evidence script's sanitized receipt once
`ALIBABA_API_KEY` is available.
