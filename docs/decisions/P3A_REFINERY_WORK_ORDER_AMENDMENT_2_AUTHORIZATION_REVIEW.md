# P3-A Refinery Work Order Amendment 2 Authorization Review

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
| `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_2.md` | `0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4` |
| Consumed Amendment 1 | `587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546` |
| Parent Work Order | `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5` |
| Final SPEC | `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf` |

The BUILD diff base remains `b93e403cf0ab6d659de0706c058d1cd7250e75d0`. The last pushed acknowledgment checkpoint is `7b4cadb8ac01e3fd4f2284b76416a83dc8cd5277`, which was `HEAD == origin/main` at review time. Amendment 2 changes only status ownership and continuation authority after Amendment 1 stopped. It does not change DESIGN or SPEC. Any byte change to Amendment 2 invalidates this review.

## Retained failure truth

The parent invocation and Amendment 1 continuation are both consumed. The parent retained `15 passed`, then `16 passed`, followed by the full-suite failure `3 failed, 1560 passed, 128 skipped, 8 errors`; later gates were not run. Amendment 1 reproduced its 25-path preflight digest, ran the catalog generator once, then stopped at the immediate semantic check because `refinery-bridge.status` remained `contract-only`. Knowledge updates and every subsequent gate were not run. Both invocations made zero provider/network/remote-ingest calls and neither was retried.

Amendment 2 does not relabel either stopped invocation as successful and does not reuse either acknowledgment.

## Independent candidate reproduction

I independently constructed the UTF-8 manifest with repository-relative paths sorted by Unicode code point using ordinal, case-sensitive comparison. Each record is exactly `path + NUL + lowercase_file_sha256 + LF`.

For all 26 retained parent BUILD paths:

- count: `26`;
- missing: `0`;
- first ordinal path: `IMPLEMENTATION_STATUS.json`;
- manifest SHA-256: `a90307c70c321c30426062198401ad11da8e77c453771130883be322dc5ee9d2`.

The two mutable catalog surfaces independently match:

- `docs/catalog/MODULE_REGISTRY.json`: `23273fb2c017080da42d0656ec83654cd30b5f368c1af10e858b3318a08265b8`;
- `docs/catalog/MODULE_CATALOG.md`: `f814040dfe7c4dfee9e30bffca3f25189b17f5edf50c67d3ac41d932c24ae8e6`.

For the protected set—those 26 paths minus the registry and generated catalog:

- count: `24`;
- missing: `0`;
- manifest SHA-256: `d61bd541bd2adbe76aeb2b759128f6080c0bf9d2b7d0ee5cd862e08569d2bec2`.

These values reproduce Amendment 2 exactly. Any preflight mismatch is an immediate stop, not repair authority.

## Registry correction and generator behavior

Source inspection of `scripts/generate_catalog.py` confirms:

- `verify()` accepts only status values present in the registry legend but does not infer a status;
- `enrich_metrics()` updates computed module metrics, totals, and `generated_at`, but does not assign module status;
- `render_markdown()` renders the registry's existing status into the table and per-module section;
- `--write` writes only `docs/catalog/MODULE_REGISTRY.json` and `docs/catalog/MODULE_CATALOG.md`.

The registry legend defines `contract-only` as no runtime behavior and `partial` as some runtime code with an incomplete intended capability. The retained candidate has an eleven-file deterministic local package, 1,250 computed LOC, five named test modules, and no runtime caller. Therefore `partial` is the truthful bounded label; `contract-only` is stale, while `enforced` would overclaim.

The authorized manual change is sufficient and non-expansive:

- module: `refinery-bridge`;
- field: `status`;
- exact transition: `contract-only` to `partial`;
- every other semantic registry field remains unchanged before generation.

One subsequent generator invocation may update only computed metrics/timestamp in the registry and render the catalog. The immediate post-write check must confirm both surfaces say `partial`, only the two catalog paths changed at that step, and the protected-24 digest remains exact. Unexpected semantic mutation or another path stops the invocation.

## Exact changed-set boundary

The continuation may create or modify exactly four repair paths:

1. `docs/catalog/MODULE_REGISTRY.json`
2. `docs/catalog/MODULE_CATALOG.md`
3. `knowledge/PROJECT_CONTEXT.md`
4. `knowledge/manifest.json`

