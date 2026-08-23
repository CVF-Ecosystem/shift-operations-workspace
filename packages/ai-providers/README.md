# ai-providers

Pure P4-B provider-mode foundation (tranche `P4B-AI-PROVIDERS-2026-08-21`).

`ProviderModeService.execute` is the sole mode-selection entry point: request
validation, mode selection, local policy or external identity binding,
execution/delegation, output validation, sanitized receipt - in that exact
order. Depends only on the standard library, Pydantic, and `ai-gateway` (for
the canonical `AIMode`/`Placement`/`GatewayRequest`/`GatewayResult`/
`ProviderRequest`/`ProviderResult`/`AIProvider` types this package reuses
rather than duplicates or relaxes). Imports no provider SDK, HTTP client,
socket, environment, filesystem, database, or hidden CVF Core.

## What this package does

1. **`NO_AI`** - returns `AI_MODE_DISABLED` with zero output and exact
   `rules/gateway/provider = 0/0/0` counters. Never resolves a provider or
   evaluates a rule, even when such dependencies exist elsewhere in the
   process; `evaluate_no_ai` takes no such arguments at all.
2. **`RULES_ONLY`** - evaluates an immutable `RuleSetV1` once. Facts and
   output are bounded JSON only (max depth 8, max 100 keys/items per
   container, max 16 KiB canonical JSON). Duplicate rule ids and duplicate
   `(task_type, priority, required_facts)` signatures fail at rule-set
   *construction*, never at match time. Matching is task equality plus exact
   scalar required-fact equality; winner order is `(-priority, rule_id)`. A
   winning output is deep-copy isolated and validated by the real
   `ai_gateway.validation.validate_output` function; invalid output returns
   `RULES_SCHEMA_INVALID` and never falls through to external AI. No match
   returns `RULES_NO_MATCH` with zero output. Never calls a gateway/provider.
3. **`EXTERNAL_AI`** - requires one nested strict `GatewayRequest` (rebuilt
   from its primitive dump, never trusted as an already-validated instance)
   whose task, mode, and output schema match the outer request; any mismatch
   is a zero-call `EXTERNAL_IDENTITY_MISMATCH` refusal. A valid request
   invokes the injected gateway's `execute` exactly once and preserves its
   accepted/refused outcome without retry or fail-open fallback. This
   package never calls an `AIProvider` directly and never constructs a
   second gateway.
4. **`MockProviderAdapter`** - a test-only, structural `AIProvider`
   implementation. Construction requires an explicit, immutable
   `MockAuthorizationV1` whose `purpose` equals exactly
   `TEST_ONLY_COMPONENT_TEST` and whose `evidence_eligible` is exactly
   `False` - the model's own validators make any other value fail
   construction. Responses are fixed, bounded, deep-copy isolated
   primitives; calls/cancels are tracked deterministically; no network.
5. **`ProviderAdapterRegistry`** - owns immutable provider kind/placement/
   model metadata. Duplicate/relabel registration fails closed. `MOCK`
   registration is denied unless `allow_test_only=True`. Both
   `production_projection` and `evidence_projection` structurally exclude
   every `MOCK` entry, regardless of any caller-supplied label.
6. Every execution emits a sanitized `ProviderModeReceiptV1` binding policy
   version, request/schema/ruleset/output digests, safe provider/model/rule
   ids, mode, outcome/reason, and exact counters. Its `receipt_hash_sha256`
   is independently recomputed by the model's own validator from the
   canonical dump of every other field.

## What this package does not do

It does not open an HTTP route, read the environment, or persist any state
(`apps/workspace-api/src/workspace_api/application/ai_provider_modes.py` is
the sole application composition point, and it does none of those either).
It implements no production/vendor provider adapter, no automatic provider
discovery/routing, no retry, and no durable usage/audit accounting. See
`docs/specs/P4B_AI_PROVIDERS_SPEC.md` and
`docs/decisions/DESIGN_2026-08-21_P4B_AI_PROVIDERS.md` for the full
requirement and architecture set this package satisfies.

## Claim boundary

This package proves a bounded provider-mode foundation: zero-call `NO_AI`,
deterministic local `RULES_ONLY`, a default-denied evidence-ineligible mock,
and at-most-once `EXTERNAL_AI` delegation to an injected P4-A gateway. It
does not prove a production/vendor adapter, automatic routing, durable
usage/audit, a public API/UI, deployment, or production readiness. Mock
output is never governance evidence; any real-provider governance claim
requires separate, non-consuming, post-review authority for exactly one
synthetic real-provider call.
