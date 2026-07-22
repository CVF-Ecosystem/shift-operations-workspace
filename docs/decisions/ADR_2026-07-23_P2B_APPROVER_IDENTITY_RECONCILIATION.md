# ADR 2026-07-23 — Approver identity reconciliation (close High Finding #4)

- ADR id: `ADR-2026-07-23-P2B-APPROVER-IDENTITY-RECONCILIATION`
- Tranche: `P2B-APPROVER-IDENTITY-RECONCILIATION`
- Control-chain phase at authoring time: `DESIGN`
- Risk: **R2** — changes a load-bearing governance control (`approval`) across
  three governed verticals, adds a migration and a persistence surface, and
  makes a public claim ("approval identity/quorum is governance-enforced") that
  requires live provider evidence. It does not touch authentication issuance or
  production data.
- Status: **PROPOSED** — awaiting independent authorization review and operator
  approval of the WORK_ORDER. **No BUILD has been performed.**
- Specification: `docs/specs/P2B_APPROVER_IDENTITY_RECONCILIATION_SPEC.md`
- Work order: `docs/work_orders/P2B_APPROVER_IDENTITY_RECONCILIATION_WORK_ORDER.md`
- Baseline commit: `848aebaf03af4efa16d04d7f0f02b6d9da0e564b`

## 1. INTAKE — boundary and authority

