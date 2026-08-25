# DESIGN — P4-C Integration Edge

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `DESIGN`
- Risk: `R2`
- Author: `DESIGN_AUTHOR`
- Parent INTAKE:
  `docs/decisions/INTAKE_2026-08-23_P4C_INTEGRATION_EDGE.md`
- INTAKE review: final `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`
- BUILD authority: `NOT GRANTED`

## 1. Decision summary

P4-C will replace the current single-route scaffold with an edge-owned,
provider-neutral ingress and outbound orchestration boundary. It will preserve
verified raw envelopes, control replay and rate budgets, quarantine unsafe or
unrouteable input, produce non-authoritative canonical candidates, and route
only through authenticated idempotent ports.

The Integration Edge owns edge evidence and delivery state. It does not own
operational truth, user/channel identity mapping, conversation placement or
concrete provider adapters.

## 2. Component boundary

The design has five layers with one-way dependencies:

1. **Transport adapter port** — receives exact bytes plus bounded headers and
   supplies provider-neutral verification/parse/send interfaces from
   `channel-sdk`. P4-C supplies only a deterministic test-only conformance fake
   behind this port. It supplies no deployable generic or provider adapter;
   generic webhook, Zalo, WhatsApp and other concrete adapters remain P4-D.
2. **Ingress orchestrator** — executes the closed admission order and is the
   only component allowed to advance an inbound envelope between terminal
   states.
3. **Edge store port** — edge-owned persistence for raw envelopes, replay
   reservations, quarantine records, rate buckets, route attempts, outbound
   commands and sanitized receipts. It is separate from Operations Ledger.
4. **Downstream ingress port** — service-authenticated idempotent handoff of a
   canonical candidate. It cannot call internal `POST /messages` anonymously
   or write confirmed truth directly.
5. **Outbound orchestrator** — validates a core-issued command and its
   prerequisite receipt references, then delegates at most one attempt through
   an injected adapter port and records the outcome.

`workspace-api`, `operations-ledger`, `ai-gateway`, `governed-rag` and provider
implementations must not be imported by the edge domain layer. Application
wiring may implement the downstream port without reversing dependencies.

## 3. Persistence and ownership

P4-C introduces an `EdgeStore` protocol owned by `integration-edge`, with a
deterministic in-memory implementation for contract tests and a SQL-backed
implementation for durable evidence. Any schema/migration is edge-owned even
if it uses the repository's shared database deployment tooling; its tables are
not Operations Ledger business-truth tables.

The store owns these conceptual records:

- immutable raw envelope: edge id, channel/endpoint ids, external message id,
  AES-256-GCM ciphertext stored in the same SQL row, key id, nonce/tag, byte
  length, plaintext body digest, verification metadata, receive time and
  retention class;
- replay reservation: namespace, external message id, body digest, state,
  owner token and expiry/version;
- quarantine record: envelope id, closed reason, safe diagnostics, retention,
  acknowledgment/release/delete lineage and actor authority reference;
- rate bucket: policy id/version, subject digest, window and atomic count;
- route attempt and outbound command/delivery attempt with idempotency keys,
  exact digests, state/version and sanitized receipts.

Raw external bytes are never stored in `messages.raw_payload`, audit metadata,
logs, HTTP responses or provider receipts. The current internal-message rule
that persists `raw_payload = NULL` remains unchanged.

P4-C does not use an external blob store. An injected edge key provider returns
an active key id and 256-bit key; no domain component reads environment secrets
directly. AEAD additional authenticated data binds edge id, endpoint/channel,
external message id, body digest and receive time. Encryption is completed in
memory before the SQL transaction; the transaction atomically inserts the
ciphertext row, replay state and any terminal receipt/quarantine record. If the
key provider, encryption or SQL store is unavailable, no reservation is
committed and no success/quarantine claim is emitted. Read verifies the AEAD
tag and plaintext digest. Retention deletion atomically removes ciphertext and
creates a digest-only tombstone; key rotation retains decrypt authority until
all ciphertext for the retired key is deleted. Plaintext is never staged to a
filesystem or second store.