The first two are already among the parent's exact 26 paths. The latter two are the minimum active Knowledge Pack source-pin/context closure. Consequently the mandatory final BUILD diff against `b93e403cf0ab6d659de0706c058d1cd7250e75d0` is exactly the parent's 26 paths plus:

27. `knowledge/PROJECT_CONTEXT.md`
28. `knowledge/manifest.json`

No twenty-ninth path is authorized. Source, fixture, test, helper, status, roadmap, validator, continuity, authority, evidence, cache, lock, snapshot, or persistent index paths remain outside the continuation changed set.

## Knowledge Pack constraints

The active `project-context` manifest entry currently pins exactly three ordered sources. Continuation may change only two digest strings:

- the `IMPLEMENTATION_STATUS.json` pin, whose protected candidate file SHA-256 is `0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10`;
- the `docs/catalog/MODULE_REGISTRY.json` pin, calculated from the final post-generator registry.

The roadmap pin remains `28edb81ef099a7905381fe721d3f827573dbe6b7a1a021630cb6ebdcc7238fc8`. Entry/source-pin order and paths, schema `1.0`, ownership, classification, consumers, disposition, policies, triggers, dates, eligibility, and all other entries remain unchanged.

`PROJECT_CONTEXT.md` remains INTERNAL advisory orientation within 600 lines. It may state only `BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW` truth and must deny P3-A closure, runtime caller, provider/remote ingest, persistence, `data_scope` enforcement, retrieval/RAG, learning, production, and Phase 3 completion.

The pinned CVF-core helper used by the focused integration test operates only on a disposable local directory, creates no persistent repository index, and is not remote ingest. It authorizes no provider, network, or POST call.

## Ordered unrun gates and stop semantics

The continuation order is causally complete:

1. verify pushed lineage, immutable authority hashes, empty staged set, exact retained 26-path manifest, registry/catalog hashes, and protected-24 digest;
2. make only the single manual registry status correction;
3. run the generator once and immediately verify catalog-pair-only output, `partial` truth, and protected-24 integrity;
4. update bounded Project Context and only the two permitted source-pin digest strings;
5. run the Knowledge Pack validator;
6. run the focused Knowledge Pack unit/local-helper rehearsal command once;
7. run catalog check;
8. run the full non-live suite once;
9. run the remaining session/file-size/repository/parse/import-I/O/secret/diff checks;
10. verify exact final 28 paths, exact four repair touches, unchanged protected-24 digest, and empty staged set.

Previously retained refinery focused gates are not rerun. Every newly authorized command is run at most once. The first nonzero command, digest/hash drift, extra/missing path, unexpected mutation, stale pin, disclosure, prohibited call attempt, or claim expansion stops the invocation. There is no diagnostic rerun, in-invocation repair, or second invocation.

The continuation authorizes zero provider, network, and remote-ingest calls. A pass yields only a dirty exact 28-path deterministic local BUILD candidate pending independent BUILD review. It authorizes no BUILD commit/push, self-review, FREEZE, runtime integration, P3-B/P3-C, retrieval/RAG, learning, production integration, or AI-governance claim.

## Fresh exact human R2 prerequisite

This review pass is not continuation authority. After Amendment 2, this review, and synchronized continuity are committed and pushed as a new authority checkpoint, the operator must provide exactly:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-2-2026-08-03, Work Order Amendment SHA-256 `0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4`, đúng 4 repair paths và final exact 28 BUILD paths, zero provider/network/remote-ingest calls.

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
  - `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_2.md`
  - `fixtures/refinery/qualified_time_message.json`
  - `packages/refinery-bridge/pyproject.toml`
  - `packages/refinery-bridge/src/`
  - `tests/unit/_refinery_fixtures.py`
  - `tests/unit/test_refinery_adversarial.py`
  - `tests/unit/test_refinery_canonical.py`
  - `tests/unit/test_refinery_contract.py`
  - `tests/unit/test_refinery_models.py`
  - `tests/unit/test_refinery_pipeline.py`
- The only path created or updated by this reviewer:
  - `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_2_AUTHORIZATION_REVIEW.md`

No Amendment, continuity, or BUILD candidate path was edited. No generator, BUILD test, provider/network/remote-ingest action, staging, commit, or push was performed.

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

There are no findings and no waivers. The next governed move is authority-checkpoint synchronization, commit, and push without staging the dirty BUILD candidate, followed by the fresh exact human R2 acknowledgment above. Continuation remains prohibited until every prerequisite is satisfied.
