# Work Order Amendment 1 — P4-A2 Governed RAG Consolidated Repair Round 3

- Tranche: `P4A2-GOVERNED-RAG-2026-08-21`
- Parent Work Order: `docs/work_orders/P4A2_GOVERNED_RAG_WORK_ORDER.md`
- Phase: `WORK_ORDER` amendment after independent `REVIEW`
- Risk ceiling: `R2` (unchanged)
- Execution base: `4016fc6708844ecea1dedc4e76dfccf2ae314c9e`
- Operator authority: explicit approval on `2026-08-21` of the consolidated
  amendment requested after `REVIEW_COST_ESCALATION_REQUIRED`
- Status: `AUTHORIZED_FOR_EXTERNAL_REPAIR_WORKER_ROUND_3`
- Provider/install/database/commit/push/deployment authority:
  `NONE/NONE/NONE/NONE/NONE/NONE`
- Replacement live call: `NOT AUTHORIZED`

## Why this amendment exists

The independent rereview reproduced all non-consuming green gates but found
three residual instances of the same reviewed root causes plus one evidence-
hash labeling defect:

1. `P4A2-REV-F3` remains open because placement is still caller-declared and
   `GovernedRAG` still defaults to `LOCAL`; no registry/adapter-owned fact
   prevents an external provider from being relabeled local.
2. `P4A2-REV-F6` remains open because an `ABSTAINED` receipt with zero physical
   attempts, null minimization/validated-answer lineage and a non-empty
   positive reason code is accepted.
3. `P4A2-REV-F7` remains open because only the first ten P4-A1 stages are
   checked. A coordinated `model_construct` receipt with stage 11
   `RECEIPT_EMITTED=NOT_RUN`, a recomputed public hash and matching handoff is
   accepted by `verify_bindings`.
4. `P4A2-REV-F8` truth is correctly historical/invalidated, but the worker
   return calls the universal-newline hash the document SHA without labeling
   it and omits the raw CRLF hash.

Canonical audit history counts the F1/F2 correction as repair round 1 and the
F3–F8 pass as repair round 2. This amendment is the explicit operator approval
required before repair round 3. It supersedes no source contract and grants no
waiver.

## Required repair contract

### A1-F3 — Registry-owned provider placement

`ProviderRegistry.register` must require an explicit, strict `Placement`
keyword with no default and bind one immutable placement to each registered
provider. Every existing registration call site in the authorized set must
declare `LOCAL`, `ENTERPRISE` or `EXTERNAL` truthfully.

`AIGateway.execute` must compare `GatewayRequest.placement` with the registered
provider placement before context admission and before the real data-scope
gate. A mismatch must return a sanitized, deterministic zero-attempt refusal;
it must not resolve/dispatch the provider, reserve usage or call any provider.
The existing real-gate order among data-scope, budget and termination remains
unchanged. An unknown provider/model retains the existing later registry
refusal and zero-attempt behavior.

`GovernedRAG` must remove its `Placement.LOCAL` default. Construction and the
application composition boundary must require placement explicitly. The
P4-A2 external live-support configuration must register the provider as
`EXTERNAL` and construct the engine with the identical value. A caller that
passes `LOCAL` for that registered external provider must be refused before
dispatch.

Required adversaries include registry/request mismatch in both directions,
missing/non-enum registration placement, duplicate-provider replacement,
unregistered provider/model, real data-scope capture of `EXTERNAL`, and proof
that mismatch produces zero physical calls/reservations.

### A1-F6 — Complete receipt terminal and lineage grammar

Both positive outcomes, `ANSWERED` and `ABSTAINED`, must require:

- every P4-A2 stage `PASS` and an empty receipt reason code;
- exactly one physical attempt;
- non-null minimization ruleset/input/output digests and retained count > 0;
- non-null index, context, output-schema and gateway-request digests;
- non-null gateway-receipt output, provider-response and validated-answer
  digests.

`OUTPUT_VALIDATION_FAILED` must preserve exactly one physical attempt.
`GATEWAY_NOT_ACCEPTED` may preserve zero or one according to the authoritative
gateway receipt. Every pre-gateway outcome remains exactly zero attempts.
Nullable digest/count fields must be coherent with the stage actually reached;
positive reason codes must be empty and negative terminal reason codes must
match the single terminal stage.

