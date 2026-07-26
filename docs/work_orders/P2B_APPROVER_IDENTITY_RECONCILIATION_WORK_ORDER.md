# WORK ORDER — P2-B Approver Identity Reconciliation

- Work order id: `WO-P2B-APPROVER-IDENTITY-RECONCILIATION`
- Tranche: `P2B-APPROVER-IDENTITY-RECONCILIATION`
- Control-chain phase at authoring time: `WORK_ORDER`
- Risk: **R2** — REVIEWER independent from IMPLEMENTATION_WORKER
- Status: **DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.**
- Design: `docs/decisions/ADR_2026-07-23_P2B_APPROVER_IDENTITY_RECONCILIATION.md`
- Specification: `docs/specs/P2B_APPROVER_IDENTITY_RECONCILIATION_SPEC.md`
- Baseline (historical, authoring-time): `848aebaf03af4efa16d04d7f0f02b6d9da0e564b`
  (`HEAD == origin/main`, clean, doctor `24/24`, suite `292 passed`) — a frozen
  record, not the BUILD target (F10).
- Baseline (current authorization re-review, revision 2): `58918c638ab34aa3fb2f7bf7de3a1ac44337b26a`
  — suite `306 passed`; doctor `RESULT: PASS WITH NOTE (24 passed, 1
  warning(s))` (sole warning: `LEGACY_PROJECT: governed downstream catalog kit
  not present`, F12); worktree carries no tracked modification and exactly one
  preserved untracked file, `docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
  (SHA-256 `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`,
  unedited/unstaged/uncommitted — F11).
- **BUILD baseline** is neither number above: it is captured fresh at C2/G6
  (§7), immediately before BUILD, from whatever `HEAD == origin/main` actually
  is at that moment. AC-14/G6/S8 are evaluated against that captured number,
  never a hardcoded `292` or `306`.

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
§3.4 for the exact audit commands a reviewer re-runs. **Total: 39 paths.** This
repair round's F9 fix (order-invariant quorum matching) adds test coverage
only, inside `test_approver_identity_reconciliation.py` (§3.1) and
`test_gates_unit.py` (§3.6), both already on this list — **the 39-path ceiling
is not raised.**

### 3.1 Create (7)

```
database/migrations/004_approval_receipts.sql
apps/workspace-api/src/workspace_api/api/approvals/__init__.py
apps/workspace-api/src/workspace_api/api/approvals/router.py         # POST /approvals only
apps/workspace-api/src/workspace_api/application/approval_service.py # receipt + audited intent + authority resolver + digest logic
scripts/run_approval_governance_evidence.py
tests/cvf/test_approver_identity_reconciliation.py                   # incl. AC-23 order-invariant/permutation coverage (F9)
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
tests/cvf/test_gates_unit.py                    # assert_approval_satisfied unit tests rewritten to receipts-based signature; incl. AC-23 order-invariant matching-algorithm coverage (F9)
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

