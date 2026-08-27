# Independent SPEC Review — P4-D Channel Adapters

- Tranche: `P4D-CHANNEL-ADAPTERS-2026-08-26`
- Phase: `SPEC`
- Risk: `R2`
- Role: `INDEPENDENT_SPEC_REVIEWER`
- Review date: `2026-08-26`
- Disposition: `SPEC_REVIEW_PASS`

## Scope and independence

This review evaluated exactly the four SPEC-author paths:

1. `docs/specs/P4D_CHANNEL_ADAPTERS_SPEC.md`
2. `docs/cvf/invariants/p4d-adapter-result-outcomes.json`
3. `docs/specs/p4d_invariant_pins.py`
4. `docs/cvf/invariants/registry.json`

They were compared with the accepted P4-D DESIGN and independent DESIGN
review, the invariant-family standard/schema, the current P4-C outbound
matrix/schema/service, and the packaged `channel-sdk` outbound port. The
reviewer did not edit any SPEC-author, product, continuity or handoff path.

## Review result

The SPEC preserves the accepted digest-only business boundary and P4-E
ownership of recipient identity and conversation routing. It makes the
following contracts testable without claiming current implementation truth:

- the closed P4-D result family has five total outcomes with exact
  outcome-controlled `transport_attempted`, `reason`, and `delivery_id`
  relations;
- the P4-D result matrix and P4-C receipt matrix remain separate canonical
  owners, with exact machine pins and a total P4-D-to-P4-C mapping;
- local pre-send failures normalize to P4-C zero-attempt
  `ADAPTER_UNAVAILABLE`, while escaped exceptions and malformed results are
  conservatively persisted as attempted `OUTCOME_UNKNOWN`;
- one indivisible workspace/channel/policy/prerequisite/adapter scope tuple is
  required before adapter invocation, with duplicate and missing matches
  failing closed;
- the HMAC v1 preimage binds the canonical HTTPS audience, body digest,
  idempotency key, key id, timestamp, method and version, and the secret
  resolver is scoped to `(key_id, audience_digest)`;
- `AuthorizedEndpointV1` plus `ResolvedHttpsTransportPort` closes the resolver,
  peer, TLS-name, proxy and second-resolution seams before signed-body
  disclosure;
- only exact `DEPLOYABLE` runtime activation is admitted. Zalo and WhatsApp
  remain zero-I/O `CONFORMANCE_ONLY` mocks and are rejected by composition;
- the acceptance set covers model/schema/matrix mutation parity, scope and
  activation zero-call paths, exact mapping and attempts, SSRF/DNS rebinding,
  HMAC mutations, telemetry denial, HTTP classification, dependency direction
  and repository guards;
- deterministic mock/spy evidence is explicitly bounded away from live
  delivery, vendor conformance, receiver replay enforcement, governance
  behavior, production readiness and deployment claims.

The current P4-C service and SDK port still expose the predecessor mapping and
`evidence_eligible` interfaces. The SPEC identifies these as BUILD targets;
their present state is not represented as already implemented.

## Deterministic evidence

- SPEC SHA-256:
  `8fb1bf6e9626dd2c3514456bdfce88f236f22d4f9668032fa35d9238f109ec78`
- P4-D matrix raw and canonical SHA-256:
  `f09811c29e94de7a93300a1dc4aa8ed6eae3a9bd83418840089c5156224bfb6d`
- Pin module SHA-256:
  `24c94777f06bd6b4e4134f63c0ae29fe471e982b994fdfc693698467b545205a`
- Registry SHA-256:
  `8e95511d17376957b86d11ba6b0fb210826dc0b010ed9ffd43d041c89ab1f4fe`
- P4-C outbound matrix canonical pin:
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`
- Current P4-C outbound schema SHA-256:
  `d7eaedac8d440c2eb2fb78f2c9d9e6a56f3924f6334710de385205c6ce6e5aca`
- Current P4-C outbound service SHA-256:
  `3024d4c2661c7138d6e96b2a5ac22d456a1fbc629c450be65c41abe1288af2dd`
- Current packaged SDK port SHA-256:
  `0e50b46cc88d8a3d039d2f3002b9bcc90afc19528870590e61f4b0252eb8fe4b`
- invariant-family, Project Knowledge, session-state, catalog and file-size
  guards: `PASS`;
- scoped diff whitespace guard: `PASS`;
- staged set: zero.

No network/provider call, credential access, install, deployment, commit or
push occurred. No live-governance or provider-delivery claim is made.

## Findings and waivers

Findings: `NONE`.

Waivers: `NONE`.

## Disposition and next allowed move

`SPEC_REVIEW_PASS`.

Return ownership to the `ORCHESTRATOR`. The next governed move is to author a
bounded P4-D WORK_ORDER from this accepted SPEC and submit it for independent
authorization review. This review grants neither BUILD nor external-effect
authority.

## Independent R3 amendment review — 2026-08-27

Role transition: `INDEPENDENT SPEC REVIEWER -> INDEPENDENT SPEC AMENDMENT REVIEWER`.

The amended SPEC SHA-256 was independently recomputed as
`b81592202e3a1770acd30d3bc06e7d4f6060b5d42096374996e6c87564e1e388`.
The review was bounded to the R3 correction required by
`P4D-COMP-REV-F2`, its acceptance text and the unchanged surrounding contract.

Amended R3 now selects the alternative already allowed by the accepted
DESIGN: the unpackaged `packages/channel-sdk/adapter-interface/adapter.py`
remains untouched, explicitly non-authoritative and forbidden from product or
test imports, while packaged `src/channel_sdk` remains the sole runtime
contract. It removes the contradictory remove-or-replace BUILD obligation and
does not authorize the legacy path, add a path, change product behavior or
weaken dependency tests.

Independent checks confirmed:

- the legacy file's current Git object id equals its `HEAD` object id,
  `0f32802fcf9c19c9d693d9bc76131507d50d3702`;
- the exact P4-D and P4-C matrix digests remain
  `f09811c29e94de7a93300a1dc4aa8ed6eae3a9bd83418840089c5156224bfb6d`
  and
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`;
- invariant-family, Project Knowledge, session-state and file-size guards
  pass; scoped whitespace and staged-zero checks pass;
- no provider/network/DNS, credential, install, database, deployment, commit
  or push action occurred.

Findings: `NONE`. Waivers: `NONE`.

Amendment disposition: `SPEC_AMENDMENT_REVIEW_PASS`.

Return ownership to the `ORCHESTRATOR` for independent Work Order amendment
authorization rereview. This amendment review grants no closure, FREEZE,
commit or external-effect authority.
