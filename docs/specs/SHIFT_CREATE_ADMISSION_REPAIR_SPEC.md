# Specification — Shift Create Admission Repair

ID: `SHIFT-CREATE-ADMISSION-REPAIR-SPEC-001`
Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
Risk: R2
Status: REVIEW_PASS — WORK_ORDER NEXT; BUILD NOT AUTHORIZED

## 1. Scope and prohibitions

This tranche repairs only the admission path for `POST /shifts`.

It must not change:

- `POST /messages`, message models, sender mapping or Integration Edge;
- any existing shift read, close or freeze behavior;
- frontend mutation controls, offline queue or realtime transport;
- role ranking, JWT format, token lifetime, user provisioning or revocation;
- database migrations or the existing shifts/audit table shapes;
- assignment, tenant or `data_scope` semantics;
- provider behavior in any production endpoint.

Anonymous message admission remains an explicit open security finding and the
sole next security tranche. Closure must not claim that all mutation routes
are authenticated.

## 2. HTTP admission contract

### R1 — verified identity

`POST /shifts` must require
`principal: Principal = Depends(get_principal)`. Identity comes only from the
existing verified JWT bearer dependency.

The route must return:

- HTTP 401 for absent or malformed bearer credentials;
- HTTP 403 when the verified principal has insufficient authority;
- HTTP 422 for invalid query values or an invalid shift time window.

No refusal may create a shift or an audit record.

### R2 — compatibility-preserving request

The existing request remains three required query parameters:

- `name: str`;
- `starts_at: datetime`;
- `ends_at: datetime`.

The response remains the canonical `operations_domain.models.Shift`. No JSON
request body or caller-controlled `shift_id`, `status`, `version` or
`created_at` is introduced.

The canonical model continues to require `ends_at > starts_at`.

### R3 — one router-to-service path

The route must call only
`ShiftService(ledger).create(name, starts_at, ends_at, principal)`.

It must not call `Ledger.create_shift`, `Ledger.append_audit` or
`Ledger.transaction` directly. `CvfDenied` must be translated using its
existing HTTP status. No second shift-creation entry point may be introduced.

## 3. Permission and service behavior

### R4 — permission

The existing permission map gains exactly:

`"shift.create": "operator"`.

The role hierarchy is unchanged. `viewer` is refused; `operator`,
`shift_supervisor`, `responsible_manager` and `authorized_executive` inherit
authority through the existing ranking.

Unknown-action fail-closed behavior remains unchanged.

### R5 — canonical construction

`ShiftService.create` constructs one canonical `Shift` from only `name`,
`starts_at` and `ends_at`.

Server-derived defaults remain:

- a new UUID `shift_id`;
- `status = OPEN`;
- `version = 1`;
- timezone-aware `created_at`.

The service must perform permission admission before opening a mutation
transaction or calling any ledger write.

### R6 — atomic create and audit

One `Ledger.transaction()` unit must contain both:

1. `Ledger.create_shift(shift, unit=unit)`;
2. `Ledger.append_audit(record, unit=unit)`.

The audit record is exact and actor-bound:

- `actor_id = principal.user_id`;
- `actor_role = principal.role`;
- `action = "shift.create"`;
- `record_type = "Shift"`;
- `record_id = str(shift.shift_id)`;
- `control_chain = ["identity", "permission", "create", "audit"]`;
- `before_state = None`;
- `after_state = str(ShiftStatus.OPEN)`.

The service returns only after both writes commit. An exception from the audit
write must roll back the shift. A shift write failure must leave no audit.
Successful admission creates exactly one shift and one matching audit.

## 4. Backend parity

### R7 — InMemory and SQLite

The same service and transaction path must run against `InMemoryLedger` and
SQLite `SqlLedger`.

For both backends, tests must prove:

- successful create and actor-bound audit;
- refusal produces zero writes;
- injected audit failure leaves neither shift nor `shift.create` audit;
- the returned record equals the persisted record;
- SQLite survives dispose/reopen with both records intact.

The tests must use public Ledger behavior, not direct internal dictionary or
table mutation as the assertion path.

### R8 — disposable PostgreSQL 16

The official owned-container runner must execute a real PostgreSQL 16 case
through the authenticated API/service path.

Evidence must prove:

- migrations apply and idempotent reapply under the existing runner;
- an operator JWT creates exactly one shift and one actor-bound audit;
- both records round-trip after connection disposal/reconnect;
- an injected audit failure rolls back shift creation;
- the connection remains usable after the rollback case;
- the exact owned container and captured anonymous volume are absent after
  cleanup.

No new migration or production/managed-PostgreSQL claim is permitted.

## 5. Contract and regression discipline

### R9 — bounded OpenAPI delta

The OpenAPI change is limited to bearer security on `POST /shifts`.

The operation's query parameters, response schema and status-contract shape
must remain otherwise stable. Every unrelated path and reachable schema must
remain byte-stable against the current golden contract.

Repository-wide OpenAPI hash/golden tests may change only if the future Work
Order explicitly authorizes their exact paths.

### R10 — existing lifecycle behavior

Existing shift list, open-work, close and freeze tests must continue to pass.
Direct ledger creation remains available to lower-level fixtures and backend
tests; this tranche governs the HTTP/application admission boundary and does
not prohibit internal test fixture setup.

### R11 — message boundary

No message router, message model, message persistence, channel adapter or
Integration Edge path may change in this tranche.

