# Work Order — P4-A3 Application Memory

- Tranche: `P4A3-APPLICATION-MEMORY-2026-08-21`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Execution base: `422661f`
- Worker role: separate `IMPLEMENTATION_WORKER`
- Status: `AUTHORIZED_FOR_EXTERNAL_IMPLEMENTATION_WORKER`
- Provider/network/install/database/commit/push/deployment: `NONE`

## Objective

Implement SPEC v1.0 session/working application memory: strict immutable
contracts, deterministic policy, process-local atomic append-only store,
correction/tombstone lifecycle, use-time scope/TTL/source revalidation,
sanitized receipts and one no-route application composition.

## Exact 50-path ceiling

The worker may change only these paths; the first 16 are pre-existing
authorization/continuity records and are read-only to the worker except the
active handoff acknowledgment and final worker-return amendment.

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
2. `IMPLEMENTATION_STATUS.json`
3. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
4. `SESSION/ACTIVE_SESSION_STATE.json`
5. `SESSION/SESSION_MEMORY.md`
6. `SESSION/handoffs/P4A3_APPLICATION_MEMORY_2026-08-21.md`
7. `docs/decisions/INTAKE_2026-08-21_P4A3_APPLICATION_MEMORY.md`
8. `docs/decisions/P4A3_APPLICATION_MEMORY_INTAKE_REVIEW_2026-08-21.md`
9. `docs/decisions/DESIGN_2026-08-21_P4A3_APPLICATION_MEMORY.md`
10. `docs/decisions/P4A3_APPLICATION_MEMORY_DESIGN_REVIEW_2026-08-21.md`
11. `docs/specs/P4A3_APPLICATION_MEMORY_SPEC.md`
12. `docs/work_orders/P4A3_APPLICATION_MEMORY_WORK_ORDER.md`
13. `docs/decisions/P4A3_APPLICATION_MEMORY_AUTHORIZATION_REVIEW_2026-08-21.md`
14. `docs/implementation/EXECUTION_ROADMAP.md`
15. `knowledge/PROJECT_CONTEXT.md`
16. `knowledge/manifest.json`
17. `pyproject.toml`
18. `packages/application-memory/README.md`
19. `packages/application-memory/pyproject.toml`
20. `packages/application-memory/contracts/application_memory.schema.json`
21. `packages/application-memory/src/application_memory/__init__.py`
22. `packages/application-memory/src/application_memory/errors.py`
23. `packages/application-memory/src/application_memory/models.py`
24. `packages/application-memory/src/application_memory/hashing.py`
25. `packages/application-memory/src/application_memory/policy.py`
26. `packages/application-memory/src/application_memory/store.py`
27. `packages/application-memory/src/application_memory/receipts.py`
28. `packages/application-memory/src/application_memory/service.py`
29. `apps/workspace-api/src/workspace_api/application/application_memory.py`
30. `scripts/_p4a3_application_memory_live_evidence_support.py`
31. `scripts/run_p4a3_application_memory_live_evidence.py`
32. `tests/unit/test_p4a3_memory_models.py`
33. `tests/unit/test_p4a3_memory_hashing.py`
34. `tests/unit/test_p4a3_memory_policy.py`
35. `tests/unit/test_p4a3_memory_store.py`
36. `tests/unit/test_p4a3_memory_receipts.py`
37. `tests/unit/test_p4a3_memory_service.py`
38. `tests/unit/test_p4a3_memory_dependency_boundaries.py`
39. `tests/contract/test_p4a3_application_memory_schema.py`
40. `tests/integration/test_p4a3_memory_application_composition.py`
41. `tests/integration/test_p4a3_memory_live_evidence_support.py`
42. `tests/cvf/test_p4a3_memory_governance_boundaries.py`
43. `tests/unit/test_operations_domain_boundary.py`
44. `docs/catalog/MODULE_REGISTRY.json`
45. `docs/catalog/MODULE_CATALOG.md`
46. `docs/cvf/CVF_CONTROL_MAPPING.md`
47. `docs/cvf/CONTEXT_CONTROL.md`
48. `docs/cvf/PROVIDER_GOVERNANCE.md`
49. `docs/INDEX.md`
50. `docs/decisions/P4A3_APPLICATION_MEMORY_WORKER_RETURN_2026-08-21.md`

Only independent `REVIEW_PASS` may add path 51:
`docs/decisions/P4A3_APPLICATION_MEMORY_COMPLETION_REVIEW_2026-08-21.md`.

## Build rules

- Declare `IMPLEMENTATION_WORKER` and acknowledge this Work Order in the
  handoff before editing.
- Implement only SPEC R1-R12; do not weaken parent P4-A/P4-A1/P4-A2 gates.
- Use stable Python 3.13.12/Pydantic 2.10.6 runtime; install nothing.
- No provider runner execution. Live scripts are mechanically tested only.
- Do not add database tables, migrations, routes, environment reads or SDKs.
- Keep files under repository size limits; regenerate catalog only when source
  metrics/status change and refresh only affected knowledge pins.

## Required evidence

Focused P4-A3 tests; affected P3-C/P4-A1/P4-A2 regressions; full suite;
adversarial scope/TTL/source/alias/concurrency/hash probes; catalog/session/
knowledge/file-size/repository/changed-JSON/diff/staged/exact-path/secret-scan
and workspace doctor. Every refusal write proves zero state mutation and every
pre-dispatch refusal proves zero gateway/provider attempts.

## Stop conditions

Stop on any path outside 50, requirement change, durable persistence, public
route, RESTRICTED/production data, provider/network use, secret need, install,
database, destructive action, commit/push/deployment, third repair round
without new operator amendment, or inability to keep source truth coherent.

## Return

Amend path 50 with exact commands/results and return `READY_FOR_REVIEW` or a
precise blocker. Do not self-review, create path 51, declare FREEZE or commit.
