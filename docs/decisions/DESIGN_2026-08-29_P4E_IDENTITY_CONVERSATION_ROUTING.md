# DESIGN — P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-08-29`
- Phase: `DESIGN`
- Risk: `R2`
- Author: `DESIGN_AUTHOR`
- Accepted predecessor: P4-E INTAKE with `INTAKE_REVIEW_PASS`, findings/
  waivers `NONE/NONE`
- BUILD authority: `NOT GRANTED`

## 1. Design objective and bounded claim

Implement the smallest useful P4-E v1 boundary in dependency order:

1. preserve one authenticated channel-scoped external-sender assertion as
   evidence without treating it as a person or principal;
2. let an authorized human confirm, reject, revoke or correct a mapping from
   that evidence to one current internal user;
3. let an authorized human bind the confirmed mapping to one supported route;
4. deterministically create an immutable placement decision for each existing
   actor-neutral P4-C proposal.

P4-E v1 supports internal-user mapping and `WORKSPACE`, `SHIFT`, `INCIDENT`
or fallback placement. It deliberately defers customer-contact mapping and
`CUSTOMER`/`VESSEL` placement because no authoritative customer-contact,
customer or vessel directory exists. Those enum values may be reserved by
contract but must return a closed unsupported-target outcome and cannot be
activated without a separately reviewed amendment.

The bounded claim is identity linkage and conversation placement metadata,
not authentication, authorization, assignment, approval, business truth,
canonical Message admission, provider integration or production readiness.

## 2. Ownership and dependency direction

Ownership is one-way:

1. `packages/identity-mapping` owns provider-neutral external-identity,
   mapping aggregate, lifecycle and result contracts plus stable token
   derivation/validation interfaces. It imports no Workspace API model.
2. `packages/conversation-routing` owns provider-neutral route-binding,
   placement-decision and route-result contracts plus the deterministic
   selection algorithm. It consumes an identity-mapping read port and never
   manufactures or mutates a mapping.
3. `operations-ledger` owns the Workspace-side durable admitted-proposal,
   placement-work and P4-E persistence plus unit-of-work parity across
   InMemory, SQLite and disposable PostgreSQL backends. P4-C still owns the
   proposal contract/lineage; Ledger owns no authorization or routing decision.
4. Workspace API application services own JWT principal admission, action
   permission, fresh user/assignment/target validation, service-assertion
   admission, atomic mutation plus audit, and composition of the two packages.
5. P4-C Integration Edge continues to own endpoint authentication, raw
   evidence, replay/collision, quarantine and ingress receipts. Its minimal
   amendment supplies authenticated sender evidence and preserves scope in the
   signed actor-neutral handoff; it does not perform P4-E mapping or placement.
6. P4-D remains unchanged and owns outbound delivery only. P4-E produces no
   delivery command and reveals no recipient handle to an adapter.

Neither package imports `workspace_api`, `integration_edge`, concrete ledger
backends, FastAPI, provider SDKs or adapters. Workspace API is the sole
application composition owner. Dynamic discovery, filesystem scanning and a
second contract owner are forbidden.

## 3. Trusted sender-evidence seam

The current `external_id` is an external message id, not a sender id. P4-E
therefore requires a minimal P4-C input/handoff amendment rather than parsing
the untrusted candidate dictionary.

P4-C introduces a new signature version for inputs that carry an external-
sender assertion. The exact field/header encoding is left to SPEC, but the
sender bytes, endpoint id, channel id, external message id, timestamp and body
digest must all be covered by the authenticated preimage. Existing signature
versions may remain valid P4-C ingress, but they carry no P4-E sender evidence
and can reach only the unmapped fallback path.

After signature verification, P4-C derives a stable opaque sender token using
HMAC-SHA-256 over one unambiguous identity-semantic tuple: injected single-
workspace digest, endpoint id, channel id, configured provider-account digest,
subject kind, extraction-policy id and semantic version, verification scheme/
version, plus normalized external-sender bytes. A scoped key id and injected
secret resolver are required. Key bytes and raw sender bytes are
never stored, logged, placed in a receipt or passed to P4-E. The signed
Workspace API handoff adds one closed `SenderEvidenceV1` containing only
workspace digest, endpoint id, channel id, configured provider-account digest,
subject kind, sender token, token key id/version, extraction-policy id/version,
source-path digest, raw-envelope id, body digest and verification scheme/
version. It carries no raw sender value. Candidate content remains
`UNTRUSTED_EXTERNAL / RAW`.

