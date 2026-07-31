# Authorization Review — P2-C C3a1 Assignment Foundation

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Reviewed phase: `WORK_ORDER`
- Risk: `R2`
- Reviewer role: `AUTHORIZATION_REVIEWER`
- Future implementation-worker independence: `YES`
- Date: `2026-07-31`
- Disposition: `REVIEW_PASS — OPERATOR-DELEGATED APPROVAL RECORDED`

## Scope reviewed

The review compared the intake, repaired DESIGN, concurrency and fan-out
addenda, SPEC R1-R30/AC-01..AC-35, current source seams, historical OpenAPI
chain, migration/live runners, hard file limits and proposed 48-path ceiling.
No implementation, Docker/PostgreSQL run, provider call or secret access
occurred.

## Mechanical ceiling review

- numbered paths: 48;
- unique paths: 48;
- wildcard/conditional/reserve paths: zero;
- every listed path is a BUILD/evidence/truth path; no self-review artifact is
  listed;
- hard-limit hosts `tables.py`, `sql_ledger.py` and `repository.py`: named and
  required to change line-neutrally through feature mixins;
- JWT-expiry dependency seam and every historical OpenAPI delta link: named;
- all governed ShiftService.create/POST-shift compatibility fixtures found by
  source inspection: named;
- catalog/source-truth and explicit PostgreSQL/live-evidence runner paths:
  named;
- route-wide operational enforcement and its broad fixture fan-out: protected
  for C3a2.

## Findings and repairs

### `P2C-C3A1-WO-REV-F1 LIVE_PROOF_ALLOCATION_TOO_NARROW`

The fan-out amendment assigns final C3a AC-10 operational-scope proof to C3a2,
but C3a1 itself makes governance-significant permission/audit claims for
staffing and atomic bootstrap. Under AGENTS.md those claims still require a
real provider-backed governance receipt.

Repair: the Work Order includes a bounded C3a1 live runner/receipt proving
zero-call staffing refusals followed by durable admitted assignment/audit
verification and exactly one provider call. It does not substitute for C3a2's
later route-wide AC-10 proof. `CLOSED_WITHOUT_WAIVER`.

### `P2C-C3A1-WO-REV-F2 REVIEW_PATH_OWNERSHIP_AMBIGUOUS`

The initial draft considered future review artifacts inside the BUILD ceiling,
which could let the worker self-author review evidence.

Repair: those paths were removed. Independent findings are returned outside
the BUILD changed set; accepted repairs update the authorized BUILD evidence
receipt truthfully and remain inside the same exact ceiling.
`CLOSED_WITHOUT_WAIVER`.

## Requirements trace

- R1-R3: paths 1-11, 20, 29, 33-35;
- R4: paths 10-13, 30-32, 36-39;
- R5: paths 4, 11-12, 17-19, 21, 28, 30, 33-35;
- R9 C3a1 portion: paths 12, 14-19, 21-27, 30;
- R10/C3a1 bounded evidence: paths 35, 40-45;
- R26-R29: exact ceiling, protected boundary, catalog/control mapping and
  worker/commit separation in sections 1-8.

No C3a1 requirement depends on an unnamed path. Source discovery to the
contrary triggers `BLOCKED_WORK_ORDER_CEILING`.

## Approval and disposition

The operator previously delegated Work Order approval authority to Codex.
That standing delegation approves this repaired exact 48-path Work Order and
manual external-worker handoff. It does not authorize Claude CLI use, worker
stage/commit/push, self-review, checkpoint combination or any out-of-ceiling
edit.

`REVIEW_PASS`. After this authorization checkpoint is committed/pushed, Codex
may create and push a separate four-surface pre-BUILD continuity checkpoint.
The worker then runs G6 from that exact clean parent. BUILD remains prohibited
until both events occur and G6 passes.
