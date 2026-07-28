# WORK ORDER — P2-C Operations Console Read Slice

- Work order id: `WO-P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Control-chain phase: `WORK_ORDER`
- Roadmap target: P2-C, first read-only operations-console slice
- Risk: **R2**
- Status: **APPROVED — C3a ONLY; C3b remains gated**
- Design:
  `docs/decisions/ADR_2026-07-28_P2C_OPERATIONS_CONSOLE_READ_SLICE.md`
- Specification:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC.md`
- Authorization review:
  `docs/decisions/P2C_OPERATIONS_CONSOLE_READ_SLICE_AUTHORIZATION_REVIEW.md`

## 1. Objective and claim boundary

Build the smallest authenticated, read-only operations-console slice described
by the ADR and SPEC. The tranche is split into two independently reviewed
BUILD checkpoints:

1. **C3a** — authenticated read API/query/contract plus PostgreSQL and real
   provider governance evidence;
2. **C3b** — React console, deterministic frontend toolchain and CI, beginning
   only after C3a independently passes review and is committed/pushed.

The accepted governance claim is narrow: a verified JWT for a known role is
required before the admitted internal read and before the one evidence-only
provider call. The production read endpoints do not call an AI provider.

## 2. Roles and authority

| Role | Holder | Authority |
|---|---|---|
| ORCHESTRATOR / WORK_ORDER_AUTHOR | Codex | Route and bound the tranche |
| REVIEWER / COMMIT_STEWARD | Codex | Independently review Claude's BUILD; own all stage/commit/push actions |
| IMPLEMENTATION_WORKER | Claude | C3a only after the pre-BUILD gate; no self-approval or Git write |
| REPAIR_WORKER | Claude | Only against exact reviewer findings and named paths |
| SESSION_SYNC_STEWARD / CLOSER | Codex | Continuity and final disposition |

The user's standing instruction assigns Claude implementation and Codex
independent review. Codex's approval of this Work Order does not waive
independent BUILD review. Claude must stop at the named checkpoint and must
not stage, commit or push.

## 3. C3a changed-set ceiling — 23 paths

This is a ceiling, not a checklist. Touching fewer paths is allowed when every
requirement still passes. Touching any unlisted path is stop condition S1.

### 3.1 Runtime/query/API — 5

```text
packages/operations-ledger/src/operations_ledger/ledger.py
packages/operations-ledger/src/operations_ledger/sql_ledger.py
apps/workspace-api/src/workspace_api/infrastructure/repository.py
apps/workspace-api/src/workspace_api/api/events/router.py
apps/workspace-api/src/workspace_api/api/shifts/router.py
```

Permitted behavior:

- add `list_events_for_shift` to the Ledger protocol and both backends;
- expose deterministic `GET /events?shift_id=...`;
- expose `GET /shifts/{shift_id}/open-work` by reusing
  `Ledger.open_work_snapshot`;
- require the existing verified-JWT dependency on `GET /shifts`,
  the new open-work route and the events read route;
- enforce the SPEC's exact ordering, response shapes and 500-record refusal.

No mutation route or authentication implementation may change. In particular,
the parked unauthenticated `POST /shifts` finding is not part of C3a.

### 3.2 Contract/documentation/catalog — 7

```text
packages/workspace-contracts/open-work/open-work.schema.json
packages/workspace-contracts/README.md
apps/workspace-api/README.md
docs/cvf/CVF_CONTROL_MAPPING.md
docs/catalog/MODULE_REGISTRY.json
docs/catalog/MODULE_CATALOG.md
docs/decisions/P2C_READ_API_BUILD_EVIDENCE_RECEIPT.md
```

The catalog Markdown is generator output only. The build receipt must state
the exact commit baseline, path count, commands, results, live-call count,
cleanup result and unresolved findings. It cannot declare its own approval.

### 3.3 Automated tests — 8

```text
tests/cvf/test_ledger_protocol.py
tests/contract/test_contract_files.py
tests/integration/test_p2c_read_ledger_parity.py
tests/integration/test_p2c_read_api.py
tests/integration/test_sql_ledger_postgres_live.py
tests/integration/test_postgres_live_runner.py
tests/unit/test_p2c_read_openapi_contract.py
tests/integration/test_p2c_read_live_evidence_runner.py
```

New tests must prove both InMemory and SQL behavior where the SPEC requires
parity. Existing unrelated assertions may not be removed, weakened or
relabelled. PostgreSQL tests must use PostgreSQL 16, not SQLite emulation.

