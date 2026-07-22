# Work Order: CVF Core Pin Synchronization

- Work order: `WO-CVF-CORE-PIN-2026-07-23`
- Tranche: `CVF-CORE-PIN-2026-07-23`
- Risk: **R2** (governance-core pin)
- Status: **§1-§12 COMPLETE — BUILD REVIEWED AND COMMITTED (`da9a122`).
  §13 FREEZE ADDENDUM REVIEW_PASS — AUTHORIZED_AFTER_ADDENDUM_COMMIT.** The
  core-pin BUILD passed independent review and is committed. §13 authorizes
  the continuity/FREEZE work that §2 deliberately deferred; that work remains
  prohibited until the addendum authorization commit hash is supplied.
- Design: `docs/decisions/ADR_2026-07-23_CVF_CORE_PIN.md`
- Specification: `docs/specs/CVF_CORE_PIN_SPEC.md`
- Live provider evidence: **NOT REQUIRED and NOT PERMITTED** for this tranche
  (no AI/agent governance behavior claim is made; see SPEC §8)

## 1. Authorized changed set

### 1.1 In-repository — exactly one file

- `.cvf/manifest.json` — change **exactly one line**: the value of
  `cvfCoreCommit`, from
  `c1076dc4be9ef9058b7c4e7b96def59c26aab148`
  to
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`.

  Full 40-character lowercase hex. No other key touched, no key added, no key
  removed, no reformatting, no re-serialization. `git diff -- .cvf/manifest.json`
  must show one `-` line and one `+` line.

**That is the complete authorized in-repository changed set.** Nothing else
in this repository may be modified, created, or deleted by BUILD.

### 1.2 Out-of-repository, expected and authorized

These are produced by the sanctioned reconciler and the doctor entrypoint.
They are not part of any commit (the workspace root is not a git repository;
`.cvf/local-binding.json` is git-ignored), but they are real filesystem
change and must be captured and reported, not hidden:

- `<workspaceRoot>/.Controlled-Vibe-Framework-CVF/` — replaced by a fresh
  clone of the public remote at `origin/main`.
- `<workspaceRoot>/_cvf-core-backups/.Controlled-Vibe-Framework-CVF-<timestamp>/`
  — the preserved previous core. Do not delete it during this tranche.
- `<workspaceRoot>/WORKSPACE_RULES.md` — regenerated from the reconciler's
  template with a recomputed sibling-project list.
- Workspace root wrapper scripts — refreshed by
  `install_cvf_workspace_root_wrappers.ps1`, invoked by the reconciler.
- `<project>/.cvf/local-binding.json` — rewritten by
  `scripts/initialize_cvf_clone.ps1`; `resolvedCoreCommit` moves to the new
  hash. Git-ignored, therefore not in the changed set.

Public-profile sync will **not** run (`ACTIVE_RULE_PACK.json` `activeProfile`
is `operator-local`, and the reconciler only syncs for `public-free` /
`paid-user-safe`). If it runs anyway, stop — the precondition read at INTAKE
was wrong.

## 2. Explicit exclusions

- **The uncommitted P2-B FREEZE batch.** These 11 paths are owned by another
  agent context and must be byte-identical before and after BUILD:

  ```
   M CVF_SESSION/ACTIVE_SESSION_STATE.json
   M IMPLEMENTATION_STATUS.json
   M SESSION/ACTIVE_SESSION_STATE.json
   M SESSION/SESSION_MEMORY.md
   M docs/catalog/MODULE_CATALOG.md
   M docs/catalog/MODULE_REGISTRY.json
   M docs/cvf/CVF_CONTROL_MAPPING.md
   M docs/implementation/EXECUTION_ROADMAP.md
   M packages/cvf-runtime/src/cvf_runtime/identity.py
  ?? SESSION/handoffs/AGENT_HANDOFF_2026-07-23_P2B_AUTHENTICATION_REPAIR_FREEZE.md
  ?? docs/decisions/P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md
  ```

  They must not be edited, deleted, staged, stashed, checked out, restored,
  reset, cleaned, or committed by this tranche.
- **Continuity surfaces during BUILD** — `SESSION/**`, `CVF_SESSION/**`,
  `IMPLEMENTATION_STATUS.json`, `docs/catalog/**`, `docs/INDEX.md`,
  `docs/implementation/**`, `docs/cvf/**`. Overlapping with the P2-B batch is
  exactly why. Any continuity sync for this tranche belongs to a later FREEZE
  phase, after the P2-B batch is committed, and needs its own authorization.
- **Project source, tests, migrations, schema, data** — untouched.
- **The CVF core's contents** — read-only reference. Only its checked-out
  commit changes, and only via the reconciler.
- **Commit `cd36b27`** — no rewrite, squash, amend, rebase, or force-push.
- **All provider surfaces** — no `ALIBABA_API_KEY` read, no provider call, no
  `packages/ai-providers/**` change.
- **Any file not named in §1.1.** If BUILD discovers a genuine need to touch
  anything else, STOP (§8) and return to WORK_ORDER_AUTHOR for an amendment.
  Do not silently expand scope.

## 3. Roles and ownership

| Role | Holder | Responsibility |
|---|---|---|
| WORK_ORDER_AUTHOR | authoring context | Bounds scope, evidence, stop conditions. Does **not** execute BUILD or self-approve. |
| IMPLEMENTATION_WORKER | authoring context, **only after** the authorization commit exists and its hash is supplied | Executes §5 exactly; produces §6 evidence; leaves the result uncommitted. |
| REVIEWER | **independent context** (required for R2 per `AGENTS.md`) | Re-runs — not re-reads — every §6 check; confirms the changed set; returns findings. |
| COMMIT_STEWARD | **independent context** | Verifies the changed set against §1.1 and owns every commit action. |

Roles are named by responsibility, never by provider. A single agent may hold
several roles in sequence, stating each transition — **except** that for this
R2 tranche REVIEWER and COMMIT_STEWARD must be independent from
IMPLEMENTATION_WORKER.

## 4. Authorized BUILD — precise definition

### 4.1 Update the hidden sibling core with the standard script

```powershell
powershell -ExecutionPolicy Bypass `
  -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\update_cvf_workspace_public_core.ps1" `
  -WorkspaceRoot "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace"
```

Invocation constraints, each a stop condition if violated:

- `-UpdateProjectManifests` — **prohibited** (SPEC R-21). It writes a short
  hash, injects `cvfPublicRemote` and `publicCoreFreshnessRequired`,
  reformats the whole file, and would skip this schema-2.0 manifest anyway.
- `-AllowPendingCoreBackup` — **prohibited** (SPEC R-22). The core is clean;
  a pending-change report contradicts INTAKE evidence and must be
  investigated, not overridden.
- `-OverlaySourcePath` — **prohibited** (SPEC R-23). The core must be exactly
  public `origin/main`, with no local overlay.

Manual substitutes for the script — `git reset --hard`, hand-deleting the
core, copying files into it — are prohibited.

### 4.2 Verify the new core is the right remote at the right commit

```bash
git -C "<corePath>" remote get-url origin      # must be the public CVF remote
git -C "<corePath>" rev-parse HEAD             # must be 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2
git -C "<corePath>" rev-parse origin/main      # must equal HEAD
git -C "<corePath>" status --porcelain         # must be empty
```

All four must hold before the manifest is touched (SPEC R-1..R-4). If HEAD is
anything other than `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` — including a
newer upstream commit that landed between INTAKE and BUILD — **stop** (§8).

### 4.3 Edit only `.cvf/manifest.json`

Single-line, in-place edit of the `cvfCoreCommit` value to the full new hash.
Preserve 2-space indentation, key order, line endings, trailing newline, and
UTF-8-without-BOM encoding. Do not regenerate or re-serialize the file.

### 4.4 If the script produces downstream change beyond the manifest — stop

After §4.1, and again after §4.3, run `git status --porcelain` in the
project. If **any** in-repository path other than `.cvf/manifest.json` has
changed relative to the §6.1 baseline — including a P2-B file, a
newly-created file, or `.cvf/local-binding.json` appearing as untracked —
**halt BUILD immediately, change nothing further, revert nothing, and report
a finding.** Do not repair it inside this tranche.

### 4.5 Do not touch the P2-B FREEZE files

No edit, stage, stash, checkout, restore, reset, clean, or commit against any
path in §2's list, at any point, for any reason.

## 5. Execution order (load-bearing, not stylistic)

1. Capture the pre-state baseline (§6.1).
2. Run the reconciler (§4.1).
3. Verify core remote/commit/cleanliness (§4.2).
4. Edit `.cvf/manifest.json` (§4.3).
5. Run the doctor entrypoint (§6.2 item 2).
6. Run the repository validation commands (§6.2 items 3-6).
7. Capture post-state; review the exact changed set (§6.2 items 7-9).

**Step 5 must not precede step 4.** With the core at `6ce1cf0` and the pin
still at `c1076dc`, `scripts/initialize_cvf_clone.ps1` fails closed with
`Hidden core cannot fast-forward safely to pinned commit`, because
`$head.StartsWith($pin)` is false and `merge-base --is-ancestor $head $pin`
also fails. That is the guard working correctly — but it means running the
doctor early aborts the run.

## 6. Required evidence

Every item below is required. Evidence is **real command output** — not
paraphrase, not expected output, not "should pass".

### 6.1 Pre-BUILD baseline

1. `git status --porcelain` (project) — the P2-B baseline.
2. `git -C "<corePath>" remote -v`, `rev-parse HEAD`, `rev-parse origin/main`,
   `status --porcelain`.
3. `git -C "<corePath>" diff --name-status c1076dc4be9ef9058b7c4e7b96def59c26aab148 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`
   plus `git log --oneline` over the same range — confirming the delta is
   still the four documentation files and one commit.
4. Workspace-root directory listing and the content or SHA-256 of
   `<workspaceRoot>/WORKSPACE_RULES.md`.

### 6.2 Post-BUILD

1. **Git remote/commit verification of the hidden core** — the four commands
   in §4.2, output pasted in full (AC-1..AC-4).
2. **Workspace doctor 24/24** —
   `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`,
   exiting 0, printing `FRESH_CLONE_CONTINUITY_PASS`, with the doctor table
   showing `RESULT: PASS (24/24 checks passed)` (AC-10, AC-11).
3. `python scripts/check_session_state.py` — PASS (AC-16).
4. `python scripts/generate_catalog.py --check` — PASS, nothing rewritten
   (AC-16).
5. `python scripts/testing/validate_repository.py` — PASS (AC-16).
6. **JSON parse of `.cvf/manifest.json`** —
   `python -c "import json;json.load(open('.cvf/manifest.json',encoding='utf-8'))"`
   succeeding (AC-9).
7. **Secret scan** over the changed set — no key, token, password, or
   `Authorization` header anywhere in the diff or in any captured output
   (AC-17).
8. **Exact changed-set review** — `git status --porcelain` and
   `git diff -- .cvf/manifest.json`, proving the changed set is the §6.1
   baseline plus `M .cvf/manifest.json` and that the manifest diff is exactly
   one line (AC-12, AC-8).
9. Post-run workspace-root listing and `WORKSPACE_RULES.md` comparison against
   §6.1 item 4, stating the out-of-repo side effects explicitly (AC-18).

## 7. Acceptance criteria

AC-1 through AC-19 as defined in `docs/specs/CVF_CORE_PIN_SPEC.md` §7. All
nineteen must hold. AC-19 (separate commit from the P2-B FREEZE batch) is
owned by COMMIT_STEWARD and verified at commit time, not at BUILD time.

## 8. Stop conditions

Stop, change nothing further, and report a finding — do not work around, do
not self-approve past, do not "fix while here" — if any of the following
occurs:

- **S-1** — Any in-repository change appears outside the authorized changed
  set of §1.1.
- **S-2** — The hidden core is not clean after the update, or its `origin` is
  not the public CVF remote.
- **S-3** — Upstream `origin/main` is anything other than
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` — including a newer commit
  landing between INTAKE and BUILD. The authorized target is that exact hash;
  a different one requires a new authorization.
- **S-4** — The workspace doctor does not reach 24/24, or any of the six
  checks named in SPEC R-14 is not `[PASS]`.
- **S-5** — Continuity conflict with the pending P2-B changes: any P2-B file
  differs from its baseline, or `check_session_state.py` reports mirror
  drift.
- **S-6** — Any step would require overwriting, stashing, resetting,
  restoring, or cleaning existing work.
- **S-7** — The reconciler reports pending changes in the hidden core, or
  fails mid-run and leaves a `-failed-<timestamp>` clone behind.
- **S-8** — Any of `check_session_state.py`,
  `generate_catalog.py --check`, or `validate_repository.py` fails, or
  changes state relative to baseline.
- **S-9** — `.cvf/manifest.json` fails to parse, gains or loses a key, or its
  diff is more than one line.
- **S-10** — Any command would read, print, log, or persist a secret.
- **S-11** — `git add -A` or `git add .` is about to be used, or a broad
  staging command would sweep in P2-B files.
- **S-12** — No independent REVIEWER is available at REVIEW time — report
  `BLOCKED_NO_INDEPENDENT_REVIEWER` and do not self-approve.

If the reconciler fails and restores the previous core (its own `catch`
block does this), the documented fallback is **not** to improvise: report the
failure, and treat ADR §3 alternative A1 (`git fetch` + `git merge --ff-only
origin/main` inside the core) as a candidate amendment requiring fresh
authorization — not as something BUILD may silently substitute.

## 9. Review requirement

REVIEWER must be independent from IMPLEMENTATION_WORKER (R2 rule,
`AGENTS.md`). REVIEWER must:

- Re-run every §6.2 command independently rather than trusting pasted output
  — this project's review history contains two separate cases where a pasted
  or self-reported closure claim was wrong.
- Confirm the in-repository changed set matches §1.1 exactly, with no file
  touched outside it.
- Confirm all 11 P2-B paths are byte-identical to their pre-BUILD state and
  were never staged, stashed, or reset.
- Confirm the manifest diff is a single line, the hash is the full 40
  characters, no key was added or removed, and formatting/encoding are
  unchanged.
- Confirm the core is a genuine clone of the public remote at the exact
  target commit, with a clean worktree and no downstream artifact inside it.
- Confirm no secret appears in the diff, evidence, or any captured output.
- Confirm the out-of-repo workspace-root side effects were captured and
  reported, not silently absorbed.

Findings are repaired under a REPAIR_WORKER role transition and re-reviewed.
REVIEW_PASS must not be recorded with any open finding.

## 10. Commit discipline

1. **Authorization-artifacts commit** — this WORK_ORDER, the ADR, and the
   SPEC, reviewed and committed by COMMIT_STEWARD **before any BUILD action**.
   No implementation file. This proves DESIGN/SPEC/WORK_ORDER preceded BUILD
   in the commit graph itself.
2. **No BUILD in the authoring turn.** IMPLEMENTATION_WORKER may begin only
   after being re-invoked with the authorization commit hash.
3. **BUILD is left uncommitted** for independent review.
4. **The core-pin commit is separate** from the P2-B FREEZE commit. Neither
   may absorb the other; project commit discipline forbids batching two
   tranches.
5. Staging is explicit single-path only (`git add .cvf/manifest.json`), owned
   by COMMIT_STEWARD. `git add -A` and `git add .` are prohibited.
6. No amend, rebase, or force-push. `cd36b27` is never rewritten.

## 11. Rollback

- In-repo: revert the one-line manifest change, or revert the core-pin commit
  once made.
- Hidden core: the previous core is preserved verbatim under
  `<workspaceRoot>/_cvf-core-backups/.Controlled-Vibe-Framework-CVF-<timestamp>/`;
  `c1076dc` also remains reachable in public history, so a checkout back is
  always possible.
- No project source, schema, migration, or data is involved, so no data
  rollback exists or is needed.

## 12. Approval

- Operator approval is recorded: synchronize the hidden core
  from `c1076dc` to `origin/main` `6ce1cf0`, update the corresponding pin in
  `.cvf/manifest.json`, re-run the workspace doctor, and keep the core-pin
  commit separate from the P2-B FREEZE commit.
- Independent REVIEWER re-verified the public remote, exact target commit,
  clean hidden-core baseline, changed-set boundary, acceptance criteria, stop
  conditions, role separation, and commit sequencing on 2026-07-23.
- Review disposition: **REVIEW_PASS** with no open finding after correcting
  the stale pre-review status labels in these three authorization artifacts.
- BUILD is authorized only after the authorization-artifacts commit exists
  and its hash has been supplied to IMPLEMENTATION_WORKER (§10 items 1-2).

---

# §13 — FREEZE Addendum (added 2026-07-23)

- Addendum id: `WO-CVF-CORE-PIN-2026-07-23-FREEZE-ADDENDUM`
- Risk: **R2** (governance continuity surfaces)
- Status: **REVIEW_PASS — AUTHORIZED_AFTER_ADDENDUM_COMMIT**
- Specification: `docs/specs/CVF_CORE_PIN_SPEC.md` §9
- Live provider evidence: **NOT REQUIRED and NOT PERMITTED**

§2 excluded continuity surfaces from BUILD because the P2-B FREEZE batch held
the same files uncommitted. That batch is now committed at `4e15ea4`, so the
exclusion's stated reason has expired. This addendum authorizes **only** the
deferred continuity work. It opens no feature tranche and re-opens nothing
already reviewed.

## 13.1 Verified preconditions

Captured read-only before authoring, each by command:

```
worktree                : git status --porcelain -> (empty)
HEAD                    : 4e15ea4260817a07e4db11543fc8ffa0aff7f4f1
commit order            : 76e7360 -> da9a122 -> 4e15ea4, each ancestor of HEAD
da9a122 changed set     : .cvf/manifest.json | 2 +-   (1 file, 1 insertion, 1 deletion)
4e15ea4 changed set     : 11 files, none of them .cvf/manifest.json
core remote             : https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git
core HEAD               : 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2
core origin/main        : 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2
manifest cvfCoreCommit  : 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2
core worktree           : clean
workspace doctor        : RESULT: PASS (24/24 checks passed)
```

`da9a122` and `4e15ea4` share no path, which is the direct evidence that the
core-pin and P2-B FREEZE tranches were never batched (SPEC AC-19).

## 13.2 Authorized changed set — exactly six paths

| # | Path | Action |
|---|---|---|
| F-1 | `SESSION/SESSION_MEMORY.md` | edit |
| F-2 | `SESSION/ACTIVE_SESSION_STATE.json` | edit |
| F-3 | `CVF_SESSION/ACTIVE_SESSION_STATE.json` | edit (mirror) |
| F-4 | `IMPLEMENTATION_STATUS.json` | edit |
| F-5 | `docs/INDEX.md` | edit |
| F-6 | `SESSION/handoffs/AGENT_HANDOFF_2026-07-23_CVF_CORE_PIN_FREEZE.md` | create |

Nothing else may be modified, created, or deleted.

## 13.3 Explicit exclusions

- **`.cvf/manifest.json`** — already committed at `da9a122`. Touching it again
  under this addendum is a stop condition, not a correction.
- Application source, tests, migrations, schema, data.
- `docs/catalog/MODULE_REGISTRY.json` and `docs/catalog/MODULE_CATALOG.md` —
  no module status changed, so the catalog must not be regenerated.
- `docs/implementation/EXECUTION_ROADMAP.md` — the roadmap must not be
  edited, reordered, or re-checked. The drift in §13.5 is recorded elsewhere,
  not fixed here.
- `docs/cvf/CVF_CONTROL_MAPPING.md` — no control changed status.
- All provider files (`packages/ai-providers/**`) and any `ALIBABA_API_KEY`
  access.
- Superseded handoffs under `SESSION/handoffs/` — retained, never deleted.
- Commits `cd36b27`, `76e7360`, `da9a122`, `4e15ea4` — no rewrite, squash,
  amend, rebase, or force-push.
- Any file not listed in §13.2. If the work discovers a genuine need to touch
  something else, STOP (§13.7) and return for an amendment.

## 13.4 Required content

The implementing role MUST satisfy SPEC §9.3 in full. Restated as obligations:

1. **Disposition** — core-pin tranche recorded as `FREEZE` /
   `CLOSED_BOUNDED` (SPEC R-33).
2. **Facts recorded exactly** (SPEC R-34..R-38):
   - authorization commit `76e7360`;
   - BUILD / REVIEW_PASS commit `da9a122`;
   - core and manifest pin `6ce1cf0`;
   - workspace doctor `24/24`;
   - P2-B FREEZE as the **separate** commit `4e15ea4`, never batched with the
     core-pin commit.
3. **Active handoff** — canonical (F-2) and mirror (F-3) both repointed to
   F-6; F-6 created and complete; `required_reads` updated; the superseded
   P2-B handoff retained (SPEC R-39..R-41).
4. **Mirror discipline** — F-3 stays a pointer mirror with
   `canonicalSource` unchanged; F-2 and F-3 agree so
   `check_session_state.py` passes (SPEC R-42).
5. **Status file** — F-4 records the closure but changes **no** roadmap
   feature status (SPEC R-43, R-44).
6. **Index** — F-5 stops calling `docs/specs/` and `docs/work_orders/`
   "stub — not yet populated", and describes their real contents without
   overstating them (SPEC R-45).
7. **No AI-governance claim, no provider call** (SPEC R-49, R-50).
8. **Bounded claims preserved** — P2-B's boundary intact, High Finding #4
   still OPEN, `cd36b27` still the unauthorized build candidate
   (SPEC R-51..R-53).

## 13.5 Continuity drift — record, do not resolve

Verified disagreement, cited from the real files:

| Source | Says |
|---|---|
| `CONTRIBUTING.md:21` | ordering rule — take the next `[ ]` roadmap item in order (`lấy item [ ] kế tiếp theo thứ tự`) |
| `docs/implementation/EXECUTION_ROADMAP.md:207` | the first `[ ]` item is **P1-B** (extract domain models into `operations-domain`) |
| `SESSION/ACTIVE_SESSION_STATE.json` `next_allowed_move` | offers only P2-A (remaining incidents/handovers), `known-principals.yaml` ↔ users (High Finding #4), and P2-C — **P1-B absent** |

Obligations:

- Record this drift explicitly in F-1, F-2, and F-6, citing both sides and
  naming P1-B (SPEC R-46).
- Record the next allowed move as **INTAKE for an operator-confirmed lane**
  (SPEC R-47).
- **Do not** choose a lane, reprioritize, edit the roadmap, or declare either
  side authoritative. Selecting a feature lane on the operator's behalf is a
  stop condition (§13.7 S-16), not a judgement call (SPEC R-48).

## 13.6 Required checks

Run in the project root; capture real output:

```
python -m pytest -q
python scripts/testing/validate_repository.py
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```

Plus:

- JSON parse of `SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`, `IMPLEMENTATION_STATUS.json`.
- Exact changed-set review — `git status --porcelain` shows the six §13.2
  paths and nothing else.
- Secret scan over the full changed set — clean.

The doctor must return `24/24` and `FRESH_CLONE_CONTINUITY_PASS`.
`generate_catalog.py --check` must pass **without regenerating anything** —
the catalog is outside the changed set, so drift there means the boundary was
breached.

## 13.7 Stop conditions

Stop, change nothing further, and report a finding if:

- **S-13** — The worktree is not clean at the start.
- **S-14** — Core HEAD, `origin/main`, and manifest `cvfCoreCommit` are not
  all `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`, or the core worktree is
  dirty.
- **S-15** — Any change is needed outside the six §13.2 paths — including any
  touch of `.cvf/manifest.json`, the catalog, or the roadmap.
- **S-16** — The work would require choosing, ranking, or reprioritizing a
  feature lane on the operator's behalf, or resolving the §13.5 drift.
- **S-17** — Any of `pytest`, `validate_repository.py`,
  `check_session_state.py`, `generate_catalog.py --check`, the JSON parse, or
  the workspace doctor fails.
- **S-18** — Any secret would be read, printed, logged, or persisted, or any
  provider call would be made.
- **S-19** — `git add -A` / `git add .` is about to be used, or a broad
  staging command would sweep in unauthorized paths.
- **S-20** — Any recorded claim would exceed the boundary: asserting the
  core-pin tranche proves AI governance behavior, widening P2-B's claim,
  marking High Finding #4 fixed, or describing `cd36b27` as authorized.
- **S-21** — No independent REVIEWER is available — report
  `BLOCKED_NO_INDEPENDENT_REVIEWER`; do not self-approve.

## 13.8 Acceptance criteria

AC-20 through AC-35 as defined in `docs/specs/CVF_CORE_PIN_SPEC.md` §9.6. All
sixteen must hold. AC-35 (separate FREEZE commit, no history rewrite) is
owned by COMMIT_STEWARD and verified at commit time.

## 13.9 Roles

| Role | Holder | Responsibility |
|---|---|---|
| SPEC_AUTHOR / WORK_ORDER_AUTHOR | authoring context | Authors this addendum only. Does not perform the continuity work and does not self-approve. |
| IMPLEMENTATION_WORKER / SESSION_SYNC_STEWARD | assigned only after the addendum authorization commit exists and its hash is supplied | Performs §13.2 exactly; produces §13.6 evidence; leaves the result uncommitted. |
| REVIEWER | **independent context** (R2 requirement) | Re-runs — not re-reads — every §13.6 check; confirms the changed set and every claim boundary. |
| COMMIT_STEWARD | **independent context** | Verifies the changed set against §13.2 and owns the commit action. |

Roles are named by responsibility, never by provider.

## 13.10 Commit discipline

1. This addendum is reviewed and committed as its own authorization commit,
   **before** any continuity change. No continuity file in that commit.
2. The continuity work begins only after that hash is supplied.
3. The continuity changes are left **uncommitted** for independent review.
4. The FREEZE commit is **separate** from `76e7360`, `da9a122`, and
   `4e15ea4`; no amend, rebase, or force-push; `cd36b27` never rewritten.
5. Staging is explicit per-path only.

## 13.11 Rollback

Every §13.2 path is a documentation or continuity file. Rollback is reverting
the FREEZE commit (or discarding the uncommitted changes before it). No
source, schema, migration, or data is involved, and the core pin at `da9a122`
is unaffected either way.

## 13.12 Approval

- Operator authorized this addendum: close the core-pin tranche's
  deferred continuity/FREEZE work, now that the P2-B FREEZE batch is
  committed at `4e15ea4`, without opening a new feature tranche.
- Independent REVIEWER verified the six-path boundary, commit ordering,
  core/manifest/public-remote equality, drift citation, acceptance criteria,
  stop conditions, claim boundaries, and role separation on 2026-07-23.
- Review disposition: **REVIEW_PASS**, with no open finding after updating
  the pre-review status labels in these two addendum artifacts.
- The continuity work is authorized only after the addendum authorization
  commit exists and its hash has been supplied (§13.10 items 1-2).
