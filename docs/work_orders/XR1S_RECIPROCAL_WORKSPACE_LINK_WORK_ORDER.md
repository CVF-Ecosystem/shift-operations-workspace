# Work Order: Shift Reciprocal Workspace-Link Authorization (XR1-S)

- Work order id: `WO-XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`
- Tranche: `XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`
- Risk: **R2**
- Status: **REPAIRED — pending independent XR1-S authorization re-review.
  BUILD IS NOT AUTHORIZED.**
- Design: `docs/decisions/ADR_2026-07-24_XR1S_RECIPROCAL_WORKSPACE_LINK.md`
- Specification: `docs/specs/XR1S_RECIPROCAL_WORKSPACE_LINK_SPEC.md`
- Live provider evidence: **NOT REQUIRED and NOT PERMITTED** for this
  tranche (no AI/agent governance behavior claim is made; see SPEC §7)
- Repository scope: `shift-operations-workspace` only, plus read-only
  inspection of `CVF-Operations-Workspace` for verification. No write to
  `CVF-Operations-Workspace` or the CVF core repository.

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `REVIEW_FAIL` with three findings, all
repaired without waiver (full detail in the ADR's repair note): `XR1S-R1`
`IMPOSSIBLE_FULL_DOCTOR_PASS` — §6/§7/§8/§9 corrected so the core/manifest
row must reach `[PASS]` while the overall doctor result may stay `PASS
WITH NOTE` with only the pre-existing legacy catalog-kit warning, never a
different or additional one. `XR1S-R2` `DETERMINISTIC_CATALOG_GATE_CONFLICT`
— §5.2's `XR1-S-C2b` ceiling gains `docs/catalog/MODULE_REGISTRY.json` and
`docs/catalog/MODULE_CATALOG.md`, conditionally authorized and bounded to
exact metric reconciliation via the canonical generator; §6/§7/§9 updated
to remove the prior mid-BUILD-conflict/amendment language. `XR1S-R3`
`UNNECESSARY_RECONCILER_SIDE_EFFECT` — §5.1/§6/§11 corrected: the hidden
core is already reconciled, so `XR1-S-C2a` is verify-only and MUST NOT run
the reconciler; a drifted core at BUILD time stops for independent review
instead. Repaired exactly the eight paths this round's ceiling permits; no
ninth path; no BUILD, stage, commit, or push occurred. Status:
`XR1S_AUTHORIZATION_REPAIRED_PENDING_INDEPENDENT_RE_REVIEW`.

## 1. Role route

```text
ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR (this authoring round) ->
REVIEWER -> COMMIT_STEWARD (XR1-S-C1, Codex) -> IMPLEMENTATION_WORKER
(XR1-S-C2a, then XR1-S-C2b, each a separate future BUILD) -> REVIEWER ->
REPAIR_WORKER if needed -> RE_REVIEW -> COMMIT_STEWARD (per-commit) ->
REVIEWER (independent receipt) -> COMMIT_STEWARD (XR1-S-C3) -> CLOSER ->
SESSION_SYNC_STEWARD -> ORCHESTRATOR
```

This authoring round holds ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR
only. Does not self-grant REVIEW_PASS, does not stage/commit/push, does not
call a provider, does not read a secret, does not run a real Shift
`scan`/`apply`, and does not modify `CVF-Operations-Workspace` or the CVF
core repository.

## 2. Authorized changed set — this authoring round (`XR1-S-C1`) — exactly 8 paths

Create:

1. `docs/decisions/ADR_2026-07-24_XR1S_RECIPROCAL_WORKSPACE_LINK.md`
2. `docs/specs/XR1S_RECIPROCAL_WORKSPACE_LINK_SPEC.md`
3. `docs/work_orders/XR1S_RECIPROCAL_WORKSPACE_LINK_WORK_ORDER.md`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-07-24_XR1S_RECIPROCAL_WORKSPACE_LINK.md`

Update:

5. `SESSION/ACTIVE_SESSION_STATE.json` (canonical)
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json` (compatibility mirror)
7. `SESSION/SESSION_MEMORY.md`
8. `IMPLEMENTATION_STATUS.json`

**No ninth path.** Not touched this round: `docs/INDEX.md`, `docs/catalog/**`,
`docs/implementation/EXECUTION_ROADMAP.md`, `docs/cvf/CVF_CONTROL_MAPPING.md`,
any application source/test/migration path, `.cvf/manifest.json`,
`.gitignore`, `AGENTS.md`, any `P2B_APPROVER_IDENTITY_RECONCILIATION*`
artifact, and the untracked assessment file.

## 3. Explicit exclusions (stop and escalate if touched)

- `P2B-APPROVER-IDENTITY-RECONCILIATION`'s ADR, SPEC, WORK_ORDER, or any
  implementation path — its WORK_ORDER remains `DRAFT — NOT APPROVED. BUILD
  IS NOT AUTHORIZED.` PARKED: not edited, resumed, superseded, cancelled, or
  built by this tranche.
- `CVF-Operations-Workspace` — read-only inspection only (verifying commits
  `74170650bd7f2732bc2eec985e5b891df6d45897` and
  `3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a` exist and their ordering); no
  write, no BUILD, no commit performed there.
- The CVF core repository/bootstrap-learning content — untouched.
- Every third repository.
- `.cvf/manifest.json` — recorded as the `XR1-S-C2a` prerequisite; not
  touched during `XR1-S-C1`.
- `docs/catalog/**`, `docs/INDEX.md`, `docs/implementation/EXECUTION_ROADMAP.md`,
  `docs/cvf/CVF_CONTROL_MAPPING.md`, `.gitignore`, `AGENTS.md`.
- The untracked assessment file
  (`docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`)
  — never read, edited, staged, or committed; its
  `sha256:168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`
  must remain unchanged.
- Any provider/AI call; any real secret access; any real Shift `scan`/`apply`
  execution.

## 4. Roles and ownership

| Role | Holder | Notes |
|---|---|---|
| ORCHESTRATOR / SPEC_AUTHOR / WORK_ORDER_AUTHOR | Claude (this context) | Authors the three artifacts plus continuity; holds no implementation role at this checkpoint. |
| REVIEWER (independent) | Codex | Reviews this authorization package; later reviews `XR1-S-C2a` and `XR1-S-C2b` BUILD independently. |
| COMMIT_STEWARD | Codex | Verifies every changed set against its authorized ceiling and owns every commit/push. |
| IMPLEMENTATION_WORKER | assigned only after independent review of this package, per future BUILD | States the role transition before the first edit of each future commit. |
| SESSION_SYNC_STEWARD / CLOSER | assigned at `XR1-S-C2a-SYNC`/`XR1-S-C2b-SYNC`/`XR1-S-C3` | Continuity and closure. |

R2 role separation is mandatory: the implementing context must not be the
approving context, for both future BUILD commits.

## 5. Authorized BUILD ceiling — future, not executed this round

### 5.1 `XR1-S-C2a` — core-pin repair, verify-only (exactly one path, `XR1S-R3`)

- `.cvf/manifest.json` — change **exactly one line**: `cvfCoreCommit` from
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` to
  `27137db4d9aa2aea931ddd2507185d5c24943080`.

Nothing else may be touched by `XR1-S-C2a`. The hidden sibling CVF core is
**already** reconciled to the target commit (verified at authoring time:
core `HEAD == origin/main == 27137db4d9aa2aea931ddd2507185d5c24943080`,
clean worktree). `XR1-S-C2a` **MUST NOT** invoke the sanctioned reconciler
(`update_cvf_workspace_public_core.ps1`) and **MUST NOT** produce any
out-of-repository side effect — no fresh core clone, no new
`_cvf-core-backups/` entry, no `WORKSPACE_RULES.md` regeneration.
`.cvf/local-binding.json` (git-ignored) is not expected to change either,
since no reconciler runs. If the core is found drifted from this state at
BUILD time, see §9's stop condition — do not reconcile it silently within
this commit.

### 5.2 `XR1-S-C2b` — reciprocal descriptor, plus bounded conditional catalog reconciliation (`XR1S-R2`)

Required (always):

- `.cvf/workspace-link.json` (new) — exactly `ADR-2026-07-24-XR1S-
  RECIPROCAL-WORKSPACE-LINK` §2.2's five-field shape.
- `tests/integration/test_xr1s_workspace_link_descriptor.py` (new) —
  proving `SPEC-XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24` R-16..R-23.

Conditionally authorized — a **ceiling**, touched only if §6's catalog step
actually reports drift caused by the two required files above:

- `docs/catalog/MODULE_REGISTRY.json` — metrics only, written exclusively by
  `python scripts/generate_catalog.py --write`, never hand-edited.
- `docs/catalog/MODULE_CATALOG.md` — regenerated canonically from the same
  run, never hand-edited.

Nothing else may be touched by `XR1-S-C2b`. If `generate_catalog.py
--check` reports zero drift from the two required files, the two catalog
paths are not touched at all and `XR1-S-C2b`'s actual changed set stays
exactly the two required paths.

### 5.3 Continuity commits

`XR1-S-C2a-SYNC` and `XR1-S-C2b-SYNC` each touch only continuity paths
(`SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json`,
`CVF_SESSION/ACTIVE_SESSION_STATE.json`, `IMPLEMENTATION_STATUS.json`) —
never an implementation path from §5.1 or §5.2.

### 5.4 `XR1-S-C2a` and `XR1-S-C2b` must never be combined

Neither future commit's changed set may contain any path from the other's.
Each receives its own continuity synchronization, its own post-commit/
pre-push direct-sibling-worktree rehearsal, and its own push, before the
tranche is considered closed.

## 6. Execution order for each future BUILD (load-bearing, not stylistic)

For `XR1-S-C2a` (verify-only, `XR1S-R3` — no reconciler run):

1. Capture pre-state baseline (`git status --porcelain`, hidden core
   remote/HEAD/`origin/main`/cleanliness, manifest `cvfCoreCommit`, doctor
   result).
2. Read-only verify the hidden core's `origin` remote identity.
3. Verify the hidden core's `HEAD` equals its `origin/main` equals
   `27137db4d9aa2aea931ddd2507185d5c24943080` exactly, and its worktree is
   clean. **If any of these does not hold, stop here and escalate for
   independent review (§9) — do not run the reconciler and do not proceed
   to step 4.**
4. Only if step 3 holds in full: edit `.cvf/manifest.json`'s
   `cvfCoreCommit` — single line, no re-serialization.
5. Run the workspace doctor; require the core/manifest row to reach
   `[PASS]`, and require no new `[FAIL]`/`[WARN]` beyond the one
   pre-existing legacy catalog-kit warning.
6. Run §7's required checks.
7. Capture post-state; review the exact changed set.

For `XR1-S-C2b` (`XR1S-R2` — bounded conditional catalog reconciliation):

1. Capture pre-state baseline (`git status --porcelain`, current test count,
   catalog/session-state/validator/file-size-guard results).
2. Author `.cvf/workspace-link.json` exactly per §5.2.
3. Author `tests/integration/test_xr1s_workspace_link_descriptor.py` exactly
   per §5.2, proving every SPEC R-16..R-23 assertion.
4. Run the focused descriptor tests; they must pass before proceeding.
5. Run `python scripts/generate_catalog.py --check`. If it reports zero
   drift caused by steps 2–3, skip to step 8. If it reports drift caused by
   those two files, continue to step 6.
6. Update the exact affected registry metrics using
   `python scripts/generate_catalog.py --write` (never a hand-edit), and
   regenerate `docs/catalog/MODULE_CATALOG.md` canonically from the same
   run.
7. Re-run `python scripts/generate_catalog.py --check`; it must report
   clean.
8. Run the full regression suite; require it green.
9. Run §7's required checks.
10. Capture post-state; review the exact changed set (exactly the two
    required paths, plus the two catalog paths only if steps 5–7 actually
    touched them).

## 7. Required checks (both future BUILD commits)

- `python -m pytest -q`
- `python scripts/testing/validate_repository.py`
- `python scripts/check_session_state.py`
- `python scripts/generate_catalog.py --check`
- `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`
  (workspace doctor)
- File-size guard
- JSON parse of every JSON file in the respective changed set
- Secret scan over the respective changed set — clean

At `XR1-S-C2a`, `generate_catalog.py --check` must pass **without
regenerating anything** — the catalog is entirely outside `XR1-S-C2a`'s
ceiling, so any drift there means the boundary was breached. At
`XR1-S-C2b`, `generate_catalog.py --check` must pass, with regeneration
permitted **only** through §6's bounded steps 5–7 — any catalog change
outside that exact reconciliation is a boundary breach, not a permitted
outcome.

## 8. Required evidence (this authoring round)

- **E-1** — `git status --porcelain` showing exactly the 8 §2 paths.
- **E-2** — `git diff --cached --name-only` empty (nothing staged).
- **E-3** — JSON parse of `SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`, `IMPLEMENTATION_STATUS.json`.
- **E-4** — `git diff --check` clean.
- **E-5** — `python scripts/check_session_state.py` PASS.
- **E-6** — `python -m pytest -q` — full current test baseline.
- **E-7** — Workspace doctor result, quoted verbatim, retaining the known
  manifest/core-pin warning (not claimed as full PASS this round).
- **E-8** — Shift HEAD/`origin/main`, Operations HEAD/`origin/main`, and the
  Operations authorization/continuity commit hashes (§9 of the ADR).
- **E-9** — Assessment file SHA-256, unchanged.
- **E-10** — Confirmation of no provider call, no secret read, no BUILD.
- **E-11** — `python scripts/check_file_size.py` PASS for this round's
  changed set.
- **E-12** — `python scripts/generate_catalog.py --check` PASS for this
  round's changed set (this authoring round touches no source/module path,
  so zero drift is expected — distinct from `XR1-S-C2b`'s future, bounded
  reconciliation).

## 9. Stop conditions

Stop, change nothing further, and report a finding — do not work around, do
not self-approve past — if any of the following occurs:

- Either repository's pin/remote drifts from the values recorded in the ADR
  (§1.2) at the time of this authoring round.
- Any of the two named Operations commits (`74170650bd7f2732bc2eec985e5b891df6d45897`,
  `3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a`) is missing from Operations'
  `origin/main`.
- The assessment file's hash mutates from
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`.
- Any edit, resumption, supersession, cancellation, or BUILD attempt against
  `P2B-APPROVER-IDENTITY-RECONCILIATION`'s parked authorization.
- `SESSION/ACTIVE_SESSION_STATE.json` and `CVF_SESSION/ACTIVE_SESSION_STATE.json`
  disagree (canonical/mirror continuity conflict) —
  `python scripts/check_session_state.py` must PASS before this round is
  considered complete.
- At `XR1-S-C2a`: any catalog drift at all (the catalog is entirely outside
  its ceiling).
- At `XR1-S-C2b`: any catalog change to a path, field, or module outside
  exactly what §5.2/§6 authorizes (bounded metric reconciliation for the
  two required files only) — not something `IMPLEMENTATION_WORKER` may
  resolve by expanding scope unilaterally.
- At `XR1-S-C2a`: the hidden core found not clean, not at
  `27137db4d9aa2aea931ddd2507185d5c24943080`, or its `HEAD` no longer
  equal to `origin/main`, at BUILD time — stop and escalate for
  independent review; do not run the reconciler to repair it silently and
  do not create `_cvf-core-backups/` or any other out-of-repository side
  effect.
- At either future BUILD: any new workspace-doctor `[FAIL]` or `[WARN]`
  beyond the exact pre-existing `LEGACY_PROJECT: governed downstream
  catalog kit not present` warning.
- A need for a ninth authoring path this round.
- `XR1-S-C2a` and `XR1-S-C2b` being combined into one commit, at any future
  point.
- `sourcePin` (or any consumer-acceptance-state field) being added to the
  Shift descriptor at `XR1-S-C2b`.
- Any absolute path, hostname, or username entering tracked content.
- Any source, migration, runtime, or roadmap scope expansion beyond §5.
- Any provider call, real secret access, or real `scan`/`apply` execution.
- A failed test, validator, doctor check, or rehearsal, at this round or
  either future BUILD.

## 10. Commit plan

| Commit | Repository | Content |
|---|---|---|
| `XR1-S-C1` | Shift | Exactly the 8 §2 paths — authorization package and authorization continuity. No seventh... no ninth path. |
| `XR1-S-C2a` | Shift | Exactly `.cvf/manifest.json`, one-line core-pin repair only, verify-only, no reconciler run (§5.1). |
| `XR1-S-C2a-SYNC` | Shift | Canonical/mirror continuity receipt only (§5.3). No implementation path. |
| `XR1-S-C2b` | Shift | The two required §5.2 paths (descriptor + test), plus `docs/catalog/MODULE_REGISTRY.json`/`docs/catalog/MODULE_CATALOG.md` only if §6's bounded catalog step actually touches them. |
| `XR1-S-C2b-SYNC` | Shift | Continuity receipt only (§5.3). |
| `XR1-S-C3` | Shift | Codex-owned independent review receipt and FREEZE continuity. |

Any optional post-push synchronization is its own separate, continuity-only
commit — never folded into the commit whose push it records.

Every commit:

1. Explicit-path staging only (never `git add -A` or `git add .`).
2. Commit created by Codex (COMMIT_STEWARD).
3. Post-commit/pre-push direct-sibling-worktree rehearsal.
4. Push only after the rehearsal PASSes.
5. No amend, rebase, force-push, `git add .`, or `git add -A`, ever.

## 11. Rollback

- `XR1-S-C1`: revert the single authorization commit; no implementation
  file is involved.
- `XR1-S-C2a`: revert the one-line manifest change (or the commit once
  made). The hidden core itself is never touched by this commit (verify-only,
  `XR1S-R3`), so there is nothing to roll back on the core side.
- `XR1-S-C2b`: revert the commit; if the conditional catalog paths were
  touched, they revert with it in the same single-commit revert — no other
  file is touched, so rollback stays a clean single-commit revert either
  way.
- No project source, schema, migration, or data is involved at any stage of
  this tranche, so no data rollback exists or is needed.

## 12. Approval / Gate

- `XR1-S-C1` (this package) is authorized to be committed and pushed only
  after Codex, acting as independent REVIEWER, returns REVIEW_PASS on this
  ADR, this SPEC, and this WORK_ORDER.
- `XR1-S-C2a` and `XR1-S-C2b` BUILD are each authorized to begin only after
  `XR1-S-C1` is committed, rehearsed, and pushed. Neither may begin before
  the other completes its own full cycle (BUILD → REVIEW → commit) unless
  explicitly reviewed as safe to run concurrently — the default assumption
  is sequential, `XR1-S-C2a` before `XR1-S-C2b`, since the core-pin repair
  is the simpler, lower-blast-radius change.
- `XR1-S-C3` (independent review receipt and FREEZE continuity) closes the
  tranche and is the signal Operations' `XR1-O-C2` waits on.
