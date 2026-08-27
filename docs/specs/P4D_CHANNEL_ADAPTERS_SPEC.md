# SPEC — P4-D Channel Adapters

- Tranche: `P4D-CHANNEL-ADAPTERS-2026-08-26`
- Phase: `SPEC`
- Risk ceiling: `R2`
- Role: `SPEC_AUTHOR`
- Accepted predecessors: P4-D INTAKE and DESIGN, each with independent PASS
- Amendment lineage: `2026-08-27 / P4D-COMP-REV-F2 / R3 clarification`
- BUILD authority: `NOT GRANTED`
- External-effect authority in this phase: `NONE`

## 1. Bounded capability and claim

P4-D shall add one deployable, provider-neutral generic outbound webhook
adapter behind the P4-C outbound port and two deterministic Zalo/WhatsApp
conformance mocks. The generic adapter sends only the existing digest-based
integration event. It shall not fetch or emit message text, attachment bytes,
recipient handles, identity mappings or conversation placement.

P4-C remains the only owner of authorization, prerequisites, rate limiting,
receipt emission, terminal state and persistence. P4-E remains the owner of
recipient identity and conversation routing. A successful HTTPS response is
only endpoint acceptance (`SENT_ACCEPTED`), never end-recipient delivery.

All evidence authorized by this SPEC is deterministic and zero-network. It
does not prove a Zalo/WhatsApp protocol, a live send, external receiver replay
enforcement, CVF control of provider behavior, production readiness or
deployment.

## 2. Normative invariant pins

The P4-D result family is mandatory because this R2 tranche has a shared result
model, outcome-controlled fields, an exact physical-attempt fact and multiple
validator surfaces.

- Adapter-result owner: `P4D-ADAPTER-RESULT-OUTCOMES`, canonical digest stored
  as `P4D_ADAPTER_RESULT_MATRIX_CANONICAL_DIGEST` in
  `docs/specs/p4d_invariant_pins.py`.
- Edge-receipt owner: `P4C-OUTBOUND-TERMINAL-OUTCOMES`, canonical digest stored
  as `P4C_OUTBOUND_MATRIX_CANONICAL_DIGEST` in the same pin file.

The two matrices are separate semantic owners. Implementations and tests shall
load and validate the pinned matrices; they shall not reproduce a second result
or receipt grammar in fixtures, prose constants or adapter-specific mappings.
Any change to either canonical digest invalidates P4-D review evidence and
requires an authorized SPEC/invariant amendment before BUILD continues.

## 3. Dependency and composition requirements

### R1 — Dependency direction

`channel-sdk` shall own the provider-neutral typed models and ports.
`channel-adapters` may depend on `channel-sdk`. Integration Edge domain modules
may depend on `channel-sdk`, but neither they nor `channel-sdk` may import a
concrete adapter. No adapter may import Integration Edge.

### R2 — Sole composition owner

`integration_edge.main:create_app` shall be the only production module allowed
to import `channel_adapters`. It shall select only the closed id
`generic-webhook`, construct validated trusted configuration, and inject the
adapter into `OutboundService`. Module-level `app` may only be the direct
result of this factory. Unknown ids, missing/invalid configuration and the ids
`zalo` or `whatsapp` shall inject no adapter and retain the existing
zero-attempt `ADAPTER_UNAVAILABLE` result.

Filesystem scanning, package entry points, reflection, dynamic import and
implicit plugin discovery are forbidden.

### R3 — Legacy interface

`packages/channel-sdk/adapter-interface/adapter.py` is non-authoritative legacy
scaffolding. It shall remain untouched, shall not be extended, and shall not be
imported by product code or tests. The packaged `src/channel_sdk` contract is
the sole authoritative runtime contract. This amended requirement addresses
`P4D-COMP-REV-F2`; it removes the prior remove-or-replace obligation without
authorizing the legacy path or changing the exact Work Order ceiling.

## 4. Closed SDK contracts

### R4 — Adapter mode and port

The packaged SDK shall define `AdapterMode = Literal["DEPLOYABLE",
"CONFORMANCE_ONLY"]`. `OutboundAdapterPort` shall expose an immutable
`adapter_mode` and exactly one operation:

```python
deliver(*, request: AdapterDeliveryRequestV1, idempotency_key: str) -> AdapterDeliveryResultV1
```

The old `evidence_eligible` boolean and arbitrary mapping return are removed
from the authoritative port. Integration Edge shall runtime-admit only exact
`DEPLOYABLE`; missing, unknown and `CONFORMANCE_ONLY` fail before invocation.

### R5 — `AdapterDeliveryRequestV1`

The request shall be a frozen Pydantic v2 model with extra fields forbidden and
these exact fields:

- `version`: literal `"1"`;
- `command_id`, `idempotency_key`, `correlation_id`: non-empty strings, maximum
  256 characters;
- `workspace_digest`, `record_digest`, `action_digest`, `content_digest`,
  `recipient_digest`, `channel_digest`: lowercase 64-character SHA-256 hex;
- `record_version`: integer at least 1;
- `policy_version`: non-empty string, maximum 128 characters;
- `prerequisite_receipt_refs`: non-empty immutable tuple of unique, non-empty
  strings, each at most 256 characters, normalized into ascending ordinal
  order before canonical serialization.

No endpoint, URL, query, key id, credential, clear-text content, attachment,
recipient handle, user identity or provider-specific field is permitted. The
separately passed `idempotency_key` shall equal the request field exactly;
mismatch returns a pre-transport result without signing, connect or send.

`canonical_bytes()` shall serialize the validated model dump as UTF-8 JSON
with `ensure_ascii=True`, lexicographically sorted object keys and separators
`,` and `:` with no whitespace or trailing newline.

### R6 — `AdapterDeliveryResultV1`

The result shall be a frozen Pydantic v2 model with extra fields forbidden.
Its sole grammar is the pinned `P4D-ADAPTER-RESULT-OUTCOMES` matrix. The closed
schema for both typed delivery models shall be
`contracts/channel/adapter-delivery.schema.json`. The Python model, that JSON
Schema, generic adapter, both conformance
mocks, edge mapper and independent conformance tests shall accept every matrix
positive and reject every deterministic one-fact mutation.

No ordinary adapter path returns a mapping or raises a transport exception
past the adapter boundary. An exception that unexpectedly escapes, or a value
that cannot be validated as `AdapterDeliveryResultV1`, is handled
conservatively by R9.

## 5. Trusted scope and edge mapping

### R7 — Exact scope tuple

Trusted composition shall supply immutable `AdapterScopeBindingV1` entries.
Each entry is one indivisible tuple:

```text
(workspace_digest, channel_digest, policy_version,
 required_prerequisite_receipt_ref, adapter_id)
```

Independent value lists are forbidden. Before adapter invocation, Integration
Edge shall require exactly one binding whose `adapter_id` is
`generic-webhook`, whose first three values equal the request exactly, and
whose required prerequisite reference is an exact member of the request's
immutable reference tuple. Zero matches or more than one match fail closed as
P4-C `NOT_ATTEMPTED / ADAPTER_UNAVAILABLE / delivery_attempts=0` without
adapter, resolver, connect, secret or send calls.

This equality check is not recipient resolution. Digests remain correlation-
and equality-bearing data; they are not encryption, anonymization or standing
egress authority.

### R8 — Total matrix-to-receipt mapping

For a validated adapter result, Integration Edge shall implement this total
cross-family mapping while P4-C remains the emitter and persistence owner:

| P4-D adapter outcome | Required P4-C receipt outcome |
|---|---|
| `NOT_ATTEMPTED` | `NOT_ATTEMPTED`, reason normalized to `ADAPTER_UNAVAILABLE`, attempts `0` |
| `SENT_ACCEPTED` | `SENT_ACCEPTED`, same `delivery_id`, attempts `1` |
| `PROVIDER_REFUSED` | `PROVIDER_REFUSED`, canonical P4-C reason, attempts `1` |
| `TERMINAL_FAILED` | `TERMINAL_FAILED`, same P4-C-compatible reason, attempts `1` |
| `OUTCOME_UNKNOWN` | `OUTCOME_UNKNOWN / AMBIGUOUS_TRANSPORT`, attempts `1` |

`DELIVERED` shall never be emitted from the generic webhook or either mock.
The adapter shall be called at most once for one P4-C command, and neither the
adapter nor Edge shall automatically retry.

### R9 — Conservative unknown handling

Because Edge cannot independently prove whether an escaped adapter exception
or malformed result occurred before the first request byte, either case shall
map to P4-C `OUTCOME_UNKNOWN / AMBIGUOUS_TRANSPORT / delivery_attempts=1`.
It shall be terminal and persisted through the existing P4-C path, with no
blind retry. Only a successfully validated P4-D `NOT_ATTEMPTED` result may
produce a zero-attempt adapter-side receipt.

## 6. Generic webhook configuration and egress

### R10 — Immutable configuration

`GenericWebhookConfig` shall be frozen and closed. It shall contain only:

- fixed `endpoint_url`, `allowed_host`, `allowed_port`, `allowed_path`;
- non-empty `key_id` of at most 128 characters;
- finite `connect_timeout_seconds` in `(0, 10]` and
  `total_timeout_seconds` in `[connect_timeout_seconds, 30]`;
- `max_request_bytes` and `max_response_bytes`, each in `[1, 65536]`.

