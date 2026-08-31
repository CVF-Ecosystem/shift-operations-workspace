# Project Documentation Index

## Start Here

- Session front door (canonical): [`SESSION/SESSION_MEMORY.md`](../SESSION/SESSION_MEMORY.md)
- Active state (canonical, machine): [`SESSION/ACTIVE_SESSION_STATE.json`](../SESSION/ACTIVE_SESSION_STATE.json)
- Active handoff: file under [`SESSION/handoffs/`](../SESSION/handoffs/) named by
  `active_handoff` in the active state above
- Implementation truth: [`IMPLEMENTATION_STATUS.json`](../IMPLEMENTATION_STATUS.json)
- Machine module registry: [`docs/catalog/MODULE_REGISTRY.json`](catalog/MODULE_REGISTRY.json)
- Human module catalog: [`docs/catalog/MODULE_CATALOG.md`](catalog/MODULE_CATALOG.md)
- Contribution / workflow front door: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- Agent operating contract: [`AGENTS.md`](../AGENTS.md)
- Docs entry point (general orientation): [`docs/README.md`](README.md)
- Accepted fresh CVF Core refresh INTAKE (target `06c3d040`;
  `INTAKE_REVIEW_PASS`; P4-E parked):
  [`INTAKE_2026-08-29_CVF_CORE_REFRESH.md`](decisions/INTAKE_2026-08-29_CVF_CORE_REFRESH.md)
- Independent fresh Core refresh INTAKE review (`PASS`; findings/waivers
  `NONE/NONE`):
  [`INTAKE_REVIEW_2026-08-29_CVF_CORE_REFRESH.md`](decisions/INTAKE_REVIEW_2026-08-29_CVF_CORE_REFRESH.md)
- Fresh Core refresh DESIGN (independently accepted; no automatic SPEC/external-
  effect authority):
  [`DESIGN_2026-08-29_CVF_CORE_REFRESH.md`](decisions/DESIGN_2026-08-29_CVF_CORE_REFRESH.md)
- Independent fresh Core refresh DESIGN review/rereviews (`DESIGN_REVIEW_PASS`;
  F1/F2 closed; final findings/waivers `NONE/NONE`):
  [`DESIGN_REVIEW_2026-08-29_CVF_CORE_REFRESH.md`](decisions/DESIGN_REVIEW_2026-08-29_CVF_CORE_REFRESH.md)
- Core refresh reviewer-target-movement DESIGN amendment (ready for independent
  review after SPEC F4; subsequently repaired and accepted):
  [`DESIGN_AMENDMENT_2026-08-29_CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT.md`](decisions/DESIGN_AMENDMENT_2026-08-29_CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT.md)
- Independent DESIGN amendment review/rereview (`PASS`; F1 closed;
  findings/waivers `NONE/NONE`):
  [`DESIGN_AMENDMENT_REVIEW_2026-08-29_CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT.md`](decisions/DESIGN_AMENDMENT_REVIEW_2026-08-29_CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT.md)
- Fresh Core refresh SPEC (final `SPEC_REVIEW_PASS`; F1-F4 closed;
  findings/waivers `NONE/NONE`):
  [`CVF_CORE_REFRESH_2026-08-29_SPEC.md`](specs/CVF_CORE_REFRESH_2026-08-29_SPEC.md)
- Independent fresh Core refresh SPEC review:
  [`SPEC_REVIEW_2026-08-29_CVF_CORE_REFRESH.md`](decisions/SPEC_REVIEW_2026-08-29_CVF_CORE_REFRESH.md)
- Fresh Core refresh invariant matrix and canonical pin:
  [`cvf-core-refresh-outcomes-2026-08-29.json`](cvf/invariants/cvf-core-refresh-outcomes-2026-08-29.json),
  [`cvf_core_refresh_2026_08_29_invariant_pin.py`](specs/cvf_core_refresh_2026_08_29_invariant_pin.py)
- Bounded fresh Core refresh Work Order (`AUTHORIZATION_REVIEW_PASS`; F1
  closed; exact BUILD boundary explicitly approved; commit/push excluded):
  [`CVF_CORE_REFRESH_2026-08-29_WORK_ORDER.md`](work_orders/CVF_CORE_REFRESH_2026-08-29_WORK_ORDER.md)
