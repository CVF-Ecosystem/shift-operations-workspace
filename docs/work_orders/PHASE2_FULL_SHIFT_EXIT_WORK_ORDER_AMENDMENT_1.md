# Work Order Amendment 1 — Phase 2 full-shift exit evidence repair

- Amendment id: `P2-FULL-SHIFT-EXIT-WO-001-A1`
- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Parent Work Order: `P2-FULL-SHIFT-EXIT-WO-001`
- Repair parent: `3b0a14204069e32dbb50b695c9306910c2266282`
- Trigger: independent BUILD `REVIEW_FAIL`, four findings, no waiver
- Human authority: renewed explicitly on 2026-08-02
- Status: `REVIEW_PASS / APPROVED`
- Independent review: `docs/decisions/PHASE2_FULL_SHIFT_EXIT_AMENDMENT_1_AUTHORIZATION_REVIEW.md`

## 1. Disposition of the first provider call

The first physical provider call is immutable historical evidence and remains
recorded in `PHASE2_FULL_SHIFT_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md`, but its
admission-order claim is **INVALIDATED_BY_REVIEW_FAIL**. It is not accepted as
the tranche's final governance proof and must never be deleted, hidden or
relabeled as a passing final call.

This amendment authorizes exactly one replacement provider call after all four
findings, full reruns and a fresh exact-parent detached rehearsal pass. Final
accounting must state: **two physical calls in the tranche, one invalidated and
one accepted replacement**. Any third call is forbidden. This is an explicit
amendment to SPEC R11/AC-10's prior one-physical-call budget; it is not a waiver
of the zero-call-before-admission rule for the replacement run.

## 2. Repair ceiling

The final BUILD ceiling remains exactly the parent Work Order's same 15 paths.
No product/API/domain/ledger/schema/migration/dependency/CI/continuity path is
opened. The repair worker may modify only these finding hosts within that set:

1. `apps/workspace-web/e2e/phase2-full-shift-exit.spec.ts`
2. `scripts/testing/run_phase2_full_shift_exit_web_evidence.py`
3. `tests/integration/test_phase2_full_shift_exit_web_evidence_runner.py`
4. `tests/integration/test_phase2_full_shift_exit_postgres_live.py`
5. `scripts/run_phase2_full_shift_live_governance_evidence.py`
6. `scripts/_phase2_full_shift_live_evidence_support.py`
7. `tests/integration/test_phase2_full_shift_live_evidence_runner.py`
8. `tests/unit/test_phase2_full_shift_live_evidence_support.py`
9. `docs/decisions/PHASE2_FULL_SHIFT_BUILD_EVIDENCE_RECEIPT.md`
10. `docs/decisions/PHASE2_FULL_SHIFT_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md`
11. `docs/cvf/CVF_CONTROL_MAPPING.md`
12. `docs/catalog/MODULE_REGISTRY.json`
13. `docs/catalog/MODULE_CATALOG.md`

The helper TS and PostgreSQL runner remain part of the exact final 15-path
candidate but require no finding repair unless a testable dependency is found.
Any new implementation path or product repair requires another amendment.

## 3. Required repairs

### A1-F1 — refusal immutability and prerequisite isolation

Each refusal case must run in a newly constructed isolated ledger scenario.
Before the refused request, capture a deterministic canonical fingerprint of
the entire mutable ledger surface used by the scenario: shifts, assignments,
events, tasks, handovers (including every ordered item and evidence field),
reports, approval receipts and the complete audit ledger. The fingerprint must
include exact collection counts and canonical serialized content, with stable
record ordering and excluded nondeterministic representation details only when
the exclusion is explicitly allowlisted. After the expected refusal, require
the same counts and byte-equivalent canonical fingerprint.

This whole-ledger comparison is mandatory for `anonymous_shift_create`, where
no target record exists before the request, and proves that neither a shift,
its automatic creator assignment nor an audit was added. For every targeted
refusal it also covers the target plus every related record that could mutate;
a target-only snapshot is insufficient. The Report-gate freeze case must first
satisfy close plus a current ACKNOWLEDGED handover, then remain refused solely
because the current Report is not APPROVED. Similar cases must satisfy every
prerequisite except the one named by the case. Provider counter stays zero
throughout.

### A1-F2 — producer-bound browser evidence

The Playwright spec must write a sanitized owned temporary assertion artifact
only after its real assertions pass. The wrapper supplies a fresh run id and
owned assertion path, reads the artifact after the shared harness returns PASS,
requires matching run id and an exact allowlisted schema, binds it to the
selected spec's SHA-256 and a canonical digest of the actual harness result,
then emits the final browser JSON. It may not hardcode observed counters or set
`sanitized=true` without validating every output field against the allowlist.

The governance validator must recompute both digests from current source and
the embedded allowlisted harness payload, require the recognized producer id,
and reject hand-authored legacy payloads without provenance. Contract tests
must prove missing/mismatched run id, source digest, harness digest, unknown
fields and forged counter values fail closed.

### A1-F3 — exact PostgreSQL durability bindings

