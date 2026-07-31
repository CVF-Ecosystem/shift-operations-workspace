# Work Order Amendment 1 — P2-C C3a1 Legacy Runner Ceiling Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Risk: `R2`
- Status: `REVIEW_PASS / APPROVED UNDER OPERATOR-DELEGATED AUTHORITY`

## Exact ceiling change

The original 48 paths remain authorized. Add exactly:

49. `scripts/run_shift_create_live_governance_evidence.py`
50. `scripts/run_message_admission_live_governance_evidence.py`

The amended ceiling is exactly 50 unique paths with zero wildcard, reserve,
self-review, dependency, continuity or roadmap path.

## Required repair

- both runners persist the exact active user used by their existing
  ShiftService.create call before that call;
- the test-only InMemoryLedger constructor monkeypatch in
  `tests/integration/test_shift_create_live_evidence_runner.py` is removed;
- real runner tests prove the compatibility path;
- `tests/cvf/test_message_admission.py`,
  `tests/cvf/test_shift_create_admission.py` and
  `tests/integration/test_shift_create_live_evidence_runner.py` return to
  <=300 lines through line-neutral fixture/comment compaction;
- assignment path/schema constants, strip helper and assignment-delta golden
  proof move to `tests/unit/test_assignment_openapi_contract.py`;
- historical OpenAPI tests import that helper without a circular import;
- `tests/unit/test_p2b_openapi_contract.py` returns to <=300 lines;
- no new helper/split/debt/exemption path is created.

All original implementation/evidence commands, stop conditions, ownership,
nonclaims and no-stage/commit/push/self-review worker rules remain unchanged.
Any further out-of-ceiling requirement returns `BLOCKED_WORK_ORDER_CEILING`.
