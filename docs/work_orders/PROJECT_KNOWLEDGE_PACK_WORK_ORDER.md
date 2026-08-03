# WORK ORDER — Project Knowledge Pack

- Tranche: `PROJECT-KNOWLEDGE-PACK-2026-08-03`
- Parent SPEC: `docs/specs/PROJECT_KNOWLEDGE_PACK_SPEC.md`
- Parent SPEC SHA-256:
  `858f519274a83d4182a69c6a76f4f9d22119e5420ceb634d0ba79627c6622439`
- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_AND_HUMAN_R2_APPROVAL`
- Active role: `WORK_ORDER_AUTHOR`

## 1. Exact final BUILD changed set

BUILD may change exactly these eight paths and no others:

1. `knowledge/README.md`
2. `knowledge/PROJECT_CONTEXT.md`
3. `knowledge/OPERATIONS_GLOSSARY.md`
4. `knowledge/GOVERNANCE_BOUNDARIES.md`
5. `knowledge/manifest.json`
6. `scripts/check_project_knowledge.py`
7. `tests/unit/test_project_knowledge_pack.py`
8. `tests/integration/test_project_knowledge_ingest_rehearsal.py`

Paths 1 is existing; paths 2-8 are new at the authorization baseline. No
governance, continuity, implementation-status, roadmap, catalog, source,
application/runtime, provider configuration or CVF-core path may change during
BUILD. A later C4 synchronization requires a separate Work Order and commit.

## 2. Governance package and checkpoints

The authorization package is exactly these seven governance paths:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`
3. `docs/decisions/PROJECT_KNOWLEDGE_PACK_DESIGN_REVIEW.md`
4. `docs/specs/PROJECT_KNOWLEDGE_PACK_SPEC.md`
5. `docs/decisions/PROJECT_KNOWLEDGE_PACK_SPEC_REVIEW.md`
6. `docs/work_orders/PROJECT_KNOWLEDGE_PACK_WORK_ORDER.md`
7. `docs/decisions/PROJECT_KNOWLEDGE_PACK_WORK_ORDER_AUTHORIZATION_REVIEW.md`

The authorization reviewer may create only path 7. After independent
`AUTHORIZATION_REVIEW_PASS` and explicit human R2 approval of this exact Work
Order, `COMMIT_STEWARD` commits and pushes exactly these seven paths. No BUILD
path may be staged or committed with them.

After that pushed authorization commit, a separate pre-BUILD continuity
checkpoint must change exactly these four paths:

1. `SESSION/SESSION_MEMORY.md`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`

That checkpoint records the exact authorization commit as BUILD baseline,
switches the role to `IMPLEMENTATION_WORKER`, keeps later queue items parked,
passes session/repository gates, and is committed/pushed separately. Only the
pushed checkpoint plus a clean `HEAD == origin/main` transfers BUILD authority.

## 3. Roles and execution order

1. `INDEPENDENT_AUTHORIZATION_REVIEWER` compares INTAKE, reviewed DESIGN,
   reviewed SPEC and this Work Order; no author self-approval.
2. Human operator gives explicit R2 approval for this exact eight-path BUILD.
3. `COMMIT_STEWARD` commits/pushes the exact seven-path governance package.
4. `SESSION_SYNC_STEWARD` creates and pushes the exact four-path pre-BUILD
   checkpoint; no BUILD edit is mixed into it.
5. `IMPLEMENTATION_WORKER` runs G6, then edits only the eight BUILD paths and
   implements SPEC R1-R13. The CVF core remains read-only.
6. The worker runs focused and repository gates, invokes the real pinned helper
   only through the authorized disposable integration rehearsal, proves exact
   cleanup and leaves the exact eight paths unstaged for review.
7. `INDEPENDENT_REVIEWER` checks source truth, exact diff, manifest pins,
   validator/tests, helper pin/source inspection, disposable output/cleanup,
   claim boundary and absence of external/provider activity.
8. Only `REVIEW_PASS` transfers the unchanged exact eight-path candidate to
   `COMMIT_STEWARD` for a separate BUILD commit/push. C4 remains separately
   unauthorized.

## 4. G6 pre-BUILD gate

Before any BUILD edit, require all of the following:

- clean `HEAD == origin/main == <pushed-authorization-resume-commit>`;
- authorization and human R2 receipts resolve and the SPEC hash equals the
  Work Order pin;
- exact four-path continuity checkpoint is present and session mirror passes;
- all eight BUILD paths match the baseline state (one tracked README, seven
  absent paths) and none is staged;
- core `HEAD == origin/main == manifest.cvfCoreCommit` and core is clean;
- helper raw-byte SHA-256 equals
  `856b99d9273b0384c40c05bc2132eae66e9dce20b9a9c8b75c3d91ae7016d2c6`;
- no repository `_index.json`, temporary rehearsal root, provider-call receipt,
  network sidecar or other runtime residue exists;
- workspace doctor is PASS, allowing only the already-bounded 24/1 legacy
  catalog warning.

Any failure stops before edit. G6 makes no helper, provider or network call.

## 5. BUILD requirements

- Implement the exact manifest/document/validator/rehearsal contracts and all
  R1-R13/AC-01..AC-12 from the pinned SPEC without weakening them.
- Generate source pins from current raw bytes at the authorized BUILD baseline;
  do not copy mutable source text into the pack.
- Keep `knowledge/README.md` operator-only and explicitly narrow the old
  automatic retrieval/injection claim to current downstream truth.
- Validator execution is deterministic, read-only and zero-provider; secret
  diagnostics never echo the matched value.
- Integration input is a system disposable directory containing exactly the
  three eligible basenames. `README.md` and manifest are excluded.
- Invoke only the exact pinned public-core helper after its byte hash and
  file-only token inspection pass. Do not copy/edit the helper.
- Do not POST, create a remote collection, open a network path, read provider
  configuration/secrets or invoke a provider.
- Remove the complete disposable root in `finally` on success and every
  induced failure; never write or retain repository `knowledge/_index.json`.
- Final BUILD diff is exactly eight paths, unstaged, with no runtime residue.

## 6. Required verification

Run at minimum:

```powershell
python scripts/check_project_knowledge.py
python -m pytest tests/unit/test_project_knowledge_pack.py -q
python -m pytest tests/integration/test_project_knowledge_ingest_rehearsal.py -q
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
```

Also require:

- parse every JSON file in the changed set;
- exact eight-path diff and no staged/outside path;
- exact source-pin recomputation;
- exact helper/core pin recomputation and source-token inspection;
- repository-wide `_index.json`/temporary-residue scan before and after tests;
- secret scan over the final changed set without printing matches;
- workspace doctor from the resolved pinned core;
- full non-live Python regression suite, with existing skips/warnings reported
  exactly rather than rounded into a broader claim.

The helper rehearsal is local chunk-transformation evidence only. No real
provider call is needed or authorized because BUILD makes no claim that CVF
controls AI/model behavior.

## 7. Independent review evidence

The reviewer must independently reproduce at least:

- G6 invariants and exact path classification;
- focused validator/unit/integration tests;
- source-pin, manifest-schema and citation-set checks;
- bare/prefixed/quoted/unmatched secret-assignment cases across Markdown and
  manifest strings, without printing the synthetic values in a receipt;
- helper/core raw hashes, source-token scan, exact eligible/index basename set,
  positive chunk coverage and README exclusion;
- cleanup on PASS and induced failure;
- repository/session/catalog/file-size/JSON/diff/secret/doctor gates;
- full non-live regression suite;
- zero provider receipt/call state, zero POST/external write and no broadened
  retrieval/Refinery/RAG/production claim.

The reviewer returns findings for repair without waiver. Any repair requires a
new bounded amendment if it would alter this Work Order, SPEC, path ceiling,
helper pin, claim boundary or authority sequence.

## 8. Commit ownership

- Governance authorization commit: `COMMIT_STEWARD`, exact seven paths in §2.
- Pre-BUILD checkpoint commit: `SESSION_SYNC_STEWARD` then
  `COMMIT_STEWARD`, exact four continuity paths in §2.
- BUILD commit: `COMMIT_STEWARD`, exact unchanged eight-path reviewed candidate
  only after independent `REVIEW_PASS`.
- C4: not authorized here; must be a new governed unit and separate commit.

Every commit is pushed to `origin main` before the next authority transfer. No
amend, squash, force-push or batching with another tranche is allowed.

## 9. Stop conditions

Stop immediately on missing/changed authorization, absent human R2 approval,
path overflow, protected-path drift, source/citation/continuity conflict,
source-pin or helper-pin mismatch, secret/sensitive/RESTRICTED content,
provider configuration access, provider/network/POST/external-write path,
core modification, repository `_index.json`, cleanup failure, staged residue,
failed test/gate, broadened claim, self-review, or missing independent review.
No provider retry is relevant or authorized because provider calls are zero.

## 10. Claim boundary

The later BUILD may establish only that a reviewed, source-cited,
classification-aware project knowledge pack passes deterministic local
validation and is transformed into disposable local chunks by the exact pinned
public-core helper. Helper source pin/inspection is not an OS-level zero-packet
proof. The tranche does not establish remote ingest, retrieval, automatic
context injection, provider/model behavior, DLP/minimization, Refinery
enforcement, RAG, learning memory, production governance or production
readiness.

## 11. Next governed move

Independent Work Order authorization review only. No BUILD, helper execution,
provider call, network/POST, external write, staging, commit, continuity edit or
later-queue work is authorized from this draft.