- Independent fresh Core refresh authorization review (`PASS`; F1 closed;
  findings/waivers `NONE/NONE`):
  [`AUTHORIZATION_REVIEW_2026-08-29_CVF_CORE_REFRESH.md`](decisions/AUTHORIZATION_REVIEW_2026-08-29_CVF_CORE_REFRESH.md)
- Closed-bounded 2026-08-29 Core refresh handoff:
  [`CVF_CORE_REFRESH_2026-08-29.md`](../SESSION/handoffs/CVF_CORE_REFRESH_2026-08-29.md)
- Fresh Core refresh BUILD worker evidence (`FAILURE_ROLLED_BACK`; public
  target moved before pin edits/initializer; independent completion review
  `REVIEW_PASS_FAILURE_ROLLED_BACK`, findings/waivers `NONE/NONE`):
  [`CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json`](decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json),
  [`CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md`](decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md),
  [`CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md`](decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md)
- Fresh target-rebase Core refresh INTAKE (`d786013`; independent review
  `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`):
  [`INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`](decisions/INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md)
- Independent target-rebase INTAKE review (`PASS`; findings/waivers
  `NONE/NONE`):
  [`INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`](decisions/INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md)
- Target-rebase DESIGN (attempt-2 evidence lifecycle; independent review
  `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`):
  [`DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`](decisions/DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md)
- Independent target-rebase DESIGN review (`PASS`; findings/waivers
  `NONE/NONE`):
  [`DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`](decisions/DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md)
- Target-rebase SPEC and successor invariant family (final review PASS;
  conformance `7/7`, `686/686`, temporal `40/40`):
  [`CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30_SPEC.md`](specs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30_SPEC.md),
  [`cvf-core-refresh-target-rebase-outcomes-2026-08-30.json`](cvf/invariants/cvf-core-refresh-target-rebase-outcomes-2026-08-30.json),
  [`cvf_core_refresh_target_rebase_2026_08_30_invariant_pin.py`](specs/cvf_core_refresh_target_rebase_2026_08_30_invariant_pin.py)
- Independent target-rebase SPEC review/rereview (final `SPEC_REVIEW_PASS`;
  F1 closed; findings/waivers `NONE/NONE`):
  [`SPEC_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`](decisions/SPEC_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md)
- Exact target-rebase Work Order (`AUTHORIZATION_REVIEW_PASS`; operator
  explicitly approved exact BUILD external effects; commit/push excluded):
  [`CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30_WORK_ORDER.md`](work_orders/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30_WORK_ORDER.md)
- Independent target-rebase authorization review (`PASS`; findings/waivers
  `NONE/NONE`; later exact BUILD approval recorded in active handoff):
  [`AUTHORIZATION_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`](decisions/AUTHORIZATION_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md)
- Closed-bounded target-rebase handoff:
  [`CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30.md`](../SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30.md)
- Target-rebase attempt-2 BUILD evidence and independent completion review
  (`REVIEW_PASS_FAILURE_ROLLED_BACK`; findings/waivers `NONE/NONE`; target not
  adopted; no retry/commit/push):
  [`CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json`](decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json),
  [`CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_ATTEMPT_2.md`](decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_ATTEMPT_2.md),
  [`CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_ATTEMPT_2.md`](decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_ATTEMPT_2.md)
- Fresh exact-target Core rebase INTAKE for `0281e93` (`INTAKE_REVIEW_PASS`,
  findings/waivers `NONE/NONE`; BUILD/reconcile withheld through Work Order review):
  [`INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md)
- Independent exact-target INTAKE review:
  [`INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md)
- Exact-target DESIGN and independent review (`DESIGN_REVIEW_PASS`,
  findings/waivers `NONE/NONE`):
  [`DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md),
  [`DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md)
- Final exact-target SPEC, successor invariant family and SPEC review
  (`SPEC_REVIEW_PASS`; F1 closed; `8/1257/40/6/4`):
  [`CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30_SPEC.md`](specs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30_SPEC.md),
  [`cvf-core-refresh-target-rebase-0281e93-outcomes-2026-08-30.json`](cvf/invariants/cvf-core-refresh-target-rebase-0281e93-outcomes-2026-08-30.json),
  [`SPEC_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/SPEC_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md)
- Exact Work Order and authorization review/rereview (`PASS`; F1 closed;
  findings/waivers `NONE/NONE`):
  [`CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-31_WORK_ORDER.md`](work_orders/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-31_WORK_ORDER.md),
  [`AUTHORIZATION_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/AUTHORIZATION_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md),
  [`AUTHORIZATION_REREVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`](decisions/AUTHORIZATION_REREVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md)
