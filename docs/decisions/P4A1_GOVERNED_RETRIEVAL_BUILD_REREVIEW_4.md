# P4-A1 Governed Retrieval Build Rereview 4

Disposition: REPAIR_5_TEST_SPLIT_REVIEW_PASS

## Authority

- Amendment 5 SHA-256:
  `923742468475ebb57c3042021d6965db08b030ea745c054e07447628e9264897`
- Amendment 5 review SHA-256:
  `51ea1bbd3ba4b540dab76c8d0b0ff6488fcd12b68119ab95225ab0375cb819ac`
- Pre-entry restoration receipt SHA-256:
  `67a4feea7644bbabb226404eb7a6725c213f75d38d55d79e16f965102dd06f11`
- Review HEAD:
  `d878001b6a1a536218b2c66019243510ef3f7aec`
- Staged paths: `0`

## Review Result

- Findings: `NONE`
- Waivers: `NONE`
- Exact-eight test split: PASS
- Exact36/no-path-37: PASS
- Moved-symbol uniqueness and assertion-semantic parity: PASS
- Immutable Repair 4 post-images: PASS
- Protected Phase A raw hashes and aggregate: PASS
- Stop-after-mapping boundary: PASS

| Amendment 5 test path | Lines | SHA-256 |
|---|---:|---|
| `tests/contract/test_p4a1_governed_retrieval_schema.py` | 274 | `ba30eabb55b772c8376618a2ca72312695278f49427d1ff6d9862d2e20023a65` |
| `tests/contract/test_p4a1_governed_retrieval_source_limits.py` | 62 | `7aa7984b227bfe04c8d91e64b4820c41538a747cdf1435219abee5c6d3f7893f` |
| `tests/cvf/test_p4a1_governed_retrieval.py` | 272 | `683ee224700c5ca2f11ed0ae41d2f39e1b45636ba4f8cbcf8cbe604ffac3cc72` |
| `tests/cvf/test_p4a1_governed_retrieval_boundaries.py` | 155 | `3ebc55ab64b6ac252d4902999c16e4e3a961886ca3e04498c49ecc62deaf251c` |
| `tests/cvf/test_p4a1_retrieval_authorization.py` | 273 | `18a19ca48e64fa390ca68f09af05459667be25dddd763ad19039c415ea99c4e0` |
| `tests/cvf/test_p4a1_retrieval_authorization_ordering.py` | 136 | `139b87fb8ca221eef3cf25cf5476781b5de78a1c6e678ac1de3ba8f42b16800f` |
| `tests/integration/test_p4a1_retrieval_ledger_parity.py` | 210 | `68e5ff2ae4d72f72645e4bd6800a16df75e9dbcad651a137b0e67a1b9091478d` |
| `tests/integration/test_p4a1_retrieval_project_knowledge.py` | 209 | `aec51fba4284ae6c3b9a443f77ba326d0139be10a9ed31fe20658b9dbf111101` |

## Verification

| Check | Result |
|---|---|
| Exact-eight collection before/after split | PASS - `49/49` |
| Exact-eight targeted suite | PASS - `49 passed` |
| Focused exact P4-A1 suite | PASS - `143 passed`, one bounded serializer warning |
| Project Knowledge pack suite | PASS - `77 passed` |
| Python file-size guard | PASS |
| Project Knowledge checker | PASS |
| Session-state checker | PASS |
| Diff check | PASS; expected Windows LF checkout warnings only |
| Catalog check | REVIEWER_CLOSURE_PENDING - expected metrics drift from accepted P4-A1 source/test additions |
| Repository validator | REVIEWER_CLOSURE_PENDING - catalog check is its only reported blocker |

The Amendment 5 worker did not rerun the broad suite because the amendment
explicitly limits the worker to move-only test layout and reuses the Repair 4
broad verification. Independent source review plus identical 49-test
collection, targeted PASS, and focused PASS prove the split did not remove,
rename, skip, or weaken the retained proof.

## External-Effect Accounting

- Review-time edits before this receipt: `0`
- Provider/network/product API/external database/Docker/PostgreSQL calls:
  `0/0/0/0/0/0`
- Stage/commit/push operations: `0/0/0`
- Disposable local SQLite: used only by the focused parity tests
- Live-governance or production claim: `NONE`

## Closure Decision And Boundary

The P4-A1 BUILD candidate is semantically accepted. The designated closer may
now perform only the reviewer-owned catalog/status/knowledge/continuity
closure, record the bounded final claim, and park P4-A1. P4-A, P4-A2,
LPCI1-REF, provider/LLM answer, API/UI, durable audit, deployment, full-document
access, restricted/confidential access, vector search, semantic RAG and deeper
project development remain parked pending fresh authority.
