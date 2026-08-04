# P3-A Refinery exact35 BUILD — Independent Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent from BUILD and repair authorship)
- Risk / phase: `R2 / REVIEW`
- Review baseline: `HEAD == origin/main == ac16f076be5a9d396f1d5f2df2b05ac78be598a1`
- Candidate: exact `35` dirty BUILD/continuity paths; staged paths `0`
- Stable binding: exact `33` paths / manifest
  `4d0ba0a8b901d5cd097f59111f959b667725df651ddcbd0bbb530c0953f6661a`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Waivers: `NONE`

## Disposition

`REVIEW_CHANGES_REQUIRED`

The deterministic Refinery implementation and its repaired public-boundary
tests pass independent source inspection and fresh local verification. Prior
final-review functional findings F1-F3 are closed without waiver. The candidate
cannot pass final BUILD review because its implementation-status source of
truth is materially stale: it still describes exact32/A18 repair-pending truth
while the governed candidate is exact35 and A26 has completed its zero-write
remaining-gate invocation. No BUILD commit or FREEZE is permitted yet.

## Reviewed authority

The following immutable authority hashes reproduce:

| Artifact | SHA-256 |
|---|---|
| Parent ADR | `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e` |
| Design Amendment 1 | `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a` |
| Design Amendment 2 | `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc` |
| Final SPEC | `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf` |
| Parent Work Order | `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5` |
| Prior final review | `4f5099c5647c715de9e1ae9e5a833dd444c2498ca1ea282d553935cd04f11cf1` |
| Amendments 15-18 | `19e1369d...aced28c`, `076032a3...27f3162`, `01e6392d...cef1a7c`, `2b11f819...240d2a` |
| Amendments 19-22 | `3b78afc6...ce11f7`, `58b576d7...6a38d4`, `f6fa72b3...a4040c`, `59ba66ea...15e3e` |
| Amendments 23-26 | `98825deb...00d63`, `cc4d481d...bef51a`, `ff2671a0...e33cf7`, `61a609c9...c42feb` |

A26 authority review SHA-256
`4c39242145a5d4c93ca7422535b2cfbd30de20a6641f5867f20cd0c985b302ce`
and canonical A26 execution state agree on zero repair paths, exact35,
stable33, staged0, and invocation PASS.

## Prior finding closure

### Functional F1 — closed

`candidate_is_bound` now binds normalization, terminology, classification and
redaction versions to their exact stage receipts. `failure_is_bound` requires
an available quarantine route. Top-level result provenance is validated by the
same safe-string/URI rules. Fresh public-construction tests reject all reviewed
drift cases.

### Functional F2 — closed

Chronological source-match selection remains `(observed_at, prior_source_id)`.
Pipeline receipts and duplicate output independently publish sorted unique
match ids. Fresh two-record/permutation coverage returns selected
`z-earlier` and public ids `("a-later", "z-earlier")` without exception escape.

### Evidence F3 — closed

Tests now independently recompute typed golden bytes, reject cross-type
fingerprints, cover deterministic/stable outputs, normalization idempotence,
dedupe permutation and inclusive/out-of-window bounds, and exercise the
control/union/receipt/log/snapshot disclosure surfaces. The executable R27
matrix remains separately parameterized.

## Finding F1 — MEDIUM: implementation-status truth is stale

`IMPLEMENTATION_STATUS.json.p3a_refinery` currently states:

- `BUILD_REPAIR_IN_PROGRESS` with final review changes required;
- Amendment 18 exact-nine repair within final exact32;
- exact32 changed set;
- A18 repair and post-repair gates pending;
- next move is fresh A18 R2 and exact-nine repair.

Those statements contradict current governed truth. Canonical state and the
active handoff record A18-A26 as consumed, exact35 as final candidate scope,
A24 full `1597/128` evidence, and A26 remaining gates PASS pending this review.
The repository-level `status` string also still ends in
`P3A_REFINERY_INTAKE`. This is a source-truth defect, not a continuity-only
wording issue, and repeats the class of prior final-review F4 after later
authorized path expansion.

No waiver is appropriate. Minimum implementation repair is bounded to
`IMPLEMENTATION_STATUS.json` plus `knowledge/manifest.json` for the resulting
source-pin update. It requires a fresh reviewed Work Order amendment and fresh
exact R2. All other exact35 bytes should remain protected.

## Fresh evidence

| Check | Result |
|---|---|
| Workspace doctor | `PASS WITH NOTE` — 24 pass, one bounded legacy catalog warning |
| Exact candidate / staged | `35 / 0` PASS |
| Stable manifest | `33 / 4d0ba0a8...661a` PASS |
| Focused Refinery | `57 passed` |
| Full non-live pytest | `1597 passed, 128 skipped` |
| Session state | PASS |
| File-size guard | PASS |
| Repository validator | PASS |
| Catalog check | PASS, 22 modules |
| Candidate JSON/YAML parse | PASS |
| Refinery contract/import/I-O tests | `4 passed` |
| `git diff --check` | PASS |

The pytest run emitted only the existing `pytest-asyncio` future-default
deprecation warning. No provider, network or remote-ingest call was made.

## Exact reviewed set and byte digests

The review artifact itself is not part of the candidate. The exact35 set is:

