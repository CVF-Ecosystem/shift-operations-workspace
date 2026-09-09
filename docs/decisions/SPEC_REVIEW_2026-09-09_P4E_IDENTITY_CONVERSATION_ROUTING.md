# Independent SPEC Review - P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Review role: `SPEC_REVIEWER`
- Phase reviewed: `SPEC`
- Risk: `R2`
- Date: `2026-09-09`
- Reviewed artifact: `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md`
- Reviewed artifact SHA-256:
  `79bc7bbb730d846adcf479fc38be35b42a3664080bb2da6271010d0bbd8cdddb`
- Consumed DESIGN digest (recomputed):
  `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9`
- Reviewed at repository HEAD: `ff715d0129ff9dfb6fa5489cf1edbc047d5ac670`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`

## Independence and review boundary

This reviewer did not author or repair the SPEC, the three invariant matrices,
the pin module, or the registry entries. All actions were read-only except the
creation of this reviewer-owned artifact. No WORK_ORDER, BUILD, product source,
schema, migration, dependency, credential, installation, deployment, commit,
push, provider call, or product-network call was performed. This review makes
no runtime, live-proof, deployment, or production-readiness claim.

## 1. Digest and pin verification (independently recomputed)

All four pinned digests were recomputed from the working tree and match the
values asserted in the SPEC, the handoff, and `docs/specs/p4e_invariant_pins.py`.

| Artifact | Recomputed SHA-256 | Matches pin |
|---|---|---|
| `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` | `2d0975a3...b9c397b9` | YES |
| `docs/cvf/invariants/p4e-mapping-action-outcomes.json` | `9edccf4d...9b859b38ef` | YES |
| `docs/cvf/invariants/p4e-identity-resolution-outcomes.json` | `a460f6d3...2bda7e67036` | YES |
| `docs/cvf/invariants/p4e-placement-outcomes.json` | `e8500e6b...a549a2913584c` | YES |

The consumed DESIGN digest also equals the digest recorded as the accepted
repaired DESIGN in the predecessor handoff
`SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md`. The
`contractSources` entry inside each of the three matrices carries the same
DESIGN digest, so matrix-to-DESIGN provenance is internally consistent.

## 2. Registry and guard verification (independently rerun)

- `python scripts/check_invariant_families.py` returned
  `INVARIANT FAMILY CHECK: PASS` (exit 0).
- All three families are present in `docs/cvf/invariants/registry.json` with
  `ownerRole: SPEC_AUTHOR`, `risk: R2`, `lifecycle: ACTIVE`, and matrix paths
  that resolve.
- Ownership bindings in all three matrices point at
  `docs/specs/p4e_invariant_pins.py` with `CANONICAL_DIGEST` strategy, and the
  three digest symbols named in the matrices exist in that module.

## 3. Focused suite recount (independent, contradicts handoff)

The handoff `SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC_2026-09-09.md`
claims `focused invariant suite: 72 passed, 2 skipped`.

Rerunning exactly the two `evidenceTestPaths` declared by all three P4-E
matrices returned a different count:

```text
python -m pytest tests/unit/test_invariant_family_contract.py \
  tests/integration/test_invariant_family_repository_guard.py -q
35 passed, 2 skipped
```

The `72` figure is therefore not reproducible from the evidence paths the
matrices themselves declare. This is recorded as `P4E-SPEC-REV-F1`. It is an
evidence-citation defect, not a gate failure: the checks that were rerun all
pass. Note also that `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
exists in the repository but is named by no P4-E matrix `evidenceTestPaths`
entry, so the declared evidence surface is narrower than the actual guard
surface.

## 4. Findings

### `P4E-SPEC-REV-F1` - Unreproducible focused-suite count (MAJOR, evidence)

**Where:** handoff `## Verification`, `focused invariant suite: 72 passed, 2 skipped`.

