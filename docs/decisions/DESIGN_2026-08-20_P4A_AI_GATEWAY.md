# DESIGN — P4-A AI Gateway

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Phase: `DESIGN`
- Risk: `R2`
- Parent: `INTAKE_ACCEPTED_FOR_DESIGN`
- Status: `APPROVED_FOR_SPEC`
- Role transition: `INTAKE_AUTHOR → DESIGN_AUTHOR`

## Decision

Implement a pure, provider-neutral library. `AIGateway.execute` is the only
authorized provider-dispatch point. It accepts typed policy/context facts and
an injected `AIProvider`; it does not read application globals or expose a web
endpoint.

The mandatory order is:

1. strict request and output-schema validation;
2. AI-mode, evidence and context-handoff checks;
3. classification/minimization and placement evaluation;
4. `assert_placement_allowed`;
5. reserve estimated tokens/cost in a process-local ledger and call
   `assert_within_budget`;
6. call `assert_not_terminated` for kill switch/preflight state;
7. resolve an explicitly registered provider/model;
8. increment the physical-attempt counter immediately before one provider
   dispatch;
9. enforce timeout and best-effort cancellation;
10. validate returned structured JSON against the exact schema;
11. commit actual usage or release the reservation; emit a sanitized receipt
    or deterministic rules fallback.

Every negative pre-call outcome returns zero provider attempts. Post-dispatch
failures preserve one attempt and never retry in this tranche.

## Data and evidence design

- PUBLIC typed canary context may reach the external provider after all gates.
- INTERNAL reaches an external provider only with explicit, independently
  verifiable minimization evidence. P4-A1's current handoff lacks that proof
  and must fail closed.
- CONFIDENTIAL/RESTRICTED cannot reach the public canary endpoint.
- The usage ledger is real process-scoped state with atomic
  reserve/commit/release semantics, but is not durable or production-grade.
- Receipts contain request/evidence/schema/output digests, safe provider/model
  identifiers, safe endpoint origin, gate outcomes, reservation/usage facts,
  timestamps, termination facts, and physical attempt count. They contain no
  prompt/context/output body, authorization header, key, or raw error that may
  echo secrets.

## Alternatives rejected

- Wiring the gateway into `workspace-api` would widen this tranche into an
  application surface and is deferred.
- Adding a production Alibaba adapter would prematurely close P4-B.
- Treating P4-A1 INTERNAL content as PUBLIC or minimized would falsify its
  reviewed contract.
- A fake provider cannot satisfy the mandatory governance proof.
- Durable usage/audit persistence is deferred because it requires a separate
  storage and failure-recovery contract.

## BUILD path ceiling

The worker may create or modify only the following 40 paths:

1. `packages/ai-gateway/pyproject.toml`
2. `packages/ai-gateway/contracts/provider_interface.py`
3. `packages/ai-gateway/contracts/ai_gateway.schema.json`
4. `packages/ai-gateway/src/ai_gateway/__init__.py`
5. `packages/ai-gateway/src/ai_gateway/errors.py`
6. `packages/ai-gateway/src/ai_gateway/models.py`
7. `packages/ai-gateway/src/ai_gateway/provider.py`
8. `packages/ai-gateway/src/ai_gateway/registry.py`
9. `packages/ai-gateway/src/ai_gateway/usage.py`
10. `packages/ai-gateway/src/ai_gateway/context.py`
11. `packages/ai-gateway/src/ai_gateway/validation.py`
12. `packages/ai-gateway/src/ai_gateway/fallback.py`
13. `packages/ai-gateway/src/ai_gateway/service.py`
14. `pyproject.toml`
15. `tests/unit/test_p4a_gateway_models.py`
16. `tests/unit/test_p4a_gateway_registry.py`
17. `tests/unit/test_p4a_gateway_usage.py`
18. `tests/unit/test_p4a_gateway_context.py`
19. `tests/unit/test_p4a_gateway_validation.py`
20. `tests/unit/test_p4a_gateway_receipts.py`
21. `tests/unit/test_p4a_gateway_dependency_boundaries.py`
22. `tests/contract/test_p4a_ai_gateway_schema.py`
23. `tests/integration/test_p4a_gateway_live_evidence_support.py`
24. `scripts/_p4a_gateway_live_evidence_support.py`
25. `scripts/run_p4a_gateway_live_evidence.py`
26. `docs/decisions/P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md`
27. `docs/cvf/CVF_CONTROL_MAPPING.md`
28. `docs/cvf/PROVIDER_GOVERNANCE.md`
29. `docs/implementation/EXECUTION_ROADMAP.md`
30. `IMPLEMENTATION_STATUS.json`
31. `docs/catalog/MODULE_REGISTRY.json`
32. `docs/catalog/MODULE_CATALOG.md`
33. `knowledge/PROJECT_CONTEXT.md`
34. `knowledge/manifest.json`
35. `SESSION/ACTIVE_SESSION_STATE.json`
36. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
37. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
38. `SESSION/SESSION_MEMORY.md`
39. `SESSION/handoffs/P4A_AI_GATEWAY_2026-08-20.md`
40. `docs/decisions/P4A_AI_GATEWAY_WORKER_RETURN_2026-08-20.md`

The separate `REVIEWER` alone may create the 41st and final review path:
`docs/decisions/P4A_AI_GATEWAY_COMPLETION_REVIEW_2026-08-20.md`.

## Rollback

All BUILD changes are ordinary tracked-file edits. On failed gates, leave the
worktree and evidence intact for review/repair; do not delete, reset, restore,
commit, or push. The live call cannot be undone, so its single physical attempt
must remain recorded even when the response is unusable.

## Design disposition

The design authorizes SPEC/WORK_ORDER authoring only. BUILD starts only after
the authorization review records `AUTHORIZATION_REVIEW_PASS`.