## 4. Inbound processing order

The ingress orchestrator is fail-stop and uses the following order:

1. Resolve an allowlisted endpoint and atomically consume a **pre-auth
   transport budget before reading the body or computing HMAC**. Its subject is
   a privacy-safe digest of endpoint id plus peer identity derived only from a
   trusted proxy/transport context; forwarded or payload fields are never
   authority. Missing trusted peer context, unavailable counter storage or an
   exhausted budget fails closed with no body read. Concurrent requests share
   one atomic fixed-window count.
2. Apply bounded header, declared-length and streamed-body limits. Over-limit
   or unknown endpoints are refused without retaining attacker-controlled
   bodies. The pre-auth count remains consumed because transport work occurred.
3. Resolve a non-placeholder secret and verify a versioned signature over a
   preimage binding the exact body to endpoint/channel id, external message id,
   timestamp and signature version. Missing/invalid/stale authentication is a
   zero-raw-persist refusal with only sanitized metrics/receipt; it has consumed
   exactly one pre-auth count and zero post-auth counts.
4. Compute the body digest and execute one SQL transaction that atomically
   consumes the **post-auth subject budget** and classifies replay state. The
   post-auth subject is the server-configured authenticated provider account,
   never a payload sender. Every valid-signature request consumes exactly one
   pre-auth and one post-auth count. Within the transaction:

   - a new key inserts the replay reservation, encrypted raw envelope and
     reservation owner/version together;
   - a matching committed key/digest records `DUPLICATE` linked to the original
     envelope without storing a second raw copy;
   - the same key with a different digest inserts a distinct encrypted
     collision envelope and a `QUARANTINED_KEY_COLLISION` record linked to both
     collision and original envelope, while leaving the original reservation
     unchanged;
   - a concurrent active same-digest reservation records a bounded retryable
     conflict and cannot overwrite evidence;
   - an exhausted post-auth budget records a terminal rate outcome; no parsing,
     attachment work or routing follows.

   Any failure rolls back the post-auth count, new reservation, envelope,
   collision/quarantine and receipt as one unit; the already-consumed pre-auth
   count is not rolled back. Concurrent collision races are resolved by unique
   constraints and retry-safe transaction classification, not last-write wins.
5. Parse a closed envelope schema. Malformed, ambiguous or unsupported content
   becomes quarantine; raw bytes are not echoed in errors.
6. Validate attachment metadata, declared size/type/hash and scan-port result.
   P4-C defines the port and fail-closed result handling but does not claim a
   production malware scanner or download from a real provider.
7. Build a non-authoritative canonical candidate with external trust marking,
   exact provenance digests and no inferred user/workspace/shift authority.
8. Persist the candidate digest and route intent, then invoke the authenticated
   downstream port at most once per attempt. Definitive acceptance commits
   `ROUTED`; definitive refusal commits `ROUTE_REFUSED`; ambiguous transport
   outcomes commit `ROUTE_OUTCOME_UNKNOWN` and require reconciliation before
   retry.

Later stages cannot run after an earlier terminal outcome. Every state change
is optimistic-versioned and transactionally bound to its receipt.

## 5. Canonical candidate and trust boundary

The candidate is data, never instruction or truth. Required semantics include:

- `trust = UNTRUSTED_EXTERNAL` and `state = RAW`;
- channel/endpoint ids from server configuration, not payload authority;
- external sender, timestamps, conversation keys and destination hints kept as
  unverified claims with source paths and digests;
- content and attachment references bounded and classified conservatively;
- raw-envelope id/body digest, verification scheme/version and adapter id;
- no confirmed event, assignment, user identity, approval or conversation
  mapping fields.

The downstream port may create only an ingress proposal/quarantine candidate.
P4-E later owns identity mapping and conversation routing; existing core
identity, permission, assignment, domain-lock, approval and audit controls
remain authoritative.

External content cannot reach an AI prompt in P4-C. The edge domain must not
import or invoke `ai-gateway`, `ai-providers`, `governed-rag` or retrieval
packages. Any later AI consumer must independently apply its own admission and
prompt-injection controls.

