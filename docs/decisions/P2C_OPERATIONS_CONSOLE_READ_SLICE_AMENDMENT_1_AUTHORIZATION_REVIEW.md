# P2-C C3a Amendment 1 — Authorization Review

- Review ID: `P2C-C3A-AMENDMENT-1-AUTHORIZATION-REVIEW-2026-07-29`
- Design:
  `docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM.md`
- SPEC:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC_AMENDMENT_1.md`
- Work Order:
  `docs/work_orders/P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER_AMENDMENT_1.md`
- Reviewer: Codex, independent from the assigned implementation worker
- Risk: R2
- Disposition: `REVIEW_PASS — C3a REPAIR AUTHORIZED; C3b GATED`

## Review result

The amendment is necessary, minimal and feasible:

- `_event_queries.py` is the narrowest repository-consistent split that
  restores the hard file-size invariant without compressing or weakening it;
- `test_p2b_openapi_contract.py` is load-bearing predecessor evidence and must
  participate in the additive P2-C delta chain rather than remain knowingly
  red;
- neither path changes the product boundary or opens mutation behavior;
- the OpenAPI repair requires structural subtraction/proof, not a blind hash
  refresh;
- the independently observed clean G5 state establishes that `uv.lock` is
  interrupted-BUILD residue, so exact-file removal does not broaden the
  tracked ceiling or authorize general cleanup;
- the original live PostgreSQL, exactly-one-provider-call, regression,
  cleanup, secret-safety and independent-review gates remain intact.

No waiver is granted for existing test, contract, catalog, file-size or
validator failures. The worker must repair and rerun them.

## Role route

`ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR -> REVIEWER`
(this amendment) `-> REPAIR_WORKER` (Claude) `-> REVIEWER`
(Codex) `-> COMMIT_STEWARD` only after independent `REVIEW_PASS`.

## Authorization

After this four-document amendment commit is rehearsed and pushed, Claude may
resume C3a as `REPAIR_WORKER` against the amended 25-path ceiling. Claude may
not edit continuity, stage, commit, push, self-approve or begin C3b.
