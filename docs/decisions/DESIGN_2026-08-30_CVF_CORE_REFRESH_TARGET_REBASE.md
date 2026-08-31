# DESIGN — CVF Public-Core Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_DESIGN_REVIEW`
- Active role: `DESIGN_AUTHOR`
- Accepted INTAKE SHA-256:
  `f4efd86c242132082949432f7c44e0f1304599826b0e823fdff3abd39cf77294`
- INTAKE review SHA-256:
  `fc381ad4485a57760b029c9072cdd3aee93333b0dd6c9d026cbc1e13625df865`
- Frozen proposed target:
  `d7860138350130d6d105826ce186f1beeaba3c2d`

## 1. Decision summary

Retain the accepted bootstrap-native reconciliation architecture from the
reviewed 2026-08-29 attempt, but create a new attempt-2 evidence lifecycle and
freeze `d786013...` as the only eligible target. A later BUILD, if separately
specified, authorized and explicitly approved at its external-effect boundary,
uses the sanctioned reconciler, an exact two-pin bridge and the downstream
initializer. Any target movement or invariant failure stops fail-closed; no
retry or in-attempt target rebase is allowed.

This DESIGN changes governance planning only. It does not adopt the target,
run network commands, mutate the hidden Core/workspace root, or resume P4-E.

## 2. Context and preserved truths

- Active Core and downstream pins remain clean at `a7a797d...`; existing local
  `origin/main` is `d786013...`, five commits ahead.
- The 202-path cumulative Core delta includes 121 paths outside the accepted
  Markdown/docs-only classification. It is not treated as a documentation-only
  update or imported into product runtime.
- Selected reconciler, doctor, new-workspace and `05_OPERATION` surfaces are
  byte/object-identical between old and proposed target. The downstream
  initializer hash remains the accepted prior value.
- Attempt 1 is immutable `FAILURE_ROLLED_BACK`, independently reviewed and
  `FREEZE/CLOSED_BOUNDED`; its evidence paths are never reused.
- P4-E remains parked at `DESIGN_REVIEW_PASS`; XR1 remains separate debt.

## 3. Architecture and ordered control points

### D1 — Frozen-target preflight

Before any external effect, a later worker must prove exact contained paths,
expected remote, clean old Core, the locally available target object and
ancestry, downstream staged-zero, accepted contract/tool/profile hashes, and
recoverable preimages for every allowed root/downstream/binding carrier. The
preflight also proves every attempt-2 evidence path absent and non-colliding.
Any mismatch terminates with zero external effect.

### D2 — Preservation-first execution

The later worker preserves the old Core, exact workspace-root targets, two pin
carriers, shared continuity carriers and ignored local binding before invoking
the sanctioned reconciler exactly once. At the immediate checkpoint, active
Core `HEAD`, local `origin/main`, cleanliness and expected remote must all match
the frozen target. If not, the worker preserves the replacement/failure state,
restores all preimages, runs the one rollback verifier required by the future
SPEC, writes failure evidence, and stops without pin edits, initializer or
retry.

### D3 — Exact pin bridge and initializer

Only after D2 passes may the worker replace the full old pin exactly once in
`.cvf/manifest.json.cvfCoreCommit` and exactly once in the generated `AGENTS.md`
header, parse both values, and invoke the downstream initializer exactly once.
Success requires the initializer/doctor command graph and final five-way target
agreement across Core HEAD, Core origin, manifest, AGENTS and binding.

### D4 — Independent completion review

A reviewer distinct from the worker recomputes receipts, roots, path ceilings,
pins, hashes, command accounting, invariant evidence, P4-E preservation and
prohibited-effect counts. It may use at most the exact doctor authority later
granted by a Work Order. Reviewer-observed target movement never causes a retry:
the immutable success evidence is retained and responsibility passes to a
distinct rollback-only repair worker, followed by a distinct rereviewer.

### D5 — Closure

Only an accepted terminal review may route to FREEZE. Success closes the narrow
Core freshness/pin claim; a complete rollback closes the failed attempt without
target adoption. Incomplete rollback remains open failure and cannot be called
closed or successful.

## 4. Collision-free attempt-2 evidence lifecycle

All six paths below were locally absent when this DESIGN was authored and must
be proved absent again at authorized BUILD preflight:

1. Evidence directory:
   `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-2026-08-30-ATTEMPT-2-EVIDENCE`.
2. Initial worker receipt:
   `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json`.
3. Worker return:
   `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_ATTEMPT_2.md`.
4. Independent completion review:
   `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_ATTEMPT_2.md`.
5. Conditional reviewer-movement rollback receipt:
   `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_ATTEMPT_2.json`.
6. Conditional terminal rereview:
   `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_ATTEMPT_2.md`.

Worker JSON and Markdown do not self-hash or cross-hash; independent terminal
review owns their final hashes. Conditional artifacts are owned by their
separate roles and never overwrite worker or attempt-1 evidence.

## 5. Effect ceilings for later specification

