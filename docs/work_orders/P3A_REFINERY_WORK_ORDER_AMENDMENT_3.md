# Work Order Amendment 3 — P3-A Knowledge-Pin and Remaining-Gate Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-3-2026-08-03`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 2 SHA-256: `0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Last acknowledgment checkpoint: `78ea4e58d61f75cd90ef153f5ea9f7396884bfe1`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls during continuation: `0/0/0`

## Trigger and retained failure

Amendment 2 was consumed once. Its preflight passed, the single authorized
registry status edit changed `refinery-bridge` from `contract-only` to
`partial`, and the catalog generator ran once with PASS. The immediately
ordered verification wrapper then failed PowerShell parsing before any check
executed. Stop-first/no-retry was honored. Knowledge paths and every later gate
were `NOT_RUN`; zero provider/network/remote-ingest calls occurred.

This Amendment does not authorize a verification retry under Amendment 2. It
binds the new post-generator candidate as a fresh immutable starting point and
authorizes only the two still-missing knowledge paths plus the never-run gates.
DESIGN and SPEC do not change.

## Exact retained candidate binding — 26 protected paths

The retained candidate contains exactly the parent's 26 mandatory BUILD paths.
Its manifest is the UTF-8 sequence of repository-relative paths sorted by
Unicode code point, each encoded as
`path + NUL + lowercase_file_sha256 + LF`.

- path count: `26`;
- manifest SHA-256: `c7c1761c699494658b6d8853e1ebcc1703f5be52d6855a6be1ddb7478be601b8`;
- registry SHA-256: `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38`;
- generated catalog SHA-256: `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92`.

All 26 paths are byte-immutable during this continuation. The registry and
catalog must already parse/render `refinery-bridge` as `partial`; neither may
be written. `python scripts/generate_catalog.py --write` is prohibited.

## Exact repair-touch ceiling — 2 paths

The continuation may create or modify only:

1. `knowledge/PROJECT_CONTEXT.md`
2. `knowledge/manifest.json`

No catalog, source, fixture, test, helper, status, roadmap, validator, lock,
continuity, evidence or other knowledge path may change during continuation.

## Final exact BUILD changed set — 28 paths

The final diff against `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
must be exactly the immutable retained 26 paths plus the two knowledge paths
above. Governance authority and continuity paths are separately committed and
are not part of the BUILD diff.

## Ordered continuation

Run once in this exact order, stopping at the first non-zero command or
contract failure:

1. verify pushed authority lineage; immutable parent/Amendment/SPEC hashes;
   empty staged set; exact 26-path manifest and registry/catalog hashes; valid
   registry JSON; and `refinery-bridge` partial truth in both catalog surfaces;
2. update `knowledge/PROJECT_CONTEXT.md` to bounded
   `BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW` truth and update only the
   `IMPLEMENTATION_STATUS.json` and immutable `MODULE_REGISTRY.json` SHA-256
   pins in the `project-context` manifest entry;
3. run `python scripts/check_project_knowledge.py`;
4. run exactly once:
   `python -m pytest tests/unit/test_project_knowledge_pack.py tests/integration/test_project_knowledge_ingest_rehearsal.py -q`;
5. run `python scripts/generate_catalog.py --check`;
6. run the full non-live repository pytest suite once;
7. run `python scripts/check_session_state.py`,
   `python scripts/check_file_size.py`, and
   `python scripts/testing/validate_repository.py`;
8. run JSON/YAML parse, forbidden-import/I/O, secret and `git diff --check`
   checks;
9. verify exact final 28-path diff, exact two repair-touch paths, unchanged
   26-path retained manifest and empty staged set.

The retained refinery focused gates are not rerun. The catalog is checked but
not regenerated. No failed or successful command is repeated under this
Amendment.

## Knowledge constraints

- `PROJECT_CONTEXT.md` remains INTERNAL advisory orientation at no more than
  600 lines.
- It may state only that a deterministic local P3-A BUILD candidate is pending
  independent review.
- It must deny P3-A closure, runtime caller, provider/remote ingest,
  persistence, `data_scope` enforcement, retrieval/RAG, learning, production
  and Phase 3 completion.
- `knowledge/manifest.json` remains schema `1.0` and preserves entry order,
  ownership, classification, consumers, disposition, policies, triggers,
  dates and eligibility.
- Only the `IMPLEMENTATION_STATUS.json` and
  `docs/catalog/MODULE_REGISTRY.json` digest strings in the `project-context`
  source pins may change. The roadmap pin and all other manifest content remain
  unchanged.
- The focused integration test may invoke the pinned CVF-core helper only in
  its disposable local directory. This is local transformation, not remote
  ingest; it authorizes no provider/network/POST call or persistent index.

## Stop and claim boundary

Stop on missing review/fresh R2, any hash/digest/path drift, catalog write,
incorrect pin, failed gate, disclosure, prohibited call attempt or claim
expansion. There is no retry, diagnostic rerun or second invocation.

A pass yields only a dirty exact 28-path deterministic local BUILD candidate
pending independent BUILD review. It authorizes no BUILD commit/push,
self-review, FREEZE, runtime integration, P3-B/P3-C, retrieval/RAG, learning,
production integration or AI-governance claim.

## Required review and fresh human acknowledgment

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to the exact
Amendment 3 SHA-256, immutable 26-path digest, exact two repair paths, final
exact 28 paths and ordered unrun gates. After the authority checkpoint is
committed/pushed, the operator must send exactly:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-3-2026-08-03,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 2 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
