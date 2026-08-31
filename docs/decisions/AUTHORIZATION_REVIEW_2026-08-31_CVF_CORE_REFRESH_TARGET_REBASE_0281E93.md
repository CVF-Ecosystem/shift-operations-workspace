# Independent Authorization Review — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase reviewed: `WORK_ORDER`
- Risk: `R2`
- Role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Date: `2026-08-31`
- Reviewed Work Order:
  `docs/work_orders/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-31_WORK_ORDER.md`
- Reviewed Work Order SHA-256:
  `9e44eb5540fec4b7b3c35e035bf57d26a9be0be2c5d92dbd2963ef7946f7e8b5`
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`
- Findings: `AUTH-REV-F1 OPEN`
- Waivers: `NONE`
- BUILD external-effect authority: `NOT_GRANTED`

## Review boundary and independence

The reviewer did not author or repair the Work Order, DESIGN, SPEC, matrix,
pin, registry entry or their reviews. No doctor, fetch, reconciler,
initializer, provider call, credential access, package installation, Core,
workspace-root, pin, binding, continuity, product, runtime or database
mutation, deployment, release, commit or push occurred. This review artifact
is the reviewer's only repository mutation and intentionally does not
self-hash.

The review used local objects and allowlisted reads. However, the initial
rehydration command also ran broad `git status --short`. Its output enumerated
the downstream untracked set and surfaced the protected assessment's path.
The assessment contents were not opened, read, hashed, staged or used, but
the enumeration itself violates the Work Order's explicit no-inventory rule.
That review-window defect is recorded as `AUTH-REV-F1`; it is not waived or
silently converted to zero contact.

## Exact lineage, policy and source identities

All Work Order-bound raw hashes independently recomputed exactly:

| Artifact | Recomputed SHA-256 |
|---|---|
| Accepted INTAKE | `28e1160993d2638554bdb810dd36f393eebb65db62b47b8f92b8049fc290ba53` |
| INTAKE review | `4c754b7cc47ef247453075e0633848534d121959aba7fb845d49f12975da1b8c` |
| Accepted DESIGN | `1fc8c00dd19bfd08a4b185f1fdc41fbe58991a7006248a593a5fc6fc371cb8b5` |
| DESIGN review | `78eaf8c9e7e01af721c877ed6aaa89b6446baea40e3ef05df85f8772d1088c56` |
| Final SPEC | `7264fb1e142062be9c60cbfd486ec93e671fe384347fd98567c22346d4e527c4` |
| Final SPEC review/rereview | `82727d1b54acccc640a179bda09691d4f104feb968e06065d9bb6a0865884bba` |
| Matrix raw/canonical | `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c` |
| Matrix pin file | `855b02058e1a358cb02187dd852cf8b6c0e47f6d6d4d5642b7b27a093dada852` |
| Invariant registry | `3022d323782e2fd3cf18f377f4293b43e1637a1f14ccef96a1b3717a2ac9f0e2` |
| CVF policy | `c8a28fb11accc2ae3d21054636f6c32046e1547203be8b4044901f658ed3a863` |
| Invariant-family standard | `c360655acb89c6fc8e412f87289d5ef990f62c5795605a95b1d4327cd6dff402` |
| Invariant-family schema | `7313f9c9f631eacf160f2ce0ad2fdef5757eb10427fdb3574354f9a3564714e0` |

The final DESIGN and SPEC dispositions are `DESIGN_REVIEW_PASS` and
`SPEC_REVIEW_PASS`, findings/waivers `NONE/NONE`; the SPEC rereview closes
`SPEC-REV-F1`. Policy retains risk ceiling `R2`, the seven-step control chain,
`liveGovernanceEvidenceRequired: true` and `mockAllowedOnlyForUi: true`.

The P0 source/preimage hashes also recomputed exactly: contract
`19616ecaf9bbdb35738a1622fa790c7f0c0e24d5afdbbae154d402528aa78497`,
generator `d5f2e13328874dc41946fe73334f8c34eb55619db3b101781869d448b54a82ae`,
ownership validator
`71ec4c547d72c9e4d3d6a8951aaf889f78e8459849106f143beb6298b523aac7`,
oracle `f9bf70a8c2adee0097c9faed7e1b2f0e554aa1fa3d6021a0ed346275de0f6cdc`,
strict harness
`cae96b6eef4ab9d5bd4e0a8a58c02d05c04591d68b835a1be356f140c5a4adb9`,
pattern test
`49dba6d885c054170fd2a48905e5ee0ebdd33b9dcb7a507b74d6c5af8b0f14a7`
and repository-guard fixture
`44cdf8451cef01bfe58239563afe3aaf162b92906812c2c5725a3925e39079e6`.
The downstream initializer is
`bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`.

## Target, tools, profile and local topology

Read-only local Git checks found clean Core
`HEAD == a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`, local
`origin/main == 0281e93bab4a75083973eb7242fd2bc8f65055d3`, ancestry exactly
`0` ahead / `6` behind, and both objects present. The old-to-target delta is
`256` tracked paths, `173` outside Markdown/docs-only. The remote and resolved
workspace/project/Core locations exactly match the Work Order. Manifest,
generated AGENTS header and ignored binding all retain the old full pin;
project staged count is zero.

At both old pin and target, the sanctioned Core identities are unchanged:

- reconciler raw/blob:
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` /
  `4b705c6bf7b10bda62520dca488ecb453a4f4945`;