- Attempt-3 independent completion review (`REVIEW_PASS_ZERO_EFFECT_PREFLIGHT_REFUSAL`,
  findings/waivers `NONE/NONE`; target not adopted; no retry):
  [`CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md`](decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md)
- Active fresh `0281e93` target-rebase handoff:
  [`CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30.md`](../SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30.md)
- Historical 2026-08-23 CVF Core refresh INTAKE (`PASS`, F1-F2 closed):
  [`INTAKE_2026-08-23_CVF_CORE_REFRESH.md`](decisions/INTAKE_2026-08-23_CVF_CORE_REFRESH.md)
- Independent Core refresh INTAKE review (`CHANGES_REQUIRED`, F1-F2 repaired,
  then final `PASS`, findings/waivers `NONE/NONE`):
  [`INTAKE_REVIEW_2026-08-23_CVF_CORE_REFRESH.md`](decisions/INTAKE_REVIEW_2026-08-23_CVF_CORE_REFRESH.md)
- Active Core refresh DESIGN (prior review PASS; evidence-contract amendment
  open for independent review):
  [`DESIGN_2026-08-23_CVF_CORE_REFRESH.md`](decisions/DESIGN_2026-08-23_CVF_CORE_REFRESH.md)
- Independent Core refresh DESIGN review (prior review PASS; evidence-contract
  amendment `AMENDMENT_PASS`, findings/waivers `NONE/NONE`):
  [`DESIGN_REVIEW_2026-08-23_CVF_CORE_REFRESH.md`](decisions/DESIGN_REVIEW_2026-08-23_CVF_CORE_REFRESH.md)
- Core refresh SPEC (evidence-contract amendment `SPEC_AMENDMENT_PASS`,
  findings/waivers `NONE/NONE`, matrix `b62eae33...`):
  [`CVF_CORE_REFRESH_2026-08-23_SPEC.md`](specs/CVF_CORE_REFRESH_2026-08-23_SPEC.md)
- Independent Core refresh SPEC review (original findings closed; evidence-
  contract amendment repair round 2 `PASS`, findings/waivers `NONE/NONE`):
  [`SPEC_REVIEW_2026-08-23_CVF_CORE_REFRESH.md`](decisions/SPEC_REVIEW_2026-08-23_CVF_CORE_REFRESH.md)
- Exact Core refresh Work Order (`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`, F1/F4
  closed; post-escalation rereview remains `CHANGES_REQUIRED` with three
  provenance blockers and fresh authority required;
  BUILD unauthorized):
  [`CVF_CORE_REFRESH_2026-08-23_WORK_ORDER.md`](work_orders/CVF_CORE_REFRESH_2026-08-23_WORK_ORDER.md)
- Independent Core refresh authorization review (`CHANGES_REQUIRED`, F1/F4
  closed; third rereview recorded `REVIEW_COST_ESCALATION_REQUIRED`, operator
  authorized cycle consumed with final `CHANGES_REQUIRED`; waivers `NONE`):
  [`AUTHORIZATION_REVIEW_2026-08-23_CVF_CORE_REFRESH.md`](decisions/AUTHORIZATION_REVIEW_2026-08-23_CVF_CORE_REFRESH.md)
- Bounded Core refresh evidence-contract Work Order amendment
  (bounded rereview `CHANGES_REQUIRED`, four residuals, repair cycle consumed;
  BUILD unauthorized) and frozen raw-evidence adapter:
  [`CVF_CORE_REFRESH_2026-08-23_EVIDENCE_CONTRACT_AMENDMENT.md`](work_orders/CVF_CORE_REFRESH_2026-08-23_EVIDENCE_CONTRACT_AMENDMENT.md),
  [`cvf_core_refresh_evidence_adapter.py`](work_orders/cvf_core_refresh_evidence_adapter.py)
