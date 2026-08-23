# Module Catalog

> GENERATED FILE — do not edit by hand. Source of truth is [`MODULE_REGISTRY.json`](MODULE_REGISTRY.json). Run `python scripts/generate_catalog.py --write` to regenerate.

_Last generated: 2026-08-23T04:49:57.978468+00:00_

## How to use this catalog

- **Before working:** find the module you will touch and read its `purpose`, `status`, `cvf_controls`, and `enforcement`.
- **After completing a piece:** update that module's entry in `MODULE_REGISTRY.json` (status, enforcement, next_step, tests), then run the generator to refresh this file and the metrics.
- **Size metrics are computed**, not written — they cannot lie about how much code exists.

## Totals

- Modules: **26**
- Code LOC (py/ts/tsx): **31391**
- Code files: **290**
- By status: contract-only=5, enforced=2, partial=13, stub=6

## Status legend

- **enforced** — Runtime code exists AND is covered by tests that block on violation.
- **partial** — Some runtime code exists but the intended capability/chain is incomplete.
- **contract-only** — Only an interface, schema, or policy YAML exists; no runtime behaviour.
- **stub** — Only README and/or empty __init__.py; no code and no contract.
- **empty** — Directory reserved by the frozen blueprint; nothing implemented yet.

## Modules

| Module | Path | Status | LOC | CVF controls | Purpose |
|---|---|---|---:|---|---|
| `cvf-runtime` | packages/cvf-runtime | enforced | 907 | identity, permission, domain_lock, data_scope, risk, approval, evidence, audit, cost, refusal, termination, freeze | Runtime enforcement of the CVF application profile: reads the profile YAML and exposes all 12 required_controls as callable gates. |
| `operations-ledger` | packages/operations-ledger | enforced | 2688 | evidence, audit, freeze | Source-of-truth persistence. Defines the Ledger Protocol and an append-only, dual-backend SqlLedger (SQLAlchemy Core over the existing migration schema; generic Uuid/JSON types work against SQLite or PostgreSQL from the same table definitions). InMemoryLedger (in workspace-api) is the offline/test backend. |
| `ai-gateway` | packages/ai-gateway | partial | 1663 | cost, termination, data_scope | Provider-neutral governed dispatch: AIGateway.execute calls data_scope, cost and termination gates before exactly one provider request; strict contracts, explicit registry, process-local usage reservations, structured-output validation, rules fallback and sanitized receipts. |
| `ai-providers` | packages/ai-providers | partial | 1417 | provider_authorization | P4-B provider-mode foundation (packages/ai-providers/src/ai_providers): ProviderModeService.execute is the sole mode-selection entry point for zero-call NO_AI, deterministic local RULES_ONLY, a default-denied evidence-ineligible MockProviderAdapter, ProviderAdapterRegistry-owned metadata, and EXTERNAL_AI delegation at most once to an injected P4-A AIGateway. Also retains the pre-existing non-secret Alibaba free-quota model catalog and deterministic expiry/quota-aware selector for governed live evidence runs. |
| `application-memory` | packages/application-memory | partial | 1254 | data_scope, evidence | Pure P4-A3 session/working application memory: strict immutable contracts, deterministic SESSION/WORKING layer policy, a process-local append-only store with correction/tombstone lineage, use-time scope/TTL/source revalidation and sanitized receipts. |
| `governed-rag` | packages/governed-rag | partial | 2442 | data_scope, evidence, cost, termination | Pure P4-A2 bounded application-layer governed-RAG composition: consumes only P4-A1's positive EvidenceAvailableV1, builds/validates a deterministic ephemeral hybrid (lexical+semantic) index, screens prompt injection, applies extractive minimization, assembles an instruction/data-separated context, and dispatches the injected P4-A AIGateway at most once with strict answer/citation-membership validation and a sanitized receipt. |
| `governed-retrieval` | packages/governed-retrieval | partial | 1681 | data_scope, evidence, termination | Pure P4-A1 request, corpus, lexical ranking, evidence projection, receipt and result contracts consumed by the workspace application composition. |
| `integration-edge` | apps/integration-edge | partial | 60 | data_scope, refusal | Channel Integration Edge: webhook gateway with signature verification, dedup, raw-payload preservation before any business system sees external input. |
| `operations-domain` | packages/operations-domain | partial | 818 | — | Domain language and invariants for shift, message, event, task, customer request, incident, handover, report, approval, correction, audit. |
| `project-knowledge-pack` | knowledge | partial | 0 | — | Repository-owned INTERNAL advisory knowledge pack for current project context, operations terminology and governance boundaries. |
| `refinery-bridge` | packages/refinery-bridge | partial | 1570 | data_scope | Boundary to CVF Refinery: normalize, terminology, dedupe, redact, classify, conflict detection, context candidates. |
| `retrieval-contracts` | packages/retrieval-contracts | partial | 1029 | data_scope | Pure deterministic P3-C contract binding admitted P3-A candidates to source, scope, lifecycle, retention, provenance and use-time revalidation evidence. |
| `workspace-api` | apps/workspace-api | partial | 8148 | identity, permission, domain_lock, risk, approval, evidence, audit, refusal, freeze | FastAPI backend for authenticated operational workflows across shifts, internal messages, events, corrections, tasks, customer requests, incidents, handovers and approvals. Each implemented action uses the applicable cvf-runtime identity/permission/audit and domain-specific risk/evidence/approval/domain_lock gates. "Golden vertical" is avoided here per the 2026-07-22 Codex review: durability and end-to-end scope remain action-, backend- and risk-specific; see docs/cvf/CVF_CONTROL_MAPPING.md. |
| `workspace-web` | apps/workspace-web | partial | 7684 | — | Mobile PWA + Desktop Web operational UI (React/Vite). P2-C provides assignment-scoped reads and operator/supervisor workflows; P2-D adds bounded offline transition staging and foreground polling. |
| `workspace-worker` | apps/workspace-worker | partial | 18 | — | Background jobs: message/event extraction, report generation, notification and outbound delivery, maintenance, scheduling, retry. |
| `channel-sdk` | packages/channel-sdk | contract-only | 12 | — | Shared interface for channel adapters: verify, parse, attachments, send, delivery status, health, credential refresh. |
| `cvf-application-profile` | packages/cvf-application-profile | contract-only | 0 | identity, permission, domain_lock, data_scope, risk, approval, evidence, cost, refusal, termination, freeze | Declarative CVF profile for this application: risk classes, approval, evidence, domain lock, data, cost, refusal, termination, freeze policies. Does not copy CVF core. |
| `cvf-bridge` | packages/cvf-bridge | contract-only | 0 | approval, refusal, evidence, audit | Bridge to CVF policy evaluation, approval gates, refusal, evidence, audit and fallback. |
| `operate-shift-workspace` | skills/operate-shift-workspace | contract-only | 0 | — | Provider-neutral navigation over current project continuity, phase/role routing, exact-path work orders, evidence review and bounded closure. |
| `workspace-contracts` | packages/workspace-contracts | contract-only | 0 | — | Canonical JSON Schemas that form the stable boundary between core, providers, channels, Refinery and CVF. |
| `channel-adapters` | packages/channel-adapters | stub | 0 | — | Concrete adapters for internal PWA, customer portal, generic webhook, Zalo, WhatsApp, email, SMS, and mocks. |
| `conversation-routing` | packages/conversation-routing | stub | 0 | domain_lock | Route messages to workspace, shift, vessel, customer, incident, or fallback. |
| `identity-mapping` | packages/identity-mapping | stub | 0 | identity | Map external identities to internal users/customer contacts with human confirmation. |
| `notification-engine` | packages/notification-engine | stub | 0 | — | In-app, push, email, SMS, outbound channels and escalation. |
| `reporting-engine` | packages/reporting-engine | stub | 0 | evidence | Build report drafts from confirmed records, validate evidence, export PDF/Excel. |
| `shared-kernel` | packages/shared-kernel | stub | 0 | — | Identifiers, time, errors, result, validation, observability and security primitives. |

