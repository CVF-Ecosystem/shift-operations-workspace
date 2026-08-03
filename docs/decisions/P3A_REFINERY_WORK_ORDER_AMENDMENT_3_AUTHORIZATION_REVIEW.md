# P3-A Refinery Work Order Amendment 3 Authorization Review

- Review date: 2026-08-03
- Reviewer role: independent `REVIEWER`
- Disposition: `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`
- Findings: none
- Waivers: none
- Provider calls: 0
- Network calls: 0
- Remote-ingest calls: 0

## Exact reviewed lineage

| Artifact | SHA-256 |
|---|---|
| `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_3.md` | `30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4` |
| Consumed Amendment 2 | `0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4` |
| Parent Work Order | `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5` |
| Final SPEC | `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf` |

The BUILD diff base remains `b93e403cf0ab6d659de0706c058d1cd7250e75d0`. The last pushed acknowledgment checkpoint is `78ea4e58d61f75cd90ef153f5ea9f7396884bfe1`, which was `HEAD == origin/main` at review time. Amendment 3 changes only continuation authority after Amendment 2 stopped. It changes no DESIGN, SPEC, or retained BUILD byte. Any byte change to Amendment 3 invalidates this review.

## Retained stop truth

Amendment 2 was consumed once. Its preflight passed, it changed only `refinery-bridge.status` from `contract-only` to `partial`, and its single catalog-generator invocation passed. The immediately following PowerShell verification wrapper failed to parse before any check executed. Stop-first/no-retry was honored. The two knowledge paths and all later gates remain `NOT_RUN`; provider/network/remote-ingest calls remained exactly zero.

Amendment 3 does not retry the Amendment 2 verification wrapper or relabel that stopped invocation. It binds the post-generator state as a new immutable candidate and authorizes only work that has never run.

## Independent immutable-candidate reproduction

I independently constructed the UTF-8 manifest using repository-relative paths sorted by Unicode code point with ordinal, case-sensitive comparison. Every record is exactly `path + NUL + lowercase_file_sha256 + LF`.

- path count: `26`;
- missing paths: `0`;
- first ordinal path: `IMPLEMENTATION_STATUS.json`;
- last ordinal path: `tests/unit/test_refinery_pipeline.py`;
- manifest SHA-256: `c7c1761c699494658b6d8853e1ebcc1703f5be52d6855a6be1ddb7478be601b8`.

The catalog surfaces independently match:

- `docs/catalog/MODULE_REGISTRY.json`: `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38`;
- `docs/catalog/MODULE_CATALOG.md`: `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92`.

The registry parses successfully and its `refinery-bridge.status` is `partial`. The generated Markdown also says `partial` in both the module table and per-module heading. The retained enforcement/next-step wording keeps the no-runtime-caller and bounded-claim limits. Thus the status correction is complete and truthful without another write.

All 26 paths are byte-immutable under this continuation. A mismatch in the combined digest, either catalog hash, JSON parse, or `partial` truth stops before any repair edit.

## Exact repair and final changed sets

The continuation may create or modify exactly two paths:

1. `knowledge/PROJECT_CONTEXT.md`
2. `knowledge/manifest.json`

No catalog, source, fixture, test, helper, implementation status, roadmap, validator, authority, continuity, evidence, cache, lock, snapshot, or other knowledge path may change.

The mandatory final diff against `b93e403cf0ab6d659de0706c058d1cd7250e75d0` is therefore exactly the immutable retained 26 parent BUILD paths plus those two knowledge paths: exact total `28`. Governance authority/continuity artifacts remain separate from the BUILD diff. There is no twenty-ninth path and no writable catalog path.

## Knowledge source-pin constraints

The active `project-context` entry has three ordered source pins. Only these two digest strings may change:

- `IMPLEMENTATION_STATUS.json` to its immutable candidate SHA-256 `0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10`;
- `docs/catalog/MODULE_REGISTRY.json` to its immutable SHA-256 `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38`.

The roadmap pin remains `28edb81ef099a7905381fe721d3f827573dbe6b7a1a021630cb6ebdcc7238fc8`. Source-pin order and paths, entry order, schema `1.0`, ownership, classification, consumers, disposition, policies, triggers, dates, eligibility, and every other manifest value remain unchanged.

