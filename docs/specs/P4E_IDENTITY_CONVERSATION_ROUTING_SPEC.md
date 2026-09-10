# SPEC - P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Version: `1.0-draft-r1`
- Phase: `SPEC`
- Risk ceiling: `R2`
- Role: `SPEC_AUTHOR`
- Accepted predecessor: P4-E DESIGN at canonical digest
  `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9`
- DESIGN review: final `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Phase transition authority: operator request on `2026-09-09`
- BUILD authority: `NOT_GRANTED`
- External-effect authority: `NONE`

## 1. Bounded capability and claim

P4-E v1 shall add durable, provider-neutral identity linkage and deterministic
conversation placement for P4-C actor-neutral external proposals. It shall:

1. preserve an authenticated channel-scoped sender assertion as opaque
   evidence;
2. require two distinct authorized humans to confirm a mapping to one current
   internal user;
3. require an authorized human to create one current route binding;
4. produce one immutable placement or non-privileged terminal decision per
   admitted proposal.

Supported positive targets are `WORKSPACE`, `SHIFT`, and `INCIDENT`.
`CUSTOMER`, `CUSTOMER_CONTACT`, and `VESSEL` remain unsupported. P4-E does not
authenticate the external person, grant permission or assignment, confirm
candidate content, create an operational record, invoke internal message
admission, deliver outbound content, or establish production readiness.

## 2. Normative invariant families

The three P4-E families are mandatory because this R2 tranche has shared
result models, outcome-controlled fields, lifecycle transitions, exact
mutation/audit facts, and multiple validator surfaces.

- `P4E-MAPPING-ACTION-OUTCOMES` is pinned by
  `P4E_MAPPING_ACTION_MATRIX_CANONICAL_DIGEST` at
  `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a`.
- `P4E-IDENTITY-RESOLUTION-OUTCOMES` is pinned by
  `P4E_IDENTITY_RESOLUTION_MATRIX_CANONICAL_DIGEST` at
  `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc`.
- `P4E-CONVERSATION-PLACEMENT-OUTCOMES` is pinned by
  `P4E_PLACEMENT_MATRIX_CANONICAL_DIGEST` at
  `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56`.

The symbols live in `docs/specs/p4e_invariant_pins.py`. The matrices are the
sole outcome-shape owners. Python models, JSON Schemas, SQL constraints,
emitters, fixtures, and tests shall consume their pinned contracts rather than
restate a second grammar. Digest drift invalidates SPEC review and stops BUILD
until an independently reviewed amendment is accepted.

## 3. Sender evidence and identity namespace

### R1 - Versioned authenticated sender evidence

P4-C shall add a new ingress signature version for sender-aware inputs. The
authenticated preimage shall use length-prefixed UTF-8 fields and bind:

```text
signature_version, workspace_digest, endpoint_id, channel_id,
provider_account_digest, subject_kind, extraction_policy_id,
extraction_policy_version, verification_scheme, verification_version,
external_message_id, timestamp, normalized_sender_bytes, body_sha256
```

The normalization profile shall require valid UTF-8, reject empty input and
NUL/control characters other than horizontal space, preserve case, perform no
phone/display-name/fuzzy canonicalization, and cap the normalized value at 512
UTF-8 bytes. The exact normalized bytes shall be authenticated before use.
Legacy signature versions remain valid P4-C inputs but carry no P4-E evidence.

### R2 - Opaque sender token

After verification, P4-C shall derive `sender_token` with HMAC-SHA-256 using an
injected active key and a domain-separated, length-prefixed tuple containing
all R1 identity-semantic fields except message id, timestamp, and body digest.
The token key id/version is part of the external identity key. Missing,
inactive, ambiguous, or unavailable key authority yields no observation and no
mapping attempt.

Raw sender bytes and token key bytes shall never be persisted, logged,
returned, audited, or passed through proposal candidate content.

### R3 - `SenderEvidenceV1`

The signed P4-C to Workspace handoff shall carry a frozen, closed evidence
object with exactly: version, workspace digest, endpoint id, channel id,
provider-account digest, subject kind, extraction-policy id/version,
verification scheme/version, sender token, token key id/version,
source-path digest, raw-envelope id, external-message id, body digest, and
received time. It shall contain no raw sender, principal, assignment,
permission, approval, confirmation, or conversation field.

### R4 - `ExternalIdentityKeyV1`

The unique key shall be the indivisible tuple of workspace, endpoint, channel,
provider-account, subject, extraction-policy, verification, sender-token, and
token-key dimensions from R2/R3. A change to any dimension produces a new key.
No partial-key lookup, cross-workspace lookup, fuzzy match, or automatic
carry-forward from an older key is permitted.

## 4. Observation and mapping lifecycle

### R5 - Immutable observation

Transaction A shall persist at most one immutable observation per complete
external identity key plus envelope lineage. Management reads may expose only
observation id, non-secret selector metadata, and received time. They shall
omit sender token, raw sender, candidate body, and operational content.

### R6 - Mapping aggregate

`IdentityMappingV1` shall be frozen and closed with immutable mapping id,
external-key digest, target kind `INTERNAL_USER`, target user id, proposal
evidence digest, proposer id, status, version, timestamps, and applicable
confirmer/rejector/revoker/successor references.

Allowed transitions are:

```text
PROPOSED -> CONFIRMED | REJECTED
CONFIRMED -> REVOKED
```

Terminal records are immutable. Correction creates a successor proposal and,
when the successor is confirmed, atomically revokes the prior confirmed
mapping. At most one current confirmed mapping may exist for a complete key.

### R7 - Human authority order

Every propose, confirm, reject, revoke, correct, bind, replace, and privacy-
delete action shall:

1. verify the JWT cryptographically and use only its subject identity;
2. load the authoritative active user and reconstruct the principal from the
   stored current role;
3. run the action-specific permission with that reconstructed principal;
4. apply workspace scope and separation-of-duty checks;
5. inside the mutation unit of work, lock/reread the actor and rerun permission;
6. verify expected version, idempotency, lifecycle, and target eligibility;
7. atomically persist state and actor-bound audit.

The JWT role claim is never an authorization input. Missing/inactive actors,
subject mismatch, demotion, or permission drift refuses before mutation.

The permission registry shall add these exact actions and minimum stored roles:

| Action | Minimum role |
|---|---|
| `external_identity_mapping.read` | `operator` |
| `external_identity_mapping.propose` | `operator` |
| `external_identity_mapping.confirm` | `shift_supervisor` |
| `external_identity_mapping.reject` | `shift_supervisor` |
| `external_identity_mapping.revoke` | `shift_supervisor` |
| `external_identity_mapping.correct` | `shift_supervisor` |
| `conversation_route.bind` | `shift_supervisor` |
| `conversation_route.replace` | `shift_supervisor` |
| `external_identity_mapping.privacy_delete` | `responsible_manager` |

Higher roles inherit these actions only through the existing canonical role
ordering. No endpoint-local role comparison may restate that ordering.

### R8 - Two-human transient verification

Propose requires observation id, target user id, expected version,
idempotency key, and transient raw sender re-entry. Confirm requires the same
observation lineage and a fresh transient re-entry by a different human who is
neither proposer nor target user. Each action recomputes the complete R4 key
and discards the raw value before persistence. Correction repeats this
two-human flow. No hidden evidence viewer or provider lookup is required.

### R9 - Idempotency, CAS, and receipts

Every human command shall carry a closed action kind, idempotency key,
canonical payload digest, and expected aggregate version. Same key and digest
returns the prior sanitized receipt; same key with a different digest returns
an idempotency conflict. Write-time CAS and unique-current constraints shall
permit at most one incompatible confirmation, correction, or binding success.
All emitted receipts shall conform to `P4E-MAPPING-ACTION-OUTCOMES`.
`command_application_count` counts accepted commands, not physical database
rows; a compound correction may update lineage and current-state rows while
still constituting exactly one command application and one audit event.

## 5. Durable proposal admission and placement work

### R10 - Operations Ledger ownership

Operations Ledger shall be the Workspace-side physical persistence and
unit-of-work owner for admitted external proposals, observations, placement
work, mappings, bindings, placement decisions, idempotency records, and audit.
P4-C remains semantic owner of proposal lineage. The existing process-local
external-ingress repository shall be retired from production composition; no
second live proposal store may remain.

A migration shall provide matching SQLAlchemy tables and SQL migration DDL for
SQLite and PostgreSQL, including foreign keys, closed status checks,
unique-current constraints, idempotency uniqueness, immutable lineage, and
CAS versions. InMemory behavior shall be parity-tested against both SQL
backends.

### R11 - Two-transaction inbox protocol

After service-assertion verification, transaction A shall idempotently persist
the immutable Edge proposal, sender observation when present, and exactly one
pending placement-work item. Same proposal key and lineage returns the prior
admission; reused proposal/envelope/idempotency identity with different lineage
is a closed collision.

After A commits, Workspace API shall make one synchronous local processing
attempt. Transaction B shall lock or CAS-claim the work item, reread proposal
and lineage digests, revalidate mapping, binding, user, assignment, and target,
then atomically persist one decision and complete the item. A transient store
failure rolls B back and leaves the item pending. There is no cross-step
atomicity or exactly-once claim.

### R12 - Bounded retry and stale claim recovery

A work item shall have `PENDING`, `CLAIMED`, or `COMPLETE` state, attempt count,
claim token, claimed-at time, and version. Maximum local attempts are three.
A claim older than five minutes may be recovered only by CAS using the exact
proposal-lineage digest. Exhaustion produces terminal `REFUSED /
RETRY_EXHAUSTED`. Unknown claim state and proposal-lineage digest mismatch
produce terminal persisted `REFUSED` decisions with reasons
`UNKNOWN_CLAIM_STATE` and `LINEAGE_DIGEST_MISMATCH` respectively; each carries
`decision_id`, `decision_count=1`, and `work_complete=true` as required by the
placement matrix. No daemon, external queue, blind retry, or deployment is
introduced by this SPEC.

## 6. Route bindings and deterministic placement

### R13 - Route binding

`RouteBindingV1` shall bind one confirmed mapping id/version to one target
kind/id/version, creator, lifecycle, version, and successor lineage. At most
one current binding may exist per current confirmed mapping. Replacement shall
atomically revoke the old binding and create its successor. Multiple current
mappings or bindings are corruption and must never be priority-sorted.

`WORKSPACE` is an explicit positive binding to the configured single-workspace
manual-triage scope. `FALLBACK` is never a binding target; it is a system
terminal, non-privileged disposition.

### R14 - Target eligibility

- `WORKSPACE` requires exact equality with the injected workspace digest.
- `SHIFT` requires an existing shift that is neither closed nor frozen.
- `INCIDENT` requires an existing non-closed incident and an eligible parent
  shift.
- For SHIFT and INCIDENT, both binding actor and mapped user require active
  assignments to the target shift at bind time and route time.
- The mapped user must be active at confirm, bind, and route time.

Unsupported target kinds, free-form customer ids, candidate fields, provider
labels, or stale target versions cannot become target authority.

### R15 - Placement outcomes

Processing shall evaluate, in order: immutable proposal lineage; exactly one
current mapping; current mapped user; zero/one/multiple bindings; target and
assignment eligibility; decision idempotency. Results shall conform to
`P4E-IDENTITY-RESOLUTION-OUTCOMES` and
`P4E-CONVERSATION-PLACEMENT-OUTCOMES`.

Absence, legacy sender evidence, rejected/revoked mapping, no binding, or an
unsupported target yields a terminal `FALLBACK` with no actor, target id,
binding id, or conversation key. Ambiguity, stale versions, collision,
authority-store unavailability, or corrupt state yields `REFUSED` or leaves a
transient work item `RETRY_PENDING`; it shall not silently degrade to a
privileged route.

`decision_count` is exactly one for every persisted terminal `PLACED`,
`FALLBACK`, or `REFUSED` decision and zero for `RETRY_PENDING`; it does not
claim that fallback/refusal placed content into a target.

### R16 - Conversation key

Only positive `WORKSPACE`, `SHIFT`, or `INCIDENT` placement may carry a
conversation key. It shall be an opaque SHA-256 digest over a domain-separated,
length-prefixed tuple of mapping id/version, binding id/version, target
kind/id/version, and workspace digest. Revoke, correction, remap, or rebind
creates a new key. Historical decisions never move retroactively. The key
confers no identity, assignment, permission, approval, or truth authority.

## 7. API, dependency, and privacy boundaries

### R17 - Closed application operations

Workspace API shall expose private authenticated application operations for
observation list, mapping propose/confirm/reject/revoke/correct, binding
create/replace, privacy delete, and placement-work retry. Request models shall
forbid extra fields. Automatic placement accepts only the verified service
assertion and stored proposal identity; callers cannot supply mapping result,
actor id, target, binding, decision, or conversation key.

### R18 - Dependency direction

`identity-mapping` owns provider-neutral identity and mapping contracts and
imports no Workspace API type. `conversation-routing` owns provider-neutral
binding and placement contracts, consumes an identity read port, and never
mutates mappings. Operations Ledger owns persistence only. Workspace API is the
sole composition owner. Integration Edge may emit sender evidence but shall
not import either P4-E package. P4-D remains unchanged.

Dynamic discovery, filesystem scanning, provider SDK imports in P4-E packages,
and a second contract owner are forbidden. P4-E shall not call internal
`POST /messages` or create Message, Event, Task, CustomerRequest, Incident,
Report, Approval, or other operational truth from external content.

The pre-existing `packages/conversation-routing/customer-router/` and
`packages/conversation-routing/vessel-router/` directories remain
documentation-only scaffolds and are excluded from P4-E BUILD ownership. They
must receive no runtime code, dependency, configuration, schema, or composition
change. The P4-E identity-mapping boundary targets internal users only;
customer-contact identity authority remains deferred.

### R19 - Privacy, retention, and disclosure

Raw sender input is transient no-log data. Sender tokens are secret-adjacent
selectors and shall not appear in management lists, receipts, audit, logs, or
telemetry. Allowlisted telemetry is limited to outcome, closed reason, target
kind, latency bucket, retry count, and opaque correlation ids.

Observations without a mapping expire after 30 days. Rejected/revoked mapping
and binding records, action receipts, and placement receipts retain digest-only
lineage for 365 days. Retention age is measured from the persisted UTC
`created_at`, terminal-action time, or decision time applicable to that record,
using one injected UTC clock; production paths shall not call an ambient system
clock directly. Tests use a fixed clock and verify the exact boundary instant.

Privacy deletion is a governed
`external_identity_mapping.privacy_delete` command requiring at least the
fresh stored `responsible_manager` role, expected version, reason,
idempotency, and actor-bound audit. It removes optional display metadata and
all sender-token lookup material while preserving only immutable record ids,
closed outcome/reason, timestamps, and non-reversible lineage digests. Lookup
and routing then refuse; reappearance requires a new two-human mapping.
The operator-supplied deletion reason is a command input written only to the
restricted actor-bound audit record. It is deliberately excluded from the
sanitized `APPLIED` and `IDEMPOTENT_REPLAY` receipts to avoid disclosing
privacy-request content; those receipt shapes therefore continue to forbid
`reason`.

Sender-evidence and token key rings accept only the current key version and the
immediately previous version for a 24-hour dual-read window measured from the
persisted UTC activation time. Evidence declares its key id/version; verifiers
must not try arbitrary keys. A new token-key version derives a distinct key and
never aliases an old mapping. Linking versions requires the normal explicit
two-human correction flow. At window expiry, the previous secret is
cryptographically erased by deleting its wrapping-key reference and secret
material from the configured secret store and purging process caches; only a
non-secret key-id/version/destroyed-at audit record remains. Failure to erase
or purge fails the rotation closed and blocks retirement. Rotation is a
secret-authority operation, not a mapping action and not a P4-E management API
operation. Its failure is reported as a sanitized
`TOKEN_KEY_RETIREMENT_BLOCKED` secret-authority audit/readiness record, never as
a `P4E-MAPPING-ACTION-OUTCOMES` receipt. Storage overwrite is not claimed.

### R20 - Representation parity

Closed Python models, JSON Schemas, InMemory records, SQLAlchemy tables, and
migration DDL shall agree on fields, enums, nullability, uniqueness, version,
and lifecycle checks. Unknown fields and unknown enum values fail closed.
SQLite and disposable PostgreSQL conflict translation shall yield the same
domain outcome as InMemory.

### R21 - Live evidence boundary

BUILD is deterministic and must make zero provider or external network calls.
Any later claim that CVF governs a provider/agent action requires a separately
authorized real provider call and sanitized receipt. P4-E can close its local
identity/routing capability using deterministic and disposable-database
evidence only, provided the closure makes no provider-governance claim.

## 8. Acceptance criteria

- **AC-01:** All three matrices pass schema, registry, ownership-pin, positive
  corpus, deterministic one-fact mutation, and exact-file-set checks.
- **AC-02:** Sender-aware signature/token vectors cover every R1/R2 dimension;
  mutation of any dimension changes or invalidates the key. Legacy ingress
  reaches fallback without mapping lookup.
- **AC-03:** Raw sender/token negative scans cover models, SQL, receipts,
  audit, logs, telemetry, and HTTP responses.
- **AC-04:** Propose/confirm separation, target-self-confirm refusal, fresh-role
  permission, demotion/inactivity, transient re-entry mismatch, and correction
  successor tests pass with zero partial mutation.
- **AC-05:** Mapping lifecycle, unique-current, CAS, idempotent replay, key
  conflict, concurrent confirmation, and audit atomicity pass on InMemory,
  SQLite, and disposable PostgreSQL.
- **AC-06:** Transaction A proves immutable idempotent admission, collision
  refusal, exactly one work item, preserved Edge proposal id, and no regenerated
  identity.
- **AC-07:** Transaction B proves digest reread, current-authority revalidation,
  at-most-one decision, rollback-to-pending, bounded attempts, stale-claim CAS,
  and terminal exhaustion.
- **AC-08:** WORKSPACE/SHIFT/INCIDENT positive cases and every fallback,
  refusal, retry, ambiguity, stale, unsupported, user, assignment, and target
  case match the pinned matrices.
- **AC-09:** Conversation-key vectors are deterministic for one current tuple,
  change on remap/rebind/revoke/version change, and are absent from fallback or
  refusal.
- **AC-10:** JSON Schema, model, migration, SQLAlchemy, and all three backend
  representations pass two-way parity and rollback probes.
- **AC-11:** Dependency/import tests prove one-way ownership, sole Workspace
  composition, no P4-E provider SDK, no Integration Edge reverse import, and
  no internal Message admission call.
- **AC-12:** Private API tests prove verified JWT subject plus fresh stored role
  and the exact R7 action/role table are the sole human authority; demotion and
  endpoint-local role shortcuts fail closed, and all request models reject
  extras.
- **AC-13:** Fixed-clock tests prove the exact 30-day and 365-day boundaries;
  privacy deletion and the 24-hour two-version rotation window preserve
  digest-only lineage without raw sender disclosure or silent remapping, and
  erasure/purge failure blocks retirement.
- **AC-14:** Focused suites, full non-live regression, Project Knowledge,
  invariant, session, catalog, file-size, repository, diff, and workspace
  doctor gates pass with exact results recorded.
- **AC-15:** Independent reviewer recomputes the DESIGN and matrix digests,
  checks every R/AC mapping, samples at least one raw positive per outcome,
  runs all deterministic mutations, and reports findings/waivers explicitly.
- **AC-16:** Composition and negative-import tests prove
  `InMemoryExternalIngressRepository` is test-only, the process-local P4-C
  proposal repository is absent from production composition, and Operations
  Ledger is the sole live proposal/placement persistence owner.

### R-to-AC traceability

| Requirement | Acceptance coverage |
|---|---|
| R1 | AC-02, AC-03 |
| R2 | AC-02, AC-03, AC-13 |
| R3 | AC-02, AC-03, AC-10 |
| R4 | AC-02, AC-05 |
| R5 | AC-03, AC-06, AC-13 |
| R6 | AC-04, AC-05, AC-10 |
| R7 | AC-04, AC-05, AC-12 |
| R8 | AC-04 |
| R9 | AC-01, AC-05 |
| R10 | AC-06, AC-10, AC-11, AC-16 |
| R11 | AC-06, AC-07 |
| R12 | AC-07, AC-08 |
| R13 | AC-05, AC-08, AC-10 |
| R14 | AC-08, AC-12 |
| R15 | AC-01, AC-07, AC-08 |
| R16 | AC-09 |
| R17 | AC-11, AC-12 |
| R18 | AC-11, AC-16 |
| R19 | AC-03, AC-13 |
| R20 | AC-01, AC-10 |
| R21 | AC-14, AC-15 |

## 9. Work Order constraints

The future Work Order shall enumerate exact paths and split implementation into
bounded dependency order: contract/matrix consumers; package contracts;
persistence/migration; P4-C sender seam; Workspace API composition; tests and
evidence; then independent review. It shall use `WORKER_MUST_NOT_COMMIT`, name
one implementation worker and an independent reviewer, prohibit provider/live
effects, and stop on path expansion, dependency installation, matrix drift, or
unresolved SQL atomicity.

The Work Order must explicitly exclude both customer/vessel scaffold
directories named in R18 and must leave them documentation-only and unchanged.

## 10. Stop conditions

Stop on contract ambiguity, missing source authority, need for customer/vessel
authority, new external effect, credential or dependency installation, matrix
drift, inability to preserve transaction/CAS parity, third same-root repair
round, unexpected product test failure, scope expansion, or any request to
start BUILD before independent SPEC and Work Order review.

## 11. Disposition

`READY_FOR_INDEPENDENT_SPEC_REREVIEW`

WORK_ORDER, BUILD, provider/live execution, deployment, Phase 5, catalog schema
migration, XR1 repair, and external-repository absorption remain unauthorized.
