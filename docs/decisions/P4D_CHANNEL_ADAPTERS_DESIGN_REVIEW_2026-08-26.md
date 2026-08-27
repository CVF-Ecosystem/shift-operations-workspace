# Independent DESIGN Review — P4-D Channel Adapters

- Tranche: `P4D-CHANNEL-ADAPTERS-2026-08-26`
- Phase: `DESIGN`
- Risk ceiling: `R2`
- Reviewer role: `INDEPENDENT_DESIGN_REVIEWER`
- Review date: `2026-08-26`
- Findings: `P4D-DESIGN-REV-F1..F4 OPEN`
- Waivers: `NONE`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`

## Review boundary

This review compares the proposed DESIGN only with the accepted P4-D INTAKE,
roadmap P4-D, settled P4-C outbound contracts, current SDK port and service,
adapter skeletons, invariant-family standard, dependency direction and live-
evidence rule. It does not authorize or perform SPEC, WORK_ORDER, BUILD,
product or continuity edits, network/provider calls, credential use, install,
deployment, commit or push.

Reviewed DESIGN raw SHA-256:
`8f3bf342776e22c8b0879fce39c42a98d821193684600a1235cf78a9a00e5e67`.

## Accepted design decisions

The DESIGN correctly keeps P4-D outbound-only, preserves P4-C as the sole
receipt/state owner and leaves identity/conversation placement to P4-E. The
closed digest-only request contains no content, recipient handle, endpoint or
credential. Activation distinguishes `DEPLOYABLE` from `CONFORMANCE_ONLY`, so
vendor mocks cannot enter runtime composition.

Attempt accounting is conservatively sound: all validation precedes the
attempt boundary; the flag changes immediately before the sole transport call;
there is no automatic retry; and any exception or malformed result whose
effect cannot be proven is mapped to attempted `OUTCOME_UNKNOWN`. Generic HTTP
success produces at most `SENT_ACCEPTED`, never `DELIVERED`.

The separate `P4D-ADAPTER-RESULT-OUTCOMES` family is the correct ownership
choice. Adapter-local status/attempt facts must not displace the existing
`P4C-OUTBOUND-TERMINAL-OUTCOMES` receipt family. The legacy non-packaged
adapter protocol is also correctly rejected as a parallel contract owner.

## Findings

### P4D-DESIGN-REV-F1 — Trusted endpoint is not bound to the authorized business scope

The endpoint is fixed in trusted configuration, but the DESIGN does not bind
that configuration/adapter instance to the command's workspace, channel and
policy lineage. A globally injected adapter could therefore send every valid
P4-C command to one technically allowlisted endpoint without proving that the
endpoint is authorized for that command's business scope.

Add a closed pre-transport binding checked by Integration Edge or the trusted
composition layer before adapter invocation. It must bind the selected adapter
configuration to the allowed workspace/channel and policy lineage using exact
digest or signed-prerequisite references, fail closed on mismatch, and perform
no recipient resolution. P4-E remains the sole future owner of recipient and
conversation mapping.

Also state that digests are correlation/equality-bearing data, not encryption,
anonymization or automatic disclosure authority. Low-entropy digests can be
guessable; their egress still requires the explicit scope binding above.

### P4D-DESIGN-REV-F2 — Deployable composition root is unspecified

The DESIGN simultaneously forbids Integration Edge from importing a concrete
adapter and says runtime composition may inject one, but it does not identify
the layer allowed to import both sides. Without an explicit composition root,
BUILD can either violate dependency direction or introduce hidden plugin/
dynamic-import behavior outside the reviewed boundary.

Name the provider-neutral composition owner and import direction before SPEC.
The domain service and `channel-sdk` must remain independent of concrete
adapters; only the named bootstrap/composition layer may select a closed
adapter id, construct validated trusted configuration and inject the concrete
port. Unknown ids and unavailable configuration must retain the zero-attempt
fail-closed outcome. No filesystem, entry-point or reflection-based discovery
may be inferred unless separately designed and authorized.

### P4D-DESIGN-REV-F3 — HMAC preimage lacks destination audience binding

The v1 preimage binds method and normalized path but not the normalized HTTPS
authority or an equivalent configured endpoint/audience id. If key material is
ever reused across endpoints, a valid request could be replayed to another
host with the same path and verification contract.

Bind the normalized scheme/host/effective port, or a unique configured
endpoint audience digest, into the v1 preimage and scope each key id to that
audience. SPEC must make the choice canonical and cover cross-host, cross-port,
cross-path, key-id, timestamp and idempotency mutations. Sender evidence may
prove only signed-request construction; receiver replay enforcement remains an
external claim requiring separately authorized evidence.

### P4D-DESIGN-REV-F4 — DNS-rebinding policy lacks one enforceable transport seam

The DESIGN permits either binding transport to an authorized resolution or
independently checking the connected peer, but it does not require which facts
the transport exposes or prevent ambient proxy configuration from bypassing
the resolver/peer checks. This leaves the stated rebinding evidence
implementation-dependent and potentially untestable.

Choose one closed resolver/transport contract before SPEC. It must disable
ambient/environment proxies, prevent a second uncontrolled resolution, retain
the original hostname for TLS hostname/SNI verification, bind the approved IP
set to the connection, and expose the connected peer for independent checking
or prove equivalent pinning. Deterministic tests must mutate resolution between
validation and connection, substitute a disallowed peer, enable a proxy and
exercise IPv4/IPv6 mixed-answer cases; every case must fail before body or HMAC
material is disclosed to the wrong peer.

## Deterministic review evidence

- Accepted INTAKE SHA-256:
  `d51e578ae2b57d2f4ee95806683236d3b684de9690b48bba3bc5b636fcb7ce8b`.
- Current packaged port SHA-256:
  `0e50b46cc88d8a3d039d2f3002b9bcc90afc19528870590e61f4b0252eb8fe4b`.
- Current P4-C outbound service SHA-256:
  `3024d4c2661c7138d6e96b2a5ac22d456a1fbc629c450be65c41abe1288af2dd`.
- Current outbound schema SHA-256:
  `d7eaedac8d440c2eb2fb78f2c9d9e6a56f3924f6334710de385205c6ce6e5aca`.
- P4-C outbound matrix canonical SHA-256:
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
- Session-state guard: `PASS`.
- Invariant-family guard: `PASS`.
- Project staged set: zero.

No doctor or live call was run under the zero-network DESIGN-review boundary.
This review makes no provider delivery or CVF-governance-behavior claim.

## Disposition and next allowed move

`DESIGN_REVIEW_CHANGES_REQUIRED`.

Findings/waivers are `P4D-DESIGN-REV-F1..F4 OPEN` / `NONE`. Repair only the
DESIGN within these four findings, then return for bounded independent
rereview. SPEC and all later phases remain unauthorized. No network/provider
call, credential use, install, deployment, commit or push is authorized by
this review.

## Bounded F1-F4 rereview

Role transition: `REPAIR_WORKER -> INDEPENDENT_DESIGN_REVIEWER`.

The repaired DESIGN was rereviewed only against
`P4D-DESIGN-REV-F1..F4`. Its independently recomputed SHA-256 is
`1f9288b6d4158bc815347050bf76e40b2b5089bcc7ee05949061ed9860ab1a22`,
matching the authorized repair target.

- `P4D-DESIGN-REV-F1 CLOSED`: `AdapterScopeBindingV1` now binds one exact
  workspace/channel/policy/prerequisite tuple at the trusted composition
  boundary, fails closed before adapter invocation, and explicitly treats
  digests as correlation-bearing data rather than anonymization or disclosure
  authority.
- `P4D-DESIGN-REV-F2 CLOSED`: `integration_edge.main:create_app` is the sole
  named composition owner. It selects the closed `generic-webhook` id,
  constructs trusted configuration and injects the port; domain modules remain
  concrete-adapter-independent, while dynamic discovery and unknown adapter
  activation are prohibited.
- `P4D-DESIGN-REV-F3 CLOSED`: the HMAC v1 preimage now binds a canonical HTTPS
  endpoint audience, and key resolution is scoped to `(key_id,
  audience_digest)`. Required SPEC mutations cover host, port, path, key,
  timestamp and idempotency, while receiver replay enforcement remains outside
  the sender claim.
- `P4D-DESIGN-REV-F4 CLOSED`: the closed `AuthorizedEndpointV1` and
  `ResolvedHttpsTransportPort` seam disables ambient proxies, prevents a
  second uncontrolled resolution, preserves hostname-based TLS/SNI checks,
  restricts connection IPs, exposes peer/TLS facts, and requires rebinding,
  peer, proxy and mixed-address failures before body or HMAC disclosure.

Bounded deterministic guards after rereview:

- session-state guard: `PASS`;
- invariant-family guard: `PASS`;
- scoped diff whitespace guard: `PASS`;
- project staged set: zero.

Findings: `NONE OPEN` (`P4D-DESIGN-REV-F1..F4 CLOSED`). Waivers: `NONE`.

### Rereview disposition

`DESIGN_REVIEW_PASS`.

Return ownership to the `ORCHESTRATOR`. The next allowed move is an explicit
transition to SPEC; this rereview does not itself authorize SPEC, BUILD, live
provider evidence, deployment, commit or push. No DESIGN, product source,
continuity or handoff artifact was changed by the reviewer.
