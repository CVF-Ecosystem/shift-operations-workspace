# Work Order Amendment 4 — P3-A Independent-Review Repair

> **Binding correction:** The first authorization candidate incorrectly bound
> the protected-15 manifest to the culture-sensitive sorting result
> `dec7b368…da3c5`. Independent review `42eb1c29…03ef8` failed that candidate,
> no waiver. This corrected candidate changes only that digest to the explicitly
> reproduced typed ordinal value below; candidate bytes and the exact 13/15/28
> path partition are unchanged.

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-4-2026-08-03`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 3 SHA-256: `30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4`
- Corrected independent BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Last acknowledgment checkpoint: `3972bbb7202af63c60e49c44b3038b753bc976ac`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls during repair: `0/0/0`

## Trigger and retained review truth

Amendment 3 produced the exact 28-path deterministic local BUILD candidate and
its ordered worker evidence passed. Independent BUILD re-review then returned
`REVIEW_CHANGES_REQUIRED`, no waiver. Its original manifest-drift F1 is fully
retracted as a reviewer sorting error: a fresh typed ordinal calculation
reproduced the immutable 26-path digest `c7c1761c…01b8`, and focused refinery
tests passed `31`.

The corrected review disposition rests on F2-F6:

1. public result construction accepts zero-quality ready results, an unrelated
   candidate fingerprint and other combinations contrary to R20/R21/R24;
2. the claimed R27 matrix counts 28 labels rather than executing 28 bound
   independent cases;
3. `POLICY_DRIFT`, `STAGE_UNAVAILABLE` and sanitized unexpected-invariant
   fallback lack complete, tested execution paths;
4. receipt identifiers/collections and offsets are under-constrained, with an
   independent probe proving negative, reversed and out-of-bounds offsets are
   accepted;
5. the registry/catalog include an unrelated `cvf-application-profile` status
   change prohibited by Amendment 2.

These are implementation and coverage defects against the unchanged reviewed
SPEC. DESIGN and SPEC do not change. This Amendment authorizes only their
bounded repair and a fresh full independent BUILD review.

## Exact retained candidate binding — 28 paths

The retained candidate is exactly the parent's 26 mandatory BUILD paths plus
`knowledge/PROJECT_CONTEXT.md` and `knowledge/manifest.json`. Its manifest is
the UTF-8 sequence of repository-relative paths sorted with ordinal,
case-sensitive Unicode-code-point comparison, each encoded as
`path + NUL + lowercase_file_sha256 + LF`.

- path count: `28`;
- manifest SHA-256: `e43e53e4610a596d987f9f3a5c70a97ebfd35ffa4337f3bc3c8aacc9b8bc4eae`;
- staged path count: `0` at authoring.

Any mismatch before repair stops the invocation.

## Exact repair-touch ceiling — 13 paths

The repair may modify only:

1. `packages/refinery-bridge/src/refinery_bridge/controls.py`
2. `packages/refinery-bridge/src/refinery_bridge/receipt_models.py`
3. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
4. `packages/refinery-bridge/src/refinery_bridge/protection.py`
5. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
6. `tests/unit/_refinery_fixtures.py`
7. `tests/unit/test_refinery_models.py`
8. `tests/unit/test_refinery_pipeline.py`
9. `tests/unit/test_refinery_adversarial.py`
10. `tests/unit/test_refinery_contract.py`
11. `docs/catalog/MODULE_REGISTRY.json`
12. `docs/catalog/MODULE_CATALOG.md`
13. `knowledge/manifest.json`

The other 15 BUILD paths are byte-immutable. Under the same ordinal manifest
algorithm their protected digest is:

`ce531fb7fe4b8fa7c97aa29863cf1980a8665f5d74d21fb3d17259af37644784`

No new BUILD path may be created. The final changed set against the BUILD base
remains exactly the same 28 paths.

## Repair contract

### 1. Public-result invariants

- `RefineryResultV1` construction MUST mechanically bind quality components and
  total to the nine stage receipts exactly as R20 defines.
- A ready result MUST bind candidate provenance/quality fields to the public
  source and quality receipt, and MUST bind `candidate_fingerprint` to the
  canonical candidate preimage under R7/R23.
- Duplicate, quarantine and fallback dispositions MUST match the first failing
  stage reason and R21 precedence. Contradictory receipt/disposition/public
  combinations MUST be rejected at model construction.

### 2. Total fail-stop paths

- Add deterministic, typed stage-unavailable handling without adding I/O,
  discovery or provider behavior.
- Detect classification downgrade, unknown detector output or other policy
  drift as `POLICY_DRIFT` rather than silently accepting/coercing it.
- Sanitize arbitrary unexpected stage exceptions to the current stage's
  `STAGE_INVARIANT_ERROR`; never expose exception text, stack, raw input or
  matched/redacted values.
- Preserve exact stage ordering, one first `FAIL`, later `NOT_RUN`, disposition
  precedence and the closed reason/stage table.

### 3. Receipt and safe-boundary validation

- Apply the existing R4 safe-string constraints to every public identifier,
  version, link, count key, candidate label and receipt field that carries such
  data.
- Reject, rather than sort/deduplicate, duplicate or unsorted boundary input.
- Reject offsets unless they are integer pairs, non-negative, strictly
  increasing within each span, sorted, non-overlapping and bounded by the R5
  maximum text length. Where candidate text is present, bind relevant offsets
  to its actual length.

### 4. Executable R27 matrix

- Replace the label-count assertion with at least 28 independently executed,
  named cases bound one-to-one to the R27 list.
- The matrix MUST include control-version substitution, qualified-time fixture
  through the pipeline, terminology overlap/cycle, sensitivity retention and
  escalation, downgrade/policy drift, stage unavailable, sanitized unexpected
  invariant fallback, exception/log/snapshot disclosure checks, and the
  remaining R27 cases already covered elsewhere.
- Shared helpers are permitted only in the five authorized test paths. A label
  without an executed assertion does not satisfy a case.

### 5. Catalog and knowledge correction

- Restore only `cvf-application-profile.status` from the unrelated candidate
  value `partial` to its BUILD-base value `contract-only`.
- Keep `refinery-bridge.status=partial` and its bounded no-runtime-caller text.
- Run the existing catalog generator once after source/test repair; generated
  metrics, timestamp and Markdown changes are permitted only in the two catalog
  paths.
- Update only the `docs/catalog/MODULE_REGISTRY.json` SHA-256 source pin in the
  active `project-context` entry of `knowledge/manifest.json`. Preserve every
  other manifest byte semantically, including ordering and the status/roadmap
  pins.

## Ordered repair and evidence

Run once in this exact order, stopping at the first non-zero command or
contract failure:

1. verify pushed authority lineage; parent/Amendment/SPEC/review hashes; empty
   staged set; exact retained 28-path manifest; and protected-15 digest;
2. repair only the ten authorized source/test paths for F2-F5;
3. run the focused refinery tests once;
4. run a dedicated public-invariant probe once, including zero-quality ready,
   unbound fingerprint, invalid offsets, disposition mismatch, policy drift,
   stage unavailable and sanitized unexpected exception cases;
5. restore only the unrelated registry status, then run
   `python scripts/generate_catalog.py --write` once;
6. update only the registry source-pin digest in `knowledge/manifest.json`;
7. run `python scripts/check_project_knowledge.py` once;
8. run the focused Knowledge Pack unit/local-helper rehearsal once;
9. run `python scripts/generate_catalog.py --check` once;
10. run the full non-live repository pytest suite once;
11. run session-state, file-size and repository validators; JSON/YAML parse,
    forbidden-import/I/O, secret and `git diff --check` checks once;
12. verify exact final 28-path diff, exact repair touches within the 13-path
    ceiling, unchanged protected-15 digest and empty staged set.

No failed or successful command is repeated under this Amendment. Stop on an
unapproved path, missing case, hash/digest drift, unsafe output, catalog or
knowledge drift, test/gate failure, prohibited call attempt or claim expansion.

## Call and claim boundary

The invocation permits zero provider, network and remote-ingest calls. It adds
no filesystem/database/environment discovery, runtime caller, persistent index
or external side effect. Mock output is not governance proof and is not used.

A pass yields only a dirty exact 28-path deterministic local BUILD candidate
pending fresh independent BUILD review. It authorizes no BUILD commit/push,
self-review, FREEZE, runtime integration, `data_scope` enforcement, P3-B/P3-C,
retrieval/RAG, learning, production integration or Phase 3 completion claim.

## Required independent review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to the exact
Amendment 4 SHA-256, corrected BUILD review, retained/protected digests, exact
13 repair paths, final exact 28 BUILD paths, ordered gates and zero-call
boundary. After that authority and synchronized continuity are committed and
pushed while all 28 BUILD paths remain unstaged, the operator must send exactly:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-4-2026-08-03,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 13 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one repair invocation only and no retry.
