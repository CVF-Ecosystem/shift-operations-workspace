# P4-A1 Governed Retrieval Foundation Build Rereview 1

- Date: `2026-08-10`
- Role: `INDEPENDENT_BUILD_REVIEWER_CLOSER`
- Risk ceiling: `R2`
- Disposition: `REPAIR_REREVIEW_CHANGES_REQUIRED`
- Findings: `9 MATERIAL`
- Waivers: `NONE`

## Reviewed Authority

| Artifact | SHA-256 |
|---|---|
| Main SPEC | `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` |
| Receipt appendix | `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` |
| Parent Work Order | `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6` |
| Initial BUILD review | `88ed37974b46b628f047a240cf878c4f24babefa8998c8b7c6ea6cbd37033c91` |
| Work Order Amendment 1 | `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1` |
| Amendment 1 review | `c645c0e0be697a4dbbb48f31d450c0bb3026696e173020d61971c3a2af043b24` |
| Phase A re-baseline review | `287719cee149d74933fe5c72cc00a997c47368d090550ddcdad0fb142009768f` |

Review baseline and current HEAD are both
`d878001b6a1a536218b2c66019243510ef3f7aec`. The worker did not commit or stage.

## Decision

The repair candidate is not accepted. The focused P4-A1 suite increased from
121 to 156 tests and passes, but direct source inspection and independent probes
reproduce contract failures that those tests do not cover. Catalog closure must
not run while semantic findings remain open.

## Reproduced Verification

| Check | Result | Evidence |
|---|---|---|
| focused P4-A1 suite | `PASS` | `156 passed in 2.57s` |
| full sanitized non-live suite | `FAIL` | `1836 passed, 128 skipped, 3 failed, 8 errors in 130.12s` |
| file-size guard | `PASS` | no new Python file exceeds 300 lines |
| Project Knowledge checker | `PASS` | project checker command |
| session-state checker | `PASS` | project checker command |
| catalog check | `FAIL_PENDING_REVIEWER_CLOSURE` | generated metrics remain stale |
| repository validator | `FAIL` | catalog failure propagates |
| protected Phase A paths | `PASS` | all six exact hashes unchanged |
| protected 15-row aggregate | `PASS` | `bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7` |
| staged files | `PASS` | zero |

The full suite also exposed two non-candidate closure dependencies:

1. `tests/unit/test_project_knowledge_pack.py` evaluates the pack as of
   `2026-08-03`, while the authorized current manifest review date is
   `2026-08-10`;
2. the hidden public-core checkout and its `origin/main` resolve to
   `2103a38fda01ee827e9fc6c3be38a824fa5d54ad`, while the downstream manifest
   remains pinned to `9b039ea6b532176d92536338659bd346f019cd5a`.

The second item is an external workspace/core-pin condition. It is not authority
for this P4-A1 worker to change `.cvf/manifest.json`, hidden-core state, a remote
ref, or network state.

## Findings

### P4A1-RR1-F1 - Canonical authentication dependency is still bypassed

Severity: `HIGH`. Parent finding: `P4A1-BUILD-F1`.

SPEC R3 requires authentication through `workspace_api.dependencies.get_principal`.
`_governed_retrieval_admission.py:249-266` imports and calls
`decode_access_token` directly. Token verification occurs, but the required
source-authorized dependency surface is not exercised.

### P4A1-RR1-F2 - Lifecycle filter widening is ignored

Severity: `HIGH`. Parent finding: `P4A1-BUILD-F3`.

`corpus.py:94-105` accepts only record and truth-class filters, while
`_governed_retrieval_sources.py:159-162` never passes or checks
`lifecycle_statuses`. A direct probe sent `CURRENT` for Project Knowledge and
returned `EVIDENCE_AVAILABLE` instead of `FILTER_WIDENS_SCOPE`. The test named
`every_widening_dimension` also omits lifecycle status.

### P4A1-RR1-F3 - Project Knowledge admission is not containment-safe or shape-closed

Severity: `HIGH`. Parent finding: `P4A1-BUILD-F4`.

`_governed_retrieval_knowledge.py:120-135,186-188` joins manifest-controlled
absolute or parent paths without proving repository and knowledge containment.
Lines 85-94 accept any non-empty retention literal as active. Lines 77-82 do
not validate the top-level manifest object/shape. A probe admitted
`../AGENTS.md` with `retentionPolicy=DELETED`; valid non-object JSON can escape
as raw `AttributeError`.