The operator confirmed the lane order at the P1-B INTAKE: (1) P1-B — DONE, (2)
**`known-principals.yaml` ↔ authenticated users reconciliation (High Finding
#4)** — this tranche, (3) P2-A incidents/handovers, (4) P2-C frontend. Only lane
2 is open. This tranche closes High Finding #4 **within a proven boundary**; it
does not open lanes 3–4 and does not extend P2-B authentication into refresh
tokens, revocation, admin provisioning, or a live PostgreSQL round-trip.

## 2. Verified current state (read-only, at `848aeba`, each by command)

| Fact | Verified value |
|---|---|
| `HEAD` == `origin/main` | `848aebaf03af4efa16d04d7f0f02b6d9da0e564b`, worktree clean |
| Workspace doctor | `PASS (24/24)` |
| Full suite | `292 passed` |
| Approval-bearing verticals | **3**: `EventService.confirm`, `CorrectionService.correct_event`, `TaskService.create_task` |
| Approval input shape | `Approval(approver_id: str, role: str)`, supplied in the **request body** (`ConfirmInput.approvals`, `CorrectionInput.approvals`, `TaskInput.approvals`) |
| Gate | `cvf_runtime.approval.assert_approval_satisfied` checks quorum **shape** + matches each `approver_id`/`role` against `known-principals.yaml` via `CvfProfile.known_role_for` |
| Registry | `packages/cvf-application-profile/known-principals.yaml` — **7** static id→role entries (sup1..3, mgr1..2, exec1, op1) |
| Authenticated identity | P2-B: `get_principal` requires a verified JWT; `Principal(user_id, role)` from signed `sub`/`role` claims only |
| Users store | `database/migrations/003_users.sql` `users` table (text pk = user_id, unique username, bcrypt hash, role CHECK = KNOWN_ROLES, is_active); ledger has `add_user`/`get_user_by_username` — **no `get_user_by_id`** |
| Two independent stores | `known-principals.yaml` and `users` share ids only "for legibility"; they are otherwise unrelated (per model/seed comments) |
| Migrations present | `001`, `002`, `003` (next unused index = `004`) |

## 3. Threat model — why the finding is still open

`assert_approval_satisfied` verifies the quorum **shape** and that each named
`approver_id` is a known principal with a sufficient registered role. It does
**not** verify that the named approver actually acted. The approver identity is
a string in the confirmer's own request body.

**Attack (reproduces the 2026-07-22 Codex probe, still viable today):** an
authenticated `shift_supervisor` (`sup1`) confirms an R3 event by putting
`[{approver_id: sup2, role: shift_supervisor}, {approver_id: mgr1, role:
responsible_manager}]` in its own `ConfirmInput.approvals`. `sup2` and `mgr1`
are real known principals with the right roles, so the quorum is "met" — yet
neither authenticated, saw the record, or approved anything. The distinct-
principal rule and the self-approval guard are satisfied (the named ids differ
from the confirmer), so both pass. **One caller fabricates a multi-party quorum.**

Swapping the lookup from YAML to the `users` table (Alternative A) does not fix
this: the caller would simply name real, active users from the table. The defect
is not *where the registry lives* — it is that **approver identity is asserted
by the caller, not authenticated by the approver.**

Secondary weaknesses in scope:

- **Cross-record replay.** An `Approval` carries no binding to a specific
  target, action, version, or risk. A set of names valid for one record is
  valid for any record at any version.
- **Two authority sources.** `known-principals.yaml` (approver authority) and
  `users` (authenticated identity) are independent, so an approver could be
  authorized in one and absent/inactive in the other — an unreconciled split.

## 4. Decision

**Replace caller-supplied approvals with authenticated, durable, scope-bound
approval receipts, and make the `users` table the single source of approver
identity and authority.**

Decomposed:

- **D1 — Receipts, not names.** An approval becomes a persisted **receipt**
  created by a request authenticated as the approver. The approver's `user_id`
  and `role` are derived **server-side** from the authenticated `Principal` and
  the `users` record — never from a payload field. There is no request in which
  a caller names another principal as an approver.
- **D2 — Scope binding.** Each receipt is bound to `(record_type, record_id,
  action, target_version, risk_class, payload_digest)`, where
  `payload_digest` is null except for `task.create`. At quorum time only
  receipts matching the target's **current** identity/version/action/risk/
  digest count, defeating cross-record, cross-version, and payload replay.
- **D3 — Single authority.** Approver existence, active status, and role come
  from the `users` table (via a new `get_user_by_id`). `known-principals.yaml`
  is **retired as a runtime authority** (§6).
- **D4 — Quorum rules preserved and now load-bearing.** Distinct-principal
  quorum and the self-approval guard are re-expressed over authenticated receipt
  approvers and stay enforced; a confirmer still cannot fill a required seat
  alone.
- **D5 — Durable + atomic.** Receipts persist through the Ledger; the governed
  mutation collects and verifies the matching receipts inside the same
  `transaction()` as the state change and audit append, with matching
  InMemoryLedger and SqlLedger semantics. Receipts are not consumed (§4.6).
- **D6 — Live evidence.** BUILD/REVIEW must bind the authenticated-approval
  quorum to a real Alibaba provider call: fabricated/insufficient/replayed
  approvals are refused **before** any provider call; only a genuine
  multi-approver quorum reaches a sanitized real call (§7).

### 4.1 Persistence surface — new migration `004`

Receipts need durable storage. A new `approval_receipts` table is added via
`database/migrations/004_approval_receipts.sql` (this migration also carries
`task_creation_intents`, §4.4 — one migration file, two related tables, kept
together rather than inventing a second migration index for the same tranche),
mapped in `tables.py`, with `add_approval_receipt` / `list_approval_receipts_for`
on the Ledger Protocol, InMemoryLedger and SqlLedger. Columns (final schema
pinned in the SPEC): `receipt_id` (pk), `record_type`, `record_id`, `action`,
`target_version`, `risk_class`, `payload_digest` (nullable — only used by the
`task.create` scope, §4.4), `approver_id` (FK → `users.user_id`),
`approver_role`, `created_at`. A unique constraint on `(record_type, record_id,
action, target_version, approver_id)` makes a single approver's receipt
idempotent and blocks double-counting one approver into two seats.
`payload_digest` is deliberately absent from the uniqueness key: for
`task.create`, `record_id` is the immutable creation-intent id and therefore
already identifies exactly one digest; for event actions the digest is null.
The full digest remains part of scope matching, not row identity.

Both tables are **fresh**; neither alters `001`/`002`/`003`. Both an existing
migrated database (apply `004` forward) and a fresh database (apply `001`→`004`)
are considered — see §4.5 for exactly how each is verified, since the naive
"run `apply_migrations.py` against SQLite" verification is not available
(§4.5 corrects this).

### 4.2 Approver identity is re-derived from `users`, not trusted from the JWT claim

`Principal.role` comes from a signed JWT claim (P2-B) captured **at login
time**. P2-B explicitly ships no revocation or token refresh (`ACTIVE_SESSION_
STATE.json` `blocked_work`), so a token can still carry a role the `users` table
no longer reflects (the account was demoted or deactivated after the token was
issued, within its up-to-60-minute TTL). Approver **authority** (R2.2) is
therefore evaluated against a **fresh** `get_user_by_id(principal.user_id)`
read at receipt-creation time — `users.role` and `users.is_active`, not
`principal.role` from the token. `principal.user_id` is still what identifies
*which* user is acting (unforgeable, from the verified signature); only the
*authority* judgment is re-derived from the current row. This closes the
narrow window a stale-but-unexpired token would otherwise leave open.

The dependency boundary is explicit: `cvf-runtime` does **not** import the
Ledger or `workspace-api`. Its successor gate accepts a server-owned authority
resolver:

```
assert_approval_satisfied(
    *, profile, risk_class, confirmer, receipts,
    authority_for: Callable[[str], str | None],
) -> None
```

`receipts` need only expose `approver_id`; the gate ignores persisted
`approver_role` when deciding current authority. Each application service
creates `authority_for` as a closure over
`ledger.get_user_by_id(user_id, unit=unit)`: it returns the current role only
for an existing active user, otherwise `None`. The closure is evaluated inside
the governed mutation's transaction, once per candidate approver per quorum
evaluation (memoization inside that single evaluation is allowed; reuse across
requests is not). This preserves `cvf-runtime` as a dependency sink while
making demotion/deactivation after receipt creation load-bearing immediately.

### 4.3 Approval-receipt creation is itself a governed, audited action

Creating a receipt is a state change and must follow the same discipline as
every other governed mutation in this codebase (§4 of the parent P1-B ADR
established this precedent for `SqlLedger`; this ADR extends it to the new
`POST /approvals` endpoint): `get_principal` → re-derive authority (§4.2) →
validate target scope (§4.4/§5) → `ledger.transaction()` wrapping
`add_approval_receipt` **and** `append_audit` together, so a failure between
the two never leaves an unaudited receipt or an audited-but-missing one. The
audit action name is `approval.create`; `record_type`/`record_id` mirror the
receipt's own scope so the audit trail is queryable per target exactly like
every other action.

### 4.4 The Task-create paradox: durable creation-intent, digest-scoped receipts

**The problem.** R2.3 (as first drafted) required an approval's target to
already exist. `Event.confirm` and `Correction.correct_event` target an
`OperationalEvent` that was persisted earlier by an unrelated, unapproved
`event.create` call — so "the target exists" is true for them before approval
is ever sought. `Task.create` has no such earlier step: the governed action
**is** the first persistence of the record. There is no `task_id` to bind a
receipt to before the Task exists, and generating one first and creating a
placeholder Task would let the confirmer silently change the title, risk
class, or evidence between "receipt collected" and "Task actually persisted"
(TOCTOU) — approvers would be approving a payload that is not the one that
ends up governing the shift.

**Rejected fix: drop target-exists validation for `task.create`.** This was
explicitly rejected. Without *some* durable, approver-visible target, a
receipt could not be scoped to anything at all, and the whole point of D2
(scope binding) collapses for this one vertical.

**Chosen design: a durable creation-intent record with a server-computed
payload digest, consumed by the actual create call — no Task lifecycle
change.**

1. **`POST /tasks/creation-intents`** (new, authenticated, `task.create`
   permission bar) accepts the same fields a Task would need
   (`shift_id`, `title`, `description`, `owner_id`, `risk_class`, `evidence`)
   and persists a `TaskCreationIntent` — `intent_id` (uuid, pk, generated
   here), `shift_id`, `risk_class`, `payload_snapshot` (JSON), `payload_digest`
   (sha256 hex of the canonical payload, §5), `created_by` (the proposing
   principal), `created_at`. Persistence and an audit record with action
   `task.creation_intent.create` occur in one Ledger transaction. This is the
   durable target R2.3 requires — it now
   exists *before* approval, without ever creating a placeholder `Task` row or
   touching `TaskStatus`/`operations_domain` (P1-B's moved lifecycle is
   untouched).
   An authenticated, currently active user whose fresh database role can fill
   at least one seat required by the intent's risk class can inspect the exact
   immutable snapshot before approving it via
   `GET /tasks/creation-intents/{intent_id}`. The response carries the snapshot,
   digest, risk class, proposer, and creation time; missing intent is 404 and
   missing/inactive/insufficient authority is 403. This makes
   "approver-visible" an API-backed property rather than an out-of-band claim.
2. Approvers create receipts scoped to `(record_type="Task",
   record_id=intent_id, action="task.create", target_version=1, risk_class,
   payload_digest)` — `target_version` is fixed at `1` for every intent (an
   intent is immutable, so it has exactly one version); `risk_class` and
   `payload_digest` are read from the **stored intent**, never accepted from
   the approver's request (defeats an approver being tricked into approving a
   different risk/payload than what the intent actually records).
