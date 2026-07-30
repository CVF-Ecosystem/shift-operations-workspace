# Specification — Message Admission and Trust Repair

ID: `MESSAGE-ADMISSION-TRUST-REPAIR-SPEC-001`
Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
Risk: R2
Status: `REVIEW_PASS — WORK_ORDER NEXT; BUILD NOT AUTHORIZED`

## 1. Scope

This tranche repairs only internal-user `POST /messages` admission and the
minimal durable ledger vertical it requires.

It must not change Integration Edge, channel adapters, canonical-message
schema, identity mapping, conversation routing, raw-envelope ownership,
fallback/quarantine, attachments, outbound delivery, domain Message fields,
database migrations, JWT format, role ranking, frontend, or provider behavior
inside a production endpoint.

External/provider messages remain unavailable. They must never enter the
internal route.

## 2. HTTP and authority contract

### R1 — authenticated internal route

`POST /messages` requires
`principal: Principal = Depends(get_principal)` and returns:

- 401 for missing, malformed, expired or invalid bearer credentials;
- 403 for a verified role below `operator`;
- 422 for request-schema validation failure.

Every refusal creates zero message and zero audit records.

### R2 — bounded compatibility body

The JSON body is:

- `shift_id: UUID` — required;
- `text: str` — required;
- `sender_id: str | None = None` — optional legacy assertion;
- `source: str | None = None` — optional legacy assertion.

`sender_id` and `source` are never persisted as caller authority:

- omitted sender is accepted; a supplied sender must exactly equal
  `principal.user_id`, otherwise 403;
- omitted source is accepted; a supplied source must exactly equal
  `INTERNAL`, otherwise 422;
- the response always contains `sender_id = principal.user_id` and
  `source = "INTERNAL"`.

No caller field may set `message_id`, `state`, `created_at`, `evidence` or
`raw_payload`.

### R3 — one router/service path

The router calls only
`MessageService(ledger).create(shift_id, text, principal, sender_assertion,
source_assertion)`.

It must not construct `Message`, call a ledger write, open a transaction or
append audit directly. It maps `CvfDenied`, unknown shift and frozen/duplicate
conflicts to controlled HTTP responses without leaking internals.

## 3. Governed service

### R4 — permission and ordering

The permission map gains exactly `"message.create": "operator"`. Role ranking
and unknown-action fail-closed behavior are unchanged.

The service order is:

1. verify optional sender/source assertions;
2. require `message.create`;
3. construct one canonical internal `Message`;
4. in one `Ledger.transaction()`, persist it and append its audit;
5. return only after commit.

No ledger mutation may occur before assertion and permission admission.

### R5 — canonical construction

The service constructs from only the admitted `shift_id`, `text` and
principal. Server/domain-derived values are:

- new UUID `message_id`;
- `sender_id = principal.user_id`;
- `source = "INTERNAL"`;
- `state = RAW`;
- timezone-aware `created_at`;
- empty evidence.

Message text remains RAW input. It does not become a confirmed event,
instruction, approval or operational fact.

### R6 — atomic exact audit

One transaction contains `add_message(message, unit=unit)` and
`append_audit(record, unit=unit)`.

The audit is exact:

- `actor_id = principal.user_id`;
- `actor_role = principal.role`;
- `action = "message.create"`;
- `record_type = "Message"`;
- `record_id = str(message.message_id)`;
- `control_chain = ["identity", "permission", "create", "audit"]`;
- `before_state = None`;
- `after_state = str(DataState.RAW)`.

Audit failure rolls back the message. Message failure leaves no audit.
Success creates exactly one matching pair.

### R7 — parent shift behavior

Unknown shift returns 404. A FROZEN shift returns 409. OPEN,
HANDOVER_PENDING and CLOSED are accepted because a message is append-only RAW
input; this tranche does not reinterpret close as freeze.

The backend invariant remains load-bearing: direct ledger `add_message` also
rejects unknown/frozen shifts.

## 4. Durable backend contract

### R8 — Ledger Protocol

Ledger exposes:

- `add_message(message, *, unit=None)`;
- `get_message(message_id, *, unit=None)`;
- `message_exists(message_id, *, unit=None)`.

`get_message` raises `KeyError` for absence on both backends.

### R9 — InMemory semantics

InMemory `add_message`:

- checks parent shift and freeze state;
- refuses duplicate `message_id` with controlled `ValueError`;
- refuses non-empty evidence because the table cannot persist it;
- deep-copies into storage and returns a separate deep copy.

`get_message` returns a deep copy. Mutating the input, returned object or read
object must not mutate stored truth.

### R10 — SQL semantics

SqlLedger maps every persisted field exactly:

| Domain | SQL |
|---|---|
| `message_id` | `message_id` |
| `shift_id` | `shift_id` |
| `source` | `source` |
| `sender_id` | `sender_id` |
| `text` | `text_content` |
| `state` | `state` |
| `created_at` | `created_at` |

Internal writes set `raw_payload = NULL`. Non-empty domain evidence is refused,
not silently dropped. SQL create/read uses the existing `messages` table and
no migration.

Unknown/frozen parent, duplicate id and unsupported evidence produce the same
controlled exception categories as InMemory. No raw `IntegrityError` escapes.

### R11 — parity and reconnect

InMemory and SQLite tests prove:

- returned, read-back and persisted values agree;
- copy/alias isolation;
- unknown/frozen/duplicate/evidence refusals leave no partial state;
- message plus audit success and audit-failure rollback;
- SQLite survives engine disposal/reconnect;
- a persisted message is accepted as a customer-request source reference
  through the public ledger path.

