# INTAKE — P4-C Integration Edge

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `INTAKE`
- Risk: `R2`
- Author: `INTAKE_AUTHOR`
- Authority: operator requested continuation with the next roadmap item after
  local `main` and GitHub `origin/main` were verified equal at
  `0b89016df8483a4904d2c64b1a6560ccbc6b27ae`
- Predecessor: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`,
  `FREEZE / CLOSED_BOUNDED`
- BUILD authority: `NOT GRANTED`

## Intent

Open the roadmap-next P4-C tranche and establish the decision boundary for a
provider-neutral Integration Edge that receives untrusted external channel
traffic without allowing provider payloads to become business truth.

The target capability named by the roadmap is the complete edge foundation:
raw-payload preservation, quarantine, rate limiting, bounded routing and
outbound delivery mechanics. DESIGN must preserve the later roadmap ownership
of concrete channel adapters (P4-D) and identity mapping/conversation routing
(P4-E).

## Current implementation truth

The existing `apps/integration-edge` is a partial scaffold:

- `POST /webhooks/generic` reads request bytes, resolves a shared secret,
  verifies an unversioned SHA-256 HMAC and rejects duplicate or missing
  `X-Message-Id` values through a process-local set;
- non-development secret resolution fails closed, while development may use
  the public placeholder `replace-me`;
- accepted JSON is returned to the caller as `raw_payload`; it is not durably
  preserved by the edge and is not handed to a canonical-message boundary;
- malformed signed JSON is parsed only after the message id is marked seen, so
  the current ordering can consume a dedupe key without producing a durable
  accepted or quarantined outcome;
- dedupe state is process-local and has no namespace, retention, reservation,
  commit/release, restart or concurrent-worker contract;
- `raw_payload`, `quarantine`, `rate_limit`, `routing`, `outbound` and `health`
  directories are README-only or empty scaffolds;
- the edge has no authenticated service-to-service handoff to
  `workspace-api`, no durable receipt/audit boundary and no attachment
  validation or scan integration;
- `docs/channels/CANONICAL_MESSAGE.md` and the channel adapter contract are
  directional stubs, not testable closed contracts;
- internal `POST /messages` deliberately sets database `raw_payload` to null
  and does not accept provider payloads. It is not an external-ingress bypass
  or an implementation of P4-C.

## Risk classification

P4-C is `R2` because it governs a public/DMZ ingress boundary, untrusted raw
content, signature and replay controls, retention/quarantine behavior, service
routing and eventual outbound external effects. INTAKE itself performs no
external call, credential use, deployment, database migration, commit or push.

## In scope for DESIGN consideration

- an exact raw-envelope contract over the original bytes and bounded safe
  metadata, with explicit owner, classification, retention and digest rules;
- versioned verification rules, replay/dedupe identity and deterministic
  reservation/finalization semantics across malformed, refused, quarantined,
  accepted and retryable outcomes;
- rate-limit identities, scopes, budgets, fail-closed behavior and sanitized
  refusal receipts;
- a closed canonical-message candidate contract that never treats provider
  sender, source, timestamps, text or attachments as authority;
- quarantine ownership, closed reason vocabulary, retention, acknowledgment,
  release/delete authority and unavailable-sink behavior;
- attachment metadata/type/size/hash validation and a scan/quarantine seam,
  without claiming a production malware-scanning service;
- service-authenticated, idempotent routing to an allowed downstream ingress
  seam without direct writes of confirmed operational truth;
- provider-neutral outbound command/receipt state mechanics that preserve the
  required permission/approval/audit prerequisites while leaving concrete
  provider adapters to P4-D;
- deterministic contracts, migration strategy if durability is selected,
  tests, receipts, observability and rollback boundaries;
- applicability of `docs/cvf/INVARIANT_FAMILY_STANDARD.md` before SPEC,
  especially shared terminal receipts, exact counters and schema/model parity.

## Out of scope

- concrete Zalo, WhatsApp, SMS, email or customer-portal provider adapters;
- production provider credentials, SDK installation, subscription setup or
  vendor certification;
- user/channel identity mapping and conversation routing owned by P4-E;
- allowing external payloads to call internal `POST /messages` directly or to
  write confirmed/corrected/frozen business truth;
- AI prompt construction, retrieval/RAG, autonomous learning or treating
  external text as system instructions;
- production deployment, managed queues/databases, HA, load certification,
  commit, push or roadmap closure during INTAKE;
- mock output as evidence that CVF governs AI or agent behavior.

## Decisions required before DESIGN can pass

1. Select the durable owner and transaction boundary for raw envelopes,
   dedupe reservations, quarantine records and sanitized receipts.
2. Define exact processing order and terminal grammar for verification,
   size/content validation, raw preservation, dedupe, rate limiting,
   attachment checks, canonicalization, quarantine and routing.
3. Resolve whether raw bytes are persisted before or after authenticity
   verification without either losing forensic evidence or storing unbounded
   attacker-controlled content.
4. Define the service-authenticated downstream ingress contract and prove it
   cannot bypass identity, permission, assignment, domain-lock, approval,
   audit or confirmation controls.
5. Define retry/idempotency behavior for ambiguous downstream and outbound
   outcomes; no exactly-once claim may be inferred from a process-local set.
6. Separate P4-C provider-neutral outbound mechanics from P4-D concrete
   adapters and P4-E identity/conversation ownership.
7. Decide the minimum live evidence needed at REVIEW/FREEZE. Any test,
   roadmap closure, release gate, demo proof or public claim asserting CVF
   governance behavior — including risk classification, approval flow, phase
   gates, DLP filtering, bypass detection, output validation, provider routing
   or audit-trail updates — requires a separately authorized real provider API
   call with its sanitized request/response recorded in the evidence artifact.
   Mock or static evidence is insufficient. No such call is authorized during
   INTAKE.

## Acceptance direction

DESIGN should make every externally controlled field non-authoritative,
preserve exact lineage from raw bytes to a canonical candidate, fail closed on
invalid signature, replay, oversized/malformed input, exhausted rate budget,
unsafe attachment, unavailable required quarantine or unauthorized routing,
and emit only sanitized public responses and receipts. Refusal and quarantine
paths must not create operational truth or accidentally consume an identifier
without a recoverable terminal record.

The edge must remain independently replaceable: channel/provider-specific
logic lives behind contracts, while core workflow and the Operations Ledger do
not import provider implementations.

## Initial disposition

`READY_FOR_INDEPENDENT_INTAKE_REVIEW`.

DESIGN, SPEC, WORK_ORDER, BUILD, provider/network calls, credentials,
deployment, commit and push remain unauthorized.
