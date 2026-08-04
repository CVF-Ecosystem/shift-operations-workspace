# P3-A Refinery BUILD — Final Independent Re-review After A28

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent from BUILD and repair authorship)
- Risk / phase: `R2 / REVIEW`
- Review baseline:
  `HEAD == origin/main == e1b333f2577f20ead72eee50715201d86304fcee`
- Final candidate: exact `35` dirty BUILD/continuity paths; staged paths `0`
- Stable33 manifest:
  `f6ed2c05f7db2737d5d668568eaaf0ea93e22dd66ba19120b10330aab27ee5ff`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`REVIEW_PASS`

The final exact35 candidate satisfies the reviewed P3-A Design, both Design
amendments, final SPEC, parent Work Order and Amendments 1–28 within the bounded
deterministic-local claim. All prior BUILD-review and authorization findings
are closed without waiver. Source, public models, contracts, fixtures, tests,
catalog/status truth, knowledge pins and retained execution evidence agree.

This PASS authorizes `COMMIT_STEWARD` to stage, commit and push exactly the 35
reviewed candidate paths as the P3-A BUILD commit. It does not itself stage,
commit, push or FREEZE anything. No path outside exact35 may enter that BUILD
commit.

## Authority lineage

The immutable core authority hashes reproduce:

| Artifact | SHA-256 |
|---|---|
| Parent Design | `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e` |
| Design Amendment 1 | `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a` |
| Design Amendment 2 | `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc` |
| Final SPEC | `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf` |
| Parent Work Order | `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5` |
| Prior final BUILD review | `4f5099c5647c715de9e1ae9e5a833dd444c2498ca1ea282d553935cd04f11cf1` |
| Exact35 review | `de226b3d74e038ba239b19afeafeb39dad98197cd08f6d6150589b3e677f3ce6` |
| Corrected A27 | `03dc3ed14e163f645ba4f6697bff5982d7f1748fa10b7230ea59b16ec2be1a90` |
| A27 authorization re-review | `8716f487d00a43f3ec639fe3f3b0d1978f81bcf10da3c578478675113b627d3c` |
| A28 | `793dfe4f99f8bd8a4ec22977e1e0ca1a7af18d264b7fd91c9a10507c14da8db0` |
| A28 authorization review | `ed94ff31668f6ab7eddb9c1d926167ad68e7df47a16c490aaea4800fca0b947a` |

Amendments 15–26 also reproduce their canonical hashes recorded in the active
state and prior review chain. Their stop-first failures and retained PASS
evidence were not relabeled or erased by later repairs.

## Exact35 scope

The current Git dirty set exactly equals the canonical A26 final set below;
there are no missing or extra paths and the staged set is empty:

1. `IMPLEMENTATION_STATUS.json`
2. `SESSION/SESSION_MEMORY.md`
3. `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`
5. `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md`
6. `docs/catalog/MODULE_CATALOG.md`
7. `docs/catalog/MODULE_REGISTRY.json`
8. `docs/reference/FILE_SPLIT_DEBT_BASELINE.json`
9. `fixtures/refinery/normalized_message.json`
10. `fixtures/refinery/qualified_time_message.json`
11. `knowledge/PROJECT_CONTEXT.md`
12. `knowledge/manifest.json`
13. `packages/refinery-bridge/README.md`
14. `packages/refinery-bridge/contracts/refinery_contract.yaml`
15. `packages/refinery-bridge/pyproject.toml`
16. `packages/refinery-bridge/src/refinery_bridge/__init__.py`
17. `packages/refinery-bridge/src/refinery_bridge/canonical.py`
18. `packages/refinery-bridge/src/refinery_bridge/controls.py`
19. `packages/refinery-bridge/src/refinery_bridge/dedupe.py`
20. `packages/refinery-bridge/src/refinery_bridge/enums.py`
21. `packages/refinery-bridge/src/refinery_bridge/input_models.py`
22. `packages/refinery-bridge/src/refinery_bridge/normalization.py`
23. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
24. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
25. `packages/refinery-bridge/src/refinery_bridge/protection.py`
26. `packages/refinery-bridge/src/refinery_bridge/receipt_models.py`
27. `pyproject.toml`
28. `scripts/generate_catalog.py`
29. `tests/integration/test_catalog_drift_detection.py`
30. `tests/unit/_refinery_fixtures.py`
31. `tests/unit/test_refinery_adversarial.py`
32. `tests/unit/test_refinery_canonical.py`
33. `tests/unit/test_refinery_contract.py`
34. `tests/unit/test_refinery_models.py`
35. `tests/unit/test_refinery_pipeline.py`

Excluding only canonical memory and active handoff gives exact33 and manifest
`f6ed2c05f7db2737d5d668568eaaf0ea93e22dd66ba19120b10330aab27ee5ff`.
The A28 protected32 binding remains
`a23aa562f08c2154c96d3b7664589c1c05c1861e77eaab23b2074b3020673cca`.

## Prior findings closure

