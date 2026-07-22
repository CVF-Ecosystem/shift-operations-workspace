# WORK ORDER — P2-B Approver Identity Reconciliation

- Work order id: `WO-P2B-APPROVER-IDENTITY-RECONCILIATION`
- Tranche: `P2B-APPROVER-IDENTITY-RECONCILIATION`
- Control-chain phase at authoring time: `WORK_ORDER`
- Risk: **R2** — REVIEWER independent from IMPLEMENTATION_WORKER
- Status: **DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.**
- Design: `docs/decisions/ADR_2026-07-23_P2B_APPROVER_IDENTITY_RECONCILIATION.md`
- Specification: `docs/specs/P2B_APPROVER_IDENTITY_RECONCILIATION_SPEC.md`
- Baseline: `848aebaf03af4efa16d04d7f0f02b6d9da0e564b` (`HEAD == origin/main`,
  clean, doctor `24/24`, suite `292 passed`)

## 1. Authorized objective

Close High Finding #4 within the SPEC boundary: authenticated, server-derived,
scope-bound approval receipts (R1–R8); a durable creation-intent digest binding
for `task.create` (R9); `users` as the single approver authority;
`known-principals.yaml` retired; a real Alibaba live-evidence run at a pinned
tracked path. Nothing beyond the SPEC. Every ambiguity resolves to **stop and
report**, never **decide and proceed**.

## 2. Roles

| Role | Holder | Notes |
|---|---|---|
| ORCHESTRATOR / SPEC_AUTHOR / WORK_ORDER_AUTHOR | Claude (this context) | Authored the three artifacts; holds no implementation role at this checkpoint. |
| REVIEWER (independent) | Codex | Reviews the artifacts, then reviews BUILD by **re-running** every AC, including the live receipt. |
| COMMIT_STEWARD | Codex | Verifies the changed set and owns every commit/push. |
| IMPLEMENTATION_WORKER | Claude — **only after §7 approval** | States the role transition before the first edit. |
| SESSION_SYNC_STEWARD / CLOSER | assigned at C2 / C4 | Continuity and closure. |

R2 role separation is mandatory: the implementing context must not be the
approving context.

## 3. Changed-set allowlist (ceiling, not a checklist) — C3

The allowlist is a **ceiling**: touching fewer paths is conformant if every
touched path is listed; touching any unlisted path is stop condition **S1**.
Every file below was verified as a real, required edit site by command — see
§3.4 for the exact audit commands a reviewer re-runs. **Total: 39 paths.**

### 3.1 Create (7)

```
database/migrations/004_approval_receipts.sql
apps/workspace-api/src/workspace_api/api/approvals/__init__.py
apps/workspace-api/src/workspace_api/api/approvals/router.py         # POST /approvals only
apps/workspace-api/src/workspace_api/application/approval_service.py # receipt + audited intent + authority resolver + digest logic
scripts/run_approval_governance_evidence.py
tests/cvf/test_approver_identity_reconciliation.py
docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md         # F4: pinned live-evidence receipt path
```

`docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md` is a **narrow,
named exception** to §4's prohibition on `docs/decisions/**` in C3: it is the
only file under that path C3 may create, and it must be produced by
`scripts/run_approval_governance_evidence.py` (SPEC §7), not hand-authored. No
other `docs/decisions/**`, `docs/specs/**`, or `docs/work_orders/**` path may
be touched in C3.

`POST /tasks/creation-intents` lives in `tasks/router.py` (§3.3), not in the
new `approvals/` router, because its path is under the existing `/tasks`
prefix.

### 3.2 Domain model + shim (2) — additive; the 12 P1-B-moved types are untouched

```
packages/operations-domain/src/operations_domain/models.py     # add ApprovalReceipt, TaskCreationIntent
apps/workspace-api/src/workspace_api/domain/models.py           # re-export both in the shim + R6.3 comment fix
```

### 3.3 CVF runtime + governed verticals (9)

```
packages/cvf-runtime/src/cvf_runtime/approval.py                 # evaluate over authenticated receipts (R3)
packages/cvf-runtime/src/cvf_runtime/policy_loader.py             # drop known_principals (R6.1)
apps/workspace-api/src/workspace_api/application/services.py             # EventService: drop approvals param, auto-collect
apps/workspace-api/src/workspace_api/application/correction_service.py   # same
apps/workspace-api/src/workspace_api/application/task_service.py         # same + intent-digest verification (R9.4-9.6)
apps/workspace-api/src/workspace_api/api/events/router.py                # ConfirmInput: drop approvals, extra="forbid"
apps/workspace-api/src/workspace_api/api/corrections/router.py           # CorrectEventInput: same
apps/workspace-api/src/workspace_api/api/tasks/router.py                 # TaskInput: same, + POST/GET creation-intents, + optional intent_id
apps/workspace-api/src/workspace_api/main.py                             # register the approvals router
```

