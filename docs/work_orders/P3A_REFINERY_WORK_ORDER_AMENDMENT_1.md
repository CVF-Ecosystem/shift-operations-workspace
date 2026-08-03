# Work Order Amendment 1 — P3-A BUILD Gate-Order and Knowledge-Pin Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-1-2026-08-03`
- Parent Work Order: `docs/work_orders/P3A_REFINERY_WORK_ORDER.md`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Pre-BUILD checkpoint: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_RE_REVIEW`
- Provider calls: `0`
- Network calls during repair: `0`
- Remote-ingest calls: `0`

## Trigger and retained failure

The parent-authorized invocation was consumed once and stopped at the first
non-zero gate. Evidence is retained without retry:

- gate 1 models/canonical/contract: `15 passed`;
- gate 2 pipeline/adversarial: `16 passed`;
- gate 3 full non-live suite: `3 failed, 1560 passed, 128 skipped, 8 errors`;
- all later gates: `NOT_RUN`;
- provider/network/remote-ingest calls: exactly zero.

The failed suite exposed two parent Work Order defects:

1. it placed full-suite catalog-drift enforcement before the authorized catalog
   generator, so the catalog test necessarily observed the new registry/source
   with stale metrics/generated Markdown;
2. it required `IMPLEMENTATION_STATUS.json` and `MODULE_REGISTRY.json` truth
   changes but omitted the Knowledge Pack's `PROJECT_CONTEXT.md` and manifest,
   whose active eligibility contract pins both source hashes.

This is an authority/scope repair only. SPEC and DESIGN do not change.

## Failed candidate binding

The dirty failed BUILD candidate contains exactly 25 of the parent's 26 paths;
`docs/catalog/MODULE_CATALOG.md` is the sole missing path because execution
stopped before generation. Its deterministic manifest is the UTF-8 sequence of
records sorted by the repository-relative path's Unicode code points, with each
record encoded as `path + NUL + lowercase_file_sha256 + LF`. The exact manifest
SHA-256 is:

`58e4685e5b1ac88cd91d191dc854a5dd4aa83dd2173c6c5899aafbeec03484da`

Before repair, this digest and the 25-path count MUST match. Of those 25 paths,
24 are byte-immutable during repair. Only `docs/catalog/MODULE_REGISTRY.json`
may change, and only through the authorized catalog generator's computed
metrics/timestamp enrichment. Any other retained-path drift stops the repair.

## Exact repair-touch ceiling — 4 paths

The continuation invocation may create or modify only:

1. `docs/catalog/MODULE_REGISTRY.json`
2. `docs/catalog/MODULE_CATALOG.md`
3. `knowledge/PROJECT_CONTEXT.md`
4. `knowledge/manifest.json`

The first two are the parent-authorized catalog pair. The last two are the
minimal source-pin closure required by the existing active Knowledge Pack
contract. No other knowledge file, validator, test, roadmap, status, source,
fixture, continuity or evidence path may change during repair.

## Final exact BUILD changed set — 28 paths

Final BUILD diff against pre-BUILD checkpoint `b93e403` MUST be exactly the
parent's 26 paths plus:

27. `knowledge/PROJECT_CONTEXT.md`
28. `knowledge/manifest.json`

All 28 are mandatory at the final exact-set audit. Governance continuity and
this reviewed amendment are separately committed authority surfaces and are not
part of the BUILD diff.

## Corrected ordered continuation

Run once, in this exact order, stopping on the first non-zero/contract failure:

1. verify HEAD/origin lineage at `b93e403`, unchanged parent/SPEC hashes, the
   exact 25-path candidate manifest digest above, and the absence of staged or
   unapproved BUILD paths;
2. run `python scripts/generate_catalog.py --write`; it may change only the two
   catalog repair paths and must set `refinery-bridge` to computed `partial`
   truth;
3. update `knowledge/PROJECT_CONTEXT.md` to bounded
   `BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW` truth—never completion—and update
   only the `IMPLEMENTATION_STATUS.json` and `MODULE_REGISTRY.json` SHA-256 pins
   for its manifest entry; retain the roadmap pin and all other entries exactly;
4. run `python scripts/check_project_knowledge.py`;
5. run the focused Knowledge Pack unit and local rehearsal tests;
6. run `python scripts/generate_catalog.py --check`;
7. run the full non-live repository pytest suite once;
8. run session-state, file-size and repository validators, JSON/YAML parse,
   forbidden import/I/O, secret, `git diff --check`, exact 28-path diff and
   failed-candidate protected-hash audits.

Gate 1/2 refinery evidence from the consumed invocation remains retained and is
not rerun. A new failure stops immediately; there is no repair, diagnostic test
rerun or second continuation invocation under this amendment.

## Knowledge repair constraints

- `PROJECT_CONTEXT.md` remains INTERNAL advisory orientation and at most 600
  lines. It may state only that a deterministic local P3-A BUILD candidate is
  pending independent review.
- It must explicitly deny P3-A closure, runtime caller, provider/remote ingest,
  persistence, `data_scope` enforcement, retrieval/RAG, learning, production or
  Phase 3 completion.
- `knowledge/manifest.json` remains schema `1.0`, preserves entry order,
  ownership, classification, consumers, disposition, policies, triggers and
  eligibility. Only the two changed source-pin digest strings may change.
- The local pinned helper rehearsal may run through the existing test. It is not
  remote ingest and authorizes no provider/network/POST call.

## Stop conditions and claim boundary

Stop on missing fresh R2/review pass, candidate digest drift, extra/missing path,
unexpected generator output, stale/incorrect source pin, any failed gate,
secret/raw-value disclosure, provider/network/remote-ingest attempt, or claim
expansion. Do not retry.

A passing continuation yields only a dirty 28-path deterministic local BUILD
candidate for independent BUILD review. It does not authorize commit, push,
FREEZE, runtime integration, P3-B/P3-C or later lanes.

## Required review and fresh human acknowledgment

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to the exact
amendment SHA-256, four repair paths, final 28 paths, candidate digest and gate
order. After the authority checkpoint is committed/pushed, the operator must
send exactly:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-1-2026-08-03,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 4 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
