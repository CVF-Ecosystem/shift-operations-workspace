# SPEC Amendment 2 — P2-A Handover Independent Review Repair

ID: `P2A-HANDOVER-SPEC-AMENDMENT-2`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: REVIEW_PASS
Design: `docs/decisions/ADR_2026-07-26_P2A_HANDOVER_REVIEW_REPAIR_ADDENDUM.md`
Amends: `P2A_HANDOVER_VERTICAL_SPEC.md` and Amendment 1

## Scope

Parent R1-R19 and AC-01-AC-25 remain in force except AC-20's exact changed set,
which is superseded below. This amendment adds executable guard and ledger
parity requirements that make existing parent R7/R13 testable.

## Added requirements

### R20 — customer-request test split

`test_customer_request_vertical.py`,
`_customer_request_fixtures.py`, and
`test_customer_request_transitions.py` must each be at most 300 physical
lines and form a coherent create/HTTP, shared-fixture, and
transition/atomicity split. The customer-request debt entry is removed, not
rehashed. The two unrelated remaining debt entries are byte-identical.

### R21 — controlled ledger parity

Both ledger backends must reject, with the same controlled `ValueError`
category and no partial persistence:

- duplicate aggregate ID;
- duplicate item `(source_record_type, source_record_id)` within a handover;
- item whose `handover_id` differs from its aggregate;
- missing source or destination shift.

No raw SQLAlchemy `IntegrityError` may escape these cases. Error text must
distinguish duplicate aggregate, duplicate item, item/aggregate mismatch and
missing shift rather than mislabeling every integrity failure as duplicate ID.

### R22 — immutable snapshot on put

`put_handover` may update lifecycle-owned fields only: status, reviewer/
receiver identities and timestamps, and version. It must reject changes to
from/to shift IDs or any item/snapshot/evidence field identically on both
backends. A rejected put leaves aggregate/items/evidence unchanged.

### R23 — truthful receipts

The build and live receipts must record F5-F8 and quote only fresh post-repair
counts. Prior live evidence may remain historical, but final REVIEW_PASS
requires fresh reviewer PostgreSQL and provider reruns after repair.

## Acceptance criteria

- **AC-20 (superseded):** C3 changes exactly 44 authorized paths; no 45th path.
- **AC-26:** all three customer-request split files are <=300 and the debt
  baseline contains exactly the two untouched legacy entries.
- **AC-27:** dedicated cross-backend tests prove every R21 controlled failure
  and no partial write.
- **AC-28:** dedicated cross-backend tests prove R22 immutable put behavior and
  allowed lifecycle puts.
- **AC-29:** full suite, file-size guard and repository validator pass together.
- **AC-30:** corrected receipts match fresh command output and finding history.

## Claim boundary

This amendment closes gaps in already-approved persistence and guard
requirements. It does not broaden the handover API, source membership,
assignment claim, migration schema, or roadmap scope.

## Disposition

F5-F8 are accepted at SPEC without waiver. AC-20 and AC-26-AC-30 are approved
under the delegated independent reviewer authority.
