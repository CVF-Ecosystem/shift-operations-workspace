# SPEC — P1-B Operations-Domain Extraction

- Spec id: `SPEC-P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase at authoring time: `SPEC`
- Risk: **R2**
- Status: **PROPOSED** — not approved, not built
- Design: `docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md`
- Work order: `docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER.md`
- Baseline commit: `ed3d94431dc55530bb7328514646adff36cff47b`

## 1. Purpose and claim boundary

This SPEC converts ADR §2 into testable requirements. It specifies a **pure
structural refactor**: the canonical definition of the operational domain
vocabulary moves from the application package into a real
`operations-domain` package, with **zero observable behaviour change**.

**This SPEC does not authorize, and its acceptance does not evidence:**

- any API contract, response schema or OpenAPI change;
- any database schema or migration change;
- any lifecycle-semantics or enum-value change;
- any CVF gate behaviour change, or any control becoming newly load-bearing;
- any change to authentication, approval, or `known-principals.yaml`
  (High Finding #4 stays **OPEN**);
- incidents, handovers, or frontend work;
- closure of the Phase 1 exit gate, or PostgreSQL live verification;
- any AI/agent-governance claim. No provider call is required or permitted
  (§8).

## 2. Terminology

| Term | Meaning in this SPEC |
|---|---|
| **Moved type** | One of the twelve types in §3.1. |
| **Moved function** | One of the three lifecycle guards in §3.2. |
| **Canonical definition** | The single `class`/`def` statement that creates the object at runtime. |
| **Shim** | `workspace_api.domain.models` / `workspace_api.domain.lifecycle` after the change: re-export only, no new class for any moved type. |
| **Production code** | Any `.py` under `apps/**`, `packages/**`, `scripts/**`. Excludes `tests/**` and `apps/workspace-api/src/workspace_api/tests/**`. |
| **Baseline** | The repository at `ed3d944`: `221 passed`, doctor `24/24`. |

## 3. Functional requirements

### R1 — The `operations_domain` package exists and is self-contained

**R1.1** A package exists at
`packages/operations-domain/src/operations_domain/` containing `__init__.py`,
`models.py`, `lifecycle.py`.

**R1.2** `operations_domain` imports **only** the standard library and
`pydantic`. It must not import `workspace_api`, `operations_ledger`,
`cvf_runtime`, `fastapi`, or `sqlalchemy` — at module level or lazily.

**R1.3** `packages/operations-domain/src` is registered in
`pyproject.toml`'s `[tool.pytest.ini_options] pythonpath`, and in the
`sys.path` bootstrap of every script that imports the domain transitively
(`scripts/seed_dev_users.py`, `scripts/apply_migrations.py`,
`scripts/run_identity_live_governance_evidence.py`).

**R1.4** `packages/operations-domain/README.md` is updated to describe the real
package. The **eleven** existing README-only blueprint subdirectories
(`approvals/`, `audit/`, `corrections/`, `customers/`, `events/`,
`handovers/`, `incidents/`, `messages/`, `reports/`, `shifts/`, `tasks/` —
count reproducible via
`find packages/operations-domain -mindepth 1 -maxdepth 1 -type d`) are **not**
deleted, moved, renamed, or populated.

### R2 — Exactly one canonical definition per moved type

**R2.1** The following twelve types have their canonical definition in
`operations_domain.models`, moved verbatim — identical field names, order,
types, defaults, `default_factory` callables, validators, docstrings and
inline comments:

`DataState`, `RiskClass`, `ShiftStatus`, `TaskStatus`,
`CustomerRequestStatus`, `EvidenceRef`, `Shift`, `Message`,
`OperationalEvent`, `Correction`, `Task`, `CustomerRequest`.

**R2.2** For each moved type `T`: `T.__module__ == "operations_domain.models"`.

**R2.3** No other module in the repository contains a `class` statement for any
moved type name. Subclassing a moved type to "re-export" it is forbidden.

### R3 — Lifecycle guards move with the package

**R3.1** `assert_transition`, `assert_task_transition` and
`assert_customer_request_transition` have their canonical definition in
`operations_domain.lifecycle`, with `__module__ ==
"operations_domain.lifecycle"`.

**R3.2** The three transition tables (`_ALLOWED`, `_ALLOWED_TASK`,
`_ALLOWED_CUSTOMER_REQUEST`) are moved verbatim, including the explanatory
comment on why `WAITING` may not transition directly to `CLOSED`.

**R3.3** Raised exception type and message format are unchanged
(`ValueError`, `f"Invalid data-state transition: {current} -> {target}"` and
the task / customer-request equivalents).

### R4 — Compatibility shim with proven class identity

**R4.1** `workspace_api.domain.models` re-exports all twelve moved types.
`workspace_api.domain.lifecycle` re-exports all three moved functions.

**R4.2** Object identity (`is`, never `==`) holds **within each module pair**:

- for each of the twelve moved types `N`:
  `getattr(workspace_api.domain.models, N) is getattr(operations_domain.models, N)`;
- for each of the three moved functions `N`:
  `getattr(workspace_api.domain.lifecycle, N) is getattr(operations_domain.lifecycle, N)`.

The lifecycle guards are **not** re-exported from `operations_domain.models`,
so asserting them against that module does not satisfy R4.2. See §4.1.

**R4.3** Neither shim module declares a `class` or `def` for any moved name.

**R4.4** `User` is **not** moved. Its canonical definition stays in
`workspace_api.domain.models` with `User.__module__ ==
"workspace_api.domain.models"`. The module docstring must state both roles of
the module (compatibility shim + canonical home of `User`) and name lane 2
(`known-principals.yaml` ↔ users reconciliation) as the owner of `User`'s
eventual relocation.

### R5 — Production code stops sourcing moved types from the application package

**R5.1** No production module imports a **moved type or moved function** from
`workspace_api.domain.models` or `workspace_api.domain.lifecycle`.

**R5.2** Exactly two documented exceptions exist, and no others:

| Exception | File | Why |
|---|---|---|
| E1 — namespace injection | `apps/.../infrastructure/ledger_factory.py` | Passes the shim module as `SqlLedger(models=...)`; the injected namespace must still expose `User` for `_rows.build_user` (ADR §2.5). It imports the **module**, not a moved type. |
| E2 — `User` import | `apps/.../infrastructure/repository.py`, `scripts/seed_dev_users.py` | `User` did not move (R4.4). |

**R5.3** The shim modules themselves are exempt (they exist to re-export).

**R5.4** Test modules migrate to `operations_domain` too, except the
shim-identity test, which imports both namespaces by design.

### R6 — The ledger seam is untouched

**R6.1** `packages/operations-ledger/src/**` has a **zero-line diff** in the
BUILD commit.

**R6.2** `SqlLedger.__init__(self, database_url, models, engine=None)` is
unchanged, and every existing `SqlLedger(...)` construction site keeps passing
a namespace that exposes `Shift`, `ShiftStatus`, `OperationalEvent`, `Task`,
`CustomerRequest`, `User`, `EvidenceRef`, `Correction`.

**R6.3** The `Ledger` Protocol in `operations_ledger/ledger.py` is unchanged.

### R7 — No circular dependency

**R7.1** `operations_domain` is importable in a fresh interpreter that retains
the Python standard library and the installed site-packages (so `pydantic`
resolves normally) and has `packages/operations-domain/src` on its path, but
from which **every other repository source root has been removed** — in
particular `apps/workspace-api/src`, `packages/operations-ledger/src` and
`packages/cvf-runtime/src`.

The isolation is *repository-scoped*, not a wholesale `sys.path` replacement:
emptying `sys.path` would make `pydantic` — a legitimate third-party
dependency of this package — unimportable, and the resulting failure would
prove nothing about the boundary. Exact construction in §4.3.

**R7.2** After that import, `workspace_api`, `operations_ledger` and
`cvf_runtime` are absent from `sys.modules` **and** are not importable at all
from that interpreter — proving the repository roots are genuinely off the
path, rather than merely unimported so far.

### R8 — Behaviour is unchanged

**R8.1** Pydantic serialization and validation are identical to baseline for
every moved model, using the correct API for each direction:

- Python-object round trip: `model_validate(model_dump())`;
- JSON round trip: `model_validate_json(model_dump_json())`.

`model_validate(<json string>)` is **not** used: it is the wrong entry point
for a JSON payload and would either raise or silently exercise a different
code path. `model_json_schema()` output is compared after canonicalization
(§4.4).

**R8.2** Every enum's member names and values are unchanged, member order
included.

**R8.3** Lifecycle transition tables are unchanged (R3.2) — every allowed
transition still allowed, every forbidden one still forbidden.

**R8.4** The FastAPI application's generated OpenAPI document is unchanged from
the baseline capture, compared as canonical bytes (§4.4).

**R8.5** HTTP request/response behaviour for all governed endpoints is
unchanged: status codes, bodies, and error shapes.

## 4. Acceptance criteria

Every AC is a command or an executed test. "Inspected and looks right" is not
acceptance. Golden captures required by AC-06/AC-09 are produced from
`ed3d944` **before** any source edit.

| AC | Requirement | Verification |
|---|---|---|
| **AC-01** | `operations_domain` imports independently of `workspace_api` | Subprocess with stdlib + site-packages retained, `packages/operations-domain/src` added, and every other repository source root removed (§4.3). R1.2, R7 |
| **AC-02** | No reverse import, statically | Source scan of `packages/operations-domain/src/**`: no `workspace_api`, `operations_ledger`, `cvf_runtime`, `fastapi`, `sqlalchemy` token in any `import`/`from` statement. R1.2 |
| **AC-03** | Exactly one canonical class definition per moved type | AST scan over `apps/**`, `packages/**`, `scripts/**`: for each of the twelve names, exactly one `ClassDef`, located in `operations_domain/models.py`; plus `T.__module__` assertion per type. Same for the three `FunctionDef` guards. R2.2, R2.3, R3.1 |
| **AC-04** | Shim proves object identity, **per module pair** | Two parametrized assertions, not one (§4.1). R4.2 |
| **AC-05** | Production code no longer owns/imports moved models from the application package | AST scan of production code: no `ImportFrom` whose module is `workspace_api.domain.models` / `.lifecycle` names a moved symbol. The **only** permitted matches are E1 (module-object import in `ledger_factory.py`) and E2 (`User` in `repository.py`, `seed_dev_users.py`), asserted by exact file path — a third match fails. R5 |
| **AC-06** | Pydantic serialization/deserialization unchanged | Per-direction round trips with the correct API, and canonical-byte schema comparison against a golden capture from `ed3d944`. Full definition in §4.4. R8.1 |
| **AC-07** | Enum values unchanged | `[(m.name, m.value) for m in E]` equals the baseline list, in order, for all five enums. R8.2 |
| **AC-08** | Lifecycle transitions unchanged | Full matrix: every (current, target) pair over each enum asserted allowed/denied against the baseline table; denial raises `ValueError` with the baseline message. R8.3 |
| **AC-09** | API request/response behaviour unchanged | `app.openapi()` equal to the baseline capture **as canonical bytes** (§4.4); existing HTTP-level tests pass **unmodified in assertions** (import lines may change). R8.4, R8.5 |
| **AC-10** | Ledger seam untouched | `git diff --stat <base>..HEAD -- packages/operations-ledger/` is empty; `Ledger` Protocol and `SqlLedger.__init__` signature asserted unchanged. R6 |
| **AC-11** | Ledger + governance regressions still pass | `python -m pytest -q tests/integration tests/cvf` — SQLite round-trip, schema parity (incl. users), freeze invariant, atomic mutation+audit, evidence persistence, shift-close governance, customer-request vertical, auth tokens/login: **all pass**. |
| **AC-12** | Full-suite baseline not reduced | `python -m pytest -q` reports **≥ 221 passed**, 0 failed, 0 errors. A lower count fails even if nothing "fails" — it means tests were lost. |
| **AC-13** | Repository validators pass | `python scripts/testing/validate_repository.py`, `python scripts/generate_catalog.py --check`, `python scripts/check_session_state.py`, `python scripts/check_file_size.py` — all PASS. |
| **AC-14** | Catalog status change is evidence-led | `operations-domain` moves `stub` → **`partial`** only if `packages/operations-domain/src/**` contains non-empty Python source with `metrics.loc > 0` after `generate_catalog.py --write`. It must **not** become `enforced`: incidents/handovers/reports/approvals still have no models. Registry edited by hand only in the `modules` block; `metrics` regenerated, never hand-edited. |
| **AC-15** | No circular dependency | AC-01's isolated subprocess (§4.3), including its negative import checks, plus a repo-wide check that no module under `packages/**` imports `workspace_api`. R7 |
| **AC-16** | PostgreSQL remains an open limitation | No artifact produced by this tranche asserts a PostgreSQL live round-trip, a Phase 1 exit-gate pass, or removes the pre-ship-gate wording from `IMPLEMENTATION_STATUS.json` / `ACTIVE_SESSION_STATE.json`. Verified by reviewer text check. |
| **AC-17** | No provider call, no secret | No network call to any provider; no read/write/print/log of any API key or `.env` secret. `git diff` contains no credential. Verified by reviewer inspection of the changed set. |
| **AC-18** | Rollback works, rehearsed off the primary workspace | Procedure and assertions in §4.2. |

### 4.1 AC-04 in full — identity is asserted per module pair

The shim is **two** modules re-exporting from **two** source modules. A single
blanket assertion against `operations_domain.models` would be wrong for the
lifecycle functions, which do not live there. AC-04 is therefore two
parametrized checks:

**AC-04a — models.** For each of the twelve moved types
(`DataState`, `RiskClass`, `ShiftStatus`, `TaskStatus`,
`CustomerRequestStatus`, `EvidenceRef`, `Shift`, `Message`,
`OperationalEvent`, `Correction`, `Task`, `CustomerRequest`):

```
getattr(workspace_api.domain.models, N) is getattr(operations_domain.models, N)
```

Explicitly includes
`workspace_api.domain.models.Shift is operations_domain.models.Shift`.

**AC-04b — lifecycle.** For each of the three moved functions
(`assert_transition`, `assert_task_transition`,
`assert_customer_request_transition`):

```
getattr(workspace_api.domain.lifecycle, N) is getattr(operations_domain.lifecycle, N)
```

Cross-module assertions are failures, not shortcuts: asserting a lifecycle
function against `operations_domain.models`, or a model against
`operations_domain.lifecycle`, does not satisfy AC-04. Identity is `is`, never
`==` and never `__name__` comparison.

Both checks assert the negative too: neither shim module declares a `ClassDef`
or `FunctionDef` for any moved name (R4.3), and
`User.__module__ == "workspace_api.domain.models"` (R4.4).

### 4.2 AC-18 in full — rollback rehearsal

**Constraint: the rehearsal must not mutate the primary workspace.** No branch
is created, switched, or deleted there; no `checkout`, `reset`, or `revert` is
run against the project worktree. The rehearsal runs in a **temporary
`git worktree`** (or a temporary clone) rooted **outside** the project
directory, and is removed afterwards.

Reference point: **`C3_PARENT`** — the commit `HEAD` points at immediately
before the BUILD commit is created (in the planned sequence, C2). It is
recorded by the IMPLEMENTATION_WORKER at that moment and quoted in the
evidence, not reconstructed later.

Procedure:

1. Before creating C3, record `C3_PARENT = git rev-parse HEAD`.
2. After C3 exists, create a temporary worktree at C3, outside the primary
   workspace, in a detached-HEAD state.
3. Inside that temporary worktree only, `git revert --no-edit <C3>`.
4. Assert: `git diff <C3_PARENT> -- <every C3 source/test/config path>` is
   **empty**. The comparison is **scoped to C3's paths**, and the reverted tree
   is compared against `C3_PARENT` — **not** against `ed3d944`, and **not**
   whole-repo.
5. Assert: C1 and C2 are still present and unmodified. A rollback of C3 that
   also erased the authorization artifacts or the continuity acknowledgment
   would be a failure, not a success.
6. Run `python -m pytest -q` in the temporary worktree; it must report exactly
   the **221 passed** baseline.
7. Remove the temporary worktree (`git worktree remove --force <path>` then
   `git worktree prune`), or delete the temporary clone. Confirm
   `git worktree list` shows only the primary worktree and that
   `git status --porcelain` there is unchanged by the rehearsal.

Failure at any step is stop condition S3/S8, not a note.

### 4.3 AC-01 in full — repository-scoped import isolation

**The subprocess must not run with an emptied `sys.path`.** `operations_domain`
legitimately depends on `pydantic`; stripping site-packages would make the
import fail for a reason that has nothing to do with the boundary, turning a
green test into a false negative and a red one into a misleading failure. The
isolation removes **repository source roots**, not the interpreter's own
environment.

Environment for the subprocess:

1. **Keep** the Python standard library and the installed site-packages, so
   `pydantic` imports normally.
2. **Add** `packages/operations-domain/src`.
3. **Remove every other repository source root** — explicitly at least
   `apps/workspace-api/src`, `packages/operations-ledger/src`,
   `packages/cvf-runtime/src`, plus the repository root itself and
   `apps/workspace-worker/src` / `apps/integration-edge/src` if present. Clear
   `PYTHONPATH` rather than inheriting the parent's, and pass `-P` (or
   otherwise ensure the script's own directory is not prepended) so no
   repository directory re-enters the path implicitly.
4. **Run from a temporary working directory outside the repository**, so
   implicit cwd resolution cannot reach repository packages.

Assertions inside the subprocess, after
`import operations_domain.models, operations_domain.lifecycle` succeeds:

- `pydantic` **is** importable — a guard proving the environment was not
  over-stripped, so a pass means "boundary holds", not "nothing could import";
- `workspace_api`, `operations_ledger` and `cvf_runtime` are **absent from
  `sys.modules`**;
- each of those three is **not importable at all** — attempting
  `importlib.import_module(name)` raises `ModuleNotFoundError`. Absence from
  `sys.modules` alone would only show they had not been imported *yet*; the
  negative import proves the repository roots are genuinely off the path;
- for completeness, no entry remaining on `sys.path` resolves to a repository
  source root other than `packages/operations-domain/src`.

The subprocess exits non-zero on any failed assertion, and the parent test
asserts a zero exit status and surfaces the captured output on failure.

### 4.4 AC-06 / AC-09 in full — correct APIs and canonical bytes

**Round trips use the matching API in each direction.** For every moved model,
starting from a golden fixture captured at `ed3d944` with fixed UUIDs and fixed
timestamps (no `uuid4()`/`now()` at assertion time):

| Direction | Assertion |
|---|---|
| Python object | `M.model_validate(inst.model_dump()) == inst` |
| JSON | `M.model_validate_json(inst.model_dump_json()) == inst` |

`model_validate(<json string>)` is **forbidden**: passing a JSON string to the
Python-object validator is the wrong entry point — it does not parse JSON the
way `model_validate_json` does, and using it would either raise or exercise a
path unrelated to what AC-06 claims to verify. A test using it does not satisfy
AC-06 even if it passes.

**"Byte-identical" is defined, not left to `dict` or `str` comparison.** Python
`dict` equality ignores key order and `str(dict)` is not a stable wire format,
so both `model_json_schema()` and `app.openapi()` are canonicalized before
comparison:

```python
def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
```

- **AC-06** compares `canonical(M.model_json_schema())` against the golden
  capture, per moved model.
- **AC-09** compares `canonical(app.openapi())` against the golden capture.

Both golden captures are produced with the **same** `canonical()` function at
`ed3d944`, before any source edit, and stored as fixture files. Comparison is
`bytes == bytes`; a diff is reported by decoding both sides, never by asserting
on a repr.

`model_dump_json()` output is already a string with a deterministic
Pydantic-defined shape and is compared directly, without re-canonicalization —
re-serializing it through `json.dumps` would test `json`'s formatting rather
than Pydantic's.

## 5. Out of scope (rejection required, not silent skipping)

If BUILD finds any of these desirable, it must **stop and report**, not act:

- refactoring `SqlLedger(models=...)` or the `Ledger` Protocol to import
  `operations_domain` directly (ADR §2.5 — later tranche);
- relocating `User` (ADR §2.2/A3 — lane 2);
- deleting, renaming or populating the **eleven** README-only blueprint
  subdirectories of `packages/operations-domain/` (`approvals/`, `audit/`,
  `corrections/`, `customers/`, `events/`, `handovers/`, `incidents/`,
  `messages/`, `reports/`, `shifts/`, `tasks/`);
- fixing `infrastructure/docker/Dockerfile.api`'s pre-existing missing package
  paths (ADR §4.2);
- any edit to `packages/cvf-runtime/**`,
  `packages/cvf-application-profile/**` (including `known-principals.yaml`),
  `workspace_api/auth/**`, `database/**`, `apps/workspace-web/**`, `.cvf/**`;
- opening lanes 2, 3 or 4.

## 6. Test artifacts to be added

New tests live under `tests/unit/` and are additive — no existing test is
deleted or weakened.

1. **`tests/unit/test_operations_domain_boundary.py`** — AC-01, AC-02, AC-03,
   AC-05, AC-15. Repository-scoped subprocess import isolation exactly as
   specified in §4.3 (stdlib + site-packages retained, other repository source
   roots removed, temporary cwd, `pydantic`-importable guard, negative
   `ModuleNotFoundError` checks); plus AST scans, `__module__` assertions, and
   the exact-path allowlist for E1/E2.
2. **`tests/unit/test_operations_domain_shim_identity.py`** — AC-04. **Two
   separate parametrized cases, one per module pair** (§4.1): AC-04a asserts
   `is`-identity for the twelve types between `workspace_api.domain.models` and
   `operations_domain.models`; AC-04b asserts `is`-identity for the three
   lifecycle functions between `workspace_api.domain.lifecycle` and
   `operations_domain.lifecycle`. Also asserts the shims declare no
   `ClassDef`/`FunctionDef` for a moved name, and that
   `User.__module__ == "workspace_api.domain.models"`.
3. **`tests/unit/test_operations_domain_serialization.py`** — AC-06, AC-07,
   AC-08. Per-direction round trips using `model_validate(model_dump())` and
   `model_validate_json(model_dump_json())` (never
   `model_validate(<json string>)`), golden `model_json_schema()` comparison
   through the `canonical()` helper of §4.4, enum member lists, and the full
   transition matrix. The `canonical()` helper is defined once and shared with
   the AC-09 OpenAPI check so both use the identical byte definition.

Modifying an existing test's **assertions** to make it pass is a stop
condition; only import lines may change.

## 7. Evidence required at REVIEW

The IMPLEMENTATION_WORKER must produce, and the independent REVIEWER must
re-run rather than trust:

- `git status --porcelain` and `git diff --stat` for the BUILD commit;
- `git diff --stat -- packages/operations-ledger/` proving empty (AC-10);
- `python -m pytest -q` tail showing `≥ 221 passed` (AC-12);
- targeted run of the three new test files (AC-01…AC-08);
- all four validator outputs (AC-13);
- `git diff --check` clean;
- the recorded `C3_PARENT` hash and the rollback-rehearsal result, including
  the temporary worktree/clone path used and proof it was removed (AC-18,
  §4.2).

Numbers are quoted from the run that produced them. Copying a count from a
prior handoff is the exact spec-drift finding recorded as Medium #7 in
`EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`.

## 8. Live governance evidence — not required, and why

`AGENTS.md`'s Mandatory Governance Proof requires a real provider API call for
any claim asserting **CVF governance behaviour** — risk classification,
approval flow, phase gates, DLP filtering, bypass detection, output validation,
provider routing, audit-trail updates, or CVF controlling AI/agent behaviour.

This tranche asserts **none** of those. It relocates class definitions and
rewrites import statements; its strongest claim is "behaviour is byte-identical
to before". No control changes status, none becomes newly load-bearing, and no
statement is made about AI or agent behaviour.

A provider call is therefore **not required and not permitted** here. Passing
tests and validators prove structural containment and behavioural parity only —
they are **not** governance evidence, and no artifact may present them as such.

## 9. Definition of done

- R1…R8 satisfied; AC-01…AC-18 all pass with recorded output.
- Changed set is within the WORK_ORDER allowlist; no prohibited path touched.
- Independent REVIEWER (not the implementer) confirms every AC by re-running.
- Catalog/roadmap/continuity updates land in their own commits per the
  WORK_ORDER, only at REVIEW/FREEZE, only from observed source truth.
- No claim beyond §1's boundary appears in any artifact.