### Public result invariants — closed

Candidate rule versions are bound to the corresponding stage receipts;
quality and candidate fingerprints are recomputed; quarantined results require
available routes; fallback top-level provenance follows safe-string/URI rules;
and contradictory public unions fail validation.

### Multi-match dedupe — closed

Chronological selection remains `(observed_at, prior_source_id)` while public
match ids are sorted and unique. Two-match/permutation tests return selected
`z-earlier` and public ids `("a-later", "z-earlier")` without exception escape.

### AC-03/05/06/07 evidence — closed

The suite independently recomputes all typed fingerprints, rejects cross-type
substitution, covers deterministic/stable invalid outputs, normalization
idempotence, sensitivity monotonicity, dedupe permutation/window/collision
vectors and disclosure through control, union, receipt, exception, log and
snapshot surfaces. The 28-case R27 matrix is executable and separately
collected.

### Status/source-pin truth — closed

`IMPLEMENTATION_STATUS.json` SHA-256 is
`18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404`.
Its repository and `p3a_refinery` fields now state exact35, current evidence,
pending independent re-review and no BUILD commit/FREEZE. It retains the exact
bounded claim and next-move prohibition.

`knowledge/manifest.json` SHA-256 is
`251ca93f47a6527a0d941b7cbd371130a041fb21154ab269a05153b7751844a4`.
The active project-context entry pins the exact status hash above. Its pin line
has exactly ten leading ASCII spaces: exact eight-space occurrences `0`, exact
ten-space occurrences `1`. A27's immediate post-hash stop and A28's exact
two-space repair are both represented truthfully.

## Source and contract assessment

The package implements the corrected nine-stage order, strict pre-admission,
closed enums/models, three non-interchangeable fingerprints, syntactic-only
normalization, typed classification/redaction/dedupe, deterministic quality,
total fail-closed dispositions and reproducible context-candidate bytes.

The retained ambiguous `11h40` fixture remains negative and does not invent
`23:40` or action truth. The separate qualified-time fixture exercises the
positive path. Contract and import checks enforce the local pure-Python
boundary: no provider, network, database, environment discovery,
`cvf_runtime.data_scope`, retrieval or application caller.

Registry/catalog remain `refinery-bridge=partial`, explicitly state no runtime
caller, and make no provider, remote-ingest, data-scope, retrieval/RAG or
production claim. The generator/debt-pin repair is current and repository
validation passes.

## Evidence

| Evidence | Result |
|---|---|
| Exact35 / staged audit | `35 / 0` PASS |
| Stable33 / protected32 | PASS |
| Focused final Refinery suite | `57 passed` |
| Retained full non-live suite | `1597 passed / 128 skipped` |
| Project Knowledge validator | PASS |
| Focused Knowledge suite | `86 passed` |
| Session state | PASS |
| File-size guard | PASS |
| Repository validator/catalog | PASS |
| JSON/YAML/contract/import-I-O | PASS; contract group `4 passed` within focused 57 |
| Secret and diff gates | retained A28 PASS; fresh `git diff --check` PASS |
| Workspace doctor | `PASS WITH NOTE`: 24 passed, one bounded legacy catalog warning |

The full suite need not be rerun after A28: source, tests, contracts, fixtures
and catalogs are byte-identical to the independently reviewed `1597/128`
candidate, and A27/A28 changed only status/source-pin bytes. A28 freshly reran
the affected Knowledge `86` and all remaining repository/security/final gates.
The only observed warning is the existing `pytest-asyncio` future-default
deprecation warning. No provider/network/remote-ingest call occurred.

## BUILD commit authorization and separate FREEZE

`COMMIT_STEWARD` is authorized to stage exactly the 35 paths above, verify no
extra/missing path and stable33 drift, create one P3-A BUILD commit, and push it
to `origin/main`. The review artifact is governance evidence and is not one of
the exact35 BUILD paths; its handling must remain in the separately bounded
review/FREEZE continuity checkpoint, not be smuggled into the BUILD commit.

After the BUILD commit is pushed, a separate `FREEZE` sync remains mandatory.
`CLOSER` and `SESSION_SYNC_STEWARD` must record the exact BUILD commit and this
review SHA, update canonical state/mirror, memory, active handoff and affected
implementation-status/catalog/knowledge truth as required, regenerate/check
the catalog if its source truth changes, verify a clean pushed repository, and
commit/push that closure separately. FREEZE may claim only `P3-A
CLOSED_BOUNDED`; P3-B/P3-C and later Phase 3 lanes remain parked. This review
does not self-approve or execute that closure.

## Claim boundary

P3-A proves only deterministic local refinement, typed fail-closed receipts,
synthetic fixtures and reproducible candidate bytes. It has no runtime
application caller and proves no provider behavior, remote ingestion, raw
persistence, load-bearing `data_scope`/DLP/minimization, retrieval, RAG,
learning, confirmed operational truth, production readiness, P3-B/P3-C or
Phase 3 completion.
