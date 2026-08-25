# Independent SPEC Review — P4-C Integration Edge

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Reviewed phase: `SPEC` only
- Reviewer role: `INDEPENDENT_SPEC_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

The review compared `docs/specs/P4C_INTEGRATION_EDGE_SPEC.md`, registered
family `P4C-INGRESS-TERMINAL-OUTCOMES`, its invariant reference and registry
entry against the accepted DESIGN/final review, invariant schema/standard and
repository guard, AGENTS live-proof rule, and P4-C/P4-D/P4-E boundaries.

Independent universal-newline SHA-256 recomputation produced:

- matrix: `8baad29dc4a8fc7b10db93a62d0b9faacdee9f02a2805474f7334ade777a2f01`;
- DESIGN contract source: `b141320a5a4fc828c7d2b6d0a318009ce131e844e24537222c9174ae391a2137`.

Both match their recorded pins. `python scripts/check_invariant_families.py
--json` returned `PASS` with no diagnostics; its focused corpus returned
`35 passed, 2 skipped`. Session-state, catalog and workspace-doctor checks also
passed, with the retained bounded legacy-catalog warning. These deterministic
checks establish declared schema/registry/ownership consistency, not semantic
completeness against the DESIGN.

### Invariant-family proof fields

- Applicability: `APPLICABLE`; registered family
  `P4C-INGRESS-TERMINAL-OUTCOMES`.
- Matrix canonical digest: independently reproduced exactly as shown above.
- Declared emitter: `integration_edge.invariants:emit_ingress_terminal_receipt`
  (`REAL_SERVICE_EMITTER`); it is a future BUILD surface and was not imported or
  sampled during SPEC review.
- Declared evidence tests: `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`.
- Mutation exclusions: `RECURSE_NESTED_OBJECTS` for each of the six declared
  flat shapes; independent-review acknowledgment recorded, with no waiver.
- Evidence owner: future `IMPLEMENTATION_WORKER` return followed by independent
  `REVIEWER`; no BUILD has occurred and no matrix expectation was derived from
  BUILD output.

No provider call was authorized or needed for this contract review, which does
not claim that the specified governance behavior is implemented or governed.

## Numbered findings

1. **P4C-SPEC-REV-F1 — The ingress terminal family is not semantically
   exhaustive against the accepted DESIGN.** The matrix declares only six
   outcomes, but DESIGN/SPEC also require a post-auth rate-exhausted terminal
   outcome, an active-reservation retryable conflict, non-collision quarantine
   outcomes for parse/attachment/scan/policy failures, and definitive
   `ROUTE_REFUSED`. Those paths have different required/forbidden ids and exact
   route/count relations, yet no matrix shape owns them. R15 nevertheless
   requires model/schema/SQL emitters to conform to this family, so the current
   family can pass while adjacent terminal branches remain unmodelled. Expand
   the independent contract source and matrix to cover every ingress terminal
   outcome (including unavailable required stores/sinks where a receipt is
   permitted), then refresh all canonical digest pins and mutation obligations.

2. **P4C-SPEC-REV-F2 — The separately triggered outbound receipt family is
   unregistered.** R11 and accepted DESIGN define shared outbound command/
   delivery states with outcome-controlled fields, exact attempt relations and
   multiple model/schema/store surfaces. These independently satisfy the
   invariant-family applicability triggers, while the registered matrix's
   bounded claim explicitly covers ingress receipts only. Register a separate
   outbound terminal family or deliberately broaden the existing independent
   contract/matrix; do not leave this triggered surface outside a family and do
   not duplicate its rules in prose.

3. **P4C-SPEC-REV-F3 — The consumer reference does not pin the canonical
   matrix digest.** `P4C_INTEGRATION_EDGE_INVARIANT_REFERENCE.json` contains
   only `familyId` and `matrixPath`, and the sole ownership binding checks only
   `/familyId` with `JSON_REFERENCE`. The digest appears only in SPEC prose.
   Consequently, a matrix change can leave the machine reference and ownership
   guard green without invalidating the consumer pin required by the standard.
   Add an enforceable canonical-digest consumer field/binding and ensure SPEC,
   reference, registry/matrix proof and future Work Order all point to the same
   recomputable digest.

4. **P4C-SPEC-REV-F4 — R16 narrows the mandatory live-proof rule.** R16 applies
   a real provider call only to a "governance-behavior closure claim." AGENTS
   and the accepted DESIGN apply it to any test, roadmap closure, release gate,
   demo proof or public claim asserting CVF governance behavior. Restore that
   complete trigger family, keep the request/response receipt sanitized, and
   preserve separate authority for any consuming call. BUILD remains
   zero-provider and cannot itself support such a claim.

5. **P4C-SPEC-REV-F5 — AES-256-GCM nonce safety is not testable.** R6 requires
   a nonce/tag but does not require nonce uniqueness per encryption key or a
   fail-closed generation/allocation rule, and AC-04 has no nonce-reuse or
   collision probe. GCM nonce reuse under one key breaks the intended
   confidentiality/integrity boundary. Specify a server-owned nonce generation
   strategy, a uniqueness constraint or equivalent deterministic guarantee per
   key, failure behavior, and positive/negative concurrency tests.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted SPEC boundaries

Subject to the findings above, R1–R14 preserve the accepted edge/core/P4-D/
P4-E boundaries, dual rate order, collision lineage, same-row encrypted SQL
transaction, `ServiceAssertionV1` non-bypass contract, no-business-truth rule,
test-only adapter fake and failure/disclosure boundaries. The recorded matrix
and DESIGN source digests are accurate at this review snapshot.

## Disposition

`SPEC_REVIEW_CHANGES_REQUIRED`.

WORK_ORDER and BUILD remain unauthorized. Return only F1–F5 for bounded SPEC/
matrix/reference repair and independent rereview.

## Bounded rereview round 1 — P4C-SPEC-REV-F1..F5

- Rereview role: `INDEPENDENT_SPEC_REVIEWER`
- Rereview scope: repaired F1 through F5 only
- Rereview disposition: `SPEC_REVIEW_CHANGES_REQUIRED`
- Waivers: `NONE`

Independent universal-newline SHA-256 recomputation produced:

- ingress matrix:
  `e2018e6cdfa6d3ac03167a22c713095f4ab43d3631443f75a1ae7beb34586bdf`;
- outbound matrix:
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`;
- DESIGN contract source:
  `b141320a5a4fc828c7d2b6d0a318009ce131e844e24537222c9174ae391a2137`.