3. **`POST /tasks`** (existing endpoint), for an R2+ `risk_class`, now requires
   `intent_id`. The server loads the intent, checks `intent.created_by ==
   principal.user_id` (only the proposer may consume their own intent —
   closes an actor-coherence gap: someone else "spending" an approved intent
   under a different actor identity), **recomputes the digest from the
   request body actually submitted right now**, and requires it to equal
   `intent.payload_digest` exactly. A mismatch (title/evidence/risk changed
   since the intent was approved) is refused — this is the TOCTOU/payload-
   substitution defence the finding asked for: the approver's receipt is only
   ever redeemable against the *exact* payload they saw. On match, the quorum
   for `(Task, intent_id, task.create, 1, risk_class, digest)` is evaluated
   (§4 of the SPEC, R3), and only then is the `Task` persisted — with
   `task_id := intent_id`, so the receipt's `record_id` and the eventual
   `Task.task_id` are the same value throughout.
4. **`add_task` on both backends must reject a duplicate `task_id`.** Today no
   caller ever supplies a pre-existing id (`task_id` is always freshly
   `uuid4()`-generated), so this path has never been exercised; it becomes
   load-bearing here (it is also §4.6's replay defence for this vertical — a
   second `POST /tasks` against the same intent collides on the primary key
   and is refused, independent of the receipts).