### 3.4 Live runners and receipt — 3

```text
scripts/run_postgres_live_roundtrip.py
scripts/run_p2c_read_live_governance_evidence.py
docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md
```

The provider runner must:

- mint and submit a real project JWT through the HTTP dependency path;
- prove rejected missing/invalid JWT reads cause zero provider calls;
- prove one admitted JWT read before exactly one real provider call;
- generate a sanitized tracked receipt with top-level
  `Overall outcome: PASS`, `FAIL` or `BLOCKED`;
- never print, persist or inspect the secret value.

The PostgreSQL runner must always remove its disposable container and volume,
including on failure. It must not reuse or alter a user database.

## 4. C3b changed-set ceiling — 28 paths, not yet authorized to edit

C3b becomes eligible only after §8 G7. Until then every path in this section
is prohibited.

### 4.1 Toolchain/CI/docs — 9

```text
package.json
pnpm-lock.yaml
apps/workspace-web/package.json
apps/workspace-web/tsconfig.json
apps/workspace-web/vitest.config.ts
infrastructure/docker/Dockerfile.web
.github/workflows/ci.yml
apps/workspace-web/README.md
docs/architecture/FRONTEND_BACKEND_BOUNDARY.md
```

Pin Node `22.14.0` and pnpm `9.15.0`; commit the root lockfile; use frozen
installs in CI and Docker. The Docker build image must be the verified exact
tag `node:22.14.0-alpine3.21`, not a floating major tag.

### 4.2 Console implementation — 15

```text
apps/workspace-web/src/app/App.tsx
apps/workspace-web/src/app/styles.css
apps/workspace-web/src/app/OperationsConsole.tsx
apps/workspace-web/src/services/api.ts
apps/workspace-web/src/types/operations.ts
apps/workspace-web/src/components/AsyncState.tsx
apps/workspace-web/src/features/authentication/session.ts
apps/workspace-web/src/features/authentication/LoginView.tsx
apps/workspace-web/src/features/shift-selection/ShiftSelector.tsx
apps/workspace-web/src/features/shift-timeline/ShiftTimeline.tsx
apps/workspace-web/src/features/open-work/OpenWorkPanel.tsx
apps/workspace-web/src/features/incident-room/IncidentSummary.tsx
apps/workspace-web/src/features/shift-handover/HandoverSummary.tsx
apps/workspace-web/src/tests/setup.ts
apps/workspace-web/src/tests/App.test.tsx
```

The UI is read-only. It may render login/logout, shift selection, timeline,
open tasks/customer requests, incidents and handovers. It must not expose
mutation controls, activate offline replay, add realtime transport, or add
AI/RAG/memory/reporting/forecasting behavior. Auth data is tab-scoped
`sessionStorage` only; `localStorage` is prohibited for tokens.

### 4.3 API test/catalog/receipt — 4

```text
apps/workspace-web/src/tests/api.test.ts
docs/catalog/MODULE_REGISTRY.json
docs/catalog/MODULE_CATALOG.md
docs/decisions/P2C_WEB_BUILD_EVIDENCE_RECEIPT.md
```

## 5. Global prohibited scope

```text
.cvf/**
../.Controlled-Vibe-Framework-CVF/**
apps/workspace-api/src/workspace_api/auth/**
apps/workspace-api/src/workspace_api/dependencies.py
apps/workspace-api/src/workspace_api/config.py
apps/workspace-api/src/workspace_api/application/**
apps/workspace-api/src/workspace_api/api/tasks/**
apps/workspace-api/src/workspace_api/api/customer_requests/**
apps/workspace-api/src/workspace_api/api/incidents/**
apps/workspace-api/src/workspace_api/api/handovers/**
apps/workspace-web/src/offline/queue.ts
database/**
docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md
docs/implementation/EXECUTION_ROADMAP.md
IMPLEMENTATION_STATUS.json
SESSION/**
CVF_SESSION/**
```

The Work Order/ADR/SPEC/authorization review are immutable during BUILD.
Secrets, provider responses containing sensitive content, host databases and
out-of-repository durable artifacts are prohibited.

## 6. Split-file and implementation guards

- Python production/test/script files: at most 300 lines.
- TypeScript/TSX/JavaScript files: at most 200 lines.
- Markdown/JSON/schema files remain within repository hard limits.
- A file may not evade a guard through minification, generated one-line
  content, compressed formatting or suppressed discovery.
