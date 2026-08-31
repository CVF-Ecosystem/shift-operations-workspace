# DESIGN Amendment — Reviewer-Time Target Movement

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Phase: `DESIGN`
- Risk: `R2`
- Parent DESIGN SHA-256:
  `2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443`
- Trigger: `CORE-REFRESH-SPEC-REV-F4`
- Status: `OPEN_FOR_INDEPENDENT_DESIGN_AMENDMENT_REVIEW`
- Active role: `DESIGN_AUTHOR`

## 1. Amendment boundary

This amendment changes only the evidence-carrier lifecycle after a successful
worker return when the independent completion review observes public-target
movement. Sections 1-7 and 9-11 of the accepted DESIGN otherwise remain in
force. Section 8 is narrowed by this amendment only for the
`REVIEW_TARGET_MOVEMENT` branch.

The old Core remains
`a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`; the frozen BUILD target remains
`06c3d040a3dc8fa22fa27f2f9c3e40739def075e`. This amendment authorizes no
network call, reconciliation, rollback execution, hidden-Core/workspace-root
mutation, product change, provider call, commit or push.

## 2. Immutable evidence already present

When a successful worker return reaches independent completion review, these
three artifacts may already exist:

1. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json` — immutable
   canonical worker receipt with outcome `SUCCESS`;
2. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md` — immutable
   worker summary of that receipt; and
3. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md` —
   immutable reviewer receipt with disposition `REVIEW_TARGET_MOVEMENT` and
   final raw SHA-256 values for both worker artifacts.

Neither the rollback-only repair worker nor any later reviewer may update,
replace or reinterpret those artifacts. In particular, the original worker
outcome remains the truthful result at worker return; later target movement
does not retroactively convert it into a worker failure.

## 3. Conditional repair record

The BUILD preflight must additionally prove this exact tracked path `ABSENT`:

`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-29.json`

It must remain absent on normal `REVIEW_PASS` and on every failure detected by
the initial worker. It may be created exactly once only after the completion
review records `REVIEW_TARGET_MOVEMENT` and routes the preauthorized distinct
`REPAIR_WORKER`.

That repair worker owns exactly one action graph: preservation-first rollback
from the frozen BUILD preimages, with no reconciliation retry or target
adoption. Its JSON record is the sole semantic owner for the rollback attempt
and must record:

- the immutable success-receipt and completion-review paths plus their raw
  SHA-256 values observed before repair;
- the original old pin, frozen target and newly observed public target;
- the exact rollback trigger, containment checks and actually executed
  rollback-verifier count;
- Core, 17 root targets, two pin carriers, nine shared continuity carriers and
  ignored-binding restore observations without fabricating unreadable facts;
- the one conditional repair-path `CREATE` effect and the exact tracked/local
  effect ceiling; and
- terminal outcome `REVIEW_TARGET_MOVEMENT_ROLLED_BACK` or
  `REVIEW_TARGET_MOVEMENT_ROLLBACK_INCOMPLETE`.

The JSON must not contain its own final raw hash. The repair worker may not
create a Markdown summary or any other evidence path.

## 4. Conditional path ceiling and restoration

The original initial-worker ceiling remains exactly 13 tracked paths plus the
ignored binding. On this later branch only, the distinct repair worker may:

- restore or update the same two pin and nine shared-continuity carriers
  already listed in accepted DESIGN section 7;
- regenerate or restore only `.cvf/local-binding.json` as the declared ignored
  local effect;
- perform the already declared hidden-Core and 17-root rollback effects; and
- create exactly the one conditional rollback JSON named in section 3.

It must not modify either original worker artifact or the completion-review
artifact. No absent-before-BUILD downstream path other than the conditional
rollback JSON may survive this repair. A complete rollback restores the Core,
root targets, pins and binding to the frozen BUILD preimages before shared
continuity carriers record the later failure. An incomplete rollback records
only observed states and forbids a clean-restore claim.

The carrier intersection is intentional and temporally closed; it is not
concurrent ownership:

| Path/effect class | Initial worker window | Post-movement repair window | Reviewer window |
|---|---|---|---|
| two pin carriers | target bridge/update | restore-only to BUILD preimage | read-only |
| nine shared continuity carriers | record worker return | restore, then record rollback truth only | read-only |
| ignored local binding | initializer regeneration | restore/regenerate old-pin preimage only | read-only |
| two original worker evidence paths | `CREATE` | immutable/read-only | read/hash-only |
| target-movement completion review | absent, reviewer-owned later | immutable/read-only | initial reviewer `CREATE` only |
| conditional rollback JSON | forbidden/absent | repair worker `CREATE` only | rereviewer read/hash-only |
| conditional terminal rereview | forbidden/absent | forbidden/absent | rereviewer `CREATE` only |

Repair ownership over the two pins, nine shared carriers and binding begins
only after the immutable completion review records `REVIEW_TARGET_MOVEMENT`
and routes the distinct repair worker. It ends when that worker writes its one
terminal rollback JSON. No initial-worker or reviewer ownership is live during
that repair window. This temporal intersection does not permit new purpose,
new content class or mutation outside restoration and truthful failure
continuity.

## 5. Independent terminal rereview

The BUILD preflight must also prove this exact tracked path `ABSENT`:

`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-29.md`

Only a fresh `INDEPENDENT_COMPLETION_REREVIEWER`, distinct from the initial
worker and rollback repair worker, may create it after the rollback record
exists. The rereviewer recomputes and records final raw SHA-256 values for:

1. the immutable root-effects receipt;
2. the immutable worker return;
3. the immutable target-movement completion review; and
4. the conditional rollback JSON.

The rereview artifact does not self-hash. It verifies the conditional repair
ceiling, rollback outcome, honest incomplete-state representation, parked P4-E
checkpoint and narrow claim boundary. It may invoke at most the separately
authorized rereviewer doctor already allowed by the accepted DESIGN; its
network observation is review evidence and never a new BUILD target.

## 6. Terminal dispositions and next authority

The initial worker family continues to own exactly `SUCCESS`,
`FAILURE_ROLLED_BACK` and `FAILURE_ROLLBACK_INCOMPLETE`. The conditional
rollback record adds exactly:

- `REVIEW_TARGET_MOVEMENT_ROLLED_BACK`; and
- `REVIEW_TARGET_MOVEMENT_ROLLBACK_INCOMPLETE`.

After either conditional outcome, reconciliation retry and adoption of a newer
public target remain forbidden. Even a complete rollback closes only the
preservation action; it does not make the original refresh current. Fresh
operator authority and governed phase amendments are required for another
attempt.

The existing invariant family remains applicable and must be amended during
SPEC repair so its sole semantic matrix covers the two conditional outcomes,
exact path/effect relations and mutually exclusive evidence lifecycles.

## 7. Acceptance and next move

Independent DESIGN amendment review must verify:

1. exact owner, pre-state and `CREATE` semantics for both new paths;
2. immutability of all three earlier evidence artifacts;
3. executable rollback and honest incomplete-state recording;
4. the exact temporal intersection for pins/shared carriers/binding and the
   disjoint owner-only evidence-path lifecycles;
5. absence of self-hash/cross-hash cycles; and
6. no widening of target, product, provider or external-effect authority.

Next move is independent DESIGN amendment review only. SPEC repair, Work
Order, reconciliation/network/root effects, P4-E SPEC, commit and push remain
unauthorized until this amendment receives `DESIGN_AMENDMENT_REVIEW_PASS`.
