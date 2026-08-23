# INTAKE — P4-B AI Provider Foundation

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Phase: `INTAKE`
- Risk: `R2`
- Author: `INTAKE_AUTHOR`
- Authority: operator requested the next roadmap tranche after P4-A3 was
  committed and pushed at `319c6a8`
- BUILD authority: `NOT GRANTED`

## Intent

Replace the P4-B README-only provider-mode scaffold with a provider-neutral,
fail-closed foundation for `NO_AI`, `RULES_ONLY` and test-only mock behavior,
while preserving P4-A `AIGateway` as the sole external-provider dispatch
point.

## Entry boundary

`NO_AI` must return a typed zero-call refusal. `RULES_ONLY` may execute only a
deterministic local rule set and must call neither gateway nor provider. A mock
adapter is test-only, evidence-ineligible and disabled by default. Any
`EXTERNAL_AI` execution must delegate to an injected real P4-A gateway; this
tranche does not implement vendor HTTP, credentials or SDK integration.

## In scope

- pure `packages/ai-providers` contracts, mode router, deterministic rules,
  test-only mock adapter, registry metadata and sanitized receipts;
- one no-route application composition with explicit dependency injection;
- strict unit/contract/integration/CVF tests and non-consuming live-runner
  mechanics;
- project-native P4-A/P4-A2/P4-A3 contracts and accepted reviews as references.

## Out of scope

- production/vendor provider adapters, HTTP clients, SDKs, credentials,
  environment-secret reads, subscription connectors or automatic discovery;
- public API/UI, database/durable usage or audit, retries, deployment, commit
  or push;
- using mock output as governance evidence or claiming production readiness.

## Acceptance direction

Fail closed on unknown modes/providers, mock registration outside an explicit
test policy, nondeterministic or schema-invalid rules output, identity drift,
and any attempt to bypass `AIGateway` for external dispatch. BUILD has zero
provider calls. Any routing-governance closure requires a separately
authorized post-review real-provider call; the mock never qualifies.

## Initial disposition

`READY_FOR_CONSOLIDATED_INTAKE_REVIEW`; DESIGN and BUILD remain unauthorized.