- Bootstrap-native Core refresh simplification DESIGN
  (`DESIGN_REVIEW_PASS`; final F1 acceptance amendment PASS; retires the
  low-value 8x2 proof path):
  [`DESIGN_2026-08-23_CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION.md`](decisions/DESIGN_2026-08-23_CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION.md)
- Bootstrap-native Core refresh simplification SPEC
  (`SPEC_REVIEW_PASS`; final F1 acceptance amendment PASS; minimal direct
  evidence only):
  [`CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION_SPEC.md`](specs/CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION_SPEC.md)
- Bootstrap-native Core refresh Work Order
  (`CLOSED_BOUNDED`; exact target `864c4e0`; final review `NONE/NONE`):
  [`CVF_CORE_REFRESH_2026-08-24_BOOTSTRAP_NATIVE_WORK_ORDER.md`](work_orders/CVF_CORE_REFRESH_2026-08-24_BOOTSTRAP_NATIVE_WORK_ORDER.md)
- Core refresh BUILD evidence and final completion review (`PASS`, F1 closed,
  findings/waivers `NONE/NONE`; no 33-path byte-equality claim):
  [`CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json`](decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json),
  [`CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md`](decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md),
  [`CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_COMPLETION_REVIEW_2026-08-24.md`](decisions/CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_COMPLETION_REVIEW_2026-08-24.md)
- Historical 2026-08-23 CVF Core refresh handoff (`CLOSED_BOUNDED`):
  [`CVF_CORE_REFRESH_2026-08-23.md`](../SESSION/handoffs/CVF_CORE_REFRESH_2026-08-23.md)
- Accepted P4-C Integration Edge INTAKE (`INTAKE_REVIEW_PASS`):
  [`INTAKE_2026-08-23_P4C_INTEGRATION_EDGE.md`](decisions/INTAKE_2026-08-23_P4C_INTEGRATION_EDGE.md)
- Independent P4-C INTAKE review (`CHANGES_REQUIRED`, F1 repaired pending
  rereview then final `PASS`, findings/waivers `NONE/NONE`):
  [`P4C_INTEGRATION_EDGE_INTAKE_REVIEW_2026-08-23.md`](decisions/P4C_INTEGRATION_EDGE_INTAKE_REVIEW_2026-08-23.md)
- Accepted P4-C DESIGN (`DESIGN_REVIEW_PASS`):
  [`DESIGN_2026-08-23_P4C_INTEGRATION_EDGE.md`](decisions/DESIGN_2026-08-23_P4C_INTEGRATION_EDGE.md)
- Independent P4-C DESIGN review (final `PASS`; path-67 amendment `PASS`,
  findings/waivers `NONE/NONE`):
  [`P4C_INTEGRATION_EDGE_DESIGN_REVIEW_2026-08-23.md`](decisions/P4C_INTEGRATION_EDGE_DESIGN_REVIEW_2026-08-23.md)
- Accepted P4-C SPEC and invariant matrices (`SPEC_REVIEW_PASS`):
  [`P4C_INTEGRATION_EDGE_SPEC.md`](specs/P4C_INTEGRATION_EDGE_SPEC.md),
  [`p4c-ingress-terminal-outcomes.json`](cvf/invariants/p4c-ingress-terminal-outcomes.json),
  [`p4c-outbound-terminal-outcomes.json`](cvf/invariants/p4c-outbound-terminal-outcomes.json)
- Independent P4-C SPEC review (final `SPEC_REVIEW_PASS`; findings/waivers
  `NONE/NONE`):
  [`P4C_INTEGRATION_EDGE_SPEC_REVIEW_2026-08-23.md`](decisions/P4C_INTEGRATION_EDGE_SPEC_REVIEW_2026-08-23.md)
- P4-C parent Work Order plus reviewed amendments (final BUILD exact 68):
  [`P4C_INTEGRATION_EDGE_WORK_ORDER.md`](work_orders/P4C_INTEGRATION_EDGE_WORK_ORDER.md)
  [`P4C_INTEGRATION_EDGE_PATH67_WORK_ORDER_AMENDMENT_2026-08-25.md`](work_orders/P4C_INTEGRATION_EDGE_PATH67_WORK_ORDER_AMENDMENT_2026-08-25.md),
  [`P4C_FULL_SUITE_EXTERNAL_FAILURE_ACCEPTANCE_AMENDMENT_2026-08-25.md`](work_orders/P4C_FULL_SUITE_EXTERNAL_FAILURE_ACCEPTANCE_AMENDMENT_2026-08-25.md),
  [`P4C_P4A1_TEST_CLOCK_REPAIR_WORK_ORDER_2026-08-25.md`](work_orders/P4C_P4A1_TEST_CLOCK_REPAIR_WORK_ORDER_2026-08-25.md)
