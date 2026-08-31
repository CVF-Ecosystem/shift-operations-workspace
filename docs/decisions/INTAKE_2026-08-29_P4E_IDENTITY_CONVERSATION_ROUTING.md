# INTAKE — P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-08-29`
- Phase: `INTAKE`
- Risk: `R2`
- Author: `INTAKE_AUTHOR`
- Authority: operator requested fresh P4-E INTAKE after P4-D commit/push
- Predecessor: `P4D-CHANNEL-ADAPTERS-2026-08-26`, `FREEZE / CLOSED_BOUNDED`,
  committed and pushed at `a8e2ad8199d700a238d7d74bdbf85329446228de`
- BUILD authority: `NOT GRANTED`

## Intent

Open roadmap P4-E as one dependency-ordered decision tranche: first map an
external channel identity to an eligible internal user or customer-contact
reference through explicit human confirmation; then place an actor-neutral
external conversation proposal into an allowed workspace, shift, vessel,
customer, incident or fallback target without turning provider assertions,
mapping, or placement into authenticated authority or operational truth.

## Current implementation truth

- `packages/identity-mapping` and `packages/conversation-routing` are README-
  only stubs with no runtime contract, persistence, tests or enforcement.
- P4-C authenticates and preserves external envelopes, then creates an
  actor-neutral `UNTRUSTED_EXTERNAL / RAW` proposal. Its `actor_id`,
  `assignment_id`, `approval_id` and `conversation_id` are fixed to `None`,
  and `confirmed` is fixed to `False`.
- P4-C `integration_edge.routing.RoutingService` only performs the signed,
  idempotent handoff of that proposal to Workspace API. Its name does not
  mean P4-E conversation placement and it must not become a second owner of
  identity or placement decisions.
- That handoff currently places P4-C `external_message_id` into the proposal's
  `external_id`; it carries no separately verified external-sender identity.
  Candidate sender/profile fields remain untrusted content. P4-E therefore
  has no safe sender key to map until DESIGN bounds a provenance-bearing
  sender-evidence contract or an explicitly authorized minimal amendment.
- Workspace API persists `ExternalIngressProposal` separately from the
  operations ledger. The boundary is actor-neutral and has no route that may
  write a canonical `Message`, confirmed event, task, customer request,
  incident, approval or other operational fact.
- Internal `POST /messages` is an authenticated internal-user command. It
  derives `sender_id` and `source=INTERNAL` server-side and explicitly forbids
  external provider payloads. P4-E must not reuse it as an ingress shortcut.
- Runtime internal-user authority remains the Workspace API `users` boundary;
  active shift assignment remains separately authoritative. There is no
  implemented customer-contact, vessel, conversation, external-identity or
  placement model whose existence may be assumed.

## Risk classification

P4-E is `R2`: it handles external identifiers and contact data, binds
untrusted senders to internal subjects, and influences which operational
scope receives an external proposal. A bad match or route can cross identity,
permission, assignment, privacy and domain-lock boundaries. This INTAKE is
documentation/continuity only and authorizes no provider/network call,
credential use, installation, migration, deployment, product edit, commit or
push.

## Proposed bounded scope for DESIGN

1. Closed external-identity, mapping-proposal, confirmation/rejection,
   revocation/correction and audit contracts, with one canonical owner and
   deterministic lifecycle semantics.
2. Human-confirmed linkage only to an eligible internal-user reference or an
   explicitly designed customer-contact reference. Linkage never creates a
   user, role, permission, assignment, approval or authenticated principal.
3. Closed conversation-placement proposal and disposition contracts for the
   roadmap target vocabulary: workspace, shift, vessel, customer, incident
   and fallback, with deterministic precedence and ambiguity handling.
4. A dependency rule under which identity-dependent placement consumes a
   valid current mapping result; unknown, conflicting, revoked or stale
   identity remains actor-neutral and may reach only a deliberately bounded
   fallback/quarantine/manual-triage outcome.
5. Minimal reviewed seams from the existing P4-C actor-neutral proposal into
   P4-E and, if needed, from P4-E to a non-truth Workspace API queue. P4-C
   retains envelope, replay, quarantine and ingress-receipt ownership.
6. Durable or explicitly bounded-local repositories, idempotency, optimistic
   concurrency, retention/deletion, evidence and audit needed to make
   confirmation, revocation and placement independently reviewable.
7. Deterministic contract, lifecycle, dependency, authorization, privacy and
   adversarial evidence. Any database or application composition amendment
   must be separately bounded by DESIGN/SPEC/WORK_ORDER.

## Explicitly out of scope

- automatic identity confirmation from provider sender ids, names, phone
  numbers, profile data, message text, AI output or prior chat history;
