# P3-A Refinery Work Order Amendment 1 Authorization Re-review

- Review date: 2026-08-03
- Review kind: independent re-review of corrected Amendment 1
- Reviewer role: independent `REVIEWER`
- Disposition: `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`
- Current-amendment findings: none
- Waivers: none
- Provider calls: 0
- Network calls: 0
- Remote-ingest calls: 0

## Invalidated prior review

The prior content of this artifact, SHA-256
`4797ea0ca789b0ca15e358da8996077aa188918349417e3571f0bcf84b0e25fd`,
and its pass disposition are invalidated. That review incorrectly described a
culture/case-insensitive path ordering result
`dd6e2d5ce8438a07af747ab66a3c9d1e753461815b032348b15fac66a20eef5d`
as case-sensitive. It is not authority and must not be cited as a valid review.
This re-review starts independently from the corrected Amendment and unchanged
failed candidate; it does not inherit the invalidated pass.

## Exact reviewed lineage

| Artifact | SHA-256 |
|---|---|
| `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_1.md` | `587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546` |
| `docs/work_orders/P3A_REFINERY_WORK_ORDER.md` | `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5` |
| `docs/specs/P3A_REFINERY_SPEC.md` | `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf` |

The retained parent authorization review remains `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`, no waiver. Amendment 1 changes only repair authority and gate order after the consumed parent invocation failed; it changes no DESIGN or SPEC requirement. Any byte change to Amendment 1 invalidates this disposition.

## Retained invocation and failed-candidate binding

The retained evidence is internally consistent and remains failure evidence, not a successful or reusable invocation:

- gate 1: `15 passed`;
- gate 2: `16 passed`;
- gate 3: `3 failed, 1560 passed, 128 skipped, 8 errors`;
- every later gate: `NOT_RUN`;
- provider/network/remote-ingest calls: exactly zero;
- no retry occurred.

The pre-BUILD checkpoint is `b93e403cf0ab6d659de0706c058d1cd7250e75d0`. At review time, `HEAD == origin/main == b93e403cf0ab6d659de0706c058d1cd7250e75d0`; the BUILD candidate remains dirty and unstaged.

I independently reproduced the failed-candidate manifest using exactly the specified UTF-8 records. Repository-relative paths were sorted by Unicode code point with ordinal, case-sensitive comparison; each record was encoded as `path + NUL + lowercase_file_sha256 + LF`. The result is:

- path count: `25`;
- missing paths: `0`;
- first ordinal path: `IMPLEMENTATION_STATUS.json`;
- manifest SHA-256: `58e4685e5b1ac88cd91d191dc854a5dd4aa83dd2173c6c5899aafbeec03484da`.

The digest exactly matches corrected Amendment 1 and is therefore a reproducible byte binding to the unchanged retained failed candidate, not a prose-only assertion.

## Exact path authorization

### Four repair-touch paths

The continuation may create or modify exactly these four paths:

1. `docs/catalog/MODULE_REGISTRY.json`
2. `docs/catalog/MODULE_CATALOG.md`
3. `knowledge/PROJECT_CONTEXT.md`
4. `knowledge/manifest.json`

This ceiling is sufficient and non-expansive. The catalog generator already owns the first pair. The Knowledge Pack's active `project-context` entry pins the changed implementation status and module registry, so the second pair is the minimum closure for eligibility and truthful advisory context. No validator, test, helper, additional knowledge document, source, fixture, status, roadmap, continuity, evidence, cache, lock, snapshot, or index path is needed or authorized during repair.

### Twenty-four protected retained paths

Of the 25 digest-bound failed-candidate paths, only `docs/catalog/MODULE_REGISTRY.json` may change, and only through the authorized generator's computed metrics and timestamp enrichment. The other 24 paths are byte-immutable. The continuation must snapshot their hashes after reproducing the 25-path digest and compare all 24 again at the final protected-hash audit. Any mismatch stops the invocation; it is not authority to repair or rerun.

### Final exact 28-path BUILD set

The mandatory final diff against `b93e403cf0ab6d659de0706c058d1cd7250e75d0` is exactly:

1. `pyproject.toml`
2. `packages/refinery-bridge/README.md`
3. `packages/refinery-bridge/pyproject.toml`
4. `packages/refinery-bridge/contracts/refinery_contract.yaml`
5. `packages/refinery-bridge/src/refinery_bridge/__init__.py`
6. `packages/refinery-bridge/src/refinery_bridge/enums.py`
7. `packages/refinery-bridge/src/refinery_bridge/canonical.py`
8. `packages/refinery-bridge/src/refinery_bridge/controls.py`
9. `packages/refinery-bridge/src/refinery_bridge/input_models.py`
10. `packages/refinery-bridge/src/refinery_bridge/receipt_models.py`
11. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
12. `packages/refinery-bridge/src/refinery_bridge/normalization.py`
13. `packages/refinery-bridge/src/refinery_bridge/protection.py`
14. `packages/refinery-bridge/src/refinery_bridge/dedupe.py`
15. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
16. `fixtures/refinery/normalized_message.json`
17. `fixtures/refinery/qualified_time_message.json`
18. `tests/unit/_refinery_fixtures.py`
19. `tests/unit/test_refinery_models.py`
20. `tests/unit/test_refinery_canonical.py`
21. `tests/unit/test_refinery_pipeline.py`
22. `tests/unit/test_refinery_adversarial.py`
23. `tests/unit/test_refinery_contract.py`
24. `docs/catalog/MODULE_REGISTRY.json`
25. `docs/catalog/MODULE_CATALOG.md`
26. `IMPLEMENTATION_STATUS.json`
27. `knowledge/PROJECT_CONTEXT.md`
28. `knowledge/manifest.json`