R0/R1 tasks (no approval required, R3.5) are unaffected: `POST /tasks` still
accepts a plain payload directly, `intent_id` must be omitted (supplying one
for a no-approval-required risk class is refused — it would be a dead,
confusing parameter otherwise).

### 4.5 Migration evidence — corrected

`scripts/apply_migrations.py` is documented as the **PostgreSQL** upgrade path
(its own docstring: "the upgrade path" for a `postgres_data` volume that
predates a later migration) and has no SQLite execution branch — `apply_all`'s
non-dry-run path calls `make_engine(database_url)` unconditionally and expects
a real server. Running it against SQLite for BUILD verification would either
error or silently do the wrong thing; neither is acceptable evidence.

Corrected plan (mirrors what P1-B/`test_schema_parity*` already do for every
other table):

- `python scripts/apply_migrations.py --dry-run --only 004_approval_receipts.sql
  --database-url sqlite:///unused` proves **discovery and statement-splitting
  only** (`--dry-run` never calls `make_engine`; the URL is required by
  `main()` but unused in this branch, and is only ever echoed through
  `redact_url()`). It is evidence that the file parses into the expected
  statement count, nothing more, and must not be described as "the migration
  ran".
- **SQLite verification** goes through `operations_ledger.tables.metadata`
  (`create_all` against a SQLite engine) plus the schema-parity suite, exactly
  the mechanism `test_schema_parity.py`/`test_schema_parity_types_and_checks.py`
  already use for `shifts`/`tasks`/`users`/etc. — table/column/FK/CHECK/unique
  presence compared two-directionally against the migration text.
