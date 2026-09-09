# P4-E Exact Manifest Amendment 2 - Closure Ordering

Memory class: governed-exact-manifest-amendment

docType: exact_manifest_amendment

Batch ID: P4E-AMENDMENT2-CLOSURE-ORDERING-2026-09-10

Status: DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW

## Purpose

Resolve one machine-reproduced closeability cycle without changing P4-E
product scope. After the independently accepted repair, CLOSER must regenerate
catalog paths 93-94 before the final full suite. That canonical generation
changes `docs/catalog/MODULE_REGISTRY.json`, which immediately makes the
Project Knowledge Pack fail until paths 91-92 are synchronized. Amendment 1,
however, schedules paths 83-92 only after the material commit while requiring
the full suite to pass before that commit. All three rules cannot be satisfied
in their current order.

Finding ID: `P4E-AM2-CLOSEABILITY-F1`

## Authority And Preserved Boundary

- Amendment 1 remains authoritative for the accepted 109-path implementation
  and repair packet.
- Product paths, risk ceiling R2, provider/network boundary, PostgreSQL proof,
  catalog ownership, independent review, and no-push boundary are unchanged.
- No product repair is authorized by this amendment.
- Existing paths 83-92 remain the only session/status/knowledge write surface;
  paths 93-94 remain the only catalog write surface.

## Additive Control-Plane Paths

110. `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_AMENDMENT_2_2026-09-10.md`
111. `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_2_2026-09-10.md`
112. `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_2_AUTHORIZATION_REVIEW_2026-09-10.md`

No other new path is authorized. Paths 110-111 are ORCHESTRATOR /
WORK_ORDER_AUTHOR-owned. Path 112 is INDEPENDENT_AUTHORIZATION_REVIEWER-owned.

## Corrected Closure Choreography

1. Technical independent review accepts the repair without waiver.
2. CLOSER regenerates only catalog paths 93-94 and confirms catalog,
   repository, invariant, and file-size gates.
3. If Project Knowledge then fails solely because catalog/status/roadmap source
   hashes or current P4-E state are stale, SESSION_SYNC_STEWARD may synchronize
   only paths 83-92 before the final full suite.
4. The synchronized state is a closure candidate until the final suite passes;
   it must record that exact evidence boundary and must not imply provider,
   deployment, production, or public readiness.
5. CLOSER runs the complete suite after the synchronization. Any non-continuity
   failure blocks closure.
6. Independent completion review records a bounded
   `MATERIAL_COMMIT_AUTHORIZED_PENDING_POST_COMMIT_CONTINUITY_FINALIZATION`
   disposition on existing path 82 after the pre-material suite passes.
7. COMMIT_STEWARD creates one material commit containing accepted product,
   worker return, review, and catalog paths, excluding paths 83-92.
8. SESSION_SYNC_STEWARD finalizes paths 83-92 with the actual material commit
   SHA, then CLOSER reruns the full required gate set, including the complete
   suite. No path other than 83-92 may change in this interval.
9. Independent completion review records terminal acceptance on path 82;
   because path 82 is not a Project Knowledge source pin, this evidence-only
   update does not invalidate the post-material full suite. File-size,
   knowledge, catalog, repository, and diff checks are rerun afterward.
10. SESSION_SYNC_STEWARD creates one separate continuity commit containing
   only paths 83-92. Terminal closure exists only after this post-material gate
   cycle and continuity commit pass.

This is an ordering correction only. It creates both a pre-material candidate
gate and a post-material final gate; it does not waive any gate or combine the
material and continuity commits.

## Activation Preconditions

- Independent authorization review of paths 110-111 returns
  `AUTHORIZATION_REVIEW_PASS` with findings and waivers `NONE/NONE`.
- Paths 110-112 are committed alone as a control-plane activation commit;
  existing product/catalog/review changes remain unstaged.
- Activation HEAD and empty staging after commit are recorded before the early
  session-sync transition.

## Stop Conditions

Stop on any requested product edit, path outside 82-94 after activation
(reviewer only 82, session-sync only 83-92, closer only 93-94),
non-continuity full-suite failure, provider/network/install/shared-database/
deployment/public action, or inability to preserve exact two-commit material
then continuity ordering.

## Public Export Disposition

DEFERRED_PRIVATE_ONLY

Reason: private project closure-order correction; no public export is in scope.

## Claim Boundary

This amendment proves only that the prior phase order is cyclic under the
machine-observed Project Knowledge source-pin dependency. It authorizes the
minimal ordering change above and makes no P4-E correctness or closure claim.