Both internal directions use a closed `ServiceAssertionV1`, separate from user
JWTs and provider webhook signatures. It is an HMAC-SHA256 assertion over
canonical bytes with exact fields: version, key id, issuer, service subject,
audience, operation, HTTP method/path, issued/expiry time (maximum 60 seconds),
unique nonce, body SHA-256, idempotency key and correlation id. The receiver
uses a server-owned allowlist of active key ids/validity windows, constant-time
signature verification, exact audience/operation matching, clock checks and an
atomic nonce replay store. Missing key registry/replay store, unknown service,
claim/body drift, stale assertion or repeated nonce fails closed before domain
effects. Rotation may overlap explicitly bounded current/previous key windows;
expired keys never verify new assertions.

For edge-to-core routing, issuer/subject is `integration-edge`, audience is
`workspace-api`, and the sole operation is `external_ingress.propose`. A new
dedicated core port accepts only a `RAW`/`UNTRUSTED_EXTERNAL` proposal and its
edge lineage; it is not internal `POST /messages`, cannot create confirmed
facts and cannot accept asserted user identity, assignment, approval or
conversation placement. The core independently verifies the service assertion,
nonce, candidate schema/digests and idempotency, then persists only the proposal
and actor-neutral receipt. Any later promotion/mapping/mutation must re-enter
the existing user identity, permission, assignment, domain-lock, approval,
audit and confirmation controls; the service assertion cannot satisfy them.

For core-to-edge outbound, issuer/subject is `workspace-api`, audience is
`integration-edge`, and the sole operation is `outbound.deliver`. The core
command-construction service independently revalidates the authenticated actor,
permission, assignment/domain lock, applicable approval, immutable content and
audit intent before signing the exact command digest. The edge independently
verifies the service assertion, nonce, command/idempotency digest and closed
receipt-reference shape, but does not restate user authorization as edge-owned
truth. No public route accepts an outbound command, and a valid service
assertion authorizes only this one bounded operation.

## 6. Quarantine model

Quarantine uses a closed versioned reason vocabulary covering at least:
signature/key collision, malformed schema, unsupported type, unsafe
attachment, unavailable required scan, canonicalization ambiguity, policy
drift, unavailable required quarantine sink and route-policy refusal.

Quarantine is terminal for automatic routing. Human acknowledgment, release
or deletion is a separate authenticated command with actor/purpose evidence;
release creates a new version and re-runs every use-time policy check. The
30-day value in `data-policy.yaml` is a retention ceiling/default, not evidence
that deletion or a sink already exists.

If required quarantine persistence is unavailable after a verified envelope
has been preserved, the edge records a sanitized fallback/error state and
does not route. It must never report successful quarantine delivery without a
committed quarantine record.

## 7. Rate limiting and replay

Rate policies are server-owned and versioned. Subjects are privacy-preserving
digests of endpoint/channel plus authenticated provider account or configured
source; unverified payload sender ids are never budget authority.

Pre-auth and post-auth policies, subjects and counters are distinct. Atomic
counters bind limit, remaining count, window and outcome. Every request that
reaches an allowlisted endpoint consumes exactly one pre-auth count; only a
valid-signature request consumes exactly one post-auth count. Refused,
duplicate, collision and accepted relations are defined by the invariant
matrix; tests must cover invalid-signature floods, concurrency and boundary
counts. Rate refusal is not a replay commit and replay handling is not a
substitute for either rate limiter.

## 8. Outbound mechanics

P4-C owns provider-neutral command and delivery state only. An outbound command
must be received through the `ServiceAssertionV1` internal port and bind immutable
workspace/record/action/version/content/recipient/channel digests, idempotency
key, policy version and references to core-owned permission/approval/audit
prerequisites. The edge verifies shape, freshness and exact digest binding but
does not invent or approve those prerequisites.

