# P4-A1 Governed Retrieval Foundation Build Rereview 3

- Date: `2026-08-10`
- Role: `INDEPENDENT_BUILD_REVIEWER_CLOSER`
- Risk ceiling: `R2`
- Disposition: `REPAIR_3_REVIEW_CHANGES_REQUIRED`
- Findings: `4 HIGH, 1 MEDIUM`
- Waivers: `NONE`

## Reviewed Authority

| Artifact | SHA-256 |
|---|---|
| Main SPEC | `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` |
| Receipt appendix | `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` |
| Parent Work Order | `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6` |
| Work Order Amendment 1 | `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1` |
| Work Order Amendment 2 | `4bd2f9a7d6252a7d8970fd8b86cc1e052c89b4ae4adc608a65ed9fd14d3a39ee` |
| Repair rereview 2 | `bbe16df476d303acb365d5bf32ea4469d5f61714c3a1fc892c9c6c412e7e8464` |
| Work Order Amendment 3 | `847a0a9705415ee6105f47c6b0b5eac0bd964ec8bc74849e60afd6d1af902661` |
| Amendment 3 review | `8dd2c7105d29bce4ec50e42a69325f694004d593eaba9d37db2420b859db7ba6` |

Review baseline and current HEAD are both
`d878001b6a1a536218b2c66019243510ef3f7aec`. The worker did not commit or
stage. This review adds only this reviewer-owned decision artifact.

## Decision

The Repair 3 candidate is not accepted. Focused, Project Knowledge, full
sanitized, diagnostic, and local repository controls are broadly green, but
independent source inspection and adversarial probes reproduce four material
runtime-contract failures. The required adversarial proof also remains
incomplete.

Catalog closure, status or continuity synchronization, commit, and FREEZE must
not run while these findings remain open.

## Reproduced Verification

| Check | Result | Evidence |
|---|---|---|
| focused exact P4-A1 suite | `PASS` | `154 passed` |
| Project Knowledge suite | `PASS` | `77 passed` |
| full sanitized non-live suite | `EXPECTED_EXTERNAL_OR_CLOSURE_BLOCKERS_ONLY` | `1835 passed, 128 skipped`; remaining failure/error derivatives are catalog drift and hidden-core pin mismatch only |
| diagnostic sanitized non-live remainder | `PASS` | `1835 passed, 128 skipped, 1 deselected, 1 warning` |
| exact32 | `PASS` | 32 of 32 worker paths present; no worker-created path 33 |
| protected Phase A paths | `PASS` | all six exact hashes match |
| protected aggregate | `PASS` | `bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7` |
| file-size, Project Knowledge, session-state and diff checks | `PASS` | local provider-free checks |
| catalog and repository checks | `EXPECTED_PENDING_CLOSURE` | reviewer-owned catalog drift plus its repository-validator derivative only |
| HEAD and staging | `PASS` | HEAD unchanged; staged file count zero before this review artifact |

## Findings

### P4A1-RR3-F1 - Malformed manifest entries are partially admitted

Severity: `HIGH`. Parent finding: `P4A1-RR2-F2`.

`apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py:199-208`
filters the manifest entries through `_entry_admissible` and returns the
remaining subset. It does not raise `KnowledgeCorpusUnavailable` when an entry
has malformed shape, owner, consumer, metadata, pin, or path facts.

An independent probe supplied one valid entry and one distinct unknown-owner
entry. The loader returned the valid entry instead of the Amendment 3 required
safe `CORPUS_UNAVAILABLE` outcome. This permits partial corpus use after a
manifest-integrity failure.

### P4A1-RR3-F2 - Initial P3 exceptions can escape the safe boundary

Severity: `HIGH`. Parent finding: `P4A1-RR2-F2`.

`apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py:244-251`
catches only `DocumentLimitExceeded` around initial candidate construction.
Ordinary exceptions from `build_ready_contract`, including the P3-A `refine`
and P3-C `construct_retrieval_contract` calls, are not converted to safe
`CORPUS_UNAVAILABLE`.