Verified against the historical authoring baseline (`848aeba`) at the time this
allowlist was authored, **exactly** (F10 — this is a record of that
verification, not a claim that `848aeba` is the tree BUILD runs against; the
same two commands MUST be re-run against the actual pre-BUILD `HEAD` at G6,
and any new surfaced file is still S1):

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
| AC-14 | `python -m pytest -q` → **≥ the BUILD baseline captured fresh at C2/G6 (F10 — neither `292` at `848aeba` nor `306` at `58918c6` is the hardcoded target; quote the number from the run that produced it)**, 0 failed/errors |
| AC-15 | `python scripts/testing/validate_repository.py`; `python scripts/generate_catalog.py --check`; `python scripts/check_session_state.py`; `python scripts/check_file_size.py`; workspace doctor `-ProjectPath` → **24 checks PASS, core/manifest row PASS, 0 FAIL, no warning beyond the single accepted `LEGACY_PROJECT: governed downstream catalog kit not present` note** — i.e. `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` is the accepted outcome, not an unqualified `24/24`/"doctor clean" claim (F12) |
| AC-16 | `python scripts/run_approval_governance_evidence.py` → sanitized receipt at the §3.1 pinned path, real Alibaba HTTP 200 after a genuine authenticated quorum, gate-refusal cases logged with 0 calls, self-asserted total call count = 1 |
| AC-17 | secret scan over the changed set; inspection of the receipt and logs |
| AC-18 | within `test_approver_identity_reconciliation.py`: payload-changed-after-intent-approval → 409; intent consumed by a different principal → 409 |
| AC-19 | failure-injection test (mirrors `tests/cvf/test_atomic_mutation_audit.py`'s pattern) on `POST /approvals`'s own `transaction()`, both backends |
| AC-20 | `python scripts/apply_migrations.py --dry-run --only 004_approval_receipts.sql --database-url sqlite:///unused` (discovery only, exit 0); SQLite verification is AC-13, not this command; no `DATABASE_URL` to a real database is required anywhere in this matrix |
| AC-21 | Codex-run revert rehearsal (temporary worktree/clone, outside the primary workspace) → C3-parent source/test behaviour and baseline suite restored with a fresh ephemeral SQLite DB; C1/C2 intact; no real-database down migration claim |
| AC-22 | intent GET authorization/snapshot tests + intent/audit failure-injection tests on both backends |
| AC-23 | Permutation test of an R3 quorum and an R4 quorum inside `tests/cvf/test_approver_identity_reconciliation.py` (service/HTTP) and `tests/cvf/test_gates_unit.py` (matching-algorithm unit level) — every permutation of a valid quorum's receipts PASSes, distinct-principal/self-approval/insufficient-quorum outcomes unchanged (F9); both files already on the §3 allowlist, no new path |
| Migration diff scope | `git diff --stat -- database/` shows **only** `004_approval_receipts.sql` |

Every number is quoted from the run that produced it; copying a stale count is
itself a stop condition.

## 7. Pre-BUILD gates (all mandatory, in order)

**F13 note — C1 already exists.** The original **C1** (the three authorization
artifacts) is already committed at `f98f29e145fa002be070e9d44520d20f0f82dcb3`
and is **retained as-is** — it is never recreated, amended, rewritten, or
squashed. Every gate below that used to describe "committing C1" now describes
this repair round's **C1b**, a separate authorization-amendment commit
carrying the same three files (this revision's fixes for F9–F13), owned by
Codex as COMMIT_STEWARD. C1b requires its own independent re-review before C2
may land.

- **G1** — Codex independently reviews this WORK_ORDER, the SPEC and the ADR for
  internal consistency and boundary correctness → `REVIEW_PASS` /
  `REVIEW_CHANGES_REQUIRED`. (Historical: the first pass returned
  `REVIEW_CHANGES_REQUIRED` on F1–F8, resolved in revision 1; the second pass
  returned `REVIEW_CHANGES_REQUIRED` on F9–F13, resolved in this revision 2.)
- **G1b (new, F13)** — Codex, as COMMIT_STEWARD, commits **exactly** the three
  authorization files (ADR + SPEC + WORK_ORDER) as **C1b** — an
  authorization-amendment commit distinct from, and after, the original **C1**
  (`f98f29e`, retained untouched). C1b contains zero implementation files.
- **G1c (new, F13)** — Independent re-review of C1b by Codex →
  `REVIEW_PASS` / `REVIEW_CHANGES_REQUIRED`. BUILD authorization does not
  advance past this point without `REVIEW_PASS` on C1b.
- **G2** — Checkpoint: both C1 (`f98f29e`, original) and C1b (this round's
  amendment) are committed, and G1c returned `REVIEW_PASS`. (Historically,
  before this repair round, G2 denoted the single act of committing the three
  authorization files; F13 splits that into the already-landed C1 plus this
  round's C1b.)
- **G3** — Operator explicitly approves this WORK_ORDER as amended by C1b
  (intact, or further amended and re-reviewed). Absent approval, BUILD is
  prohibited.
- **G4** — After G1–G3 (including G1b/G1c), before BUILD, the continuity
  surfaces record this tranche as the active lane (**C2**, §11 allowlist);
  `check_session_state.py` passes before C2 commits.
- **G5** — Claude states the transition to IMPLEMENTATION_WORKER explicitly
  before the first source edit — only after **C2 has committed and pushed**
  and **G6 has been re-checked** at that same moment.
- **G6 (rewritten, F10/F11/F12)** — Clean start re-verified at that moment,
  fresh, not assumed from this document:
  - `HEAD == origin/main`, at whatever commit that actually is post-C2 (**this
    is the BUILD baseline** — capture and record its suite count here; do not
    substitute `292` or `306` from either baseline recorded in this document's
    header, F10);
  - the worktree carries **no tracked modification**, and **at most** the one
    preserved untracked file
    `docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
    with SHA-256 `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`
    unchanged, unedited, unstaged, and uncommitted — this file being present
    and untouched is **not** a stop condition; **any other** untracked or
    modified path **is** stop condition S1 (F11 — a demand for an absolutely
    empty `git status --porcelain -uall` is not the correct gate given this
    file is deliberately preserved);
  - workspace doctor reports `RESULT: PASS WITH NOTE (24 passed, 1
    warning(s))` — 24 checks PASS including the core/manifest row, 0 FAIL, and
    the **sole** permitted warning is `LEGACY_PROJECT: governed downstream
    catalog kit not present`; any other warning, or any FAIL, is a stop
    condition (F12 — this is not claimed as "doctor clean" or unqualified
    `24/24`);
  - full suite passes with **0 failed, 0 errors**, at a count **≥ the BUILD
    baseline just captured above** in this same G6 check (F10).

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
- **S8** — full suite drops below the BUILD baseline captured at G6 (F10 — not
  a hardcoded `292`/`306`), any test fails/errors, any validator fails, doctor
  reports a FAIL or any warning beyond the single accepted
  `LEGACY_PROJECT: governed downstream catalog kit not present` note (F12), or
  `git diff --check` errors.
- **S9** — a test's assertions/fixtures would be weakened to force a pass
  (only the deliberately-changed premises — retired YAML, removed `approvals`
  field, server-collected quorum, intent-digest binding — may be rewritten, and
  only to the new intended behaviour).
- **S10** — operator has not approved this WORK_ORDER (G3); C1, C1b, or C2 have
  not landed in order; or C1b lacks `REVIEW_PASS` (G1c).
- **S11** — a `.md`/artifact would exceed the 600-line file-size hard limit;
  split rather than compress.

## 9. Git discipline

Codex is COMMIT_STEWARD. Claude does **not** stage, commit, amend, push, or
branch at any point. **Never** `git add -A` / `git add .`; every commit stages
explicitly enumerated paths matched to that commit's allowlist. **No**
`--amend`, `rebase`, `squash`, `reset --hard`, `checkout --`, or `push --force`.
One tranche per commit; push to `origin main` after each. `cd36b27` and all
history stay intact. **The original C1 (`f98f29e145fa002be070e9d44520d20f0f82dcb3`)
is never amended, rewritten, or squashed under any circumstance (F13)** — this
repair round's changes land only as the new, separate C1b commit.

## 10. Commit plan

| # | Contents | Owner | Gate |
|---|---|---|---|
| **C1** | The three original authorization artifacts | COMMIT_STEWARD | **already committed** at `f98f29e145fa002be070e9d44520d20f0f82dcb3`, retained as-is (F13) |
| **C1b (new, F13)** | Authorization-amendment: the same three files, this repair round's fixes for F9–F13 | COMMIT_STEWARD | after G1 (this round's `REVIEW_CHANGES_REQUIRED`) |
| **C2** | Pre-BUILD continuity (§11) | COMMIT_STEWARD | after G1c `REVIEW_PASS` on C1b, G2, G3 |
| **C3** | BUILD: §3's 39-path allowlist | COMMIT_STEWARD | after independent REVIEW_PASS on all ACs incl. AC-16 live receipt |
| **C4** | REVIEW/FREEZE continuity + roadmap + status + control-mapping (no catalog) | COMMIT_STEWARD | only if authorized at FREEZE |

C1 and C1b are both authorization-only commits: three files, no
implementation, no test, no migration. C3 carries **no**
continuity/roadmap/status file; C4 carries **no** source, test, migration, or
catalog file.

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
`C3_PARENT`, C1/C1b/C2 remain intact, the suite returns to the BUILD baseline
captured at G6, and the ephemeral SQLite database is recreated from reverted
metadata. No down
migration exists; a real database that applied `004` retains the additive
tables until separately authorized migration work. Cleanup verified
(`git worktree remove --force` + `prune`). No history rewrite in any scenario.

## 13. Checkpoint state at the time of writing

Authored by Claude as ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR. At
original authoring, exactly three files existed as uncommitted changes — the
ADR, the SPEC and this WORK_ORDER; those three were subsequently committed as
**C1** (`f98f29e145fa002be070e9d44520d20f0f82dcb3`), retained untouched since
(F13). No implementation, continuity, catalog, roadmap, migration, or status
file was touched by that commit or by this repair round; nothing staged,
committed, or pushed by this repair round; no BUILD action; no provider call;
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

Checkpoint state at the end of revision 1 was: three uncommitted files,
nothing staged, nothing built, no provider call, no secret read. Those three
files were subsequently committed as **C1** (`f98f29e`) after `REVIEW_PASS`
(F13).

### 13.2 Authorization-review revision 2 (2026-07-26)

The independent authorization re-review, run at baseline
`58918c638ab34aa3fb2f7bf7de3a1ac44337b26a` (`306 passed`), returned
`REVIEW_CHANGES_REQUIRED` with five findings. All five are resolved in this
revision, as this repair round's edits to the same three authorization files:

| Finding | Resolution |
|---|---|
| **F9** — Order-dependent quorum matching | ADR §4.7/O7 + SPEC R3.6/AC-23: quorum matching is redefined as deterministic, order-invariant bipartite matching/backtracking; new permutation-based AC-23 lives inside the already-allowlisted `test_approver_identity_reconciliation.py`/`test_gates_unit.py` — the 39-path ceiling is not raised. |
| **F10** — Stale prebuild baseline | Header + ADR §2 + SPEC Terminology/AC-14 + this WORK_ORDER's header/§3.10/§6/§7 G6/S8 now distinguish the historical authoring baseline (`848aeba`/292), the current authorization re-review baseline (`58918c6`/306), and the BUILD baseline (captured fresh at G6, never hardcoded to either number). |
| **F11** — Impossible clean-worktree gate | §7 G6 is rewritten: no tracked modification, and **at most** the one preserved untracked file (`ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`, SHA-256 `168ea2c7…70fde2`, unedited/unstaged/uncommitted) is the accepted clean-start condition; any other untracked/modified path remains S1. |
| **F12** — Doctor-note drift | SPEC AC-15 + this WORK_ORDER's §6/§7 G6/S8 now state the honest current doctor outcome — `PASS WITH NOTE (24 passed, 1 warning(s))`, sole warning `LEGACY_PROJECT: governed downstream catalog kit not present`, 0 FAIL — rather than an unqualified `24/24`/"doctor clean" claim. |
| **F13** — C1 already exists | §7/§9/§10/§13 now record that the original **C1** (`f98f29e145fa002be070e9d44520d20f0f82dcb3`) is retained untouched; this repair round is a separate **C1b** authorization-amendment commit (same three files), gated by its own independent re-review (new **G1b**/**G1c**) before **C2** — and, per G5, Claude transitions to IMPLEMENTATION_WORKER only after C2 has committed/pushed and G6 is re-checked. |

Checkpoint state is otherwise unchanged from the end of revision 1: exactly
three files carry this repair round's edits (the ADR, the SPEC, and this
WORK_ORDER); nothing staged, committed, or pushed by this repair round; no
BUILD action; no provider call; no secret read. The one pre-existing untracked
file (`ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`) was read
only to confirm its SHA-256, never edited.

Returned checkpoint: `READY_FOR_INDEPENDENT_AUTHORIZATION_RE_REVIEW`.
