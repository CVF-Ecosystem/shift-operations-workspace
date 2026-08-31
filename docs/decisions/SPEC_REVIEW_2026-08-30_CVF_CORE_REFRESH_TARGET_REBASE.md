# Independent SPEC Review — CVF Public-Core Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Review date: `2026-08-30`
- Phase reviewed: `SPEC`
- Risk: `R2`
- Role: `INDEPENDENT_SPEC_REVIEWER`
- Final reviewed SPEC raw/canonical SHA-256:
  `f8c2de27e5aca67f53bb530cd9bbce17abc1f3b65a56ad7bfe5ba0a1fb044161`
- Final reviewed matrix raw/canonical SHA-256:
  `dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc`
- Final reviewed machine-pin raw/canonical SHA-256:
  `4ce97c9823ae63447ffe158ae9b0d81ac7690a19c019b368ce00da5be8793b66`
- Reviewed registry raw/canonical SHA-256:
  `e22195a46528feff89ee7f622ac1d964a0a94e9acc8b85f82a93de77c57525c5`
- Final disposition: `SPEC_REVIEW_PASS`
- Final findings: `NONE` (`TARGET-REBASE-SPEC-REV-F1` closed on rereview)
- Waivers: `NONE`

## Review boundary and method

The reviewer did not author the SPEC, matrix, pin or registry entry. Review
used only explicit local allowlisted reads, local Git objects and deterministic
repository commands. It performed no network, doctor, reconciler, initializer,
provider call, credential access, package installation, hidden-Core/workspace-
root/product/database/deployment mutation, continuity edit, commit or push.
The protected operator assessment was not opened, read, hashed, staged,
inventoried or used, and no broad untracked inventory was performed. Creation
of this review document is the reviewer's sole mutation.

Raw and universal-newline canonical hashes were independently recomputed for
the four accepted phase artifacts, SPEC, matrix, pin and registry. The four
phase hashes exactly match R1 and the matrix contract-source bindings. The
restored Core is clean at `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`;
the existing local `origin/main` is
`d7860138350130d6d105826ce186f1beeaba3c2d`, with the expected public remote.
No fetch was used.

## Contract and boundary evidence

The accepted tool/profile bindings recompute exactly: reconciler raw/blob
`96ac0cce...`/`4b705c6b...`, doctor `2410bbab...`/`2ad83efe...`, new-workspace
`7e5567c5...`/`5f311a1a...`, operation tree `23fe8bd3...`, downstream
initializer `bb37b162...`, and active `operator-local` profile `f51bacd2...`.
The three Core blobs and operation tree are equal at old pin and frozen target.

The SPEC contains the exact ordered `17` unique workspace-root targets and the
exact `13` unique initial-worker tracked paths, categorized `2` pin, `9` shared
continuity and `2` worker-evidence carriers. The conditional repair ceiling is
the same `11` pin/shared carriers plus one conditional JSON create, for at most
`12` tracked paths and one ignored binding. All six attempt-2 evidence paths
are distinct and their ownership/pre-state lifecycle is non-circular: worker
JSON/Markdown do not self- or cross-hash; the completion review owns their
final hashes; conditional rollback JSON does not self-hash; terminal rereview
owns readable predecessor hashes and does not self-hash.

The frozen remote, old pin/target, sanctioned reconciler-to-two-pin-to-
initializer graph, three-operation success network sequence, executed failure
prefixes, no-retry rule and reviewer-only doctor windows are consistent with
the accepted DESIGN. Role windows remain non-concurrent. P4-E stays parked at
`DESIGN_REVIEW_PASS`; protected-assessment, provider/credential, product/
database, deployment, commit/push and live-evidence claim boundaries remain
closed. The prose references the matrix for per-outcome rules and does not
create a second outcome-field owner.

## Invariant-family proof

- **Applicability decision:** `TRIGGERED`; registered family
  `CVF-CORE-REFRESH-TARGET-REBASE-OUTCOMES-2026-08-30`.
- **Matrix id / canonical digest:** family above at
  `d81e6b81764f6dfdefbad57f92d057a7034a1b880fd043085733913e982e3de0`.
- **Adapter / test paths:** synthetic deterministic identity
  `CVF_CORE_REFRESH_TARGET_REBASE_INLINE_ADAPTER_V3`; declared evidence tests
  `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`.