Review must inspect the exact changed set and record that anonymous message
admission remains open. It must not add a regression test whose purpose is to
freeze anonymous message admission as desired behavior.

## 6. Live governance evidence

### R12 — refusal call accounting

The live evidence runner must reset and observe a real provider-call counter
for each invocation. Before any provider call it must exercise the real
FastAPI/JWT route chain for:

- missing bearer token;
- malformed or invalid bearer token;
- valid `viewer` token;
- invalid shift window with a valid operator token.

Each refusal must show:

- the expected HTTP status;
- no persisted shift;
- no `shift.create` audit;
- observed provider-call delta exactly zero.

### R13 — admitted exactly-one-call proof

After the refusal cases, a valid operator JWT must create a shift through the
real route and satisfy R5-R6. Only after the persisted shift and actor-bound
audit are read back may the evidence runner make exactly one real,
non-mocked provider call.

R7 and R8 remain mandatory closure gates, but their backend/owned-container
proof runs separately from the provider evidence runner. A provider
credential failure must not prevent PostgreSQL evidence from being evaluated,
and a Docker/PostgreSQL prerequisite failure must not be disguised as a
provider failure.

The production `POST /shifts` endpoint must not call a provider. The provider
call is external release evidence that the identity/permission/audit gate was
load-bearing in the tested chain.

Missing or expired credentials must produce a truthful prerequisite/block
result, never PASS.

### R14 — sanitized evidence

No receipt, stdout, stderr or exception rendering may expose:

- provider API key;
- JWT signing secret or bearer token;
- PostgreSQL credentials or full database URL;
- Authorization headers;
- endpoint userinfo, query or fragment.

Receipts may store only the provider family, model, safe host description,
HTTP outcome, deterministic expected token and observed call count.

## 7. Structural constraints

### R15 — file-size guard

All Python files remain at or below 300 physical lines; all
TS/TSX/JS/JSX files remain at or below 200. No debt-registry update or file
size exception is allowed.

The existing `shift_service.py` and shifts router may receive bounded
create-path additions. If a live runner or tests would cross the limit, the
future Work Order must authorize a coherent support module before BUILD.

### R16 — test separation

Tests must remain split by concern:

- permission/service/API admission;
- atomic rollback and backend parity;
- OpenAPI contract;
- PostgreSQL live behavior;
- provider-bound live evidence and sanitization.

No catch-all test module may hide these proof boundaries.

## 8. Acceptance criteria

- **AC-01:** missing and malformed bearer credentials return 401 with zero
  shift/audit/provider writes.
- **AC-02:** a valid viewer token returns 403 with zero writes/calls.
- **AC-03:** operator and every higher role are admitted; role ranking is
  otherwise byte-stable.
- **AC-04:** the route retains the three query parameters and canonical Shift
  response; invalid windows return 422.
- **AC-05:** router source has no direct ledger mutation/audit/transaction call.
- **AC-06:** service constructs only server-default OPEN/version-1 shifts.
- **AC-07:** successful creation emits exactly one actor-bound audit with the
  exact R6 fields.
- **AC-08:** injected audit failure rolls back creation on InMemory and SQLite.
- **AC-09:** SQLite create/audit survives reconnect.
- **AC-10:** disposable PostgreSQL 16 create/audit/reconnect and rollback pass
  with exact cleanup.
- **AC-11:** OpenAPI changes only by the authorized `POST /shifts` bearer
  security delta.
- **AC-12:** existing shift list/open-work/close/freeze and contract tests pass.
- **AC-13:** message and Integration Edge paths have zero-line diff and the
  open message-admission finding remains explicit.
- **AC-14:** refusal cases observe provider-call delta zero.
- **AC-15:** admitted route proof precedes exactly one real provider call and
  the provider result is PASS.
- **AC-16:** receipts and failure output pass adversarial secret-redaction
  probes.
- **AC-17:** full non-live regression has zero failure/error.
- **AC-18:** catalog, session, repository, file-size, JSON, diff and workspace
  doctor gates pass with no new warning.
- **AC-19:** exact future Work Order changed-set ceiling is respected; no
  protected path changes.
- **AC-20:** rollback rehearsal restores the authorization parent and its
  verified baseline.
- **AC-21:** final claim remains exactly the bounded statement in R17.

Any authentication bypass, permission bypass, non-atomic mutation/audit,
secret-bearing output, PostgreSQL residue, unrelated OpenAPI delta or message
scope expansion is a STOP condition.

## 9. Claim boundary

### R17 — permitted closure statement

Only after independent BUILD review may this tranche claim:

> `POST /shifts` requires a verified JWT, enforces `shift.create` permission,
> and atomically persists the shift with an actor-bound audit record.

It may not claim that all mutation routes are authenticated, message identity
is verified, assignment/data-scope authorization exists, the frontend can
mutate, PostgreSQL is production-ready, or P2-C/Phase 2 is complete.

## 10. Next gate

The reviewer must be independent of the future implementation worker and must
compare this SPEC to the INTAKE, ADR, source truth and existing test/evidence
architecture. The operator assigns Codex as ORCHESTRATOR/REVIEWER and Claude
as the future IMPLEMENTATION_WORKER/REPAIR_WORKER.

`REVIEW_PASS` permits authoring a bounded Work Order only. It does not permit
BUILD, provider calls, staging, committing or pushing.

Review record:
`docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_SPEC_REVIEW.md`.