- doctor raw/blob:
  `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` /
  `2ad83efee05c738fec40aa1779929da07f3d1c8c`;
- new-workspace raw/blob:
  `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` /
  `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7`; and
- operation tree:
  `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6`.

The active selector is `operator-local` and its selector file recomputes to
`f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855`.

## Exact P0 and invariant-family proof

- **Applicability:** `TRIGGERED` for registered family
  `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-OUTCOMES-2026-08-30`, owner
  `SPEC_AUTHOR`, risk `R2`, lifecycle `ACTIVE`.
- **Matrix / digest:** the sole matrix named by the Work Order; raw and
  canonical digest both
  `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c`.
- **Consumer:**
  `docs/specs/cvf_core_refresh_target_rebase_0281e93_2026_08_30_invariant_pin.py`;
  its symbol equals that digest and the registry has exactly one owner entry.
- **Adapter:**
  `CVF_CORE_REFRESH_TARGET_REBASE_0281E93_READ_ONLY_P0_ADAPTER_V1`.
- **Evidence tests:** `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`.
- **Mutation exclusions:** `NONE`.
- **Evidence owner:** the role owning the applicable receipt/review under the
  Work Order's non-overlapping role windows.

The LF-normalized UTF-8 payload bytes strictly between the Work Order markers
recompute to
`0cd29a56f7186a5c030aae8d365d3f778d787d27a6797eab6e12226639bdb925`.
They were executed directly in memory with `python -B -c`, no payload file,
network or provider action. Fresh output was:

- exclusive positives `8/8`;
- generator/oracle exact-set mutations `1257/1257` with no duplicate id;
- temporal judgments `40/40` (`38` accepted, `2` rejected);
- six lower-case SHA witnesses and literal-`"x"` rejection `6/6` on both
  surfaces; and
- correlated BUILD-success outcome-selection rejection `4/4`.

One synthesized raw positive for each of the eight outcomes was separately
sampled. Every sample matched only its own shape on both repository and
independent strict surfaces. The matrix predates BUILD and no expectation was
derived from implementation output.

`python scripts/check_invariant_families.py --json` returned `PASS`. The
required focused command reproduced the disclosed parked fixture baseline:
`28 passed, 2 skipped, 7 failed`, with all seven failures caused by the known
disposable-repository omission of mutation-generator/oracle helpers. It is
not represented as unrestricted test success and was not repaired or
suppressed.

## Effects, ceilings, rollback and boundaries