States distinguish `NOT_ATTEMPTED`, `SENT_ACCEPTED`, `DELIVERED`,
`PROVIDER_REFUSED`, `RATE_LIMITED`, `OUTCOME_UNKNOWN` and terminal failure.
Timeout is never automatically restated as not sent. A retry requires the same
idempotency identity and a reconciled retryable state. Concrete provider HTTP,
credentials and delivery semantics remain P4-D or later production work.
BUILD tests use only an injected deterministic conformance fake; it is marked
test-only and evidence-ineligible and cannot be registered by runtime wiring.

## 9. Public disclosure and observability

Public responses expose only correlation id, coarse outcome/reason and safe
retry guidance. Logs, metrics, traces and receipts must exclude raw bodies,
content, secrets, authorization headers, attachment bytes and full provider
errors. Safe identifiers are allowlisted or hashed with explicit type labels.

Health distinguishes liveness from readiness of secret configuration, edge
store, quarantine sink, downstream ingress and outbound adapter. It must not
claim readiness from process liveness alone.

## 10. Failure and concurrency semantics

- All store transitions use compare-and-set versions or equivalent atomic
  constraints; concurrent duplicate deliveries cannot create two accepted
  envelopes or two outbound attempts.
- Reservation abandonment has bounded expiry and owner-token recovery; expiry
  never deletes committed evidence.
- Required sink/store unavailability fails closed before routing/sending.
- Ambiguous downstream/provider outcomes remain explicit and block blind
  retries.
- Rollback tests prove no partial state and no accidental business-truth write.
- Runtime secrets have no development placeholder. Tests inject explicit
  fixtures; missing/placeholder configuration fails closed in every mode.

## 11. Invariant-family applicability

`APPLICABLE`. P4-C materially changes an R2 surface with shared receipts across
multiple outcomes, outcome-controlled fields, exact counter relations,
schema/model parity, multiple validators and prior adjacent-outcome findings.

Before SPEC completes, register at least one P4-C terminal-outcome family in
`docs/cvf/invariants/registry.json` with a canonical matrix and digest. SPEC,
WORK_ORDER and review must reference the family id/digest through
`docs/templates/INVARIANT_FAMILY_PROOF.md`; they must not copy matrix rules.

## 12. Evidence strategy

BUILD evidence is deterministic and zero-provider: model/schema tests,
in-memory/SQL parity, migration-created disposable database tests, HMAC and
replay adversarial probes, rate/concurrency boundaries, quarantine/sink
failures, downstream/outbound ambiguity, secret/disclosure scans, dependency
guards and repository gates.

Any test, roadmap closure, release gate, demo proof or public claim asserting
CVF governance behavior must additionally use a separately authorized real
provider API call and record sanitized request/response evidence. Mock/static
evidence and local channel fakes cannot satisfy that rule. DESIGN authorizes no
provider call, credential use, install, deployment, commit or push.

## 13. Alternatives rejected

1. **Keep process-local dedupe and call the edge complete** — rejected because
   restart/concurrency and identifier-consumption semantics remain unproved.
2. **Write external payload directly to `messages.raw_payload`** — rejected
   because it merges edge evidence with operational truth and bypasses the
   authenticated internal-message boundary.
3. **Implement concrete channel providers in P4-C** — rejected because P4-D
   owns adapters and credentials.
4. **Let payload hints choose identity/conversation destination** — rejected
   because P4-E owns those decisions and external fields are untrusted.
5. **Retry every timeout** — rejected because an ambiguous send/route may have
   succeeded and duplicate external effects are material.
6. **External blob storage for raw envelopes** — rejected because a separate
   object store cannot share the required atomic SQL reservation/quarantine
   transaction without a larger outbox/reconciliation protocol.

## 14. Design acceptance conditions

DESIGN review must confirm:

- every INTAKE decision is resolved or explicitly deferred outside P4-C;
- current source truth and P4-D/P4-E ownership remain accurate;
- persistence, ordering, terminal outcomes, retry and disclosure boundaries
  are internally consistent and testable;
- no design path writes confirmed truth or bypasses core controls;
- invariant-family applicability and live-evidence requirements are complete;
- implementation remains unauthorized pending SPEC, independently reviewed
  WORK_ORDER and explicit BUILD authority.

## Disposition

`READY_FOR_INDEPENDENT_DESIGN_REVIEW`.