Both matrix digests match SPEC, the machine reference and the corresponding
symbols in `docs/specs/p4c_invariant_pins.py`. The production ownership guard
independently recomputes each owner digest and validates those symbols.
`python scripts/check_invariant_families.py --json` returned `PASS` with no
diagnostics; the focused invariant corpus returned `35 passed, 2 skipped`.

### Finding dispositions

1. **F1 REMAINS OPEN as P4C-SPEC-REV-F1-R1.** The expanded ingress matrix now
   covers post-auth rate refusal, active-reservation conflict, ordinary
   quarantine and definitive route refusal. It still cannot represent the
   accepted DESIGN §6 branch where a verified raw envelope is already
   preserved but required quarantine persistence is unavailable. DESIGN
   requires a sanitized fallback/error state and forbids both routing and a
   false successful-quarantine claim. The only general `QUARANTINED` shape
   requires `quarantine_id` and its reason domain omits quarantine-sink
   unavailability, so an emitter must either invent a nonexistent quarantine
   id or emit an outcome outside the matrix. Add a distinct terminal shape or
   outcome requiring the preserved `raw_envelope_id`, forbidding
   `quarantine_id`, fixing both counters to one and route attempts to zero, and
   include its mutation obligation and refreshed digest pins. Store-wide
   failure before any durable receipt need not be modelled as a receipt.
2. **F2 CLOSED.** `P4C-OUTBOUND-TERMINAL-OUTCOMES` is independently registered
   and covers the accepted outbound states and exact attempt relations, with a
   bounded no-real-adapter/no-provider claim.
3. **F3 CLOSED.** Both matrices bind through `CANONICAL_DIGEST` ownership to
   distinct Python symbols; the reference and SPEC currently reproduce those
   enforced values. Matrix drift fails the repository guard.
4. **F4 CLOSED.** R16 restores the full test/roadmap-closure/release-gate/demo/
   public-claim trigger family, requires a separately authorized real provider
   call and sanitized request/response evidence, rejects mock/static evidence,
   and keeps BUILD zero-provider.
5. **F5 CLOSED.** R6 now requires server-owned CSPRNG 96-bit nonces and durable
   `(key_id, nonce)` uniqueness with fail-closed collision/generator behavior;
   AC-04 requires reuse, collision and concurrent-writer probes across the
   bounded stores.

Fresh rehydration found canonical continuity consistent at
`p4c_integration_edge_spec_repair_ready_for_rereview`. Session-state and
invariant-family guards passed; workspace doctor returned 24 passes and the
retained bounded legacy-catalog warning. No provider call was needed or
authorized for this contract rereview, which makes no implemented-governance
claim.

## Current final disposition

`SPEC_REVIEW_CHANGES_REQUIRED`.

F2–F5 are closed without waiver. Return only `P4C-SPEC-REV-F1-R1` for bounded
matrix/SPEC-pin repair and independent rereview. WORK_ORDER and BUILD remain
unauthorized.

