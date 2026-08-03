# Agent Handoff — Project Operations Skill

## Disposition

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Risk: `R2`
- Control-chain phase: `SPEC`
- Active role: `ORCHESTRATOR / SESSION_SYNC_STEWARD`
- Status: `SPEC_RE_REVIEW_PASS_READY_FOR_WORK_ORDER`
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

SPEC repair 1 received independent `SPEC_RE_REVIEW_PASS`; the HIGH cardinality
finding is closed without waiver. Draft an exact-path WORK_ORDER only.
Knowledge-pack and later queue items stay inactive.
