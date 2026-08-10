# P4-A1 Governed Retrieval Foundation Build Rereview 2

- Date: `2026-08-10`
- Role: `INDEPENDENT_BUILD_REVIEWER_CLOSER`
- Risk ceiling: `R2`
- Disposition: `REPAIR_2_REVIEW_CHANGES_REQUIRED`
- Findings: `6 MATERIAL`
- Waivers: `NONE`

## Reviewed Authority

| Artifact | SHA-256 |
|---|---|
| Main SPEC | `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` |
| Receipt appendix | `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` |
| Parent Work Order | `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6` |
| Work Order Amendment 1 | `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1` |
| Repair rereview 1 | `cadead0315517519ea66d95438bc18a5f9e5be2f9510a12d3c6216b87bb062ea` |
| Work Order Amendment 2 | `4bd2f9a7d6252a7d8970fd8b86cc1e052c89b4ae4adc608a65ed9fd14d3a39ee` |
| Amendment 2 review | `f93143022d3cd0b8e6a9be3db1c4ff62f03d5b502e747d1a9487da2e1245ea0c` |

Review baseline and current HEAD are both
`d878001b6a1a536218b2c66019243510ef3f7aec`. The worker did not commit or
stage. This review adds only this reviewer-owned decision artifact.

## Decision

The Repair 2 candidate is not accepted. The focused suite and the bounded
repository controls pass, but direct source inspection and independent
adversarial probes reproduce material contract failures that the current tests
do not cover. Catalog closure must not run while these semantic findings remain
open.

## Reproduced Verification

| Check | Result | Evidence |
|---|---|---|
| focused exact P4-A1 suite | `PASS` | `150 passed, 1 warning` |
| Project Knowledge suite | `PASS` | `77 passed` |
| diagnostic sanitized non-live remainder | `PASS` | `1831 passed, 128 skipped, 1 deselected` |
| full sanitized non-live suite | `BLOCKED_EXPECTED_EXTERNAL_OR_CLOSURE` | `1831 passed, 128 skipped`; remaining failures/errors derive only from reviewer-owned catalog truth and hidden-core pin mismatch |
| file-size guard | `PASS` | every touched Python file is at or below 300 lines; maximum is 259 |
| Project Knowledge checker | `PASS` | repository-local checker |
| session-state checker | `PASS` | canonical state and compatibility mirror agree |
| catalog check | `FAIL_PENDING_REVIEWER_CLOSURE` | source-derived metrics and generated catalog truth remain stale |
| repository validator | `FAIL_CATALOG_ONLY` | catalog failure propagates |
| diff check | `PASS` | line-ending warnings only |
| exact32 | `PASS` | 32 of 32 paths present; no candidate path outside the ceiling |
| protected Phase A paths | `PASS` | all six exact hashes match |
| protected 15-row aggregate | `PASS` | `bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7` |
| current HEAD and staging | `PASS` | HEAD unchanged; staged file count zero before this review artifact |

One concurrent diagnostic run observed a transient Project Knowledge failure
while another independent full-suite process was executing catalog-drift
negative tests against the same worktree. Immediate isolated rerun passed and
the protected hashes remained exact. The serial diagnostic result above is the
accepted evidence; the cross-process observation is not classified as a
worker defect.

## Findings

### P4A1-RR2-F1 - Positive result integrity remains forgeable

Severity: `HIGH`. Parent finding: `P4A1-RR1-F6`.

`packages/governed-retrieval/src/governed_retrieval/result_models.py:47-75`
binds citation order and selected handoff fields but does not independently
recompute the evidence-set hash, serialized context bytes, token estimate, or
bind `receipt.counts.projections_emitted`.

Independent probes accepted all of these invalid constructions:

- coordinated bogus receipt and handoff evidence hashes after recomputing only
  the receipt hash;
- `serialized_context_bytes` differing from the canonical projection tuple;
- `estimated_input_tokens` differing from the declared estimate method; and
- handoff or receipt projection-count facts differing from the projections.