An injected ordinary `RuntimeError` escaped the application boundary. Use-time
revalidation correctly stale-omits ordinary `Exception` failures, but that
does not close the initial-admission path.

### P4A1-RR3-F3 - The Project Knowledge base symlink is not checked

Severity: `HIGH`. Parent finding: `P4A1-RR2-F2`.

`apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py:127-145`
starts its symlink walk at the supplied base and checks only components added
beneath it. The `repository_root/knowledge` base itself is never inspected.
When that base is a symlink, its resolved target becomes the containment base,
so an outside target can pass the current resolved-containment comparison.

The descendant-component checks work, but Amendment 3 requires refusal of any
symlink from the governed root through the entry or source-pin target.

### P4A1-RR3-F4 - Positive elapsed time accepts an identical wall-clock interval

Severity: `HIGH`. Parent finding: `P4A1-RR2-F3`.

`packages/governed-retrieval/src/governed_retrieval/receipt_models.py:113-121`
enforces finish-not-before-start and source-cutoff range, but does not enforce
that positive `elapsed_ms` requires a strictly later `finished_at_utc`.

An independent probe recomputed the receipt hash and constructed a receipt
with `elapsed_ms=1` and equal start and finish timestamps. The schema accepted
it, contrary to Amendment 3 section 5.3.

### P4A1-RR3-F5 - Required adversarial proof remains incomplete

Severity: `MEDIUM`. Parent finding: `P4A1-RR2-F6`.

The current exact32 tests do not directly prove all Amendment 3 section 6
requirements. Material gaps include coordinated receipt/handoff evidence-hash
tampering, several handoff mismatch classes, final-third timeout, and the full
negative-outcome grammar set. The replacement-scan test also permits a
negative result and can pass without proving that the fitting second candidate
was emitted.

The green suites are retained as regression evidence, not acceptance of the
missing adversarial proof.

## Verified Pass Areas

- Positive result source independently recomputes evidence hash, serialized
  bytes, token estimate, projection count, receipt count, and related handoff
  bindings.
- Execution allocation occurs before R2 validation and distinct UUIDv4
  identities are enforced.
- Authentication, permission, initial assignment, and final assignment access
  denials use the required stage, `DENY`, and reason-code mappings.
- Final-third cancellation records `PROJECTED=FAIL`, returns no projection or
  handoff, and retains `RECEIPT_EMITTED=PASS`.
- Use-time ordinary exceptions are stale-omitted.
- No provider, audit, route, UI, operational-corpus positive adapter, vector
  search, semantic RAG, or deeper project surface was added.

No accepted pass area waives an open finding.

## Review-Cost And Stop Disposition

Amendment 3 authorized one final same-scope repair and explicitly did not
authorize another sequential repair cascade. This review therefore does not
dispatch Repair 4.

| Field | Value |
|---|---|
| `reviewRoundCount` | `4` |
| `workerRepairTurnCount` | `3` |
| `newRootCauseCountThisRound` | `0` |
| `dependentFindingCountThisRound` | `5` |
| `providerCallCount` | `0` |
| `materialCommitCount` | `0` |
| `continuityCommitCount` | `0` |
| `stopDisposition` | `PARKED_CHANGES_REQUIRED_OPERATOR_DECISION` |
| `commitPlanDisposition` | `NO_COMMIT_REVIEW` |

The next move requires a fresh operator decision to park P4-A1 or authorize a
new bounded repair authority. Catalog generation, implementation-status
update, knowledge/session sync, commit, push, FREEZE, provider use, P4-A,
P4-A2, LPCI1-REF completion, and deeper project development remain blocked.

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
foundation candidate. It does not claim an LLM answer path, complete RAG,
vector search, durable audit, persistence, operational-corpus retrieval,
production API/UI, live deployment, external-agent interface, LPCI1-REF
completion, P4-A, P4-A2, or deeper project readiness.

## Final Disposition

`REPAIR_3_REVIEW_CHANGES_REQUIRED`

Findings: `4 HIGH, 1 MEDIUM`.

Waivers: `NONE`.
