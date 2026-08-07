# Work Order Amendment 1 - P3-C Knowledge Pin Refresh

- Amendment id: `P3C-RETRIEVAL-READY-DATA-CONTRACT-WO-AMENDMENT-1-2026-08-07`
- Parent: `docs/work_orders/P3C_RETRIEVAL_READY_DATA_CONTRACT_WORK_ORDER.md`
- Parent SHA-256: `0e83fc03660f10640bd15f3edab1696d66299fe29ba64ec779aa07f8e1855e9f`
- Execution base: `aea7544fb28cb9c14dfe7149822d2b38e1918ef7`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/product-network/POST calls: `0/0/0`

## 1. Trigger and operator authority

The separate implementation worker stopped at the parent Work Order's full
non-live suite gate with `1629 passed`, `128 skipped`, `2 failed` and `8
errors`. Every failure/error came from Project Knowledge validation. The
validator reads `knowledge/manifest.json`, whose active source pins include
two paths that the parent Work Order requires BUILD to change:

- `IMPLEMENTATION_STATUS.json`;
- `docs/catalog/MODULE_REGISTRY.json`.

The registry pin matched the execution base and necessarily drifted after the
required P3-C module entry and catalog generation. The status pin and the
governance-boundaries `AGENTS.md` pin were already stale at the execution base.
The original exact 22-path ceiling did not include the manifest, so the worker
correctly returned `BUILD_BLOCKED_SOURCE_OR_SCOPE` without widening scope.

The operator explicitly approved expansion from 22 to 23 BUILD paths, adding
only `knowledge/manifest.json`. This is a real path-boundary approval. It does
not change objective, risk, external-effect class, claim boundary, provider
budget, commit owner or reviewer independence.

## 2. Source verification and frozen hashes

All values below were derived by local byte reads only. No provider, product
network, POST, secret, configuration, database or runtime retrieval call was
made.

| Claimed item | Source | Verified fact | Disposition |
|---|---|---|---|
| Parent authority | `docs/work_orders/P3C_RETRIEVAL_READY_DATA_CONTRACT_WORK_ORDER.md` | SHA-256 `0e83fc03660f10640bd15f3edab1696d66299fe29ba64ec779aa07f8e1855e9f` | ACCEPT |
| Execution base | repository `HEAD` and `origin/main` before BUILD | `aea7544fb28cb9c14dfe7149822d2b38e1918ef7` | ACCEPT |
| Manifest before repair | `knowledge/manifest.json` | SHA-256 `849de575768078f611fb0b2b8f9bed8bcf0063ae89a01109bf55a35b240472f0` | ACCEPT |
| Governance source bytes | `AGENTS.md` | current worktree SHA-256 `a29efc0f7a79d659a8982ec5f391b0bbcd9d588891299658ce894e15d0b9e7a0` | ACCEPT |
| Status source bytes | `IMPLEMENTATION_STATUS.json` | post-candidate SHA-256 `65bef92b7a702f90df1189f5c24db91d8c2b31fefa7e3bf192c952096714664f` | ACCEPT |
| Registry source bytes | `docs/catalog/MODULE_REGISTRY.json` | post-candidate SHA-256 `8faab1df238ec3d9d64429bb5490f15b063570d14792aadfd6ea6013ed3f2483` | ACCEPT |

The three expected source hashes are frozen by this amendment. Any candidate
edit that changes one of those source bytes before manifest repair stops the
repair and returns for source re-verification; the repair worker must not
silently refresh a different hash.

## 3. Exact final BUILD changed-set ceiling - 23 paths

Every path below is mandatory. The final BUILD candidate may change exactly:

1. `pyproject.toml`
2. `packages/refinery-bridge/src/refinery_bridge/enums.py`
3. `packages/refinery-bridge/contracts/refinery_contract.yaml`
4. `tests/unit/test_refinery_contract.py`
5. `packages/retrieval-contracts/README.md`
6. `packages/retrieval-contracts/pyproject.toml`
7. `packages/retrieval-contracts/contracts/retrieval_contract.schema.json`
8. `packages/retrieval-contracts/src/retrieval_contracts/__init__.py`
9. `packages/retrieval-contracts/src/retrieval_contracts/enums.py`
10. `packages/retrieval-contracts/src/retrieval_contracts/common.py`
11. `packages/retrieval-contracts/src/retrieval_contracts/source_models.py`
12. `packages/retrieval-contracts/src/retrieval_contracts/contract_models.py`
13. `packages/retrieval-contracts/src/retrieval_contracts/canonical.py`
14. `packages/retrieval-contracts/src/retrieval_contracts/constructor.py`
15. `tests/unit/test_p3c_retrieval_contract_models.py`
16. `tests/unit/test_p3c_retrieval_contract_constructor.py`
17. `tests/unit/test_p3c_retrieval_contract_adversarial.py`
18. `tests/unit/test_p3c_retrieval_contract_digest_guards.py`
19. `tests/contract/test_p3c_retrieval_contract_schema.py`
20. `docs/catalog/MODULE_REGISTRY.json`
21. `docs/catalog/MODULE_CATALOG.md`
22. `IMPLEMENTATION_STATUS.json`
23. `knowledge/manifest.json`