Before reconnect retain the full canonical immutable handover item snapshot.
After reconnect compare every item field including digest/evidence and order;
verify the approval receipt's complete six-field binding plus exact approver,
and assert the following exact audit multiset by target record, action and
actor. A required duplicate action is distinguished by its target record id;
the count for each tuple must be exactly one. No additional required-action
tuple with an anonymous, empty or wrong actor may exist.

| Target | Action | Actor | Expected tuple count |
|---|---|---|---:|
| source shift | `shift.create` | `p2-op` | 1 |
| destination shift | `shift.create` | `p2-op` | 1 |
| each of the four explicit assignment records (sup1 and sup2 on both shifts) | `shift.assignment.manage` | `p2-sup1` | 1 each |
| confirmed event | `event.confirm` | `p2-sup1` | 1 |
| task | `task.create` | `p2-op` | 1 |
| task | `task.transition` | `p2-op` | 1 |
| handover | `handover.create` | `p2-op` | 1 |
| handover | `handover.review` | `p2-sup1` | 1 |
| handover | `handover.acknowledge` | `p2-sup2` | 1 |
| source shift | `shift.close` | `p2-op` | 1 |
| report | `report.generate` | `p2-op` | 1 |
| report | `report.submit_review` | `p2-op` | 1 |
| report | `approval.create` | `p2-sup2` | 1 |
| report | `report.approve` | `p2-sup1` | 1 |
| report | `report.freeze` | `p2-sup1` | 1 |
| source shift | `shift.freeze` | `p2-sup1` | 1 |

The two automatic creator assignments are proven as durable assignment state
but do not invent a `shift.assignment.manage` audit: source truth binds their
atomic creation to the corresponding `shift.create` audit. Event creation is
also durable state but has no `event.create` audit claim. The in-memory
integrated scenario used by provider admission must perform the same exact
tuple/count checks before claiming actor-bound audit coverage.

### A1-F4 — fresh GET before committed task rendering

Instrument real task-list GET responses. Record the count before reconnect.
After the single replay POST, require a later HTTP-success task-list GET whose
response contains the exact created task id at the exact committed version and
status `IN_PROGRESS`; only after that response completes may the DOM assertion
for that same task id and status pass. The test must fail if the render came
from optimistic mutation output, retained local state, a different task, a
stale version or a GET observed before the replay. The assertion artifact
records only bounded counts/order booleans and the equality booleans for
id/version/status, never tokens, payloads, raw ids or URLs.

## 4. Authorization and pre-repair continuity checkpoint

This amendment and its independent authorization-review receipt are governance
artifacts outside the final BUILD 15-path ceiling. They must be selectively
committed and pushed as a standalone authorization commit while preserving the
unstaged BUILD candidate. After authorization passes, the following canonical
continuity surfaces are temporarily opened outside that ceiling for one
separate pre-repair checkpoint commit and push:

1. `SESSION/SESSION_MEMORY.md`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. `IMPLEMENTATION_STATUS.json`
5. the active handoff named by canonical active state

Those surfaces must agree that the original provider call occurred but is
invalidated, the tranche budget is two physical calls with exactly one
replacement remaining, the active role has transitioned to `REPAIR_WORKER`,
the dirty BUILD candidate is still `REVIEW_FAIL`, and provider use is
prohibited until an independent repaired-candidate pre-call `REVIEW_PASS`.
Both governance commits must reach `origin/main`, and the five continuity
paths must be clean, before implementation repair begins. They never become
part of the final exact 15-path BUILD commit.

## 5. Replacement evidence order

No provider call is allowed during repair or review. After repair:

1. dedicated static/contract tests;
2. real browser wrapper producing a fresh producer-bound JSON;
3. full frontend and Python baselines;
4. disposable PostgreSQL live suite and exact cleanup;
5. governance dry-run with all refusal/durable gates and counter zero;
6. repository/catalog/session/file-size/diff/secret gates;
7. fresh detached exact-parent rehearsal of the repaired exact 15 paths and
   verified worktree/temporary-core cleanup;
8. independent pre-replacement-call repair review `REVIEW_PASS`;
9. exactly one replacement provider call;
10. only receipt accounting, sanitized validation, exact diff and owned-temp
    cleanup afterward;
11. independent final BUILD review.

The replacement receipt must preserve the invalidated call metadata and append
a separate accepted-call section; it must not overwrite history into an
apparent one-call tranche.

## 6. Stop conditions and roles

Stop on any outside path, product repair, non-isolated refusal, provenance
self-attestation, partial snapshot/actor binding, fresh-GET ambiguity, failed
gate, cleanup residue, unsanitized field or third provider call.

`REPAIR_WORKER` may implement but not authorize or self-review. An independent
`AUTHORIZATION_REVIEWER` must approve this amendment before repair. A separate
independent reviewer must pass the repaired candidate before the replacement
call and again after the finalized two-call receipt. Apart from the standalone
authorization and pre-repair continuity commits expressly required by section
4, no BUILD commit/push or C4 is authorized until final `REVIEW_PASS`; Phase 2
remains open.
