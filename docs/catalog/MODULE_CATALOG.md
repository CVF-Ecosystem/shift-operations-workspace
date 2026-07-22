# Module Catalog

> GENERATED FILE — do not edit by hand. Source of truth is [`MODULE_REGISTRY.json`](MODULE_REGISTRY.json). Run `python scripts/generate_catalog.py --write` to regenerate.

_Last generated: 2026-07-22T04:05:03.733871+00:00_

## How to use this catalog

- **Before working:** find the module you will touch and read its `purpose`, `status`, `cvf_controls`, and `enforcement`.
- **After completing a piece:** update that module's entry in `MODULE_REGISTRY.json` (status, enforcement, next_step, tests), then run the generator to refresh this file and the metrics.
- **Size metrics are computed**, not written — they cannot lie about how much code exists.

## Totals

- Modules: **20**
- Code LOC (py/ts/tsx): **2847**
- Code files: **87**
- By status: contract-only=6, enforced=2, partial=4, stub=8

## Status legend

- **enforced** — Runtime code exists AND is covered by tests that block on violation.
- **partial** — Some runtime code exists but the intended capability/chain is incomplete.
- **contract-only** — Only an interface, schema, or policy YAML exists; no runtime behaviour.
- **stub** — Only README and/or empty __init__.py; no code and no contract.
- **empty** — Directory reserved by the frozen blueprint; nothing implemented yet.

## Modules

| Module | Path | Status | LOC | CVF controls | Purpose |
|---|---|---|---:|---|---|
| `cvf-runtime` | packages/cvf-runtime | enforced | 793 | identity, permission, domain_lock, data_scope, risk, approval, evidence, audit, cost, refusal, termination, freeze | Runtime enforcement of the CVF application profile: reads the profile YAML and exposes all 12 required_controls as callable gates. |
| `operations-ledger` | packages/operations-ledger | enforced | 669 | evidence, audit, freeze | Source-of-truth persistence. Defines the Ledger Protocol and an append-only, dual-backend SqlLedger (SQLAlchemy Core over the existing migration schema; generic Uuid/JSON types work against SQLite or PostgreSQL from the same table definitions). InMemoryLedger (in workspace-api) is the offline/test backend. |
| `integration-edge` | apps/integration-edge | partial | 60 | data_scope, refusal | Channel Integration Edge: webhook gateway with signature verification, dedup, raw-payload preservation before any business system sees external input. |
| `workspace-api` | apps/workspace-api | partial | 1214 | identity, permission, domain_lock, risk, approval, evidence, audit, refusal, freeze | FastAPI backend: shifts, messages, operational events, corrections, tasks. Four domains route through the same cvf-runtime gate chain (identity/permission/audit, plus risk/evidence/approval where applicable): event confirmation, post-freeze correction, task create/transition, and shift close/freeze. "Golden vertical" is avoided here per the 2026-07-22 Codex review (docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md): whether a given path is durable/end-to-end depends on ledger backend and risk class - see docs/cvf/CVF_CONTROL_MAPPING.md for the callable/load-bearing/not-verified-server-side distinction per control. |
| `workspace-web` | apps/workspace-web | partial | 59 | — | Mobile PWA + Desktop Web operational UI (React/Vite). Minimal shell today. |
| `workspace-worker` | apps/workspace-worker | partial | 18 | — | Background jobs: message/event extraction, report generation, notification and outbound delivery, maintenance, scheduling, retry. |
| `ai-gateway` | packages/ai-gateway | contract-only | 22 | cost, termination, data_scope | Provider-neutral model routing, context control, budget, structured output, validation, fallback, kill switch. |
| `channel-sdk` | packages/channel-sdk | contract-only | 12 | — | Shared interface for channel adapters: verify, parse, attachments, send, delivery status, health, credential refresh. |
| `cvf-application-profile` | packages/cvf-application-profile | contract-only | 0 | identity, permission, domain_lock, data_scope, risk, approval, evidence, cost, refusal, termination, freeze | Declarative CVF profile for this application: risk classes, approval, evidence, domain lock, data, cost, refusal, termination, freeze policies. Does not copy CVF core. |
| `cvf-bridge` | packages/cvf-bridge | contract-only | 0 | approval, refusal, evidence, audit | Bridge to CVF policy evaluation, approval gates, refusal, evidence, audit and fallback. |
| `refinery-bridge` | packages/refinery-bridge | contract-only | 0 | data_scope | Boundary to CVF Refinery: normalize, terminology, dedupe, redact, classify, conflict detection, context candidates. |
| `workspace-contracts` | packages/workspace-contracts | contract-only | 0 | — | Canonical JSON Schemas that form the stable boundary between core, providers, channels, Refinery and CVF. |
| `ai-providers` | packages/ai-providers | stub | 0 | provider_authorization | Adapters for NO_AI, RULES_ONLY, OpenAI-compatible, non-compatible, local, enterprise, subscription, and mock providers. |
| `channel-adapters` | packages/channel-adapters | stub | 0 | — | Concrete adapters for internal PWA, customer portal, generic webhook, Zalo, WhatsApp, email, SMS, and mocks. |
| `conversation-routing` | packages/conversation-routing | stub | 0 | domain_lock | Route messages to workspace, shift, vessel, customer, incident, or fallback. |
| `identity-mapping` | packages/identity-mapping | stub | 0 | identity | Map external identities to internal users/customer contacts with human confirmation. |
| `notification-engine` | packages/notification-engine | stub | 0 | — | In-app, push, email, SMS, outbound channels and escalation. |
| `operations-domain` | packages/operations-domain | stub | 0 | — | Domain language and invariants for shift, message, event, task, customer request, incident, handover, report, approval, correction, audit. |
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
- **Metrics:** 793 LOC across 13 code file(s)
- **Next step:** Wire ai-gateway/ai-providers to call data_scope/budget/termination when an AI mode is enabled. Replace known-principals.yaml registry check with real authentication when P2-B is implemented.

