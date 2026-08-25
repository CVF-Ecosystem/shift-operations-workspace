# Independent DESIGN Review — P4-C Integration Edge

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Reviewed phase: `DESIGN` only
- Reviewer role: `INDEPENDENT_DESIGN_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

The review compared
`docs/decisions/DESIGN_2026-08-23_P4C_INTEGRATION_EDGE.md` against the accepted
INTAKE and its final review, current canonical continuity, roadmap P4-C/P4-D/
P4-E ownership, channel/trust contracts, module registry, current
`integration-edge` and `channel-sdk` source, the R2 live-proof rule, and the
invariant-family standard. The review focused on security, persistence,
concurrency, failure semantics, feasibility, testability, and claim boundaries.

Current source remains the bounded scaffold described by the DESIGN parent:
unversioned HMAC, full-body read, process-local dedupe before JSON parsing, no
durable raw/quarantine/rate/routing/outbound implementation, and a directional
`ChannelAdapter` protocol. `HEAD == origin/main ==
0b89016df8483a4904d2c64b1a6560ccbc6b27ae`; staged paths are empty. The dirty
set contains the P4-C governance artifacts/continuity plus the pre-existing
untracked operator assessment, which was not opened or modified by this
reviewer.

Read-only checks returned: session-state guard `PASS`; invariant-family guard
`PASS`; workspace doctor `24 passed, 1` retained bounded legacy-catalog
warning. No provider call is authorized or needed for this design-only review,
and no governance-behavior proof claim is made here.

## Numbered findings

1. **P4C-DESIGN-REV-F1 — Unauthenticated traffic bypasses the only designed
   rate limit.** The closed order streams the request body and performs HMAC
   verification in steps 1–2, while the only atomic rate-budget consumption is
   step 5 and depends on an authenticated subject. Invalid/missing/stale
   signatures therefore never reach a rate bucket, allowing a public caller to
   consume body-read and cryptographic resources without the P4-C `rate_limit`
   control. Define a bounded pre-auth transport/endpoint budget before body
   work (plus the post-auth subject budget if retained), including privacy-safe
   subject derivation, atomic concurrency semantics, failure behavior and the
   relationship between both counters. Body-size limits alone do not close
   request-rate exhaustion.

2. **P4C-DESIGN-REV-F2 — Key-collision quarantine precedes the raw envelope it
   requires.** Step 3 declares a same-key/different-digest delivery
   `QUARANTINED_KEY_COLLISION`, but step 4 preserves the verified raw envelope
   only after a replay reservation is acquired. The collision branch cannot
   acquire that reservation and therefore cannot naturally create the
   envelope id required by the quarantine record or preserve the colliding
   evidence without violating the stated order. Define an atomic collision
   path that preserves the new verified envelope under a distinct edge id,
   links it without overwriting the first accepted evidence, commits the
   quarantine receipt, and states the reservation outcome. The invariant
   family must cover this branch and concurrent collision races.

3. **P4C-DESIGN-REV-F3 — The service-authenticated ports are labels, not yet a
   testable trust contract.** INTAKE decision 4 required the downstream ingress
   contract to be defined and shown unable to bypass identity, permission,
   assignment, domain-lock, approval, audit or confirmation controls. DESIGN
   states only that downstream and outbound ports are authenticated and bind
   receipt references. It does not select the credential/issuer boundary,
   audience and operation claims, expiry/rotation/replay rules, service
   principal authorization, request-digest binding, or fail-closed behavior
   when auth/receipt validation is unavailable. Nor does it define the exact
   core-owned ingress-proposal operation that is permitted. Select these
   semantics for both directions and make clear which core controls are
   independently revalidated versus accepted from an authenticated signed
   command; otherwise a SPEC cannot derive non-bypass acceptance tests.

4. **P4C-DESIGN-REV-F4 — The raw-store transaction boundary is unresolved
   across the two selected persistence shapes.** Section 3 permits either raw
   bytes in the SQL-backed store or an encrypted-at-rest blob reference, while
   step 4 promises raw preservation and replay reservation in the same durable
   unit. A SQL transaction cannot atomically commit an external blob and its
   reference without an explicit staging/outbox/reconciliation protocol. The
   design also does not require encryption at rest for the direct-byte option.
   Choose the P4-C implementation shape or define the exact multi-resource
   commit/recovery state machine, including orphan cleanup, digest verification,
   encryption/key authority, unavailable storage behavior and retention delete
   ordering. This is necessary to make the no-silent-consumption and rollback
   claims feasible.

5. **P4C-DESIGN-REV-F5 — The generic adapter boundary overlaps roadmap P4-D.**
   Section 2 says P4-C includes a "generic contract implementation sufficient
   for conformance," while the roadmap and module registry assign the concrete
   generic-webhook adapter, alongside mock Zalo/WhatsApp adapters, to P4-D.
   State unambiguously that P4-C may provide only a deterministic test fixture/
   conformance fake behind the port, with no production/provider semantics, or
   defer the generic implementation entirely to P4-D. A deployable generic
   adapter must not be pulled into P4-C under the name of conformance.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted design boundaries

Subject to the findings above, the following are accepted: edge ownership is
separate from Operations Ledger truth; verified raw evidence is intended to
precede parsing; candidates remain `UNTRUSTED_EXTERNAL`/`RAW`; P4-E retains
identity and conversation ownership; ambiguous route/send outcomes block blind
retry; quarantine release re-runs policy; observability excludes sensitive raw
content; runtime placeholder secrets are removed; invariant-family
applicability is correctly `APPLICABLE`; and the full live-governance evidence
rule is preserved without authorizing a call during DESIGN.

## Disposition

`DESIGN_REVIEW_CHANGES_REQUIRED`.

SPEC, WORK_ORDER and BUILD remain unauthorized. Return only the five findings
above for bounded DESIGN repair and independent rereview.

## Bounded rereview — P4C-DESIGN-REV-F1..F5

- Rereview role: `INDEPENDENT_DESIGN_REVIEWER`
- Rereview scope: repaired DESIGN findings F1 through F5 only
- Rereview findings: `NONE`
- Rereview waivers: `NONE`

1. **F1 CLOSED.** The order now consumes an atomic pre-auth endpoint/trusted-
   peer budget before body read or HMAC and a distinct atomic post-auth
   provider-account budget only after valid signature. The design fixes exact
   counter relations, concurrency, unavailable-store failure, trusted subject
   derivation and non-rollback of transport work; invalid-signature flood and
   boundary-count tests are explicitly required.
2. **F2 CLOSED.** The replay classification transaction now inserts a distinct
   encrypted collision envelope plus `QUARANTINED_KEY_COLLISION`, links both
   collision and original envelope, leaves the original reservation unchanged,
   and rolls back the complete collision/quarantine/receipt unit on failure.
   Unique constraints and invariant-family coverage bind concurrent races.
3. **F3 CLOSED.** `ServiceAssertionV1` now defines closed signed claims,
   request/body/idempotency binding, 60-second expiry, key rotation, atomic
   nonce replay rejection, exact audience/operation authorization and
   fail-closed dependencies. The sole edge-to-core operation creates only an
   actor-neutral `RAW`/`UNTRUSTED_EXTERNAL` proposal; it cannot satisfy user
   identity, permission, assignment, domain-lock, approval, audit or
   confirmation. The reverse operation binds an independently revalidated
   core command and authorizes only `outbound.deliver`.
4. **F4 CLOSED.** External blob storage is rejected. Raw bytes are encrypted
   in memory with AES-256-GCM through an injected key authority and the
   ciphertext/key id/nonce/tag are stored in the same SQL row and transaction
   as replay and terminal state. Failure commits nothing; reads verify AEAD and
   plaintext digest; retention deletion and digest-only tombstone are atomic;
   rotation preserves decrypt authority until dependent ciphertext expires.
   There is no second-store orphan or plaintext staging path.
5. **F5 CLOSED.** P4-C now permits only a deterministic test-only,
   evidence-ineligible conformance fake that runtime wiring cannot register.
   Every deployable generic webhook or provider adapter remains explicitly
   owned by P4-D.

Fresh rehydration found bootstrap projection, canonical state, active handoff,
session memory and docs index consistent at
`p4c_integration_edge_design_repair_ready_for_rereview`. The session-state and
invariant-family guards passed; the workspace doctor returned 24 passes and
the retained bounded legacy-catalog warning. No provider call was needed or
authorized for this design-only rereview, which makes no governance-behavior
proof claim.

## Final disposition

`DESIGN_REVIEW_PASS`.

The initial `DESIGN_REVIEW_CHANGES_REQUIRED` disposition is retained above as
review history and is superseded by this bounded rereview. F1 through F5 are
closed without waiver. SPEC may proceed only through the next recorded
governed role/phase transition; WORK_ORDER, BUILD, commit, push, provider,
credential, install and deployment effects remain unauthorized.

## Independent review — DESIGN Amendment 1 / path 67

- Review date: `2026-08-25`
- Reviewer role: `INDEPENDENT_DESIGN_AMENDMENT_REVIEWER`
- Scope: `docs/decisions/P4C_INTEGRATION_EDGE_PATH67_DESIGN_AMENDMENT_2026-08-25.md`
- Findings: `NONE`
- Waivers: `NONE`

Independent SHA-256 recomputation confirmed that the Knowledge manifest has
exactly three currently stale source pins among its 16 pins, and that the
amendment records each replacement value exactly:

- `docs/catalog/MODULE_REGISTRY.json` —
  `4a7c621126cc1237bc8ec43bc67dba69ca1ccfc94a402ac65a8131d18fe5710f`;
- `AGENTS.md` —
  `6b2629d21f49b6841ffccad3dd1912dca50b5ea9a9eb6c6c2a1edf56c1b3fecf`;
- `.cvf/manifest.json` —
  `2f319767aadce1da76650bfe4b682ad993d664746157dd4b80a49a85f6f8d79a`.

The selected boundary is one additional BUILD path and only those three
current-to-next SHA values. The already-present `IMPLEMENTATION_STATUS.json`
pin delta belongs to the settled Core-refresh lineage and is preserved; no
manifest metadata, path, classification, eligibility, consumer, lifecycle or
other pin is authorized to change. The parent DESIGN remains at raw SHA-256
`b141320a5a4fc828c7d2b6d0a318009ce131e844e24537222c9174ae391a2137`.
The P4-C ingress and outbound invariant matrices remain at canonical digests
`277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`
and `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`;
the invariant-family and session-state guards pass.

The amendment preserves the zero provider, credential, install, deployment,
database, commit and push boundary. This deterministic contract review makes
no claim that CVF governance behavior was executed, so no provider call was
required or authorized.

### Amendment disposition

`DESIGN_AMENDMENT_REVIEW_PASS`.

SPEC may receive only the corresponding path-67 amendment through the next
recorded governed role/phase transition. BUILD remains stopped until the SPEC
and Work Order amendments each receive independent PASS disposition.
