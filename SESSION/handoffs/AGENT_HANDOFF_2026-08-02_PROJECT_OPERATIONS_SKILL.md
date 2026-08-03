# Agent Handoff — Project Operations Skill

## Disposition

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Risk: `R2`
- Control-chain phase: `FREEZE`
- Active role: `CLOSER / SESSION_SYNC_STEWARD / COMMIT_STEWARD`
- Status: `CLOSED_BOUNDED`
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

## Amendment 1 live failure and Amendment 2 draft

F1-F5 and all residual pre-call findings closed without waiver; focused 60,
full 1438/128, repository gates and independent `PRE_CALL_REVIEW_PASS` all
passed. Evidence migrated with zero call and preserved the original v1 pins.
The one authorized runner invocation stopped after FT-1 returned an invalid
action label: FT-1 is `FAILED/physical 1`; FT-2..FT-4 are `UNUSED/0` and may
not run. Current history is `5 physical / 4 invalidated / 0 final accepted`.
Post-call gates passed and independent review returned
`REVIEW_CHANGES_REQUIRED — AMENDMENT_REQUIRED`.

The failed checkpoint is pinned at receipt `49817` bytes / SHA-256
`9334ab2e6b51bcbd7017c75628e1b0e723d2089463ea352c9dbe51b5874f2c6a`
and state `110062` bytes / SHA-256
`71e4f42fbf921561f52066d707b98464599c02a11da2d0706eb33a561f7e6c8c`.
ADR/SPEC/WORK_ORDER Amendment 2 drafts preserve it, expose the global action
enum without private per-FT answers, create a fresh final four-lineage set and
raise the exact historical ceiling to nine. Independent authorization review
is the only next move. No BUILD edit, migration, provider call, stage, commit,
push or FREEZE is authorized from the drafts.

Independent Amendment 2 authorization re-review returned PASS with no waiver
after closing dependency/authority drift, lineage-formula ambiguity and commit
set ambiguity. The exact seven governance paths must now be committed/pushed;
all eight BUILD paths remain unstaged. A separate exact four-continuity-path
resume commit is required before G6-R2 and any BUILD repair.

Governance authorization `7656ca8` is pushed and `HEAD == origin/main`. This
separate four-path checkpoint acknowledges repair transfer. Run G6-R2 before
editing the same eight BUILD paths. Only G6-R2 PASS permits public-enum/v3
repair; evidence migration, provider calls and human R2 acknowledgment remain
later gates.

## Amendment 2 live failure and Amendment 3 draft

The public-action repair, v3 migration and all pre-call gates independently
passed. The authorized runner was invoked once. Replacement-2 FT-1 passed
strict schema/type/public-enum validation but failed private semantic
evaluation; it is durably `FAILED/1`, FT-2..FT-4 remain `UNUSED/0`, rerun is
zero-call, and post-call focused `64`, full `1442/128` plus repository gates
passed. Independent review requires Amendment 3; no retry or diagnostic call.

The complete failed v3 checkpoint is pinned: receipt `60182` bytes / SHA-256
`d6b92e9ff84215e472e111b78feef87ddd22ee1ff3f1dc18bba4c72bb649775f`;
state `268577` bytes / SHA-256
`95b7ceb737bd549027eac8ad7e74dfb7f2fb66eef87544f4ebb284630f92155b`.
History is physical 6 / invalidated-so-far 5 / accepted 0; Amendment 3 will
invalidate replacement 2, making the migrated start 6/6/0.

ADR/SPEC/Work Order Amendment 3 define one public structured semantic language
for all FTs, deterministic private equivalence rules, bounded safe parsed
candidate retention on semantic failure, recursive v3/v2/v1 preservation,
fresh `replacement3` lineages and exact final ceiling 10/6/4. Independent
authorization review is the only next move. No BUILD edit, migration, provider
call, stage, commit or push is authorized from these drafts.