### `operations-ledger` — enforced

- **Path:** `packages/operations-ledger` (package)
- **Purpose:** Source-of-truth persistence. Defines the Ledger Protocol and an append-only, dual-backend SqlLedger (SQLAlchemy Core over the existing migration schema; generic Uuid/JSON types work against SQLite or PostgreSQL from the same table definitions). InMemoryLedger (in workspace-api) is the offline/test backend.
- **CVF controls:** evidence, audit, freeze
- **Enforcement:** ledger.py defines the Protocol (including transaction() unit-of-work); sql_ledger.py implements append-only INSERT for corrections/audit and maps tables.py to migrations 001+002; every mutating method accepts an optional unit= connection so callers can chain writes into one real SQL transaction (P-FIX-2). tables.py uses SQLAlchemy generic Uuid + JSON.with_variant(JSONB, 'postgresql') so one schema definition serves both backends, WITH matching FK/CHECK/column-set/nullability verified against the migration (P-FIX-4: tightened test_schema_parity.py compares exact column names and nullability, not just table/FK-table presence; negative-tested by reproducing the tasks.version-missing bug). evidence_links table (P-FIX-3) persists OperationalEvent/Task evidence, written once at creation. make_engine() turns ON SQLite foreign-key enforcement (off by default) so SQLite and PostgreSQL enforce the same integrity. Selected at runtime by workspace-api ledger_factory via DATABASE_URL. Verified end-to-end against SQLite (round-trip across reconnect, FK/CHECK rejection, append-only, atomic rollback on audit failure, evidence round-trip). PostgreSQL round-trip has NEVER been run live in this environment (no Docker daemon) - the known static schema defect is fixed, but this is not the same as a verified live run.
- **Contract:** database/ (schema, migrations, views); operations_ledger.ledger.Ledger
- **Depends on:** `shared-kernel`
- **Tests:** `tests/cvf/test_ledger_protocol.py`, `tests/integration/test_sql_ledger_sqlite.py`, `tests/integration/test_sql_ledger_integrity.py`, `tests/integration/test_schema_parity.py`, `tests/integration/test_evidence_persistence.py`
- **Metrics:** 669 LOC across 6 code file(s)
- **Next step:** Run the same integration + integrity + evidence + parity suite against a real PostgreSQL instance (docker compose up postgres) once available - this is a pre-ship gate, not required for ordinary SQLite-based development. Map remaining migration tables (messages, customer_requests, reports) into tables.py as tranches need them.

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

### `workspace-api` — partial

