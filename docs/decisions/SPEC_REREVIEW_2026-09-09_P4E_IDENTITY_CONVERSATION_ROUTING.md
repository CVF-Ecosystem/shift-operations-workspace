# Independent SPEC Rereview (Gen 2) - P4-E Identity and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Review role: `SPEC_REVIEWER`
- Phase reviewed: `SPEC`
- Generation: `2` (rereview of repairs to Generation 1 findings)
- Risk: `R2`
- Date: `2026-09-09`
- Reviewed artifact: `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md`
- Reviewed artifact SHA-256 (recomputed):
  `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618`
- Generation 1 review SHA-256 (recomputed, unchanged):
  `a4ee2f643186ca11be7d08c8e555aa55372c63b20d58bb3ab81b24e5b83d17f8`
- Rework response reviewed:
  `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC_REWORK_2026-09-09.md`
- Reviewed at repository HEAD: `e367bc996e6fceaff08d23af34c2d5d8dada0ded`
- Disposition: `SPEC_REVIEW_PASS`

## Independence and review boundary

This reviewer authored the Generation 1 review and did not author or perform any
repair. The repairs under review were made by the SPEC author. All actions in
this generation were read-only except the creation of this reviewer-owned
artifact. No WORK_ORDER, BUILD, product source, schema, migration, dependency,
credential, installation, deployment, commit, push, provider call, or
product-network call was performed. This review makes no runtime, live-proof,
deployment, or production-readiness claim.

The author explicitly declined to self-close the findings and required
independent recomputation before any disposition change. That is the correct
posture and is honored here: every row below was reverified from the working
tree, not accepted from the rework ledger.

## 1. Integrity of the Generation 1 record

The Generation 1 review is byte-unchanged at
`a4ee2f643186ca11be7d08c8e555aa55372c63b20d58bb3ab81b24e5b83d17f8`. `git show`
confirms it entered the repository at `e367bc9` as a pure 293-line addition with
zero deletions and no subsequent modifying commit. The prior review therefore
survives as independent evidence rather than as a rewritten record.

## 2. Digest and pin reverification (independently recomputed)

| Artifact | Recomputed SHA-256 | Matches rework claim | Matches pin module |
|---|---|---|---|
| `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md` | `de3af4a9...fdc90618` | YES | n/a |
| `docs/cvf/invariants/p4e-mapping-action-outcomes.json` | `ea2af812...4d003e1a` | YES | YES |
| `docs/cvf/invariants/p4e-identity-resolution-outcomes.json` | `4ef64cf1...1c0000bdc` | YES | YES |
| `docs/cvf/invariants/p4e-placement-outcomes.json` | `fd351b66...a8ec8cc56` | YES | YES |

All three matrices were modified by the repair, all three digests changed, and
`docs/specs/p4e_invariant_pins.py` was repinned to the new values. The repin
obligation flagged at the close of the Generation 1 review was met.

`python scripts/check_invariant_families.py` returned
`INVARIANT FAMILY CHECK: PASS` (exit 0) after the repin.

## 3. Finding-by-finding verification

### `P4E-SPEC-REV-F1` - CLOSED

Both cited commands were rerun independently at HEAD `e367bc9`:

```text
python -m pytest -q tests/unit/test_invariant_family_contract.py \
  tests/integration/test_invariant_family_repository_guard.py
-> 35 passed, 2 skipped

python -m pytest -q tests/unit/test_invariant_family_contract.py \
  tests/unit/test_invariant_family_contract_repair_round2.py \
  tests/integration/test_invariant_family_repository_guard.py \
  tests/integration/test_invariant_family_repository_guard_repair_round2.py
-> 72 passed, 2 skipped
```

Both counts reproduce exactly, and both commands are now recorded verbatim in
the active handoff alongside their results.

The author's qualification is accepted and this reviewer records the correction:
the `72` figure was neither fabricated nor wrong. It came from a genuine
four-path extended regression. The Generation 1 defect was that the handoff
presented it as the "focused invariant suite" without naming the command, so it
could not be distinguished from the two-path declared-evidence surface. The
Generation 1 section heading "contradicts handoff" overstated this; "provenance
not recorded" is the accurate characterization. The MAJOR severity remains
appropriate, because an evidence count whose command is unrecorded cannot be
independently recomputed, which is the standard the rule exists to enforce.

