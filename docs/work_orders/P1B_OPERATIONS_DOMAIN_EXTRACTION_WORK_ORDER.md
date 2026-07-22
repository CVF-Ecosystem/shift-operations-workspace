# WORK ORDER — P1-B Operations-Domain Extraction

- Work order id: `WO-P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase at authoring time: `WORK_ORDER`
- Risk: **R2** — REVIEWER must be independent from IMPLEMENTATION_WORKER
- Status: **DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.**
- Design: `docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md`
- Specification: `docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC.md`
- Baseline commit: `ed3d94431dc55530bb7328514646adff36cff47b`
  (`HEAD == origin/main`, worktree clean, doctor `24/24`, suite `221 passed`)

## 1. Authorized objective

Move the canonical definition of the twelve operational models and three
lifecycle guards from `workspace_api.domain` into a real
`operations_domain` package, leave proven-identity compatibility shims behind,
and repoint import sites — with **zero observable behaviour change**.

Nothing else. Every ambiguity resolves to *stop and report*, never to *decide
and proceed*.

## 2. Roles

| Role | Holder | Notes |
|---|---|---|
| ORCHESTRATOR / SPEC_AUTHOR / WORK_ORDER_AUTHOR | Claude (this context) | Authored the three authorization artifacts. Held **no** implementation role at that checkpoint. |
| REVIEWER (independent) | Codex | Reviews the authorization artifacts, then independently reviews BUILD by **re-running** every AC. Must not accept a reported number without reproducing it. |
| COMMIT_STEWARD | Codex | Verifies the changed set and owns every commit action. |
| IMPLEMENTATION_WORKER | Claude — **only after §7 approval** | Role transition must be stated explicitly before the first edit. |
| SESSION_SYNC_STEWARD | assigned at §7 / §11 | Owns continuity, catalog, roadmap and status synchronization. |

R2 role separation is mandatory: the context that implements must not be the
context that approves.

## 3. Changed-set allowlist

Only the paths below may be created or modified, and only in the commit named
in §10. Anything else is a stop condition.

**Count provenance.** Every figure in this WORK_ORDER is reproducible from the
baseline commit `ed3d944` by the command quoted beside it. The import inventory
the allowlist is derived from is:

```bash
# 43 import statements across 30 files
grep -rnE "^[[:space:]]*(from|import)[[:space:]]+workspace_api\.domain" \
     --include=*.py apps packages scripts tests | grep -v __pycache__
