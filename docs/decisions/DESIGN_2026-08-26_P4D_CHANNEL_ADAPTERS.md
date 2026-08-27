# DESIGN — P4-D Channel Adapters

- Tranche: `P4D-CHANNEL-ADAPTERS-2026-08-26`
- Phase: `DESIGN`
- Risk: `R2`
- Author: `DESIGN_AUTHOR`
- Accepted predecessor: P4-D INTAKE with `INTAKE_REVIEW_PASS`
- BUILD authority: `NOT GRANTED`

## 1. Design objective

Deliver the smallest concrete P4-D boundary that is useful without absorbing
P4-E: a deployable generic outbound webhook adapter over the existing
digest-only P4-C outbound command, plus deterministic non-production Zalo and
WhatsApp conformance mocks.

The generic webhook emits an integration event, not a human-channel message.
It never resolves a provider recipient, fetches message content, or claims
end-recipient delivery. Those capabilities require later identity/routing and
data-projection authority.

## 2. Ownership and dependency direction

The dependency direction remains:

1. `channel-sdk` owns provider-neutral adapter request/result models and the
   narrow outbound adapter port.
2. `channel-adapters` owns generic-webhook implementation and Zalo/WhatsApp
   conformance mocks.
3. `integration-edge` owns authorization, prerequisites, rate limiting,
   adapter activation, terminal receipt/state persistence and no-blind-retry.
4. Application/core and P4-E remain the owners of operational truth,
   recipient identity and conversation placement.

Concrete adapters may import `channel-sdk`. `channel-sdk` and Integration Edge
domain modules must not import concrete adapters. Runtime composition may
inject one selected adapter, but no provider implementation is registered by
domain code.

The sole composition owner is `integration_edge.main:create_app`, already the
application bootstrap rather than a domain service. Only that module may
import `channel_adapters`, select the closed id `generic-webhook`, construct
validated trusted configuration and inject the port into `OutboundService`.
SDK and edge domain modules remain concrete-adapter independent. Unknown ids,
missing configuration and either vendor-mock id produce no adapter and retain
the zero-attempt `ADAPTER_UNAVAILABLE` path. Filesystem scanning, package entry
points, reflection and dynamic plugin discovery are forbidden.

The legacy `packages/channel-sdk/adapter-interface/adapter.py` file is not part
of the packaged `src/channel_sdk` surface and is not a second contract owner.
SPEC must either mark it legacy/non-authoritative or remove it within an exact
Work Order; it must not be extended in parallel.

## 3. Bounded request contract

`AdapterDeliveryRequestV1` is a closed, immutable projection of the existing
P4-C outbound command. It contains only version, command/idempotency/
correlation identifiers and the existing workspace, record, action, content,
recipient and channel digests plus policy/version lineage needed by the
receiver to correlate an authorized event.

It contains no message text, attachment bytes, external endpoint, recipient
handle, user identity, credential or provider-specific field. Its canonical
JSON bytes are deterministic UTF-8 with sorted keys and compact separators.
The adapter verifies that the separately passed idempotency key equals the
request value before signing or transport.

Digests remain correlation and equality-bearing data. They are not encryption,
anonymization or disclosure authority; low-entropy source values may be
guessable. Their egress therefore requires the explicit adapter-scope binding
below even though no clear-text content is present.

`AdapterScopeBindingV1` is trusted configuration owned by the composition
root. Each entry is one closed tuple of exact workspace digest, channel digest,
policy version and required signed-prerequisite reference; independent lists
that could accidentally form a Cartesian product are not allowed. Before
adapter invocation, Integration Edge requires the command to match one whole
tuple and to carry its prerequisite reference. A mismatch fails closed before
transport as `ADAPTER_UNAVAILABLE`. This check performs no recipient or
conversation resolution and does not transfer P4-E ownership.

This design deliberately does not add content or recipient material to the
P4-C outbound command. A later tranche may authorize a minimized delivery
projection after P4-E resolves identity/routing and its data-scope contract is
reviewed.

## 4. Adapter activation contract

The ambiguous `evidence_eligible` boolean is replaced on the packaged port by
one closed adapter mode:

- `DEPLOYABLE`: eligible for runtime injection when trusted configuration is
  valid;
- `CONFORMANCE_ONLY`: never eligible for runtime injection.

