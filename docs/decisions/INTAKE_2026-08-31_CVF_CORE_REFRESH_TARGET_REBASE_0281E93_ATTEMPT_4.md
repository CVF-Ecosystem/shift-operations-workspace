# INTAKE — CVF Public-Core Exact-Target Rebase 0281e93 — Attempt 4

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-2026-08-31`
- Phase: `INTAKE`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_INTAKE_REVIEW`
- Active role: `INTAKE_AUTHOR`
- Proposed old Core/pin:
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Proposed frozen target:
  `0281e93bab4a75083973eb7242fd2bc8f65055d3`
- Parked product lane: P4-E at `DESIGN_REVIEW_PASS`

## 1. Successor authority and phase boundary

After attempt 3 reached reviewed
`FREEZE / CLOSED_BOUNDED_ZERO_EFFECT_PREFLIGHT_REFUSAL`, the operator
instructed `next`. This opens a fresh successor INTAKE only. Attempt 4 is not
a retry, continuation, repair or rerun of attempt 3, and it does not inherit
attempt 3's BUILD authority, external-effect approval, mutable path ceilings,
evidence lifecycle or execution window.

This INTAKE may be independently reviewed using exact local allowlisted reads.
It authorizes no doctor, fetch, reconciler, initializer, network/provider/
credential use, wrapper execution, evidence-directory creation, hidden-Core,
workspace-root, pin, binding, continuity, fixture, product, runtime or database
mutation, installation, deployment, release, commit or push. DESIGN, SPEC,
WORK_ORDER and BUILD require their own explicit phase transitions.

Attempt 4 remains R2 because any later BUILD would use public Git network and
mutate the hidden Core, workspace governance kit, downstream pin carriers and
ignored local binding. BUILD/reconcile remains prohibited until an exact
attempt-4 Work Order has passed independent authorization review and a later
external-effect approval identifies that exact Work Order path and SHA-256,
old pin, target, commands, network graph, effect ceilings, lifecycle paths and
role assignment.

## 2. Fixed predecessor truth and accepted correction

The immutable predecessor anchors are:

| Artifact | Current raw SHA-256 | Meaning retained by this INTAKE |
|---|---|---|
| `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md` | `004ce65b653abe23270d8da01528584eef52aeccd06a5e706ba6925ab0b59239` | Independent `REVIEW_PASS_ZERO_EFFECT_PREFLIGHT_REFUSAL`, findings/waivers `NONE/NONE` |
| `docs/work_orders/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-31_WORK_ORDER.md` | `9e44eb5540fec4b7b3c35e035bf57d26a9be0be2c5d92dbd2963ef7946f7e8b5` | Exact attempt-3 Work Order; immutable input, not attempt-4 authority |
| `SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30.md` | `1853933e85713203d80f906b7c71cb52ee01f4ee01ae138db6888094d605faa4` | Closed attempt-3 continuity |

Attempt 3 stopped before P0 because the implementation worker constructed a
temporary inline PowerShell wrapper whose statement-form `if` was parsed as a
command. The wrapper was not embedded or retained in the Work Order bytes.
The accepted provenance correction is therefore that the failure belongs to
the worker-composed ephemeral control wrapper, not to Work Order bytes at
`9e44eb55...`.

P0, network, reconciler, pin bridge, initializer, root, downstream and binding
effects were all zero; no rollback was required; the six attempt-3 lifecycle
paths were absent before the completion reviewer created its one review path.
Target `0281e93...` was not adopted. Attempt 3 may not be retried or repaired
in place, and none of its paths or artifacts may be repurposed by attempt 4.

## 3. Current local target, ancestry, delta and pin truth

Fresh allowlisted local checks, without doctor or fetch, establish:

- hidden Core is tracked-clean at
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`;
- public remote is exactly
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`;
- local `refs/remotes/origin/main` is exactly
  `0281e93bab4a75083973eb7242fd2bc8f65055d3`, and both old and target objects
  exist locally as commits;
- old pin versus target is exactly `0` commits ahead and `6` behind;
- the cumulative tracked delta is `256` paths, with `173` outside the fixed
  Markdown/docs-only class, where a path is inside that class when it is
  Markdown or under `docs/` or `documentation/`;