### P4A1-RR1-F4 - Use-time revalidation still leaks failures and bypasses limits

Severity: `HIGH`. Parent findings: `P4A1-BUILD-F5`, `P4A1-BUILD-F11`.

`revalidate_entry` may raise `KnowledgeCorpusUnavailable`, but
`_governed_retrieval_revalidation.py:140-145` catches only
`DocumentLimitExceeded`. It also calls `_admissible_entries` directly and
bypasses the 100-entry use-time guard. A malformed manifest probe escaped a
typed retrieval result.

### P4A1-RR1-F5 - Projection replacement scan is pre-sliced

Severity: `HIGH`. Parent finding: `P4A1-BUILD-F6`.

`_governed_retrieval_revalidation.py:212` iterates
`survivors[:max_projection_records]`. When an earlier survivor cannot fit, a
later fitting survivor outside that slice is never examined. The revised repair
contract requires scanning the deterministic selected window until the output
ceiling is filled or candidates are exhausted.

### P4A1-RR1-F6 - Evidence, receipt, result, and handoff remain unbound

Severity: `HIGH`. Parent finding: `P4A1-BUILD-F7`.

- `evidence_models.py:59-80` accepts empty or digest-inconsistent snippets;
- `receipt_models.py:44-80` accepts arbitrary receipt hashes;
- `result_models.py:17-26` does not bind wrapper outcome to
  `receipt.final_outcome`; and
- the positive result does not bind projection citation order/hashes/counts and
  limits to the receipt and handoff.

Direct probes accepted an empty digest-inconsistent projection, a bogus receipt
hash, and an `AccessDeniedV1` carrying a `NO_EVIDENCE` receipt. The new contract
test changes the wrapper discriminator instead of testing this actual mismatch.

### P4A1-RR1-F7 - Negative receipt stage truth and population timing remain wrong

Severity: `HIGH`. Parent finding: `P4A1-BUILD-F8`.

`governed_retrieval.py:202-218` records `NO_EVIDENCE` and all-stale termination
stages as `PASS`; the appendix requires the first terminal non-access stage to
be `FAIL`. Applied limits are not set until projection, and source cutoff is
populated only for positive evidence. A direct no-match probe returned terminal
`PASS`, `applied_limits=None`, and `source_cutoff_utc=None` after source reads.

### P4A1-RR1-F8 - Timeout/cancellation lacks a final checkpoint

Severity: `MEDIUM`. Parent finding: `P4A1-BUILD-F11`.

The last stop check is at `governed_retrieval.py:228-230`. Projection,
serialization, hashing, receipt construction, and handoff construction continue
afterward. A stop occurring during that work can still return positive evidence.

### P4A1-RR1-F9 - Required variant and adversarial proof remains incomplete

Severity: `MEDIUM`. Amendment 1 proof boundary.

The suite does not construct or reach every required outcome and does not test
the real F2-F8 failure shapes above. In particular, it lacks concrete
construction/reachability proof for `StaleEvidenceV1`,
`RetrievalLimitExceededV1`, and `InvariantFailureV1` and lacks path-containment,
lifecycle-widening, cross-binding, replacement-scan, and final-stop cases.

## Closed Findings Retained

The rereview independently accepts these repair results:

- F0 protected re-baseline remains exact;
- F2 authentication/permission/assignment stage separation;
- F9 JSON-wire-safe structural validation and post-auth corpus resolution;
- F10 100/101 manifest and 65,536/65,537 document overflow behavior;
- F12 equal-distance trimming removes the high/end side;
- immutable registry, lower client budgets, P3-A sensitivity propagation,
  UUIDv4 validation, timeout/cancellation typed variants, and safe initial
  manifest failure are partially or fully improved as recorded above.

No closed item is a waiver for an open finding.

## Next Allowed Move

One bounded Work Order Amendment 2 must source-verify and assign all nine
findings in one repair round. It may retain the same exact31 candidate ceiling,
with a separately justified test-only closure path for the current Project
Knowledge review-date fixture if independently authorized. It must not absorb
the hidden-core pin mismatch into P4-A1 implementation scope.

No catalog generation, implementation-status update, knowledge/session sync,
commit, push, FREEZE, provider/network/product-API/external-database call,
core-pin change, P4-A, P4-A2, or deeper project work is authorized yet.

## External-Effect Accounting

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

`REPAIR_REREVIEW_CHANGES_REQUIRED`

The candidate remains in REVIEW and must not proceed to closure or FREEZE.
