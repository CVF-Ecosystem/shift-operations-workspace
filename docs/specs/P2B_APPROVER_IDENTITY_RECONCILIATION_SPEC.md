# SPEC — P2-B Approver Identity Reconciliation

- Spec id: `SPEC-P2B-APPROVER-IDENTITY-RECONCILIATION`
- Tranche: `P2B-APPROVER-IDENTITY-RECONCILIATION`
- Control-chain phase at authoring time: `SPEC`
- Risk: **R2**
- Status: **PROPOSED** — not approved, not built
- Design: `docs/decisions/ADR_2026-07-23_P2B_APPROVER_IDENTITY_RECONCILIATION.md`
- Work order: `docs/work_orders/P2B_APPROVER_IDENTITY_RECONCILIATION_WORK_ORDER.md`
- Baseline commit: `848aebaf03af4efa16d04d7f0f02b6d9da0e564b`

## 1. Purpose and claim boundary

Close **High Finding #4** (approver-identity fabrication) within a proven
boundary: approver identity and authority become **authenticated and
server-derived**, approvals become **durable, scope-bound receipts**, and the
`users` table becomes the **single** runtime authority for approver
identity/role/active-status.

**Intended behaviour vs current implementation truth.** Today the `approval`
control is *callable and known-principal-checked* but **not** approver-
authenticated: `approver_id`/`role` arrive in the confirmer's request body and
are matched against `known-principals.yaml` (ADR §3). This SPEC specifies the
*intended* behaviour; it must not be read as describing what the code does
before BUILD.

**This SPEC does not authorize and its acceptance does not evidence:** any
change to authentication issuance/TTL/refresh/revocation; admin provisioning; a
PostgreSQL live round-trip; incidents/handovers or frontend; moving `User` to
`operations-domain`; any claim that "all High findings are fixed"; or any claim
that production `Event`/`Task`/`Correction` actions call an AI provider (ADR
§7.1 — only the live-evidence runner does, in-process).

## 2. Decisions resolved (ADR §9)

| # | Decision |
|---|---|
| O1 | A request still submitting `approvals` is rejected **422**, via `extra="forbid"` (R7.1) — not silently ignored. |
| O2 | Receipts carry **no TTL**; validity ends only when the target's scope (version/digest) changes (R4.3). |
| O3 | `known-principals.yaml` is **deleted outright** (R6.1); no test fixture retains it. |
| O4 | The server **auto-collects** stored receipts matching the target scope (R5.1); no request carries approver or receipt ids. |
| O5 | `task.create` binds receipts to a durable `TaskCreationIntent` with a server-computed payload digest (R9), not to a pre-existing `Task`. |
| O6 | Receipts are **not single-use**; replay is defeated per-vertical by scope/version/digest/PK-uniqueness (R4, R9.6), not an explicit consumption state. |

## 3. Terminology

| Term | Meaning |
|---|---|
| **Approver** | An authenticated `Principal` who creates an approval receipt for a specific target, acting under their own JWT. |
| **Confirmer** | The authenticated `Principal` performing the governed action (confirm/correct/create) that requires a quorum. |
| **Receipt** | A persisted `ApprovalReceipt` bound to `(record_type, record_id, action, target_version, risk_class, payload_digest, approver_id, approver_role)`. `payload_digest` is `NULL` except for `task.create`. |
| **Target scope** | The tuple `(record_type, record_id, action, target_version, risk_class, payload_digest)` a receipt is bound to. |
| **Creation intent** | A persisted `TaskCreationIntent` — the durable, approver-visible target `task.create` approvals bind to before any `Task` exists (R9). |
| **Baseline** | The repo at `848aeba`: `292 passed`, doctor `24/24`. |
| **Production code** | `.py` under `apps/**`, `packages/**`, `scripts/**` (excludes `tests/**`). |

## 4. Functional requirements

### R1 — `users` is the single approver authority

**R1.1** The Ledger Protocol, InMemoryLedger and SqlLedger gain
`get_user_by_id(user_id)` returning the `User` or `None`.

