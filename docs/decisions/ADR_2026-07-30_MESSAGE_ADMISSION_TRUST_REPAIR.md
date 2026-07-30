# ADR — Message Admission and Trust Repair

- ADR id: `ADR-2026-07-30-MESSAGE-ADMISSION-TRUST-REPAIR`
- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `PROPOSED — SPEC NEXT; BUILD NOT AUTHORIZED`

## Context

`POST /messages` currently combines three unsafe assumptions: the request is
anonymous, `sender_id` and `source` are caller authority, and the router writes
directly to a ledger whose SQL message path is not implemented. The InMemory
path therefore accepts an impersonated internal sender, persists a message,
and emits no audit.

The adjacent external-channel architecture is not yet a usable alternative.
Integration Edge verifies and deduplicates a generic webhook, but it does not
persist a raw envelope, canonicalize the payload, establish service identity,
map the external sender, route to a shift or fallback queue, or hand a durable
canonical message to workspace-api. The richer Canonical Message Contract is
not equivalent to the minimal shift-bound operations-domain/database Message.

## Decision 1 — two explicit entry-point classes

The existing `POST /messages` becomes an authenticated internal-user command
only. It accepts first-party text for an already-known shift and creates an
operations-domain Message with server-derived internal provenance.

External channel ingestion is a separate entry-point class owned by
Integration Edge. Provider payloads, canonical external envelopes and
service-to-service calls must never enter `POST /messages`.

This tranche closes only the internal-user command. External ingestion stays
unavailable and is parked for a later governed Integration Edge tranche. That
later tranche must define a dedicated canonical ingress surface; its exact URL
is intentionally not frozen here.

## Decision 2 — internal sender and source authority

`POST /messages` must require `principal = Depends(get_principal)` and
permission action `message.create`, minimum role `operator`.

The persisted fields are derived as follows:

- `sender_id = principal.user_id`;
- `source = "INTERNAL"`;
- `shift_id` and `text` come from the validated internal command;
- `message_id`, `state` and `created_at` remain server/domain generated.

For bounded compatibility, legacy `sender_id` and `source` request fields may
remain optional assertions during this tranche. They are never authority:

- an omitted value is accepted;
- `sender_id` equal to the authenticated user is accepted;
- a different `sender_id` is refused;
- an omitted or `INTERNAL` source is accepted;
- any other source is refused as invalid for this endpoint.

The SPEC must freeze the exact request schema and HTTP outcomes. The OpenAPI
delta must be mechanically reviewed and limited to bearer security plus this
authority/requiredness change.

## Decision 3 — one governed internal service

Add `MessageService.create(shift_id, text, principal)` as the sole internal
application entry point. The router must not construct or persist a Message
directly.

The service order is:

1. verified identity supplied by the dependency;
2. `message.create` permission;
3. existence and mutable-state check for the selected shift;
4. canonical internal Message construction;
5. one ledger transaction containing message persistence and an exact
   actor-bound `message.create` audit append;
6. return only after both writes commit.

Audit failure must roll back message creation. A frozen shift refuses new
internal messages. Message text remains unconfirmed input and must not become
an operational event, instruction, approval or other confirmed fact.

## Decision 4 — bounded durable model

The existing operations-domain Message and existing `messages` table are the
durable model for this internal command. No migration is required:

- `shift_id` remains required;
- `source` is fixed to `INTERNAL`;
- `sender_id` stores the authenticated internal user id;
- `text_content` maps to the domain `text`;
- `state`, `created_at`, and empty/no external `raw_payload` retain their
  bounded internal meaning.

Implement the smallest missing ledger surface needed for parity: message
create and read on SqlLedger, matching InMemory behavior, transaction
rollback, duplicate-id refusal, returned-versus-persisted equality and
reconnect proof. InMemory must use copy semantics so caller mutation cannot
silently mutate stored truth.

This is deliberately not a reconciliation of the Canonical Message Contract.
No external provider, direction, external identity, verification, attachment,
conversation or nullable shift-routing fields are fabricated in the internal
record.

## Decision 5 — external handoff contract is fail-closed and later

The later external-ingestion tranche must provide all of the following before
workspace-api can admit an external message:

- authenticated service-to-service identity distinct from end-user JWT;
- Integration Edge verification evidence bound to the provider and envelope;
- stable provider/dedupe identity with deterministic replay behavior;
- durable raw-envelope ownership and retention/redaction rules;
- canonical-contract validation before core handoff;
- sender identity mapping with explicit unmapped behavior;
- server-controlled routing to a shift or durable fallback/quarantine;
- atomic durable acceptance plus provenance-bound audit;
- fail-closed behavior when any required trust fact is absent.

Integration Edge may establish provenance and propose routing, but it may not
write confirmed operational truth. Ambiguous or missing shift context must go
to fallback/quarantine, never to a caller-selected shift.