- **Mutation exclusions:** none.
- **Exact commands:** `python scripts/check_invariant_families.py --json` and
  `python -m pytest -q tests/unit/test_invariant_family_contract.py
  tests/integration/test_invariant_family_repository_guard.py`.
- **Evidence owner:** `INDEPENDENT_SPEC_REVIEWER` for this review receipt;
  later BUILD/terminal evidence ownership remains as declared by SPEC R10-R12.
- **Reviewer recomputation:** canonical digest, registry identity/path/owner/
  risk/lifecycle, `CANONICAL_DIGEST` pin binding, all seven raw in-memory
  positives, complete generated corpus, two independent validator surfaces,
  exclusivity and temporal domains were recomputed. No BUILD output exists or
  supplied an expectation.

All `7/7` positives matched exactly one intended shape. Canonical positive
SHA-256 samples by matrix order are `5ecf72db...`, `12f3f56b...`,
`c674454e...`, `9fa92eac...`, `a177a292...`, `c927ed19...` and
`5c196510...`. Mutation counts were respectively `75`, `93`, `89`, `73`,
`79`, `138` and `115`; both validators rejected all `662/662`, and the
independently generated required-id basis matched the generated corpus with no
duplicate or excluded operator. The focused temporal cross-product checked all
nine initial failure-stage/prefix tokens across both initial failure shapes and
the union of eleven rollback-stage/verifier tokens across both incomplete
shapes: `40/40` judgments matched their declared domains (`38` accepted, `2`
cross-owner tokens rejected).

## Numbered findings

1. **`TARGET-REBASE-SPEC-REV-F1` — complete rollback projections omit
   mandatory clean-stage and evidence-hash invariants.** SPEC R13 requires the
   applicable repository/scoped-diff and staged-zero guards, while R5 requires
   the initial worker JSON and Markdown to contain no self-hash or cross-hash.
   `SUCCESS_VALID` encodes all three facts, and the accepted predecessor
   `FAILURE_ROLLED_BACK_VALID` also encoded them. The successor
   `FAILURE_ROLLED_BACK_VALID` declares none of `staged_count`,
   `self_hash_count` or `cross_hash_count`; because the projection is closed,
   injecting any of those truthful zero facts is rejected. Separately,
   `REVIEW_TARGET_MOVEMENT_ROLLED_BACK_VALID` cannot carry
   `staged_count == 0` after its rollback-only repair; the same probe is
   rejected. Thus a mechanically valid complete-rollback projection can omit
   a required final gate, while a receipt that records that gate cannot match
   the sole semantic matrix. This is an adjacent invariant-family regression,
   not cured by `7/7`/`662/662` mechanical conformance.

   Repair the matrix so both complete-rollback shapes require and constrain
   `staged_count` to zero, and so the initial-worker complete-rollback shape
   also requires and constrains `self_hash_count` and `cross_hash_count` to
   zero. Preserve honest incomplete-state rules. Then recompute the canonical
   digest, update the machine pin and every SPEC digest reference, rerun all
   positives/mutations and the focused temporal checks, and return the bounded
   repair for independent SPEC rereview.

## Waivers and adjacent findings

- Waivers: `NONE`.
- Adjacent findings beyond F1: `NONE`.

## Deterministic checks

- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family repository guard: `PASS`, diagnostics empty.
- Focused invariant tests: `35 passed, 2 skipped`.
- Ownership binding and canonical pin: `PASS`.
- Seven-outcome exclusivity and generated corpus: `7/7`, `662/662`.
- Focused temporal judgments: `40/40`, zero mismatch.
- Allowlisted scoped diff check before receipt: `PASS`; scoped staged set: zero.

## Final disposition

`SPEC_REVIEW_CHANGES_REQUIRED` — F1 open; waivers `NONE`.

Return only F1 to a declared `REPAIR_WORKER`, then route the recomputed SPEC,
matrix and pin to an independent SPEC rereviewer. Work Order, BUILD,
reconciler/doctor/network, Core/workspace-root/pin/binding mutation, P4-E SPEC,
provider/credential use, installation, product/database change, deployment,
commit and push remain unauthorized.

---

## Independent SPEC rereview — bounded F1 closure — 2026-08-30

- Role: `INDEPENDENT_SPEC_REVIEWER`
- Prior review pre-append raw SHA-256:
  `e68bd7e7a676b1d7ed62c319e86691abdea841f740e39cdc71b8f135815946a7`