- **PostgreSQL** remains **NOT LIVE VERIFIED** and a pre-ship gate, exactly as
  every prior tranche has stated; this tranche does not change that boundary
  and does not require `DATABASE_URL` to point at a real database for ordinary
  BUILD verification.

### 4.6 Replay defence, per vertical — no explicit "consumed" state

The first draft of this ADR said receipts are "consumed atomically". That
claim had no backing mechanism: the schema had only `created_at`, and the
Ledger had `add`/`list`, no state transition. **Corrected decision: receipts
are not single-use and carry no consumption flag.** Replay is defeated by
scope-binding at the point of use, proven separately per vertical rather than
by a generic "consumed" abstraction:

- **`event.confirm`** — a receipt is scoped to `target_version = N`. On success
  `event.version` becomes `N+1` **and** `event.state` moves to `CONFIRMED`,
  which `operations_domain.lifecycle.assert_transition` does not allow to
  transition to `CONFIRMED` again (`CONFIRMED -> {CORRECTED, FROZEN}` only) —
  two independent barriers (version scope + lifecycle guard) block a replayed
  confirm.
- **`event.correct`** — each correction bumps `event.version`; a receipt scoped
  to the pre-correction version does not match the post-correction version, so
  the same receipts cannot back a second correction attempt without new
  receipts scoped to the new version.
- **`task.create`** — `task_id := intent_id` is a Ledger primary key (§4.4
  point 4); a second `POST /tasks` against the same intent collides on that
  key and is refused, independent of receipt state.
- **Retries after a rolled-back failure are intentionally still valid**: if
  `transaction()` rolls back (e.g. the audit append fails), the target's
  version did **not** advance, so the same receipts remain valid for a retry by
  the same confirmer — this is the desired behaviour (an authorized retry after
  transient failure should not force every approver to re-approve), not a gap,
  because the retry is scope-checked against the same unchanged state an
  attacker cannot manufacture.

Unused "extra" receipts (e.g. a third approval when only two seats are
required) are simply never counted past quorum; pruning them is out of scope.

## 5. Alternatives considered

### A — Look up the approver in the `users` table only (rejected)

Swap `known_role_for` (YAML) for a `users` lookup, keeping caller-supplied
`approver_id`/`role`. **Rejected:** the approver id is still asserted by the
caller. A confirmer names any real active user of sufficient role and the quorum
passes with no approver having acted. This relocates the registry without
closing the impersonation finding, and leaves cross-record replay untouched. It
is exactly the "do not treat YAML→table as real authentication" trap the design
constraint names.

### B — Authenticated durable approval receipts (**chosen**)