- **Path:** `apps/workspace-api` (app)
- **Purpose:** FastAPI backend: shifts, messages, operational events, corrections, tasks. Four domains route through the same cvf-runtime gate chain (identity/permission/audit, plus risk/evidence/approval where applicable): event confirmation, post-freeze correction, task create/transition, and shift close/freeze. "Golden vertical" is avoided here per the 2026-07-22 Codex review (docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md): whether a given path is durable/end-to-end depends on ledger backend and risk class - see docs/cvf/CVF_CONTROL_MAPPING.md for the callable/load-bearing/not-verified-server-side distinction per control.
- **CVF controls:** identity, permission, domain_lock, risk, approval, evidence, audit, refusal, freeze
- **Enforcement:** events/router.py + services.py run the confirm chain; corrections/router.py + correction_service.py run the correction chain; tasks/router.py + task_service.py run task create/transition; shifts/router.py + shift_service.py run close/freeze (close requires identity/permission `shift.close` (min role operator) + a state-check rejecting close of an already-FROZEN shift; freeze requires identity/permission/shift_closed + an explicit audited override for the two prerequisites with no model yet). All reuse cvf-runtime gates and depend on the operations-ledger Ledger Protocol (backend via DATABASE_URL). domain/lifecycle.py enforces data-state and task-status transitions. 2026-07-22 (P-FIX-1): both InMemoryLedger and SqlLedger now block add_event/put_event/add_task/put_task when the parent shift is FROZEN (previously only InMemoryLedger blocked new records, and SqlLedger blocked nothing); CorrectionService uses allow_when_frozen=True as the sole permitted post-freeze mutation path. 2026-07-22 (P-FIX-6): shifts/router.py close_shift previously called ledger.close_shift() directly with no identity/permission/audit at all (a second independent review's probe: anonymous close -> 200 CLOSED, audit_count=0, which could silently satisfy freeze's shift_closed prerequisite); now routed through ShiftService.close, same identity -> permission -> state-check -> transaction(mutate+audit) shape as freeze.
- **Contract:** apps/workspace-api/pyproject.toml
- **Depends on:** `cvf-runtime`, `operations-ledger`
- **Tests:** `apps/workspace-api/src/workspace_api/tests/test_lifecycle.py`, `tests/cvf/test_vertical_end_to_end.py`, `tests/cvf/test_correction_vertical.py`, `tests/cvf/test_task_vertical.py`, `tests/cvf/test_freeze_invariant.py`, `tests/cvf/test_atomic_mutation_audit.py`, `tests/cvf/test_approval_known_principals.py`, `tests/cvf/test_shift_close_governance.py`, `tests/integration/test_evidence_persistence.py`
- **Metrics:** 1214 LOC across 41 code file(s)
- **Next step:** P-FIX tranche closed bounded (P-FIX-0 through P-FIX-6). Next: replicate the chain to remaining domains (customer requests, incidents, handovers) per P2-A, or P2-B (real authentication - should replace known-principals.yaml), or P2-C (frontend UI).

### `workspace-web` — partial

- **Path:** `apps/workspace-web` (app)
- **Purpose:** Mobile PWA + Desktop Web operational UI (React/Vite). Minimal shell today.
- **CVF controls:** —
- **Enforcement:** App.tsx shell + api.ts client + offline/queue.ts skeleton; feature folders are stub README only.
- **Contract:** packages/workspace-contracts (JSON schemas)
- **Depends on:** `workspace-contracts`, `workspace-api`
- **Tests:** —
- **Metrics:** 59 LOC across 5 code file(s)
- **Next step:** Build feature verticals matching backend chain, starting with events/approvals.

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

### `ai-gateway` — contract-only

- **Path:** `packages/ai-gateway` (package)
- **Purpose:** Provider-neutral model routing, context control, budget, structured output, validation, fallback, kill switch.
- **CVF controls:** cost, termination, data_scope
- **Enforcement:** contracts/provider_interface.py defines the LLM contract; no router implementation.
- **Contract:** packages/ai-gateway/contracts/provider_interface.py
- **Depends on:** `ai-providers`, `refinery-bridge`
- **Tests:** —
- **Metrics:** 22 LOC across 1 code file(s)
- **Next step:** Implement model router + budget/kill-switch when an AI mode beyond NO_AI is enabled.

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

### `refinery-bridge` — contract-only

- **Path:** `packages/refinery-bridge` (package)
- **Purpose:** Boundary to CVF Refinery: normalize, terminology, dedupe, redact, classify, conflict detection, context candidates.
- **CVF controls:** data_scope
- **Enforcement:** contracts/refinery_contract.yaml only; no runtime bridge.
- **Contract:** packages/refinery-bridge/contracts/refinery_contract.yaml
- **Depends on:** `shared-kernel`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement the refinery boundary before any LLM context is built.

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

### `ai-providers` — stub

- **Path:** `packages/ai-providers` (package)
- **Purpose:** Adapters for NO_AI, RULES_ONLY, OpenAI-compatible, non-compatible, local, enterprise, subscription, and mock providers.
- **CVF controls:** provider_authorization
- **Enforcement:** None yet.
- **Contract:** packages/ai-gateway/contracts/provider_interface.py
- **Depends on:** `ai-gateway`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Implement NO_AI + RULES_ONLY + mock providers first.

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

### `operations-domain` — stub

- **Path:** `packages/operations-domain` (package)
- **Purpose:** Domain language and invariants for shift, message, event, task, customer request, incident, handover, report, approval, correction, audit.
- **CVF controls:** —
- **Enforcement:** None yet. Domain models currently live inline in workspace-api/domain/models.py.
- **Contract:** packages/workspace-contracts
- **Depends on:** `shared-kernel`
- **Tests:** —
- **Metrics:** 0 LOC across 0 code file(s)
- **Next step:** Extract domain models out of workspace-api into this shared package.

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