- `.cvf/manifest.json`, the generated `AGENTS.md` header and ignored
  `.cvf/local-binding.json` all retain the old full pin; and
- project staged count is zero. The downstream worktree contains existing
  governed work and is not claimed clean; broad untracked inventory is
  prohibited.

`0281e93...` is a frozen proposal for this INTAKE, not an adopted pin. Any
local or advertised target movement, ancestry change, remote change or missing
object before later authorized execution is `TARGET_DRIFT`; it fails closed
and requires a new target decision. No agent may retarget attempt 4 in place.

## 4. Frozen tool and selector facts

Selected sanctioned surfaces are byte/object-identical at the old pin and
target:

| Surface | Raw SHA-256 | Git blob/tree at old and target |
|---|---|---|
| Core reconciler `scripts/update_cvf_workspace_public_core.ps1` | `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` | `4b705c6bf7b10bda62520dca488ecb453a4f4945` |
| Core doctor `scripts/check_cvf_workspace_agent_enforcement.ps1` | `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` | `2ad83efee05c738fec40aa1779929da07f3d1c8c` |
| Core `scripts/new-cvf-workspace.ps1` | `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` | `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7` |
| Core `governance/toolkit/05_OPERATION` | n/a | `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6` |
| Downstream `scripts/initialize_cvf_clone.ps1` | `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8` | n/a |
| Active `CVF_RULE_PACKS/ACTIVE_RULE_PACK.json` selector | `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855` | `operator-local` |

These facts establish intake feasibility only. Any change in a selected tool,
tree, selector, policy, target or eventual effect graph before BUILD is
`TOOL_OR_EFFECT_DRIFT` and cannot be waived or refreshed silently.

## 5. Mandatory retained-wrapper successor intent

Attempt 4 exists to remove the ephemeral-control ambiguity that caused the
zero-effect refusal. DESIGN and SPEC must make all of the following mandatory:

1. The execution/preflight wrapper is retained as independently reviewable
   bytes. The preferred artifact class is a tracked script; DESIGN may select
   another retained repository-native artifact class only with an explicit
   rationale, ownership and path ceiling.
2. The retained wrapper has one exact raw SHA-256 bound by the SPEC, exact
   Work Order and independent authorization review. The worker may invoke only
   those accepted bytes; it may not compose, translate or repair a temporary
   inline control wrapper.
3. Before any external-effect authority is eligible, an independent reviewer
   must verify the wrapper's syntax/parse result and a no-effect rehearsal of
   its control flow. The rehearsal must prove no network/provider/credential,
   Core/root/pin/binding/evidence-directory or continuity effect, and its
   command, environment, expected output and exit semantics must themselves be
   exact and reviewable.
4. BUILD must re-hash the retained wrapper and fail closed before any effect
   on mismatch, parse ambiguity, rehearsal drift or command substitution.
   Worker-authored aliases, alternate invocations, copied snippets and
   ephemeral control logic are prohibited.
5. Because the retained wrapper couples command bytes, parse/rehearsal proof,
   outcome contracts and multiple validator surfaces at R2, SPEC must apply
   `docs/cvf/INVARIANT_FAMILY_STANDARD.md`: register a collision-free
   attempt-4 family/matrix and digest pin if triggered, or record a reviewed
   `NOT_APPLICABLE` determination without copying matrix rules into prose.

This INTAKE selects the retained/hash-bound requirement, not the final wrapper
implementation or command graph. Those exact details belong to DESIGN, SPEC
and the independently reviewed attempt-4 Work Order.

## 6. New lifecycle, preservation, preimages and rollback

DESIGN must define a complete, collision-free attempt-4 lifecycle whose every
directory, receipt, worker return, completion review, conditional rollback and
rereview path contains an unambiguous `ATTEMPT_4` identity. Before later
execution, all future paths must be resolved under their authorized
containment roots, independently reviewed, proven absent and hash-bound in the
exact Work Order. Attempt-1, attempt-2 and attempt-3 paths, fixture-repair and
protocol-exception artifacts are immutable historical evidence; no path may
be overwritten, renamed, moved, used as scratch storage or reinterpreted.

