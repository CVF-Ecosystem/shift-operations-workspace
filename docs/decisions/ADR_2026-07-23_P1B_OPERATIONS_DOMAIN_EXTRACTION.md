# ADR 2026-07-23 — Extract operational domain models into `operations-domain`

- ADR id: `ADR-2026-07-23-P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase at authoring time: `DESIGN`
- Risk: **R2** — the change is behaviour-neutral by intent, but it rewrites the
  import boundary of every governed vertical and touches model identity,
  Pydantic serialization, the ledger row-mapping seam and the catalog. A silent
  duplicate class definition here would break `isinstance` checks and ledger
  round-trips across the whole application.
- Status: **PROPOSED** — awaiting independent authorization-artifact REVIEW and
  operator approval of the WORK_ORDER. **No BUILD has been performed.**
- Specification: `docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC.md`
- Work order: `docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER.md`

## 1. Context

### 1.1 Operator lane decision (INTAKE)

The `CVF-CORE-PIN-2026-07-23` FREEZE recorded an unresolved continuity drift
and deliberately left it to the operator: `CONTRIBUTING.md:21` rules that the
next unchecked roadmap item is taken in order, `EXECUTION_ROADMAP.md:207` shows
that item is **P1-B**, while the recorded lane list in
`SESSION/ACTIVE_SESSION_STATE.json` omitted P1-B.

The operator has now resolved it explicitly, confirming this order:

1. **P1-B operations-domain extraction** ← the only lane opened
2. `known-principals.yaml` ↔ authenticated users
3. P2-A incidents / handovers
4. P2-C frontend

Lanes 2–4 are **not** opened by this tranche and must not be implemented.
Recording that acknowledgment into canonical continuity is a **pre-BUILD gate**
governed by the WORK_ORDER (§7 there), not something this DESIGN checkpoint
performs.

### 1.2 Observed state (verified read-only at `ed3d944`, 2026-07-23)

| Fact | Verified value |
|---|---|
| `HEAD` == `origin/main` | `ed3d94431dc55530bb7328514646adff36cff47b` |
| Worktree | clean |
| Workspace doctor | `PASS (24/24)` |
| Full suite | `221 passed` (run, not copied from a file) |
| `packages/operations-domain/` | **11 README-only directories, zero Python files, zero LOC** — registry status `stub` |
| Canonical model file today | `apps/workspace-api/src/workspace_api/domain/models.py` (153 lines) |
| Canonical lifecycle file today | `apps/workspace-api/src/workspace_api/domain/lifecycle.py` (61 lines) |
| Import statements referencing `workspace_api.domain.*` | **43 statements across 30 files** |
| Real `SqlLedger(...)` constructor calls | **15 calls across 9 files** |
| Reverse imports (`packages/**` importing `workspace_api`) | **none** — one prose mention in a `cvf_runtime/identity.py` docstring only |

### 1.2.1 How these numbers are counted (reproducible)

Every count in this ADR, the SPEC and the WORK_ORDER is produced by one of the
commands below, run from the repository root at `ed3d944`. A re-reviewer must
re-run them rather than trust the figure.

```bash
# 11 README-only blueprint subdirectories
find packages/operations-domain -mindepth 1 -maxdepth 1 -type d | sort

# 43 import statements across 30 files
grep -rnE "^[[:space:]]*(from|import)[[:space:]]+workspace_api\.domain" \
     --include=*.py apps packages scripts tests | grep -v __pycache__

# 15 real SqlLedger(...) constructor calls across 9 files
# (the raw pattern yields 16 matches; one is prose inside the
#  tests/cvf/test_shift_close_governance.py module docstring and is excluded)
grep -rnE "SqlLedger\(" --include=*.py apps packages scripts tests \
     | grep -v __pycache__
```

Notes that matter when re-counting:

- The 43 figure counts **import statements**, not physical lines: a
  parenthesised multi-line `from ... import (` block is one statement.
- One of the 43 is **function-local**, not module-level:
  `tests/cvf/test_freeze_invariant.py:168`. A module-level-only pattern
  undercounts by one and misses that file's second edit site.
- `apps/workspace-api/src/workspace_api/domain/lifecycle.py:1` imports
  `from .models import ...` — a *relative* import inside the package being
  refactored. It is deliberately **excluded** from the 43/30 figures (it is not
  a consumer of the boundary; it is the boundary), but it is still an edit site
  and appears in the WORK_ORDER allowlist as one of the two shims.

### 1.3 The actual coupling problem

There is no *static* reverse import today, because `SqlLedger` avoids one by
taking a `models` **namespace object** at construction:

```python
# apps/workspace-api/src/workspace_api/infrastructure/ledger_factory.py:27
return SqlLedger(settings.database_url, models=domain_models)
```

`operations_ledger/_rows.py` then calls `models.OperationalEvent(...)`,
`models.Task(...)`, `models.CustomerRequest(...)`, `models.User(...)`,
`models.EvidenceRef(...)`, `models.Correction(...)`, and `sql_ledger.py` calls
`self.models.Shift(...)` / `self.models.ShiftStatus`.

The `Ledger` Protocol docstring states the consequence in its own words:

> *"Domain records are typed loosely here (the domain models live in the
> application layer today; when they move to operations-domain this Protocol
> can import them directly)."*

So the coupling is **structural and runtime**, not textual: every consumer of
the persistence layer — **15 real `SqlLedger(...)` constructor calls across 9
files** (14 in 8 test modules, plus the one production call in
`ledger_factory.py`) and `scripts/seed_dev_users.py` — must reach **into the
application package** to obtain the domain vocabulary. A package that is
architecturally *below* `workspace-api` in the dependency order
(`contracts → domain → ledger → core workspace`, per `EXECUTION_ROADMAP.md:9`)
can only be exercised by importing from *above* it. That is the dependency
inversion P1-B exists to remove.

## 2. Decision

**Create a real Python package at
`packages/operations-domain/src/operations_domain/`, move the operational
models and their lifecycle guards there as the single canonical definition, and
leave `workspace_api.domain.models` / `workspace_api.domain.lifecycle` as pure
re-export shims that define no class of their own — with the single, explicitly
reasoned exception of `User`.**

Decomposed:

- **D1** — New package `operations_domain` with `models.py` and `lifecycle.py`.
  It imports only the standard library and `pydantic`. It imports nothing from
  `workspace_api`, `operations_ledger`, or `cvf_runtime`.
- **D2** — The twelve operational types move verbatim (§2.1).
- **D3** — The three lifecycle guards and their transition tables move with them
  (§2.3).
- **D4** — `User` does **not** move (§2.2).
- **D5** — `workspace_api.domain.models` and `workspace_api.domain.lifecycle`
  become compatibility shims (§2.4), proven by class-identity assertions.
- **D6** — The `SqlLedger(models=...)` seam and the `Ledger` Protocol are **not
  refactored** (§2.5).
- **D7** — Production and test import sites migrate to `operations_domain`
  (§2.6); the shims exist for backward compatibility and for the two documented
  namespace-injection sites, not as the normal import path.

### 2.1 What moves

Twelve types, moved byte-for-byte (same fields, defaults, validators,
docstrings and comments):

| Type | Kind |
|---|---|
| `DataState` | `StrEnum` |
| `RiskClass` | `StrEnum` |
| `ShiftStatus` | `StrEnum` |
| `TaskStatus` | `StrEnum` |
| `CustomerRequestStatus` | `StrEnum` |
| `EvidenceRef` | `BaseModel` |
| `Shift` | `BaseModel` (+ `validate_window`) |
| `Message` | `BaseModel` |
| `OperationalEvent` | `BaseModel` (+ `validate_time`) |
| `Correction` | `BaseModel` |
| `Task` | `BaseModel` |
| `CustomerRequest` | `BaseModel` |

Every one of these is a record the operations ledger persists, a lifecycle enum
that governs those records, or (`EvidenceRef`, `Correction`) part of the CVF
evidence/correction vocabulary shared by every vertical. All twelve are domain
language, none is transport or application wiring.

### 2.2 `User` stays — a reasoned exception, not an oversight

`User` is defined alongside the operational models today, but it is **not** an
operational-domain record:

- It mirrors `database/migrations/003_users.sql`, introduced by **P2-B
  authentication**, not by any operations vertical.
- It is a credential store: `user_id`, `username`, `password_hash`, `role`,
  `is_active`. Its `role` values are constrained by
  `cvf_runtime.identity.KNOWN_ROLES`, i.e. its invariants come from the
  identity/authorization boundary, not the shift-operations domain.
- It is consumed by `workspace_api/auth/router.py` and
  `scripts/seed_dev_users.py`. No governed operations vertical references it.
- Its final home is genuinely undecided: **lane 2** (`known-principals.yaml` ↔
  authenticated users, High Finding #4) is the tranche that will reconcile the
  two independent principal registries. Moving `User` now would pre-empt that
  tranche's design with a mechanical relocation, and would require editing
  `workspace_api/auth/**`, which is out of bounds here.

**Decision: `User` remains defined in
`apps/workspace-api/src/workspace_api/domain/models.py`.** That module is
therefore a shim *plus* the canonical home of exactly one class, and its
docstring must say so in those words. `User` is explicitly named as a
non-goal-for-relocation and handed to lane 2.

An alternative — relocate `User` to `workspace_api/auth/models.py` — is
rejected in §3/A3.

### 2.3 Lifecycle functions move with the package

`assert_transition`, `assert_task_transition` and
`assert_customer_request_transition` are pure functions over `DataState`,
`TaskStatus` and `CustomerRequestStatus` — three enums that are moving. They
hold no application state, touch no ledger, and import nothing else.

Leaving them behind would force `operations_domain` consumers to import back
into `workspace_api` to obtain the invariants of `operations_domain`'s own
enums — reintroducing the exact inverted dependency this tranche removes, and
creating a genuine import cycle risk the moment any package below
`workspace-api` needs a transition check. They move **in this tranche**, not a
later one. The transition tables are copied verbatim, including the comment
explaining why `WAITING` cannot skip to `CLOSED`.

### 2.4 Compatibility shim: yes, and it must prove class identity

`workspace_api.domain.models` and `workspace_api.domain.lifecycle` are retained
as re-export shims:

```python
from operations_domain.models import (  # noqa: F401
    Correction, CustomerRequest, CustomerRequestStatus, DataState,
    EvidenceRef, Message, OperationalEvent, RiskClass, Shift, ShiftStatus,
    Task, TaskStatus,
)
```

Because a Python `from X import Y` binds the *same object*, not a copy, this is
class **identity**, not class equivalence:
`workspace_api.domain.models.Shift is operations_domain.models.Shift` is `True`
by construction. The SPEC turns that into an executed assertion for every
exported name (AC-04), so a future agent that "helpfully" re-declares a class in
the shim fails a test instead of silently creating two `Shift` types that fail
each other's `isinstance` checks.

Three reasons the shim is kept rather than deleting the module outright:

1. **Rollback surface.** With the shim in place, reverting the BUILD commit is
   the entire rollback; no consumer signature ever changed.
2. **It makes the identity requirement testable.** A deleted module cannot be
   asserted against. The shim converts "we did not duplicate the classes" from
   a claim into a check.
3. **It absorbs the `User` and `models=`-namespace cases** (§2.2, §2.5) without
   inventing a new seam.

The shim is **not** a licence to keep importing from it: §2.6 migrates every
call site, and AC-05 fails the build if production code imports a *moved* model
from `workspace_api.domain.*`.

### 2.5 The `SqlLedger(models=...)` seam is deliberately NOT refactored

It is tempting to now delete the injection and have `operations_ledger` import
`operations_domain` directly, as the `Ledger` Protocol docstring anticipates.
**Rejected for this tranche.**

- `_rows.py` needs `models.User` (`build_user`). If the injected namespace
  became `operations_domain.models`, `add_user`/`get_user_by_username` would
  break at runtime — and **no current test constructs a `SqlLedger` and calls
  `add_user`**. Verified two ways: the only `add_user` caller under `tests/` is
  `tests/cvf/test_auth_login.py`, which uses `InMemoryLedger`; and none of the
  14 test-side `SqlLedger(...)` calls belongs to that module. The failure would
  therefore land in production, not CI — exactly the class of silent gap this
  project's review history penalizes.
- Changing the Protocol from structural/loose typing to concrete imports is a
  separate design decision with its own blast radius across both backends.
- The BOUNDARY for this tranche forbids touching this seam without need.

**Therefore: `packages/operations-ledger/src/**` has a zero-line diff in this
tranche** (AC-10, enforced by `git diff --stat`). Every existing
`SqlLedger(..., models=domain_models)` call site keeps passing the
`workspace_api.domain.models` namespace, which after the change re-exports the
eleven persisted types *and* still defines `User` — so the namespace contract
`_rows.py` and `sql_ledger.py` depend on is bit-for-bit satisfied.

Tightening the Protocol to import `operations_domain` directly is recorded as
**follow-up work for a later tranche**, unblocked but not authorized by this
one.

### 2.6 Migration of 43 import statements across 30 files

Mechanical, one-for-one substitution of the module path only — no symbol
renames, no import reordering beyond what the substitution forces. The 30 files
carrying those 43 statements decompose as:

| Site class | Files | New import source |
|---|---|---|
| Routers (`api/*/router.py`) | 6 | `operations_domain.models` |
| Services (`application/*.py`) | 5 | `operations_domain.models` / `.lifecycle` |
| `infrastructure/repository.py` | 1 | 7 types from `operations_domain.models`; `User` from `workspace_api.domain.models` (documented exception E2) |
| `infrastructure/ledger_factory.py` | 1 | unchanged — keeps injecting the shim namespace (§2.5, exception E1) |
| `scripts/seed_dev_users.py` | 1 | `sys.path` entry added; keeps importing `User` from the application package |
| In-app test (`workspace_api/tests/test_lifecycle.py`) | 1 | `operations_domain.lifecycle` / `.models` |
| Tests under `tests/` | 15 | `operations_domain.*`; the 8 `SqlLedger`-constructing modules additionally keep their shim-namespace import (§2.5) |
| **Total (the 43/30 figures)** | **30** | |

Two further files are edit sites but carry **no** `workspace_api.domain`
statement, so they are outside the 43/30 count while still inside the
WORK_ORDER allowlist:

- `apps/.../domain/models.py` and `apps/.../domain/lifecycle.py` — the shims
  themselves (`lifecycle.py`'s `from .models import ...` is the relative import
  noted in §1.2.1);
- `pyproject.toml`, `scripts/apply_migrations.py` and
  `scripts/run_identity_live_governance_evidence.py` — path registries only
  (`pythonpath` / `sys.path` bootstrap), no domain import today or after.

### 2.7 No circular dependency

Resulting direction, strictly one-way:

```
operations_domain      →  (stdlib, pydantic)          only
operations_ledger      →  (sqlalchemy)                unchanged, still no domain import
cvf_runtime            →  (yaml)                      unchanged
workspace_api          →  operations_domain, operations_ledger, cvf_runtime
```

`operations_domain` is a **sink**: nothing it imports can import it back.

AC-01/AC-15 prove this with a **repository-scoped** isolation subprocess, not a
wholesale `sys.path` wipe. The subprocess keeps the standard library and the
installed site-packages — `pydantic` is a legitimate dependency of this
package, and an emptied path would fail the import for a reason unrelated to
the boundary — adds `packages/operations-domain/src`, and removes every other
repository source root (`apps/workspace-api/src`,
`packages/operations-ledger/src`, `packages/cvf-runtime/src`, the repository
root itself), running from a temporary working directory outside the
repository. It then asserts that `pydantic` still imports (proving the
environment was not over-stripped) and that `workspace_api`,
`operations_ledger` and `cvf_runtime` are both absent from `sys.modules` **and
not importable at all** — absence alone would only show they had not been
imported yet. Exact construction: SPEC §4.3.

## 3. Alternatives considered

### A1 — Move the models and delete `workspace_api/domain/` entirely (rejected)

Cleanest end state, and it would make AC-05 trivially true. **Rejected** because
it forces `User` to relocate in the same stroke (§2.2 explains why that belongs
to lane 2), removes the object that makes the identity assertion executable
(§2.4), and turns rollback from "revert one commit" into "restore a deleted
module and re-point 43 imports". The shim costs ~20 lines and buys a provable
invariant.

### A2 — Re-export by re-declaring (`class Shift(operations_domain.models.Shift): pass`) (rejected)

This is the failure mode the tranche exists to prevent. It produces **two**
`Shift` classes: `isinstance(op_domain_shift, workspace_api_shift)` is `False`,
`SqlLedger` rows built through one namespace fail validation against the other,
and Pydantic schema output diverges. Explicitly forbidden; AC-03/AC-04 are
written to catch it.

### A3 — Relocate `User` to `workspace_api/auth/models.py` in this tranche (rejected)

Arguably its correct long-term home. **Rejected** because it requires editing
`workspace_api/auth/**`, which the tranche BOUNDARY prohibits; it pre-empts
lane 2's design of the users ↔ `known-principals.yaml` reconciliation; and it
would change what the `models=` namespace exposes, dragging the ledger seam
(§2.5) into scope. Recorded as an open question owned by lane 2.

### A4 — Also make `operations_ledger` import `operations_domain` directly (rejected)

See §2.5. It breaks `build_user` in an untested path and expands an R2 tranche
into a persistence-layer refactor. Deferred, not forgotten.

### A5 — Split the move across several tranches (models first, lifecycle later) (rejected)

Would leave `operations_domain.DataState` with its transition table stranded in
`workspace_api`, i.e. a half-inverted dependency that is worse than either end
state, and would require two migrations of the same call sites.

### A6 — Do nothing; mark P1-B as satisfied by the existing README stubs (rejected)

`packages/operations-domain/` has zero Python files. Claiming the module is
anything but `stub` without source truth is precisely the over-claim pattern
`EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md` and P-FIX-6 documented.

## 4. Consequences

### 4.1 Accepted

- **A new top-level importable package** appears on the test/script path.
  `pyproject.toml`'s `pythonpath` and three scripts' `sys.path` bootstraps must
  each gain one entry; missing any one of them is an import error at
  collection time, i.e. loud, not silent.
- **`packages/operations-domain/` gains `src/` beside its 11 existing
  README-only blueprint directories.** Enumerated in full, so the count is
  checkable rather than asserted: `approvals/`, `audit/`, `corrections/`,
  `customers/`, `events/`, `handovers/`, `incidents/`, `messages/`,
  `reports/`, `shifts/`, `tasks/`. Those directories are **not** deleted,
  reorganized, or populated by this tranche.
- **Module status moves `stub` → `partial`, never `enforced`.** `partial` is
  correct per the registry legend ("some runtime code exists but the intended
  capability/chain is incomplete"): incidents, handovers, reports and approvals
  still have no models at all. This edit happens only at REVIEW/FREEZE, only
  from observed source truth (AC-14).
- **`workspace_api.domain.models` becomes a two-purpose module** (shim +
  canonical `User`). This is unusual and must be documented in the module
  docstring, or a future reader will "clean it up" and delete `User`.
- **Metrics churn.** `MODULE_REGISTRY.json` LOC/file counts shift for both
  `operations-domain` and `workspace-api`; `MODULE_CATALOG.md` must be
  regenerated with `scripts/generate_catalog.py --write`, never hand-edited.

### 4.2 Pre-existing defects observed and deliberately NOT fixed here

- `infrastructure/docker/Dockerfile.api` copies only
  `apps/workspace-api/src` and sets `PYTHONPATH=/app/src`. It already omits
  `packages/cvf-runtime/src` and `packages/operations-ledger/src`, so that
  image cannot import the ledger or the CVF runtime **today, before this
  tranche**. P1-B does not worsen it and does not fix it. Recorded here so it
  is not later mistaken for P1-B regression, and not silently repaired inside
  an R2 boundary-refactor changed set.

### 4.3 Explicitly not claimed

This tranche does **not**:

- change any API contract, request/response schema, or OpenAPI output;
- change any database schema or migration;
- change lifecycle semantics or any enum value;
- change CVF gate behaviour or make any control newly load-bearing;
- touch authentication, approval, or `known-principals.yaml` — High Finding #4
  remains **OPEN**;
- implement incidents, handovers, or any frontend work;
- constitute live governance evidence of AI/agent behaviour. No AI-governance
  claim is asserted, so `AGENTS.md`'s Mandatory Governance Proof is not
  triggered and **no provider call is required or permitted**;
- advance the Phase 1 exit gate. **PostgreSQL live round-trip remains
  unverified** and stays a pre-ship gate; ticking P1-B `[x]` does not close
  Phase 1;
- alter the `P2B-AUTHENTICATION-REPAIR` or `CVF-CORE-PIN-2026-07-23`
  dispositions.

### 4.4 Rollback

- The BUILD lands as one commit (**C3**) touching only source/test/config
  paths. Reverting that single commit restores the pre-BUILD behaviour exactly,
  because no consumer-visible signature changed (§2.4 reason 1).
- **The reference point is `C3_PARENT`, not `ed3d944`.** `C3_PARENT` is the
  commit `HEAD` points at immediately before C3 is created — in the planned
  sequence that is **C2**. C1 (authorization artifacts) and C2 (pre-BUILD
  continuity) are legitimate history and **must survive** a C3 rollback;
  requiring the whole repository to match `ed3d944` after a revert would
  wrongly demand their destruction. The correct assertion is scoped: after the
  revert, C3's source/test/config paths match `C3_PARENT`.
- **Rollback and its rehearsal never mutate the primary workspace.** They run
  in a temporary `git worktree` (or a temporary clone) outside the project
  worktree, which is then removed. No branch is created, switched, or deleted
  in the primary workspace; no `checkout`/`reset` is run there. Mechanics are
  specified in WORK_ORDER §12 and SPEC AC-18.
- No schema, migration, or data is touched, so rollback needs no data step.
- Continuity/catalog/roadmap edits land in separate commits and revert
  independently.
- The suite is the rollback oracle: back to the **221 passed** baseline.

## 5. Compliance notes

- **Phase discipline** — fresh control chain from INTAKE. This ADR, the SPEC and
  the WORK_ORDER are authored and reviewed as authorization artifacts and
  committed **before** any BUILD action.
- **Role separation** — R2 requires REVIEWER independent from
  IMPLEMENTATION_WORKER. The authoring context holds ORCHESTRATOR, SPEC_AUTHOR
  and WORK_ORDER_AUTHOR only; REVIEWER and COMMIT_STEWARD are held by an
  independent context.
- **Provider neutrality** — roles are named by responsibility throughout.
- **Secrets** — no provider call, no API key read, written, printed or logged.
- **History** — `cd36b27` and every other commit remain untouched: no amend,
  squash, rebase, or force-push.