The generic webhook declares `DEPLOYABLE`. Zalo and WhatsApp mocks declare
`CONFORMANCE_ONLY`. Integration Edge rejects a missing, unknown or
conformance-only adapter as its existing zero-attempt `ADAPTER_UNAVAILABLE`
outcome. Tests may invoke conformance mocks directly; they may not weaken the
runtime activation check.

## 5. Result and physical-attempt contract

`AdapterDeliveryResultV1` is a closed immutable model returned on every
ordinary adapter path. It carries a terminal adapter status, exact
`transport_attempted` boolean and only the outcome-controlled delivery id or
closed reason fields. The port does not return arbitrary mappings.

The generic adapter owns the attempt boundary:

1. request/config/egress/signing validation occurs before transport;
2. a failure in that region returns `transport_attempted = false`;
3. the flag changes to true immediately before the single transport call;
4. every response, timeout or error after that point returns
   `transport_attempted = true`;
5. the adapter performs no automatic retry.

Integration Edge remains the sole receipt owner. It validates the result
model and maps it to the existing P4-C terminal family. A valid pre-transport
refusal maps to `NOT_ATTEMPTED / ADAPTER_UNAVAILABLE / 0`; accepted transport,
provider refusal, terminal failure and ambiguous transport retain their
existing P4-C outcomes and exact counters. An adapter exception or malformed
result is conservatively `OUTCOME_UNKNOWN / AMBIGUOUS_TRANSPORT / 1` because
the edge cannot prove that no external effect occurred.

`DELIVERED` is not produced by the generic webhook: HTTP acceptance proves
only `SENT_ACCEPTED`. No response body is trusted as end-recipient delivery.

## 6. Generic webhook request

The adapter sends exactly one HTTPS `POST` whose body is the canonical
`AdapterDeliveryRequestV1`. Destination, path and all authentication material
come only from injected trusted configuration; the outbound command cannot
select or alter them.

Required request metadata is limited to content type, signature version, key
id, UTC timestamp, idempotency key, body digest and HMAC signature. Header
names, canonical encoding and size limits become exact SPEC requirements.
Response bodies are bounded and used only for safe transport classification;
they are not persisted as provider truth.

## 7. HMAC contract

The existing HMAC-signed skeleton is retained. A secret resolver receives a
configured key id and returns key bytes at call time. Keys never enter source,
commands, models, fixtures, receipts or logs.

Signature version `v1` covers, in a SPEC-defined unambiguous canonical
preimage, the version, timestamp, HTTP method, normalized endpoint audience,
idempotency key, and SHA-256 digest of the exact request bytes. The endpoint
audience is the canonical HTTPS scheme, lowercase IDNA host, effective port
and normalized fixed path; its digest is also exposed as typed request
metadata. The secret resolver accepts the pair `(key_id, audience_digest)` so
a key id is valid for exactly one audience. The receiving contract requires
the same key id/version/audience, constant-time comparison, a bounded timestamp
window and idempotency/replay handling. SPEC must reject cross-host, cross-port,
cross-path, key-id, timestamp and idempotency mutations. The sender does not
claim receiver replay enforcement; its evidence is limited to producing a
conformant signed request.

Telemetry may expose the key id, signature version, request byte length and
body digest. It must not expose key bytes, signature preimage, full signature,
request body, response body or configured URL query.

## 8. Trusted egress policy

`GenericWebhookConfig` is immutable and injected by runtime composition. It
contains a fixed HTTPS endpoint, exact allowed host and port, key id, timeout
and request/response byte ceilings. It has no development placeholder or
command-level override.

Before transport, a trusted endpoint policy must:

- require HTTPS, reject user-info and fragments, and require the configured
  normalized host/port/path to equal the allowlisted values;
- disable redirects;
- resolve the host and reject any non-global, loopback, private, link-local,
  multicast, reserved or unspecified address;
- return one closed `AuthorizedEndpointV1` containing the original hostname,
  effective port, normalized path, audience digest and complete approved IP
  set; no component may perform a second uncontrolled resolution;
- enforce finite connect/total timeout and request/response byte ceilings;
- emit only allowlisted fields or typed hashes in telemetry.

The only network seam is a two-step `ResolvedHttpsTransportPort`. Its
`connect` operation takes `AuthorizedEndpointV1`, disables ambient/environment
proxies, selects only an approved IP, retains the original hostname for HTTP
Host, TLS SNI and certificate hostname verification, and returns a bound
connection exposing the connected peer IP and verified TLS server name. No
request body or HMAC header is sent during `connect`. The adapter rejects a
peer outside the approved set or a TLS-name mismatch, then calls `send` exactly
once on that same connection. `send` cannot resolve, redirect, proxy or change
authority.

