# Work Order Amendment 2 — P3-A Catalog Status Correction and Gate Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-2-2026-08-03`
- Parent Work Order: `docs/work_orders/P3A_REFINERY_WORK_ORDER.md`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 1 SHA-256: `587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Last acknowledgment checkpoint: `7b4cadb8ac01e3fd4f2284b76416a83dc8cd5277`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider calls: `0`
- Network calls during repair: `0`
- Remote-ingest calls: `0`

## Trigger and retained failures

The parent BUILD invocation and Amendment 1 continuation are both consumed and
cannot be retried.

Parent BUILD retained evidence:

- refinery focused gates: `15 passed`, then `16 passed`;
- full non-live suite: `3 failed, 1560 passed, 128 skipped, 8 errors`;
- later gates: `NOT_RUN`;
- provider/network/remote-ingest calls: zero; no retry.

Amendment 1 retained evidence:

- preflight PASS at exact 25-path digest `58e4685e5b1ac88cd91d191dc854a5dd4aa83dd2173c6c5899aafbeec03484da`;
- `python scripts/generate_catalog.py --write` ran once, exited zero and changed
  only the registry/catalog pair;
- the immediate semantic check failed because `refinery-bridge.status`
  remained `contract-only`, not required `partial`;
- the candidate stopped at exactly 26 BUILD paths;
- knowledge updates, validator, focused Knowledge Pack tests, catalog check,
  full suite and all later gates were `NOT_RUN`;
- provider/network/remote-ingest calls: zero; no retry.

The cause is now explicit: `scripts/generate_catalog.py` validates a registry
status and renders it into the catalog, but it does not infer or mutate that
status. Amendment 1 incorrectly assigned status ownership to the generator.
This Amendment corrects only that Work Order defect. DESIGN and SPEC do not
change.

## Retained 26-path candidate binding

The retained candidate contains exactly the parent's 26 mandatory BUILD paths.
Its deterministic manifest is the UTF-8 sequence of records sorted by the
repository-relative path's Unicode code points, each encoded as
`path + NUL + lowercase_file_sha256 + LF`.

- path count: `26`;
- manifest SHA-256: `a90307c70c321c30426062198401ad11da8e77c453771130883be322dc5ee9d2`;
- registry SHA-256: `23273fb2c017080da42d0656ec83654cd30b5f368c1af10e858b3318a08265b8`;
- generated catalog SHA-256: `f814040dfe7c4dfee9e30bffca3f25189b17f5edf50c67d3ac41d932c24ae8e6`.

Exactly 24 of those paths are protected byte-for-byte during the continuation.
They are the 26 paths minus `docs/catalog/MODULE_REGISTRY.json` and
`docs/catalog/MODULE_CATALOG.md`. Their manifest SHA-256 under the same
algorithm is:

`d61bd541bd2adbe76aeb2b759128f6080c0bf9d2b7d0ee5cd862e08569d2bec2`

Any preflight mismatch stops the invocation.

## Exact repair-touch ceiling — 4 paths

The continuation may create or modify only:

1. `docs/catalog/MODULE_REGISTRY.json`
2. `docs/catalog/MODULE_CATALOG.md`
3. `knowledge/PROJECT_CONTEXT.md`
4. `knowledge/manifest.json`

No source, fixture, test, helper, status, roadmap, validator, lock, continuity,
evidence or other knowledge path may change during the continuation.

## Exact registry correction

Before catalog rendering, change exactly one semantic registry value:

- module id: `refinery-bridge`;
- field: `status`;
- from: `contract-only`;
- to: `partial`.

Do not manually alter any other registry field. Then run the existing catalog
generator once. Its computed metrics/timestamp output is allowed in the
registry, and its rendered Markdown is allowed in the catalog. Immediately
verify both surfaces say `partial`, the registry remains valid, and only the
two catalog paths changed at this step.

The `partial` label is bounded truth for a deterministic local package with
tests and no runtime caller. It is not `enforced`, P3-A closure, production
readiness, provider behavior, remote ingest, persistence, `data_scope`
enforcement, retrieval/RAG, learning or Phase 3 completion.

## Final exact BUILD changed set — 28 paths

The final diff against `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
must be exactly the parent's 26 mandatory paths plus:

27. `knowledge/PROJECT_CONTEXT.md`
28. `knowledge/manifest.json`

All 28 are mandatory. Governance authority and continuity paths are separately
committed surfaces and are not part of this BUILD diff.

## Corrected ordered continuation

Run once in this exact order, stopping on the first non-zero command or
contract failure:

1. verify pushed authority lineage, immutable parent/Amendment/SPEC hashes,
   empty staged set, exact 26-path candidate manifest, exact registry/catalog
   hashes and exact protected-24 digest;
2. edit only `refinery-bridge.status` from `contract-only` to `partial` in the
   registry;
3. run `python scripts/generate_catalog.py --write` once, then verify the two
   catalog paths only, registry/catalog `partial` truth and protected-24 digest;
4. update `knowledge/PROJECT_CONTEXT.md` to bounded
   `BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW` truth and update only the
   `IMPLEMENTATION_STATUS.json` and final `MODULE_REGISTRY.json` SHA-256 pins
   in the `project-context` manifest entry;
5. run `python scripts/check_project_knowledge.py`;
6. run exactly once:
   `python -m pytest tests/unit/test_project_knowledge_pack.py tests/integration/test_project_knowledge_ingest_rehearsal.py -q`;
7. run `python scripts/generate_catalog.py --check`;
8. run the full non-live repository pytest suite once;
9. run session-state, file-size and repository validators, JSON/YAML parse,
   forbidden import/I/O, secret and `git diff --check` checks;
10. verify exact final 28-path diff, exact four repair-touch paths, unchanged
    protected-24 digest and no staged path.

The previously retained refinery focused gates are not rerun. No failed or
successful command is repeated under this Amendment.

## Knowledge repair constraints

- `PROJECT_CONTEXT.md` remains INTERNAL advisory orientation and at most 600
  lines.
- It may state only that a deterministic local P3-A BUILD candidate is pending
  independent review.
- It must explicitly deny P3-A closure, runtime caller, provider/remote ingest,
  persistence, `data_scope` enforcement, retrieval/RAG, learning, production
  and Phase 3 completion.
- `knowledge/manifest.json` stays schema `1.0` and preserves entry order,
  ownership, classification, consumers, disposition, policies, triggers,
  dates and eligibility.
- Only two source-pin digest strings may change: `IMPLEMENTATION_STATUS.json`
  and `docs/catalog/MODULE_REGISTRY.json`. The roadmap pin and all other
  manifest content remain unchanged.
- The focused integration test may invoke the already pinned CVF-core helper
  only against its disposable local directory. That is local transformation,
  not remote ingest, and authorizes no provider/network/POST call or persistent
  repository index.

## Stop conditions and claim boundary

Stop on missing fresh R2/review pass, candidate/hash/digest drift, extra or
missing path, unexpected registry/generator output, stale or incorrect source
pin, any failed gate, secret/raw disclosure, prohibited call attempt or claim
expansion. There is no retry, diagnostic rerun or second invocation.

A pass yields only a dirty exact 28-path deterministic local BUILD candidate
pending independent BUILD review. It authorizes no BUILD commit/push, self
review, FREEZE, runtime integration, P3-B/P3-C, retrieval/RAG, learning,
production integration or AI-governance claim.

## Required review and fresh human acknowledgment

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to the exact
Amendment 2 SHA-256, candidate/protected digests, four repair paths, final exact
28 paths, single registry correction and ordered gates. After the reviewed
authority checkpoint is committed/pushed, the operator must send exactly:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-2-2026-08-03,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 4 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
