# SPEC — P4-C Integration Edge

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Version: `1.0`
- Phase: `SPEC`
- Risk: `R2`
- Parent DESIGN: `docs/decisions/DESIGN_2026-08-23_P4C_INTEGRATION_EDGE.md`
- DESIGN review: final `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`
- BUILD authority: `NOT GRANTED`

## Normative requirements

- **R1 — Boundary:** P4-C owns edge evidence/orchestration only. It MUST NOT
  write operational truth, implement deployable channel adapters, or own P4-E
  identity/conversation decisions.
- **R2 — Transport admission:** An allowlisted endpoint MUST atomically consume
  one trusted-peer-derived pre-auth count before body read/HMAC. Missing peer
  context, counter failure, exhaustion, oversized body or unknown endpoint MUST
  fail closed without raw persistence.
- **R3 — Verification:** Exact bounded bytes MUST be authenticated by a
  versioned HMAC preimage binding endpoint, channel, external id, timestamp,
  signature version and body. Missing, invalid, stale or placeholder secrets
  MUST fail with post-auth count zero.
- **R4 — Atomic verified admission:** Each valid signature MUST consume exactly
  one post-auth count in the same SQL transaction that classifies replay and
  writes the encrypted envelope/receipt/quarantine state. Transaction failure
  rolls back every post-auth effect but not the already consumed pre-auth count.
- **R5 — Replay/collision:** Same key+digest MUST link `DUPLICATE` to the first
  envelope without a second raw copy. Same key+different digest MUST atomically
  create a distinct encrypted envelope and quarantine linked to both records,
  without changing the original reservation. Concurrent races MUST be
  constraint/CAS safe.
- **R6 — Raw storage:** Raw bytes MUST be AES-256-GCM ciphertext in the same SQL
  row/transaction, with injected key authority, key id, nonce/tag, AAD and
  plaintext digest verification. A server-owned CSPRNG MUST generate a 96-bit
  nonce, and `(key_id, nonce)` MUST be unique in durable storage. A collision,
  generator failure or uniqueness conflict fails closed before reservation;
  concurrent writers cannot reuse a nonce. No external blob, filesystem
  staging, logs, HTTP echo, audit body or `messages.raw_payload` write is allowed.
- **R7 — Parse/quarantine:** Only post-R4 bytes may parse. Malformed,
  unsupported, ambiguous, unsafe-attachment, unavailable-scan, policy-drift or
  route-policy failures MUST be terminally quarantined with a closed reason and
  committed lineage; unavailable required quarantine MUST block routing.
- **R8 — Candidate:** A candidate MUST be closed, bounded, `RAW` and
  `UNTRUSTED_EXTERNAL`, preserve exact provenance, and carry no authoritative
  user, assignment, approval, confirmation or conversation mapping.
- **R9 — Service assertion:** Both internal directions MUST use closed
  `ServiceAssertionV1` canonical HMAC fields from DESIGN §5, maximum 60-second
  lifetime, allowlisted key window, exact audience/operation/body/idempotency
  binding and atomic nonce replay refusal. Missing validation infrastructure
  MUST fail before domain effects.
- **R10 — Core ingress:** Only `external_ingress.propose` may cross edge→core.
  It MUST create an actor-neutral proposal, never call internal `POST /messages`
  or satisfy later identity/permission/assignment/domain-lock/approval/audit/
  confirmation controls.
- **R11 — Outbound:** Only authenticated `outbound.deliver` commands built
  after core revalidation may enter the edge. The edge MUST bind prerequisite
  references and distinguish accepted/delivered/refused/rate-limited/unknown;
  unknown MUST block blind retry. BUILD uses a test-only evidence-ineligible
  fake and zero external sends.
- **R12 — Disclosure/health:** Public responses and telemetry MUST allowlist
  safe fields only. Readiness MUST separately reflect key registry, SQL store,
  nonce/rate store, quarantine sink and required ports.
- **R13 — Retention:** Ciphertext deletion and digest-only tombstone MUST be one
  transaction. A key MUST remain decryptable until its ciphertext is removed.
- **R14 — Dependency direction:** Edge domain MUST NOT import workspace-api,
  operations-ledger, AI/provider/RAG/retrieval packages or concrete adapters.
- **R15 — Invariant families:** Normative ingress family/digest is
  `P4C-INGRESS-TERMINAL-OUTCOMES` / `277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`.
  Normative outbound family/digest is `P4C-OUTBOUND-TERMINAL-OUTCOMES` /
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
  Matrix paths and machine-enforced pins are in
  `P4C_INTEGRATION_EDGE_INVARIANT_REFERENCE.json`; all model/schema/SQL
  emitters and mutation tests MUST conform to the pinned matrices.
- **R16 — Live proof:** Any test, roadmap closure, release gate, demo proof or
  public claim asserting CVF governance behavior—including risk, approval,
  phase gates, DLP, bypass detection, output validation, provider routing or
  audit updates—MUST use a separately authorized real provider API call with
  sanitized request/response recorded. Mock/static evidence is insufficient;
  BUILD remains zero-provider and SPEC authorizes no call.

## Acceptance criteria

- **AC-01:** Closed model/JSON-schema/SQL parity and unknown-field rejection.
- **AC-02:** Pre-auth invalid-signature flood proves N/N/0 pre/post counts and
  zero body work after exhaustion; concurrent boundary counts are exact.
- **AC-03:** Valid new/duplicate/collision/concurrent-reservation cases match
  R4/R5 and the invariant matrix with rollback/no-silent-consumption probes.
- **AC-04:** AES round-trip, AAD/tag/digest tamper, missing/rotated key,
  CSPRNG failure, injected nonce reuse, `(key_id, nonce)` collision under
  concurrent writers, transaction rollback and retention tombstone tests pass
  on in-memory, SQLite and disposable PostgreSQL evidence boundaries.
- **AC-05:** Every quarantine reason, unavailable sink/scan, release recheck and
  disclosure-negative probe passes without routing or raw leakage.
- **AC-06:** Service assertions reject wrong issuer/audience/op/path/body,
  expiry, nonce replay, inactive key and unavailable verifier; allowed ports
  cannot produce operational truth or bypass core controls.
- **AC-07:** Route/send definitive and ambiguous outcomes prove at-most-one
  attempt per attempt record, reconciliation before retry and no real adapter.
- **AC-08:** Dependency/import, secret/placeholder, log/receipt, file-size,
  session, catalog, invariant-family, repository and doctor gates pass.
- **AC-09:** Full non-live suite passes; database evidence is accurately bounded
  and cleaned. No provider/network/install/deployment occurs during BUILD.
- **AC-10:** Independent review recomputes both R15 digests, verifies both
  enforced pin symbols, samples a raw emitter result per matrix outcome and
  reports findings/waivers explicitly.

## Stop conditions

Stop on contract ambiguity, new external-effect/credential/dependency scope,
unavailable atomic persistence, matrix drift, third same-root repair round,
test failure, dirty-set breach or any need for provider/commit/push/deployment
authority.

## Disposition

`READY_FOR_INDEPENDENT_SPEC_REVIEW`. WORK_ORDER and BUILD remain unauthorized.