Configuration, scope binding, DNS, connect/peer validation, signing or
projection failure occurs before the delivery-attempt boundary. The exact
attempt flag changes immediately before `send` releases the first signed HTTP
request byte. From that point all failures are attempted and never blindly
retried. Deterministic tests must cover changed resolution between authorize
and connect, disallowed connected peers, enabled ambient proxy settings, and
mixed IPv4/IPv6 answers; every case fails before body or HMAC disclosure.

## 9. Zalo and WhatsApp conformance mocks

The two mocks implement the packaged request/result contract without vendor
SDKs, credentials, HTTP clients, official templates or runtime registration.
They accept only deterministic synthetic fixtures and can produce the closed
adapter outcomes required by contract tests. Their adapter mode is permanently
`CONFORMANCE_ONLY`.

Mocks prove only provider-neutral shape, mapping and dependency replacement.
They do not prove a Zalo/WhatsApp request format, vendor acceptance, delivery,
credential readiness, governance behavior or production integration.

## 10. Invariant-family decision

P4-D triggers the invariant-family standard through shared result models,
outcome-controlled fields, exact attempt relations and multiple validator
surfaces.

SPEC must register a separate family,
`P4D-ADAPTER-RESULT-OUTCOMES`, because adapter-local result/attempt semantics
have a different owner and representation boundary from P4-C receipts. The
existing `P4C-OUTBOUND-TERMINAL-OUTCOMES` family remains the canonical receipt
owner and is not extended merely to model adapter internals. SPEC pins both
families and proves the mapping between them without copying matrix rules into
prose.

The new family must bind its canonical matrix digest to the SDK model/schema,
generic adapter, conformance mocks, edge mapping and independent tests.

## 11. Evidence and acceptance direction

DESIGN/SPEC/BUILD evidence is deterministic and zero-network:

- closed model/schema parity and negative extra-field tests;
- exact one-call/zero-call transport spy tests for every family outcome;
- activation rejection of conformance-only mocks;
- HMAC canonicalization, timestamp and secret-free telemetry tests;
- endpoint-policy tests covering scheme, authority, redirects, DNS/address
  classes, rebinding seam, bounds and timeouts;
- dependency tests proving no concrete-adapter import into SDK/edge domain;
- mapping tests preserving P4-C receipt ownership, counters and no-blind-retry;
- invariant-family, Project Knowledge, session, catalog, file-size and
  repository guards.

Mock/conformance evidence is never live-delivery or CVF-governance evidence.
No real provider call is required for a bounded adapter contract/library claim.
Any later claim that CVF governs behavior through an external provider requires
separate call authority and a sanitized real-provider receipt.

## 12. Out of scope

- real Zalo/WhatsApp APIs, SDKs, credentials, templates or certification;
- message text, attachment bytes, recipient handles, identity mapping or
  conversation routing;
- inbound generic webhook changes or P4-C raw evidence/quarantine mechanics;
- automatic retry, reconciliation service or exactly-once delivery claims;
- public API/UI, durable secret store, deployment, production readiness,
  provider call, install, commit or push during DESIGN;
- email, SMS, PWA, customer-portal or notification-engine adapters.

## 13. Rejected alternatives

1. **Put endpoint URL in the command** — rejected as an SSRF/data-egress
   authority transfer to runtime data.
2. **Send message content now** — rejected because P4-E identity/routing and a
   reviewed minimized data projection do not exist.
3. **Treat HTTP 2xx as delivered** — rejected because it proves endpoint
   acceptance only.
4. **Reuse the P4-C receipt matrix as the adapter-result owner** — rejected
   because adapter-local attempt evidence and edge-owned receipts are distinct
   contracts.
5. **Make vendor mocks runtime-registerable** — rejected because it could turn
   deterministic fixtures into false delivery evidence.
6. **Retry timeout/5xx automatically** — rejected because an external effect
   may already have happened.

## 14. Design disposition

`READY_FOR_INDEPENDENT_DESIGN_REVIEW`.

SPEC, WORK_ORDER, BUILD, provider/network calls, credentials, installation,
deployment, commit and push remain unauthorized.
