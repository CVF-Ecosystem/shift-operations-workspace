# P4-E Identity Mapping And Conversation Routing Exact Manifest

docType: governed_exact_manifest

Status: READY_FOR_REVIEW

Batch ID: P4E-IDENTITY-CONVERSATION-ROUTING

Dispatch base head: e367bc996e6fceaff08d23af34c2d5d8dada0ded

Commit mode: WORKER_MUST_NOT_COMMIT

## Purpose

This immutable supporting manifest carries the exact 94-path ceiling for the
paired P4-E Work Order. The Work Order controls behavior, evidence, roles,
failure semantics, and authority; this file controls path membership and owner
class. Neither file grants BUILD before independent authorization review.

## Exact Final Changed-Set Ceiling - 94 Paths

The final tranche diff against the worker-captured `executionBaseHead` may
contain exactly the paths below and no others. No path may be deleted or
renamed. A required 95th path stops work and requires an independently reviewed
amendment to both this manifest and the Work Order.

### Settled governance packet - paths 1-14

These paths are read-only to the implementation worker and completion reviewer,
except that an independently authorized amendment may modify paths 13-14.

1. `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md`
2. `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_DESIGN_REVIEW_2026-08-29.md`
3. `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md`
4. `docs/decisions/SPEC_REVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md`
5. `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC_REWORK_2026-09-09.md`
6. `docs/decisions/SPEC_REREVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md`
7. `docs/cvf/invariants/p4e-mapping-action-outcomes.json`
8. `docs/cvf/invariants/p4e-identity-resolution-outcomes.json`
9. `docs/cvf/invariants/p4e-placement-outcomes.json`
10. `docs/specs/p4e_invariant_pins.py`
11. `docs/cvf/invariants/registry.json`
12. `docs/baselines/CVF_GC018_BASELINE_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`
13. `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_2026-09-09.md`
14. `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`

### IMPLEMENTATION_WORKER - paths 15-80