## Bounded rereview round 2 — P4C-SPEC-REV-F1-R1

- Rereview role: `INDEPENDENT_SPEC_REVIEWER`
- Rereview scope: residual `P4C-SPEC-REV-F1-R1` only
- Finding disposition: `P4C-SPEC-REV-F1-R1 CLOSED`
- Findings: `NONE`
- Waivers: `NONE`

The ingress matrix now contains a distinct
`QUARANTINE_PERSISTENCE_FAILED` terminal shape for the accepted branch where
the verified raw envelope is durable but quarantine persistence is
unavailable. It requires `outcome`, `reason`, `raw_envelope_id`,
`preauth_count`, `postauth_count` and `route_attempts`; fixes the reason to
`QUARANTINE_SINK_UNAVAILABLE`; requires a non-empty preserved
`raw_envelope_id`; forbids `quarantine_id`; and fixes the exact relations to
`preauth_count = 1`, `postauth_count = 1` and `route_attempts = 0`. Its
mutation obligation includes the flat-shape exclusion, so a false successful
quarantine receipt or a routed fallback cannot satisfy the family.

Independent universal-newline SHA-256 recomputation produced the refreshed
ingress digest
`277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`.
That exact value is aligned across the ingress matrix, SPEC R15, the machine
reference and `P4C_INGRESS_MATRIX_CANONICAL_DIGEST` in
`docs/specs/p4c_invariant_pins.py`; the ownership binding uses
`CANONICAL_DIGEST` and therefore recomputes the owner rather than trusting a
prose pin. The unchanged outbound digest remains
`41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.

Verification evidence at this rereview snapshot:

- `python scripts/check_invariant_families.py --json`: `PASS`, no diagnostics;
- focused invariant corpus: `35 passed, 2 skipped`;
- `python scripts/check_session_state.py`: `PASS`;
- `git diff --check`: clean;
- workspace doctor: 24 passes and the retained bounded legacy-catalog warning.

No provider call was needed or authorized: this is a contract-consistency
rereview and makes no implemented-governance claim. Earlier
`SPEC_REVIEW_CHANGES_REQUIRED` dispositions remain as historical review
evidence and are superseded by the final disposition below.

## Current final disposition after bounded rereview round 2

`SPEC_REVIEW_PASS`.

All P4-C SPEC review findings are closed without waiver. The next phase may
proceed only through the governed role/state transition; this review does not
authorize BUILD, provider use or external effects.

## Independent review — SPEC Amendment 1 / path 67

- Review date: `2026-08-25`
- Reviewer role: `INDEPENDENT_SPEC_AMENDMENT_REVIEWER`
- Scope: `docs/specs/P4C_INTEGRATION_EDGE_PATH67_SPEC_AMENDMENT_2026-08-25.md`
- Findings: `NONE`
- Waivers: `NONE`

The amendment accurately converts the accepted path-67 DESIGN into testable
requirements. It adds only `knowledge/manifest.json` to the original 66-path
ceiling and permits exactly these current-to-next source-pin replacements:

- registry `3505654a...e30e36` -> `4a7c6211...5710f`;
- `AGENTS.md` `afce67b2...2b5770` -> `6b2629d2...3fecf`;
- `.cvf/manifest.json` `8cd22f2a...9c0da` -> `2f319767...8d79a`.

Independent byte hashing reproduced all three complete target values recorded
in A1-R2. A full scan of the 16 Knowledge source pins found exactly those three
current mismatches. The pre-existing `IMPLEMENTATION_STATUS.json` pin already
matches its source at
`c416f4cb642c757fe6766991e927efe99e0156292202fa3639af0d9d4d42fd93`
and remains explicitly outside P4-C authorship; A1-R3 forbids every other
path-67 byte change and any validator, catalog, invariant, runtime or test
weakening.

The two named Knowledge verification commands are valid. In the required
pre-BUILD snapshot, `python scripts/check_project_knowledge.py` and the exact
repository-pack positive test fail closed on the stale-pin state; this is the
condition A1-R2 repairs, not evidence of a contract gap. Post-edit PASS is a
mandatory return condition alongside the inherited focused/full non-live and
repository gates. Session-state and invariant-family guards pass, and the
parent SPEC R1-R16, AC-01..AC-10 and canonical matrix digests remain unchanged.

The amendment adds no provider, external HTTP, credential, install,
deployment, production database, commit or push effect. No provider call was
required or authorized for this deterministic specification review, which
makes no implemented-governance claim.

### Amendment disposition

`SPEC_AMENDMENT_REVIEW_PASS`.

The Work Order may receive only the corresponding exact-67 amendment through
the next recorded governed phase/role transition. BUILD remains stopped until
that Work Order amendment receives independent authorization PASS.
