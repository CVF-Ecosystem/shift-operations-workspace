# ADR Addendum — P2-A Handover Independent Review Repair

ID: `ADR-2026-07-26-P2A-HANDOVER-REVIEW-REPAIR`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Phase: DESIGN amendment after independent BUILD review
Status: REVIEW_PASS
Amends: `ADR_2026-07-26_P2A_HANDOVER_VERTICAL.md`

## Independent findings

Codex reviewed source, authorization, guards and fresh execution rather than
accepting the worker receipts as approval evidence.

### HOV-REV-F5 — DEBT_RATCHET_BYPASS

Amendment 1 authorized a narrow content edit to
`tests/cvf/test_customer_request_vertical.py`, but the parent authorization
still required every touched Python file to be at most 300 lines and protected
the remaining debt entries. BUILD left the file at 321 lines and rewrote its
digest-bound debt entry. That defeats the ratchet: the baseline explicitly
says any content edit forces a coherent split in the same changed set.

Decision: split the file into two coherent test modules plus a shared fixture
module and remove its debt entry. A scope ceiling cannot waive an executable
guard; the ceiling must be amended.

### HOV-REV-F6 — CONTINUITY_GATE_RED

`check_file_size.py` and `validate_repository.py` fail because
`SESSION/SESSION_MEMORY.md` is 607 lines. The overage was introduced by
reviewer-owned C2c continuity, not by the worker's 41 BUILD paths.

Decision: Codex owns a separate continuity repair before BUILD repair resumes.
It is not part of C3 and is not delegated to Claude.

### HOV-REV-F7 — LEDGER_PARITY_AND_IMMUTABILITY_GAP

Fresh probes found behavior forbidden by parent ADR 3.3 and SPEC R7:

- InMemoryLedger accepts duplicate `(record_type, record_id)` handover items;
- SqlLedger leaks raw `IntegrityError` for the same duplicate;
- InMemoryLedger accepts missing source/destination shift IDs;
- SqlLedger mislabels a shift-FK failure as `duplicate handover_id`;
- `put_handover` does not enforce the immutable snapshot boundary identically
  across backends.

Existing tests cover aggregate duplicate IDs but not duplicate items, FK error
shape or immutable `put_handover`. Green tests therefore did not establish the
approved ledger-parity claim.

Decision: both backends must prevalidate the same aggregate/item/FK and
immutable-snapshot rules and return the same controlled `ValueError` shape
without partial writes. A dedicated cross-backend test module owns these
requirements.

### HOV-REV-F8 — BUILD_RECEIPT_DRIFT

The BUILD receipt claims `571 passed`; the independent rerun at the reviewed
tree produced `567 passed, 53 skipped, 1 warning`. The receipt must quote the
fresh post-repair result and record F5-F8 plus the fact that PostgreSQL/provider
re-review stopped when F7 was found.

## Exact split decision

Add:

1. `tests/cvf/_customer_request_fixtures.py`;
2. `tests/cvf/test_customer_request_transitions.py`;
3. `tests/integration/test_handover_ledger_parity.py`.

The original customer-request module becomes the coherent create/HTTP module;
the new transition module owns lifecycle/transition atomicity; the shared
fixture module owns backend/principal/request setup. Existing imports from the
original module may be preserved by explicit re-export, without duplicating
fixture definitions.

## Boundary

No new production surface is added. Existing handover store/repository paths
may change only to enforce already-approved R7 and immutable-snapshot rules.
Migration 006 and the public API contract do not expand. No authentication,
approval, report, customer-request service, incident, task or event semantic
change is authorized.

No live provider call is needed to authorize repair. The parent PostgreSQL and
provider gates remain mandatory after all findings are repaired.

## Disposition

F5-F8 are accepted without waiver. This design amendment is independently
approved. Repair remains prohibited until its SPEC/Work Order companions and
reviewer-owned continuity repair are pushed.
