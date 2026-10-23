# P5-A2 independent SPEC review

Disposition: SPEC_REVIEW_PASS_BOUNDED
Date: 2026-10-24. Risk R2. Reviewer: root INTERNAL_AGENT REVIEWER,
independent of the SPEC_AUTHOR. Source assessed fd903371; no product source delta.

## Target, method and findings

Whole milestone and all14 gaps remain bound by
docs/decisions/P5A2_PROACTIVE_REPORTING_INTAKE_DESIGN_2026-10-24.md.
Root checked canonical Report/ReportContent, aggregate_digest, history stores,
assignment scope, worker skeleton, numerical definitions and matrix ownership.
Routine defaults accepted: snapshot-observed Incident record_id counts per
distinct shift; next eligible observation horizon; six-count median; effective
18-observation floor with12 recent out-of-origin folds. These defaults are
technical choices, not operator business acceptance or demonstrated accuracy.

Two consolidated repair rounds resolved canonical record IDs, late-version
exclusion versus invalid selected times, exact historical fold reconstruction,
history floors, latest12 rather than oldest folds, complete supplied manifest
and bounds, exact lineage/evaluation digest payloads, nonprobabilistic envelope
labeling, READY-only signals and selected/unselected abstention lineage.
No remaining finding or waiver in this SPEC boundary. No third repair round.

## Invariant-Family Proof

Owner: docs/cvf/INVARIANT_FAMILY_STANDARD.md; family P5A2-PROACTIVE-OUTCOMES.
Root recomputed SPEC canonical SHA256
fd35641cf43768c1d35a5187c43af7b3c8a3e08caaa21253e9527ed3ae67bf5e
and matrix canonical SHA256
4ff487569ef29d413dcd3e51e3e595057f395f61a0cd79ea299b046a54f2e573.
Static pin docs/specs/p5a2_proactive_invariant_pin.py matches. Independent
structural samples cover all8 shapes including both abstention states,342
generated mutations, exact mutation-ID coverage and unique positive matching.
All pass through the existing invariant_family_contract and mutation oracle.
Local detail: .venv/p5a2-spec-structural-review.json. This is matrix mechanics
only, with no actual run/emitter, numerical result, scheduling or AI proof.
Root acknowledges all8 RECURSE_NESTED_OBJECTS exclusions: abstract receipts are
flat; full nested lineage and actual result binding remain future adapter proof.
Real scheduler/API emitter corpus and cross-surface parity remain unimplemented.
Commands: python scripts/check_invariant_families.py; existing Python contract
matches_shape_exactly/generate_mutations/required_mutation_ids for each shape.
Independent source was fixed before numerical BUILD; worker may not rewrite it.

## Risk, disposition and product return

Public doctor24/2; inheritance/closeability0/0. Both Core references read-only.
One bounded reference reconciliation at721f98dec; no guard or policy change.
The historical P5-A handoff is retained byte-for-byte at HEAD. Live/key/model/
CSV updates remain deferred; original401attempt spent, additional trial held.

SPEC accepted only. All14 product gaps remain open/blocked/held, Phase5 0/5.
Source/history/numeric implementation requires the separately reviewed bounded
Work Order, committed dispatch and material-SHA acknowledgment before BUILD.
Whole P5-A2 still needs reporting/RAG readiness, integrated API/UI/scheduler,
exact human approval, real operational quality evidence and applicable live proof.
Root owns every remainder and P5-B/C/D routing in the canonical binding.