- Independent P4-C Work Order authorization review (`PASS`; F1 closed,
  findings/waivers `NONE/NONE`):
  [`P4C_INTEGRATION_EDGE_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md`](decisions/P4C_INTEGRATION_EDGE_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md)
- P4-C acceptance and path-68 amendment authorization reviews (final `PASS`;
  findings/waivers `NONE/NONE`):
  [`P4C_FULL_SUITE_EXTERNAL_FAILURE_ACCEPTANCE_AMENDMENT_AUTHORIZATION_REVIEW_2026-08-25.md`](decisions/P4C_FULL_SUITE_EXTERNAL_FAILURE_ACCEPTANCE_AMENDMENT_AUTHORIZATION_REVIEW_2026-08-25.md),
  [`P4C_P4A1_TEST_CLOCK_REPAIR_AUTHORIZATION_REVIEW_2026-08-25.md`](decisions/P4C_P4A1_TEST_CLOCK_REPAIR_AUTHORIZATION_REVIEW_2026-08-25.md)
- P4-C completion review (`FINAL_REVIEW_PASS`; exact 68; findings/waivers
  `NONE/NONE`; XR1 environmental debt retained):
  [`P4C_INTEGRATION_EDGE_COMPLETION_REVIEW_2026-08-25.md`](decisions/P4C_INTEGRATION_EDGE_COMPLETION_REVIEW_2026-08-25.md)
- Active P4-C handoff:
  [`P4C_INTEGRATION_EDGE_2026-08-23.md`](../SESSION/handoffs/P4C_INTEGRATION_EDGE_2026-08-23.md)
- Accepted P4-D Channel Adapters INTAKE (`INTAKE_REVIEW_PASS`):
  [`INTAKE_2026-08-26_P4D_CHANNEL_ADAPTERS.md`](decisions/INTAKE_2026-08-26_P4D_CHANNEL_ADAPTERS.md)
- Independent P4-D INTAKE review (final `INTAKE_REVIEW_PASS`; F1-F3 closed,
  findings/waivers `NONE/NONE`):
  [`P4D_CHANNEL_ADAPTERS_INTAKE_REVIEW_2026-08-26.md`](decisions/P4D_CHANNEL_ADAPTERS_INTAKE_REVIEW_2026-08-26.md)
- P4-D Channel Adapters DESIGN (`READY_FOR_INDEPENDENT_DESIGN_REVIEW`):
  [`DESIGN_2026-08-26_P4D_CHANNEL_ADAPTERS.md`](decisions/DESIGN_2026-08-26_P4D_CHANNEL_ADAPTERS.md)
- Independent P4-D DESIGN review (final `DESIGN_REVIEW_PASS`; F1-F4 closed,
  findings/waivers `NONE/NONE`):
  [`P4D_CHANNEL_ADAPTERS_DESIGN_REVIEW_2026-08-26.md`](decisions/P4D_CHANNEL_ADAPTERS_DESIGN_REVIEW_2026-08-26.md)
- P4-D Channel Adapters SPEC and invariant matrix (amended R3;
  `SPEC_AMENDMENT_REVIEW_PASS`):
  [`P4D_CHANNEL_ADAPTERS_SPEC.md`](specs/P4D_CHANNEL_ADAPTERS_SPEC.md),
  [`p4d-adapter-result-outcomes.json`](cvf/invariants/p4d-adapter-result-outcomes.json)
- Independent P4-D SPEC review (original `SPEC_REVIEW_PASS`, amended R3
  `SPEC_AMENDMENT_REVIEW_PASS`; findings/waivers `NONE/NONE`):
  [`P4D_CHANNEL_ADAPTERS_SPEC_REVIEW_2026-08-26.md`](decisions/P4D_CHANNEL_ADAPTERS_SPEC_REVIEW_2026-08-26.md)