This is exactly the parent's 26 mandatory BUILD paths plus the two Knowledge Pack repair paths. The four repair-touch set overlaps the parent set only at the two catalog paths, so it converts the retained 25-path candidate into the required 28-path final set without authorizing a twenty-ninth path.

## Gate order and Knowledge Pack contract

The corrected sequence is executable and causally ordered:

1. re-establish exact lineage, hashes, candidate digest, staged-state, and changed-set boundaries;
2. generate registry metrics and `MODULE_CATALOG.md` before any catalog-dependent test;
3. make bounded `BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW` context truth and refresh the two stale source pins;
4. validate Knowledge Pack eligibility;
5. run the focused Knowledge Pack suite and disposable local helper rehearsal;
6. verify generated catalog drift;
7. run the full non-live suite once;
8. run the remaining validators and final exact-set/protected-hash audits.

This order closes both retained gate-3 causes before the Knowledge Pack checks and the only permitted full-suite rerun. The consumed refinery gate 1 and gate 2 evidence is retained and must not be rerun.

The existing Knowledge Pack manifest contract requires three ordered `project-context` source pins. Only two source-pin digest strings may change:

- `IMPLEMENTATION_STATUS.json`, whose digest is already changed by the protected failed candidate; and
- `docs/catalog/MODULE_REGISTRY.json`, whose final digest must be calculated after catalog generation.

The roadmap path and digest, source-pin order and paths, all other manifest entries, schema `1.0`, ownership, classification, consumers, disposition, policies, triggers, dates, and eligibility remain byte-semantically unchanged. `PROJECT_CONTEXT.md` must remain INTERNAL advisory orientation within 600 lines, cite the same three sources, state only pending independent-review truth, and expressly deny P3-A closure and every excluded runtime/provider/ingest/persistence/data-scope/retrieval/RAG/learning/production/Phase-3 claim.

The focused rehearsal invokes the already pinned CVF-core helper only against a disposable local directory, validates its hash and no-network token boundary, writes `_index.json` only inside that temporary directory, and removes it. That is local transformation evidence, not remote ingest. It grants no provider, network, POST, repository-index, or persistent-output authority.

## Baseline, stop, and claim semantics

`b93e403cf0ab6d659de0706c058d1cd7250e75d0` remains the immutable BUILD diff base and must remain in the pushed authority checkpoint's ancestry. After this review and continuity are committed and pushed, continuation starts only when `HEAD == origin/main` at that new authority checkpoint while the retained BUILD candidate is still dirty and digest-identical. The Amendment's lineage check does not mean resetting `HEAD` back to `b93e403`; doing so would discard the required reviewed authority checkpoint.

The continuation is one invocation. It stops at the first nonzero command, contract violation, digest drift, protected-path drift, unexpected generator output, incorrect pin, missing/extra path, secret/raw disclosure, prohibited call attempt, or claim expansion. There is no diagnostic rerun, repair after failure, second continuation, or reuse of the parent acknowledgment.

The repair authorizes zero provider, network, and remote-ingest calls. A pass yields only a dirty deterministic local 28-path BUILD candidate pending independent BUILD review. It authorizes no BUILD commit/push, FREEZE, runtime caller, persistence, P3-B/P3-C, retrieval/RAG, learning, production integration, or AI-governance claim.

## Fresh exact human R2 prerequisite

This review pass is not continuation authority. After Amendment 1, this review, and synchronized continuity are committed and pushed as the authority checkpoint, the human acknowledgment must use the literal reviewed hash:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-1-2026-08-03, Work Order Amendment SHA-256 `587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546`, đúng 4 repair paths và final exact 28 BUILD paths, zero provider/network/remote-ingest calls.

An earlier acknowledgment, placeholder or different hash, generalized approval, additional path/call, retry, or second invocation is invalid.

## Review-time changed set

- Staged paths before and after this review: none.
- Pre-existing modified paths observed and not edited by this reviewer:
  - `CVF_SESSION/ACTIVE_SESSION_STATE.json`
  - `IMPLEMENTATION_STATUS.json`
  - `SESSION/ACTIVE_SESSION_STATE.json`
  - `SESSION/SESSION_MEMORY.md`
  - `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`
  - `docs/catalog/MODULE_REGISTRY.json`
  - `fixtures/refinery/normalized_message.json`
  - `packages/refinery-bridge/README.md`
  - `packages/refinery-bridge/contracts/refinery_contract.yaml`
  - `pyproject.toml`
- Pre-existing untracked surfaces observed and not edited by this reviewer:
  - `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_1.md`
  - `fixtures/refinery/qualified_time_message.json`
  - `packages/refinery-bridge/pyproject.toml`
  - `packages/refinery-bridge/src/`
  - `tests/unit/_refinery_fixtures.py`
  - `tests/unit/test_refinery_adversarial.py`
  - `tests/unit/test_refinery_canonical.py`
  - `tests/unit/test_refinery_contract.py`
  - `tests/unit/test_refinery_models.py`
  - `tests/unit/test_refinery_pipeline.py`
- The only path updated by this re-reviewer:
  - `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_1_AUTHORIZATION_REVIEW.md`

No BUILD path was edited; no BUILD test, catalog generator, expected-failing validator, provider/network/remote-ingest action, staging, commit, or push was performed.

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

The corrected Amendment has no findings and no waivers. The manifest correction closes the invalidated prior-review defect without changing any BUILD byte. The next governed move is to synchronize the authorization checkpoint, commit and push it without staging the dirty BUILD candidate, then obtain the fresh exact human R2 acknowledgment above. Repair and rerun remain prohibited until all prerequisites are satisfied.