The exact Work Order must require recoverable preimages before any effect for
the old hidden Core, every declared workspace-root target, every downstream
pin and shared carrier, ignored binding, retained wrapper and protected parked
artifacts. Each preimage records resolved path, containment, `PRESENT` plus raw
hash or `ABSENT`, restoration source and deterministic restoration order.
Failure after start must preserve the observed failure first, then restore
only from those accepted preimages and independently verify exact restoration.
Unreadable or incomplete restoration remains an honest incomplete outcome;
unavailable hashes or counters must never be fabricated.

There is exactly one attempt-4 execution. No preflight rerun after failure,
reconciliation retry, wrapper hotfix, alternate command, in-attempt repair or
retarget is allowed. Any failure before start is a zero-effect refusal. Any
failure after start must follow the matrix-owned preservation/rollback outcome
and stop. A future successor requires fresh INTAKE and new lifecycle paths.

## 7. Parked and protected state

The completion review for attempt 3 independently retained the reviewed
workspace-root baseline at `17/17` and these three P4-E hashes at `3/3`:

| Parked P4-E artifact | SHA-256 |
|---|---|
| `SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md` | `23ce2ae4c71e0db29c1d673baef0c1d269791524776f987466d7ad177514fe61` |
| `docs/decisions/INTAKE_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` | `a48e6f3a5fb2c1137608fb1c99a15f28cb6cbc98032bf9ac99fdf62b0aad9ac7` |
| `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` | `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9` |

P4-E remains byte-protected at `DESIGN_REVIEW_PASS`; XR1 sibling historical-
object debt remains unresolved. The inherited fixture baseline remains
`28 passed, 2 skipped, 7 failed`, with fixture repair status
`AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`; attempt 4 may neither call the
fixture-specific top-level run nor repair, suppress or reclassify those
failures.

The protected operator assessment remains excluded from open, read, hash,
name, inventory, stage and use. This INTAKE does not disclose its path. Every
later role must retain zero protected-state contacts and must not use broad
downstream untracked inventory as proof. Product/runtime/database, catalog,
prior evidence and unrelated governed work remain outside the change scope.

## 8. Acceptance criteria for independent INTAKE review

Independent review must use local allowlisted reads only and must verify:

1. attempt 4 is a fresh successor, not an attempt-3 retry or in-place repair;
2. R2, phase order and the absence of current BUILD/external-effect authority;
3. exact old pin, target, public remote, local object presence, clean old Core,
   old pins/binding, staged zero, `0/6` ancestry and `256/173` delta facts;
4. raw/blob/tree identities for the sanctioned tools, downstream initializer
   and active `operator-local` selector;
5. predecessor Work Order and completion-review hashes and the accepted
   worker-wrapper provenance correction;
6. the mandatory retained, exact-hash-bound wrapper; independent parse/syntax
   and no-effect rehearsal before external authority; and the prohibition on
   worker-composed ephemeral control wrappers;
7. collision-free attempt-4 lifecycle, exact preimages, preservation-first
   rollback, no-retry/no-retarget and invariant-family applicability duties;
8. immutable prior evidence, `17/17` root baseline, `3/3` P4-E artifacts,
   parked `28/2/7` fixture state, protected-assessment exclusion and dirty-
   worktree preservation boundaries; and
9. findings and waivers explicitly recorded.

The review must not run doctor, fetch, reconciler, initializer, the prior
wrapper, P0, provider calls or fixture tests, and must not create any attempt-4
execution/evidence path.

## 9. Claim boundary and next governed move

This artifact proves only that a bounded successor proposal exists and that
its current local intake facts and mandatory design constraints are explicit.
It does not prove successful preflight, P0, wrapper correctness, target
adoption, Core freshness, doctor PASS, fixture closure, P4-E progression, XR1
repair, downstream adoption of the 256-path Core delta, AI/agent governance,
provider behavior, deployment or production readiness. No provider call is
required for this repository-maintenance INTAKE; mock output cannot support an
AI-governance claim.

Next governed move: a distinct `INDEPENDENT_INTAKE_REVIEWER` reviews this
exact artifact. DESIGN remains unauthorized until that review passes and an
explicit phase transition is recorded. WORK_ORDER, BUILD, doctor/fetch,
reconcile, wrapper execution, Core/root/pin/binding mutation, fixture repair,
commit and push remain prohibited.