### `P4E-SPEC-REV-F2` - CLOSED

R12 no longer says "without a placement decision." It now makes unknown claim
state and proposal-lineage digest mismatch terminal persisted `REFUSED`
decisions, and states inline that each carries `decision_id`,
`decision_count=1`, and `work_complete=true` "as required by the placement
matrix."

The placement matrix `P4E_PLACEMENT_REFUSED` reason enum was verified to now
contain `UNKNOWN_CLAIM_STATE` and `LINEAGE_DIGEST_MISMATCH`, so both conditions
are emittable. R15's "exactly one for every persisted terminal `PLACED`,
`FALLBACK`, or `REFUSED` decision" is now consistent with R12 rather than
contradicting it. `RETRY_PENDING` was correctly left alone: its reason enum
still carries only the four genuinely transient conditions, so the repair did
not blur the terminal/transient boundary to make the contradiction disappear.

The chosen resolution is the safer of the two available: a digest mismatch now
leaves a durable, auditable terminal record instead of a silently unresolved
work item.

### `P4E-SPEC-REV-F3` - CLOSED

R19 now states that the operator-supplied deletion reason is "a command input
written only to the restricted actor-bound audit record," deliberately excluded
from the sanitized `APPLIED` and `IDEMPOTENT_REPLAY` receipts "to avoid
disclosing privacy-request content," and that those shapes therefore continue to
forbid `reason`.

The mapping-action matrix was verified unchanged on this point: `APPLIED` and
`IDEMPOTENT_REPLAY` still list `reason` in `forbiddenFields`. This is the
correct direction of repair. Adding a conditional receipt field would have
widened the disclosure surface for exactly the content R19 is meant to protect;
the SPEC instead closed the ambiguity in prose while leaving the receipt
contract tight. The stated rationale means a BUILD worker no longer has to infer
the intent.

### `P4E-SPEC-REV-F4` - CLOSED

`SECRET_ERASURE_FAILED` was verified absent from the `P4E_ACTION_REFUSED` reason
enum, which now holds ten reasons all reachable through the eight declared
actions. R19 adds that rotation "is a secret-authority operation, not a mapping
action and not a P4-E management API operation," and that failure surfaces as a
sanitized `TOKEN_KEY_RETIREMENT_BLOCKED` secret-authority audit/readiness record,
"never as a `P4E-MAPPING-ACTION-OUTCOMES` receipt."

The author's wording qualification is accepted: "unreachable" was too
categorical as a diagnosis. The substantive defect - an enum value with no
normative action binding - was real and is now removed at the root by separating
the two authority surfaces rather than by inventing a ninth action. R7's
permission table correctly did not grow, since rotation is not a management API
operation.

### `P4E-SPEC-REV-F5` - CLOSED

A complete `R-to-AC traceability` table was added covering R1 through R21 with no
gaps. Spot-checking the rows against the SPEC body, the assignments are
substantive rather than nominal (for example R8 maps to AC-04, which is the
criterion that actually tests propose/confirm separation and target-self-confirm
refusal).

AC-16 was added and directly discharges R10's negative retirement claim by name:
it requires composition and negative-import tests proving
`InMemoryExternalIngressRepository` is test-only, that the process-local P4-C
proposal repository is absent from production composition, and that Operations
Ledger is the sole live proposal/placement persistence owner. R10 and R18 both
now cite AC-16. This is the specific gap Generation 1 identified, closed with a
criterion that names the exact symbol at issue.

### `P4E-SPEC-REV-F6` - CLOSED

Verified at all four surfaces:

- SPEC R18 now states both scaffold directories "remain documentation-only
  scaffolds and are excluded from P4-E BUILD ownership" and "must receive no
  runtime code, dependency, configuration, schema, or composition change."
- `packages/conversation-routing/customer-router/README.md` and
  `packages/conversation-routing/vessel-router/README.md` each now carry the
  explicit P4-E v1 exclusion.
- `packages/identity-mapping/README.md` no longer claims customer-contact scope;
  it now reads "internal users only" with customer-contact authority deferred.
- SPEC section 9 requires the Work Order to exclude both directories explicitly.