**R1.2** Approver existence, `is_active`, and `role` are read **only** from a
**fresh** `get_user_by_id` call at the moment of use (receipt creation or
quorum evaluation) — **never** from `principal.role` (the JWT claim) and never
from any request payload. This is deliberate, not redundant with P2-B's
`get_principal`: P2-B ships no token revocation, so a still-valid JWT can carry
a role the `users` table no longer reflects (ADR §4.2). `principal.user_id`
(unforgeable, from the verified signature) identifies *who*; the fresh `users`
row decides *whether they may act as an approver right now*.

**R1.3** After this tranche, no runtime code reads `known-principals.yaml`, and
`CvfProfile.known_role_for` / `CvfProfile.known_principals` no longer exist.

### R2 — Authenticated receipt creation (`event.confirm`, `event.correct`)

**R2.1** `POST /approvals` (§5) creates an approval receipt. It depends on
`get_principal` (verified JWT). The receipt's `approver_id` =
`principal.user_id`; `approver_role` = the role from the **fresh** `users`
lookup (R1.2). Neither is read from the request body.

**R2.2** Receipt creation is refused (no receipt persisted) when the
authenticated approver: does not exist in `users`, is `is_active = false`, or
holds a role with insufficient authority for **any** seat the target's risk
class requires. Refusals are `CvfDenied` with the control name and HTTP status
pinned in §5.

**R2.3** For `record_type="OperationalEvent"` (`action ∈ {event.confirm,
event.correct}`), the request body carries only `record_type`, `action`,
`record_id` — never `risk_class`, `target_version`, or `payload_digest`. The
server loads the live `OperationalEvent` by `record_id`, and:
- refuses **404** if it does not exist;
- derives `risk_class` and `target_version` from the record's **current**
  stored values and stores the receipt with `payload_digest = NULL`.

None of `risk_class`, `target_version`, or `payload_digest` is caller-supplied
for this record type, so a caller cannot pre-sign a guessed future version or
misstate the approval bar.

**R2.4** Receipt creation is **idempotent** on the database uniqueness key
`(record_type, record_id, action, target_version, approver_id)`: a repeat
request returns the **existing** receipt with HTTP `200` (not a new row, not an
error). A request that resolves to a genuinely new key creates a new receipt
and returns HTTP `201`. `payload_digest` is still compared as part of full
scope validation; it is redundant in row identity because an immutable Task
intent id identifies exactly one digest and Event digests are null (R8.1).
There is no destructive "benign conflict" path — idempotent replay is always a
safe `200`.

### R3 — Quorum evaluated over authenticated receipts

**R3.1** `assert_approval_satisfied` (or its successor) takes the **confirmer**
and the **stored receipts** for the target scope (fetched server-side via
`list_approval_receipts_for`), never a caller-supplied approval list. Its
signature no longer accepts approver names from the caller. The exact successor
contract is:

```
assert_approval_satisfied(
    *, profile: CvfProfile, risk_class: str, confirmer: Principal,
    receipts: Sequence[ApprovalReceiptLike],
    authority_for: Callable[[str], str | None],
) -> None
```

`ApprovalReceiptLike` is a structural/internal protocol requiring only
`approver_id`; `cvf-runtime` does not import `operations-domain`,
`operations-ledger`, or `workspace-api`. Each application service supplies
`authority_for` as a server-owned closure over
`ledger.get_user_by_id(user_id, unit=unit)`, returning the fresh database role
only for an existing active user and `None` otherwise. Persisted
`approver_role` is evidence only and is never current authority. The resolver
is evaluated inside the governed transaction; it may be memoized only for that
single quorum evaluation, never across requests.

**R3.2** A seat counts only if filled by a receipt whose `approver_id` resolves,
via a **fresh** `get_user_by_id` call at evaluation time, to an existing,
`is_active` `users` record whose role has authority for that seat. A receipt
whose approver has since become inactive or been removed does **not** count —
evaluated fresh every time, not cached from receipt-creation time.

**R3.3** Distinct-principal quorum: each required role is filled by a
**distinct** `approver_id`. No single approver fills two required seats.