15. `pyproject.toml`
16. `packages/identity-mapping/README.md`
17. `packages/identity-mapping/pyproject.toml`
18. `packages/identity-mapping/src/identity_mapping/__init__.py`
19. `packages/identity-mapping/src/identity_mapping/models.py`
20. `packages/identity-mapping/src/identity_mapping/invariants.py`
21. `packages/identity-mapping/src/identity_mapping/crypto.py`
22. `packages/identity-mapping/src/identity_mapping/ports.py`
23. `packages/identity-mapping/src/identity_mapping/service.py`
24. `packages/identity-mapping/src/identity_mapping/retention.py`
25. `packages/conversation-routing/README.md`
26. `packages/conversation-routing/pyproject.toml`
27. `packages/conversation-routing/src/conversation_routing/__init__.py`
28. `packages/conversation-routing/src/conversation_routing/models.py`
29. `packages/conversation-routing/src/conversation_routing/invariants.py`
30. `packages/conversation-routing/src/conversation_routing/ports.py`
31. `packages/conversation-routing/src/conversation_routing/service.py`
32. `packages/channel-sdk/src/channel_sdk/__init__.py`
33. `packages/channel-sdk/src/channel_sdk/sender_evidence.py`
34. `apps/integration-edge/src/integration_edge/__init__.py`
35. `apps/integration-edge/src/integration_edge/config.py`
36. `apps/integration-edge/src/integration_edge/canonical.py`
37. `apps/integration-edge/src/integration_edge/models.py`
38. `apps/integration-edge/src/integration_edge/verification/hmac.py`
39. `apps/integration-edge/src/integration_edge/verification/sender_keys.py`
40. `apps/integration-edge/src/integration_edge/inbound/service.py`
41. `apps/integration-edge/src/integration_edge/routing/service.py`
42. `apps/integration-edge/src/integration_edge/main.py`
43. `packages/operations-ledger/src/operations_ledger/ledger.py`
44. `packages/operations-ledger/src/operations_ledger/p4e_records.py`
45. `packages/operations-ledger/src/operations_ledger/p4e_tables.py`
46. `packages/operations-ledger/src/operations_ledger/p4e_store.py`
47. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
48. `packages/operations-ledger/src/operations_ledger/tables.py`
49. `database/migrations/011_p4e_identity_conversation_routing.sql`
50. `packages/cvf-runtime/src/cvf_runtime/permission.py`
51. `apps/workspace-api/pyproject.toml`
52. `apps/workspace-api/src/workspace_api/dependencies.py`
53. `apps/workspace-api/src/workspace_api/main.py`
54. `apps/workspace-api/src/workspace_api/external_ingress/__init__.py`
55. `apps/workspace-api/src/workspace_api/external_ingress/models.py`
56. `apps/workspace-api/src/workspace_api/external_ingress/repository.py`
57. `apps/workspace-api/src/workspace_api/external_ingress/service.py`
58. `apps/workspace-api/src/workspace_api/external_ingress/router.py`
59. `apps/workspace-api/src/workspace_api/application/p4e_commands.py`
60. `apps/workspace-api/src/workspace_api/application/p4e_placement.py`
61. `apps/workspace-api/src/workspace_api/api/external_identities/__init__.py`
62. `apps/workspace-api/src/workspace_api/api/external_identities/router.py`
63. `apps/workspace-api/src/workspace_api/api/conversation_routes/__init__.py`
64. `apps/workspace-api/src/workspace_api/api/conversation_routes/router.py`
65. `contracts/identity/external-identity-mapping.schema.json`
66. `contracts/conversation/conversation-placement.schema.json`
67. `tests/unit/test_p4e_invariants.py`
68. `tests/unit/test_p4e_identity_models.py`
69. `tests/unit/test_p4e_identity_service.py`
70. `tests/unit/test_p4e_conversation_routing.py`
71. `tests/unit/test_p4e_sender_key_retirement.py`
72. `tests/security/test_p4e_sender_evidence.py`
73. `tests/security/test_p4e_privacy_disclosure.py`
74. `tests/contract/test_p4e_contract_schemas.py`
75. `tests/integration/test_p4e_backend_parity.py`
76. `tests/integration/test_p4e_workspace_composition.py`
77. `tests/integration/test_p4e_transaction_protocol.py`
78. `tests/integration/test_p4e_postgres_live.py`
79. `tests/unit/test_p4e_dependency_boundary.py`
80. `docs/reviews/CVF_P4E_IDENTITY_CONVERSATION_ROUTING_WORKER_RETURN_2026-09-09.md`

### INDEPENDENT REVIEWER - paths 81-82

81. `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_WORK_ORDER_AUTHORIZATION_REVIEW_2026-09-09.md`
82. `docs/reviews/CVF_P4E_IDENTITY_CONVERSATION_ROUTING_COMPLETION_2026-09-09.md`

### CLOSER and SESSION_SYNC_STEWARD - paths 83-94

83. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
84. `IMPLEMENTATION_STATUS.json`
85. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
86. `SESSION/ACTIVE_SESSION_STATE.json`
87. `SESSION/SESSION_MEMORY.md`
88. `SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC_2026-09-09.md`
89. `docs/INDEX.md`
90. `docs/implementation/EXECUTION_ROADMAP.md`
91. `knowledge/PROJECT_CONTEXT.md`
92. `knowledge/manifest.json`
93. `docs/catalog/MODULE_REGISTRY.json`
94. `docs/catalog/MODULE_CATALOG.md`

## Protected Exclusions

- `packages/conversation-routing/customer-router/README.md` remains unchanged,
  and no new path may be created under its directory.
- `packages/conversation-routing/vessel-router/README.md` remains unchanged,
  and no new path may be created under its directory.
- Any path not numbered above is outside P4-E BUILD authority.

## Claim Boundary

This is path-accounting evidence only. It does not authorize BUILD or assert
that any listed implementation path exists, changes, passes tests, or is ready
for production.