The author's framing is accepted: empty scaffolds were never themselves a
contract violation. The repair correctly treats this as scope hardening so the
constraint is not left to worker inference.

### `P4E-SPEC-REV-F7` - CLOSED

All three families now share one vocabulary: `TRIGGER_1_SHARED_OUTCOME_MODEL_CONTRACT`,
`TRIGGER_2_OUTCOME_CONTROLS_FIELDS`, `TRIGGER_3_EXACT_COUNTER_OR_RELATION`,
`TRIGGER_4_MULTIPLE_VALIDATOR_OR_SERIALIZATION_SURFACES`, and
`TRIGGER_5_COUPLED_ARTIFACTS`. The divergent `TRIGGER_1_SHARED_RECEIPT_MODEL`
variant and the three conflicting `TRIGGER_5_*` aliases are gone. The identity
family correctly omits `TRIGGER_3`, which it does not claim.

This reviewer accepts the author's note that the defect is closer to MINOR than
COSMETIC, and records it without retroactively altering the Generation 1
severity, which remains as originally written.

## 4. Regression check on the repair itself

The repair was examined for scope creep and for new contradictions introduced
while closing the old ones:

- The full SPEC diff is confined to the three re-pinned digests, the R12
  rewrite, the R18 scaffold paragraph, the R19 privacy-reason and rotation
  paragraphs, AC-16, the traceability table, the Work Order exclusion sentence,
  and the disposition line. No unrelated normative requirement was altered.
- No requirement was weakened to make a finding disappear. Every repair adds a
  constraint or removes an unreachable value; none removes an obligation.
- The commit `e367bc9` touches documentation, matrices, pins, READMEs, and
  continuity surfaces only. No product source, application schema, database
  migration, or dependency file appears in its 20-file stat.
- `git diff --check` is clean; the working tree has no uncommitted drift.
- The three matrices remain mutually consistent: the placement family still
  consumes but does not duplicate mapping-family rules, and no outcome gained a
  field that another surface forbids.

## 5. Disposition

`SPEC_REVIEW_PASS`

- Generation 1 findings: 7
- Closed in Generation 2: 7 (`P4E-SPEC-REV-F1` .. `P4E-SPEC-REV-F7`)
- Open findings: NONE
- New findings raised in Generation 2: NONE
- Waivers: NONE

All seven repairs were independently reverified from the working tree. The two
blocking contract self-contradictions (F2, F3) are resolved in the direction
that tightens rather than loosens the contract, and the blocking evidence defect
(F1) now reproduces exactly from recorded commands.

Under the Generation 1 stated condition, this rereview closes the findings.
This reviewer authored Generation 1 but performed none of the repairs, and
every claim in the rework ledger was recomputed rather than accepted. If
project policy requires that a rereview be performed by a reviewer who did not
author the preceding generation, this artifact should be treated as
reviewer-recomputed evidence supporting that separate rereview rather than as
the sole closure authority. That is a governance routing decision for the
ORCHESTRATOR, not a finding against the SPEC.

The SPEC at `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618`
is fit to authorize a separate Work Order authoring transition. Work Order
authoring authority is granted by the ORCHESTRATOR, not by this artifact.

BUILD, provider/live execution, deployment, Phase 5, catalog schema migration,
XR1 repair, and external-repository absorption remain unauthorized.

## 6. Carry-forward notes for the Work Order

Not findings; recorded so they are not lost between phases.

- The Work Order must carry the R18/section-9 scaffold exclusion explicitly, as
  the SPEC now requires.
- AC-16 is a negative composition claim. It needs a real import/composition
  probe, not a comment asserting the repository is test-only.
- `TOKEN_KEY_RETIREMENT_BLOCKED` now names a record produced outside the three
  P4-E families. The Work Order should identify which surface owns it, so it
  does not become an unowned artifact at BUILD time.

## 7. Claim boundary

This artifact is an independent SPEC rereview of documentation only. It asserts
no runtime behavior, no provider-governance claim, no deployment or public-sync
claim, and no production readiness. The verification it reports covers digest
recomputation, pin reconciliation, registry/guard execution, two deterministic
test-command reproductions, matrix enum inspection, and repair-diff scope review
at HEAD `e367bc996e6fceaff08d23af34c2d5d8dada0ded`.
