# Work Order — P4-B AI Provider Foundation

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Execution base: `319c6a8`
- Worker role: separate `IMPLEMENTATION_WORKER`
- Status: `AUTHORIZED_FOR_EXTERNAL_IMPLEMENTATION_WORKER`
- Provider/network/install/database/commit/push/deployment: `NONE`

## Objective

Implement SPEC v1.0: a strict provider-mode service with zero-call `NO_AI`,
deterministic schema-validated `RULES_ONLY`, default-denied test-only mock,
registry-owned metadata, sanitized receipts, and exactly-one delegation of an
admitted `EXTERNAL_AI` request to injected P4-A `AIGateway`.

## Exact 50-path ceiling

The worker may change only these paths. Paths 1-16 are the authorization and
continuity packet and are read-only to the worker except the active-handoff
acknowledgment. Path 50 is the worker-owned return.

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
2. `IMPLEMENTATION_STATUS.json`
3. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
4. `SESSION/ACTIVE_SESSION_STATE.json`
5. `SESSION/SESSION_MEMORY.md`
6. `SESSION/handoffs/P4B_AI_PROVIDERS_2026-08-21.md`
7. `docs/decisions/INTAKE_2026-08-21_P4B_AI_PROVIDERS.md`
8. `docs/decisions/P4B_AI_PROVIDERS_INTAKE_REVIEW_2026-08-21.md`
9. `docs/decisions/DESIGN_2026-08-21_P4B_AI_PROVIDERS.md`
10. `docs/decisions/P4B_AI_PROVIDERS_DESIGN_REVIEW_2026-08-21.md`
11. `docs/specs/P4B_AI_PROVIDERS_SPEC.md`
12. `docs/work_orders/P4B_AI_PROVIDERS_WORK_ORDER.md`
13. `docs/decisions/P4B_AI_PROVIDERS_AUTHORIZATION_REVIEW_2026-08-21.md`
14. `docs/implementation/EXECUTION_ROADMAP.md`
15. `knowledge/PROJECT_CONTEXT.md`
16. `knowledge/manifest.json`
17. `pyproject.toml`
18. `packages/ai-providers/README.md`
19. `packages/ai-providers/pyproject.toml`
20. `packages/ai-providers/contracts/provider_modes.schema.json`
21. `packages/ai-providers/src/ai_providers/__init__.py`
22. `packages/ai-providers/src/ai_providers/errors.py`
23. `packages/ai-providers/src/ai_providers/models.py`
24. `packages/ai-providers/src/ai_providers/protocols.py`
25. `packages/ai-providers/src/ai_providers/no_ai.py`
26. `packages/ai-providers/src/ai_providers/rules_only.py`
27. `packages/ai-providers/src/ai_providers/mock_provider.py`
28. `packages/ai-providers/src/ai_providers/registry.py`
29. `packages/ai-providers/src/ai_providers/service.py`
30. `apps/workspace-api/src/workspace_api/application/ai_provider_modes.py`
31. `scripts/_p4b_ai_providers_live_evidence_support.py`
32. `scripts/run_p4b_ai_providers_live_evidence.py`
33. `tests/unit/test_p4b_provider_models.py`
34. `tests/unit/test_p4b_no_ai.py`
35. `tests/unit/test_p4b_rules_only.py`
36. `tests/unit/test_p4b_mock_provider.py`
37. `tests/unit/test_p4b_provider_registry.py`
38. `tests/unit/test_p4b_provider_service.py`
39. `tests/unit/test_p4b_provider_dependency_boundaries.py`
40. `tests/contract/test_p4b_provider_modes_schema.py`
41. `tests/integration/test_p4b_provider_application_composition.py`
42. `tests/integration/test_p4b_provider_live_evidence_support.py`
43. `tests/cvf/test_p4b_provider_governance_boundaries.py`
44. `docs/catalog/MODULE_REGISTRY.json`
45. `docs/catalog/MODULE_CATALOG.md`
46. `docs/cvf/CVF_CONTROL_MAPPING.md`
47. `docs/cvf/PROVIDER_GOVERNANCE.md`
48. `docs/INDEX.md`
49. `tests/unit/test_operations_domain_boundary.py`
50. `docs/decisions/P4B_AI_PROVIDERS_WORKER_RETURN_2026-08-21.md`

Only an independent reviewer may add path 51:
`docs/decisions/P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md`.

## Build rules

- Declare `IMPLEMENTATION_WORKER`, rehydrate continuity and acknowledge this
  Work Order in the active handoff before editing.
- Implement only SPEC R1-R12; do not weaken or duplicate P4-A types, gates,
  registry placement binding, output validation, usage ledger or receipts.
- Use stable Python 3.13.12/Pydantic 2.10.6; install nothing.
- Do not execute the live runner. Its tests use spies/fakes only and must prove
  that mock output is labeled evidence-ineligible.
- Add no HTTP client, SDK, environment/secret read, database, route, retry,
  background task or deployment configuration.
- Keep files below repository limits. Regenerate catalog only after source
  changes and refresh only source pins actually affected.

## Required evidence

Focused P4-B tests; affected P4-A/P4-A2/P4-A3 regressions; full suite;
adversarial primitive-reconstruction, duplicate/ambiguous rule, JSON-bound,
aliasing, mock-relabel, external-identity and receipt-hash probes; catalog,
session, knowledge, file-size, repository, changed-JSON, diff, staged,
exact-path, secret scan and workspace doctor. BUILD call/install/database/
commit/push/deployment counters must remain zero.

## Stop conditions

