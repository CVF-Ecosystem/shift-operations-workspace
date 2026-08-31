# Active Handoff — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Date: `2026-08-29`
- Risk: `R2`
- Phase: `FREEZE`
- Status: `CLOSED_BOUNDED_FAILURE_ROLLED_BACK`
- Active role: `CLOSER/SESSION_SYNC_STEWARD`

## Authority acknowledgment

After the P4-E DESIGN rereview passed, final doctor detected local/pinned Core
`a7a797d` behind public `origin/main` `06c3d040`. The operator answered
`tiếp tục` to the explicit request to open a fresh governed Core reconciliation
INTAKE before P4-E SPEC. This grants INTAKE documentation/review authority
only; it grants no hidden-Core/root mutation, network, later phase, product,
provider, credential, install, deployment, commit or push authority.

## Current truth

The clean hidden Core is `0` ahead / `1` behind the frozen observed public
target. The one-commit delta changes 190 Core paths, including runtime and
governance source, while the downstream workspace-kit/reconciler surface is
unchanged. Downstream `HEAD == origin/main == a8e2ad8`; staged set is empty.

Fresh INTAKE is
`docs/decisions/INTAKE_2026-08-29_CVF_CORE_REFRESH.md`. P4-E remains parked at
accepted `DESIGN_REVIEW_PASS`; XR1 debt remains separately parked.

Independent review returned `INTAKE_REVIEW_PASS`, findings/waivers
`NONE/NONE`. Reviewed INTAKE SHA-256 is
`a86b2d2d4a93e003fe3a2c5a6bebba7e7ef723a6e4352f42aa77c3dbba87cf76`.

The operator then answered `next`, recording the explicit INTAKE-to-DESIGN
transition. `docs/decisions/DESIGN_2026-08-29_CVF_CORE_REFRESH.md` selects the
bootstrap-native two-script sequence, preservation-first rollback, exact
17-root/13-worker ceilings, three-operation success graph, reviewer-movement
rollback route and one triggered invariant family. No external effect occurred.

The first independent DESIGN review found F1 (absent evidence-path rollback).
Repair closed F1; rereview found F2 (self-referential evidence hashes). A
second bounded repair assigned final worker-evidence hashes to independent
terminal review. Fresh rereview returned `DESIGN_REVIEW_PASS`: F1/F2 closed,
final findings/waivers `NONE/NONE`. Accepted DESIGN SHA-256 is
`2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443`.

The operator assigned standing ORCHESTRATOR/REVIEWER authority to progress
through CVF documentation/review gates with independent subagents without
repeated same-scope prompts. This recorded the DESIGN-to-SPEC transition but
does not grant BUILD external effects. Fresh SPEC and registered invariant
family `CVF-CORE-REFRESH-OUTCOMES-2026-08-29` entered review.

Independent SPEC review returned `SPEC_REVIEW_CHANGES_REQUIRED`, findings
F1-F4 and waivers `NONE`. F1-F3 require later SPEC/matrix repair. F4 exposed
an impossible reviewer-time target-movement evidence lifecycle and therefore
returned the tranche to bounded DESIGN. The new DESIGN amendment preserves
the immutable successful worker evidence and target-movement completion review,
adds one rollback-only JSON owned by a distinct `REPAIR_WORKER`, and adds one
separately owned terminal rereview receipt. No external effect occurred.

Independent amendment review found one wording/ownership defect: the pins,
shared continuity carriers and binding form an intentional temporal
intersection rather than disjoint role ceilings. Bounded repair defined the
closed post-movement ownership window. Fresh rereview returned
`DESIGN_AMENDMENT_REVIEW_PASS`; F1 closed, findings/waivers `NONE/NONE`.

Returned SPEC F1-F4 were repaired across the SPEC, sole invariant matrix and
machine digest pin. Repaired SPEC raw SHA-256 is
`03932a375516ff100e452a40c92fa4886e5e4b1bb10488d446dc8faa162b4f01`;
matrix canonical digest is
`5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`.
The first rereview closed F1/F2 but retained F3/F4. The second repair encodes
rollback-stage/verifier time as one closed token and removes self-owning
conditional evidence failure. Local conformance accepted 5/5 positives,
rejected all 400 one-fact mutations and all 40 stage/state cross-product cases.

Final SPEC rereview returned `SPEC_REVIEW_PASS`: F1-F4 closed, final findings/
waivers `NONE/NONE`; review SHA-256 is
`5b77e40c103cdab1a648a06d60595cc0a07aaeb65e856688c36d664e265b5890`.
Standing documentation/review authority records the explicit SPEC-to-
WORK_ORDER transition. The bounded Work Order SHA-256 is
`6498b5cbd49f98caa368f719190d01fb62348af1ca2cee5478df0d1f731425d6`.
This transition does not authorize BUILD or any external effect.

Independent authorization review found F1: complete rollback verifier wording
was optional despite SPEC/matrix requiring exactly one. Bounded repair closed
F1. Fresh rereview returned `AUTHORIZATION_REVIEW_PASS`, findings/waivers
`NONE/NONE`; accepted Work Order SHA-256 is
`1de50c0f4545f975aa415cde4924db02b401a191a7703c6ec2d272d6c994518f`
and review SHA-256 is
`66202381d5cf35e49b48db723fa4bc179d94ed4b6092b62dbbf35c12abc076bc`.
No BUILD or external effect occurred.

The operator then answered `đồng ý` to the explicit external BUILD boundary.
This activates only Work Order
`1de50c0f4545f975aa415cde4924db02b401a191a7703c6ec2d272d6c994518f`:
public Git operations inherent in the sanctioned reconciler/initializer,
declared 17-root/13-downstream effects and preservation-first rollback. It does
not authorize provider/credentials, product/database, deployment, commit or
push. Responsibility transitions `ORCHESTRATOR → IMPLEMENTATION_WORKER` only
after this acknowledgment and fresh worker rehydration.

## Authority and exclusions

Independent INTAKE review may use read-only local Git evidence and may write
only its reviewer-owned receipt. It must not fetch, run the reconciler, mutate
the hidden Core or workspace root, open later phases, change product/database
source, use credentials, call a provider, install, deploy, commit or push.

The protected operator assessment named in the INTAKE must not be opened,
read, edited, hashed, staged, inventoried or used. Broad untracked inventory is
forbidden.

## Next governed move

Independent completion review returned `REVIEW_PASS_FAILURE_ROLLED_BACK`,
findings/waivers `NONE/NONE`; review SHA-256 is
`0340fce5248c1f1b5ed57191e946364c55ee62d23e53cd894e8143daed31a0b9`.
This attempt is closed bounded: the target was not adopted, restoration is
complete, and no retry/commit/push occurred.

The operator subsequently authorized a fresh target-rebase INTAKE. Continue
only through `SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30.md`;
this closed handoff grants no external effect.

## BUILD worker return

- Worker role: `IMPLEMENTATION_WORKER`
- Outcome: `FAILURE_ROLLED_BACK`
- Failure stage/network prefix: `RECONCILER_RETURN_CHECKPOINT:P1`
- Command exits: reconciler `0`; initializer `NOT_RUN`; rollback verifier `1`
- Core/pins/binding after rollback: old pin `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Root restoration: `17/17`; pin/shared/binding restoration: `2/2`, `9/9`, `1/1`
- Evidence: `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json` and
  `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md`
- P4-E checkpoint: preserved at `DESIGN_REVIEW_PASS`

## Parked predecessor

`SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md` remains the
parked P4-E handoff and must not be rewritten by the reconciliation reviewer.