This violates Amendment 2 section 5.5 and SPEC R9/R10.

### P4A1-RR2-F2 - Project Knowledge admission remains shape-unsafe

Severity: `HIGH`. Parent findings: `P4A1-RR1-F3`, `P4A1-RR1-F4`.

`apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py:80-99`
checks only that the top-level value is a mapping and that the entry ceiling is
not exceeded. It does not enforce the manifest owner's exact top-level shape.
Lines 102-107 accept an unknown non-empty owner; lines 121-131 permit an
in-root symlink; and lines 159-163 can raise raw `TypeError` for malformed
consumer values.

The initial and use-time callers catch only selected exception classes. Probes
accepted an incomplete manifest with an extra field and reproduced raw
`TypeError` leakage from malformed `allowedConsumers`. Use-time P3-A/P3-C or
unexpected manifest failures can therefore escape instead of becoming a typed
result or stale omission. This violates Amendment 2 section 5.3.

### P4A1-RR2-F3 - Service-owned identity and timing are incomplete

Severity: `HIGH`. Parent finding: retained F11.

`apps/workspace-api/src/workspace_api/application/governed_retrieval.py:93-105`
runs structural validation before constructing the execution context. The two
UUID factory calls and start-clock call therefore occur after R2, contrary to
Amendment 2 section 5.6.

`packages/governed-retrieval/src/governed_retrieval/receipt_models.py:54-70`
checks that each identity is UUIDv4 but does not require the two identities to
be distinct. It also accepts positive elapsed time with identical start and
finish timestamps. Direct probes reproduced all three conditions.

### P4A1-RR2-F4 - Final-stop stage receipt is not truthful

Severity: `HIGH`. Parent findings: `P4A1-RR1-F7`, `P4A1-RR1-F8`.

The final stop check uses `RECEIPT_EMITTED` at
`apps/workspace-api/src/workspace_api/application/governed_retrieval.py:269-275`.
`apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py:94-114`
records that stage as `FAIL` and immediately overwrites the same stage as
`PASS`.

A cancellation triggered only at the third and final checkpoint correctly
suppressed evidence, but its returned receipt recorded all eleven stages as
`PASS`. No terminal `FAIL` remained to explain the stopped outcome. This
violates Amendment 2 section 5.6 and the receipt appendix stage language.

### P4A1-RR2-F5 - Negative receipt schemas accept impossible histories

Severity: `MEDIUM`. Parent findings: `P4A1-RR1-F6`, `P4A1-RR1-F7`.

`packages/governed-retrieval/src/governed_retrieval/receipt_models.py:49-91`
does not bind a negative final outcome to the required first terminal
`FAIL`/`DENY` and subsequent `NOT_RUN` stages. The shared test fixture creates
negative receipts with every stage set to `PASS`, so construction of all result
variants does not prove the normative negative receipt contract.

### P4A1-RR2-F6 - Required adversarial proof is incomplete

Severity: `MEDIUM`. Parent finding: `P4A1-RR1-F9`.

The current suite does not directly prove:

- unfit-first and fitting-second projection replacement;
- coordinated evidence-hash, byte, token, and count mismatch rejection;
- exact manifest shape, malformed consumer, owner allowlist, and symlink
  rejection;
- duplicate UUID rejection and service allocation before R2;
- elapsed and wall-clock consistency;
- final pre-emission stop stage truth; and
- structurally valid negative receipt stage histories for all variants.

The green focused suite is retained as regression evidence, not acceptance of
the missing proof.

## Closed Findings Retained

The rereview independently accepts the following Repair 2 improvements:

- canonical authentication calls `get_principal` and P4-A1 does not directly
  call `decode_access_token`;
- authentication, permission, single transaction, assignment, and corpus
  resolution remain in the required order;
