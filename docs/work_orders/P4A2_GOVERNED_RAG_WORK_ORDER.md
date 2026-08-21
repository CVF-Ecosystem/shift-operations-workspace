# Work Order — P4-A2 Governed RAG

- Tranche: `P4A2-GOVERNED-RAG-2026-08-21`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Status: `AUTHORIZED_FOR_EXTERNAL_WORKER_BUILD`
- Execution base: `4016fc6708844ecea1dedc4e76dfccf2ae314c9e`
- Parent/role ancestry: `ORCHESTRATOR → INTAKE_AUTHOR → REVIEWER →
  ORCHESTRATOR → DESIGN_AUTHOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR → REVIEWER`
- Authorization disposition: `AUTHORIZATION_REVIEW_PASS`
- Commit/push/deployment authority: `NONE/NONE/NONE`

## Assignment

The receiving agent must declare `IMPLEMENTATION_WORKER`, run mandatory
rehydration, acknowledge this Work Order in the active handoff, and implement
only SPEC R1–R24. The worker must not act as reviewer, create the completion
review, commit, push, deploy, install packages, widen the reference plan or
modify the immutable authorization artifacts.

The current orchestrator retains independent REVIEW/CLOSER responsibility.

## BUILD sequence

1. Confirm HEAD still equals the execution base and the worktree contains
   exactly the pre-existing authorization packet listed below, with staged set
   empty. Do not require or create a packet commit.
2. Rehydrate continuity, verify Core/manifest/binding at
   `7d9f360a3df11ac998972728000785799399c02b`, and run the workspace doctor.
3. Implement strict `governed-rag` contracts and deterministic semantic,
   index, injection, minimization, context, validation and receipt modules.
4. Implement the single no-route application composition function that calls
   P4-A1 and then P4-A2 with an injected real `AIGateway` object.
5. Add adversarial unit/contract/integration/CVF tests. Fakes are mechanics
   only and must be labeled non-proof.
6. Run focused P4-A2 plus P4-A1/P4-A parent suites and all non-consuming
   repository gates. Stop before credential access if any fails.
7. Run the live evidence script once: representative negative paths first with
   zero physical calls, then one admitted harmless Project Knowledge path
   through the full application composition and exactly one HTTPS POST.
8. Update bounded truth surfaces, regenerate catalog, synchronize continuity,
   write the worker return and rerun every non-consuming gate.
9. Verify the exact resulting changed set, staged zero and secret scan, then
   stop with `READY_FOR_REVIEW` or a named blocked disposition.

## Immutable authorization packet

These 16 paths already differ from the execution base. They are reviewer/
orchestrator-owned evidence. The worker must preserve their entry-state bytes,
except for the nine continuity/truth paths also explicitly included in the
worker ceiling below:

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
2. `IMPLEMENTATION_STATUS.json`
3. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
4. `SESSION/ACTIVE_SESSION_STATE.json`
5. `SESSION/SESSION_MEMORY.md`
6. `docs/implementation/EXECUTION_ROADMAP.md`
7. `docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md`
8. `knowledge/PROJECT_CONTEXT.md`
9. `knowledge/manifest.json`
10. `SESSION/handoffs/P4A2_GOVERNED_RAG_2026-08-21.md`
11. `docs/decisions/INTAKE_2026-08-21_P4A2_GOVERNED_RAG.md`
12. `docs/decisions/P4A2_GOVERNED_RAG_INTAKE_REVIEW_2026-08-21.md`
13. `docs/decisions/DESIGN_2026-08-21_P4A2_GOVERNED_RAG.md`
14. `docs/specs/P4A2_GOVERNED_RAG_SPEC.md`
15. `docs/work_orders/P4A2_GOVERNED_RAG_WORK_ORDER.md`
16. `docs/decisions/P4A2_GOVERNED_RAG_AUTHORIZATION_REVIEW_2026-08-21.md`

Paths 7 and 11–16 are fully immutable during BUILD. Any required correction
to them stops work for reviewer-owned amendment. Paths 1–6 and 8–10 may change
only for truthful BUILD synchronization because they also occur below.

## Exact worker write ceiling

The worker may create or modify only these 50 paths:

1. `packages/governed-rag/pyproject.toml`
2. `packages/governed-rag/README.md`
3. `packages/governed-rag/contracts/governed_rag.schema.json`
4. `packages/governed-rag/src/governed_rag/__init__.py`
5. `packages/governed-rag/src/governed_rag/errors.py`
6. `packages/governed-rag/src/governed_rag/models.py`
7. `packages/governed-rag/src/governed_rag/hashing.py`
8. `packages/governed-rag/src/governed_rag/semantic.py`
9. `packages/governed-rag/src/governed_rag/index.py`
10. `packages/governed-rag/src/governed_rag/injection.py`
11. `packages/governed-rag/src/governed_rag/minimization.py`
12. `packages/governed-rag/src/governed_rag/context.py`
13. `packages/governed-rag/src/governed_rag/validation.py`
14. `packages/governed-rag/src/governed_rag/receipts.py`
15. `packages/governed-rag/src/governed_rag/service.py`
16. `pyproject.toml`
17. `apps/workspace-api/src/workspace_api/application/governed_rag.py`
18. `tests/unit/_p4a2_rag_fixtures.py`
19. `tests/unit/test_p4a2_rag_models.py`
20. `tests/unit/test_p4a2_rag_hashing.py`
21. `tests/unit/test_p4a2_rag_semantic.py`
22. `tests/unit/test_p4a2_rag_index.py`
23. `tests/unit/test_p4a2_rag_injection.py`
24. `tests/unit/test_p4a2_rag_minimization.py`
25. `tests/unit/test_p4a2_rag_context.py`
26. `tests/unit/test_p4a2_rag_validation.py`
27. `tests/unit/test_p4a2_rag_receipts.py`
28. `tests/unit/test_p4a2_rag_service.py`
29. `tests/unit/test_p4a2_rag_dependency_boundaries.py`
30. `tests/contract/test_p4a2_governed_rag_schema.py`
31. `tests/integration/test_p4a2_rag_application_composition.py`
32. `tests/cvf/test_p4a2_rag_governance_boundaries.py`
33. `tests/integration/test_p4a2_rag_live_evidence_support.py`
34. `scripts/_p4a2_governed_rag_live_evidence_support.py`
35. `scripts/run_p4a2_governed_rag_live_evidence.py`
36. `docs/decisions/P4A2_GOVERNED_RAG_LIVE_EVIDENCE_RECEIPT.md`
37. `docs/decisions/P4A2_GOVERNED_RAG_WORKER_RETURN_2026-08-21.md`
38. `docs/cvf/CVF_CONTROL_MAPPING.md`
39. `docs/cvf/PROVIDER_GOVERNANCE.md`
40. `docs/implementation/EXECUTION_ROADMAP.md`
41. `IMPLEMENTATION_STATUS.json`
42. `docs/catalog/MODULE_REGISTRY.json`
43. `docs/catalog/MODULE_CATALOG.md`
44. `knowledge/PROJECT_CONTEXT.md`
45. `knowledge/manifest.json`
46. `SESSION/ACTIVE_SESSION_STATE.json`
47. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
48. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
49. `SESSION/SESSION_MEMORY.md`
50. `SESSION/handoffs/P4A2_GOVERNED_RAG_2026-08-21.md`

The union of the 16-path authorization packet and the 50 worker paths
is exactly 57 unique status paths at worker return. The reviewer alone may add
the 58th path:
`docs/decisions/P4A2_GOVERNED_RAG_COMPLETION_REVIEW_2026-08-21.md`.

## Live-evidence authority

The only authorized external effect is one HTTPS POST made through the
existing P4-A `AIGateway.execute` path to the configured, already-approved
Alibaba DashScope OpenAI-compatible endpoint. Model selection uses the local
committed quota/catalog mechanism. No embedding/reranking call, health check,
telemetry, retry, fallback provider call, product API, Git network operation,
package install or second provider request is permitted.

Before that call, the runner must prove at minimum:

- P4-A1 negative/no-evidence short-circuit;
- forged/mismatched positive evidence rejection;
- stale/partial index rejection;
- all-evidence injection omission;
- failed minimization/external placement rejection;
- context budget or termination rejection;

with zero physical provider attempts. The admitted call uses an isolated
synthetic Project Knowledge fixture containing no operational/customer data,
secret or real identifier. It must pass verified P4-A1 authorization, P4-A2
hybrid/index/injection/minimization/context construction, all P4-A gates, one
provider response, strict schema and citation-membership validation.

Any provider-side failure, invalid citation, timeout or unusable response is
retained as `LIVE_EVIDENCE_BLOCKED`. Do not retry. A replacement call requires
reviewer-owned amendment and operator authority.

## Required test and verification set

Run all P4-A2 test paths 18–33, then all existing P4-A1 and P4-A focused tests,
then `python -m pytest -q`. Run every command in SPEC and capture command,
interpreter/version, exit code and concise output. The live runner is last
among consuming checks and runs once only after all non-consuming gates pass.

Secret scan must cover the complete diff and every new receipt/return. It must
fail on credential-like values, authorization headers, environment values,
raw prompt/evidence/output bodies and URL userinfo.

## Stop and repair rules

Stop on execution-base drift, an unexpected pre-existing path, immutable
packet drift, path 58 before reviewer action, any unlisted path, secret
exposure, file-size breach, failed parent suite, stale catalog/knowledge pin,
continuity drift, pre-call physical attempt, call count other than exactly one
after admitted dispatch, or need for new dependency/database/provider/network/
deployment authority.

Repairs within the same objective, acceptance contract, external-effect class
and exact path ceiling remain authorized. At repair round three without an
independent new root cause, record `REVIEW_COST_ESCALATION_REQUIRED` and stop.
Never reset, delete or overwrite retained evidence.

## Worker return contract

The worker return must contain:

- execution base, authorization-packet verification and final status paths;
- R1–R24 evidence, including source-level dependency and object-identity proof;
- focused/parent/full/gate commands with interpreter, versions and exit codes;
- zero-call cases and the single live call's safe transition/count/status;
- safe endpoint origin/model, receipt hashes and secret-scan result;
- exact 57-path comparison and staged-zero proof;
- all repairs, deviations and residual limitations;
- `READY_FOR_REVIEW`, `LIVE_EVIDENCE_BLOCKED` or another precise blocker.

## REVIEW and commit boundary

The independent `REVIEWER` reruns every non-consuming check, inspects the one
retained live receipt without another call, verifies exact source/order/hash/
citation/zero-call behavior and returns `REVIEW_PASS`,
`REVIEW_CHANGES_REQUIRED` or `REVIEW_BLOCKED`. Only REVIEW_PASS permits the
reviewer-owned completion path and later FREEZE/commit stewardship. Commit,
push and deployment are not authorized by this Work Order.