Normalization is conservative and channel-profile-owned: UTF-8 validity,
length and exact profile rules are fixed by SPEC. No case folding, phone
canonicalization, display-name matching or fuzzy equivalence is inferred
unless a later profile explicitly proves it. A missing, invalid or unknown-
key sender assertion produces no token and no mapping attempt.

This seam authenticates that the endpoint asserted a channel-scoped subject;
it does not prove the real-world identity behind that subject.

## 4. External identity and mapping aggregate

`ExternalIdentityKeyV1` is the closed tuple represented by workspace digest,
endpoint id, channel id, provider-account digest, subject kind, extraction-
policy id/semantic version, verification scheme/version, sender token and
token key id/version. The raw sender value is not a model field. The complete
tuple, not an independently mixed set of fields, is the uniqueness scope. The
signed preimage, `SenderEvidenceV1`, token preimage and stored key bind the same
semantic dimensions. Any account, subject, extraction or verification change
creates a different key and requires human-reviewed correction; it never
reuses an old confirmed mapping automatically.

The first valid sender-evidence handoff may materialize an actor-neutral
external-identity observation, but it cannot choose a user target or create a
mapping proposal. A human proposer must select the candidate internal-user
reference through the governed propose action.

One `IdentityMappingV1` aggregate owns:

- immutable mapping id and external-identity key;
- target kind `INTERNAL_USER` and target user id;
- proposal evidence reference/digest and proposing actor class;
- lifecycle status, version and timestamps;
- confirmer/rejector/revoker/successor references as applicable.

The lifecycle is `PROPOSED -> CONFIRMED | REJECTED`; `CONFIRMED -> REVOKED`.
Terminal records are never silently rewritten. Correction creates a new
proposal referencing the prior mapping and atomically revokes the prior
confirmed mapping when the successor is confirmed. At most one current
confirmed mapping may exist for one complete external-identity key, enforced
equivalently in domain validation and durable storage.

Mapping outcomes distinguish absence, conflict, staleness, revoked state,
target unavailability and accepted current mapping. Exact outcome-controlled
fields belong only in the invariant matrix created during SPEC.

## 5. Human authority and mapping actions

P4-E exposes authenticated Workspace API application actions to propose,
confirm, reject, revoke and correct mappings. Router/request fields are never
authority. Every human action follows:

1. cryptographically verified JWT subject;
2. fresh actor lookup from the authoritative `users` store, including active
   status and current role;
3. reconstruct an authorization principal from that verified subject and the
   fresh stored role, then run action-specific permission using only it;
4. scope and separation checks;
5. re-read/lock the actor and rerun fresh-role permission inside the mutation
   transaction;
6. expected-version comparison and lifecycle/target revalidation;
7. atomic state mutation plus actor-bound audit.

The JWT role claim is not a P4-E permission input. A missing/inactive user,
subject mismatch, changed role that no longer permits the action, or failed
transaction-time reread refuses before mutation. This rule applies to every
mapping and binding management action.

Confirmation requires a currently active target user and forbids the target
user from confirming their own linkage. If a human created the proposal, the
same human may not confirm it. P4-E v1 has no system-created targeted mapping
proposal. Rejection/revocation/correction require
their own permissions and current-version checks; none is inferred from a
prior confirmation receipt.

An authenticated permissioned management read lists only opaque observation
id, workspace/endpoint/channel/account/subject/policy selector metadata and
received time; it omits sender token, raw sender and candidate content. Propose
accepts one observation id, target user and the exact external-sender value as
a transient no-log field. The server loads the immutable selector tuple,
recomputes the complete scoped token, requires it to match that one observation
and discards the raw value before persistence. The proposal command digest
binds only observation/key digest and target user, never the raw sender.

Confirm accepts proposal id plus a fresh transient re-entry, reloads the same
observation tuple and must recompute the identical key; mismatch refuses before
target-user lookup or mutation. Correction repeats the two-human successor
flow; rejection/revocation may use the already authorized mapping id/version.
Thus humans can select evidence without candidate content, hidden UI, evidence
viewer or live provider lookup. The transient value is never persisted or
included in audit.

A confirmed mapping stores a user reference only. Consumers must re-read the
user at use time. Mapping never copies or freezes password hash, role, active
status, JWT claims, permission, assignment or approval authority.

## 6. Persistence and transaction boundary

