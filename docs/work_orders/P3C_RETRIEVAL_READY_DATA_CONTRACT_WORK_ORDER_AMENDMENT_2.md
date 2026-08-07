# Work Order Amendment 2 - P3-C Exhaustive Knowledge Pin Closure

- Amendment id: `P3C-RETRIEVAL-READY-DATA-CONTRACT-WO-AMENDMENT-2-2026-08-07`
- Parent Work Order: `docs/work_orders/P3C_RETRIEVAL_READY_DATA_CONTRACT_WORK_ORDER.md`
- Parent Work Order SHA-256: `0e83fc03660f10640bd15f3edab1696d66299fe29ba64ec779aa07f8e1855e9f`
- Prior amendment: `docs/work_orders/P3C_RETRIEVAL_READY_DATA_CONTRACT_WORK_ORDER_AMENDMENT_1.md`
- Prior amendment SHA-256: `c0cd74ac7a85102ea027c8121ca6c9489804e7a81a59d9107d6e4e34ea57d6b5`
- Prior review: `WORK_ORDER_AMENDMENT_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Authority checkpoint: `cc21cfa277a6d8808f3f450e83c30770f98ad2cb`
- Original execution base: `aea7544fb28cb9c14dfe7149822d2b38e1918ef7`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/product-network/POST calls: `0/0/0`

## 1. Trigger and unchanged boundary

Amendment 1 authorized exactly three source-pin substitutions in
`knowledge/manifest.json`. The repair worker applied those substitutions
byte-for-byte and reproduced the expected post-Amendment-1 manifest SHA-256:

`58a1050885b53f745db7a5ff235e934883752fc0a77e60ce0347e0d7a48ce0c1`

The required post-repair knowledge checker still failed. A complete local
enumeration of every source pin found two additional stale values that
predated the P3-C candidate. Amendment 1 had explicitly forbidden a fourth
manifest byte range, so the worker stopped rather than silently refreshing
them.

This amendment changes no BUILD path, objective, acceptance requirement,
risk, external-effect class, provider budget, commit owner, reviewer
independence or claim boundary. The final BUILD ceiling remains exactly 23
paths. It refines repair authority inside the already authorized path
`knowledge/manifest.json` only.

## 2. Exhaustive 16-source-pin audit

The amendment author enumerated all three manifest entries and all 16
`sourcePins`, hashing each current local source as raw bytes. Exactly 14 pins
match and exactly two are stale:

| Entry | Source path | Manifest SHA-256 | Current source SHA-256 | Result |
|---|---|---|---|---|
| `PROJECT_CONTEXT.md` | `IMPLEMENTATION_STATUS.json` | `65bef92b7a702f90df1189f5c24db91d8c2b31fefa7e3bf192c952096714664f` | `65bef92b7a702f90df1189f5c24db91d8c2b31fefa7e3bf192c952096714664f` | MATCH |
| `PROJECT_CONTEXT.md` | `docs/catalog/MODULE_REGISTRY.json` | `8faab1df238ec3d9d64429bb5490f15b063570d14792aadfd6ea6013ed3f2483` | `8faab1df238ec3d9d64429bb5490f15b063570d14792aadfd6ea6013ed3f2483` | MATCH |
| `PROJECT_CONTEXT.md` | `docs/implementation/EXECUTION_ROADMAP.md` | `c0b1c4558c0a3fea90316b7c15697f6a611f0d12835e5c8a43bade2d8b6cf458` | `cf9aa19334cef6861f7392e78fa14b2acad7f93586a922839d9a526a72e6b0aa` | STALE |
| `OPERATIONS_GLOSSARY.md` | `packages/operations-domain/README.md` | `e1c967a194ded12f302eec6773bc35065edb7dad2a4fb6372e66b13991d4dc58` | `e1c967a194ded12f302eec6773bc35065edb7dad2a4fb6372e66b13991d4dc58` | MATCH |
| `OPERATIONS_GLOSSARY.md` | `packages/operations-domain/src/operations_domain/models.py` | `a5e70e7ab48354b3087f5c0070ad1328df91812f4101e492c49a454353a6ebb4` | `a5e70e7ab48354b3087f5c0070ad1328df91812f4101e492c49a454353a6ebb4` | MATCH |
| `OPERATIONS_GLOSSARY.md` | `packages/operations-domain/src/operations_domain/lifecycle.py` | `d5a26e99343c1969508146e92cd38e3b91977d6d8cf9974217d6dabd9b04309a` | `d5a26e99343c1969508146e92cd38e3b91977d6d8cf9974217d6dabd9b04309a` | MATCH |
| `OPERATIONS_GLOSSARY.md` | `packages/operations-domain/src/operations_domain/assignment_models.py` | `f1454bd24904b00eebd61a577c0037da66cc47ccd71acd100175b3cd7bd6b8fd` | `f1454bd24904b00eebd61a577c0037da66cc47ccd71acd100175b3cd7bd6b8fd` | MATCH |
| `OPERATIONS_GLOSSARY.md` | `packages/operations-domain/src/operations_domain/report_models.py` | `67ce6c73fc9a42e752690b786c24e9282c93acb9aa05c5069cfe47cbe6864093` | `67ce6c73fc9a42e752690b786c24e9282c93acb9aa05c5069cfe47cbe6864093` | MATCH |
| `OPERATIONS_GLOSSARY.md` | `packages/workspace-contracts/README.md` | `1333aca990d855e52288c9262a9d744e828e93e7548e96eec30c9e153055ef2f` | `1333aca990d855e52288c9262a9d744e828e93e7548e96eec30c9e153055ef2f` | MATCH |
| `GOVERNANCE_BOUNDARIES.md` | `AGENTS.md` | `a29efc0f7a79d659a8982ec5f391b0bbcd9d588891299658ce894e15d0b9e7a0` | `a29efc0f7a79d659a8982ec5f391b0bbcd9d588891299658ce894e15d0b9e7a0` | MATCH |
| `GOVERNANCE_BOUNDARIES.md` | `.cvf/manifest.json` | `16ee4caea555252c1a4c8fa5eb35daebb237a6445534f5f7eab50fa97ed68e2d` | `617bb281aea622790c30b2e65204f7fa7b4d3a5923b8ca3a0995daa051fa1867` | STALE |
| `GOVERNANCE_BOUNDARIES.md` | `.cvf/policy.json` | `c8a28fb11accc2ae3d21054636f6c32046e1547203be8b4044901f658ed3a863` | `c8a28fb11accc2ae3d21054636f6c32046e1547203be8b4044901f658ed3a863` | MATCH |
| `GOVERNANCE_BOUNDARIES.md` | `docs/cvf/CONTEXT_CONTROL.md` | `7ebda16f48e113c1e39cecdf5b557ca1f4285271bd5313afdb311ac832f208f2` | `7ebda16f48e113c1e39cecdf5b557ca1f4285271bd5313afdb311ac832f208f2` | MATCH |
| `GOVERNANCE_BOUNDARIES.md` | `docs/cvf/EVIDENCE_AND_TRUTH.md` | `095a43e2dae2dc921ef2a720ce3e2c9a6a6ff0a95d2cc2fa19b11e96d3476a20` | `095a43e2dae2dc921ef2a720ce3e2c9a6a6ff0a95d2cc2fa19b11e96d3476a20` | MATCH |
| `GOVERNANCE_BOUNDARIES.md` | `docs/cvf/PROVIDER_GOVERNANCE.md` | `17705afda16bca001c27752121705e58764dcde83bf7ddd9761cb08976d78dc7` | `17705afda16bca001c27752121705e58764dcde83bf7ddd9761cb08976d78dc7` | MATCH |
| `GOVERNANCE_BOUNDARIES.md` | `docs/cvf/RISK_AND_APPROVAL.md` | `2abfb7946ea14c3ae59d4fc608a1cd58f34215c6ab8912bbe225e5ce487881f3` | `2abfb7946ea14c3ae59d4fc608a1cd58f34215c6ab8912bbe225e5ce487881f3` | MATCH |

Audit result: `16 TOTAL / 14 MATCH / 2 STALE`.

## 3. Exact repair authority

Only after independent `WORK_ORDER_AMENDMENT_REVIEW_PASS`, the same separate
repair worker may change exactly two additional existing 64-character values
in `knowledge/manifest.json`:

1. In entry `project-context`, source pin
   `docs/implementation/EXECUTION_ROADMAP.md` changes from
   `c0b1c4558c0a3fea90316b7c15697f6a611f0d12835e5c8a43bade2d8b6cf458`
   to
   `cf9aa19334cef6861f7392e78fa14b2acad7f93586a922839d9a526a72e6b0aa`.
2. In entry `governance-boundaries`, source pin `.cvf/manifest.json` changes
   from
   `16ee4caea555252c1a4c8fa5eb35daebb237a6445534f5f7eab50fa97ed68e2d`
   to
   `617bb281aea622790c30b2e65204f7fa7b4d3a5923b8ca3a0995daa051fa1867`.

The manifest pre-repair SHA-256 must be exactly:

`58a1050885b53f745db7a5ff235e934883752fc0a77e60ce0347e0d7a48ce0c1`

After exactly those two substitutions, the expected manifest SHA-256 is:

`13b6c982714a81966df269354f95220e31e34d04f437340ef6f0c2f54bb43ff1`

All other manifest bytes, including the three Amendment-1 repairs, schema,
field/entry/pin order, dates, owners, dispositions, eligibility values and
policies, are protected. No other candidate path may change during this
repair.

## 4. Final ceiling, roles and calls

The exact final BUILD ceiling remains the same 23 paths enumerated by
Amendment 1. No 24th path is authorized. In particular, neither
`docs/implementation/EXECUTION_ROADMAP.md` nor `.cvf/manifest.json` may be
edited; they are read-only pin sources.

- Amendment author: `WORK_ORDER_AMENDMENT_AUTHOR`.
- Amendment reviewer: independent from author and worker.
- Repair worker: same separate worker after review PASS only.
- Root agent: `INDEPENDENT_BUILD_REVIEWER`; does not co-author candidate code.
- Commit mode: `WORKER_MUST_NOT_COMMIT`.
- Provider/product-network/POST/secret/config/database call budget: all zero.

## 5. Post-repair exhaustive gate and full rerun

Before any test, the repair worker must:

1. reproduce the expected manifest post-image hash;
2. enumerate all 16 source pins again from the repaired manifest;
3. hash each current source as raw bytes;
4. assert exactly `16 MATCH / 0 STALE`;
5. stop if any source changed, any pin is missing/extra, or any third byte
   range differs.

Only after that exhaustive equality assertion passes, rerun the complete
Amendment-1 chain:

1. JSON parse of `knowledge/manifest.json`;
2. `python scripts/check_project_knowledge.py`;
3. focused Project Knowledge unit and integration tests;
4. all five focused P3-C test files;
5. all five retained P3-A focused test files;
6. `python scripts/generate_catalog.py --check` without another write;
7. `python -m pytest -q` full non-live suite;
8. session-state, catalog, file-size and repository validators;
9. JSON/YAML, secret-pattern, private-helper/import, `git diff --check`,
   exact-23-path, staged-zero and generated-residue audits;
10. workspace doctor, allowing only the bounded legacy-catalog note.

Any mismatch, third substitution, 24th path, staged file, provider/network/
POST/secret/config/database call, unresolved test/gate failure or broadened
claim stops the worker and returns to independent review.

## 6. Claim boundary and independent review return

This amendment repairs only local knowledge source-pin consistency. It does
not authorize or prove retrieval runtime, query, vector/index, persistence,
provider behavior, tenant authorization, minimization/placement enforcement,
RAG, production readiness, Phase 3 completion or public release.

The independent reviewer must reproduce the 16-pin audit, the two exact stale
values, manifest pre/post hashes, exact-23 boundary, zero-call route and full
rerun contract. Return exactly one:

- `WORK_ORDER_AMENDMENT_REVIEW_PASS`;
- `WORK_ORDER_AMENDMENT_CHANGES_REQUIRED`;
- `WORK_ORDER_AMENDMENT_BLOCKED_SOURCE_OR_SCOPE`.

No repair resumes from this amendment candidate alone.
