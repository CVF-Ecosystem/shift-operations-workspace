# P4-A1 Governed Retrieval Foundation Build Review

- Date: `2026-08-10`
- Role: `INDEPENDENT_BUILD_REVIEWER_CLOSER`
- Risk ceiling: `R2`
- Disposition: `BUILD_REVIEW_CHANGES_REQUIRED`
- Findings: `13 MATERIAL`
- Waivers: `NONE`

## Reviewed Authority

| Artifact | SHA-256 |
|---|---|
| Work Order: `docs/work_orders/P4A1_GOVERNED_RETRIEVAL_FOUNDATION_WORK_ORDER.md` | `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6` |
| Main SPEC: `docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md` | `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` |
| Receipt appendix: `docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md` | `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` |
| Parent ADR: `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md` | `8dbdfbaded8ed523eb465bc3c657620a323fafae465f5d0d0d66fe8cac6aa4fc` |
| Work Order authorization review | `00f9b927ad7206c54c07b4342810c690345cd3e1569174b5c1cc8e14ada6484a` |

Review baseline and current HEAD are both
`d878001b6a1a536218b2c66019243510ef3f7aec`. The worker did not commit.

## Executive Decision

The candidate is not accepted for closure or FREEZE. The focused exact suite
passes, the positive implementation remains provider-free and Project
Knowledge-only, and the exact31 implementation paths are present. Those facts
do not offset material contract failures in authentication, authorization
staging, filter enforcement, source revalidation, disclosure budgets, receipt
integrity, request handling, and hard-limit behavior.

The candidate also changed six protected pre-existing governance paths whose
bytes were frozen by the released pre-BUILD manifest. The full non-live suite
and required repository checks are not green. A bounded repair Work Order
amendment and independent authorization review are required before repair.

## Reproduced Verification Evidence

| Check | Result | Evidence |
|---|---|---|
| exact focused P4-A1 suite | `PASS` | `121 passed in 1.50s` |
| full non-live suite | `FAIL` | `1801 passed, 128 skipped, 3 failed, 8 errors in 147.33s` |
| governed file size | `PASS` | `python scripts/check_file_size.py` |
| Project Knowledge | `FAIL` | `KPK_ELIGIBILITY_MISMATCH:PROJECT_CONTEXT.md`; `KPK_SOURCE_PIN_DRIFT:PROJECT_CONTEXT.md` |
| generated catalog check | `FAIL` | source changed without matching generated catalog truth |
| session state | `PASS` | `python scripts/check_session_state.py` |
| repository validation | `FAIL` | catalog drift propagated to repository validation |
| diff whitespace check | `PASS_WITH_NOTE` | no whitespace error; line-ending warnings only |

The catalog check recomputed 22,294 LOC and 237 files while the committed
registry still records 21,296 LOC and 232 files. The Work Order assigns catalog
and Project Knowledge closure surfaces to the reviewer, but they cannot be
updated to close a semantically rejected BUILD.

## Changed-Set Review

- exact31 authorized BUILD paths: `31`;
- exact31 paths present: `31`;
- exact31 missing paths: `0`;
- candidate paths outside exact31 that pre-existed the BUILD release: protected
  governance paths listed below;
- new source files over 300 lines: `0`.

The released 15-row protected governance manifest had SHA-256
`98837a163e436c76412177356dd32f3bbcb9346f0c8c19455f3c46cdd18153a0`.
The following six protected paths no longer match their released byte hashes:

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
2. `SESSION/ACTIVE_SESSION_STATE.json`;
3. `SESSION/SESSION_MEMORY.md`;
4. `docs/implementation/EXECUTION_ROADMAP.md`;
5. `knowledge/PROJECT_CONTEXT.md`;
6. `knowledge/manifest.json`.

The other nine protected rows remain byte-identical. The six-path drift is an
execution-boundary failure even where the semantic text appears unchanged.

## Material Findings

### P4A1-BUILD-F0 - Protected release manifest was not preserved

Severity: `CRITICAL`. Boundary: Work Order execution isolation and released
successor handoff.

