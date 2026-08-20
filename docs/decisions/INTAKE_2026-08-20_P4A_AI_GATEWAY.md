# INTAKE — P4-A AI Gateway

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Phase: `INTAKE`
- Risk: `R2`
- Status: `ACCEPTED_FOR_DESIGN`
- Execution base: `a1aeb60f3b4f7ab10959c9b1ab79b5293dec13dd`
- Operator authority: open P4-A and delegate the bounded reference-plan
  decision to the acting `ORCHESTRATOR`; another agent will perform BUILD.
- Active role: `INTAKE_AUTHOR`

## Request and authority boundary

Open only P4-A's provider-neutral AI Gateway foundation and produce a copyable
Work Order for a separate `IMPLEMENTATION_WORKER`. The acting orchestrator may
approve the alternative entry-gate plan, author the authority packet, and later
review the worker return. This delegation does not authorize the orchestrator
to perform BUILD or the worker to commit or push.

## Entry-gate disposition

The planned `LPCI1-REF` external-reference lane remains
`PLANNED_EXTERNAL_REFERENCE_LANE_REQUIRES_SEPARATE_CVF_AUTHORITY`. It is
explicitly replaced for this P4-A tranche by a project-native reference plan:

1. consume the reviewed P4-A1 contracts, receipts, and fail-closed handoff
   semantics already present in this repository;
2. consume the pinned public CVF Core only as read-only governance guidance;
3. reuse existing local live-evidence patterns for secret redaction and
   physical-call accounting;
4. import no external repository code, truth, configuration, deployment,
   database, or secret.

This replacement applies only to P4-A. It does not satisfy or open P4-A2.

## Verified current truth

- `packages/ai-gateway` contains README scaffolds and one provider protocol;
  there is no runtime gateway caller.
- `cvf_runtime.data_scope.assert_placement_allowed`,
  `cvf_runtime.budget.assert_within_budget`, and
  `cvf_runtime.termination.assert_not_terminated` exist and have unit tests,
  but no AI/provider call site invokes them.
- P4-A1 is deterministic and provider-free. Its `FutureContextHandoffV1`
  truth is `minimization_evidence_status=NOT_PROVEN`,
  `placement_enforcement_status=NOT_EVALUATED`,
  `runtime_caller_status=NO_LOAD_BEARING_CALLER`, and zero provider attempts.
- Default application AI mode is `NO_AI`. Provider adapters remain a separate
  P4-B responsibility.
- Data policy allows PUBLIC external use; INTERNAL requires proven
  minimization; CONFIDENTIAL is local/enterprise-only; RESTRICTED is local-only.

## Intended bounded outcome

Build a pure Python `ai_gateway` package with a provider-neutral injected
provider, strict request/result/receipt contracts, context admission,
data-scope/budget/termination gates, a process-local reservation ledger,
structured-output validation, fallback, kill switch, timeout/cancel behavior,
and sanitized evidence. Prove the gate order with pre-call zero-attempt cases
and exactly one admitted PUBLIC canary call through the gateway to a real
provider.

## External effects

BUILD may make exactly one HTTPS provider request to the configured Alibaba
DashScope OpenAI-compatible endpoint after all gates pass. It may read one of
`ALIBABA_API_KEY` or `DASHSCOPE_API_KEY` from the environment without printing,
persisting, hashing, or committing it. No other provider/product endpoint,
credential, database, deployment, message, or public release is authorized.

## Exclusions and claim boundary

- No app/API/UI caller, channel, RAG, vector/hybrid retrieval, citation answer
  validation, application memory, durable usage/audit store, production
  adapter, deployment, or production-readiness claim.
- Do not mutate or reinterpret P4-A1's INTERNAL handoff. It must be refused for
  external placement while minimization remains `NOT_PROVEN`.
- Mock providers may support non-governance component tests only. They may not
  prove gate enforcement or any governance claim.
- P4-B remains open: the live runner's evidence-only adapter is not a production
  provider adapter.

## Stop conditions

Stop before BUILD if the path ceiling or provider-call budget must widen. Stop
during BUILD on a dirty/unexpected base, missing secret, no eligible model,
failed pre-call zero-attempt proof, any physical call before admission, more
than one physical call, invalid/unsanitized evidence, failed required gate,
or need for P4-A2/P4-B/API/database/deployment work.

## Intake disposition

The operator-approved replacement closes the P4-A entry gate within the above
boundary. `INTAKE_AUTHOR → DESIGN_AUTHOR` is authorized; BUILD is not.