- If an authorized file would exceed its limit, stop and request an exact-path
  amendment; do not append a debt-baseline or exception entry.
- Shared parsing/fetch/render responsibilities must remain separated along the
  path list above; no monolithic `App.tsx`, API module or test file.

`python scripts/check_file_size.py` and repository validation are mandatory
guards, not advisory reviewer memory.

## 7. C3a evidence matrix

| Requirement | Mandatory evidence |
|---|---|
| Ledger/API/ordering/ceiling | focused new tests plus `test_ledger_protocol.py` |
| Exact contract/OpenAPI | contract and P2-C OpenAPI tests |
| Backend parity | InMemory + SQLite SQL parity tests |
| Real database | PostgreSQL 16 live round-trip; real enum writes and all P2-C reads |
| JWT admission/refusal | API tests through real token verification |
| Governance claim | real provider runner; refusals 0 calls, admitted path exactly 1 call |
| Regression | `python -m pytest -q`, 0 failures/errors, count not below baseline |
| Repository | validator, catalog check, session check, file-size guard, `git diff --check` |
| Cleanup | zero tranche containers and volumes after live run |
| Boundary | exact changed/untracked/staged inventory and secret scan |

The independent REVIEWER reruns the focused, full, PostgreSQL and real-provider
gates. A worker-authored receipt is evidence input, never review approval.

## 8. Gates and commit plan

### Pre-BUILD

- **G1** — Work Order feasibility review is `REVIEW_PASS`.
- **G2** — Work Order and authorization review are committed/pushed with zero
  BUILD files.
- **G3** — post-push authorization re-review confirms exact content.
- **G4** — continuity records C3a as the sole next move and is committed/pushed
  separately.
- **G5** — immediately before BUILD: `HEAD == origin/main`; nothing staged;
  no tracked change; the only permitted untracked path is the preserved
  assessment with SHA-256
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`.
- **G6** — Docker daemon responds, PostgreSQL and Node tags resolve, repository
  gates pass, and Claude declares `IMPLEMENTATION_WORKER`.

If Docker is unavailable at G6, report `BLOCKED_DOCKER_UNAVAILABLE`; do not
substitute SQLite or claim live coverage.

### C3a review/commit

- Claude stops at `READY_FOR_INDEPENDENT_P2C_READ_API_BUILD_REVIEW`.
- Codex returns `REVIEW_PASS` or exact stable findings.
- Repairs use Claude's `REPAIR_WORKER` role and only reviewer-named paths.
- On pass, Codex stages exactly the reviewed C3a set, commits and pushes C3a.
- **G7** — only after pushed C3a, continuity rehydration and acknowledgment,
  Codex may authorize C3b. This Work Order does not itself authorize Claude
  to begin C3b.

### C3b review/commit

- Claude stops at `READY_FOR_INDEPENDENT_P2C_WEB_BUILD_REVIEW`.
- Codex reruns frozen install, typecheck, unit tests, production build, Docker
  image build, Python regression and repository guards.
- Codex alone commits/pushes a passing C3b.

C4/FREEZE is a separate closer-owned continuity/roadmap commit after both
BUILD checkpoints pass. This Work Order does not authorize a roadmap claim
before that review.

## 9. Stop conditions

- **S1** any path outside the active checkpoint allowlist changes;
- **S2** any mutation behavior, role/permission model, auth issuance or parked
  `POST /shifts` finding changes;
- **S3** any test is skipped, weakened, deleted or replaced with a mock for a
  governance claim;
- **S4** provider call count differs from exactly one admitted call or any
  refusal calls the provider;
- **S5** PostgreSQL is unavailable, emulated, not cleaned up, or exposes a
  production/migration/metadata defect;
- **S6** secret or sensitive provider content appears in logs/receipts;
- **S7** file-size, catalog, session, validation, focused or full-suite gate is
  red;
- **S8** staged/committed/pushed content is created by the worker;
- **S9** C3b begins before G7;
- **S10** requirements require an unlisted file or conflict with ADR/SPEC.

On any stop condition: stop, preserve evidence, name the finding, and attempt
no unauthorized repair.

## 10. Rollback

C3a and C3b are separate additive commits. Roll back by reverting the affected
commit in a clean worktree, rebuilding from the retained frozen lockfile where
applicable, and rerunning the predecessor suite. No database down migration is
claimed because this tranche authorizes no schema migration.

