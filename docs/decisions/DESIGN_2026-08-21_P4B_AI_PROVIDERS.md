# DESIGN — P4-B AI Provider Foundation

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Phase: `DESIGN`
- Risk: `R2`
- Author: `DESIGN_AUTHOR`
- Execution base: `319c6a8`

## Decision

Create a pure `ai-providers` Python package and one no-route application
composition. `ProviderModeService.execute` owns mode selection. It complements
P4-A without becoming a second external dispatch point: external work is
delegated exactly once to an injected `AIGateway`; this package performs no
HTTP, SDK, environment, credential, database or filesystem I/O.

## Closed mode behavior

The service consumes P4-A's canonical `AIMode` enum.

- `NO_AI`: return `AI_MODE_DISABLED`, no rules/gateway/provider attempt.
- `RULES_ONLY`: evaluate a local immutable rule set once; no gateway/provider
  attempt. A no-match returns `RULES_NO_MATCH` without fabricated content.
- `EXTERNAL_AI`: accept only a strict P4-A `GatewayRequest` whose mode,
  provider/model and placement match the outer request, then call the injected
  gateway exactly once and preserve its accepted/refused outcome.

No caller string, registry label or mock object may introduce another mode.

## Deterministic rules

`RuleDefinitionV1` binds id, task type, integer priority, exact required facts
and a JSON object output. Facts and outputs are JSON-only and size/depth
bounded. Eligible rules require task equality and exact scalar fact matches;
winner order is `(-priority, rule_id)`. Duplicate ids or indistinguishable
priority/match signatures fail at construction. Output is validated using the
real P4-A JSON-schema validator before release. No regex, code execution,
template expansion, clock, randomness or I/O is allowed in this tranche.

## Test-only mock

`MockProviderAdapter` structurally implements P4-A `AIProvider` for component
and integration tests. Construction requires a strict
`TEST_ONLY_COMPONENT_TEST` authorization object whose `evidence_eligible`
field is immutably false. Its responses are fixed deep-copied primitives; it
tracks calls/cancellation deterministically and never performs network I/O.

`ProviderAdapterRegistry` owns provider kind and placement metadata. Mock
registration is denied by default and requires explicit `allow_test_only=True`.
Production/evidence registry projection always excludes mocks. A mock receipt
or result is never accepted as governance proof.

## Receipts

`ProviderModeReceiptV1` contains safe enums/ids, policy/schema/request/output
digests, rule id when applicable, gateway-call count, physical provider-attempt
count copied from the gateway receipt, outcome/reason and timestamps supplied
by the caller. It contains no context, facts, rule output, prompt, response,
credential, endpoint query or raw exception. Receipt digest is recomputable
from its canonical body.

## Application composition

`workspace_api.application.ai_provider_modes` builds the mode service from
explicit dependencies. It opens no HTTP route, reads no environment, persists
nothing and owns no provider credential. Existing P4-A2/P4-A3 composition may
call it only in a future separately authorized wiring tranche; no implicit
rewiring occurs here.

## Evidence

BUILD uses no provider/network call. Tests prove mode isolation, zero calls,
deterministic winner selection, schema rejection, mock default denial,
identity binding, at-most-one external gateway call, receipt recomputation and
dependency bans. Runner mechanics rehearse refusal/rules/mock-test cases
without consuming live authority.

After independent non-consuming review, a separate operator checkpoint may
authorize one synthetic real-provider call: all `NO_AI`, `RULES_ONLY`, invalid
external and mock-evidence cases must remain zero-call; one admitted
`EXTERNAL_AI` case may reach the real provider at most once through P4-A.

## Claim boundary

Provider-mode foundation only. No production/vendor adapter, automatic
routing, retries, durable accounting/audit, public route, deployment or
production readiness.