### 3.4 Ledger (5) — dual-backend, new methods only

```
packages/operations-ledger/src/operations_ledger/tables.py       # approval_receipts, task_creation_intents (+ R6.3 comment fix)
packages/operations-ledger/src/operations_ledger/ledger.py       # Protocol: get_user_by_id, add/list_approval_receipt(s), add/get_task_creation_intent
packages/operations-ledger/src/operations_ledger/sql_ledger.py   # SqlLedger impl of the above
packages/operations-ledger/src/operations_ledger/_rows.py        # row mapping for both new tables
apps/workspace-api/src/workspace_api/infrastructure/repository.py # InMemoryLedger impl + duplicate-task_id rejection (R9.6) + R6.3 comment fix
```

### 3.5 Tests — schema parity (2)

```
tests/integration/test_schema_parity.py
tests/integration/test_schema_parity_types_and_checks.py
```

### 3.6 Tests — real, required edits (9), verified by the audit in §3.9

```
tests/cvf/test_approval_known_principals.py     # rewrite to authenticated-receipt model (R6.2)
tests/cvf/test_atomic_mutation_audit.py         # drop approvals= kwarg at each EventService/TaskService/CorrectionService call
tests/cvf/test_correction_vertical.py           # replace inline Approval(...) with receipt setup
tests/cvf/test_freeze_invariant.py              # drop approvals= kwarg
tests/cvf/test_gates_unit.py                    # assert_approval_satisfied unit tests rewritten to receipts-based signature
tests/cvf/test_task_vertical.py                 # add the two-phase creation-intent flow for its R2+ cases
tests/cvf/test_vertical_end_to_end.py           # replace inline Approval(...) with receipt setup
tests/integration/test_evidence_persistence.py  # drop approvals= kwarg / add receipt setup where needed
tests/cvf/test_customer_request_repair.py       # drop the CvfProfile(known_principals=...) constructor kwarg
```

Only call-site argument shape changes (how the test sets up a valid quorum) and
the outcomes R7/R9 deliberately change may be edited; an assertion whose
expected outcome is unrelated to approver identity must not move (stop
condition S9).

### 3.7 Comment-only, no behaviour change (2)

```
scripts/seed_dev_users.py              # R6.3: docstring no longer claims known-principals.yaml is current
packages/operations-domain/README.md   # R6.3: the reconciliation this file names is now decided
```

### 3.8 Delete (1)

```
packages/cvf-application-profile/known-principals.yaml
```

### 3.9 Catalog — generator-only outputs (2), in C3 per the P1-B lesson

```
docs/catalog/MODULE_REGISTRY.json      # module descriptive fields only; run --write
docs/catalog/MODULE_CATALOG.md         # via `python scripts/generate_catalog.py --write` only
```

### 3.10 Audit commands, run against the pre-BUILD baseline tree (re-run at G6;
a different result on the baseline is S1 — running them again post-BUILD will
of course also match the new files this WORK_ORDER itself creates, which is
expected and not a drift signal)

```bash
rg -l -g '*.py' "Approval\(|approvals\s*=|\.approvals|approvals:" apps packages scripts tests
rg -l -g '*.py' -g '*.yaml' "known_principals|known_role_for|known-principals\.yaml" apps packages scripts tests
```

Verified against the baseline (`848aeba`), **exactly**:

- **First command → 15 files**: 7 production/library (`approval.py`,
  `services.py`, `correction_service.py`, `task_service.py`, `events/router.py`,
  `corrections/router.py`, `tasks/router.py` — all in §3.3) + 8 tests
  (`test_approval_known_principals.py`, `test_atomic_mutation_audit.py`,
  `test_correction_vertical.py`, `test_freeze_invariant.py`,
  `test_gates_unit.py`, `test_task_vertical.py`, `test_vertical_end_to_end.py`,
  `test_evidence_persistence.py` — all in §3.6). `test_customer_request_repair.py`
  is correctly **absent** from this list (it references `known_principals`, not
  `Approval`/`approvals`).
- **Second command → 10 files**: `domain/models.py`, `repository.py` (§3.2/3.4),
  `approval.py` (overlap with the first list), `policy_loader.py` (§3.3),
  `operations_domain/models.py` (§3.2), `tables.py` (§3.4), `seed_dev_users.py`
  (§3.7), `test_approval_known_principals.py` (overlap),
  `test_customer_request_repair.py`, `test_gates_unit.py` (overlap) — all
  already on this allowlist.

