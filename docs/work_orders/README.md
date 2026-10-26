# Work Orders

Store project-governed work orders here and link active artifacts from docs/INDEX.md.
Historical inline authorizations remain in SESSION/handoffs; do not backfill or
rewrite settled historical work orders.

## Mandatory before dispatch or redispatch

Every new or revised assignment, including inline handoffs and support/repair
work, MUST include **Product Milestone Binding** under
[Acceptance Gates](../implementation/ACCEPTANCE_GATES.md#product-milestone-binding).
Use that canonical contract rather than copying a second rule set here.

Bind the named product milestone, user outcome and complete acceptance/gap
reconciliation; identify assigned gap IDs and every unassigned remainder with
owner and concrete destination. Include a bounded stop condition and return to
product work for support tasks. Missing coverage blocks dispatch. The same
reconciliation must be updated on worker return, review and closure.

This block supplements existing scope, risk, authorization, phase, invariant
and gate-to-role closeability requirements. It does not grant execution rights.