Stop on any path outside 50, contract/objective/risk change, live/provider or
network use, credential/environment need, install, database, route, durable
state, retry, deployment, destructive action, commit/push, third repair round
without a new root cause and amendment, or inability to keep gates coherent.

## Return

Write path 50 with exact commands/results and return `READY_FOR_REVIEW` or a
precise blocker. Do not self-review, create path 51, claim live governance
proof, declare FREEZE, commit or push.

## Amendment 1 — repair round 3 (operator-authorized 2026-08-22)

### Authority

After independent rereview round 2 returned
`REVIEW_COST_ESCALATION_REQUIRED`, the operator explicitly authorized one
bounded repair round 3 for only `P4B-REV-F4-R2`, `P4B-REV-F5-R2` and
`P4B-REV-F6-R2`. This Amendment is recorded in the existing Work Order path;
it creates no path 52 and does not authorize a live call.

### Scope and ceiling

- The changed-set ceiling remains the exact paths 1-50 above.
- Path 51, `docs/decisions/P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md`,
  remains reviewer-owned and read-only to the worker.
- No path 52 or other path may be created or changed.
- Source/test/document/continuity edits inside paths 1-50 are permitted only
  when directly necessary to close the three named findings and return a
  coherent worker handoff.
- Provider/network call, real or synthetic credential use, install, database,
  commit, push and deployment remain prohibited. Tests must use injected
  fakes/spies and may not read a real credential or execute the consuming
  runner branch.

### Complete repair contract

`P4B-REV-F4-R2`:

- `ProviderAdapterRegistry.register` must normalize invalid untrusted input
  to the documented typed registration error without partial mutation.
- Cover primitive mapping, arbitrary object, `model_construct` bypass and
  valid model inputs. Do not expose raw `AttributeError`/`TypeError`.

`P4B-REV-F5-R2`:

- Implement one complete emitted-shape matrix in Pydantic and Draft 2020-12
  schema, not another list of probe-specific exceptions.
- Every external outcome has zero rule counters and no rule/ruleset facts.
- Non-accepted external outcomes carry no output digest.
- Every rules outcome carries the actual ruleset digest; matched/schema-
  invalid outcomes carry the applicable rule id and positive evaluated count.
- Identity-mismatch provider/model facts are both present or both absent.
- Accepted external provider/model/output facts and gateway/provider attempt
  counters are exact; disabled/invalid invariants remain exact.
- Add a paired negative matrix for all impossible shapes and positive tests
  generated from every real service-emitted terminal shape.

`P4B-REV-F6-R2`:

- Compute every evidence invariant before choosing receipt disposition.
- `LIVE_EVIDENCE_PASS` requires accepted outcome, clean secret scan and exact
  physical/adapter/gateway/receipt counters. Any failed invariant must result
  only in `LIVE_EVIDENCE_BLOCKED`; it must never leave a PASS-labeled receipt.
- Add injected fake-transport success, counter-drift and secret-hit tests.
  Tests must not execute network, consume/read a real credential, or write a
  tracked live receipt.

### Evidence and stop condition

Run the exact adversarial probes, focused P4-B suite, affected P4-A/A2/A3
regressions, full suite, catalog/session/knowledge/file-size/repository/JSON/
diff/exact-path/staged/secret gates and workspace doctor. Stop immediately on
scope/path/external-effect drift. The worker must update path 50 and stop at
`READY_FOR_REREVIEW_ROUND_3`; it must not self-review, edit path 51, declare
FREEZE, request or execute the post-review live call, commit or push.

## Amendment 2 — repair round 4 (operator-authorized 2026-08-22)

### Authority

After independent rereview round 3 returned
`REVIEW_COST_ESCALATION_REQUIRED` for the single residual
`P4B-REV-F5-R3`, the operator explicitly authorized one bounded repair round
4 for only that finding. This Amendment is recorded in the existing Work
Order path; it creates no path 52 and does not authorize a live call.

### Scope and ceiling

- The worker changed-set ceiling remains the exact paths 1-50 above.
- Path 51, `docs/decisions/P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md`,
  remains reviewer-owned and read-only to the worker.
- No path 52 or other path may be created or changed.
- Edits inside paths 1-50 are permitted only when directly necessary to close
  `P4B-REV-F5-R3`, add its paired tests, and return coherent continuity.
- Provider/network call, credential use, install, database, commit, push and
  deployment remain prohibited.

### Complete repair contract

- In the general Pydantic receipt grammar, `EXTERNAL_ACCEPTED` must require
  `provider_attempts == 1`.
- In the published Draft 2020-12 JSON Schema, `EXTERNAL_ACCEPTED` must require
  `provider_attempts == 1` with equivalent semantics.
- Add paired negative Pydantic/schema tests proving an otherwise-valid
  `EXTERNAL_ACCEPTED` receipt with `provider_attempts=0` is rejected.
- Retain positive coverage for the real service-emitted accepted receipt.
- Do not tighten `EXTERNAL_NOT_ACCEPTED`: its provider-attempt count may remain
  zero or one depending on where P4-A refused.

### Evidence and stop condition

Run the exact F5-R3 adversarial probes, focused P4-B suite, affected P4-A/A2/A3
regressions, full suite, catalog/session/knowledge/file-size/repository/JSON/
diff/exact-path/staged/secret gates and workspace doctor. Stop immediately on
scope/path/external-effect drift. Update path 50 and stop at
`READY_FOR_REREVIEW_ROUND_4`; do not self-review, edit path 51, create path 52,
declare FREEZE, request or execute the post-review live call, commit or push.
