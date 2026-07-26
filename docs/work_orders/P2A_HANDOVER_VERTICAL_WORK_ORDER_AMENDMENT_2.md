# Work Order Amendment 2 — P2-A Handover Independent Review Repair

ID: `P2A-HANDOVER-WO-AMENDMENT-2`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — REPAIR PROHIBITED UNTIL C2d AND C2e ARE PUSHED
Amends: parent Work Order and Amendment 1

## 1. Accepted findings

- `HOV-REV-F5 DEBT_RATCHET_BYPASS`
- `HOV-REV-F6 CONTINUITY_GATE_RED` — reviewer-owned, not worker repair
- `HOV-REV-F7 LEDGER_PARITY_AND_IMMUTABILITY_GAP`
- `HOV-REV-F8 BUILD_RECEIPT_DRIFT`

No finding is waived.

## 2. Exact amended C3 changed set

The existing 41 paths remain authorized. Add exactly:

42. `tests/cvf/_customer_request_fixtures.py` — NEW
43. `tests/cvf/test_customer_request_transitions.py` — NEW
44. `tests/integration/test_handover_ledger_parity.py` — NEW

Final C3 is exactly 44 paths. No 45th path is conditional.

The existing authorization for
`docs/reference/FILE_SPLIT_DEBT_BASELINE.json` is narrowed as follows:

- remove the customer-request and shift-close entries;
- retain the other two entries byte-for-byte;
- do not add, rehash or rewrite any debt entry.

## 3. Repair scope

Claude may change only the 44 C3 paths and must:

1. split the customer-request test exactly per SPEC R20;
2. repair `_handover_repository.py` and `_handover_store.py` for R21/R22;
3. add the dedicated parity tests before production repair;
4. extend the already-authorized PostgreSQL handover tests for the applicable
   controlled-integrity cases;
5. correct build/live receipts and catalog wording/counts from fresh truth;
6. rerun every parent and amended gate.

Do not modify customer-request service/router semantics. Do not weaken the
guard. Do not directly set terminal handover state in tests.

## 4. Required ledger error behavior

Both backends use `ValueError` with stable reason fragments:

- `duplicate handover_id`;
- `duplicate handover item source`;
- `handover item aggregate mismatch`;
- `source shift not found` or `destination shift not found`;
- `handover snapshot is immutable`.

Prevalidation and mutation must share the caller's transaction when `unit` is
provided. Rejection leaves no aggregate/item/evidence residue.

## 5. Evidence

In addition to all prior suites:

```text
python -m pytest tests/integration/test_handover_ledger_parity.py -q
python -m pytest tests/cvf/test_customer_request_vertical.py
                 tests/cvf/test_customer_request_transitions.py
                 tests/cvf/test_customer_request_repair.py -q
```

Then run the full non-live suite, catalog/session/file-size/validator/diff/
doctor gates, disposable PostgreSQL 16, and the real provider evidence exactly
as the parent Work Order requires.

Receipts must report fresh results. The independent review checkpoint before
Amendment 2 was:

```text
focused Amendment 1 suite: 60 passed
full non-live: 567 passed, 53 skipped, 1 warning
catalog: PASS
session-state: PASS
file-size and repository validator: FAIL on SESSION_MEMORY 607/600
```

## 6. Reviewer-owned C2e

Codex, not Claude, repairs/compacts `SESSION/SESSION_MEMORY.md` and synchronizes
the active handoff/state/mirror in C2e. Those continuity files are not part of
C3. Claude confirms the file-size gate is green after C2e before repair.

## 7. Stop conditions

All prior stops remain. STOP on:

- required 45th path;
- any debt rehash/addition;
- raw database exception escaping an R21 case;
- backend error or immutable-put divergence;
- customer-request behavior change rather than test split;
- red repository gate, receipt drift or secret-bearing output.

## 8. Commit graph and role

- C2d: exactly these three Amendment 2 artifacts.
- C2e: reviewer-owned continuity repair/acknowledgment.
- C3: exactly 44 BUILD paths after independent REVIEW_PASS.
- C4: unchanged closure family.

After C2d/C2e push, Claude may declare `REPAIR_WORKER`. Claude performs no
stage, commit, push or self-approval and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_REVIEW`

## 9. Independent approval

Codex independently reproduced F5-F8 and approves this exact 44-path repair
boundary under the operator-delegated reviewer authority.