The amendment artifact itself is authorization evidence, not a BUILD path.
No 24th BUILD path, renamed path, generated residue, continuity file, roadmap,
ADR, SPEC, review, application, ledger, database or runtime path is allowed.

## 4. Exact repair authority for path 23

After independent amendment review PASS, the repair worker may edit only the
three existing `sha256` string values below in `knowledge/manifest.json`:

1. In entry `project-context`, source pin `IMPLEMENTATION_STATUS.json` becomes
   `65bef92b7a702f90df1189f5c24db91d8c2b31fefa7e3bf192c952096714664f`.
2. In entry `project-context`, source pin
   `docs/catalog/MODULE_REGISTRY.json` becomes
   `8faab1df238ec3d9d64429bb5490f15b063570d14792aadfd6ea6013ed3f2483`.
3. In entry `governance-boundaries`, source pin `AGENTS.md` becomes
   `a29efc0f7a79d659a8982ec5f391b0bbcd9d588891299658ce894e15d0b9e7a0`.

The repair must preserve the manifest schema, field order, entry order, source
pin order, dates, owners, dispositions, eligibility values, policies,
citations and every other byte except those three 64-character values. It may
not edit any of the existing 22 candidate paths. It may not regenerate,
reinterpret, expand or re-review the knowledge pack.

## 5. Resume gate and verification

Only `WORK_ORDER_AMENDMENT_REVIEW_PASS` permits the same separate worker to
resume as `REPAIR_WORKER`. Before editing, it must verify:

- parent Work Order hash and execution base above;
- manifest pre-repair hash above;
- exact current hashes of all three pinned source files above;
- the existing candidate still changes exactly the original 22 paths and is
  entirely unstaged;
- the amendment is independently reviewed with findings/waivers `NONE/NONE`.

After the exact three-value repair, run in this order:

1. parse `knowledge/manifest.json` as JSON;
2. run `python scripts/check_project_knowledge.py`;
3. run focused Project Knowledge unit and integration tests;
4. run all five focused P3-C test files;
5. run all five retained P3-A focused test files;
6. run `python scripts/generate_catalog.py --check` without another write;
7. run `python -m pytest -q` for the full non-live suite;
8. run session-state, catalog, file-size and repository validators;
9. run JSON/YAML parse, secret-pattern, private-helper/import, `git diff
   --check`, exact-23-path, staged-file and generated-residue audits;
10. run the workspace doctor, allowing only the bounded legacy-catalog note.

Any source-hash drift, fourth manifest byte range, 24th BUILD path, staged
file, provider/network/POST attempt, secret/config read, unresolved test/gate
failure or broadened claim stops the worker and returns to the reviewer.

## 6. Roles, independence and claim boundary

- Amendment author: `WORK_ORDER_AMENDMENT_AUTHOR`; authors this artifact only.
- Amendment reviewer: independent from the author and implementation worker.
- Repair worker: the separate worker, only after amendment review PASS.
- Root agent: `INDEPENDENT_BUILD_REVIEWER`; does not co-author candidate code.
- BUILD/repair commit mode: `WORKER_MUST_NOT_COMMIT`.
- Commit steward acts only after independent final BUILD `REVIEW_PASS`.

The prior P3-C implementation and claim boundaries remain unchanged. This
amendment authorizes only source-pin consistency for the existing local
knowledge validator. It does not authorize retrieval, query, vector/index,
persistence, provider behavior, tenant authorization, minimization/placement
enforcement, RAG, production readiness, Phase 3 completion or public release.

## 7. Independent amendment review return

The reviewer must source-verify the parent/hash/base, blocker evidence, exact
23-path ceiling, three frozen source hashes, manifest byte-preservation rule,
rerun sequence, ownership and claim boundary. Return exactly one:

- `WORK_ORDER_AMENDMENT_REVIEW_PASS`;
- `WORK_ORDER_AMENDMENT_CHANGES_REQUIRED`;
- `WORK_ORDER_AMENDMENT_BLOCKED_SOURCE_OR_SCOPE`.

No repair resumes from this amendment candidate alone.