There is no command-level override, and ambient proxy or HTTP-client
environment settings shall not alter the validated object after composition.
The composition owner may receive trusted non-secret deployment values through
its explicit factory input; this SPEC does not authorize deployment or secret
loading. The endpoint shall
be HTTPS, contain no user-info/query/fragment, and use a DNS hostname rather
than an IP literal. The host shall already equal its lowercase IDNA A-label
without a trailing dot. The explicit/effective port shall be in `1..65535`.
The path shall be absolute ASCII, non-empty and already normalized: no percent
encoding, backslash, repeated slash, or `.`/`..` segment. The normalized
endpoint host, port and path shall equal the three allowlist fields exactly.
Redirect following is always disabled.

### R11 — Authorized endpoint

An injected resolver shall perform the only DNS resolution and return the
complete answer set. Empty answers fail closed. Every answer shall parse as an
IP address and be globally routable; the entire set is rejected if any member
is private, loopback, link-local, multicast, reserved, unspecified or otherwise
not global. An all-global mixed IPv4/IPv6 set is valid and retained completely
in deterministic numeric order.

The policy shall return frozen `AuthorizedEndpointV1` with exactly the
original canonical hostname, effective port, normalized path, canonical
audience, audience digest and complete approved IP tuple. The canonical
audience is:

```text
https://<lowercase-idna-host>:<effective-port><normalized-path>
```

`audience_digest` is lowercase SHA-256 hex of its ASCII bytes.

### R12 — Two-step transport seam

The only network seam is `ResolvedHttpsTransportPort`:

1. `connect(authorized_endpoint, connect_timeout_seconds)` creates one bound
   HTTPS connection without DNS, redirect, proxy, body or HMAC headers;
2. the returned connection exposes `connected_peer_ip`, verified
   `tls_server_name`, and `send(...)`.

The implementation shall use `trust_env=False`, ignore ambient proxy variables,
connect only to an approved IP, retain the original hostname for HTTP `Host`,
TLS SNI and certificate hostname verification, and expose the actual peer.
Before signing or send, the adapter shall reject a peer outside the complete
approved set or a verified TLS name unequal to the original hostname.
`send` cannot resolve, redirect, proxy, reconnect or change authority.

A deterministic changed-resolution or substituted-peer test is represented
by a bound connection reporting a peer outside the approved set; it shall fail
before body or HMAC disclosure. Tests shall also cover a proxy-populated
environment and valid/invalid mixed IPv4/IPv6 answers.

## 7. Signing, send boundary and response mapping

### R13 — Canonical HMAC request

The adapter sends exactly one HTTPS `POST`; the body is the exact request
canonical bytes. A secret resolver is called only after scope, request,
configuration, endpoint, DNS, connection-peer and TLS-name checks pass. It
accepts exactly `(key_id, audience_digest)` and returns key bytes at call time.

The injected UTC clock produces a timestamp exactly formatted as
`YYYY-MM-DDTHH:MM:SS.ffffffZ`. The canonical v1 signature preimage is the
UTF-8, `ensure_ascii=True`, sorted-key, compact JSON encoding of exactly:

```json
{"audience":"<canonical audience>","body_sha256":"<sha256 body>","idempotency_key":"<exact request value>","key_id":"<configured id>","method":"POST","timestamp":"<UTC text>","version":"v1"}
```

`X-CVF-Signature` is lowercase hex HMAC-SHA256 of this preimage. The complete
outbound header allowlist is: `Content-Type: application/json`,
`X-CVF-Signature-Version: v1`, `X-CVF-Key-Id`, `X-CVF-Timestamp`,
`Idempotency-Key`, `X-CVF-Body-SHA256`, `X-CVF-Audience-SHA256`, and
`X-CVF-Signature`. No other application header is emitted.

Tests shall prove that mutations of host, port, path, key id, timestamp,
idempotency key or body invalidate the expected signature. Receiver-side
constant-time comparison, timestamp-window enforcement and replay storage are
requirements on a future receiver and are not claimed by sender evidence.

### R14 — Exact attempt boundary

Projection, scope, configuration, resolution, connect, peer/TLS validation and
signing are pre-attempt. Failure there returns a matrix-valid P4-D result with
`transport_attempted=false`; resolver/connect/secret/send spy counts shall show
the exact calls appropriate to the failing stage and `send=0`.

Immediately before invoking `send`, the adapter fixes the result fact to
`transport_attempted=true`. Any return or exception from `send`, including a
timeout, connection loss, oversized response or indeterminate parse, remains
attempted. `send` is invoked at most once and there is no retry.

### R15 — HTTP classification

For a syntactically valid final response within the configured total byte
ceiling:

- status `200..299` returns `SENT_ACCEPTED` with sender-generated
  `delivery_id = "gwv1-" + sha256_hex(ASCII("generic-webhook-v1\\n" +
  audience_digest + "\\n" + idempotency_key + "\\n" + body_sha256))`;
- status `400..499` returns `PROVIDER_REFUSED`;
- status `500..599` returns `TERMINAL_FAILED / NONRETRYABLE_ERROR`;
- status `100..199`, `300..399`, an invalid status line or structurally invalid
  response returns `TERMINAL_FAILED / INVALID_RESPONSE`.

A send exception, timeout, connection loss, exceeded total/response ceiling or
other condition that prevents a trustworthy final classification returns
`OUTCOME_UNKNOWN / AMBIGUOUS_TRANSPORT`. Response bodies are never parsed into
operational truth, logged or persisted. Redirects are never followed.

### R16 — Secret-free telemetry

Allowed telemetry fields are adapter id/mode, key id, signature version,
audience digest, body digest, request byte length, status class, result status,
attempt fact and typed failure code. Key bytes, endpoint query, canonical
request body, response body, preimage and full signature are forbidden from
logs, exceptions, receipts and fixtures. Source and fixtures shall contain no
real credential. Explicitly labeled synthetic bytes such as `b"unit-test-key"`
are allowed only inside deterministic signing tests and are not credential
readiness evidence.

## 8. Conformance mocks

### R17 — Zalo and WhatsApp

The Zalo and WhatsApp mocks shall each implement the typed port with immutable
`adapter_mode="CONFORMANCE_ONLY"`. They shall accept only deterministic
synthetic fixtures, make zero DNS/connect/send/secret/environment calls, and
be able to emit every positive in the pinned P4-D result matrix for parity
tests. They shall contain no vendor SDK, HTTP client, official template,
credential, runtime registration or vendor-specific request assertion.

Direct unit invocation proves only provider-neutral contract replacement.
`create_app` shall reject both ids even if a caller supplies otherwise valid
generic-webhook configuration.

## 9. Required deterministic evidence

The Work Order shall authorize focused tests that prove, with zero real
network/provider calls:

1. Python model/JSON Schema parity for request and result, closed extra-field
   rejection, and the full positive/mutation corpus of the pinned P4-D matrix;
2. exact activation and scope-tuple behavior, including duplicate-match,
   missing-prerequisite and `CONFORMANCE_ONLY` refusal with zero adapter call;
3. the total P4-D-to-P4-C mapping, conservative malformed/exception mapping,
   exact receipt attempts and no retry;
4. endpoint canonicalization, all prohibited address classes, empty/mixed DNS,
   rebinding/substituted peer, TLS-name mismatch, proxy environment, size and
   timeout bounds, all before wrong-peer body/HMAC disclosure;
5. exact canonical body, audience, HMAC preimage/header allowlist, mutation
   set, secret resolver audience binding and telemetry denylist;
6. HTTP classification and exact resolver/connect/secret/send spy counts for
   every pre-attempt and attempted outcome;
7. Zalo/WhatsApp zero-I/O conformance and runtime rejection;
8. dependency tests proving the sole composition owner and absence of legacy,
   dynamic-discovery and reverse imports;
9. invariant-family, Project Knowledge, session, catalog, file-size, diff and
   repository guards required by the eventual changed set.

No mock or transport spy result may be labeled live delivery or governance
proof. A later claim that CVF governs behavior through an external provider
requires separate network/provider authority and a sanitized real-call receipt.

## 10. Explicit exclusions and stop conditions

Excluded: inbound webhook changes; P4-C authorization/rate/quarantine/raw-
evidence redesign; P4-E identity/routing; clear-text delivery; real Zalo or
WhatsApp integration; vendor SDK or credential; durable secret store; retry or
reconciliation worker; public route/UI; install; provider call; deployment;
production-readiness claim.

BUILD shall stop and return to DESIGN/SPEC if it requires any excluded data,
external effect, second composition owner, relaxed egress rule, different
result/receipt grammar, matrix digest change, or path outside the approved Work
Order. It shall stop for credential discovery rather than inspecting or using
the credential.

## 11. SPEC acceptance

SPEC is ready for independent review only when:

- the new matrix is registered and passes the deterministic invariant guard;
- both matrix digests are exact and machine-pinned;
- every normative behavior above has a deterministic acceptance route;
- no product code, test, continuity, catalog or remote state changed in SPEC;
- staged set is zero and no network/provider/credential/install/deploy action
  occurred.

Amendment disposition: `READY_FOR_INDEPENDENT_SPEC_AMENDMENT_REVIEW`.

The original SPEC review remains predecessor evidence, but this R3 amendment
requires independent amendment review and Work Order authorization rereview.
This SPEC does not grant BUILD authority.