The released manifest required all 15 pre-existing governance paths to remain
byte-identical. Its recomputed hash changed from
`98837a163e436c76412177356dd32f3bbcb9346f0c8c19455f3c46cdd18153a0`
to `17e081c5cd7fbf98eb6649e2a9e560fcc9651bfddfb372dfdd6ea7193cbfdc22`.
The six paths enumerated in Changed-Set Review now fail their pinned individual
hashes. The released files did not share one uniform newline history: a local
in-memory LF normalization reproduces only two of the six old hashes. The drift
must therefore be resolved by a separately authorized session-sync action that
either restores proven bytes or creates a deterministic semantic-equivalent
re-baseline with new exact hashes. It must not be silently accepted as part of
exact31 implementation repair.

### P4A1-BUILD-F1 - Authentication and transaction ordering are incorrect

Severity: `HIGH`. Requirements: `R3`, `R7`; acceptance criteria: `AC3`, `AC7`.

`apps/workspace-api/src/workspace_api/application/governed_retrieval.py:93`
accepts an arbitrary `Principal` and never invokes the verified bearer path
owned by `workspace_api.dependencies.get_principal`. At line 120 it opens a
Ledger transaction before permission is checked. The required order is
authentication, permission authorization, then one Ledger unit for assignment
and later governed reads.

### P4A1-BUILD-F2 - Authorization stage outcomes are misclassified

Severity: `HIGH`. Requirements: `R3`, `R9`; acceptance criteria: `AC3`, `AC9`.

`governed_retrieval.py:128-139` combines permission and assignment in one call.
Any `AccessDenied`, including assignment denial, is recorded as
`PERMISSION_AUTHORIZED=DENY`; authentication and assignment can remain
`NOT_RUN`. This breaks the ordered receipt-stage contract.

### P4A1-BUILD-F3 - Corpus filters and immutable-registry boundary are not enforced

Severity: `HIGH`. Requirement: `R4`; acceptance criterion: `AC4`.

`packages/governed-retrieval/src/governed_retrieval/corpus.py:88` defines
`filters_within_descriptor`, but the application never calls it. Requested
record, truth, and lifecycle filters are ignored, and widening requests do not
return `FILTER_WIDENS_SCOPE`. `CORPUS_REGISTRY` is also a mutable dictionary.
A local probe using a `Task` filter returned Project Knowledge evidence.

### P4A1-BUILD-F4 - Project Knowledge admission fabricates or omits provenance checks

Severity: `HIGH`. Requirements: `R5`, `R7`; acceptance criteria: `AC5`, `AC7`.

`_governed_retrieval_knowledge.py:88-125` does not require a valid active owner
and retention policy. Lines 151-156 derive the compared source pins from the
same already-read bytes, and lines 193-200 manufacture an active retention
assertion instead of validating the manifest authority. This does not establish
the required P3-A/P3-C ownership and retention facts.

### P4A1-BUILD-F5 - Use-time revalidation does not revalidate evidence

Severity: `HIGH`. Requirement: `R7`; acceptance criterion: `AC7`.

`_governed_retrieval_revalidation.py:38-56` checks only that a fresh manifest
entry exists and has the same path, then reuses the old `RetrievalReadyV1`.
It does not reread the source or compare source/content digest, version, chunk
ID, revalidation token, sensitivity, owner, retention, or raw-byte-derived
facts. Stale evidence can therefore remain projection-eligible.

### P4A1-BUILD-F6 - Client disclosure ceilings are claimed but not enforced

Severity: `HIGH`. Requirement: `R8`; acceptance criterion: `AC8`.

`_governed_retrieval_knowledge.py:229-235` hard-codes 1,024 code points and
3,072 bytes. The revalidation/projection call does not receive lower client
ceilings. A local probe requesting 5 code points and 20 bytes returned a
1,024-code-point, 1,036-byte snippet while the receipt claimed limits 5/20.
The same path hard-codes `INTERNAL` sensitivity instead of preserving the
validated candidate sensitivity.

### P4A1-BUILD-F7 - Receipt, evidence, result, and handoff integrity is not bound

Severity: `HIGH`. Requirements: `R8`, `R9`, `R10`; acceptance criteria:
`AC8`, `AC9`, `AC10`.

The evidence models permit empty or digest-inconsistent projections; receipt
models accept supplied hashes without contract recomputation; result models do
not bind outcome to receipt status or positive projections to the handoff.
Probes accepted a tampered empty projection and an `AccessDeniedV1` carrying a
`NO_EVIDENCE` receipt.

### P4A1-BUILD-F8 - Returned negative receipts omit mandatory emission state

