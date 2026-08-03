# Agent Handoff — Project Operations Skill

## Disposition

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Risk: `R2`
- Control-chain phase: `BUILD` repair (G6-R first)
- Active role: `REPAIR_WORKER`
- Status: `AMENDMENT_1_REPAIR_RESUMED_G6_R_REQUIRED`
- Parent: Phase 2 C4 `0a29192dacf7380ee565a13bc48a164eb79e65a9`

## Settled predecessor

Phase 2 is `FREEZE / CLOSED_BOUNDED`; BUILD `d02186a` and C4 `0a29192` are
pushed, HEAD equals origin/main and the worktree was clean before this INTAKE.
That authority does not carry forward.

## Active boundary

Author a provider-neutral reusable operations skill over existing project
truth. The skill may guide continuity rehydration, phase/role routing,
exact-path Work Orders, evidence/review/cleanup and bounded closure. It must not
become a second truth source or claim that prompts alone enforce governance.

No skill files, installation, provider call, external write, DESIGN/SPEC/Work
Order or BUILD are authorized by this INTAKE. The skill-creator guidance was
read to frame examples, progressive disclosure, path decisions and validation.

## SPEC candidate

`docs/specs/PROJECT_OPERATIONS_SKILL_SPEC.md` converts D1-D7 into the exact
two-file skill shape, frontmatter/metadata contracts, R1-R8 procedures and
refusals, four synthetic forward-test scenarios, four separately initialized
durable real-provider lineages, AC-01..AC-14, candidate path families and stop
conditions. It authorizes no source, installation, BUILD, provider call,
commit or FREEZE.

## SPEC review history

The initial PASS was withdrawn after a clarification audit found a HIGH
cardinality conflict: four fresh-agent behavioral scenarios could not coexist
with one total provider call. Repair 1 requires four separate FT lineages,
exactly one non-mocked call per lineage, no batch/shared context/retry, durable
reservation and aggregate `4 physical / 4 accepted` closure accounting. No
waiver was taken.

## Next governed move

`docs/work_orders/PROJECT_OPERATIONS_SKILL_WORK_ORDER.md` proposes an exact
eight-path BUILD, separate authorization/pre-BUILD checkpoints, initializer
use, static and live harness contracts, four durable FT lineages, G6,
independent review and commit/C4 ownership. It is now independently approved;
BUILD/provider/install remain unauthorized pending checkpoint and G6.

## Authorization review history

Initial review returned five accepted findings, no waiver: Windows lock/temp
authority; evidence-bundle invalidation; exact provider config precedence;
canonical request/response and fail-on-redaction semantics; and missing
SPEC/WORK_ORDER in machine required reads. Repair 1 adds exact runtime-only
lock/temp paths while retaining eight final BUILD paths, a uniform six-path
bundle digest, exact read-only Alibaba sources, canonical JSON evidence and the
corrected dependency read order. Final verdict is
`AUTHORIZATION_RE_REVIEW_PASS`; all five findings are closed without waiver.

## Next governed move after authorization push

Authorization commit `e1da12b641ca516bc915fbdc4dc7c05fa2ba194f`
is pushed and this separate checkpoint acknowledges the role transfer. Run G6
from the clean pushed checkpoint. Only G6 PASS unlocks the exact eight BUILD
paths and later four-call live step; installation/staging/commit/self-review/
FREEZE remain unauthorized. Later queue items remain inactive.

## BUILD review disposition

G6 passed; BUILD produced the exact eight unstaged paths, focused `19`, full
`1397/128`, repository/doctor gates, rollback rehearsal and one live run at
bundle `a5ac9cc...` with four physical/four mechanically accepted responses.
Independent review returned `REVIEW_CHANGES_REQUIRED` with F1-F5: answer
leakage, pre-finish crash accounting, incomplete state integrity, bool/int
coercion and incomplete zero-call preflight tests. All are accepted without
waiver. The four-call bundle is retained `INVALIDATED_BY_REVIEW_FAIL` and
governance-accepted behavior count is zero; no retry authority remains.

## Amendment 1

The review-repair ADR addendum, SPEC Amendment 1 and Work Order Amendment 1
separate public fixtures/private expectations, add durable DISPATCHED
accounting, exact state/receipt validation, strict types, complete preflight
tests, immutable original evidence and at most four replacement calls. Exact
eight final paths remain. Independent amendment authorization review only is
next; no repair/provider call before pushed approval, resume checkpoint, G6-R.

Initial amendment review returned three further findings, repaired without
waiver: F1 proof now uses structural noninterference/private canaries rather
than impossible generic-literal exclusion; original receipt/state are pinned
at `39659`/`42044` bytes and exact SHA-256 values with prefix/base64-snapshot
preservation; required reads now follow design dependency order. Independent
amendment re-review is next.

Final amendment verdict is `AMENDMENT_1_AUTHORIZATION_RE_REVIEW_PASS`; all
three authorization findings and F1-F5 repair scope are approved without
waiver. Authorization `64d5f7f` plus mandatory size-gate correction `27926c3`
are pushed. This separate checkpoint resumes REPAIR_WORKER. Run G6-R before
repair; replacement calls remain blocked until all amended pre-call gates pass.