`PROJECT_CONTEXT.md` remains INTERNAL advisory orientation at no more than 600 lines. It may state only that the deterministic local P3-A BUILD candidate is `BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW`. It must deny P3-A closure, runtime caller, provider/remote ingest, persistence, `data_scope` enforcement, retrieval/RAG, learning, production, and Phase 3 completion.

The focused integration test's pinned CVF-core helper operates only inside a disposable local directory and leaves no persistent repository index. It is local transformation, not remote ingest, and grants no provider/network/POST authority.

## Catalog-write prohibition

`python scripts/generate_catalog.py --write` is explicitly prohibited. No manual registry or catalog edit is authorized. The later `python scripts/generate_catalog.py --check` command is a read-only consistency gate and must not write either file. Any catalog byte change—including a new generated timestamp—is a stop condition.

## Ordered never-run gates

The continuation is complete and causally ordered:

1. verify pushed lineage, authority hashes, empty staged set, exact immutable 26-path manifest and catalog hashes, valid registry JSON, and `partial` truth in both catalog surfaces;
2. update only the two knowledge repair paths within the pin/context constraints;
3. run the Knowledge Pack validator once;
4. run the focused Knowledge Pack unit/local-helper rehearsal command once;
5. run catalog `--check` once, never `--write`;
6. run the full non-live repository suite once;
7. run session-state, file-size, and repository validators once;
8. run JSON/YAML, forbidden-import/I/O, secret, and diff checks;
9. verify exact final 28 paths, exact two repair touches, unchanged immutable 26-path digest, and empty staged set.

The retained refinery focused gates are not rerun. No Amendment 2 command is retried, and no failed or successful command is repeated under Amendment 3. The first nonzero command, hash/digest/path drift, catalog write, incorrect pin, disclosure, prohibited call attempt, or claim expansion stops the invocation. There is no diagnostic rerun, in-invocation repair, or second invocation.

The continuation authorizes zero provider, network, and remote-ingest calls. A pass yields only a dirty exact 28-path deterministic local BUILD candidate pending independent BUILD review. It authorizes no BUILD commit/push, self-review, FREEZE, runtime integration, P3-B/P3-C, retrieval/RAG, learning, production integration, or AI-governance claim.

## Fresh exact human R2 prerequisite

This review pass is not continuation authority. After Amendment 3, this review, and synchronized continuity are committed and pushed as a new authority checkpoint, the operator must provide exactly:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-3-2026-08-03, Work Order Amendment SHA-256 `30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4`, đúng 2 repair paths và final exact 28 BUILD paths, zero provider/network/remote-ingest calls.

An earlier acknowledgment, placeholder/different hash, generalized approval, extra path/call, retry, or second invocation is invalid.

## Review-time changed set

- Staged paths before this review: none.
- Pre-existing modified paths observed and not edited by this reviewer:
  - `CVF_SESSION/ACTIVE_SESSION_STATE.json`
  - `IMPLEMENTATION_STATUS.json`
  - `SESSION/ACTIVE_SESSION_STATE.json`
  - `SESSION/SESSION_MEMORY.md`
  - `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`
  - `docs/catalog/MODULE_CATALOG.md`
  - `docs/catalog/MODULE_REGISTRY.json`
  - `fixtures/refinery/normalized_message.json`
  - `packages/refinery-bridge/README.md`
  - `packages/refinery-bridge/contracts/refinery_contract.yaml`
  - `pyproject.toml`
- Pre-existing untracked surfaces observed and not edited by this reviewer:
  - `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_3.md`
  - `fixtures/refinery/qualified_time_message.json`
  - `packages/refinery-bridge/pyproject.toml`
  - `packages/refinery-bridge/src/`
  - `tests/unit/_refinery_fixtures.py`
  - `tests/unit/test_refinery_adversarial.py`
  - `tests/unit/test_refinery_canonical.py`
  - `tests/unit/test_refinery_contract.py`
  - `tests/unit/test_refinery_models.py`
  - `tests/unit/test_refinery_pipeline.py`
- The only path created by this reviewer:
  - `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_3_AUTHORIZATION_REVIEW.md`

No Amendment, continuity, catalog, or BUILD candidate path was edited. No generator, test, provider/network/remote-ingest action, staging, commit, or push was performed.

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

There are no findings and no waivers. The next governed move is authority-checkpoint synchronization, commit, and push without staging the dirty BUILD candidate, followed by the fresh exact human R2 acknowledgment above. Continuation remains prohibited until every prerequisite is satisfied.
