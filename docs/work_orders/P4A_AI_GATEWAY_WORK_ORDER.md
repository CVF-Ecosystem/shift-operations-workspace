# Work Order — P4-A AI Gateway

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Status: `AUTHORIZED_FOR_EXTERNAL_WORKER_BUILD`
- Execution base: `a1aeb60f3b4f7ab10959c9b1ab79b5293dec13dd`
- Parent/role ancestry: `ORCHESTRATOR → INTAKE_AUTHOR → DESIGN_AUTHOR →
  SPEC_AUTHOR → WORK_ORDER_AUTHOR → REVIEWER`
- Authorization disposition: `AUTHORIZATION_REVIEW_PASS`

## Assignment

The receiving agent declares `IMPLEMENTATION_WORKER`, rehydrates current
continuity, acknowledges this Work Order in the active handoff, and implements
only SPEC R1–R15. The worker must not act as reviewer, create the completion
review, commit, push, deploy, or widen scope. The current orchestrator will
perform independent REVIEW after the worker returns.

## BUILD sequence

1. Verify project HEAD is the clean local authorization-packet commit whose
   first parent is the execution base, staged set is empty, Core/manifest/
   binding are equal at `7d9f360a3df11ac998972728000785799399c02b`,
   and doctor has no failure.
2. Implement the strict package/contract and register `packages/ai-gateway/src`
   in root pytest pythonpath.
3. Implement explicit registry, context admission, process-local atomic usage
   ledger, JSON-schema validation, fallback, termination, safe receipts, and
   `AIGateway.execute` in the SPEC order.
4. Add focused contract/unit/integration-support tests. Fakes may test mechanics
   but every such test must state that it is not governance proof.
5. Update bounded truth surfaces and regenerate the catalog; do not claim
   application, durable, P4-B, P4-A2, deployment, or production behavior.
6. Run all non-live required gates before accessing a credential. Any failure
   stops before provider I/O.
7. Run the live evidence script once. It must first prove each refusal has zero
   calls, then allow one PUBLIC canary through the real gateway. Read the secret
   from the environment only; sanitize all artifacts. Do not retry.
8. Write the worker return, synchronize continuity, rerun all local gates that
   do not consume another provider call, verify exact 40 paths and staged zero,
   then stop for REVIEW.

## Exact authority

The exact worker write ceiling is the numbered 40-path list in DESIGN. No
other path may be created, modified, staged, deleted, renamed, or generated.
The worker must not create
`docs/decisions/P4A_AI_GATEWAY_COMPLETION_REVIEW_2026-08-20.md`; that is the
reviewer-owned 41st path.

The only external network authority is one HTTPS POST made by the live runner
through the gateway to the configured Alibaba DashScope OpenAI-compatible
endpoint. Model selection reads the committed local quota catalog. Health
checks, retries, fallback calls, telemetry, package installs, product APIs,
Git network operations, and any second provider request are unauthorized.

## Live-evidence protocol

- Preflight must not reveal whether a credential exists beyond a boolean and
  selected environment-variable name.
- The runner executes zero-call cases for `NO_AI`, no evidence, P4-A1 INTERNAL
  without minimization, RESTRICTED external placement, budget exceeded, and
  active kill switch.
- If all zero-call cases pass, reserve exactly one attempt, choose one eligible
  model, and send a harmless PUBLIC canary requesting a small JSON object under
  a strict schema.
- Increment physical count immediately before I/O. Persist sanitized transition
  facts even if the call times out, errors, or returns invalid JSON.
- Success requires HTTP success, one physical call, matching structured output,
  schema acceptance, committed usage, and no secret/raw content in the receipt.
- Any failure is `LIVE_EVIDENCE_BLOCKED`. Preserve evidence and stop; do not
  make a replacement call without an amended Work Order.

## Stop and repair rules

Stop on base drift, unexpected path, secret exposure, any pre-call attempt,
call count other than one after dispatch, failed test/validator/doctor, stale
catalog, continuity drift, or need for new external effects. Ordinary repairs
inside the same 40 paths and acceptance contract remain under this authority.
At repair round three without a new root cause, record
`REVIEW_COST_ESCALATION_REQUIRED` and stop. Never reset or delete evidence.

## Worker return contract

`docs/decisions/P4A_AI_GATEWAY_WORKER_RETURN_2026-08-20.md` must contain:

- execution base and final unstaged status paths;
- requirement-by-requirement R1–R15 evidence;
- every command and exit code;
- live-call transition/count/status, safe endpoint origin, selected model,
  receipt hash and explicit secret-scan result;
- exact 40-path comparison and staged-zero proof;
- findings, deviations, repairs, and residual claim boundary;
- explicit `READY_FOR_REVIEW` or a named blocked disposition.

## REVIEW and commit boundary

The independent `REVIEWER` reruns all non-consuming checks, validates the live
receipt without making another provider call, inspects source/order/negative
paths, and returns `REVIEW_PASS`, `REVIEW_CHANGES_REQUIRED`, or
`REVIEW_BLOCKED`. Only REVIEW_PASS permits the reviewer-owned completion file
and later FREEZE/commit stewardship. Push is not authorized.