- treating a mapped internal-user reference as login authentication, a JWT
  principal, current role, permission, active assignment or approval;
- direct creation or mutation of canonical `Message` or any confirmed,
  corrected, approved, closed or frozen operational record;
- autonomous semantic/LLM routing, prompt execution, retrieval/RAG, learning,
  or allowing external text to supply route authority;
- real Zalo/WhatsApp/vendor identity lookup, contact sync, credentials, SDKs,
  subscriptions, live messages, vendor certification or production claims;
- reopening P4-C/P4-D verification, raw evidence, replay, quarantine,
  outbound delivery, HMAC, egress or receipt ownership except for a minimal
  amendment that later phases explicitly justify and authorize;
- admin user provisioning, authentication refresh/revocation, tenant
  isolation, production database/queue, deployment, commit or push;
- mock or deterministic output as proof that CVF governs AI/agent behavior.

## Decisions required before DESIGN can pass

1. Define the stable external-identity key and scope. It must bind the
   provider/channel/endpoint/workspace dimensions actually available from the
   trusted P4-C envelope rather than accept an unscoped sender string, and it
   must specify normalization, digest/minimization and collision handling.
2. Select the canonical owner and persistence boundary for external
   identities, customer contacts, mapping proposals and confirmations.
   Existing Workspace API users remain reference authority; DESIGN must not
   duplicate user credentials, roles, active status or assignment truth.
3. Define who may propose, confirm, reject, revoke and correct a mapping, the
   permission and scope checks for each action, separation-of-duty needs,
   version/TOCTOU protection and atomic audit behavior. Self-asserted provider
   identity is evidence only, never authority.
4. Define a closed mapping lifecycle and terminal outcomes for unknown,
   proposed, confirmed, rejected, conflicted, revoked, stale and unavailable
   dependencies. Confirmation and revocation must be idempotent, replay-safe
   and independently attributable.
5. Define what a “conversation” is, its canonical id and owner, whether P4-E
   creates a placement record or only a placement proposal, and how repeated
   external messages join or split a conversation without trusting provider
   threading claims.
6. Define target registries and existence/eligibility checks for workspace,
   shift, vessel, customer and incident. Current source lacks some of these
   canonical models: `CustomerRequest.customer_id` is not a customer-contact
   authority, and no vessel master/aggregate exists. DESIGN must explicitly
   defer unsupported target kinds or separately propose their authoritative
   sources; it must not invent authority from free-form ids.
7. Define deterministic route evidence, precedence and ambiguity rules. A
   route must be bound to the current mapping/version and target/version;
   zero or multiple eligible targets, stale evidence, closed/frozen targets,
   missing assignment or unavailable dependencies must fail closed to an
   explicit non-truth disposition.
8. Define the exact relationship to P4-C's signed handoff and Workspace API's
   actor-neutral proposal store. P4-E may annotate/link by immutable refs but
   may not overwrite raw evidence, retroactively alter P4-C receipts or bypass
   authenticated internal command services.
9. Close privacy and lifecycle boundaries for external identifiers/contact
   data: classification, minimization, encryption, retention, correction,
   deletion/tombstone, audit redaction and secret/PII-safe telemetry.
10. Apply `docs/cvf/INVARIANT_FAMILY_STANDARD.md` before SPEC. Mapping and
    placement lifecycles appear to trigger shared outcome/model, controlled-
    field, counter and multi-surface families; register the required family or
    families and bind canonical digests rather than copying rules into prose.
11. Any test, roadmap closure, release gate, demo proof or public claim that
    asserts CVF governance behavior—including risk, approval, phase gates,
    DLP, bypass detection, output validation, provider routing or audit-trail
    updates—requires a separately authorized real provider API call with a
    sanitized request/response evidence artifact. INTAKE authorizes no call;
    mocks may prove only deterministic structure and local contracts.

## Acceptance direction

An accepted DESIGN must make identity mapping and conversation placement
replaceable, dependency-directed components with one owner per contract and
no route around the existing trust boundaries. Every positive mapping is
human-confirmed, scope-bound, versioned, revocable/correctable and audited;
every placement is reproducible from admitted evidence, current mapping and
current target eligibility. Unknown, ambiguous, conflicting or stale input
must remain actor-neutral and non-authoritative. No accepted result alone may
authenticate a user, grant permission/assignment/approval, or persist
operational truth.

## Initial disposition

`READY_FOR_INDEPENDENT_INTAKE_REVIEW`.

DESIGN, SPEC, WORK_ORDER, BUILD, product/database changes, provider/network
calls, credentials, installation, deployment, commit and push remain
unauthorized.