Severity: `HIGH`. Requirement: `R9`; acceptance criterion: `AC9`.

`_governed_retrieval_admission.py:114-139` fills unrecorded stages as
`NOT_RUN` but never records `RECEIPT_EMITTED=PASS`. `NO_EVIDENCE` and
`STALE_EVIDENCE` also record the terminal operational stage as `PASS` instead
of the first terminal `FAIL`. A blocked corpus can populate `corpus_id` before
`CORPUS_RESOLVED` passes, contrary to the appendix nullability rule.

### P4A1-BUILD-F9 - Structural request validation is neither JSON-wire-safe nor closed

Severity: `HIGH`. Requirement: `R2`; acceptance criterion: `AC2`.

`request_models.py` uses strict tuple fields, rejecting normal JSON arrays.
Malformed filter values can escape as raw `TypeError`, `shift_ids` permits
unsafe whitespace, and a corpus ID is resolved to the closed enum before
authorization. That both breaks the closed invalid-request outcome and exposes
registry validity before the authorized corpus-resolution stage.

### P4A1-BUILD-F10 - Hard-limit overflow is silently truncated

Severity: `HIGH`. Requirement: `R6`; acceptance criterion: `AC6`.

`_governed_retrieval_knowledge.py:95` silently evaluates only the first 100
manifest entries, and line 150 silently truncates source text to 65,536 code
points. The contract requires `RETRIEVAL_LIMIT_EXCEEDED` and forbids silent
truncation. Truncating before hashing also changes the admitted evidence.

### P4A1-BUILD-F11 - Timeout, cancellation, and safe source failures are not executable

Severity: `MEDIUM`. Requirements: `R7`, `R11`; acceptance criteria: `AC7`,
`AC11`.

Timeout is copied into a receipt but never enforced; cancellation has no
execution path; stopped-result variants are not mapped. An unreadable or
malformed Project Knowledge manifest can raise `KnowledgeCorpusUnavailable`
out of the application instead of returning a safe typed outcome. Receipt
timing is caller-supplied and always reports zero elapsed time.

### P4A1-BUILD-F12 - Deterministic projection tie-breaking is reversed

Severity: `MEDIUM`. Requirement: `R8`; acceptance criterion: `AC8`.

`packages/governed-retrieval/src/governed_retrieval/projection.py:66` removes
the low/start side when distances tie. The SPEC requires removing the high/end
side. The reproduced boundary probe returned `TARGETb [1,8)` instead of
`aTARGET [0,7)`.

## Verified Pass Boundaries

- `retrieval.query` is added at viewer level and existing unknown-action denial
  remains fail-closed.
- The only implemented positive corpus is Project Knowledge.
- Both operational corpora remain dependency-blocked and do not read canonical
  or Message data.
- No provider adapter/call, audit write, production route, FastAPI router, UI,
  deployment, vector search, operational positive adapter, or canonical digest
  owner was added.
- Provider-attempt counts remain structurally zero.
- No live-provider claim is made by this review.

These passes are retained requirements for repair and do not authorize closure.

## Repair Boundary

The next allowed move is a repair Work Order amendment that:

1. source-verifies and assigns every finding above;
2. expands or separates the reviewer-owned catalog and Project Knowledge
   reconciliation needed to make all required gates reproducible;
3. restores proven bytes or provides a separately authorized deterministic
   semantic-equivalent re-baseline for the six protected paths before
   implementation resumes;
4. adds adversarial tests that fail on every reproduced defect;
5. preserves all verified pass boundaries and the original stop-after-mapping
   boundary; and
6. receives independent authorization before any repair edit.

No code repair, catalog regeneration, continuity mutation, commit, push,
provider call, network call, external database call, P4-A, P4-A2, FREEZE, or
deeper project development is authorized by this review.

## External-Effect And Reviewer Accounting

| Surface | Count |
|---|---:|
| Provider calls | 0 |
| Network calls | 0 |
| Product API calls | 0 |
| External database calls | 0 |
| Audit writes | 0 |
| Source files modified by reviewer | 0 |
| Review artifacts authored | 1 |
| Files staged | 0 |
| Commits | 0 |
| Pushes | 0 |

## Final Disposition

`BUILD_REVIEW_CHANGES_REQUIRED`

The BUILD remains in REVIEW and must not proceed to closure or FREEZE.