**`packages/operations-domain/README.md` is deliberately absent from both
outputs** — the second command's glob is `-g '*.py' -g '*.yaml'`, which
structurally excludes `.md` files, so no `rg` command as specified can surface
it. It is listed in §3.7 anyway because manual review (not this grep) found it
names the same reconciliation this tranche resolves. This is stated explicitly
so a reviewer does not mistake its absence from the `rg` output for an error.

If either command, run against the baseline, surfaces a file not accounted for
above, that is **S1**: stop and report for a WORK_ORDER amendment, do not
silently widen scope inside BUILD.

## 4. Prohibited paths

```
.cvf/**
apps/workspace-api/src/workspace_api/auth/**        # no change to auth issuance/login/TTL
apps/workspace-api/src/workspace_api/config.py
apps/workspace-api/src/workspace_api/dependencies.py  # get_principal unchanged
database/migrations/001_foundation.sql
database/migrations/002_tasks_customers_reports.sql
database/migrations/003_users.sql                   # existing migrations are immutable
apps/workspace-web/**                               # lane 4
apps/integration-edge/**  apps/workspace-worker/**
infrastructure/**
docs/decisions/**  docs/specs/**  docs/work_orders/**   # EXCEPT the one file named in §3.1
.githooks/**  .github/**  Makefile
```

The 12 P1-B-moved operational types and 3 lifecycle guards must not be moved,
renamed, or redefined; `User` must not move to `operations-domain`; the
`SqlLedger(models=...)` seam must not be refactored beyond the new methods
listed in §3.4; `permission.py` is not touched — receipt-creation authorization
is the fine-grained R2.2/R9.1 role check, not a new `_ACTION_MIN_ROLE` entry.

## 5. Out of scope (reject, do not silently skip)

Auth issuance/refresh/revocation/registration/reset/rate-limiting; admin
provisioning; PostgreSQL live round-trip; incidents/handovers; frontend;
relocating `User`; any AI mode beyond the single evidence call; any claim that
"all High findings are fixed" or that production actions call a provider
(ADR §7.1); receipt pruning/cleanup of unused extra receipts (ADR §4.6).

## 6. AC → evidence matrix

| AC | Evidence command / artifact |
|---|---|
| AC-01…AC-11, AC-18, AC-19, AC-22 | `python -m pytest -q tests/cvf/test_approver_identity_reconciliation.py` (service + HTTP, both backends) |
| AC-11 | the three ADR §4.6 replay-defeat cases specifically (lifecycle-guard block, version-scope block, valid-retry-after-rollback) — no test may assert a "consumed" state/method |
| AC-12 | `python -m pytest -q tests/cvf/test_approval_known_principals.py` (rewritten) + the two §3.10 `rg` scans matching exactly the allowlisted file set |
| AC-13 | `python -m pytest -q tests/integration/test_schema_parity.py tests/integration/test_schema_parity_types_and_checks.py` |
| AC-14 | `python -m pytest -q` → **≥ baseline (verify the committed number at BUILD; 292 at `848aeba`)**, 0 failed/errors |
| AC-15 | `python scripts/testing/validate_repository.py`; `python scripts/generate_catalog.py --check`; `python scripts/check_session_state.py`; `python scripts/check_file_size.py`; workspace doctor `-ProjectPath` → `24/24` |
| AC-16 | `python scripts/run_approval_governance_evidence.py` → sanitized receipt at the §3.1 pinned path, real Alibaba HTTP 200 after a genuine authenticated quorum, gate-refusal cases logged with 0 calls, self-asserted total call count = 1 |
| AC-17 | secret scan over the changed set; inspection of the receipt and logs |
| AC-18 | within `test_approver_identity_reconciliation.py`: payload-changed-after-intent-approval → 409; intent consumed by a different principal → 409 |
| AC-19 | failure-injection test (mirrors `tests/cvf/test_atomic_mutation_audit.py`'s pattern) on `POST /approvals`'s own `transaction()`, both backends |
| AC-20 | `python scripts/apply_migrations.py --dry-run --only 004_approval_receipts.sql --database-url sqlite:///unused` (discovery only, exit 0); SQLite verification is AC-13, not this command; no `DATABASE_URL` to a real database is required anywhere in this matrix |
| AC-21 | Codex-run revert rehearsal (temporary worktree/clone, outside the primary workspace) → C3-parent source/test behaviour and baseline suite restored with a fresh ephemeral SQLite DB; C1/C2 intact; no real-database down migration claim |
| AC-22 | intent GET authorization/snapshot tests + intent/audit failure-injection tests on both backends |
| Migration diff scope | `git diff --stat -- database/` shows **only** `004_approval_receipts.sql` |

Every number is quoted from the run that produced it; copying a stale count is
itself a stop condition.

## 7. Pre-BUILD gates (all mandatory, in order)

- **G1** — Codex independently reviews this WORK_ORDER, the SPEC and the ADR for
  internal consistency and boundary correctness → `REVIEW_PASS` /
  `REVIEW_CHANGES_REQUIRED`.
- **G2** — Codex, as COMMIT_STEWARD, commits **exactly** the three authorization
  files (ADR + SPEC + WORK_ORDER), zero implementation files (**C1**).
- **G3** — Operator explicitly approves this WORK_ORDER (intact, or amended and
  re-reviewed). Absent approval, BUILD is prohibited.
- **G4** — After G1–G3, before BUILD, the continuity surfaces record this
  tranche as the active lane (**C2**, §11 allowlist); `check_session_state.py`
  passes before C2 commits.
- **G5** — Claude states the transition to IMPLEMENTATION_WORKER explicitly
  before the first source edit.
- **G6** — Clean start re-verified at that moment: `HEAD == origin/main`, clean
  worktree, doctor `24/24`, suite `292` — not assumed from this document.

## 8. Stop conditions

- **S1** — a required change falls outside §3's allowlist, any §4 path would be
  touched, or the §3.10 audit surfaces a file not already listed.
- **S2 (migration conflict)** — `004_approval_receipts.sql` collides with an
  existing migration index, or its constraints conflict with `001`/`002`/`003`,
  or `operations_ledger.tables.metadata.create_all()` against a fresh SQLite
  engine fails for either new table.
- **S3 (catalog conflict)** — `generate_catalog.py --check` cannot pass within
  C3's allowlist (pre-empted by including catalog in C3; if it still conflicts,
  stop and amend rather than deferring or force-passing).