Add direct construction, hash-recomputed construction and `model_construct`
revalidation probes for every positive field above, especially `ABSTAINED`.

### A1-F7 — Full P4-A1 nested-model revalidation

Treat the complete supplied P4-A1 positive result as untrusted. Reconstruct
strict upstream models from primitive dumps so their validators execute; do
not call `model_validate` on an existing model instance in a mode that returns
it without revalidation. Independently recompute the downstream-used receipt,
projection, handoff, citation, size/token, sensitivity and hash facts.

Require all eleven positive P4-A1 stages to satisfy the upstream grammar,
including `RECEIPT_EMITTED=PASS`. Add coordinated `model_construct`
adversaries for stage 11, receipt outcome/reason, nested projection fields,
hash-recomputed receipt and shallow-equality-updated handoff. Every invalid
positive object must fail before index/context/gateway work with zero calls.

### A1-F8 — Historical receipt hash truth

Do not alter or rerun
`docs/decisions/P4A2_GOVERNED_RAG_LIVE_EVIDENCE_RECEIPT.md`. Record both:

- raw on-disk CRLF SHA-256:
  `2771c4b8fefa447021d2c7e2ace5720baffaf409ab178a0bc54f48d3230bfbc4`;
- universal-newline LF SHA-256:
  `82f65a984520897fc39fac74e88fcae2b63c9723ce8b99fbdca97a52f2420aa1`.

Continue labeling the artifact
`HISTORICAL_INVALIDATED_FOR_FINAL_ACCEPTANCE`. Its internal
`LIVE_EVIDENCE_PASS` text is historical only and does not prove repaired
source.

## Exact authority expansion

The original 50 worker paths remain authorized for this repair. This
amendment adds exactly these eight existing P4-A parent paths:

1. `packages/ai-gateway/src/ai_gateway/errors.py`
2. `packages/ai-gateway/src/ai_gateway/registry.py`
3. `packages/ai-gateway/src/ai_gateway/service.py`
4. `tests/unit/test_p4a_gateway_registry.py`
5. `tests/unit/test_p4a_gateway_dependency_boundaries.py`
6. `tests/unit/test_p4a_gateway_receipts.py`
7. `scripts/_p4a_gateway_live_evidence_support.py`
8. `scripts/run_p4a_gateway_live_evidence.py`

No other path is writable. The original immutable authorization artifacts,
this amendment and the reviewer-owned completion review are read-only to the
worker.

Before worker action, the exact status set is the prior 57-path union plus
this amendment record: `58` paths. The required repair return set is exactly
those 58 plus all eight expansion paths: `66` paths. Unexpected/missing paths
must be `0/0`, staged paths `0`, and HEAD must remain the execution base.

Only an independent `REVIEW_PASS` may add path 67:
`docs/decisions/P4A2_GOVERNED_RAG_COMPLETION_REVIEW_2026-08-21.md`.

## Required verification

Use only:
`C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv\Scripts\python.exe`
(Python `3.13.12`, Pydantic `2.10.6`). No installation is authorized.

Run and record exact commands/exits for:

1. all P4-A2 focused tests;
2. all P4-A1/P4-A focused tests, including the expanded P4-A files;
3. the complete repository suite;
4. the specific reviewer probes described in A1-F3/A1-F6/A1-F7;
5. session/mirror, Project Knowledge, catalog, file-size, repository, changed-
   JSON, diff, staged-zero, exact-path, secret-scan and workspace-doctor gates.

All new refusal/adversarial tests must assert zero gateway/provider physical
attempts. Do not run either P4-A or P4-A2 live-evidence runner; they are source
surfaces to update and test mechanically only.

## Worker return and stop condition

A separate agent must declare `REPAIR_WORKER`, acknowledge this amendment in
the active handoff before editing, and amend the existing P4-A2 worker return.
Correct stale test counts and distinguish raw from universal-newline receipt
hashes. Return only `READY_FOR_REREVIEW_ROUND_3` or a precise blocker.

The worker must not self-review, create path 67, call a provider, install,
commit, push, deploy, use a secret, widen the path set or declare FREEZE/
`CLOSED_BOUNDED`/load-bearing completion. Independent `REVIEWER` action is
required after return. A replacement post-repair live call remains a separate
operator checkpoint after non-consuming `REVIEW_PASS`.
