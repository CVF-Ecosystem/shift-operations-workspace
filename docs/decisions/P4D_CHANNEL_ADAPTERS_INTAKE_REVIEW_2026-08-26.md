# Independent INTAKE Review — P4-D Channel Adapters

- Tranche: `P4D-CHANNEL-ADAPTERS-2026-08-26`
- Phase: `INTAKE`
- Risk ceiling: `R2`
- Reviewer role: `INDEPENDENT_INTAKE_REVIEWER`
- Review date: `2026-08-26`
- Findings: `P4D-INTAKE-REV-F1..F3 OPEN`
- Waivers: `NONE`
- Disposition: `INTAKE_REVIEW_CHANGES_REQUIRED`

## Review boundary

This review compares only the P4-D INTAKE with roadmap P4-D, settled P4-C
closure, the current `channel-sdk` port, Integration Edge outbound service,
channel-adapter skeletons, the invariant-family standard, current continuity
and the live-evidence rule. It does not authorize or perform DESIGN, SPEC,
WORK_ORDER, BUILD, product or continuity edits, provider/network calls,
credential use, installation, deployment, commit or push.

Reviewed INTAKE raw SHA-256:
`51d318f89abf8730bd5897b94f6f182100679f1e7f3c023b70196e4da809b8cf`.

## Accepted direction

The selected business slice matches roadmap P4-D: generic webhook plus visibly
non-production Zalo/WhatsApp mocks. The INTAKE correctly preserves P4-C ingress,
receipt/state and quarantine ownership, excludes P4-E identity/conversation
routing, forbids blind retry after ambiguity, distinguishes acceptance from
end-recipient delivery, and prevents mock evidence from proving live or CVF-
governance behavior.

The invariant-family applicability direction is also correct. A shared result
vocabulary with outcome-controlled fields and exact attempt counts triggers
the mandatory R2 family analysis before SPEC; DESIGN/SPEC must bind either an
approved extension of `P4C-OUTBOUND-TERMINAL-OUTCOMES` or a separate adapter
family by canonical digest.

## Findings

### P4D-INTAKE-REV-F1 — Current P4-C activation and attempt-accounting blockers are not stated

The INTAKE says P4-D can implement the existing `OutboundAdapterPort`, but the
current consumer admits only an adapter whose `evidence_eligible` value is
exactly `False`; every other concrete adapter is returned as
`ADAPTER_UNAVAILABLE`. After any admitted adapter invocation, the service also
records one delivery attempt for every returned status or exception. The
mapping-only port cannot distinguish an adapter-side refusal before transport
from an ambiguous result after a physical attempt.

This conflicts with the proposed possibility of runtime registration and the
acceptance direction that pre-transport refusals remain zero-attempt outcomes.
Repair the current-truth and decision sections so DESIGN must choose explicitly
between:

1. a library/conformance-only P4-D boundary that is not runtime-registered; or
2. a minimal, separately bounded `channel-sdk`/P4-C contract amendment that
   defines production-vs-conformance eligibility and an independently
   verifiable exact physical-attempt signal/result grammar.

The repair must preserve current fail-closed unavailable-adapter behavior,
the P4-C receipt owner, exact terminal counters and no-blind-retry rule.

Evidence:

- `packages/channel-sdk/src/channel_sdk/ports.py` SHA-256
  `0e50b46cc88d8a3d039d2f3002b9bcc90afc19528870590e61f4b0252eb8fe4b`;
- `apps/integration-edge/src/integration_edge/outbound/service.py` SHA-256
  `3024d4c2661c7138d6e96b2a5ac22d456a1fbc629c450be65c41abe1288af2dd`.

### P4D-INTAKE-REV-F2 — Generic-webhook egress authority is under-bounded

A generic outbound webhook creates an SSRF and data-egress boundary. The
INTAKE keeps secrets out of commands but does not explicitly keep the
destination itself out of untrusted/runtime command data or require closed
egress policy before transport.

Add a DESIGN decision requiring endpoint authority from injected trusted
configuration, never from the outbound command. The decision must bound at
least scheme, host/port allowlisting, redirect behavior, DNS/private-address
handling, request/response size, timeout and safe telemetry. Tests may use the
injected transport seam, but no mock may weaken the production configuration
contract.

### P4D-INTAKE-REV-F3 — The generic-webhook HMAC contract is omitted