**R3.4** Self-approval guard: the confirmer's own `user_id` cannot be the sole
filler of the required quorum; a required quorum is never satisfied by the
confirmer alone.

**R3.5** R0/R1 (no required roles) require no receipts, unchanged.

### R4 — Scope binding defeats replay

**R4.1** Only receipts whose full target scope equals the target's **current**
`(record_type, record_id, action, version, risk_class, payload_digest)` are
counted.

**R4.2** A receipt created for record A never counts toward record B
(cross-record replay denied).

**R4.3** When a record's `version` changes (`event.confirm`/`event.correct`) or
a different `payload_digest` is presented (`task.create`, R9), receipts bound
to the prior scope no longer match and no longer count. No time-based expiry
(O2). Retries after a **rolled-back** failure remain valid, because the
target's scope did not actually advance (ADR §4.6) — this is intended, not a
gap.

### R5 — Server-side collection

**R5.1** At confirm/correct/create, the service **auto-collects** all stored
receipts matching the target's current scope via `list_approval_receipts_for`;
the governed request body contains no approver identities and no receipt ids
(O4).

### R6 — `known-principals.yaml` retired

**R6.1** `packages/cvf-application-profile/known-principals.yaml` is deleted;
`policy_loader._PROFILE_FILES` no longer references it; `CvfProfile` no longer
carries `known_principals` or `known_role_for`.

**R6.2** `tests/cvf/test_approval_known_principals.py` is rewritten to the
authenticated-receipt model. `tests/cvf/test_gates_unit.py` and
`tests/cvf/test_customer_request_repair.py` — the two other test modules that
construct `CvfProfile(known_principals=...)` or call `assert_approval_satisfied`
with caller-supplied `Approval(...)` objects (verified by
`rg -l -g '*.py' "known_principals|known_role_for" apps packages scripts tests`
and the `Approval(` scan in the WORK_ORDER) — are updated to the new
constructor/call shape. No test may re-introduce a YAML approver authority or a
caller-supplied approver list.

**R6.3** Comment-only references to `known-principals.yaml` as a still-current
runtime registry become stale once R6.1 lands and must be corrected to past
tense / point at this tranche as the reconciliation, in: the `User` docstring
in `apps/workspace-api/src/workspace_api/domain/models.py` and
`packages/operations-domain/src/operations_domain/models.py` (both already
touched by this tranche for `ApprovalReceipt`); the `users` table comment in
`packages/operations-ledger/src/operations_ledger/tables.py` (already touched
for the new tables); `packages/operations-domain/README.md`'s "reconciliation
… quyết định" sentence, which now has a decided outcome to state; and
`scripts/seed_dev_users.py`'s module docstring, whose claim that dev fixtures
"stay legible across both registries" no longer holds once one registry is
gone. None of these four files' **behaviour** changes — comment/prose only, no
functional edit, no new test obligation.

### R7 — Governed request shape (breaking, fail-closed)

**R7.1** `ConfirmInput`, the correction input, and `TaskInput` no longer accept
an `approvals` field, **and** are declared with `model_config =
ConfigDict(extra="forbid")` (or the Pydantic v2 equivalent). This is the
concrete mechanism behind O1: FastAPI/Pydantic silently drop unrecognised
fields by default, so removing the field from the model alone would **not**
satisfy "reject 422" — `extra="forbid"` is what turns a stray `approvals` key
into a validation error instead of a silent no-op. A request that still
includes `approvals` (or any approver-identity field) is rejected **422**.

**R7.2** Every existing governed behaviour unrelated to approver identity is
unchanged: permission min-roles, risk/evidence gates, lifecycle transitions,
freeze/atomic-audit, HTTP status codes for those refusals.

### R8 — Durable, atomic, dual-backend (receipts)

**R8.1** A new `approval_receipts` table exists via
`database/migrations/004_approval_receipts.sql`, mapped in `tables.py`, with a
`users.user_id` FK on `approver_id`, `payload_digest` nullable, and a unique
constraint on `(record_type, record_id, action, target_version, approver_id)`.
`payload_digest` is deliberately not part of row uniqueness: a Task intent id
is immutable and identifies one digest, while Event receipts have a null
digest. It remains mandatory in full-scope matching (R4).

