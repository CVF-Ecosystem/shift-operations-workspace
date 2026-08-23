# SPEC — P4-B AI Provider Foundation

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Version: `1.0`
- Risk: `R2`
- Execution base: `319c6a8`

## Requirements

R1. Public Pydantic models are strict, frozen and extra-forbid. P4-B imports
P4-A's canonical `AIMode`, `Placement`, `GatewayRequest`, `GatewayResult`,
`ProviderRequest`, `ProviderResult` and `AIProvider`; it does not duplicate or
relax those types. All untrusted nested objects are reconstructed from
primitive dumps before use.

R2. `ProviderModeService.execute` is the sole mode-selection entry point and
uses this exact order: request validation → mode selection → local policy or
external identity binding → execution/delegation → output validation →
sanitized receipt. Each execution reaches exactly one terminal outcome.

R3. `NO_AI` returns `AI_MODE_DISABLED`, no output and counters
`rules/gateway/provider = 0/0/0`. It does not resolve a provider or evaluate a
rule, even when such dependencies were supplied.

R4. `RULES_ONLY` never calls gateway/provider. Rule facts and output contain
only bounded JSON primitives/containers: maximum depth 8, 100 keys/items per
container and 16 KiB canonical JSON each. Rule matching is task equality plus
exact scalar required-fact equality. Winner order is `(-priority, rule_id)`;
no match returns `RULES_NO_MATCH` with zero output.

R5. Duplicate rule ids and duplicate `(task_type, priority, required_facts)`
signatures fail at immutable rule-set construction. The winning output is
deep-copy isolated and validated by the real `ai_gateway.validation` function
against the request schema. Invalid output returns `RULES_SCHEMA_INVALID` and
never falls through to external AI.

R6. `EXTERNAL_AI` requires one nested strict `GatewayRequest` whose task,
mode, provider, model, placement, output schema and relevant digests match the
outer request. Mismatch is zero-call. A valid request invokes the injected
gateway exactly once; P4-B never calls an `AIProvider` directly and preserves
the gateway result without retry or fail-open fallback.

R7. `MockProviderAdapter` requires an explicit immutable authorization purpose
`TEST_ONLY_COMPONENT_TEST` and `evidence_eligible=false`. Responses are fixed,
bounded, deep-copy isolated primitives. It tracks calls/cancel deterministically
and performs no network. Missing/invalid authorization fails construction.

R8. `ProviderAdapterRegistry` owns immutable provider kind, placement and model
metadata. Duplicate/relabel registration fails closed. Mock registration is
denied unless `allow_test_only=True`; production/evidence projections exclude
all mock entries regardless of caller labels.

R9. Receipts bind policy version, request/schema/ruleset/output digests, safe
provider/model/rule ids, mode, outcome/reason and exact local/gateway/provider
counters. Their digest is recomputed from the canonical receipt body. They
contain no facts/context/rule output/prompt/provider output, credential,
authorization header, endpoint query or raw exception.

R10. Package source imports no workspace application, provider SDK, HTTP
client, socket, environment, filesystem, database or hidden Core. The
application composition opens no route, reads no environment, persists
nothing and uses explicit dependency injection only.

R11. Tests cover primitive reconstruction and `model_construct` adversaries,
unknown modes/fields, JSON depth/size, ambiguous rules, deterministic order,
schema-invalid local output, mutation aliasing, mock relabel/evidence attempts,
external identity mismatch, gateway exception/timeout results, exact counters,
receipt recomputation and dependency imports.

R12. BUILD provider/network/install/database/commit/push/deployment counts are
zero. The runner is rehearsal-only. Any final routing-governance claim requires
separate post-review authority for one real-provider call; every refusal,
rules-only and mock-evidence case must remain zero-call.

## Acceptance criteria

- AC1: R1-R11 focused unit/contract/integration/CVF tests pass.
- AC2: all `NO_AI`, `RULES_ONLY` and pre-delegation refusals prove zero gateway
  and zero physical provider attempts.
- AC3: one admitted external case invokes the injected gateway at most once;
  BUILD uses a mechanical spy, never a provider call.
- AC4: mock is default-denied and structurally impossible to mark
  evidence-eligible through validated public models.
- AC5: P4-A/P4-A2/P4-A3 focused regressions and the full suite pass.
- AC6: catalog, session, Project Knowledge, file-size, repository, JSON, diff,
  exact-path, staged and secret-scan gates plus workspace doctor pass.
- AC7: worker returns exact commands/results at path 50 and stops at
  `READY_FOR_REVIEW`; reviewer-only completion evidence is not worker-authored.

## Exclusions

No production/vendor adapter, HTTP/SDK/credential integration, automatic
provider discovery/routing, retry, durable usage/audit, database, public
API/UI, deployment or production-readiness claim.
