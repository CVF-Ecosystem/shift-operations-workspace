# INTAKE — Message Admission and Trust Repair

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE RECORDED — DESIGN NOT YET AUTHORED`
- Owner boundary: `shift-operations-workspace`

## Request and trigger

`SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29` reached `FREEZE /
CLOSED_BOUNDED` and recorded anonymous `POST /messages` as the sole next
security tranche.

The operator instructed the governed workflow to continue. This intake opens
only the message-admission trust problem. It does not inherit DESIGN, SPEC,
WORK_ORDER, BUILD, provider-call, commit, or mutation authority from the
shift-create tranche.

## Reproduced current truth

At clean `HEAD == origin/main ==
56e2f3ba871541e1fb80302cf7aa39b1b84a623b`:

- `POST /messages` has no `Depends(get_principal)` or other authenticated
  service identity;
- `MessageInput` accepts caller-controlled `shift_id`, `sender_id`, `text`
  and `source`, with `source` defaulting to the privileged-looking value
  `INTERNAL`;
- the router constructs the canonical operations-domain `Message` directly
  from that payload and calls `Ledger.add_message(...)` directly;
- there is no message application service, permission action, transaction, or
  audit write;
- an ephemeral real `TestClient`/InMemoryLedger probe returned HTTP 200 for an
  anonymous request, accepted `sender_id="forged-executive"` and
  `source="INTERNAL"` unchanged, persisted one message, and emitted zero audit
  records;
- `InMemoryLedger.add_message` persists messages but returns/stores the
  caller's object directly;
- `SqlLedger.add_message` raises
  `NotImplementedError("message persistence not yet wired to SQL")`;
- the migration and SQLAlchemy metadata already contain a minimal `messages`
  table, but the runtime SQL write/read vertical is absent.

The probes used only ephemeral local test state. No production data, provider
call, external webhook, credential, stage, commit, or push was involved.

## Existing trust and contract boundaries

Repository architecture already states:

- external channel input is untrusted until Integration Edge verifies the
  signature, deduplicates, preserves raw payload, and canonicalizes it;
- workspace-api must not receive provider payload directly;
- Integration Edge does not own or write confirmed business truth;
- internal PWA is first-party/authenticated, while customer portal and
  external channels have different trust models;
- ambiguous conversation routing belongs in a fallback queue;
- channel content must not control system instructions or become confirmed
  operational fact automatically.

Current implementation does not yet join those statements into a working
message-admission path:

- Integration Edge's generic webhook verifies HMAC and deduplicates, then
  returns a raw payload response; it does not persist a raw envelope,
  canonicalize a message, map sender identity, route to a shift/fallback
  queue, or invoke workspace-api;
- the operations-domain `Message` is a minimal shift-bound record, while
  `canonical-message.schema.json` carries provider, direction, external
  sender, mapped user, timestamps, verification, context, and attachments;
- the canonical contract allows a nullable/absent shift context, while the
  operations-domain model and database require `shift_id`.

INTAKE records this boundary conflict; it does not choose a design.

## Required DESIGN decisions

- `MAR-INTAKE-F1 ENTRYPOINT_CLASSIFICATION`: decide whether `/messages` is an
  authenticated internal-user command, a service-to-service canonical ingest
  endpoint, or two explicitly separate entry points. External provider
  payload must not silently enter the internal-user route.
- `MAR-INTAKE-F2 SENDER_AUTHORITY`: define how internal sender identity is
  derived from a verified JWT and how external sender identity/provenance is
  derived from a verified channel envelope. Caller-controlled `sender_id` and
  `source` cannot remain authority.
- `MAR-INTAKE-F3 EDGE_TO_CORE_HANDOFF`: define the load-bearing contract
  between Integration Edge and workspace-api, including service
  authentication, signature-verification evidence, dedupe identity, raw
  payload ownership, replay behavior, and fail-closed semantics.
- `MAR-INTAKE-F4 MODEL_CONTRACT_DRIFT`: reconcile the minimal
  operations-domain/database `Message` with the richer Canonical Message
  Contract without pretending they are already equivalent or making an
  unreviewed breaking change.
- `MAR-INTAKE-F5 ROUTING_AND_SHIFT_BINDING`: decide how a verified message is
  bound to a shift and how missing/ambiguous context enters the documented
  fallback queue instead of accepting a caller-selected operational target.
- `MAR-INTAKE-F6 DURABLE_PARITY`: decide the SQL read/write surface, migration
  implications, InMemory copy semantics, duplicate behavior, reconnect
  proof, PostgreSQL 16 evidence, and atomic message-plus-audit boundary.
- `MAR-INTAKE-F7 GOVERNANCE_ACTIONS`: define separate permission/service
  authority for internal creation and external ingestion if both exist,
  including exact actor/provenance-bound audit records and frozen-shift
  behavior.
- `MAR-INTAKE-F8 FAILURE_AND_HTTP_CONTRACT`: define controlled outcomes for
  missing/invalid identity, invalid service authentication, unknown/frozen
  shift, duplicate/replay, invalid canonical envelope, ambiguous routing,
  unavailable persistence, and quarantine/fallback decisions.
- `MAR-INTAKE-F9 LIVE_EVIDENCE`: if closure claims identity, provenance,
  permission, audit, or edge verification is load-bearing, require refusal
  zero-call behavior and exactly one real provider call only after a genuine
  admitted, durable path; mocks remain UI-only.

## Scope questions DESIGN must bound explicitly

- Whether raw-payload persistence, quarantine, attachment scanning and rate
  limiting are included now or split into later Integration Edge tranches.
- Whether the existing `POST /messages` request shape is preserved,
  deprecated, or replaced, and what compatibility proof is required.
- Whether a new migration is unavoidable for canonical provenance fields or a
  deliberately smaller internal-message vertical should close first.
- Whether external channel ingestion can honestly close without a durable
  service-to-service identity mechanism already present in the repository.

These are decisions for DESIGN, not assumptions authorized by this intake.

## Non-goals

- outbound delivery, delivery receipts, retries, channel credential refresh;
- production Zalo/WhatsApp/customer-portal adapters or real channel
  credentials;
- attachment download/scanning implementation unless DESIGN explicitly
  includes it with its own evidence;
- AI classification, RAG, memory, forecasting, prompt execution, or turning
  message content into confirmed operational truth;
- frontend inbox/mutation UI;
- tenant, assignment, or broad `data_scope` redesign;
- reopening shift-create, P2-C reads, incidents, handovers, authentication, or
  approver-identity closures;
- production/managed-PostgreSQL readiness.

## Claim boundary

This intake claims only that the current message path and adjacent trust
surfaces were inspected and the anonymous/caller-authority/backend-parity gap
was reproduced.

It does not claim message admission is repaired, Integration Edge is complete,
sender identity is verified, external messages are durable, all mutation
routes are authenticated, or any provider/channel governance is load-bearing.

## Acceptance boundary for INTAKE

INTAKE is complete when DESIGN can resolve `MAR-INTAKE-F1` through
`MAR-INTAKE-F9` without:

- trusting caller-supplied sender/source authority;
- bypassing Integration Edge for external payloads;
- conflating verified raw input with confirmed operational truth;
- hiding the InMemory/SQL persistence divergence;
- silently choosing a migration or compatibility break;
- inheriting BUILD authority from the closed predecessor tranche.

Next move: author DESIGN only. No production source, test, schema, migration,
contract, provider, Docker/PostgreSQL, stage, commit, or push authority is
granted by this intake.
