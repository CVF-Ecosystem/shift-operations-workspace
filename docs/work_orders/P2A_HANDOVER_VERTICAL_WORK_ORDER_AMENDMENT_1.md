# Work Order Amendment 1 — P2-A Handover Legacy Freeze Tests

ID: `P2A-HANDOVER-WO-AMENDMENT-1`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — REPAIR PROHIBITED UNTIL C2b AND C2c ARE PUSHED
Amends: `P2A_HANDOVER_VERTICAL_WORK_ORDER.md`

## 1. Authorization defect

The stopped BUILD exposed `HOV-AUTH-F4 — LEGACY_FREEZE_TEST_SCOPE_OMISSION`.
Codex independently reproduced four failures in two legacy test paths omitted
from the exact authorization. Making those tests pass through a production
bypass would violate SPEC R11/AC-11 and is prohibited.

## 2. Exact amended C3 changed set

Parent Work Order section 3's 39 paths remain required. Add exactly:

40. `tests/cvf/test_atomic_mutation_audit.py`
41. `tests/cvf/test_customer_request_vertical.py`

The final C3 changed set is exactly 41 paths. No 42nd path is conditional.

Permission on paths 40-41 is limited to:

- constructing a source and destination shift;
- creating a server-derived handover through `HandoverService`;
- genuine review by one authenticated supervisor;
- genuine acknowledgement by a distinct authenticated supervisor;
- retaining the original test's rollback or frozen-parent assertion.

No direct terminal-state insertion, readiness mock, production bypass,
customer-request semantic change, unrelated cleanup or broad refactor.

## 3. Repair role and order

After C2b and C2c are pushed, Claude may declare `REPAIR_WORKER` and:

1. repair only paths 40-41 for `HOV-AUTH-F4`;
2. repair the already-authorized handover/freeze implementation where needed
   to satisfy parent R4/R11/R12, including destination revalidation and one
   freeze transaction;
3. finish the remaining parent Work Order steps and evidence;
4. stop at `READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_REVIEW`.

Claude performs no stage, commit, push or self-approval.

## 4. Mandatory focused evidence

In addition to all parent evidence:

```text
python -m pytest tests/cvf/test_atomic_mutation_audit.py
                 tests/cvf/test_customer_request_vertical.py
                 tests/cvf/test_freeze_invariant.py
                 tests/cvf/test_handover_vertical.py -q
```

must pass, and the full `tests/` suite must have zero failure/error. Evidence
must show paths 40-41 contain no change beyond the bounded setup/assertions.

## 5. Stop conditions

All parent stop conditions remain. STOP again on:

- a required 42nd path;
- any attempt to preserve legacy tests with a production readiness bypass;
- atomic readiness/freeze/audit not sharing one transaction;
- destination OPEN not revalidated at freeze;
- change to the original behavioral purpose of either legacy test.

## 6. Commit graph

- C1: original authorization, pushed.
- C2: original pre-BUILD continuity, pushed.
- C2b: exactly these three amendment artifacts, zero implementation paths.
- C2c: continuity acknowledgment of C2b and the bounded repair route.
- C3: exactly 41 BUILD paths, only after independent REVIEW_PASS.
- C4: unchanged parent closure set.

The existing unstaged BUILD remains evidence input and is not staged into C2b
or C2c.

## 7. Independent approval

Codex independently reproduced and classified `HOV-AUTH-F4`. The finding is
closed without waiver by the ADR/SPEC/Work Order amendment set. This exact
41-path ceiling is approved under the operator-delegated reviewer authority,
subject to C2b/C2c push before repair resumes.