The root-effect ceiling remains the exact 17 workspace-kit targets accepted in
the prior architecture; SPEC and Work Order must enumerate them rather than
infer them from directory scans. The downstream worker ceiling remains the two
pin carriers, nine current shared continuity carriers, the ignored binding and
the two attempt-2 worker artifacts. The active shared handoff is
`SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30.md`; the closed
attempt-1 handoff and all P4-E/governance/product artifacts are protected.

The future contract must distinguish `CREATE`, `UPDATE`, `DELETE` and
`NO_CHANGE`, preserve originally absent targets as absent during rollback, and
retain backups, failed replacements and failure deltas. Broad downstream
untracked inventory is forbidden.

## 6. Roles and temporal ownership

- `ORCHESTRATOR`: records gates and routes authority.
- `SPEC_AUTHOR`: freezes requirements, hashes and outcome grammar.
- `WORK_ORDER_AUTHOR`: enumerates commands, paths, evidence and stop rules.
- `IMPLEMENTATION_WORKER`: owns preflight, initial execution, rollback on
  worker-time failure, worker evidence and return only.
- `INDEPENDENT_COMPLETION_REVIEWER`: reviews; never repairs its own finding.
- `REPAIR_WORKER`: on reviewer target movement only, restores from frozen
  preimages and creates the conditional rollback JSON; never retries.
- `INDEPENDENT_COMPLETION_REREVIEWER`: owns the conditional terminal receipt.
- `CLOSER/SESSION_SYNC_STEWARD`: synchronizes accepted terminal truth.
- `COMMIT_STEWARD`: inactive unless separately authorized after closure.

Shared continuity ownership is a deliberate temporal intersection: worker or
repair worker may write within its accepted window; closer synchronizes only
after terminal review. Review artifacts remain role-exclusive.

## 7. Invariant-family decision

Applicability is `TRIGGERED`: the later attempt has shared receipts across
multiple terminal outcomes, outcome-controlled required/forbidden fields,
exact command/counter relations and multiple validator surfaces. Before SPEC
review, the SPEC author must register a successor target-rebase family and
matrix under `docs/cvf/invariants/`, bind a canonical digest through a machine
pin, and use `docs/templates/INVARIANT_FAMILY_PROOF.md`. Per-outcome rules must
exist only in that matrix, not be copied into DESIGN, SPEC or Work Order.

The successor may derive structure from the accepted 2026-08-29 family, but it
must use the new target, attempt-2 lifecycle and current ownership paths; it
must not reinterpret the immutable attempt-1 matrix or evidence.

## 8. Failure and rollback model

The future SPEC must close at least these terminal families: zero-effect
preflight refusal; successful worker return; worker-time failure with complete
rollback; worker-time rollback incomplete; reviewer target movement;
reviewer-movement complete rollback; and reviewer-movement rollback incomplete.
It must encode ordered command counts, the rollback stage/verifier state and
required/forbidden evidence fields so adjacent outcomes cannot validate.

Target movement, path/tool/profile drift, evidence collision, containment or
preimage failure, unexpected effect, credential need, protected-assessment
contact, prohibited product/provider/deployment effect, or inability to restore
is fail-closed. No failure route permits retry inside the attempt.

## 9. Security, live evidence and claim boundary

The protected operator assessment remains excluded from open/read/hash/stage/
inventory/use. Credentials and provider calls are outside this maintenance
claim. This DESIGN does not claim CVF controls AI/agent behavior, so no mock or
provider output is offered as governance proof. If a later tranche adds such a
claim, the live-provider evidence rule applies independently.

A successful later closure proves only deterministic public-Core
freshness/pin reconciliation inside the enumerated workspace boundary. It does
not prove adoption of the 202 Core paths into product runtime, provider
behavior, AI governance, arbitrary-untracked absence, database behavior,
deployment or production readiness.

## 10. Alternatives considered

- **Reuse attempt-1 evidence paths:** rejected because it destroys provenance
  and violates the accepted immutable-history boundary.
- **Update pins or checkout target directly:** rejected because it bypasses
  the sanctioned bootstrap command graph and rollback accounting.
- **Treat local `origin/main` as permanent:** rejected; the later reconciler and
  reviewer must still fail closed on movement from the frozen target.
- **Resume P4-E first:** rejected while mandatory Core reconciliation remains a
  separate active maintenance lane.

## 11. DESIGN acceptance criteria

Independent review must verify the frozen-target choice, collision-free path
lifecycle, preservation-first graph, exact role separation, effect-ceiling
shape, reviewer-movement rollback route, invariant-family trigger, fail-closed
rules, P4-E/protected-assessment boundaries and narrow claim. Findings and
waivers must be explicit.

## 12. Next governed move

Independent DESIGN review only. SPEC, Work Order, BUILD, network/Core/root
mutation, retry, provider/credential use, product/database change,
installation, deployment, commit/push and P4-E SPEC remain unauthorized until
`DESIGN_REVIEW_PASS` and an explicit phase transition.