P4-E selects durable repository parity rather than process-local closure. A
new migration and matching in-memory/SQL stores cover:

- immutable Workspace external proposals and proposal-scoped placement work
  items;
- identity mappings and their version/supersession lineage;
- route bindings and revocation/version lineage;
- immutable placement decisions and idempotency keys.

P4-C remains the semantic owner of external-proposal contract and lineage;
operations-ledger is selected as the Workspace-side physical persistence and
unit-of-work owner for the admitted immutable copy plus P4-E tables. P4-E
records reference proposal/envelope ids and digests without copying candidate
content or raw sender bytes. This deliberately replaces the current process-
local Workspace repository; no second live Workspace proposal store remains.

All compound actions use the Ledger unit-of-work. Unique-current and CAS
constraints are authoritative at write time, not preflight-only checks.
SQLite and PostgreSQL driver conflicts are translated to the same controlled
domain outcomes as InMemory. No partial mapping, binding, placement or audit
write may survive a failed action.

Every human command carries a command kind, idempotency key, canonical payload
digest and expected aggregate version. The same key plus same digest returns
the prior sanitized action receipt; the same key plus a different digest is a
closed idempotency conflict. Confirmation, revoke, correction and binding
replacement use write-time CAS. Concurrent incompatible confirmations or
bindings can produce at most one success.

The existing User model has no version. P4-E does not expand the authentication
schema merely to add one. User eligibility is re-read and locked or otherwise
serializably protected inside the action transaction, and a canonical
eligibility digest is retained in the action receipt. A mapping stores only
the user reference, not that digest as future authority.

Proposal admission and placement use a digest-pinned two-transaction inbox
model rather than claiming impossible cross-step atomicity:

1. after service-assertion verification, transaction A idempotently persists
   the immutable proposal and exactly one pending placement work item;
2. after A commits, Workspace API synchronously makes one local processing
   attempt; transaction B locks the work item, re-reads the proposal and exact
   lineage digest, revalidates current mapping/binding/target state, then
   persists one terminal placement decision and marks the item complete;
3. a transient dependency failure rolls back B and leaves the item pending
   with zero placement decision; a repeated same proposal or bounded local
   processor may retry the idempotent item;
4. a permanent non-privileged fallback/refusal is itself a terminal placement
   decision and completes the item.

The Core ingress call is accepted once transaction A is durable. P4-C's
`ROUTED` receipt therefore means only “actor-neutral proposal accepted by the
Workspace boundary,” never “P4-E placed” or business truth. SPEC fixes work-
item claim/retry limits, stale-claim recovery and exact outcome counters. No
external queue, background deployment or exactly-once claim is introduced.

## 7. Route binding and supported targets

Conversation placement never reads message text, attachment metadata,
provider thread labels or AI output. It consumes only a current confirmed
mapping, one current human-authorized `RouteBindingV1`, immutable proposal
lineage and fresh target state.

P4-E v1 permits at most one current active binding per confirmed mapping. A
binding contains mapping id/version, target kind/id/version reference,
binding version, creator and lifecycle timestamps. Replacement atomically
revokes the prior binding and creates a successor. Multiple current bindings
are treated as corruption/ambiguity, never priority-sorted into success.

Supported targets are:

- `WORKSPACE`: an explicit human-authorized binding to the configured single-
  workspace manual-triage scope;
- `SHIFT`: an existing non-closed, non-frozen shift;
- `INCIDENT`: an existing non-closed incident whose parent shift is eligible.

Creating or replacing a SHIFT/INCIDENT binding requires the human actor to
have a current active assignment to the target shift. When the mapped target
is an internal user, that user must also be active and actively assigned to
the target shift at bind time and again at route time. A demotion does not
invalidate identity equality, but deactivation or assignment revocation makes
the binding unusable until separately corrected.

`CUSTOMER`, `CUSTOMER_CONTACT` and `VESSEL` are unsupported in v1. A free-form
`CustomerRequest.customer_id`, candidate field or provider label is never a
directory or target authority.

`WORKSPACE` is a positive placement only because a human created the binding;
it means a configured triage scope under the injected workspace digest, not a
new Workspace aggregate or operational truth. `FALLBACK` is not a binding
target. It is a system terminal disposition used when no privileged placement
is allowed, even if it is surfaced through the same physical triage queue.

## 8. Deterministic placement and conversation identity

Routing runs only after the signed proposal has already been persisted. It
performs one deterministic evaluation:

1. verify proposal existence and immutable lineage;
2. resolve exactly one current mapping by complete external-identity key;
3. revalidate mapping version and current target user;
4. resolve zero, one or multiple current route bindings;
5. revalidate the selected target and required assignments;
6. persist one immutable placement decision or one explicit fallback/refusal
   decision under a proposal-scoped idempotency key.

No mapping, missing/legacy sender evidence, rejected/revoked mapping, missing
binding or deliberately unsupported target creates a system `FALLBACK`
disposition with no actor, target binding or conversation key. Conflicting
mappings/bindings, stale versions, unavailable stores
or ambiguous target state fail closed and never silently degrade into a
privileged route. SPEC decides which non-privileged conditions are triageable
fallback versus terminal refusal and records them in the canonical matrix.

P4-E does not introduce a mutable Conversation aggregate. A
`conversation_key` is a deterministic opaque digest of the current mapping
id/version and binding target/version. Repeated proposals under the same
current tuple share the key; remap, revoke or rebind creates a different key.
Historical placement decisions never move retroactively. The key groups
placement metadata only and confers no actor, assignment or truth authority.
Only positive `WORKSPACE`, `SHIFT` or `INCIDENT` placements carry it; fallback
and refusal decisions forbid it.

## 9. Workspace API and P4-C integration

P4-C's signed internal call remains the only external-proposal creation seam.
Workspace API replaces the current process-local, regenerated-id behavior with
a durable idempotent external-proposal repository. Its closed input preserves
the Edge-issued proposal id and idempotency key, envelope id, workspace/
endpoint/channel scope, external message id, body/lineage digests and the
sender-evidence object above while retaining null actor/assignment/approval/
conversation and `confirmed=False`. Same proposal key plus same lineage returns
the prior proposal; key or envelope reuse with different lineage is a
controlled collision. Workspace API persists that actor-neutral proposal
and its one pending placement work item in transaction A. Only after that
commit does it invoke the local transaction-B processor described in section
6. Placement failure cannot erase the admitted proposal or rewrite P4-C's
receipt; it leaves either a terminal non-truth decision or a pending item for
bounded idempotent retry.

P4-E never overwrites the proposal. It creates separate mapping, binding and
placement records linked by immutable ids/digests. Internal `POST /messages`
is unchanged and cannot be called by P4-E. No canonical Message, event, task,
customer request, incident, approval or audit fact is synthesized from
external candidate content.

The human management API may be private/hidden from public OpenAPI until a UI
and operator-disclosure review exists, but it must use real JWT, permission,
fresh authority and assignment checks. The automatic placement seam accepts
only the verified service assertion and stored proposal id; callers cannot
supply a mapping result, actor id, route target or conversation key.

This is a minimal predecessor seam, not authority to repair unrelated P4-C
implementation debt. P4-E must not absorb broader raw-envelope, reservation,
post-auth rate, transaction or quarantine changes. Any such need returns to a
separate reviewed amendment.

## 10. Privacy, retention and observability

Raw sender values are `RESTRICTED`; external identity tokens and their lineage
are `CONFIDENTIAL` pseudonymous identifiers, not anonymous data. Sender-token
keys are injected secrets with version/key-id rotation; raw sender bytes are
transient only and explicitly excluded from application logs, mapping/
placement rows, audit bodies, receipts and fixtures.

Mapping and binding history is retained for audit while current authority can
be revoked. Privacy deletion tombstones the external key and removes any
optional display metadata without rewriting historical decision digests.
After tombstone, lookup and routing refuse the identity; a future reappearance
requires a new reviewed mapping. Unconfirmed/manual-triage records have a
30-day ceiling; placement/action receipts and revoked digest-only lineage have
a 365-day ceiling, matching current quarantine/raw-message policy ceilings.
An active confirmed mapping is retained only while needed and becomes a
digest-only tombstone on revocation/deletion. SPEC fixes the exact clock,
deletion authority, key-rotation dual-read window and cryptographic-erasure
procedure. A new token-key version never auto-links to an old mapping; aliasing
requires an explicit human-reviewed correction action.

Telemetry is allowlist-only: opaque record ids, outcome, version, target kind,
key id, counts and digests. It excludes sender value/token, username, message
text, candidate fields, JWT, role evidence, assignment details, secret bytes
and full audit snapshots.

## 11. Invariant-family decision