## Per-module detail

### `cvf-runtime` — enforced

- **Path:** `packages/cvf-runtime` (package)
- **Purpose:** Runtime enforcement of the CVF application profile: reads the profile YAML and exposes all 12 required_controls as callable gates.
- **CVF controls:** identity, permission, domain_lock, data_scope, risk, approval, evidence, audit, cost, refusal, termination, freeze
- **Enforcement:** policy_loader.py loads profile; gates in identity/permission/domain_lock/data_scope/risk/approval/evidence/audit/budget(cost)/termination/errors(refusal). cost+termination run and are tested now, load-bearing when an AI mode beyond NO_AI is enabled.
- **Contract:** packages/cvf-application-profile/*.yaml
- **Depends on:** `cvf-application-profile`
- **Tests:** `tests/cvf/test_gates_unit.py`, `tests/cvf/test_vertical_end_to_end.py`, `tests/cvf/test_remaining_controls.py`, `tests/cvf/test_approval_known_principals.py`
- **Metrics:** 907 LOC across 13 code file(s)
- **Next step:** P2B approver-identity reconciliation is already FREEZE / CLOSED_BOUNDED: known-principals.yaml is no longer runtime authority, and authenticated durable six-field approval receipts are load-bearing within the reviewed boundary. Remaining cvf-runtime work is to wire data_scope, budget/cost and termination into a real AI runtime caller, and to implement refusal routing/recording; neither is load-bearing yet.

### `operations-ledger` — enforced

- **Path:** `packages/operations-ledger` (package)
- **Purpose:** Source-of-truth persistence. Defines the Ledger Protocol and an append-only, dual-backend SqlLedger (SQLAlchemy Core over the existing migration schema; generic Uuid/JSON types work against SQLite or PostgreSQL from the same table definitions). InMemoryLedger (in workspace-api) is the offline/test backend.
- **CVF controls:** evidence, audit, freeze
- **Enforcement:** ledger.py defines the Protocol (including transaction() unit-of-work); sql_ledger.py implements append-only INSERT for corrections/audit and maps tables.py to migrations 001+002; every mutating method accepts an optional unit= connection so callers can chain writes into one real SQL transaction (P-FIX-2). tables.py uses SQLAlchemy generic Uuid + JSON.with_variant(JSONB, 'postgresql') so one schema definition serves both backends, WITH matching FK/CHECK/column-set/nullability verified against the migration (P-FIX-4). evidence_links table (P-FIX-3) persists OperationalEvent/Task evidence, written once at creation. make_engine() turns ON SQLite foreign-key enforcement (off by default) so SQLite and PostgreSQL enforce the same integrity. Selected at runtime by workspace-api ledger_factory via DATABASE_URL. P1-POSTGRESQL-LIVE-ROUNDTRIP (2026-07-26, Amendment 1 repair): the three migration-native enum types (data_state, risk_class, shift_status) are now mapped with a per-column with_variant - portable String on SQLite, postgresql.ENUM(..., create_type=False) on PostgreSQL - across shifts.status, operational_events.risk/state, messages.state, tasks.risk/state, task_creation_intents.risk_class and approval_receipts.risk_class. The first live attempt correctly caught a real defect (psycopg v3 rejected a bare String bind against a native enum column with DatatypeMismatch); after this repair, a disposable local PostgreSQL 16 container (schema created only from database/migrations/001-004 via the existing apply_migrations.py, applied then reapplied) was verified end-to-end: real postgresql dialect/server-version-16 identity, live pg_catalog table/enum/column/PK/FK/CHECK parity for every SqlLedger-owned table, live enum type-name/value parity, full round-trip (shift/event+evidence/task+transition/correction/audit/user/approval-receipt/task-creation-intent) across engine disposal and reconnect, five constraint-rejection probes each followed by a working connection, and atomic transaction rollback - 36/36 passed, zero skips, reproduced twice, with the disposable container and its anonymous volume independently confirmed absent afterward. Bounded claim: this verifies a disposable local PostgreSQL 16 round-trip only - not production deployment, load, concurrency, backup/restore, HA or managed-PostgreSQL parity - and does not by itself close Phase 1 (see docs/decisions/POSTGRESQL_LIVE_ROUNDTRIP_EVIDENCE_RECEIPT.md; Phase 1 closes only once the existing shift-lifecycle and contract exit-gate suites are also independently reviewed and passing together with this result). 2026-07-22 (P2-A customer_request): customer_requests Table added (nullable shift_id FK, second FK to messages.message_id, status CHECK matching migration exactly) plus add/get/put_customer_request on both backends, verified two-directionally by test_schema_parity.py/test_schema_parity_types_and_checks.py. A minimal messages Table was added at this time purely so the source_message_id foreign key could resolve against this MetaData. 2026-07-30 (MESSAGE-ADMISSION-TRUST-REPAIR): messages persistence is now implemented - _message_store.py provides add_message/get_message/message_exists for SqlLedger (duplicate-id and unsupported-evidence refusals raise the same controlled ValueError shape as add_task/add_incident, never a raw IntegrityError), InMemoryLedger gained matching deep-copy semantics, and messages joined the schema-parity MAPPED set (test_schema_parity.py) and the explicit always-explicitly-supplied-PK set. Verified two-directionally, cross-backend (test_message_sqlite.py), and against a disposable live PostgreSQL 16 container through the real authenticated FastAPI/JWT route (test_message_postgres_live.py). 2026-07-22 (P2-B real authentication): users Table added (migration 003_users.sql - text primary key reusing known-principals.yaml-style ids, unique username, bcrypt password_hash, role CHECK matching cvf_runtime.identity.KNOWN_ROLES exactly, is_active) plus add_user/get_user_by_username on both backends; verified two-directionally by tests/integration/test_schema_parity_users.py (role CHECK values compared against KNOWN_ROLES, not just existence). 2026-07-26 (P2A-HANDOVER-VERTICAL): handovers/handover_items Tables added (_handover_tables.py, mirroring migration 006 exactly, including a native handover_status enum alongside the reused risk_class enum) plus open_work_snapshot/add_handover/get_handover/list_handovers_for_shift/put_handover on both backends (_handover_store.py for SqlLedger, _handover_repository.py for InMemoryLedger), verified two-directionally by test_schema_parity_handovers.py and cross-backend by test_sql_ledger_handovers.py/test_handover_vertical.py. open_work_snapshot derives the exact mandatory open-work set (Task not DONE/CANCELLED, CustomerRequest not CLOSED, Incident not CLOSED) directly from persisted state on both backends identically. 2026-07-26 HOV-REV-F7 repair (P2A-HANDOVER-VERTICAL Amendment 2): _handover_store.py's add_handover now prevalidates source/destination shift existence, duplicate aggregate id, duplicate item source and item/aggregate mismatch via SELECT against the SAME connection/unit before any INSERT, so no raw IntegrityError can escape and a rejection leaves no partial write; put_handover now loads the current row/items first and rejects any change outside status/reviewer/receiver/timestamps/version identically to InMemoryLedger. tests/integration/test_handover_ledger_parity.py (NEW) proves both backends reject the exact same controlled ValueError categories with no partial write. 2026-07-26 HOV-REV-F9 repair: _handover_store.py's immutability comparator now covers every HandoverItem field and the aggregate's created_at identically to InMemoryLedger, closing the gap where summary/evidence/created_at mutations passed through put_handover undetected. tests/integration/test_handover_ledger_parity.py adds parametrized per-field cross-backend rejection tests for every previously-omitted field (35 tests total).
- **Contract:** database/ (schema, migrations, views); operations_ledger.ledger.Ledger
- **Depends on:** `shared-kernel`
- **Tests:** `tests/cvf/test_ledger_protocol.py`, `tests/integration/test_sql_ledger_sqlite.py`, `tests/integration/test_sql_ledger_integrity.py`, `tests/integration/test_schema_parity.py`, `tests/integration/test_schema_parity_types_and_checks.py`, `tests/integration/test_schema_parity_users.py`, `tests/integration/test_evidence_persistence.py`, `tests/integration/test_sql_ledger_postgres_live.py`, `tests/integration/test_postgres_live_runner.py`, `tests/cvf/test_customer_request_vertical.py`, `tests/integration/test_schema_parity_handovers.py`, `tests/integration/test_sql_ledger_handovers.py`, `tests/integration/test_handover_postgres_live.py`, `tests/cvf/test_handover_vertical.py`, `tests/integration/test_handover_ledger_parity.py`, `tests/integration/test_message_sqlite.py`, `tests/integration/test_message_postgres_live.py`
- **Metrics:** 2688 LOC across 19 code file(s)
- **Next step:** PostgreSQL live round-trip is now reviewed and passing (bounded to a disposable local container - see enforcement note above). Messages persistence is implemented (see enforcement note above); it is no longer remaining work. Remaining pre-ship items: production deployment/load/concurrency/HA/backup verification, and mapping the remaining migration table (reports) into tables.py/SqlLedger as a tranche needs it. Phase 1 closure itself is a separate, independently-reviewed decision (SPEC AC-20), not implied by this entry.

### `ai-gateway` — partial

- **Path:** `packages/ai-gateway` (package)
- **Purpose:** Provider-neutral governed dispatch: AIGateway.execute calls data_scope, cost and termination gates before exactly one provider request; strict contracts, explicit registry, process-local usage reservations, structured-output validation, rules fallback and sanitized receipts.
- **CVF controls:** cost, termination, data_scope
- **Enforcement:** AIGateway.execute is the sole provider-dispatch point and invokes cvf_runtime.assert_placement_allowed, assert_within_budget and assert_not_terminated before dispatch; every pre-dispatch refusal yields provider_attempts=0. P4-A2 now supplies a reviewed bounded no-route application composition caller. No public API caller, durable usage store, production provider adapter (P4-B open) or deployment.
- **Contract:** packages/ai-gateway/contracts/ai_gateway.schema.json
- **Depends on:** `cvf-runtime`
- **Tests:** `tests/unit/test_p4a_gateway_models.py`, `tests/unit/test_p4a_gateway_registry.py`, `tests/unit/test_p4a_gateway_usage.py`, `tests/unit/test_p4a_gateway_context.py`, `tests/unit/test_p4a_gateway_validation.py`, `tests/unit/test_p4a_gateway_receipts.py`, `tests/unit/test_p4a_gateway_dependency_boundaries.py`, `tests/contract/test_p4a_ai_gateway_schema.py`, `tests/integration/test_p4a_gateway_live_evidence_support.py`
- **Metrics:** 1663 LOC across 11 code file(s)
- **Next step:** P4-B production provider adapter, public API/UI wiring and durable usage/audit persistence remain separate fresh-authority tranches. P4-A2's bounded no-route application composition is CLOSED_BOUNDED.

### `ai-providers` — partial

- **Path:** `packages/ai-providers` (package)
- **Purpose:** P4-B provider-mode foundation (packages/ai-providers/src/ai_providers): ProviderModeService.execute is the sole mode-selection entry point for zero-call NO_AI, deterministic local RULES_ONLY, a default-denied evidence-ineligible MockProviderAdapter, ProviderAdapterRegistry-owned metadata, and EXTERNAL_AI delegation at most once to an injected P4-A AIGateway. Also retains the pre-existing non-secret Alibaba free-quota model catalog and deterministic expiry/quota-aware selector for governed live evidence runs.
- **CVF controls:** provider_authorization
- **Enforcement:** ProviderModeService.execute implements request validation, mode selection, local policy or external identity binding, execution/delegation, output validation and a sanitized receipt in that exact order. NO_AI and RULES_ONLY structurally cannot reach a gateway/provider; RULES_ONLY validates winning output with the real ai_gateway.validation function and never falls through on schema failure; EXTERNAL_AI requires an identity-matched nested GatewayRequest and calls the injected gateway at most once. Alibaba live-run configuration excludes disabled, exhausted, and expiration-day models, then selects deterministically by explicit priority, nearest expiration, remaining quota, and model code. No production/vendor provider adapter, automatic routing, retry, durable usage/audit, public API/UI or deployment; workspace_api.application.ai_provider_modes is a no-route, no-persistence composition function only, not yet wired to any application caller.
- **Contract:** packages/ai-providers/contracts/provider_modes.schema.json
- **Depends on:** `ai-gateway`
- **Tests:** `tests/unit/test_alibaba_model_selector.py`, `tests/unit/test_p4b_provider_models.py`, `tests/unit/test_p4b_no_ai.py`, `tests/unit/test_p4b_rules_only.py`, `tests/unit/test_p4b_mock_provider.py`, `tests/unit/test_p4b_provider_registry.py`, `tests/unit/test_p4b_provider_service.py`, `tests/unit/test_p4b_provider_dependency_boundaries.py`, `tests/contract/test_p4b_provider_modes_schema.py`, `tests/integration/test_p4b_provider_application_composition.py`, `tests/integration/test_p4b_provider_live_evidence_support.py`, `tests/cvf/test_p4b_provider_governance_boundaries.py`
- **Metrics:** 1417 LOC across 10 code file(s)
- **Next step:** BUILD-complete pending independent REVIEW. Real-provider governance proof (running scripts/run_p4b_ai_providers_live_evidence.py) remains a separate, non-consuming post-review authority checkpoint; no production/vendor adapter or application wiring is authorized yet.

### `application-memory` — partial

- **Path:** `packages/application-memory` (package)
- **Purpose:** Pure P4-A3 session/working application memory: strict immutable contracts, deterministic SESSION/WORKING layer policy, a process-local append-only store with correction/tombstone lineage, use-time scope/TTL/source revalidation and sanitized receipts.
- **CVF controls:** data_scope, evidence
- **Enforcement:** application_memory.ApplicationMemory implements fixed admission/read/correct/delete flows over InMemoryApplicationMemoryStore. Entries are immutable, frozen and deep-copy isolated; admission requires authenticated owner/shift/scope and a positive source-revalidation result bound to source type/id/version/content/provenance digests; correction atomically appends a successor and tombstones its predecessor; delete atomically appends a tombstone; every refusal reports zero mutations. workspace_api.application.application_memory.build_application_memory is the sole application composition owner (verifies assignment, computes the exact authorization-scope digest, injects store/clock/revalidator; opens no route, persists nothing, and never recalls memory implicitly into P4-A2). No provider SDK, HTTP client, environment, database or hidden-Core import anywhere in the pure package.
- **Contract:** packages/application-memory/contracts/application_memory.schema.json
- **Depends on:** `retrieval-contracts`
- **Tests:** `tests/unit/test_p4a3_memory_models.py`, `tests/unit/test_p4a3_memory_hashing.py`, `tests/unit/test_p4a3_memory_policy.py`, `tests/unit/test_p4a3_memory_store.py`, `tests/unit/test_p4a3_memory_receipts.py`, `tests/unit/test_p4a3_memory_service.py`, `tests/unit/test_p4a3_memory_dependency_boundaries.py`, `tests/contract/test_p4a3_application_memory_schema.py`, `tests/integration/test_p4a3_memory_application_composition.py`, `tests/integration/test_p4a3_memory_live_evidence_support.py`, `tests/cvf/test_p4a3_memory_governance_boundaries.py`
- **Metrics:** 1254 LOC across 8 code file(s)
- **Next step:** P4-A3 is FREEZE / CLOSED_BOUNDED after independent review and separately authorized one-call synthetic live evidence. P4-B requires a fresh control chain. Episodic/semantic memory, durable persistence, public API/UI, production provider adapter, deployment and production readiness remain out of scope.

### `governed-rag` — partial

- **Path:** `packages/governed-rag` (package)
- **Purpose:** Pure P4-A2 bounded application-layer governed-RAG composition: consumes only P4-A1's positive EvidenceAvailableV1, builds/validates a deterministic ephemeral hybrid (lexical+semantic) index, screens prompt injection, applies extractive minimization, assembles an instruction/data-separated context, and dispatches the injected P4-A AIGateway at most once with strict answer/citation-membership validation and a sanitized receipt.
- **CVF controls:** data_scope, evidence, cost, termination
- **Enforcement:** governed_rag.GovernedRAG.execute implements DESIGN steps 4-13: independent SPEC R5 re-verification of every P4-A1 receipt/handoff/projection/citation binding (never trusts caller relabeling), fresh ephemeral index build+self-validation with STALE_INDEX fail-closed, deterministic 45/55 integer lexical+semantic fusion via the local PROJECT_CONCEPT_FEATURE_VECTOR_V1 substrate, versioned injection screening with INJECTION_BLOCKED fail-closed, MINIMIZATION_EXTRACTIVE_V1 with an independently recomputable proof, closed instruction/evidence context assembly bound to a recomputed context_digest, at most one dispatch of the injected ai_gateway.service.AIGateway, and post-dispatch citation-membership validation against the exact post-omission granted set. workspace_api.application.governed_rag.execute_governed_rag is the sole application composition owner (calls P4-A1 then this package; opens no HTTP route; persists nothing). No provider SDK, HTTP client, environment, database or hidden-Core import anywhere in the pure package.
- **Contract:** packages/governed-rag/contracts/governed_rag.schema.json
- **Depends on:** `governed-retrieval`, `retrieval-contracts`, `ai-gateway`
- **Tests:** `tests/unit/test_p4a2_rag_models.py`, `tests/unit/test_p4a2_rag_hashing.py`, `tests/unit/test_p4a2_rag_semantic.py`, `tests/unit/test_p4a2_rag_index.py`, `tests/unit/test_p4a2_rag_injection.py`, `tests/unit/test_p4a2_rag_minimization.py`, `tests/unit/test_p4a2_rag_context.py`, `tests/unit/test_p4a2_rag_validation.py`, `tests/unit/test_p4a2_rag_receipts.py`, `tests/unit/test_p4a2_rag_service.py`, `tests/unit/test_p4a2_rag_dependency_boundaries.py`, `tests/contract/test_p4a2_governed_rag_schema.py`, `tests/integration/test_p4a2_rag_application_composition.py`, `tests/integration/test_p4a2_rag_live_evidence_support.py`, `tests/cvf/test_p4a2_rag_governance_boundaries.py`
- **Metrics:** 2442 LOC across 12 code file(s)
- **Next step:** P4-A2 is FREEZE / CLOSED_BOUNDED for the reviewed synthetic/local Project Knowledge, ephemeral-index and no-route application-composition boundary. Operational-corpus RAG, general embeddings, durable index/audit/memory, a public API/UI, P4-A3, P4-B production provider adapter, deployment and production readiness remain open.

### `governed-retrieval` — partial

- **Path:** `packages/governed-retrieval` (package)
- **Purpose:** Pure P4-A1 request, corpus, lexical ranking, evidence projection, receipt and result contracts consumed by the workspace application composition.
- **CVF controls:** data_scope, evidence, termination
- **Enforcement:** Strict local V1 request, corpus, lexical, projection, receipt and result contracts. The separately owned workspace-api application composition verifies token identity, permission and assignment before source reads; Project Knowledge is the sole positive INTERNAL/LOCAL_ONLY corpus and operational corpora fail closed. No provider, API route, durable audit/persistence, semantic/vector RAG or production deployment.
- **Contract:** packages/governed-retrieval/contracts/governed_retrieval.schema.json
- **Depends on:** `retrieval-contracts`
- **Tests:** `tests/unit/test_p4a1_retrieval_models.py`, `tests/unit/test_p4a1_retrieval_lexical.py`, `tests/unit/test_p4a1_retrieval_projection.py`, `tests/unit/test_p4a1_retrieval_receipts.py`, `tests/unit/test_p4a1_retrieval_dependencies.py`, `tests/cvf/test_p4a1_governed_retrieval.py`, `tests/cvf/test_p4a1_governed_retrieval_boundaries.py`, `tests/cvf/test_p4a1_retrieval_authorization.py`, `tests/cvf/test_p4a1_retrieval_authorization_ordering.py`, `tests/integration/test_p4a1_retrieval_ledger_parity.py`, `tests/integration/test_p4a1_retrieval_project_knowledge.py`, `tests/contract/test_p4a1_governed_retrieval_schema.py`, `tests/contract/test_p4a1_governed_retrieval_source_limits.py`
- **Metrics:** 1681 LOC across 11 code file(s)
- **Next step:** P4-A1 is CLOSED_BOUNDED and parked after mapping. Operational digest owners, LPCI1-REF, P4-A/P4-A2, provider/RAG, API/UI, durable audit/persistence and deployment require fresh authority.

### `integration-edge` — partial

- **Path:** `apps/integration-edge` (app)
- **Purpose:** Channel Integration Edge: webhook gateway with signature verification, dedup, raw-payload preservation before any business system sees external input.
- **CVF controls:** data_scope, refusal
- **Enforcement:** webhook/router.py verifies HMAC (constant-time) and fails closed on missing secret outside development; deduplication/store.py drops duplicates.
- **Contract:** packages/channel-sdk (adapter interface)
- **Depends on:** `channel-sdk`
- **Tests:** `tests/security/test_hmac.py`
- **Metrics:** 60 LOC across 14 code file(s)
- **Next step:** Implement raw_payload, quarantine, rate_limit, routing, outbound modules (currently stub).

### `operations-domain` — partial

- **Path:** `packages/operations-domain` (package)
- **Purpose:** Domain language and invariants for shift, message, event, task, customer request, incident, handover, report, approval, correction, audit.
- **CVF controls:** —
- **Enforcement:** operations_domain.models and operations_domain.lifecycle are the single canonical definitions for the extracted shift/message/event/task/customer-request/correction types and guards. Later P2-A tranches added canonical Incident/IncidentStatus plus assert_incident_transition, and Handover/HandoverItem/HandoverStatus plus assert_handover_transition. workspace_api.domain.models/.lifecycle remain compatibility shims with object-identity tests. User intentionally remains canonical in workspace_api.domain.models because it belongs to the authentication boundary; the closed approver-identity reconciliation removed known-principals.yaml as runtime authority without relocating User. The package remains a stdlib+pydantic dependency sink and is partial, not enforced: Report, Approval and Audit still lack package-owned operational models/lifecycle, and the eleven per-domain blueprint subdirectories remain README-only rather than owning the central definitions.
- **Contract:** packages/workspace-contracts
- **Depends on:** `shared-kernel`
- **Tests:** `tests/unit/test_operations_domain_boundary.py`, `tests/unit/test_operations_domain_shim_identity.py`, `tests/unit/test_operations_domain_serialization.py`, `tests/cvf/test_incident_vertical.py`, `tests/cvf/test_handover_vertical.py`
- **Metrics:** 818 LOC across 5 code file(s)
- **Next step:** Incident, handover, operational Report and the Phase 2 full-shift exit gate are CLOSED_BOUNDED; do not reopen them. Fresh PROJECT-OPERATIONS-SKILL INTAKE is next. Approval/Audit ownership and any split of central models.py remain separate future tranches; do not claim operations-domain enforced.

### `project-knowledge-pack` — partial

- **Path:** `knowledge` (package)
- **Purpose:** Repository-owned INTERNAL advisory knowledge pack for current project context, operations terminology and governance boundaries.
- **CVF controls:** —
- **Enforcement:** Local validator checks exact schema and types, source pins, citations, freshness, path containment, bounded secret patterns and residue. It does not enforce access, data minimization, external ingest, retrieval, automatic context injection or AI/provider behavior.
- **Contract:** knowledge/manifest.json
- **Depends on:** —
- **Tests:** `tests/unit/test_project_knowledge_pack.py`, `tests/integration/test_project_knowledge_ingest_rehearsal.py`
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Fresh P3-A Refinery INTAKE only; retrieval, RAG and learning remain parked.

### `refinery-bridge` — partial

- **Path:** `packages/refinery-bridge` (package)
- **Purpose:** Boundary to CVF Refinery: normalize, terminology, dedupe, redact, classify, conflict detection, context candidates.
- **CVF controls:** data_scope
- **Enforcement:** Deterministic local V1 boundary with strict pre-admission, nine fail-stop receipts, typed dedupe, redaction, quarantine/fallback and 100/100 candidate admission; no runtime caller.
- **Contract:** packages/refinery-bridge/contracts/refinery_contract.yaml
- **Depends on:** `shared-kernel`
- **Tests:** `tests/unit/test_refinery_models.py`, `tests/unit/test_refinery_canonical.py`, `tests/unit/test_refinery_pipeline.py`, `tests/unit/test_refinery_adversarial.py`, `tests/unit/test_refinery_contract.py`
- **Metrics:** 1570 LOC across 11 code file(s)
- **Next step:** P3-A is CLOSED_BOUNDED at reviewed BUILD a6cf978. Module remains partial until a separately governed runtime caller; no provider, remote ingest, data_scope enforcement, retrieval/RAG or production claim.

### `retrieval-contracts` — partial

- **Path:** `packages/retrieval-contracts` (package)
- **Purpose:** Pure deterministic P3-C contract binding admitted P3-A candidates to source, scope, lifecycle, retention, provenance and use-time revalidation evidence.
- **CVF controls:** data_scope
- **Enforcement:** Strict V1 models and a total zero-I/O constructor. Message and project-knowledge advisory evidence can become retrieval-ready when every explicit input is valid; canonical operational records fail closed until a separately reviewed public source-owned digest contract exists. No runtime caller, retrieval, tenant model or placement enforcement.
- **Contract:** packages/retrieval-contracts/contracts/retrieval_contract.schema.json
- **Depends on:** `refinery-bridge`, `operations-domain`
- **Tests:** `tests/unit/test_p3c_retrieval_contract_models.py`, `tests/unit/test_p3c_retrieval_contract_constructor.py`, `tests/unit/test_p3c_retrieval_contract_adversarial.py`, `tests/unit/test_p3c_retrieval_contract_digest_guards.py`, `tests/contract/test_p3c_retrieval_contract_schema.py`
- **Metrics:** 1029 LOC across 7 code file(s)
- **Next step:** P3-C is CLOSED_BOUNDED at reviewed BUILD 4cc0691. Fresh P4-A1 governed-retrieval INTAKE is next; no runtime retrieval, provider, vector/index, tenant authorization, load-bearing data_scope, placement or production claim carries forward.

### `workspace-api` — partial

- **Path:** `apps/workspace-api` (app)
- **Purpose:** FastAPI backend for authenticated operational workflows across shifts, internal messages, events, corrections, tasks, customer requests, incidents, handovers and approvals. Each implemented action uses the applicable cvf-runtime identity/permission/audit and domain-specific risk/evidence/approval/domain_lock gates. "Golden vertical" is avoided here per the 2026-07-22 Codex review: durability and end-to-end scope remain action-, backend- and risk-specific; see docs/cvf/CVF_CONTROL_MAPPING.md.
- **CVF controls:** identity, permission, domain_lock, risk, approval, evidence, audit, refusal, freeze
- **Enforcement:** events/router.py + services.py run the confirm chain; corrections/router.py + correction_service.py run the correction chain; tasks/router.py + task_service.py run task create/transition; shifts/router.py + shift_service.py run close/freeze (close requires identity/permission `shift.close` (min role operator) + a state-check rejecting close of an already-FROZEN shift; freeze requires identity/permission/shift_closed + an explicit audited override for the two prerequisites with no model yet); customer_requests/router.py + customer_request_service.py run customer-request create/transition (create requires identity/permission `customer_request.create` + domain_lock `customer_request` + a frozen-shift check only when shift_id is provided, since shift_id is nullable on this table; transition requires identity/permission `customer_request.transition` + the customer-request-status lifecycle guard). All reuse cvf-runtime gates and depend on the operations-ledger Ledger Protocol (backend via DATABASE_URL). 2026-07-23 (P1B-OPERATIONS-DOMAIN-EXTRACTION): the operational models and their three lifecycle guards (assert_transition, assert_task_transition, assert_customer_request_transition) moved to the operations-domain package; domain/models.py and domain/lifecycle.py in this app are now compatibility shims that re-export the same objects (proven by identity assertions, not just equality) rather than defining them, with the single documented exception of User, which stays defined here because it belongs to the authentication boundary, not the operations domain. Application code, routers and tests import the moved types directly from operations_domain; the only remaining workspace_api.domain.models imports are User (does not move) and the shim-namespace object injected into SqlLedger(models=...), which still needs to expose User alongside the re-exported operational types. See docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md. 2026-07-22 (P-FIX-1): both InMemoryLedger and SqlLedger now block add_event/put_event/add_task/put_task when the parent shift is FROZEN (previously only InMemoryLedger blocked new records, and SqlLedger blocked nothing); CorrectionService uses allow_when_frozen=True as the sole permitted post-freeze mutation path. 2026-07-22 (P-FIX-6): shifts/router.py close_shift previously called ledger.close_shift() directly with no identity/permission/audit at all (a second independent review's probe: anonymous close -> 200 CLOSED, audit_count=0, which could silently satisfy freeze's shift_closed prerequisite); now routed through ShiftService.close, same identity -> permission -> state-check -> transaction(mutate+audit) shape as freeze. 2026-07-22 (P2-A customer_request): fourth CVF vertical added; no risk/evidence/approval gate wired for create (customer_requests has no risk_class/evidence column in the migration, unlike tasks/operational_events - simpler by design, not an omission); domain_lock is now exercised for a second domain besides create_event. 2026-07-22 (P2-B real authentication): dependencies.py::get_principal no longer trusts client-supplied X-User-Id/X-User-Role headers - it now requires a JWT bearer token (workspace_api/auth/tokens.py, HS256, signed with the required JWT_SECRET_KEY env var, no default so the app fails closed at startup without one) and constructs Principal only from the verified sub/role claims. POST /auth/login (workspace_api/auth/router.py) issues tokens after checking a username/password against the new users table (bcrypt-hashed, workspace_api/auth/passwords.py) - unknown username, wrong password, and inactive account all return the same generic 401 to avoid username enumeration. Every router keeps `principal: Principal = Depends(get_principal)` unchanged; only get_principal's body changed. The `identity` CVF control moves from not-verified-server-side to load-bearing - see docs/cvf/CVF_CONTROL_MAPPING.md. Explicitly out of scope for this tranche (recorded, not silently dropped): refresh tokens/revocation, self-service registration, password reset, login rate-limiting, and reconciling known-principals.yaml's separate approver registry with the new users table - approval-fabrication (High Finding #4) is unaffected. User provisioning is scripts/seed_dev_users.py (dev/test only). An independent review (fresh agent context) probed the running code for bypasses (old-header impersonation, alg=none, wrong signing key, expired token, forged unknown-role claim) and found none, but found and this tranche fixed a real login-timing side-channel: verify_password was skipped entirely for an unknown username, making that response measurably faster than a wrong-password response despite an identical body - fixed by always running verify_password against a precomputed DUMMY_PASSWORD_HASH. 2026-07-26 (P2A-HANDOVER-VERTICAL): sixth CVF vertical added - HandoverService.create/review/acknowledge (domain shift_handover). create derives every item server-side from the exact open Task/CustomerRequest/Incident set for the source shift (never caller-supplied); each item carries a canonical SHA-256 digest over its server-derived source snapshot. review (sender) and acknowledge (distinct receiver) both revalidate destination-OPEN/source-not-FROZEN state and exact snapshot membership before persisting. ShiftService.freeze's open_handover_items_linked prerequisite is now real (assert_freeze_ready): at least one ACKNOWLEDGED handover whose snapshot still matches current open work, sharing one transaction with the freeze mutation and both audit writes; report_approved remains the sole explicit audited override. HOV-AUTH-F4 repair: test_atomic_mutation_audit.py and test_customer_request_vertical.py's freeze-adjacent fixtures now construct a genuine reviewed/acknowledged handover instead of relying on the retired open_handover_items_linked override. 2026-07-26 HOV-REV-F5/F7 repair (P2A-HANDOVER-VERTICAL Amendment 2): test_customer_request_vertical.py (321 lines, previously grandfathered debt) is split into itself (create/HTTP, <=300), _customer_request_fixtures.py (shared setup) and test_customer_request_transitions.py (lifecycle/transition); its debt entry is removed, not rehashed. test_customer_request_repair.py (outside this repair's authorized paths) still imports its fixtures unchanged from test_customer_request_vertical, which now re-exposes them from the shared module. _handover_repository.py now prevalidates source/destination shift existence, duplicate aggregate id, duplicate item source and item/aggregate mismatch before any dict mutation, and enforces put_handover as lifecycle-fields-only (status/reviewer/receiver/timestamps/version), matching SqlLedger's equivalent fix exactly (see operations-ledger). 2026-07-26 HOV-REV-F9 repair (P2A-HANDOVER-VERTICAL Amendment 2, same 44-path ceiling, no Amendment 3): _handover_repository.py's immutability comparator now covers every HandoverItem field (item_id, handover_id, source type/id/digest, summary, owner_id, due_at, risk_class, all evidence fields) and the aggregate's own created_at, not only (record_type, record_id, digest); a rejected put_handover still leaves stored data unchanged.
- **Contract:** apps/workspace-api/pyproject.toml
- **Depends on:** `cvf-runtime`, `operations-ledger`, `operations-domain`
- **Tests:** `apps/workspace-api/src/workspace_api/tests/test_lifecycle.py`, `tests/cvf/test_vertical_end_to_end.py`, `tests/cvf/test_correction_vertical.py`, `tests/cvf/test_task_vertical.py`, `tests/cvf/test_freeze_invariant.py`, `tests/cvf/test_atomic_mutation_audit.py`, `tests/cvf/test_approval_known_principals.py`, `tests/cvf/test_shift_close_governance.py`, `tests/cvf/test_customer_request_vertical.py`, `tests/cvf/test_auth_tokens.py`, `tests/cvf/test_auth_login.py`, `tests/integration/test_evidence_persistence.py`, `tests/unit/test_operations_domain_boundary.py`, `tests/unit/test_operations_domain_shim_identity.py`, `tests/unit/test_operations_domain_serialization.py`, `tests/cvf/test_handover_vertical.py`, `tests/cvf/_shift_close_fixtures.py`, `tests/cvf/test_shift_close_freeze_interaction.py`, `tests/integration/test_sql_ledger_handovers.py`, `tests/unit/test_p2b_openapi_contract.py`, `tests/cvf/_customer_request_fixtures.py`, `tests/cvf/test_customer_request_transitions.py`, `tests/cvf/test_message_admission.py`, `tests/unit/test_message_openapi_contract.py`, `tests/integration/test_message_admission_live_evidence_runner.py`
- **Metrics:** 8148 LOC across 83 code file(s)
- **Next step:** Phase 2 is CLOSED_BOUNDED after reviewed full-shift exit BUILD d02186a and separate C4. Fresh PROJECT-OPERATIONS-SKILL INTAKE is next; governed external/channel ingestion remains a separate Phase 4 Integration Edge tranche.

### `workspace-web` — partial

- **Path:** `apps/workspace-web` (app)
- **Purpose:** Mobile PWA + Desktop Web operational UI (React/Vite). P2-C provides assignment-scoped reads and operator/supervisor workflows; P2-D adds bounded offline transition staging and foreground polling.
- **CVF controls:** —
- **Enforcement:** App.tsx restores a tab-scoped JWT session; ConnectivityRuntime resolves /auth/me before queue/poll activation. Exactly three typed CAS transitions may stage in a strict actor-bound 50-item/24-hour queue while pre-dispatch offline; all other mutations remain online-only. Replay and foreground polling share serialized refresh, fail stop on ambiguity/conflict/server errors and keep backend identity/permission/assignment/version gates authoritative. The navigation service worker never caches API/auth data; polling is not push and the queue is not exactly-once.
- **Contract:** packages/workspace-contracts (JSON schemas)
- **Depends on:** `workspace-contracts`, `workspace-api`
- **Tests:** `apps/workspace-web/src/tests/App.test.tsx`, `apps/workspace-web/src/tests/api.test.ts`, `apps/workspace-web/src/tests/operatorActionsCore.test.tsx`, `apps/workspace-web/src/tests/supervisorStaffing.test.tsx`, `apps/workspace-web/src/tests/supervisorCloseout.test.tsx`, `apps/workspace-web/src/tests/supervisorMutationState.test.tsx`, `apps/workspace-web/src/tests/offlineQueue.test.ts`, `apps/workspace-web/src/tests/offlineSync.test.ts`, `apps/workspace-web/src/tests/realtimeSync.test.ts`, `apps/workspace-web/e2e/p2d-offline-realtime.spec.ts`, `apps/workspace-web/e2e/phase2-full-shift-exit.spec.ts`, `tests/integration/test_phase2_full_shift_exit_postgres_live.py`, `tests/integration/test_phase2_full_shift_live_evidence_runner.py`
- **Metrics:** 7684 LOC across 79 code file(s)
- **Next step:** Phase 2 is CLOSED_BOUNDED after exact reviewed/pushed full-shift exit BUILD d02186a plus separate C4. Fresh PROJECT-OPERATIONS-SKILL INTAKE is next. Tenant/provider data_scope, soak and production readiness remain unclaimed.

### `workspace-worker` — partial

- **Path:** `apps/workspace-worker` (app)
- **Purpose:** Background jobs: message/event extraction, report generation, notification and outbound delivery, maintenance, scheduling, retry.
- **CVF controls:** —
- **Enforcement:** main.py + retry/policy.py present; all job modules are stub.
- **Contract:** apps/workspace-worker/pyproject.toml
- **Depends on:** `operations-ledger`, `notification-engine`
- **Tests:** —
- **Metrics:** 18 LOC across 6 code file(s)
- **Next step:** Implement job modules once their owning packages exist.

### `channel-sdk` — contract-only

- **Path:** `packages/channel-sdk` (package)
- **Purpose:** Shared interface for channel adapters: verify, parse, attachments, send, delivery status, health, credential refresh.
- **CVF controls:** —
- **Enforcement:** adapter-interface/adapter.py defines the interface; used by integration-edge.
- **Contract:** packages/channel-sdk/adapter-interface/adapter.py
- **Depends on:** —
- **Tests:** —
- **Metrics:** 12 LOC across 1 code file(s)
- **Next step:** Provide concrete adapters in channel-adapters.

### `cvf-application-profile` — contract-only

- **Path:** `packages/cvf-application-profile` (package)
- **Purpose:** Declarative CVF profile for this application: risk classes, approval, evidence, domain lock, data, cost, refusal, termination, freeze policies. Does not copy CVF core.
- **CVF controls:** identity, permission, domain_lock, data_scope, risk, approval, evidence, cost, refusal, termination, freeze
- **Enforcement:** Policy source only; all 12 controls now enforced by cvf-runtime (cost/termination AI-gated).
- **Contract:** profile.yaml, risk-classes.yaml, approval-policy.yaml, evidence-policy.yaml, domain-lock.yaml, data-policy.yaml, cost-policy.yaml, refusal-policy.yaml, termination-policy.yaml, freeze-policy.yaml, provider-policy.yaml
- **Depends on:** —
- **Tests:** `tests/contract/test_contract_files.py`
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Keep policy YAML authoritative; changes here flow into cvf-runtime gates automatically.

### `cvf-bridge` — contract-only

- **Path:** `packages/cvf-bridge` (package)
- **Purpose:** Bridge to CVF policy evaluation, approval gates, refusal, evidence, audit and fallback.
- **CVF controls:** approval, refusal, evidence, audit
- **Enforcement:** policy-evaluation/policy_contract.yaml only. NOTE: cvf-runtime now provides the concrete in-workspace enforcement; reconcile scope with cvf-runtime.
- **Contract:** packages/cvf-bridge/policy-evaluation/policy_contract.yaml
- **Depends on:** `cvf-application-profile`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Decide whether this stays a contract or is superseded by cvf-runtime.

### `operate-shift-workspace` — contract-only

- **Path:** `skills/operate-shift-workspace` (skill)
- **Purpose:** Provider-neutral navigation over current project continuity, phase/role routing, exact-path work orders, evidence review and bounded closure.
- **CVF controls:** —
- **Enforcement:** None. This skill is guidance over current repository authority; it grants no permission and does not enforce governance.
- **Contract:** skills/operate-shift-workspace/SKILL.md
- **Depends on:** —
- **Tests:** `tests/unit/test_project_operations_skill_contract.py`, `tests/unit/test_project_operations_skill_live_evidence.py`
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Keep repository source uninstalled until a separate post-FREEZE installation tranche is explicitly authorized. Fresh PROJECT-KNOWLEDGE-PACK INTAKE is next.

### `workspace-contracts` — contract-only

- **Path:** `packages/workspace-contracts` (package)
- **Purpose:** Canonical JSON Schemas that form the stable boundary between core, providers, channels, Refinery and CVF.
- **CVF controls:** —
- **Enforcement:** Schemas only.
- **Contract:** JSON Schemas under this package
- **Depends on:** —
- **Tests:** `tests/contract/test_contract_files.py`
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Keep schemas authoritative as domains are implemented.

### `channel-adapters` — stub

- **Path:** `packages/channel-adapters` (package)
- **Purpose:** Concrete adapters for internal PWA, customer portal, generic webhook, Zalo, WhatsApp, email, SMS, and mocks.
- **CVF controls:** —
- **Enforcement:** None yet.
- **Contract:** packages/channel-sdk
- **Depends on:** `channel-sdk`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement generic-webhook + mock adapters first; Zalo/WhatsApp remain mock until credentials.

### `conversation-routing` — stub

- **Path:** `packages/conversation-routing` (package)
- **Purpose:** Route messages to workspace, shift, vessel, customer, incident, or fallback.
- **CVF controls:** domain_lock
- **Enforcement:** None yet.
- **Contract:** packages/workspace-contracts
- **Depends on:** `operations-domain`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement after operations-domain and identity-mapping.

### `identity-mapping` — stub

- **Path:** `packages/identity-mapping` (package)
- **Purpose:** Map external identities to internal users/customer contacts with human confirmation.
- **CVF controls:** identity
- **Enforcement:** None yet.
- **Contract:** packages/workspace-contracts
- **Depends on:** `shared-kernel`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement when external channels are integrated.

### `notification-engine` — stub

- **Path:** `packages/notification-engine` (package)
- **Purpose:** In-app, push, email, SMS, outbound channels and escalation.
- **CVF controls:** —
- **Enforcement:** None yet.
- **Contract:** packages/workspace-contracts
- **Depends on:** `channel-adapters`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement after outbound channel adapters exist.

### `reporting-engine` — stub

- **Path:** `packages/reporting-engine` (package)
- **Purpose:** Build report drafts from confirmed records, validate evidence, export PDF/Excel.
- **CVF controls:** evidence
- **Enforcement:** None yet.
- **Contract:** packages/workspace-contracts
- **Depends on:** `operations-ledger`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement once operations-ledger returns confirmed records.

### `shared-kernel` — stub

- **Path:** `packages/shared-kernel` (package)
- **Purpose:** Identifiers, time, errors, result, validation, observability and security primitives.
- **CVF controls:** —
- **Enforcement:** None yet.
- **Contract:** internal
- **Depends on:** —
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Extract shared primitives as real code appears across packages.

## Related

- CVF control enforcement points: [`docs/cvf/CVF_CONTROL_MAPPING.md`](../cvf/CVF_CONTROL_MAPPING.md)
- Release/validation status: `IMPLEMENTATION_STATUS.json` (repo root)
