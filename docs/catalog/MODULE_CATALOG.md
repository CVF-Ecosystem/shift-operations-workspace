# Module Catalog

> GENERATED FILE — do not edit by hand. Source of truth is [`MODULE_REGISTRY.json`](MODULE_REGISTRY.json). Run `python scripts/generate_catalog.py --write` to regenerate.

_Last generated: 2026-07-21T00:12:28.968794+00:00_

## How to use this catalog

- **Before working:** find the module you will touch and read its `purpose`, `status`, `cvf_controls`, and `enforcement`.
- **After completing a piece:** update that module's entry in `MODULE_REGISTRY.json` (status, enforcement, next_step, tests), then run the generator to refresh this file and the metrics.
- **Size metrics are computed**, not written — they cannot lie about how much code exists.

## Totals

- Modules: **20**
- Code LOC (py/ts/tsx): **1944**
- Code files: **82**
- By status: contract-only=6, enforced=1, partial=5, stub=8

## Status legend

- **enforced** — Runtime code exists AND is covered by tests that block on violation.
- **partial** — Some runtime code exists but the intended capability/chain is incomplete.
- **contract-only** — Only an interface, schema, or policy YAML exists; no runtime behaviour.
- **stub** — Only README and/or empty __init__.py; no code and no contract.
- **empty** — Directory reserved by the frozen blueprint; nothing implemented yet.

## Modules

| Module | Path | Status | LOC | CVF controls | Purpose |
|---|---|---|---:|---|---|
| `cvf-runtime` | packages/cvf-runtime | enforced | 744 | identity, permission, domain_lock, data_scope, risk, approval, evidence, audit, cost, refusal, termination, freeze | Runtime enforcement of the CVF application profile: reads the profile YAML and exposes all 12 required_controls as callable gates. |
| `integration-edge` | apps/integration-edge | partial | 60 | data_scope, refusal | Channel Integration Edge: webhook gateway with signature verification, dedup, raw-payload preservation before any business system sees external input. |
| `operations-ledger` | packages/operations-ledger | partial | 347 | evidence, audit, freeze | Source-of-truth persistence. Defines the Ledger Protocol and an append-only SqlLedger (SQLAlchemy Core over the existing migration schema). InMemoryLedger (in workspace-api) is the offline/test backend. |
| `workspace-api` | apps/workspace-api | partial | 682 | identity, permission, domain_lock, risk, approval, evidence, audit, refusal, freeze | FastAPI backend: shifts, messages, operational events, corrections. Hosts two CVF golden verticals: event confirmation and post-freeze correction. |
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
- **Tests:** `tests/cvf/test_gates_unit.py`, `tests/cvf/test_vertical_end_to_end.py`, `tests/cvf/test_remaining_controls.py`
- **Metrics:** 744 LOC across 13 code file(s)
- **Next step:** Wire ai-gateway/ai-providers to call data_scope/budget/termination when an AI mode is enabled.

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

### `operations-ledger` — partial

- **Path:** `packages/operations-ledger` (package)
- **Purpose:** Source-of-truth persistence. Defines the Ledger Protocol and an append-only SqlLedger (SQLAlchemy Core over the existing migration schema). InMemoryLedger (in workspace-api) is the offline/test backend.
- **CVF controls:** evidence, audit, freeze
- **Enforcement:** ledger.py defines the Protocol; sql_ledger.py implements append-only INSERT for corrections/audit and maps tables.py to migration 001. Selected at runtime by workspace-api ledger_factory via DATABASE_URL. Structural conformance is tested; live PostgreSQL round-trip is not yet covered.
- **Contract:** database/ (schema, migrations, views); operations_ledger.ledger.Ledger
- **Depends on:** `shared-kernel`
- **Tests:** `tests/cvf/test_ledger_protocol.py`
- **Metrics:** 347 LOC across 4 code file(s)
- **Next step:** Add a DB-backed integration suite (docker compose postgres) to exercise SqlLedger round-trips; wire messages persistence.

### `workspace-api` — partial

- **Path:** `apps/workspace-api` (app)
- **Purpose:** FastAPI backend: shifts, messages, operational events, corrections. Hosts two CVF golden verticals: event confirmation and post-freeze correction.
- **CVF controls:** identity, permission, domain_lock, risk, approval, evidence, audit, refusal, freeze
- **Enforcement:** api/events/router.py + application/services.py run the confirm chain; api/corrections/router.py + application/correction_service.py run the correction chain; both reuse cvf-runtime gates and depend on the operations-ledger Ledger Protocol (backend chosen by ledger_factory via DATABASE_URL). domain/lifecycle.py enforces data-state transitions.
- **Contract:** apps/workspace-api/pyproject.toml
- **Depends on:** `cvf-runtime`, `operations-ledger`
- **Tests:** `apps/workspace-api/src/workspace_api/tests/test_lifecycle.py`, `tests/cvf/test_vertical_end_to_end.py`, `tests/cvf/test_correction_vertical.py`
- **Metrics:** 682 LOC across 38 code file(s)
- **Next step:** Wire remaining routers (approvals, tasks, incidents, customer requests) through the same chain; replace InMemoryLedger with operations-ledger.

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
