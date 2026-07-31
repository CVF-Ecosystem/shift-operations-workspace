# Authorization Review — P2-C C3a2 Work Order

- Review target: `docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER.md`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Risk: `R2`
- Reviewer role: independent `AUTHORIZATION_REVIEWER`
- Final disposition: `REVIEW_PASS / APPROVED`
- BUILD status: `BLOCKED UNTIL PUSHED PRE-BUILD CHECKPOINT AND G6 PASS`

## Evidence reviewed

The reviewer compared the Work Order with the current source, pushed C3a1
commit `ec90c78c98c6d314e81d7b50506b514c81f7f580`, the canonical P2-C DESIGN
and SPEC, the C3a fan-out DESIGN/SPEC amendments, R6-R10/R30, AC-04..AC-10
and AC-29..AC-34.

Mechanical inspection confirmed exactly 79 numbered BUILD paths, 79 unique,
with every absent path explicitly marked `NEW`; there is no wildcard,
conditional allowance, reserve or self-review path.

## Findings and repairs

### `C3A2-WO-REV-F1 LEGACY_LIVE_RUNNER_PATH_OMISSION`

Initial review found four real governance runners that build direct-ledger
legacy shifts and would regress once ACTIVE assignment becomes load-bearing:

- `scripts/run_handover_live_governance_evidence.py`;
- `scripts/run_report_live_governance_evidence.py`;
- `scripts/run_incident_live_governance_evidence.py`;
- `scripts/run_p2c_read_live_governance_evidence.py`.

Repair added exactly these four paths, raised the ceiling from 75 to 79 and
requires persisted active users plus explicit ACTIVE assignments while
preserving established refusal/admission/provider call-count assertions.
Bypass, default assignment and monkeypatch repair are prohibited. The
298/297/299-line handover/report/read runners must be repaired line-neutrally.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3A2-WO-REV-F2 AC29_REHEARSAL_NOT_OPERATIONALIZED`

Initial review found that the draft named exact-parent evidence generally but
did not operationalize AC-29 in the execution order or worker return.

Repair requires an isolated temporary worktree/tree at the exact recorded
pre-BUILD parent, its recorded full baseline and repository gates, no stash/
reset/mutation of the primary candidate tree, and removal/prune/path-absence
proof recorded in the BUILD receipt. The rehearsal is ordered before fresh
provider proof and repeated in the worker-return contract.

Disposition: `CLOSED_WITHOUT_WAIVER`.

## Final disposition and boundary

Independent re-review returned `REVIEW_PASS`. The 23-path production matrix
covers the non-staffing operational routers/services, centralizes canonical
stored-shift assignment enforcement and protects C3a1 storage/staffing/
bootstrap behavior. R6-R9, evidence and enumeration-safe claim boundaries are
appropriately bounded.

Under the operator's standing Work Order delegation, the repaired Work Order
is approved intact. This approval does not itself authorize BUILD. The
authorization commit must be pushed, then a separate four-surface pre-BUILD
continuity checkpoint must record its own exact parent and pass G6 before any
source edit or provider call. C3b-C3d remain blocked. No Claude CLI/MCP call,
BUILD, provider call, stage, commit, push or FREEZE occurred during review.
