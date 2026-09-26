# Module Catalog

Machine-readable source: `docs/catalog/MODULE_REGISTRY.json`

Status: GOVERNED

## Metrics

- Total modules: 26
- Enforced: 2
- Partial: 14
- Contract-only: 5
- Stub: 5
- Deprecated: 0

| id | status | path | evidence | description |
|---|---|---|---|---|
| ai-gateway | PARTIAL | `packages/ai-gateway` | tests/unit/test_p4a_gateway_models.py | Provider-neutral governed dispatch: AIGateway.execute calls data_scope, cost and termination gates before exactly one provider request; strict contracts, explicit registry, process-local usage reservations, structured-output validation, rules fallback and sanitized receipts. |
| ai-providers | PARTIAL | `packages/ai-providers` | tests/unit/test_alibaba_model_selector.py | P4-B provider-mode foundation (packages/ai-providers/src/ai_providers): ProviderModeService.execute is the sole mode-selection entry point for zero-call NO_AI, deterministic local RULES_ONLY, a default-denied evidence-ineligible MockProviderAdapter, ProviderAdapterRegistry-owned metadata, and EXTERNAL_AI delegation at most once to an injected P4-A AIGateway. Also retains the pre-existing non-secret Alibaba free-quota model catalog and deterministic expiry/quota-aware selector for governed live evidence runs. |
| application-memory | PARTIAL | `packages/application-memory` | tests/unit/test_p4a3_memory_models.py | Pure P4-A3 session/working application memory: strict immutable contracts, deterministic SESSION/WORKING layer policy, a process-local append-only store with correction/tombstone lineage, use-time scope/TTL/source revalidation and sanitized receipts. |
| channel-adapters | PARTIAL | `packages/channel-adapters` | tests/unit/test_p4d_generic_webhook.py | Digest-only generic outbound webhook adapter plus deterministic provider-neutral conformance mocks. |
| channel-sdk | CONTRACT_ONLY | `packages/channel-sdk` | tests/unit/test_p4c_service_assertion.py | Provider-neutral closed contracts for service assertions, attachment scanning and digest-only outbound adapter delivery. |
| conversation-routing | STUB | `packages/conversation-routing` | packages/conversation-routing/customer-router/README.md | Route messages to workspace, shift, vessel, customer, incident, or fallback. |
| cvf-application-profile | CONTRACT_ONLY | `packages/cvf-application-profile` | tests/contract/test_contract_files.py | Declarative CVF profile for this application: risk classes, approval, evidence, domain lock, data, cost, refusal, termination, freeze policies. Does not copy CVF core. |
| cvf-bridge | CONTRACT_ONLY | `packages/cvf-bridge` | packages/cvf-bridge/policy-evaluation/policy_contract.yaml | Bridge to CVF policy evaluation, approval gates, refusal, evidence, audit and fallback. |
| cvf-runtime | ENFORCED | `packages/cvf-runtime` | tests/cvf/test_gates_unit.py | Runtime enforcement of the CVF application profile: reads the profile YAML and exposes all 12 required_controls as callable gates. |
| governed-rag | PARTIAL | `packages/governed-rag` | tests/unit/test_p4a2_rag_models.py | Pure P4-A2 bounded application-layer governed-RAG composition: consumes only P4-A1's positive EvidenceAvailableV1, builds/validates a deterministic ephemeral hybrid (lexical+semantic) index, screens prompt injection, applies extractive minimization, assembles an instruction/data-separated context, and dispatches the injected P4-A AIGateway at most once with strict answer/citation-membership validation and a sanitized receipt. |
| governed-retrieval | PARTIAL | `packages/governed-retrieval` | tests/unit/test_p4a1_retrieval_models.py | Pure P4-A1 request, corpus, lexical ranking, evidence projection, receipt and result contracts consumed by the workspace application composition. |
| identity-mapping | STUB | `packages/identity-mapping` | packages/identity-mapping/audit/README.md | Map external identities to internal users/customer contacts with human confirmation. |
| integration-edge | PARTIAL | `apps/integration-edge` | tests/security/test_hmac.py | Provider-neutral Integration Edge for authenticated encrypted ingress evidence, quarantine/proposals, signed internal ports, bounded outbound receipts, and digest-only generic-webhook composition. |
| notification-engine | STUB | `packages/notification-engine` | packages/notification-engine/channel-outbound/README.md | In-app, push, email, SMS, outbound channels and escalation. |
| operate-shift-workspace | CONTRACT_ONLY | `skills/operate-shift-workspace` | tests/unit/test_project_operations_skill_contract.py | Provider-neutral navigation over current project continuity, phase/role routing, exact-path work orders, evidence review and bounded closure. |
| operations-domain | PARTIAL | `packages/operations-domain` | tests/unit/test_operations_domain_boundary.py | Domain language and invariants for shift, message, event, task, customer request, incident, handover, report, approval, correction, audit. |
| operations-ledger | ENFORCED | `packages/operations-ledger` | tests/cvf/test_ledger_protocol.py | Source-of-truth persistence. Defines the Ledger Protocol and an append-only, dual-backend SqlLedger (SQLAlchemy Core over the existing migration schema; generic Uuid/JSON types work against SQLite or PostgreSQL from the same table definitions). InMemoryLedger (in workspace-api) is the offline/test backend. |
| project-knowledge-pack | PARTIAL | `knowledge` | tests/unit/test_project_knowledge_pack.py | Repository-owned INTERNAL advisory knowledge pack for current project context, operations terminology and governance boundaries. |
| refinery-bridge | PARTIAL | `packages/refinery-bridge` | tests/unit/test_refinery_models.py | Boundary to CVF Refinery: normalize, terminology, dedupe, redact, classify, conflict detection, context candidates. |
| reporting-engine | STUB | `packages/reporting-engine` | packages/reporting-engine/customer-report/README.md | Build report drafts from confirmed records, validate evidence, export PDF/Excel. |
| retrieval-contracts | PARTIAL | `packages/retrieval-contracts` | tests/unit/test_p3c_retrieval_contract_models.py | Pure deterministic P3-C contract binding admitted P3-A candidates to source, scope, lifecycle, retention, provenance and use-time revalidation evidence. |
| shared-kernel | STUB | `packages/shared-kernel` | packages/shared-kernel/errors/README.md | Identifiers, time, errors, result, validation, observability and security primitives. |
| workspace-api | PARTIAL | `apps/workspace-api` | apps/workspace-api/src/workspace_api/tests/test_lifecycle.py | FastAPI backend for authenticated operational workflows across shifts, internal messages, events, corrections, tasks, customer requests, incidents, handovers and approvals. Each implemented action uses the applicable cvf-runtime identity/permission/audit and domain-specific risk/evidence/approval/domain_lock gates. "Golden vertical" is avoided here per the 2026-07-22 Codex review: durability and end-to-end scope remain action-, backend- and risk-specific; see docs/cvf/CVF_CONTROL_MAPPING.md. |
| workspace-contracts | CONTRACT_ONLY | `packages/workspace-contracts` | tests/contract/test_contract_files.py | Canonical JSON Schemas that form the stable boundary between core, providers, channels, Refinery and CVF. |
| workspace-web | PARTIAL | `apps/workspace-web` | apps/workspace-web/src/tests/App.test.tsx | Mobile PWA + Desktop Web operational UI (React/Vite). P2-C provides assignment-scoped reads and operator/supervisor workflows; P2-D adds bounded offline transition staging and foreground polling. |
| workspace-worker | PARTIAL | `apps/workspace-worker` | apps/workspace-worker/src/workspace_worker/__init__.py | Background jobs: message/event extraction, report generation, notification and outbound delivery, maintenance, scheduling, retry. |