- P4-D bounded Work Order (exact 54; amended closure sequencing;
  `AMENDMENT_AUTHORIZATION_REVIEW_PASS`):
  [`P4D_CHANNEL_ADAPTERS_WORK_ORDER.md`](work_orders/P4D_CHANNEL_ADAPTERS_WORK_ORDER.md)
- Independent P4-D Work Order authorization review (original
  `AUTHORIZATION_REVIEW_PASS`, amendment
  `AMENDMENT_AUTHORIZATION_REVIEW_PASS`; F1 closed, findings/waivers
  `NONE/NONE`):
  [`P4D_CHANNEL_ADAPTERS_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-26.md`](decisions/P4D_CHANNEL_ADAPTERS_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-26.md)
- P4-D BUILD worker return (exact worker paths 9–40; deterministic
  zero-network evidence):
  [`P4D_CHANNEL_ADAPTERS_WORKER_RETURN_2026-08-26.md`](decisions/P4D_CHANNEL_ADAPTERS_WORKER_RETURN_2026-08-26.md)
- Independent P4-D completion review (all findings closed; final
  `FINAL_REVIEW_PASS`, findings/waivers `NONE/NONE`):
  [`P4D_CHANNEL_ADAPTERS_COMPLETION_REVIEW_2026-08-26.md`](decisions/P4D_CHANNEL_ADAPTERS_COMPLETION_REVIEW_2026-08-26.md)
- Active P4-D handoff:
  [`P4D_CHANNEL_ADAPTERS_2026-08-26.md`](../SESSION/handoffs/P4D_CHANNEL_ADAPTERS_2026-08-26.md)
- Accepted P4-E Identity Mapping and Conversation Routing INTAKE (final
  `INTAKE_REVIEW_PASS`; no automatic DESIGN/BUILD authority):
  [`INTAKE_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md`](decisions/INTAKE_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md)
- Independent P4-E INTAKE review (`INTAKE_REVIEW_PASS`; findings/waivers
  `NONE/NONE`):
  [`P4E_IDENTITY_CONVERSATION_ROUTING_INTAKE_REVIEW_2026-08-29.md`](decisions/P4E_IDENTITY_CONVERSATION_ROUTING_INTAKE_REVIEW_2026-08-29.md)
- P4-E Identity Mapping and Conversation Routing DESIGN (independently
  accepted; no automatic SPEC/BUILD authority):
  [`DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md`](decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md)
- Independent P4-E DESIGN review and rereview (`DESIGN_REVIEW_PASS`; original
  findings F1-F5 closed; final findings/waivers `NONE/NONE`):
  [`P4E_IDENTITY_CONVERSATION_ROUTING_DESIGN_REVIEW_2026-08-29.md`](decisions/P4E_IDENTITY_CONVERSATION_ROUTING_DESIGN_REVIEW_2026-08-29.md)
- Active P4-E handoff:
  [`P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md`](../SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md)
- Predecessor learning INTAKE:
  [`INTAKE_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`](decisions/INTAKE_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md)
- Independent learning INTAKE review (`PASS`, `NONE/NONE`):
  [`CROSS_AGENT_INVARIANT_LEARNING_INTAKE_REVIEW_2026-08-22.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_INTAKE_REVIEW_2026-08-22.md)
- Accepted learning DESIGN:
  [`DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`](decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md)
- Independent learning DESIGN review (`PASS`, `NONE/NONE`):
  [`CROSS_AGENT_INVARIANT_LEARNING_DESIGN_REVIEW_2026-08-22.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_DESIGN_REVIEW_2026-08-22.md)
- Accepted learning SPEC v1.0:
  [`CROSS_AGENT_INVARIANT_LEARNING_SPEC.md`](specs/CROSS_AGENT_INVARIANT_LEARNING_SPEC.md)