The six attempt-3 lifecycle paths are unique, contained and absent. The
ordered workspace-root ceiling contains exactly `17/17` unique paths and
matches the reconciler plus public-safe wrapper installer. The initial worker
ceiling is exactly `13` unique tracked paths: two pins, nine shared carriers
and two worker artifacts, plus one ignored binding. The completion reviewer
owns one tracked artifact. Conditional repair owns exactly 11 existing
pin/shared carriers plus one JSON create (`12` tracked) and one ignored
binding effect; the terminal rereviewer owns one Markdown create.

Inspection of the frozen scripts confirms the successful graph is exactly
one reconciler clone, one scoped two-pin bridge, one initializer fetch and the
initializer-owned doctor fetch: ordered Git network prefix
`P1/P2/P3 == RECONCILER_CLONE/INITIALIZER_FETCH/INITIALIZER_DOCTOR_FETCH`.
No manual fetch, overlay, project-manifest update, worker doctor, retry or
retarget is admitted. Checkpoints correctly require the immediate
replacement target and final five-way Core/ref/pin/binding equality.

The preimage contract covers old Core, `17` roots, `2` pins, `9` shared
carriers and `1` binding with present/absent state, restoration source and
order. Worker-time rollback is preservation-first and requires complete
`17/2/9/1` restoration before success. Reviewer target movement freezes the
three prior attempt artifacts; only a distinct repair worker may restore from
BUILD preimages, and a distinct rereviewer owns terminal hashes. Complete and
incomplete rollback outcomes are disjoint; unavailable observations may not
be fabricated.

The three P4-E checkpoint preimages recomputed to
`23ce2ae4c71e0db29c1d673baef0c1d269791524776f987466d7ad177514fe61`,
`a48e6f3a5fb2c1137608fb1c99a15f28cb6cbc98032bf9ac99fdf62b0aad9ac7`
and `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9`.
They remain byte-protected at `DESIGN_REVIEW_PASS`. Fixture source/tests,
matrix, pin and evidence remain outside edit scope; the operational fixture
status still selects the freeze-blocked BUILD-success shape. XR1 remains
open. No outcome authorizes P4-E, fixture, product/runtime/database,
installation, deployment, release, commit or push work.

Session/mirror, Project Knowledge, invariant-family, catalog and file-size
guards passed. Stop conditions, no-retry/no-retarget behavior, provider/mock
zero, credential zero, role separation, evidence hash ownership and the
bounded non-AI-governance claim match the accepted DESIGN and final SPEC.

## Finding

### `AUTH-REV-F1` — forbidden broad-untracked inventory in reviewer window

The reviewer's initial local-state command used broad `git status --short`.
That enumerated untracked downstream paths and surfaced the protected
assessment path. This conflicts directly with Work Order sections 1, 5 and
13, which forbid broad downstream untracked inventory and exclude the
protected assessment from inventory by every role.

No content was opened, read, hashed, staged or used and no external effect
occurred, but the review cannot truthfully claim the required zero-inventory
method. This is a review-window failure, not evidence that the Work Order's
technical contract is defective.

Required resolution: a fresh distinct independent authorization reviewer must
rereview the exact unchanged Work Order using only allowlisted path checks and
tracked/staged probes that do not enumerate the untracked set. That reviewer
must independently recompute the exact Work Order hash, P0 payload/results,
lineage/tool/profile hashes, target/ancestry, ceilings, outcomes and protected
boundaries. No Work Order repair or waiver is authorized by this finding.

## Waivers

`NONE`.

## Disposition and next authority boundary

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED` because `AUTH-REV-F1` remains open.
The Work Order's substantive target, P0, matrix, command/network graph,
preimage, rollback, evidence, role, stop, commit and claim contracts otherwise
recomputed consistently with the accepted DESIGN and SPEC.

BUILD/reconcile remains unauthorized. Even after a clean
`AUTHORIZATION_REVIEW_PASS`, exact external-effect approval is still required
and must identify this Work Order path and exact SHA-256, old pin, target and
enumerated reconciler/two-pin/initializer network and filesystem graph. No
doctor, fetch, reconcile, BUILD, commit or push is authorized by this review.