- corpus registry immutability and lifecycle narrowing are enforced;
- both operational corpora remain dependency-blocked;
- exact retention literal and current raw-byte pin comparison are present;
- later-fit projection scanning traverses the complete survivor window;
- applied limits, source cutoff, no-evidence and stale terminal behavior are
  improved; and
- no provider, audit, API route, UI, operational-corpus positive adapter, or
  deeper project surface was added.

No closed item waives an open finding.

## Review Cost Telemetry And Stop Disposition

Review-Cost Telemetry: REQUIRED

| Field | Value |
|---|---|
| `reviewRoundCount` | `3` |
| `workerRepairTurnCount` | `2` |
| `newRootCauseCountThisRound` | `0` |
| `dependentFindingCountThisRound` | `6` |
| `elapsedReviewMinutes` | `NOT_AVAILABLE_WITH_REASON: cross-agent elapsed-time accounting is not exposed as one authoritative value` |
| `providerCallCount` | `0` |
| `tokenOrQuotaUsage` | `NOT_AVAILABLE_WITH_REASON: provider-neutral token accounting is unavailable` |
| `valueDelta` | The round preserves protected-state integrity and closes several source defects, but six dependent contract and proof gaps still block acceptance. |
| `stopDisposition` | `REVIEW_COST_ESCALATION_REQUIRED` |
| `preRepairAuditDisposition` | `COMPLETE_BEFORE_FIRST_REPAIR` |
| `materialCommitCount` | `0` |
| `continuityCommitCount` | `0` |
| `commitPlanDisposition` | `NO_COMMIT_REVIEW` |
| `latencyDisposition` | `EXPECTED_LONG_RUNNING_PROOF` |
| `avoidableDelayClass` | `SEQUENTIAL_FINDING_CASCADE` |

This stop disposition does not waive a defect. A third repair turn requires a
fresh operator release or newly evidenced critical contradiction under the
round-three rule.

## Dual Agent Surface Matrix

| Consumer class | Interface or owner surface | Authority and risk boundary | Evidence | Adapter boundary | Disposition |
|---|---|---|---|---|---|
| `INTERNAL_AGENT` | provider-free P4-A1 package and application composition | local R2 exact32 only; no commit or external effect | source, focused tests, serial diagnostic suite, and adversarial probes above | internal-only application function; no external adapter | `CONTRACT_ONLY` |
| `EXTERNAL_AGENT_CLI_MCP` | no interface exists in P4-A1 | CLI/MCP ingress, authentication, action, and receipt transport remain outside this tranche | no source path or runtime proof exists | no adapter is authorized; later work requires separate design and work order | `N/A_WITH_REASON` |

## Next Allowed Move

Stop at `REVIEW_COST_ESCALATION_REQUIRED`. The operator may either:

1. authorize one final consolidated Repair 3 packet limited to the existing
   exact32 paths and all six findings above; or
2. park P4-A1 without acceptance.

No repair begins from this review alone. Catalog generation,
implementation-status update, knowledge/session sync, commit, push, FREEZE,
provider or external service use, core-pin change, P4-A, P4-A2, and deeper
project development remain unauthorized.

## External-Effect Accounting

| Surface | Count |
|---|---:|
| Provider calls | 0 |
| Network calls | 0 |
| Product API calls | 0 |
| External database calls | 0 |
| Audit writes | 0 |
| Runtime or test source files modified by reviewer | 0 |
| Review artifacts authored | 1 |
| Files staged | 0 |
| Commits | 0 |
| Pushes | 0 |

## Claim Boundary

This review evaluates only the provider-free, INTERNAL/LOCAL_ONLY P4-A1
foundation candidate. It does not claim an LLM answer path, full RAG, vector
search, durable audit, persistence, operational-corpus retrieval, production
API/UI, live deployment, external-agent interface, LPCI1-REF completion, P4-A,
P4-A2, or deeper project readiness.

## Final Disposition

`REPAIR_2_REVIEW_CHANGES_REQUIRED`

The candidate remains in REVIEW and must not proceed to closure or FREEZE.