- Independent learning SPEC review (`PASS`, `NONE/NONE`, `OBS-1..3`):
  [`CROSS_AGENT_INVARIANT_LEARNING_SPEC_REVIEW_2026-08-23.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_SPEC_REVIEW_2026-08-23.md)
- Exact-27 learning Work Order (`AUTHORIZATION_REVIEW_PASS`):
  [`CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER.md`](work_orders/CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER.md)
- Invariant-family standard, schema, registry and shared template:
  [`docs/cvf/INVARIANT_FAMILY_STANDARD.md`](cvf/INVARIANT_FAMILY_STANDARD.md),
  [`docs/cvf/invariants/registry.json`](cvf/invariants/registry.json),
  [`docs/cvf/invariants/invariant-family.schema.json`](cvf/invariants/invariant-family.schema.json),
  [`docs/templates/INVARIANT_FAMILY_PROOF.md`](templates/INVARIANT_FAMILY_PROOF.md)
- Core refresh evidence-contract invariant family and canonical pin:
  [`cvf-core-refresh-evidence-contract.json`](cvf/invariants/cvf-core-refresh-evidence-contract.json),
  [`cvf_core_refresh_evidence_contract_pin.py`](specs/cvf_core_refresh_evidence_contract_pin.py)
- Learning worker lineage and independent final review (`REVIEW_PASS_ROUND_10`,
  `NONE/NONE`, `FREEZE / CLOSED_BOUNDED`):
  [`CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md),
  [`CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md)

## Governed Artifact Families

- Decisions **and review evidence** (this project keeps both together, not in
  a separate `docs/reviews/`): [`docs/decisions/`](decisions/)
- Business/delivery roadmap (five-phase model, distinct from the AGENTS.md
  seven-step control chain): [`docs/implementation/EXECUTION_ROADMAP.md`](implementation/EXECUTION_ROADMAP.md)
  and [`docs/implementation/IMPLEMENTATION_PHASES.md`](implementation/IMPLEMENTATION_PHASES.md)
- Specifications — populated with discrete per-tranche artifacts
  (`P2B_AUTHENTICATION_REPAIR_SPEC.md`,
  `ALIBABA_LIVE_PROVIDER_CONFIGURATION_SPEC.md`, `CVF_CORE_PIN_SPEC.md`,
  `P4A3_APPLICATION_MEMORY_SPEC.md`, `P4B_AI_PROVIDERS_SPEC.md`):
  [`docs/specs/`](specs/). These are **per-tranche** governance specifications
  — testable requirements, acceptance criteria and claim boundaries for one
  bounded unit of work — not a complete specification of the system. Tranches
  predating this family still carry their spec content inline in handoffs and
  the roadmap.
- Work orders — populated alongside the specs above
  (`P2B_AUTHENTICATION_REPAIR_WORK_ORDER.md`,
  `ALIBABA_LIVE_PROVIDER_CONFIGURATION_WORK_ORDER.md`,
  `CVF_CORE_PIN_WORK_ORDER.md`, `P4A3_APPLICATION_MEMORY_WORK_ORDER.md`,
  `P4B_AI_PROVIDERS_WORK_ORDER.md`):
  [`docs/work_orders/`](work_orders/). Each
  authorizes one bounded changed set with its roles, required evidence, stop
  conditions and commit ownership; the same per-tranche scope caveat applies.
- CVF control mapping: [`docs/cvf/CVF_CONTROL_MAPPING.md`](cvf/CVF_CONTROL_MAPPING.md)
- Architecture / boundary rules: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](architecture/FRONTEND_BACKEND_BOUNDARY.md)
- File size guard: [`docs/reference/FILE_SIZE_GUARD.md`](reference/FILE_SIZE_GUARD.md)

Plans describe intended work. `IMPLEMENTATION_STATUS.json`, source, tests, and
review evidence (currently under `docs/decisions/`) determine what is actually
implemented.

## Note on continuity naming

This project predates the `CVF_SESSION/` naming convention introduced by the
CVF Project Bootstrap Continuity Contract. Its canonical continuity system
lives under `SESSION/`. `CVF_SESSION_MEMORY.md` at the project root is a
pointer file only, and `CVF_SESSION/ACTIVE_SESSION_STATE.json` **does exist**
as a compatibility mirror required by
`scripts/check_cvf_workspace_agent_enforcement.ps1` (which checks that exact
literal path) — see `CVF_SESSION_MEMORY.md` or `AGENTS.md` for the full
explanation. Do not treat `CVF_SESSION/ACTIVE_SESSION_STATE.json` as a second
canonical active-state source; only `SESSION/ACTIVE_SESSION_STATE.json` is
canonical, and `scripts/check_session_state.py` verifies the two stay in
agreement.