- Repaired SPEC raw/canonical SHA-256:
  `f8c2de27e5aca67f53bb530cd9bbce17abc1f3b65a56ad7bfe5ba0a1fb044161`
- Repaired matrix raw/canonical SHA-256:
  `dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc`
- Repaired machine-pin raw/canonical SHA-256:
  `4ce97c9823ae63447ffe158ae9b0d81ac7690a19c019b368ce00da5be8793b66`
- Registry raw/canonical SHA-256:
  `e22195a46528feff89ee7f622ac1d964a0a94e9acc8b85f82a93de77c57525c5`
- Disposition: `SPEC_REVIEW_PASS`
- Findings: `NONE`
- Waivers: `NONE`

### Rereview boundary

This rereview rehydrated current canonical continuity and inspected only the
returned F1 repair, accepted phase artifacts, existing review receipt,
invariant-family machinery and local allowlisted state. It performed no
network, doctor, reconciler, initializer, provider, credential, installation,
Core/workspace-root/product/database/deployment mutation, continuity edit,
commit or push. The protected assessment remained untouched and uninventoried;
no broad untracked inventory was performed. This append and the final header
disposition are the rereviewer's only mutation.

### F1 closure

`TARGET-REBASE-SPEC-REV-F1` is **`CLOSED`**.

- `FAILURE_ROLLED_BACK_VALID` now requires `staged_count`,
  `self_hash_count` and `cross_hash_count`; each has integer constant zero and
  its own counter-equality relation to zero.
- `REVIEW_TARGET_MOVEMENT_ROLLED_BACK_VALID` now requires `staged_count`, with
  integer constant zero and a counter-equality relation to zero.
- Both complete-rollback positives accept those truthful facts. Deletion,
  minus-one, plus-one, zero/nonzero flip where applicable, and wrong-type
  mutations are rejected by both validator surfaces.
- Removing exactly the returned F1 field/domain/relation additions from the
  repaired matrix in memory reconstructs the prior matrix byte-for-byte at
  canonical SHA-256 `d81e6b81764f6dfdefbad57f92d057a7034a1b880fd043085733913e982e3de0`.
  This proves the matrix change is bounded to F1. The registry is unchanged.
- Both incomplete rollback shapes retain their prior raw positive hashes
  (`9fa92eac...` and `5c196510...`), required staged/P4-E/blocking observation
  states and rejection of injected Core/pin hashes, staged-zero, exact restore
  counts or P4-E-success facts. No honest-incomplete surface was weakened.

The repaired digest independently recomputes to `dc0c3529...f4cc`, exactly
matching both SPEC references and the statically extracted machine pin. The
registry family/path/owner/risk/lifecycle and `CANONICAL_DIGEST` ownership
binding pass.

### Recomputed conformance

All seven raw in-memory positives match exactly one intended shape on both the
repository matcher and the independently implemented closed-object validator.
Per-shape mutation counts are `75`, `93`, `107`, `73`, `79`, `144` and `115`.
The independently generated obligation-id basis equals the emitted corpus with
no duplicate or exclusion, and both validators reject all `686/686` mutations.

The focused temporal cross-product is unchanged: all nine initial failure-
stage/prefix tokens across the two initial failure shapes plus the union of
eleven rollback-stage/verifier tokens across the two incomplete shapes produce
`40/40` correct judgments (`38` accepted, two cross-owner tokens rejected).

### Deterministic rereview checks

- Session state/mirror: `PASS`.
- Project Knowledge: `PASS`.
- Invariant-family repository guard: `PASS`, diagnostics empty.
- Focused invariant tests: `35 passed, 2 skipped`.
- Matrix ownership/digest pin: `PASS`.
- Positive exclusivity and full corpus: `7/7`, `686/686`.
- Focused temporal judgments: `40/40`, zero mismatch.
- Allowlisted diff check: `PASS`; allowlisted staged set: zero.

### Final rereview disposition

`SPEC_REVIEW_PASS` — F1 closed; final findings `NONE`, waivers `NONE`.

The ORCHESTRATOR may open WORK_ORDER only through an explicit phase transition.
This review grants no Work Order, BUILD, reconciler/doctor/network, Core/root/
pin/binding mutation, P4-E SPEC, provider/credential, installation, product/
database, deployment, commit or push authority.