`messages` joins the two-directional migration/table schema-parity set.

### R12 — PostgreSQL 16

The owned disposable PostgreSQL 16 runner must include a separate message live
module and prove through a genuine JWT/FastAPI request:

- migrations apply and idempotently reapply;
- exact message/audit persistence and read-back after reconnect;
- `raw_payload IS NULL`;
- audit failure rolls back message creation;
- frozen-shift refusal and duplicate ledger refusal leave no partial rows;
- connection remains usable;
- owned container and captured anonymous volumes are absent after cleanup.

The existing 300-line runner may change only line-neutrally. No production or
managed-PostgreSQL claim is permitted.

## 5. OpenAPI and regression

### R13 — bounded OpenAPI delta

The only intended `POST /messages` delta is:

- bearer security becomes required;
- `shift_id` and `text` remain required JSON fields;
- `sender_id` becomes optional/nullable without authority;
- `source` becomes optional/nullable without the privileged default;
- canonical Message response remains unchanged.

Every unrelated operation and reachable schema remains stable. Existing P2-B
and P2-C OpenAPI chain tests must be updated to carry this single authorized
delta without re-baselining unrelated changes.

### R14 — external zero-diff boundary

Integration Edge, canonical-message schema, channel-sdk/adapters,
identity-mapping and conversation-routing have zero-line diff. Tests and
receipts must state that external ingestion remains unimplemented.

### R15 — regression and size

All existing freeze, customer-request reference, lifecycle, ledger, contract
and OpenAPI tests pass. Python remains at or below 300 lines and
TS/TSX/JS/JSX at or below 200. No file-size debt/exception change is allowed.

## 6. Live governance evidence

### R16 — zero-call refusal matrix

The provider-evidence runner exercises the real FastAPI/JWT chain separately
for:

- missing bearer;
- malformed/invalid bearer;
- valid viewer;
- mismatched sender assertion;
- non-`INTERNAL` source assertion;
- unknown shift;
- frozen shift.

Each case proves expected status, zero message/audit writes and observed
provider-call delta exactly zero.

### R17 — one admitted call

A valid operator JWT then creates exactly one internal message. The runner
reads back and verifies every R5/R6 field. Only after that proof may it make
exactly one real, non-mocked provider call.

The production endpoint never calls a provider. PostgreSQL and provider gates
are separately mandatory; one prerequisite failure must not be disguised as
the other or as PASS.

### R18 — sanitization

No receipt or output exposes provider key, JWT secret/token, database
credential/URL, Authorization header, raw provider body or external payload.
Receipts store only safe provider/model/host, HTTP outcome, expected marker,
observed call count and bounded admission facts.

## 7. Acceptance criteria

- **AC-01:** missing/invalid credentials return 401 with zero writes/calls.
- **AC-02:** viewer returns 403; operator and higher roles are admitted.
- **AC-03:** sender mismatch returns 403 and external source returns 422.
- **AC-04:** admitted response derives sender/source and all R5 defaults.
- **AC-05:** router has no direct construction, mutation, transaction or audit.
- **AC-06:** permission map adds only `message.create: operator`.
- **AC-07:** success emits exactly one R6 actor-bound audit.
- **AC-08:** unknown shift is 404; frozen shift is 409; neither writes.
- **AC-09:** InMemory copy, duplicate and evidence behavior satisfies R9.
- **AC-10:** SQLite mapping/reconnect/rollback satisfies R10-R11.
- **AC-11:** customer-request source reference uses public message persistence.
- **AC-12:** messages table joins complete two-directional schema parity.
- **AC-13:** PostgreSQL 16 JWT-route/reconnect/rollback/cleanup proof passes.
- **AC-14:** OpenAPI delta is exactly R13.
- **AC-15:** external-ingestion surfaces have zero-line diff.
- **AC-16:** all seven refusal cases observe provider-call delta zero.
- **AC-17:** admitted durable proof precedes exactly one real provider call.
- **AC-18:** adversarial output/receipt secret probes pass.
- **AC-19:** focused and full non-live regressions have zero failure/error.
- **AC-20:** repository/catalog/session/file-size/JSON/diff/doctor gates pass
  with no new warning.
- **AC-21:** exact Work Order ceiling is respected; protected paths are clean.
- **AC-22:** authorization-parent rollback rehearsal restores its verified
  baseline and cleans its temporary worktree.
- **AC-23:** closure uses only the bounded R19 statement.

Any bypass, caller-derived authority, partial audit, silent field loss, raw
database exception, external-scope edit, secret exposure, residue or unrelated
OpenAPI delta is a STOP condition.

## 8. Claim boundary

### R19 — permitted closure statement

Only after independent BUILD review may this tranche claim:

> Internal `POST /messages` requires a verified JWT, derives sender/source
> authority server-side, enforces `message.create`, and atomically persists a
> shift-bound internal Message with an actor-bound audit record on the proven
> backends.

It may not claim external ingestion, canonical-envelope equivalence,
verification/mapping/routing/fallback/quarantine/attachments, all-mutation
security, assignment/data-scope, confirmed message truth, production
PostgreSQL, P2-C/P4-C/P4-E or Phase 2/4 completion.

## 9. Next gate

A reviewer independent of the future implementation worker must compare this
SPEC to INTAKE, ADR, source, migrations and existing evidence architecture.
`REVIEW_PASS` permits Work Order authoring only; it does not permit BUILD,
provider calls or implementation edits.

Review record:
`docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_SPEC_REVIEW.md`.