The standard is `APPLICABLE`. P4-E introduces shared outcome contracts,
outcome-controlled fields, lifecycle/version relations, unique-current and
exact decision-count rules, and Python/schema/InMemory/SQL surfaces.

SPEC must register three separate semantic families:

- `P4E-MAPPING-ACTION-OUTCOMES`, owned by identity-mapping lifecycle/action
  surfaces;
- `P4E-IDENTITY-RESOLUTION-OUTCOMES`, owned by the identity-mapping read/
  resolution boundary;
- `P4E-CONVERSATION-PLACEMENT-OUTCOMES`, owned by `conversation-routing`.

The placement family consumes a pinned mapping-family result but does not
duplicate its rules. P4-C ingress families remain separate owners; the sender-
evidence amendment must prove compatibility without copying P4-C terminal
receipt semantics. SPEC pins canonical digests and declares independent
positive/mutation emitters before any product implementation.

## 12. Evidence and acceptance direction

DESIGN/SPEC/BUILD deterministic evidence must cover:

- P4-C signature-version downgrade, sender mutation and missing-evidence
  refusals before token or P4-E use;
- complete identity-semantic token tuple, account/subject/extraction/
  verification/key-version separation and zero raw-sender persistence/logging;
- closed model/schema/migration parity and one-fact mutation corpora;
- durable/idempotent Workspace external-proposal preservation, replay and
  lineage-collision tests plus pending-work recovery across the two
  transactions;
- mapping lifecycle, separation of duty, JWT-role demotion versus fresh stored
  role, fresh user status, CAS, uniqueness,
  correction and atomic audit rollback across all backends;
- route-binding uniqueness, target/assignment revalidation, deterministic
  explicit-WORKSPACE versus system-FALLBACK semantics, replay/idempotency and
  immutable history;
- proof that candidate content cannot set mapping, actor, assignment, target,
  conversation key or operational truth;
- dependency/import boundaries and unchanged internal Message/P4-D ownership;
- all three invariant families, Project Knowledge, session, catalog, file-size and
  repository guards.

No provider call is needed for a deterministic source/contract claim. If a
review, roadmap closure, demo or public claim asserts that CVF identity,
permission, domain-lock, refusal, phase, DLP, bypass, routing or audit behavior
is enforced, a separately authorized live evidence runner must first prove
refusal cases make zero provider calls and exactly one admitted synthetic-
PUBLIC case makes one real provider API call, with sanitized request/response
and physical/accepted counters. That evidence would not prove live channel,
vendor or production identity routing.

## 13. Failure, rollback and stop conditions

Fail closed on missing sender evidence, token-key mismatch, duplicate current
mapping/binding, stale expected version, inactive user, revoked assignment,
closed/frozen target, missing proposal, digest mismatch, ambiguous store
state, audit failure, dependency drift or unknown outcome.

A failed transaction leaves no partial mutation/audit/placement. Migration
rollback may remove only unused P4-E schema before data exists; once records
exist, forward correction/tombstone is required. Any need for provider
credentials, live channel traffic, customer/vessel authority, public UI,
production database, deployment or a larger P4-C/P4-D amendment stops and
returns to the ORCHESTRATOR.

## 14. Rejected alternatives

1. **Use `external_id` as sender id** — rejected because it is the external
   message id and has no sender semantics.
2. **Read sender/target from candidate JSON** — rejected because content is
   untrusted and schema/provider-specific.
3. **Auto-map by name, phone, chat history or AI** — rejected because evidence
   cannot confirm human identity or grant authority.
4. **Copy User role/assignment into a mapping** — rejected because authority
   becomes stale and mappings are identity references only.
5. **Route by message text or provider thread id** — rejected because it
   transfers domain-lock authority to external content.
6. **Invent Customer/Vessel directories from free-form ids** — rejected;
   unsupported targets remain closed until an authoritative owner exists.
7. **Create canonical Messages during placement** — rejected because placement
   metadata is not internal-user admission or operational truth.
8. **Mutate one conversation aggregate across remaps** — rejected because it
   obscures historical scope; deterministic version-bound keys preserve it.
9. **Process-local-only closure** — rejected because confirmation, revocation
   and route history require durable, independently reviewable authority.

## 15. Design disposition

`READY_FOR_INDEPENDENT_DESIGN_REVIEW`.

SPEC, WORK_ORDER, BUILD, product/database changes, provider/network calls,
credentials, installation, deployment, commit and push remain unauthorized.