Independent authorization review returned `AUTHORIZATION_REVIEW_PASS` with no
finding or waiver. It verified exact v3/v2/v1 pins, 6/6/0 migration and final
10/6/4 accounting, public/private noninterference, bounded candidate retention,
fresh lineages, exact 8 BUILD / 3 runtime / 7 governance / 4 resume paths and
the complete G6-R3/pre-call/new-human-R2 chain. Commit/push exactly the seven
governance paths next, leaving BUILD unstaged; only a separate pushed four-path
resume may transfer to REPAIR_WORKER.

Governance authorization `777dbf1e350abdc9da1e5f1f78dbf7f34464a0ae` is
pushed and HEAD equals origin/main. This separate exact four-path checkpoint
acknowledges repair transfer. Run G6-R3 before editing the same eight BUILD
paths. Only G6-R3 PASS permits structured-semantic/v4 source repair; repository
migration, provider calls and new human R2 acknowledgment remain later gates.

## Amendment 3 live failure and Amendment 4 draft

After all Amendment 3 gates and fresh human R2 approval, the runner was invoked
once. FT-1 is ACCEPTED/1; FT-2 is FAILED/1 solely because its public-safe
candidate used observed `WORK_ORDER` while the private evaluator required
fallback `INTAKE`; FT-3..FT-4 remain UNUSED/0. No rerun occurred or is allowed.
Post-call focused 74, full 1452/128 and repository/doctor gates passed with
residue/staged zero.

Pinned v4 evidence is receipt `80883` /
`5ab461564c942785806354019ee5f7f795872672ff9d63261d221a5cad9d5cc3` and
state `394267` /
`3a8d6f66477939631b9a6bc0f32e0da2eacdd0c0e295e427f2e00e25cc3c85db`.
Amendment 4 defines one global observed-phase/governed-next semantic, preserves
v4 recursively in v5, invalidates replacement3, creates fresh replacement4
and sets exact final ceiling 12/8/4. Independent authorization review is the
only next move; no BUILD, migration, provider or Git write is authorized.

Independent authorization re-review passed without finding or waiver after
closing F1–F3 continuity drift. Exact v4 pins, phase semantics, preservation,
8/8/0→12/8/4 accounting and 8/3/7/4 boundaries are approved. Push exactly the
seven governance paths next; only a separate pushed four-path resume transfers
to REPAIR_WORKER/G6-R4.

Governance authorization `6e25887eb9bfc0b7de5a61de978979c43166e42c` is
pushed and HEAD equals origin/main. This separate exact four-path checkpoint
acknowledges repair transfer. Run G6-R4 before editing the same eight BUILD
paths; migration/provider/human R2 remain later gates.

## Amendment 4 BUILD and C4 closure candidate

G6-R4, phase-semantics/v5 repair, zero-call migration and all pre-call gates
passed. A fresh human R2 acknowledgment authorized exactly one runner
invocation with at most four real-provider calls, fail-fast and no retry. The
invocation returned replacement 4 `4 physical / 4 accepted`; total history is
exactly `12 physical / 8 invalidated / 4 accepted`. No thirteenth call exists.

Post-call focused `76`, full `1454/128`, skill/repository/doctor gates and
exact-parent `1378/128` rehearsal passed. Independent final review returned
PASS without finding/waiver. Exact eight-path BUILD `ad7e037` is pushed.

Separate C4 authorization `d953b18` is pushed after four authorization
findings closed without waiver. The exact eight closure paths received
independent FREEZE re-review PASS after `C4-FREEZE-REV-F1` corrected
candidate-state residue to final post-push truth; no waiver. Protected
BUILD/evidence bytes, continuity/catalog truth, zero provider/runtime/staged
residue and the bounded claim all passed.

The bounded claim is only that four separately initialized real-provider
sessions followed the reviewed repository-owned navigation skill for four
synthetic fixtures. It is not prompt enforcement, universal compliance,
production governance, installation or Phase 3 progress. Fresh
`PROJECT-KNOWLEDGE-PACK` INTAKE is the sole next authority; later queue items
remain parked.