The existing generic-webhook skeleton defines the integration as HMAC-signed,
while the proposed scope mentions deterministic request projection and
idempotency forwarding but no outbound authentication/signing contract.
Leaving this unresolved makes the INTAKE inconsistent with its current
repository boundary.

Add an explicit pre-DESIGN decision: either retain the HMAC-signed skeleton and
define injected key authority, version/key id, canonical signed bytes,
timestamp/replay window and secret-free observability, or explicitly propose a
reviewed skeleton/claim-boundary change. Secrets must never enter source,
commands, receipts or fixtures. The current skeleton SHA-256 is
`7dc4eb4c1ff74294d6fee18f503943c085f75d4ff13e061b18b9b9a41f0f83aa`.

## Deterministic review evidence

- Roadmap P4-D remains unchecked and names generic webhook plus mock
  Zalo/WhatsApp.
- P4-C remains `FREEZE / CLOSED_BOUNDED`; its claim excludes deployable
  adapters and provider sends.
- Canonical continuity, bootstrap, mirror and P4-D handoff agree on INTAKE,
  active reviewer and next move.
- Session-state guard: `PASS`.
- Invariant-family guard: `PASS`.
- Core offline HEAD and local `origin/main` both equal
  `9c01832930226f2f770eafa346e01279160f22cb`; Core is clean.
- Project staged set: zero.

The network-capable doctor was not rerun because this INTAKE review has an
explicit zero-network boundary; the retained doctor receipt is not presented
as fresh evidence. No real provider call was authorized or needed because
this review makes no CVF-governance-behavior or live-delivery claim.

## Disposition and next allowed move

`INTAKE_REVIEW_CHANGES_REQUIRED`.

Findings/waivers are `P4D-INTAKE-REV-F1..F3 OPEN` / `NONE`. Repair only the
INTAKE document within these three findings, then return it for bounded
independent rereview. DESIGN and all later phases remain unauthorized. No
provider/network call, credential use, install, deployment, commit or push is
allowed by this review.

## Bounded F1-F3 rereview

- Repaired INTAKE SHA-256:
  `d51e578ae2b57d2f4ee95806683236d3b684de9690b48bba3bc5b636fcb7ce8b`
- Findings: `NONE`
- Waivers: `NONE`
- Disposition: `INTAKE_REVIEW_PASS`

### Finding closure

`P4D-INTAKE-REV-F1` is `CLOSED`. Current truth now records both activation
blockers exactly: the consumer admits only `evidence_eligible == False`, and
the mapping result cannot distinguish pre-transport refusal from
post-attempt ambiguity. The INTAKE selects the roadmap-capable deployable
route and requires a minimal reviewed `channel-sdk`/P4-C amendment for
deployable-versus-conformance eligibility, exact physical-attempt reporting
and closed mapping to P4-C terminal outcomes. P4-C retains sole receipt/state
ownership, unavailable adapters remain fail-closed, and ambiguous attempts
remain terminal without blind retry.

`P4D-INTAKE-REV-F2` is `CLOSED`. Endpoint authority is now restricted to
injected trusted configuration and forbidden from the outbound command.
DESIGN must close scheme, host/port allowlisting, redirects, DNS and private/
link-local/loopback handling, request/response bounds, timeout and secret-free
telemetry before transport. The injected test seam cannot weaken that
production configuration contract.

`P4D-INTAKE-REV-F3` is `CLOSED`. The INTAKE explicitly retains the generic-
webhook skeleton's HMAC contract and routes injected key authority, version/
key id, canonical signed bytes, timestamp/replay window and secret-free
observability into DESIGN. Signing keys remain forbidden from source,
commands, receipts and fixtures.

### Bounded evidence and disposition

The repaired text preserves P4-C, P4-E, mock/live-evidence and invariant-
family boundaries. Session-state and invariant-family guards passed; bounded
`git diff --check` passed and the staged set is zero. No new finding or waiver
was identified.

`INTAKE_REVIEW_PASS`. Findings/waivers are `NONE/NONE`. Return to
`ORCHESTRATOR`; DESIGN may open only through an explicit phase transition and
must resolve the decisions recorded by the accepted INTAKE. This rereview
authorizes no SPEC, WORK_ORDER, BUILD, network/provider call, credential use,
install, deployment, commit or push.