**Problem:** The two evidence paths declared by all three matrices yield
`35 passed, 2 skipped` at HEAD `ff715d0`. No stated command in the handoff or
SPEC reproduces `72`. Under the CVF rule that a reviewer must recompute cited
counts rather than trust a self-report, an unreproducible count cannot carry
into a Work Order as settled evidence.

**Required repair:** Either record the exact command whose output is
`72 passed, 2 skipped` (including every path and selector), or correct the
handoff to the reproducible count and the command that produces it.

### `P4E-SPEC-REV-F2` - R12 contradicts the placement matrix REFUSED shape (MAJOR, contract)

**Where:** SPEC section 5, R12, final sentence; versus
`docs/cvf/invariants/p4e-placement-outcomes.json`, shape `P4E_PLACEMENT_REFUSED`.

**Problem:** R12 states that unknown claim state or digest mismatch "refuses
without a placement decision." The placement matrix makes `REFUSED` a terminal
decision shape whose `requiredFields` include `decision_id` and whose
`decision_count` is `const 1` with `work_complete` `const true`. SPEC R15
reinforces the matrix: "`decision_count` is exactly one for every persisted
terminal `PLACED`, `FALLBACK`, or `REFUSED` decision."

So the SPEC asserts both that a digest-mismatch refusal produces no placement
decision and that every `REFUSED` is a persisted decision with a decision id.
These cannot both hold. This is exactly the class of ambiguity a BUILD worker
must not resolve unilaterally: one reading persists a terminal refusal row, the
other leaves the work item in a non-terminal state with no row, and the two
produce different durable state and different audit history.

**Required repair:** Decide explicitly which outcome covers unknown-claim-state
and digest-mismatch. If it is terminal, R12 must stop saying "without a
placement decision." If it is genuinely non-terminal, the matrix needs a
distinct outcome or reason (the `RETRY_PENDING` reason enum currently offers
only `AUTHORITY_STORE_UNAVAILABLE`, `TARGET_STORE_UNAVAILABLE`,
`TRANSACTION_ROLLED_BACK`, `CLAIM_RECOVERABLE`, none of which is a digest
mismatch), and R15's "exactly one for every terminal REFUSED" must be
reconciled.

### `P4E-SPEC-REV-F3` - `PRIVACY_DELETE` receipt cannot carry its required reason (MAJOR, contract)

**Where:** SPEC R19 versus `p4e-mapping-action-outcomes.json`, shape
`P4E_ACTION_APPLIED`.