| SHA-256 | Path |
|---|---|
| `9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6` | `IMPLEMENTATION_STATUS.json` |
| `f6cf6858e28bf6d0ebf31a3602baf5a16fa178560221f04134bacc91573dae84` | `SESSION/SESSION_MEMORY.md` |
| `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` | `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md` |
| `5021a37371352fcba22006057bbd8030483594af03a0abdbe07faa3c201d0431` | `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md` |
| `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` | `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md` |
| `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` | `docs/catalog/MODULE_CATALOG.md` |
| `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` | `docs/catalog/MODULE_REGISTRY.json` |
| `ae9ed0dfc28f41f2b551a6f02d878e5a0bcc800b2025738ec54704a0031c5132` | `docs/reference/FILE_SPLIT_DEBT_BASELINE.json` |
| `06e362e2a22179da5cca48a094b9a606ea6867017d1fd2498eff81373f15ff4e` | `fixtures/refinery/normalized_message.json` |
| `6d7ddf1e0ee302d590d193d4eeb50b1e863a15f2b01d6cc32d440a9df362e70b` | `fixtures/refinery/qualified_time_message.json` |
| `2354df70f61cdd0e027b2790dec8b31d22fbbb9fafc11a47508d05ae9277c7ce` | `knowledge/PROJECT_CONTEXT.md` |
| `cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80` | `knowledge/manifest.json` |
| `65b34d1706efb20a46e497009284e8a9caa86705450d52f0a7dcc523850e140b` | `packages/refinery-bridge/README.md` |
| `39ab127b13755c56f0e8cab229f59a27d53a182ed3c9994b629f4134a232b798` | `packages/refinery-bridge/contracts/refinery_contract.yaml` |
| `194ddfaacc59d4cd2e03820713410903da014cd806eafdd537ea6b7d9fccb9dd` | `packages/refinery-bridge/pyproject.toml` |
| `d44148b3ca0f2d000f3299c9d7a838d6ea0f50a9d55a5ecb0c416513aa1523b5` | `packages/refinery-bridge/src/refinery_bridge/__init__.py` |
| `618594868deddad47f56029a0535cc14a336fb13cadeadf5a0edcf39862fbdc9` | `packages/refinery-bridge/src/refinery_bridge/canonical.py` |
| `523aa3396aa283343c132b4717d0c834177c25a8913fe4035c9a28acf798b505` | `packages/refinery-bridge/src/refinery_bridge/controls.py` |
| `812aa7380996ff11e7545c72d1e9bec5355ba520eb404f90c22ab33c01c3e165` | `packages/refinery-bridge/src/refinery_bridge/dedupe.py` |
| `5e4e56ffe8c7f9c30ae40b869e6271c1310acf78429427546c7be1e3d4d19dbf` | `packages/refinery-bridge/src/refinery_bridge/enums.py` |
| `5e9ab6bbdc47c727831ae9e7641cc54ea07b60fe905396b7dd209e28e73ace72` | `packages/refinery-bridge/src/refinery_bridge/input_models.py` |
| `7b912df48b0aa6d287843e180c0f03da401c438d56b4af17ed0b9d01561d4081` | `packages/refinery-bridge/src/refinery_bridge/normalization.py` |
| `7ea839ac3cad56ec7fa058a9e3ad7da05a6b0cd6b31b65a1ad5eb8e677260396` | `packages/refinery-bridge/src/refinery_bridge/output_models.py` |
| `7b5bfc9374f59a636f9cf0dd963eb1d05ccee64a4bd96f50f98f5853d7891d58` | `packages/refinery-bridge/src/refinery_bridge/pipeline.py` |
| `9a37cdc0879ad087864aea6d027b1a5a623e2a77dab70f6cdef67e18421a9c53` | `packages/refinery-bridge/src/refinery_bridge/protection.py` |
| `32bdf786127faa773b8b6a83128c178d45098bb44871e144b03667d7ba7133d3` | `packages/refinery-bridge/src/refinery_bridge/receipt_models.py` |
| `6c8a23245dc32934a4dcd5b5b56af2f1bf88f7c6ac3cf30641d30a2ffa430207` | `pyproject.toml` |
| `6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6` | `scripts/generate_catalog.py` |
| `820e4f3bd5b299f341e511e15ecb0de2de7a3e49b28a68f1aa83eabd5aee791d` | `tests/integration/test_catalog_drift_detection.py` |
| `4fff2fc50fa0d8d8e0fc0978dcd8e64a89ebb60e831c7a39500e16b4f1f9aead` | `tests/unit/_refinery_fixtures.py` |
| `291c920f5b3d9c137522f6cb191bc348cdd832cb1b9a41cb3c89d885b4bee74d` | `tests/unit/test_refinery_adversarial.py` |
| `9e3e552f0122b39aa568481303ebfe41b3b94eed9c3a975b300cd33698c3bed1` | `tests/unit/test_refinery_canonical.py` |
| `217a41435076cda7b9ab776aa204c4bd867ab5f1bd15972c35c4219bb7ad1ff3` | `tests/unit/test_refinery_contract.py` |
| `7af17012708ceead193bc35361e96665acf17cd3c886ca3fac9f72b9fffc3d89` | `tests/unit/test_refinery_models.py` |
| `a25f0878eeb5ca6359885c25ba2798abee23b379dabd32c375dba5d210e4d518` | `tests/unit/test_refinery_pipeline.py` |

Full digests are reproducible directly from the files and are bound by the
stable33 manifest above plus canonical exact35 state.

## Claim boundary

This review supports only a deterministic local Refinery candidate with typed
fail-closed outputs and reproducible candidate bytes. It proves no runtime
application caller, provider behavior, remote ingestion, persistence,
`data_scope` enforcement, retrieval, RAG, learning, confirmed truth,
production readiness, P3-A closure or Phase 3 completion.