- **S4 (authorization ambiguity)** — the SPEC/ADR do not determine a needed
  behaviour (e.g. an unlisted error case not in SPEC §5.5). Stop and request an
  amendment; do not invent governance semantics inside BUILD.
- **S5 (secret exposure)** — any API key / Authorization header / JWT / password
  / raw secret would enter a log, the receipt, or the diff.
- **S6 (provider failure)** — the live call fails, is quota-blocked, times out,
  or the selected model is unavailable: record honestly as FAIL/BLOCKED and
  stop; never coerce to PASS, never hardcode a fallback model to force a green.
- **S7 (scope expansion)** — any temptation to change auth issuance, add
  refresh/revocation/admin provisioning, run PostgreSQL live, open lanes 3–4,
  or claim production actions call a provider.
- **S8** — full suite drops below the committed baseline, any test fails/errors,
  any validator fails, or `git diff --check` errors.
- **S9** — a test's assertions/fixtures would be weakened to force a pass
  (only the deliberately-changed premises — retired YAML, removed `approvals`
  field, server-collected quorum, intent-digest binding — may be rewritten, and
  only to the new intended behaviour).
- **S10** — operator has not approved this WORK_ORDER (G3), or C1/C2 have not
  landed in order.
- **S11** — a `.md`/artifact would exceed the 600-line file-size hard limit;
  split rather than compress.

## 9. Git discipline

Codex is COMMIT_STEWARD. Claude does **not** stage, commit, amend, push, or
branch at any point. **Never** `git add -A` / `git add .`; every commit stages
explicitly enumerated paths matched to that commit's allowlist. **No**
`--amend`, `rebase`, `squash`, `reset --hard`, `checkout --`, or `push --force`.
One tranche per commit; push to `origin main` after each. `cd36b27` and all
history stay intact.

## 10. Commit plan

| # | Contents | Owner | Gate |
|---|---|---|---|
| **C1** | The three authorization artifacts only | COMMIT_STEWARD | after G1 |
| **C2** | Pre-BUILD continuity (§11) | COMMIT_STEWARD | after G2, G3 |
| **C3** | BUILD: §3's 39-path allowlist | COMMIT_STEWARD | after independent REVIEW_PASS on all ACs incl. AC-16 live receipt |
| **C4** | REVIEW/FREEZE continuity + roadmap + status + control-mapping (no catalog) | COMMIT_STEWARD | only if authorized at FREEZE |

C3 carries **no** continuity/roadmap/status file; C4 carries **no** source,
test, migration, or catalog file.

## 11. C2 / C4 allowlists