**Problem:** R19 requires the privacy-delete command to carry a `reason`
("requiring at least the fresh stored `responsible_manager` role, expected
version, reason, idempotency, and actor-bound audit"). `PRIVACY_DELETE` is in
the `action` enum of the mapping-action matrix. But the `APPLIED` shape lists
`reason` in `forbiddenFields`, and so does `IDEMPOTENT_REPLAY`. A successful
privacy delete therefore has no matrix-legal place to surface the reason it was
required to carry, and the SPEC does not say whether the reason is a
command-only input excluded from the receipt or a receipt field.

**Required repair:** State explicitly that the privacy-delete `reason` is a
command input recorded only in the actor-bound audit and deliberately excluded
from the sanitized receipt (and say why, given R19's disclosure limits), or add
a conditional rule to the matrix. Note that resolving this by adding a field to
the matrix changes its digest and re-pins all consumers.

### `P4E-SPEC-REV-F4` - `SECRET_ERASURE_FAILED` is unreachable through any declared action (MINOR, contract)

**Where:** `p4e-mapping-action-outcomes.json`, `P4E_ACTION_REFUSED` reason enum,
value `SECRET_ERASURE_FAILED`; versus SPEC R19 rotation paragraph and R7 action
table.

**Problem:** R19 says failure to erase or purge "fails the rotation closed and
blocks retirement." Key rotation/retirement is not one of the eight actions in
the matrix `action` enum (`PROPOSE`, `CONFIRM`, `REJECT`, `REVOKE`, `CORRECT`,
`BIND`, `REPLACE_BINDING`, `PRIVACY_DELETE`) and is not in the R7 permission
table. A `REFUSED` receipt requires an `action`, so `SECRET_ERASURE_FAILED` can
only be emitted by attributing it to an unrelated action.

**Required repair:** Either designate which action surfaces this reason (and add
the corresponding governed action plus minimum role to R7), or remove the reason
from the enum and state where rotation failure is reported instead. AC-13
currently asserts that "erasure/purge failure blocks retirement" without naming
the receipt that carries it.

### `P4E-SPEC-REV-F5` - No explicit R-to-AC traceability map (MINOR, reviewability)

**Where:** SPEC sections 3-7 (21 numbered requirements R1-R21) versus section 8
(15 acceptance criteria AC-01..AC-15).

**Problem:** AC-15 obliges the independent reviewer to check "every R/AC
mapping," but the SPEC provides no such mapping. With 21 requirements against 15
criteria the correspondence is many-to-one and must be reconstructed by reading.
Reconstructing it, I could not find acceptance coverage specific to R10's
retirement clause - "the existing process-local external-ingress repository
shall be retired from production composition; no second live proposal store
may remain."
AC-06 proves durable admission and preserved proposal id; AC-11 proves import
direction. Neither asserts that
`apps/workspace-api/src/workspace_api/external_ingress/repository.py`
(`InMemoryExternalIngressRepository`, which exists at HEAD) is out of production
composition. A negative retirement claim needs its own check.

**Required repair:** Add an explicit R-to-AC table, and add an acceptance
criterion that proves no second live proposal store remains in production
composition.

### `P4E-SPEC-REV-F6` - Unsupported-target scaffolds contradict the closed target set (MINOR, boundary)

**Where:** SPEC section 1 and R14 versus the working tree.

**Problem:** SPEC declares `CUSTOMER`, `CUSTOMER_CONTACT`, and `VESSEL`
unsupported. The repository already contains
`packages/conversation-routing/customer-router/` and
`packages/conversation-routing/vessel-router/` (README-only module-boundary
scaffolds whose text says implementation must follow locked contracts), and
`packages/identity-mapping/README.md` still describes mapping external
identities into "internal users/customer contacts." These are pre-existing
scaffolds, not SPEC-introduced, and they contain no code - hence MINOR. But a
BUILD worker enumerating package paths will meet directories the SPEC forbids
populating, and the identity-mapping README states a broader scope than the SPEC
grants.

**Required repair:** Have the Work Order state that these scaffold paths are
explicitly out of scope and must remain empty, or correct the stale README scope
line, so the constraint is not left to worker inference.

### `P4E-SPEC-REV-F7` - Inconsistent applicability-trigger vocabulary (COSMETIC)

**Where:** `applicabilityTriggers` across the three P4-E matrices.

**Problem:** The same ordinal carries different names: `TRIGGER_1_SHARED_RECEIPT_MODEL`
(mapping) versus `TRIGGER_1_SHARED_RESULT_MODEL` (identity, placement); and
`TRIGGER_5` appears as three distinct values (`_LIFECYCLE_TRANSITIONS`,
`_ADJACENT_FAMILY_FINDINGS`, `_RETRY_TERMINAL_FAMILY`) where the P4-C and P4-D
precedent families use no `TRIGGER_5` at all. The schema types this field as a
free-form string array, so this is not a guard failure. It weakens the ordinals
as a shared vocabulary across families.

**Required repair:** Optional. Normalize the ordinal names or drop the numeric
prefixes.

## 5. What the SPEC gets right

These were checked and are recorded as accepted, not merely unexamined:

- **Fail-closed direction is consistent.** Every ambiguity path in R15 lands on
  `REFUSED` or `RETRY_PENDING`, never on a privileged route. The matrices enforce
  this structurally: `forbiddenFields` on `FALLBACK`/`REFUSED` exclude
  `mapping_id`, `binding_id`, `target_kind`, `target_id`, and `conversation_key`,
  so a non-positive outcome cannot carry target authority even by construction
  error.
- **The JWT-role exclusion is correctly specified.** R7's seven-step order
  (verify subject, load authoritative user, reconstruct principal from stored
  role, permission, scope/SoD, in-transaction relock and rerun, then atomic
  persist plus audit) faithfully implements DESIGN section 5 and correctly
  states the JWT role claim is never an authorization input.
- **The R7 role table is consistent with the live registry.** `_ROLE_RANK` in
  `packages/cvf-runtime/src/cvf_runtime/permission.py` orders
  `viewer < operator < shift_supervisor < responsible_manager <
  authorized_executive`, and the SPEC's minimum roles sit correctly against the
  existing precedent bars (`event.confirm`/`shift.freeze` at `shift_supervisor`).
  R7's ban on endpoint-local role comparison is well-aimed: the existing
  `apps/workspace-api/src/workspace_api/api/staffing/router.py` does exactly the
  local `has_authority(...)` comparison that R7 forbids for P4-E, so the
  prohibition is a real constraint against an existing in-repo pattern, not a
  hypothetical one.
- **Two-human separation is properly closed.** R8 requires the confirmer to be
  neither proposer nor target user, with fresh transient re-entry and key
  recomputation, and correction repeats the flow. AC-04 tests the self-confirm
  refusal explicitly.
- **The two-transaction inbox honestly disclaims exactly-once.** R11 states
  there is no cross-step atomicity or exactly-once claim, and R12 bounds
  attempts at three with a five-minute CAS-guarded stale-claim recovery and
  no daemon or queue. This matches DESIGN section 6 without inflating it.
- **Secret handling is specified to the byte level.** R2/R3/R19 keep raw sender
  bytes and key bytes out of persistence, logs, receipts, audit, telemetry, and
  candidate content; AC-03 makes that a negative scan across seven surfaces.
- **Retention uses an injected clock.** R19 measures from persisted UTC
  timestamps via one injected clock and forbids ambient system-clock calls in
  production paths, with AC-13 testing exact boundary instants - this closes the
  usual flaky-boundary hole.
- **The live-evidence boundary is correctly drawn.** R21 keeps BUILD at zero
  provider calls and states that any CVF-governs-provider-action claim needs a
  separately authorized real call. The SPEC claims only deterministic and
  disposable-database closure.
- **Work Order constraints are already scoped.** Section 9 names
  `WORKER_MUST_NOT_COMMIT`, one implementation worker, an independent reviewer,
  and stop conditions on path expansion, dependency installation, and matrix
  drift.

## 6. Disposition

`SPEC_REVIEW_CHANGES_REQUIRED`

- Findings: 7 (`P4E-SPEC-REV-F1` .. `P4E-SPEC-REV-F7`)
- Severity: MAJOR 3 (F1, F2, F3), MINOR 3 (F4, F5, F6), COSMETIC 1 (F7)
- Waivers: NONE

F2 and F3 are blocking because they are contract self-contradictions inside the
normative body: a BUILD worker cannot satisfy both readings, and resolving them
during BUILD would be an unreviewed contract decision. F1 is blocking because an
unreproducible evidence count must not carry into a Work Order.

This reviewer does not authorize the Work Order transition. Repairs to F1-F6
should be made within the documentation-only boundary by the SPEC author, and a
rereview - by a reviewer independent of the repair - should confirm closure.
Note that any repair touching a matrix file changes its digest and requires
repinning `docs/specs/p4e_invariant_pins.py` and rerunning the family guard.

WORK_ORDER, BUILD, provider/live execution, deployment, Phase 5, catalog schema
migration, XR1 repair, and external-repository absorption remain unauthorized.

## 7. Claim boundary

This artifact is an independent SPEC review of documentation only. It asserts no
runtime behavior, no provider-governance claim, no deployment or public-sync
claim, and no production readiness. The verification it reports covers digest
recomputation, registry/guard execution, and a focused deterministic test rerun
at HEAD `ff715d0129ff9dfb6fa5489cf1edbc047d5ac670`.
