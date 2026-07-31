# Work Order Amendment 1 — P2-C C3a2 Ceiling Repair

- Parent: `docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER.md`
- Finding: `C3A2-BUILD-BLOCK-F1 TWO_REQUIRED_HOSTS_OMITTED`
- Risk: `R2`
- Status: `APPROVED — RESUME ONLY AFTER PUSHED CHECKPOINT AND G6 RECONFIRMATION`

## Exact amendment

Add exactly these BUILD paths:

80. `tests/contract/test_contract_files.py`
81. `scripts/run_message_admission_live_governance_evidence.py`

The final ceiling is exactly 81 unique paths: the original 79 plus these two.
No wildcard, reserve or other authority is added.
For amended execution and worker reporting, every original Work Order §2/§6
reference to a 79-path ceiling is superseded by this exact 81-path ceiling.

## Repair contract

- the contract test explicitly persists the viewer and ACTIVE assignment for
  its real open-work route proof, without weakening schema validation;
- the message runner persists and ACTIVE-assigns `msg-ev-op` in both separate
  fresh-ledger branches: frozen refusal preserves 409, zero message/audit
  writes and zero provider calls; genuine admission preserves exactly one message, exact
  actor-bound audit and the later exactly-one real provider call;
- both files remain within the hard line limit without debt/exemption;
- all original C3a2 verification, AC-29, receipt, worker/commit separation,
  protected boundary and claim limitations remain mandatory.

The partial BUILD stays unstaged. After independent approval and push, a
separate four-surface resume checkpoint is required before either new path is
edited. The worker still returns
`READY_FOR_INDEPENDENT_P2C_C3A2_BUILD_REVIEW` and does not stage, commit,
push, self-review or FREEZE.