Each approver independently authenticates and creates a receipt scoped to a
specific target; the gate counts receipts, not names. **Chosen** because it is
the only option where approver identity is *proved by the approver's own
authenticated request*, it is durable and auditable (receipts persist and are
collected and verified inside the governed mutation's atomic boundary), and
scope binding (from C) defeats replay. Cost: a new migration + persistence
surface + receipt/intent endpoints.

### C — Signed, scoped, expiring approval assertions (partially adopted)

Each approver obtains a short-lived signed assertion scoped to
target+action+version+risk; the confirmer submits them; the server verifies
signature/scope/expiry and derives the approver from the verified assertion.
**Rejected as the primary mechanism, its scoping adopted into B:** a purely
stateless assertion is replayable within its expiry window unless single-use is
tracked — which reintroduces state — and it stands up a second token system
parallel to P2-B's JWT, doubling the crypto/verification surface for no gain
over durable receipts. B already authenticates the approver via the existing
P2-B JWT at receipt-creation time; C's *scope* discipline (D2) is the valuable
part and is kept. Expiry, if wanted, is a receipt `created_at` + policy TTL
check — recorded as an **open decision** (§9), not a blocker.

## 6. Source-of-truth ownership — retiring `known-principals.yaml`

Keeping both `known-principals.yaml` and `users` as approver authorities is the
"two authority sources" anti-pattern. Decision: **`users` is the single
runtime authority for approver identity, role, and active status.**
`known-principals.yaml` is **removed from the runtime profile** — dropped from
`_PROFILE_FILES` in `policy_loader.py`, and `CvfProfile.known_role_for` /
`known_principals` are deleted along with the approval gate's dependency on
them.

Disposition of the file itself is fixed: **delete it outright**. No test fixture
retains a YAML approver authority; tests create users through the Ledger.
Retiring it also requires rewriting `tests/cvf/test_approval_known_principals.py`
(it asserts the old YAML behaviour) into the new authenticated-receipt shape.

## 7. Live-evidence design

The tranche claims `approval` identity/quorum is governance-enforced, so
`AGENTS.md` Mandatory Governance Proof applies. `scripts/run_approval_
governance_evidence.py` must, in order:

1. Reject a **fabricated** approval attempt (a confirm with no/foreign receipts)
   **before** any provider call.
2. Reject **wrong-role**, **inactive-user**, **self-approval**, **insufficient-
   quorum**, and **replay** (receipt bound to a different record/version/
   digest) — each before any provider call.
3. Have genuinely distinct **authenticated** approvers create valid receipts
   (via the real `POST /approvals` code path — the runner calls the actual
   service/gate functions in-process, the same pattern
   `run_identity_live_governance_evidence.py` already uses for the identity
   gate) until the quorum for the risk class is satisfied.
4. Only then let a valid governed action proceed to **one real Alibaba call**.
5. Record a **sanitized** request/response receipt at the exact tracked path
   `docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md` (no API key,
   no Authorization header, no JWT, no password, no raw secret) — schema pinned
   in the SPEC.
6. Report network/quota/expiry/provider failure **honestly** as FAIL/BLOCKED
   with `reached_server` truthfully set — never coerced to PASS.
7. Select the model from the current provider inventory
   (`packages/ai-providers/alibaba/select_model.py` over the quota catalog),
   never a hardcoded model that may be exhausted.
8. **Assert the provider-call count explicitly**: `0` after every refusal case
   in steps 1–2, `1` total after the single successful call in step 4 — the
   runner counts its own calls to `call_alibaba`-equivalent and fails itself if
   the count is wrong, so an accidental extra/early call cannot slip past a
   human skim of the receipt.

This mirrors the audited P2-B identity-evidence runner's structure (gate cases
first, one real call, honest failure semantics) rather than inventing a new one.

### 7.1 Claim boundary of the live-evidence run

The evidence runner exercises `approval` governance **in-process, through the
real gate/service functions** — it is not the production HTTP surface calling
Alibaba on every governed action. **No production code path (`EventService.
confirm`, `TaskService.create_task`, `CorrectionService.correct_event`, or the
new `POST /approvals`) ever calls a provider.** The receipt evidences that the
`approval` control, exercised through its real implementation, correctly gates
a provider call one way in this tranche's test harness; it must not be read or
cited as "every production approval routes through an AI provider" — that
claim is false today and this tranche does not make it true. §8.2 below states
this as a non-goal explicitly.

## 8. Consequences

### 8.1 Accepted

