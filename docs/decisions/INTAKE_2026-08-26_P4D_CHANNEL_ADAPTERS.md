# INTAKE — P4-D Channel Adapters

- Tranche: `P4D-CHANNEL-ADAPTERS-2026-08-26`
- Phase: `INTAKE`
- Risk: `R2`
- Author: `INTAKE_AUTHOR`
- Authority: operator requested the roadmap-next move after P4-C reached
  `FREEZE / CLOSED_BOUNDED`
- Predecessor: `P4C-INTEGRATION-EDGE-2026-08-23`, independently closed
- BUILD authority: `NOT GRANTED`

## Intent

Open the roadmap P4-D tranche with the smallest useful channel-adapter
boundary: one generic webhook implementation behind the existing
`OutboundAdapterPort`, plus deterministic Zalo and WhatsApp conformance mocks.
The tranche must not reopen P4-C state mechanics or absorb P4-E identity and
conversation routing.

## Current implementation truth

- `packages/channel-sdk` exposes the provider-neutral `OutboundAdapterPort`:
  one `deliver(command, idempotency_key)` operation and an
  `evidence_eligible` marker.
- P4-C `OutboundService` owns authorization, prerequisites, rate limiting,
  terminal receipt emission and replay-safe persistence around that port.
- The current consumer admits only adapters whose `evidence_eligible` marker
  is exactly `False`; all other values fail closed as `ADAPTER_UNAVAILABLE`.
  Once admitted, every adapter return or exception is counted as one delivery
  attempt. The current mapping result cannot distinguish a pre-transport
  refusal from post-attempt ambiguity. A deployable adapter therefore requires
  a minimal reviewed contract amendment; implementing the port alone is not
  sufficient for runtime activation or exact attempt accounting.
- `packages/channel-adapters` contains only README skeletons. There is no
  concrete or deployable adapter.
- The existing generic ingress route belongs to the P4-C edge boundary. P4-D
  must not duplicate its verification, raw-evidence, dedupe or quarantine
  ownership.
- Zalo and WhatsApp explicitly remain mock/conformance skeletons pending
  official credentials and API approval.

## Risk classification

P4-D is `R2` because a deployable outbound transport can create external
effects and later handle credentials. This INTAKE is documentation-only and
uses no network, provider, credential, SDK install, deployment, commit or push.

## Proposed bounded scope for DESIGN

1. A generic outbound webhook adapter implementing an amended-compatible
   `OutboundAdapterPort`, with deterministic request projection, bounded
   timeout/error classification and idempotency-key forwarding.
2. An injected transport seam so deterministic tests never require a network
   call and secrets are not stored in commands, receipts or fixtures.
3. Zalo and WhatsApp conformance mocks that exercise the same port/result
   contract without vendor SDKs, credentials or claims of live delivery.
4. A minimal `channel-sdk`/P4-C contract amendment defining deployable versus
   conformance eligibility and an exact physical-attempt signal in the closed
   adapter result vocabulary. Adapter code must not issue P4-C receipts or
   write edge state itself.
5. Focused contract, unit and dependency-boundary evidence; no production or
   governance claim may be derived from a mock.

## Explicitly out of scope

- real Zalo or WhatsApp API calls, credentials, subscriptions, templates,
  webhooks, vendor certification or SDK installation;
- production secrets, credential refresh, deployment, managed queues,
  production readiness, commit or push;
- P4-E identity mapping, conversation routing or provider-sender authority;
- changes to P4-C authentication, rate limits, persistence, receipts,
  quarantine, ingress processing or service assertions unless DESIGN proves a
  minimal contract amendment is unavoidable and obtains fresh authority;
- retries that can duplicate an ambiguous external effect, exactly-once
  delivery claims, or treating an HTTP success as end-recipient delivery;
- mock output as evidence that CVF governs AI or agent behavior.

## Decisions required before DESIGN can pass

1. Confirm that roadmap “generic webhook” means the outbound adapter behind
   P4-C's existing port; the P4-C generic ingress route remains unchanged.
2. Define the minimum command fields exposed to an adapter and a bounded
   `channel-sdk`/P4-C amendment for deployable-versus-conformance eligibility,
   exact physical-attempt reporting and mapping of transport responses/errors
   to existing P4-C terminal outcomes. P4-C remains the sole receipt/state
   owner; unavailable adapters still fail closed and ambiguous attempts never
   trigger blind retry. This deployable path is selected over a
   library/conformance-only tranche because the latter would not deliver the
   roadmap's generic webhook capability.
3. Keep destination authority in injected trusted configuration, never in the
   outbound command. DESIGN must close scheme, host/port allowlisting,
   redirects, DNS resolution and private/link-local/loopback address handling,
   request/response size, timeout and secret-free telemetry before any
   transport call. The injected test transport must not weaken that production
   configuration contract.
4. Retain the skeleton's HMAC-signed contract. DESIGN must define injected key
   authority, version and key id, canonical signed bytes, timestamp/replay
   window and secret-free observability. Signing keys must never enter source,
   commands, receipts or fixtures.
5. Apply `docs/cvf/INVARIANT_FAMILY_STANDARD.md` before SPEC. The shared
   result vocabulary and outcome-controlled fields appear to trigger an
   invariant-family check; DESIGN/SPEC must decide whether to extend the
   existing P4-C outbound family or register a separate adapter family.
6. Bound evidence precisely. Deterministic mock/conformance evidence may prove
   interface shape and mapping only. Any governance-behavior claim requires a
   separately authorized real provider API call and sanitized receipt.

## Acceptance direction

The generic adapter should be replaceable without changing Integration Edge
business/state logic beyond the minimal eligibility/attempt-accounting
contract amendment above. One call to the adapter represents at most one
physical transport attempt. Adapter-reported pre-transport refusals remain
zero-attempt P4-C outcomes; ambiguous post-attempt results remain
terminal/unknown and must not trigger blind retry. The endpoint is selected
only from closed trusted egress configuration and every outbound request uses
the reviewed HMAC contract. Zalo/WhatsApp mocks must be visibly non-production
and must never be mistaken for live delivery evidence.

## Initial disposition

`READY_FOR_INDEPENDENT_INTAKE_REVIEW`.

DESIGN, SPEC, WORK_ORDER, BUILD, provider/network calls, credentials, install,
deployment, commit and push remain unauthorized.