**C2** (pre-BUILD continuity): `SESSION/ACTIVE_SESSION_STATE.json`,
`SESSION/SESSION_MEMORY.md`, `CVF_SESSION/ACTIVE_SESSION_STATE.json`, and a new
`SESSION/handoffs/AGENT_HANDOFF_2026-07-23_P2B_APPROVER_IDENTITY_RECONCILIATION.md`.

**C4** (FREEZE closure, authorized only at FREEZE): the four continuity files
above + `IMPLEMENTATION_STATUS.json` + `docs/implementation/EXECUTION_ROADMAP.md`
+ `docs/cvf/CVF_CONTROL_MAPPING.md`. Constraints: the `approval` row moves from
"known-principal checked (interim)" to authenticated/receipt-bound **only from
observed source truth and only after AC-16 PASS**; High Finding #4 recorded as
**closed within the stated boundary**, never "all findings fixed"; PostgreSQL
pre-ship-gate wording preserved verbatim; the next lane (P2-A incidents/
handovers) named, not started; `check_session_state.py` passes before C4.
**No catalog path in C4** — it is in C3.

## 12. Rollback plan

`C3_PARENT = git rev-parse HEAD` is recorded immediately before C3. Rollback
rehearsal (AC-21) runs in a temporary `git worktree`/clone **outside** the
primary workspace: `git revert --no-edit <C3>`, assert the C3 paths match
`C3_PARENT`, C1/C2 remain intact, the suite returns to the committed baseline,
and the ephemeral SQLite database is recreated from reverted metadata. No down
migration exists; a real database that applied `004` retains the additive
tables until separately authorized migration work. Cleanup verified
(`git worktree remove --force` + `prune`). No history rewrite in any scenario.

## 13. Checkpoint state at the time of writing

Authored by Claude as ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR. Exactly
three files exist as uncommitted changes — the ADR, the SPEC and this WORK_ORDER.
No implementation, continuity, catalog, roadmap, migration, or status file was
touched; nothing staged, committed, or pushed; no BUILD action; no provider call;
no secret read.

### 13.1 Authorization-review revision 1 (2026-07-23)

The first independent authorization review returned `REVIEW_CHANGES_REQUIRED`
with eight findings. All eight are resolved in this revision:

| Finding | Resolution |
|---|---|
| **F1** — Task-create approval paradox | ADR §4.4 + SPEC R9: a durable `TaskCreationIntent` with a server-computed payload digest is the target `POST /approvals` binds to; `POST /tasks` re-verifies the digest against the current request body before consuming the intent. New AC-18. |
| **F2** — Receipt consumption had no model | ADR §4.6 + SPEC O6: receipts are explicitly **not** single-use; replay is defeated per-vertical by lifecycle guard (confirm), version-scope (correct), and PK uniqueness (create) — all three proven independently in AC-11, which no longer references a nonexistent "consume" operation. |
| **F3** — C3 allowlist incomplete | §3 rewritten from the ground up against the exact `rg` audits the finding specified; 39 paths total, all 8 named test files plus `test_customer_request_repair.py` (found by the second `rg`) now listed with per-file disposition; `seed_dev_users.py` and `operations-domain/README.md` added as comment-only edits (R6.3) rather than left silently stale. |
| **F4** — No authorized path for the live receipt | `docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md` named exactly, added to §3.1, with a narrow exception carved into §4's prohibited paths; minimum schema pinned in SPEC §7. |
| **F5** — Error contract / idempotency circular | SPEC §5 pins every endpoint, schema, and error case in one table; R2.4 resolved to "200 + existing receipt on exact repeat, 201 on new". |
| **F6** — Wrong migration evidence command | ADR §4.5 + SPEC AC-20: `--dry-run` proves discovery only; SQLite verification goes through `metadata.create_all()` + schema parity; no real `DATABASE_URL` required; PostgreSQL stays NOT LIVE VERIFIED. |
| **F7** — Approval act not atomically audited | ADR §4.3 + SPEC R8.3/AC-19: `POST /approvals` persists the receipt and an `approval.create` audit record inside one `transaction()`; new file `application/approval_service.py` added to §3.1. |
| **F8** — Live-call claim boundary | ADR §7.1 + SPEC §1/§10: explicit statement that no production action calls a provider; the evidence runner asserts call count 0 for every refusal and exactly 1 after a valid quorum (AC-16). |

Checkpoint state is otherwise unchanged: three uncommitted files, nothing
staged, nothing built, no provider call, no secret read.

Returned checkpoint: `READY_FOR_INDEPENDENT_AUTHORIZATION_RE_REVIEW`.