**R8.2** `add_approval_receipt` and `list_approval_receipts_for` exist on the
Ledger Protocol, InMemoryLedger and SqlLedger with matching semantics; InMemory
returns `model_copy()` (no live-reference leak, per the standing invariant).

**R8.3** `POST /approvals` persists the receipt **and** appends an
`action="approval.create"` audit record **inside one `ledger.transaction()`**
(ADR §4.3): a failure between the two leaves neither committed. This is
independent of, and in addition to, R9.5's transaction for the governed
mutation itself. The audit is written only for a newly created receipt
(HTTP 201). An exact idempotent repeat (HTTP 200) returns the existing receipt
without appending a duplicate `approval.create` audit record.

**R8.4** The governed mutation (`event.confirm`/`event.correct`/`task.create`)
collects receipts, evaluates the quorum, mutates the record, and appends its
own audit **inside one `transaction()`**, exactly as today (no change to that
existing atomicity boundary). Schema parity (`test_schema_parity*`) covers
`approval_receipts` two-directionally.

### R9 — `task.create` binds to a durable creation-intent digest (F1 fix)

**R9.1** `POST /tasks/creation-intents` (authenticated, `task.create` min-role,
same as today's task-create bar) accepts `{shift_id, title, description,
owner_id, risk_class, evidence}` and persists a `TaskCreationIntent`:
`intent_id` (uuid, server-generated pk), `shift_id`, `risk_class`,
`payload_snapshot` (JSON — the submitted fields), `payload_digest` (§5's digest
definition), `created_by = principal.user_id`, `created_at`. This is the
durable, approver-visible target R2.3-style validation requires for a record
that doesn't exist yet — no `Task` row, no `TaskStatus` value, is created by
this call.

Creation intents are only valid when the submitted risk class has at least one
required approval role. R0/R1 intent creation is rejected 422; those Tasks use
the unchanged direct-create path and must omit `intent_id` (R9.3).

The intent and an audit record with
`action="task.creation_intent.create"`, `record_type="TaskCreationIntent"`, and
`record_id=intent_id` are persisted inside one `ledger.transaction()`; failure
of either write rolls back both. `GET /tasks/creation-intents/{intent_id}` lets
an authenticated user inspect the immutable target before approval only when a
fresh `users` lookup finds the account active and its current role can fill at
least one seat required by the intent's risk class. The response contains
`intent_id`, the complete canonical payload snapshot, `payload_digest`,
`risk_class`, `created_by`, and `created_at`; missing intent is 404 and
missing/inactive/insufficient authority is 403.

**R9.2** For `record_type="Task"` (`action="task.create"`), `POST /approvals`
loads the `TaskCreationIntent` by `record_id`, refusing **404** if it does not
exist. `target_version` is fixed at `1` (an intent is immutable — exactly one
version exists). `risk_class` and `payload_digest` are read from the **stored
intent**, never from the approver's request; the approver's request supplies
only `record_type="Task"`, `action="task.create"`, `record_id=intent_id`.

**R9.3** `POST /tasks`, when the submitted `risk_class` requires approval
(`requirement_for(...).required_roles` non-empty), **requires** `intent_id` in
the body (else **422**). When `risk_class` requires no approval (R0/R1),
`intent_id` **must be omitted** (else **422** — a dead parameter for a
no-approval risk class is refused rather than silently ignored, for the same
fail-closed reason as R7.1).

**R9.4** When `intent_id` is present, the server: loads the intent (**404** if
missing); refuses **409** if `intent.created_by != principal.user_id` (only the
proposer may consume their own intent); recomputes the payload digest from the
**current request body** using the same definition as R9.1 and refuses **409**
if it does not equal `intent.payload_digest` (defeats payload substitution —
the approver's receipt is only redeemable against the *exact* payload they
saw); then evaluates the quorum for `(Task, intent_id, task.create, 1,
intent.risk_class, intent.payload_digest)` per R3.

**R9.5** On a satisfied quorum, the `Task` is persisted with `task_id :=
intent_id` inside the same `transaction()` as the audit append (R8.4,
unchanged shape).

**R9.6** `add_task` on **both** backends refuses a duplicate `task_id`
(InMemoryLedger: explicit existence check; SqlLedger: the primary-key
constraint, mapped to `CvfDenied(control="approval", http_status=409)` — not an
unhandled `IntegrityError`). This is the replay defence for `task.create`: a
second `POST /tasks` against the same `intent_id` collides on the key
regardless of receipt state (ADR §4.6).

## 5. API contract — pinned

Every endpoint, schema, and error case below is exact; a REVIEWER checks
against this table, not prose.

### 5.1 Endpoints

| Method + path | Auth | Purpose |
|---|---|---|
| `POST /approvals` | JWT | Create an approval receipt (R2, R9.2). |
| `POST /tasks/creation-intents` | JWT | Create a `TaskCreationIntent` (R9.1). |
| `GET /tasks/creation-intents/{intent_id}` | JWT | Inspect the immutable creation intent before approval (R9.1). |
| `POST /events/{event_id}/confirm` | JWT | Unchanged path; body loses `approvals` (R7). |
| `POST /corrections/events/{event_id}` | JWT | Unchanged path; body loses `approvals` (R7). |
| `POST /tasks` | JWT | Unchanged path; body loses `approvals`, gains optional `intent_id` (R9.3). |

### 5.2 `record_type` / `action` vocabulary

`record_type ∈ {"OperationalEvent", "Task"}`. `action ∈ {"event.confirm",
"event.correct", "task.create"}` (reusing `permission.py`'s existing action
names). Valid pairs: `("OperationalEvent", "event.confirm")`,
`("OperationalEvent", "event.correct")`, `("Task", "task.create")`. Any other
pair is **422**.

### 5.3 Payload digest definition (R9.1/R9.4)

```
canonical = json.dumps(
    {
        "shift_id": str(shift_id),
        "title": title,
        "description": description,          # or null
        "owner_id": owner_id,                 # or null
        "risk_class": str(risk_class),
        "evidence": [
            {"source_type": e.source_type, "source_id": e.source_id, "sha256": e.sha256}
            for e in evidence
        ],
    },
    sort_keys=True, separators=(",", ":"), ensure_ascii=False,
).encode("utf-8")
payload_digest = sha256(canonical).hexdigest()
```

`evidence_id` (random per `EvidenceRef`) is **excluded** — only the meaningful
fields are digested; list order is preserved as submitted. This mirrors the
`canonical()` convention P1-B established for byte-identical comparisons.

### 5.4 Request/response schemas

**`POST /approvals`** — request: `{record_type, action, record_id}` with
`extra="forbid"`. `risk_class`, `target_version`, and `payload_digest` are all
server-derived from the stored Event/TaskCreationIntent per R2.3/R9.2.
Response `200`/`201`: `{receipt_id, record_type, record_id, action,
target_version, risk_class, approver_id, approver_role, created_at}`.

**`POST /tasks/creation-intents`** — request: `{shift_id, title, description,
owner_id, risk_class, evidence}`. Response `201`: `{intent_id, payload_digest,
risk_class, created_at}`.

**`GET /tasks/creation-intents/{intent_id}`** — response `200`: `{intent_id,
payload_snapshot, payload_digest, risk_class, created_by, created_at}`.

**`POST /events/{event_id}/confirm`** — request body: `{}` (no fields;
`extra="forbid"`). **`POST /corrections/events/{event_id}`** — request body:
`{reason}` with `extra="forbid"`; only its former `approvals` field is removed.

**`POST /tasks`** — request: `{shift_id, title, description, owner_id,
risk_class, evidence, intent_id}` (`intent_id: UUID | None = None`;
`extra="forbid"`).

### 5.5 Error contract — pinned per case

| Case | Control | HTTP | Applies to |
|---|---|---|---|
| Missing/invalid JWT | — (`get_principal`, unchanged) | 401 | all |
| Unknown `record_type`/`action` pair | `approval` | 422 | `POST /approvals` |
| Unknown target (`record_id`/`intent_id` not found) | `approval` | 404 | `POST /approvals`, `POST /tasks` (intent lookup) |
| Approver missing from `users` or `is_active=false` | `approval` | 403 | `POST /approvals` (R2.2) |
| Approver role insufficient for any required seat | `approval` | 403 | `POST /approvals` (R2.2) |
| Idempotent repeat (exact same scope+approver) | — | 200 | `POST /approvals` (R2.4) |
| New receipt | — | 201 | `POST /approvals` |
| Insufficient quorum | `approval` | 409 | confirm / correct / create |
| Self-approval-only quorum | `approval` | 409 | confirm / correct / create |
| Old `approvals` field present | — (Pydantic `extra="forbid"`) | 422 | confirm / correct / create (R7.1) |
| `intent_id` required but missing (risk needs approval) | `approval` | 422 | `POST /tasks` (R9.3) |
| `intent_id` present but risk needs no approval | `approval` | 422 | `POST /tasks` (R9.3) |
| Creation intent requested for risk with no required approval role | `approval` | 422 | `POST /tasks/creation-intents` (R9.1) |
| Intent owned by a different principal | `approval` | 409 | `POST /tasks` (R9.4) |
| Payload digest mismatch vs. intent | `approval` | 409 | `POST /tasks` (R9.4) |
| Duplicate `task_id` (intent already consumed) | `approval` | 409 | `POST /tasks` (R9.6) |
| Malformed body (Pydantic) | — | 422 | all |
| Intent viewer missing/inactive/insufficient for every required seat | `approval` | 403 | `GET /tasks/creation-intents/{intent_id}` |

## 6. Acceptance criteria

Every AC is a command or an executed test. Both backends (InMemoryLedger and
SqlLedger over SQLite) are exercised wherever persistence is involved. **The
live-evidence AC (AC-16) requires a real Alibaba call** and is the only AC that
does. PostgreSQL is **not** exercised by any AC (§4.6/R8/R9 verify via SQLite +
metadata + schema parity only).

| AC | Requirement | Verification |
|---|---|---|
| **AC-01** | Impersonation closed | With no receipts, confirm of an R3 record is refused (409); the old `approvals` body is 422 (R7.1). |
| **AC-02** | Approver identity is server-derived | A receipt created under approver X's JWT records `approver_id=X`; the endpoint accepts no approver field at all (R2.1, §5.4). |
| **AC-03** | Role inflation closed | An approver whose `users` role is `operator` gets 403 attempting a `shift_supervisor`/`responsible_manager` seat (R2.2). |
| **AC-04** | Inactive/stale-role user closed | An approver with `is_active=false` gets 403 on receipt creation; a receipt from an approver later deactivated **or demoted below the required seat** no longer counts at quorum time — re-checked through the server-owned authority resolver, not cached or taken from `approver_role` (R1.2, R3.1, R3.2). |
| **AC-05** | Duplicate principal closed | Two receipts from the same `approver_id` cannot fill two distinct required seats (R3.3); a repeat identical request returns the same receipt with 200, not a duplicate row (R2.4). |
| **AC-06** | Self-approval closed | The confirmer's own receipt cannot be the sole filler of a required quorum (R3.4). |
| **AC-07** | Insufficient quorum closed | An R3 record with only one valid supervisor receipt (missing the manager seat) is refused 409 (R3.2). |
| **AC-08** | Cross-record replay closed | A receipt for event A does not count for event B (R4.2). |
| **AC-09** | Target/version mismatch closed | A receipt bound to version N does not count once the record is at version N+1; risk/version/digest are derived from the live stored target rather than accepted from the approval request (R4.3, R2.3). |
| **AC-10** | Valid quorum passes | Distinct authenticated approvers of sufficient role create receipts; `event.confirm` and `event.correct` then succeed and write audit — both backends (R3, R8.4). |
| **AC-11** | Replay defeated per-vertical (not a generic "consume") | Three separate cases, matching ADR §4.6 exactly: (a) a confirmed event's receipts do not satisfy a second confirm attempt (lifecycle guard `CONFIRMED -> CONFIRMED` already rejects it, independent of receipts); (b) a correction's receipts, scoped to the pre-correction version, do not satisfy a second correction at the new version; (c) a rolled-back failure (audit-append raises) leaves the target's version unchanged and the **same** receipts remain valid for a same-confirmer retry — both backends. No test asserts a "consumed" state/method, because none exists (O6). |
| **AC-12** | `users` is single authority | `rg -l -g '*.py' -g '*.yaml' "known_principals\|known_role_for\|known-principals\.yaml" apps packages scripts tests` returns only comment-only matches (R6.3 files) and test files that were rewritten (R6.2) — no runtime code path; `known-principals.yaml` does not exist on disk. |
| **AC-13** | Schema parity | `test_schema_parity*` covers `approval_receipts` and `task_creation_intents` two-directionally (columns, nullability, FK, unique, CHECK) (R8.1, R9.1). |
| **AC-14** | Full regression not reduced | `python -m pytest -q` reports **≥ the committed baseline (292 at `848aeba`; re-verify at BUILD, do not hardcode a stale number)**, 0 failed, 0 errors. |
| **AC-15** | Validators + guards + doctor | `validate_repository.py`, `generate_catalog.py --check`, `check_session_state.py`, `check_file_size.py` PASS; workspace doctor `24/24`. |
| **AC-16** | Live governance evidence | The runner refuses fabricated/wrong-role/inactive/self/insufficient/replay approvals **with 0 provider calls**; drives a genuine authenticated quorum through the real `POST /approvals` code path; makes **exactly 1** real Alibaba call after quorum is satisfied, returning the expected token; writes the sanitized receipt at `docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md` (§7 schema); network/quota/expiry/provider failure is recorded honestly as FAIL/BLOCKED, never PASS; the runner self-asserts its own call count (ADR §7 steps 1–8). |
| **AC-17** | No secret leak | No API key, Authorization header, JWT, password, or raw secret appears in the receipt, logs, or the diff; secret scan over the changed set is clean. |
| **AC-18** | TOCTOU / payload-substitution closed | Approve a `TaskCreationIntent`, then submit `POST /tasks` with a changed `title` (or `risk_class`, or `evidence`) referencing the same `intent_id`: refused 409, digest mismatch (R9.4). A second `POST /tasks` against an already-consumed `intent_id` with the *original* unchanged payload is refused 409 on the duplicate `task_id` (R9.6). An intent consumed by a principal other than its `created_by` is refused 409 (R9.4). |
| **AC-19** | Receipt creation is atomic, audited, and idempotent | Creating a new receipt persists **both** the receipt and one `action="approval.create"` audit record in one `transaction()`; a failure injected between them leaves neither committed. An exact repeat returns 200 with the existing receipt and adds no duplicate audit — both backends (R8.3). |
| **AC-20** | Migration evidence is honest | `python scripts/apply_migrations.py --dry-run --only 004_approval_receipts.sql --database-url sqlite:///unused` proves discovery/statement-splitting only (exit 0, prints the statement count) and is never described as "the migration ran"; `approval_receipts` and `task_creation_intents` are verified via `operations_ledger.tables.metadata` + schema parity against SQLite, not via `apply_migrations.py`; no AC requires a real `DATABASE_URL`; PostgreSQL remains explicitly **NOT LIVE VERIFIED** (ADR §4.5). |
| **AC-21** | Rollback | `git revert` of the BUILD commit on a temporary worktree/clone (never the primary workspace) restores C3-parent source/test behaviour and the baseline suite using a newly created ephemeral SQLite database; C1/C2 remain intact. No down migration or rollback of a real database schema/data is claimed. |
| **AC-22** | Creation intent is visible and atomically audited | An authorized approver can read the immutable intent snapshot/digest; missing/inactive/insufficient users get the pinned 404/403 outcomes. Intent creation commits both intent and `task.creation_intent.create` audit, or neither on injected failure — both backends (R9.1). |