No Integration Edge, canonical schema, channel adapter, identity-mapping,
conversation-routing, raw-payload, attachment, quarantine or fallback
implementation changes are authorized in this internal-only tranche.

## Decision 6 — controlled outcomes

The SPEC must freeze and test at least these outcomes:

- missing, malformed or invalid user token: `401`;
- authenticated role below `operator`: `403`;
- legacy sender assertion mismatching the principal: refusal with no write;
- non-`INTERNAL` source assertion: validation refusal with no write;
- unknown shift: controlled not-found refusal;
- frozen shift: controlled conflict refusal;
- duplicate message id at ledger boundary: controlled duplicate refusal;
- audit or persistence failure: no partial message/audit state;
- production endpoint dependency failure: controlled server response without
  disclosing internals.

Exact non-authentication status codes and error bodies belong in SPEC after
comparison with existing repository conventions. External replay, invalid
canonical envelope and ambiguous routing are requirements for the later
external tranche, not false coverage claims for this one.

## Decision 7 — evidence and provider boundary

Because closure will claim authenticated identity, permission and audit are
load-bearing, BUILD evidence must include:

- anonymous, malformed-token, insufficient-role, sender-mismatch,
  non-internal-source, unknown-shift and frozen-shift refusals;
- zero provider calls for every refusal;
- a genuine operator JWT creating one internal message through the real
  FastAPI/service/ledger path;
- exact persisted message and actor-bound audit proof before exactly one real
  provider call;
- atomic rollback and copy/duplicate parity on InMemory and SQLite;
- disposable PostgreSQL 16 migration, create/read/reconnect and rollback
  evidence through the authenticated API path;
- focused, full-regression, OpenAPI/contract, catalog, session, file-size and
  repository gates.

The provider call is governance evidence only. Production `POST /messages`
does not and must not call an AI provider.

## Decision 8 — claim boundary

On successful review this tranche may claim only:

> Internal `POST /messages` requires a verified JWT, derives sender/source
> authority server-side, enforces `message.create`, and atomically persists a
> shift-bound internal Message with an actor-bound audit record on the proven
> backends.

It may not claim:

- external/channel message ingestion is implemented or durable;
- the Canonical Message Contract is implemented by operations-domain;
- signature verification, raw-envelope persistence, replay, identity mapping,
  fallback, quarantine or attachment handling is end-to-end;
- all mutation routes are authenticated;
- tenant, assignment or `data_scope` authorization;
- message content is confirmed operational truth;
- production/managed-PostgreSQL readiness;
- P2-C, P4-C, P4-E or Phase 2/4 completion.

## Findings disposition

- `MAR-INTAKE-F1`: resolved by separate internal-user and external-service
  entry-point classes; only the internal class is in this tranche.
- `MAR-INTAKE-F2`: resolved internally by JWT principal-derived sender and
  fixed `INTERNAL` source; external provenance remains fail-closed/later.
- `MAR-INTAKE-F3`: resolved as a required future dedicated canonical,
  service-authenticated handoff; no raw provider payload may use `/messages`.
- `MAR-INTAKE-F4`: resolved by a bounded internal durable projection and an
  explicit non-equivalence claim; no fabricated canonical fields.
- `MAR-INTAKE-F5`: resolved internally by server-validated required shift and
  frozen-shift refusal; external routing/fallback remains later.
- `MAR-INTAKE-F6`: resolved by SQL create/read/reconnect, atomic audit and
  InMemory/SQLite/PostgreSQL parity requirements without a migration.
- `MAR-INTAKE-F7`: resolved by `message.create` at operator minimum and an
  exact actor-bound audit; external service authority remains separate.
- `MAR-INTAKE-F8`: resolved by the controlled internal outcome matrix and an
  explicit separation from later external outcomes.
- `MAR-INTAKE-F9`: resolved by refusal zero-call proof and exactly one real
  provider call only after genuine durable internal admission proof.

## Alternatives rejected

- Treat `/messages` as a mixed internal/external endpoint: rejected because
  end-user identity and provider provenance are different authorities.
- Forward verified raw webhooks directly to `/messages`: rejected because
  signature verification alone does not establish canonicalization, mapping,
  routing, raw-envelope durability or service identity.
- Expand the database now to the full Canonical Message Contract: rejected
  because external ingestion dependencies are absent and this would mix P4-C/
  P4-E architecture into a bounded admission repair.
- Leave SQL persistence unimplemented: rejected because an authenticated
  in-memory-only success would still be a durability overclaim.

## Next move

Author a testable SPEC for the bounded internal-message vertical and its
explicit external nonclaims. No source, test, permission, schema, migration,
stage, commit, provider-call or Docker/PostgreSQL authority is granted by this
ADR.