```

This pattern intentionally matches indented (function-local) imports as well as
module-level ones; a `^from|^import`-anchored pattern undercounts. See ADR
§1.2.1 for the full counting rules and the two exclusions.

### 3.1 C3 — BUILD commit

**Create:**

```
packages/operations-domain/pyproject.toml
packages/operations-domain/src/operations_domain/__init__.py
packages/operations-domain/src/operations_domain/models.py
packages/operations-domain/src/operations_domain/lifecycle.py
tests/unit/test_operations_domain_boundary.py
tests/unit/test_operations_domain_shim_identity.py
tests/unit/test_operations_domain_serialization.py
```

**Modify — package docs and path registries (5 files):**

```
packages/operations-domain/README.md
pyproject.toml                                    # pythonpath entry only
scripts/seed_dev_users.py                         # sys.path bootstrap (+ import path)
scripts/apply_migrations.py                       # sys.path bootstrap only
scripts/run_identity_live_governance_evidence.py  # sys.path bootstrap only
```

**Modify — shims (2 files):**

```
apps/workspace-api/src/workspace_api/domain/models.py
apps/workspace-api/src/workspace_api/domain/lifecycle.py
```

**Modify — application import sites (13 files):**

```
apps/workspace-api/src/workspace_api/api/corrections/router.py
apps/workspace-api/src/workspace_api/api/customer_requests/router.py
apps/workspace-api/src/workspace_api/api/events/router.py
apps/workspace-api/src/workspace_api/api/messages/router.py
apps/workspace-api/src/workspace_api/api/shifts/router.py
apps/workspace-api/src/workspace_api/api/tasks/router.py
apps/workspace-api/src/workspace_api/application/correction_service.py
apps/workspace-api/src/workspace_api/application/customer_request_service.py
apps/workspace-api/src/workspace_api/application/services.py
apps/workspace-api/src/workspace_api/application/shift_service.py
apps/workspace-api/src/workspace_api/application/task_service.py
apps/workspace-api/src/workspace_api/infrastructure/repository.py
apps/workspace-api/src/workspace_api/infrastructure/ledger_factory.py
```

`ledger_factory.py` is listed **only** to permit a comment documenting
exception E1 (SPEC R5.2). Its `SqlLedger(..., models=domain_models)` call and
its import of the shim module must not change.

**Modify — test import sites (16 files):**

```
apps/workspace-api/src/workspace_api/tests/test_lifecycle.py
tests/cvf/test_atomic_mutation_audit.py
tests/cvf/test_auth_login.py
tests/cvf/test_correction_vertical.py
tests/cvf/test_customer_request_repair.py
tests/cvf/test_customer_request_vertical.py
tests/cvf/test_freeze_invariant.py
tests/cvf/test_ledger_protocol.py
tests/cvf/test_shift_close_governance.py
tests/cvf/test_task_vertical.py
tests/cvf/test_vertical_end_to_end.py
tests/integration/test_evidence_persistence.py
tests/integration/test_freeze.py
tests/integration/test_sql_ledger_integrity.py
tests/integration/test_sql_ledger_sqlite.py
tests/unit/test_state_machine.py
```

`tests/unit/test_state_machine.py` was missing from the first draft of this
allowlist and was added at authorization review (F1). It carries two
`workspace_api.domain` imports (`assert_transition`, `DataState`) and is
therefore an unavoidable edit site; omitting it would have forced a
mid-BUILD S1 stop.

In these files, **only import lines may change.** Assertions, fixtures,
parameters and test names are frozen. Rewriting an assertion to make a test
pass is a stop condition (§8, S4). Note that
`tests/cvf/test_freeze_invariant.py` has **two** edit sites: a module-level
import block and a function-local `from workspace_api.domain.models import
TaskStatus` at line 168.

**C3 path totals:** 7 created + 36 modified (5 registries/docs + 2 shims +
13 application + 16 test) = **43 paths**. A changed set with a different total
is an S1 stop until reconciled against this list.

### 3.2 Two rules that are easy to get wrong

**Rule A — SqlLedger injection sites keep the shim namespace.**
At baseline there are **15 real `SqlLedger(...)` constructor calls across 9
files** — 14 calls in **8 test modules**, plus the single production call in
`ledger_factory.py`. Counted with:

```bash
grep -rnE "SqlLedger\(" --include=*.py apps packages scripts tests | grep -v __pycache__
```

which yields 16 matches; the extra one is prose inside the
`tests/cvf/test_shift_close_governance.py` module docstring
(`"InMemoryLedger and SqlLedger(SQLite) backends."`) and is **not** a
constructor call.

The 8 test modules are: `test_atomic_mutation_audit` (1),
`test_customer_request_vertical` (1), `test_freeze_invariant` (1),
`test_ledger_protocol` (1), `test_shift_close_governance` (1),
`test_evidence_persistence` (2), `test_sql_ledger_integrity` (1),
`test_sql_ledger_sqlite` (6). In each, the line
`from workspace_api.domain import models as domain_models` **must stay** — the
injected namespace has to expose `User`, which does not move (ADR §2.2, §2.5).
Only their *type* imports move to `operations_domain.models`.

`tests/cvf/test_customer_request_repair.py` was listed here in the first draft
and is **removed**: it constructs no `SqlLedger` (it only annotates a helper
parameter and calls `domain_models.Message(...)`). Its
`from workspace_api.domain import models as domain_models` alias therefore
**does** migrate, to `from operations_domain import models as domain_models`.

**Rule B — `User` stays put.** `repository.py`, `scripts/seed_dev_users.py`
and `tests/cvf/test_auth_login.py` continue to import `User` from
`workspace_api.domain.models`. Do not relocate it, do not add it to
`operations_domain`.

### 3.3 C2 and C4 commits

C2 (pre-BUILD continuity, §7) and C4 (REVIEW/FREEZE continuity, §11) have their
own allowlists, stated in those sections. Their paths are **prohibited** in C3
and vice versa.

## 4. Prohibited paths

No file under these paths may be created, modified, deleted or renamed by this
tranche in any commit:

```
.cvf/**                                  # incl. manifest.json — pinned at da9a122
database/**                              # schema, migrations, views
packages/cvf-runtime/**
packages/cvf-application-profile/**      # incl. known-principals.yaml
packages/operations-ledger/**            # the injection seam - zero-line diff required
packages/workspace-contracts/**          # API contracts / JSON schemas
apps/workspace-api/src/workspace_api/auth/**
apps/workspace-api/src/workspace_api/main.py
apps/workspace-api/src/workspace_api/config.py
apps/workspace-api/src/workspace_api/dependencies.py
apps/workspace-api/src/workspace_api/middleware/**
apps/workspace-web/**
apps/integration-edge/**
apps/workspace-worker/**
infrastructure/**                        # incl. the pre-existing Dockerfile gap
docs/decisions/**  docs/specs/**  docs/work_orders/**   # frozen after C1
.githooks/**  .github/**  Makefile
```

`packages/operations-domain/{approvals,audit,corrections,customers,events,handovers,incidents,messages,reports,shifts,tasks}/`
— the **eleven** README-only blueprint directories, enumerated in full and
countable with
`find packages/operations-domain -mindepth 1 -maxdepth 1 -type d` — are also
prohibited: not deleted, renamed, populated or reorganized. Only `README.md`,
`pyproject.toml` and the new `src/` tree are in scope.

## 5. Explicitly out of scope

Not authorized, and not to be "fixed while we're in there":

- API contract or response-schema changes;
- database schema or migration changes;
- lifecycle-semantics or enum-value changes;
- CVF gate behaviour changes;
- authentication, approval, or `known-principals.yaml` — High Finding #4 stays
  **OPEN**;
- incidents / handovers (lane 3) and frontend (lane 4);
- the `known-principals.yaml` ↔ users reconciliation (lane 2), including any
  relocation of `User`;
- refactoring `SqlLedger(models=...)` or the `Ledger` Protocol;
- repairing `infrastructure/docker/Dockerfile.api`'s pre-existing missing
  package paths (ADR §4.2);
- any provider / Alibaba call;
- reading, writing, printing or logging any API key or `.env` secret;
- any claim that the Phase 1 exit gate is met or that PostgreSQL was live
  verified.

## 6. Required evidence

The IMPLEMENTATION_WORKER records, and the REVIEWER independently re-runs:

| # | Command | Required result |
|---|---|---|
| E-1 | `git rev-parse HEAD origin/main` | equal at start of BUILD |
| E-2 | `git status --porcelain` / `git diff --stat` | changed set ⊆ §3.1 |
| E-3 | `git diff --stat <base>..HEAD -- packages/operations-ledger/` | **empty** (AC-10) |
| E-4 | `python -m pytest -q tests/unit/test_operations_domain_boundary.py tests/unit/test_operations_domain_shim_identity.py tests/unit/test_operations_domain_serialization.py` | all pass (AC-01…AC-08). The REVIEWER additionally confirms the isolation subprocess is built per SPEC §4.3 (site-packages retained, `pydantic` guard present, negative import checks) and that no round trip uses `model_validate(<json string>)` (SPEC §4.4). |
| E-5 | `python -m pytest -q tests/integration tests/cvf` | all pass (AC-11) |
| E-6 | `python -m pytest -q` | **≥ 221 passed**, 0 failed, 0 errors (AC-12) |
| E-7 | `python scripts/testing/validate_repository.py` | PASS (AC-13) |
| E-8 | `python scripts/generate_catalog.py --check` | PASS (AC-13) |
| E-9 | `python scripts/check_session_state.py` | PASS (AC-13) |
| E-10 | `python scripts/check_file_size.py` | PASS (AC-13) |
| E-11 | `git diff --check` | clean, no whitespace errors |
| E-12 | rollback rehearsal in a **temporary worktree/clone** (§12.1) | C3 paths match `C3_PARENT`; C1/C2 intact; suite exactly **221 passed**; temporary worktree removed (AC-18, SPEC §4.2) |
| E-13 | workspace doctor (`-ProjectPath`) | `PASS (24/24)` |

Every number must be quoted from the run that produced it. Copying a count
from a prior handoff is the spec-drift finding recorded as Medium #7 in
`EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md` and is itself a stop condition.

## 7. Pre-BUILD gates (all mandatory, in order)

BUILD may not begin until **every** gate below is satisfied.

**G1 — Independent review of the authorization artifacts.** Codex reviews this
WORK_ORDER, the SPEC and the ADR for internal consistency and boundary
correctness, and returns `REVIEW_PASS` or `REVIEW_CHANGES_REQUIRED`.

**G2 — Authorization artifacts committed separately.** Codex, as
COMMIT_STEWARD, commits **exactly** the three files:

```
docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md
docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC.md
docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER.md
```

Zero implementation files. This commit (**C1**) is what puts
DESIGN → SPEC → WORK_ORDER ahead of BUILD in the commit graph itself, the same
proof structure `CVF-CORE-PIN-2026-07-23` used at `76e7360`.

**G3 — Operator approval of this WORK_ORDER.** The operator explicitly approves
this document (intact, or amended and re-reviewed). Absent that approval, BUILD
is prohibited. This is the gate whose absence made `cd36b27` an unauthorized
build candidate.

**G4 — Continuity records the operator's lane choice.** *After* G1–G3, and
*before* BUILD, the canonical continuity surfaces are updated to record that
the operator selected **P1-B** as lane 1 of four, resolving the drift that
`CVF-CORE-PIN-2026-07-23` deliberately left open. Commit **C2**, allowlist:

```
SESSION/ACTIVE_SESSION_STATE.json      # active_handoff, next_allowed_move, activePhase, activeRole
SESSION/SESSION_MEMORY.md              # drift resolved by operator; P1-B open
CVF_SESSION/ACTIVE_SESSION_STATE.json  # compatibility mirror only
SESSION/handoffs/AGENT_HANDOFF_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md   # new
```

C2 must record: the operator's four-lane order; that only lane 1 is open; the
tranche id; the C1 commit hash; the role route; and that BUILD had not yet
started when C2 was written. It must **not** claim any implementation result.
`python scripts/check_session_state.py` must pass before C2 is committed
(mirror-drift check).

**G5 — Role transition stated.** Claude states the transition to
IMPLEMENTATION_WORKER explicitly before the first source edit.

**G6 — Clean start.** `HEAD == origin/main`, worktree clean, doctor `24/24`,
suite `221 passed`, re-verified at that moment — not assumed from this
document.

## 8. Stop conditions

Stop immediately, revert nothing without instruction, and report:

- **S1** — a required change falls outside §3's allowlist, or any §4 path would
  be touched.
- **S2** — `packages/operations-ledger/` shows any diff (E-3 non-empty).
- **S3** — the full suite drops below **221 passed**, or any test fails or
  errors.
- **S4** — making a test pass would require editing its assertions, fixtures or
  parameters rather than only its imports.
- **S5** — an import cycle appears, or `operations_domain` needs anything from
  `workspace_api` / `operations_ledger` / `cvf_runtime`.
- **S6** — serialization, JSON schema (compared as canonical bytes per SPEC
  §4.4), OpenAPI output, an enum value, or a
  lifecycle transition differs from baseline in any byte.
- **S7** — `User` appears to need relocation, or the `models=` injection
  namespace appears to need changing.
- **S8** — any validator (E-7…E-10) fails, `git diff --check` reports an error,
  or the rollback rehearsal (§12.1) fails any of its three assertions or leaves
  a temporary worktree/clone behind.
- **S9** — the operator has not approved this WORK_ORDER (G3), or C1/C2 have
  not landed in that order.
- **S10** — any temptation to open lanes 2, 3 or 4, to call a provider, or to
  read a secret.
- **S11** — a `.md` artifact would exceed the file-size hard limit (600 lines);
  split or rotate per `docs/reference/FILE_SIZE_GUARD.md` rather than
  compressing prose to slip under the guard.

## 9. Commit ownership and git discipline

- **Codex is COMMIT_STEWARD.** Claude does **not** stage, commit, amend, push,
  or create branches at any point unless the operator reassigns the role in
  writing.
- **Never** `git add -A` or `git add .`. Every commit stages explicitly
  enumerated paths, matched against the allowlist for that commit.
- **No** `--amend`, `rebase`, `squash`, `reset --hard`, `checkout --`, or
  `push --force` — on any commit, ever. `cd36b27` and all history stay intact.
- **No scratch branch in the primary workspace.** The primary worktree stays on
  `main` for the whole tranche. Rollback rehearsal happens in a temporary
  `git worktree`/clone outside the project directory and is cleaned up (§12.1).
- One tranche per commit; no batching. Each message names the tranche id and
  the verification result.
- Push to `origin main` after each commit, per `CONTRIBUTING.md`.

## 10. Commit plan

| # | Contents | Owner | Gate |
|---|---|---|---|
| **C1** | The three authorization artifacts only | COMMIT_STEWARD | after G1 |
| **C2** | Pre-BUILD continuity: operator lane acknowledgment (§7 G4 allowlist) | COMMIT_STEWARD | after G2, G3 |
| **C3** | BUILD: §3.1 allowlist only — source, tests, path registries | COMMIT_STEWARD | after independent REVIEW_PASS on all ACs |
| **C4** | REVIEW/FREEZE continuity + catalog + roadmap + status (§11) | COMMIT_STEWARD | only if explicitly authorized at FREEZE |

C3 must contain **no** continuity, catalog, roadmap or status file. C4 must
contain **no** source or test file. A commit that mixes them violates this
project's commit discipline and the containment proof this tranche relies on.

## 11. C4 — REVIEW / FREEZE closure (authorized only at FREEZE)

Allowlist, and only from observed source truth:

```
docs/catalog/MODULE_REGISTRY.json          # operations-domain stub -> partial; metrics regenerated
docs/catalog/MODULE_CATALOG.md             # via `python scripts/generate_catalog.py --write` only
docs/implementation/EXECUTION_ROADMAP.md   # tick P1-B [x]; record bounded scope
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/handoffs/AGENT_HANDOFF_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md
```

Constraints:

- `operations-domain` → **`partial`**, never `enforced` (SPEC AC-14). Justify
  with the real LOC/file counts; incidents, handovers, reports and approvals
  still have no models.
- `MODULE_CATALOG.md` is **generated**; never hand-edited. `metrics` in the
  registry is likewise never hand-edited.
- Ticking P1-B `[x]` closes a **roadmap item**, not the Phase 1 exit gate.
  PostgreSQL live round-trip remains an open pre-ship limitation and its
  wording must survive verbatim (AC-16).
- The FREEZE record must state the boundary in §5 and must not claim any
  governance/AI evidence.
- `python scripts/check_session_state.py` must pass before C4 is committed.

## 12. Rollback plan

### 12.1 `C3_PARENT` and the rehearsal environment

**Record `C3_PARENT` immediately before the BUILD commit is created:**

```bash
git rev-parse HEAD    # -> C3_PARENT ; in the planned sequence this is C2
```

Quote that hash in the evidence. It is the reference point for every rollback
assertion — **not** `ed3d944`.

**The rehearsal must not mutate the primary workspace.** No branch is created,
switched or deleted in it; no `checkout`, `reset` or `revert` is run against
the project worktree. Use a temporary `git worktree` (preferred) or a temporary
clone, rooted **outside** the project directory — the session scratchpad
directory is an appropriate location.

```bash
# detached temporary worktree at the BUILD commit, outside the project tree
git worktree add --detach "<temp-path>" <C3>
# inside the temporary worktree ONLY
git -C "<temp-path>" revert --no-edit <C3>
```

Assertions after the revert, in the temporary worktree:

1. `git -C "<temp-path>" diff <C3_PARENT> -- <each C3 source/test/config path>`
   is **empty** — scoped to C3's paths, compared against `C3_PARENT`, never
   whole-repo and never against `ed3d944`.
2. **C1 and C2 are still present and unmodified.** The authorization artifacts
   and the continuity acknowledgment are legitimate history; a "rollback" that
   erased them is a failure, not a success.
3. `python -m pytest -q` reports exactly the **221 passed** baseline.

Cleanup, mandatory and verified:

```bash
git worktree remove --force "<temp-path>"
git worktree prune
git worktree list                 # only the primary worktree remains
git status --porcelain            # in the primary workspace: unchanged by the rehearsal
```

If a temporary clone was used instead, delete the clone directory and confirm
it is gone. Leaving a stale worktree registration behind is an S8 stop.

### 12.2 Real rollback, if ever needed

1. **Before C3 is pushed** — discard the working tree for the §3.1 paths only.
2. **After C3** — `git revert` the single BUILD commit (a new commit; never an
   amend or a reset). Because the shims keep every consumer signature unchanged
   (ADR §2.4), the revert is complete: C3's paths return to `C3_PARENT` and the
   suite returns to the **221 passed** baseline, exactly as rehearsed at E-12.
   C1 and C2 remain in history.
3. **After C4** — revert C4 independently; it shares no path with C3.
4. No schema, migration or data change exists, so rollback needs no data step.
5. No history rewrite in any scenario.

## 13. Checkpoint state at the time of writing

Authored by Claude as ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR. At this
checkpoint:

- exactly three files exist as uncommitted changes — the ADR, the SPEC and this
  WORK_ORDER;
- no implementation, continuity, catalog, roadmap or status file was touched;
- nothing was staged, committed, or pushed;
- no BUILD action was taken;
- no provider was called and no secret was read.

### 13.1 Authorization-review revision 1 (2026-07-23)

The first independent authorization review returned
`REVIEW_CHANGES_REQUIRED` with four findings. All four are resolved in this
revision, with no change to the tranche's scope or boundary:

| Finding | Resolution |
|---|---|
| **F1** — `tests/unit/test_state_machine.py` missing from the allowlist | Added to §3.1 (test import sites now **16**); C3 path total restated as **43**. Import-lines-only, like its peers. |
| **F2** — AC-04 asserted identity against one module | Split per module pair: SPEC §4.1 AC-04a (12 types, `…domain.models` ↔ `operations_domain.models`) and AC-04b (3 functions, `…domain.lifecycle` ↔ `operations_domain.lifecycle`); R4.2 and the test-artifact description updated. |
| **F3** — rollback rehearsal used a scratch branch and compared against `ed3d944` | Rewritten as §12.1 / SPEC §4.2: temporary worktree or clone outside the primary workspace, `C3_PARENT` recorded before C3, path-scoped comparison against `C3_PARENT`, C1/C2 explicitly required to survive, baseline 221, mandatory verified cleanup. E-12 and S8 updated. |
| **F4** — inventory figures wrong | Corrected to **11** blueprint subdirectories (enumerated), **43** import statements across **30** files, **15** real `SqlLedger(...)` calls across **9** files (docstring match excluded). Counting commands are now quoted in ADR §1.2.1, WORK_ORDER §3 and §3.2. `test_customer_request_repair` removed from the SqlLedger-injection list — it constructs no ledger. |

Checkpoint state is otherwise unchanged: three uncommitted files, nothing
staged, nothing built, no provider call, no secret read.

### 13.2 Authorization-review revision 2 (2026-07-23)

The second independent review confirmed F1–F4 resolved and raised two new
findings, both about verification methods that would not have proven what they
claimed. Both are resolved here; scope and boundary are unchanged.

| Finding | Resolution |
|---|---|
| **F5** — AC-01/R7 replaced the whole `sys.path`, which would make `pydantic` unimportable and the isolation check meaningless | Rewritten as **repository-scoped** isolation (SPEC §4.3, R7.1/R7.2, ADR §2.7): stdlib and site-packages retained, `packages/operations-domain/src` added, every other repository source root removed (`apps/workspace-api/src`, `packages/operations-ledger/src`, `packages/cvf-runtime/src`, repo root), `PYTHONPATH` cleared, run from a temporary cwd outside the repository. Adds a `pydantic`-importable guard so a pass cannot mean "nothing could import", and requires the three forbidden modules to be both absent from `sys.modules` **and** non-importable. AC-01/AC-15 and the test-artifact description updated. |
| **F6** — AC-06 used `model_validate(<json string>)` and left "byte-identical" undefined for dicts | Rewritten in SPEC §4.4 and R8.1/R8.4: `model_validate(model_dump())` for the Python-object round trip, `model_validate_json(model_dump_json())` for the JSON round trip, `model_validate(<json string>)` explicitly forbidden. `model_json_schema()` and `app.openapi()` are compared as canonical bytes via a shared `canonical()` helper using `json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`, with golden captures produced by the same helper at `ed3d944`. AC-06, AC-09, S6 and the test-artifact description updated. |

Returned checkpoint: `READY_FOR_INDEPENDENT_AUTHORIZATION_RE_REVIEW_2`.