- **Breaking request-shape change** to the three governed endpoints: the
  caller-supplied `approvals` field is removed (it was the vulnerability). This
  is acceptable because `workspace-web` is a non-functional shell (no real
  approvals UI consumes it), and keeping the field would preserve the exact
  bypass being closed. The old-payload disposition (reject 422 vs ignore) is
  fixed in the SPEC; the ADR's intent is **fail-closed** (a request that still
  tries to assert approvals must not be silently accepted as approved).
- A new authenticated endpoint to create an approval receipt for a target.
- A new migration, table mapping, and two Ledger methods, plus `get_user_by_id`.
- `known-principals.yaml` retired; `CvfProfile.known_role_for` removed;
  `test_approval_known_principals.py` rewritten.
- `docs/cvf/CVF_CONTROL_MAPPING.md` `approval` row updated at FREEZE from
  "known-principal checked (interim)" to authenticated/receipt-bound — only
  from observed source truth and only after live evidence PASS.

### 8.2 Explicitly not claimed / non-goals

- No change to authentication issuance (`/auth/login`, token TTL), refresh
  tokens, revocation, self-service registration, password reset, rate-limiting.
- No admin user-provisioning flow (`scripts/seed_dev_users.py` stays dev/test).
- **No PostgreSQL live round-trip** — remains a pre-ship gate; the new table is
  verified on SQLite + InMemory only, exactly as prior verticals.
- No incidents/handovers (lane 3), no frontend (lane 4).
- `User` is **not** moved to `operations-domain` — it stays on the auth boundary
  (P1-B decision). This tranche may add a `get_user_by_id` read path but does
  not relocate the model.
- No claim that "all High findings are fixed" — this closes #4 within its proven
  boundary only.
- **No claim that production Event/Task/Correction actions call an AI
  provider.** They do not, before or after this tranche. Only the live-evidence
  runner makes a real call, in-process, to prove the `approval` gate behaves
  correctly under a real request/response cycle (§7.1).

### 8.3 Rollback

BUILD lands as one commit (source + migration + tests); `git revert` restores
the C3-parent **source and test behaviour** in a temporary worktree. The
rehearsal recreates its ephemeral SQLite database from the reverted metadata.
There is no down migration: a real database that has applied `004` retains the
two additive tables until a separately authorized migration removes them, and
their emptiness is not claimed. Existing tables/data are not altered by `004`.
Continuity/catalog/roadmap land in separate commits and revert independently.

## 9. Decisions resolved in this revision (were open, now fixed)

- **O1 — RESOLVED:** old-payload disposition is **reject 422**, implemented via
  `extra="forbid"` on the three request models so an old `approvals` field
  fails Pydantic validation rather than being silently dropped (SPEC §5).
- **O2 — RESOLVED:** receipts carry **no TTL**; durability ends only when the
  target's scope (version/digest) changes (§4.6).
- **O3 — RESOLVED:** `known-principals.yaml` is **deleted outright**, not
  demoted to a fixture; no test retains a YAML approver authority (SPEC R6).
- **O4 — RESOLVED:** the server **auto-collects** stored receipts matching the
  target scope; no request carries approver ids or receipt ids (SPEC R5).
- **O5 (new, from F1) — RESOLVED:** `task.create` binds receipts to a durable
  `TaskCreationIntent` with a server-computed payload digest (§4.4), not to a
  pre-existing `Task`.
- **O6 (new, from F2) — RESOLVED:** receipts are not single-use; replay is
  defeated per-vertical by scope/version/digest/PK-uniqueness (§4.6), not by an
  explicit consumption state.

## 10. Compliance notes

- Fresh control chain from INTAKE; ADR/SPEC/WORK_ORDER authored and reviewed as
  authorization artifacts and committed before any BUILD.
- R2 → REVIEWER independent from IMPLEMENTATION_WORKER; Codex holds REVIEWER and
  COMMIT_STEWARD. The authoring context holds ORCHESTRATOR/SPEC_AUTHOR/
  WORK_ORDER_AUTHOR only.
- Provider-neutral roles. No provider call and no secret read in this
  authorization phase.
- `cd36b27` and all history remain untouched.