## 7. Live-evidence receipt — minimum schema

`docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`, produced by
`scripts/run_approval_governance_evidence.py` (mirrors the P2-B identity
receipt's structure). Required fields:

- generation timestamp;
- provider + model selected (from the quota catalog, never hardcoded);
- a table of gate-refusal cases with outcome (each must show **0** provider
  calls reached);
- the authenticated-quorum construction steps (each receipt created, through
  the real code path);
- the single real-call section: `reached_server` (bool), HTTP status,
  started-at timestamp, expected-token match (PASS/FAIL), **not** the raw
  response body beyond the minimal excerpt needed to prove the expected token
  was present;
- explicit total provider-call count (must read `1`);
- an explicit redaction statement ("contains no API key, no Authorization
  header, no JWT, no password, no raw secret" — matching the existing P2-B
  receipt's own header line);
- overall outcome: PASS / FAIL / BLOCKED, honest under network/quota/expiry
  failure (never coerced to PASS);
- a claim-boundary paragraph stating this evidences the `approval` gate's
  in-process behaviour only, not that production actions call a provider (ADR
  §7.1).

## 8. Test artifacts to be added (names fixed in the WORK_ORDER allowlist)

- A CVF vertical test covering AC-01…AC-11, AC-18, AC-19, AC-22 at service and HTTP
  level, both backends.
- A schema-parity extension for `approval_receipts` and `task_creation_intents`
  (AC-13).
- A rewrite of `test_approval_known_principals.py` into the authenticated model
  (AC-12).
- Targeted updates (call-site argument shape only, not outcome assertions
  beyond what R9/R7 deliberately change) to the eight files identified by the
  WORK_ORDER's `rg` audit that construct `Approval(...)`, pass `approvals=`, or
  build a `CvfProfile` with `known_principals=` — see WORK_ORDER §3 for the
  exact list and per-file disposition.
- Modifying an existing test's assertions to force a pass is a stop condition;
  only tests whose *premise the tranche deliberately changes* (the retired-YAML
  test, the removed-`approvals`-field call sites, the now-server-collected
  quorum) may be rewritten, and only to the new intended behaviour.

## 9. Evidence required at REVIEW

The IMPLEMENTATION_WORKER produces and the independent REVIEWER re-runs:
`git status --porcelain -uall` and `git diff --stat`; targeted new-test runs;
`pytest -q` tail (≥ baseline); all four validators + doctor; `git diff --check`;
`git diff --stat -- database/` showing only `004_approval_receipts.sql`; the
`--dry-run` migration-discovery output (AC-20, not a claim of execution); the
sanitized live-evidence receipt with its honest outcome and call count; and the
AC-21 revert rehearsal. Numbers are quoted from the run that produced them —
copying a count is the spec-drift finding recorded as Medium #7 in
`EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`.

## 10. Live governance evidence — required, and why

Unlike P1-B, this tranche asserts a **governance behaviour** claim ("approval
identity/quorum is governance-enforced"), so `AGENTS.md` Mandatory Governance
Proof is triggered: BUILD/REVIEW MUST include a real provider (Alibaba) API
call, recorded sanitized, per AC-16 and ADR §7. Passing unit/integration tests
prove structural enforcement; only the live receipt backs the governance claim.
Mock/TestClient output is **not** acceptable as that evidence. The claim is
scoped to the `approval` gate's own correctness (ADR §7.1) — it is not a claim
that any production endpoint calls a provider.

## 11. Definition of done

R1…R9 satisfied; AC-01…AC-22 pass with recorded output including a real Alibaba
receipt at the pinned path; changed set within the WORK_ORDER allowlist;
independent REVIEWER confirms every AC by re-running; catalog/roadmap/continuity
updated only at REVIEW/FREEZE from observed source truth; no claim beyond §1's
boundary; High Finding #4 recorded as **closed within the stated boundary**, not
"all findings fixed".
