# ADR 2026-07-23 — Synchronize the hidden CVF core and re-pin `.cvf/manifest.json`

- ADR id: `ADR-2026-07-23-CVF-CORE-PIN`
- Tranche: `CVF-CORE-PIN-2026-07-23`
- Control-chain phase at authoring time: `DESIGN`
- Risk: **R2** (governance-core pin — the manifest pin is the enforcement
  anchor the workspace doctor and the First-Request Protocol both resolve
  from)
- Status: **ACCEPTED** — independent authorization-artifact REVIEW passed on
  2026-07-23. BUILD remains gated on the separate authorization commit hash.
  No BUILD has been performed.
- Specification: `docs/specs/CVF_CORE_PIN_SPEC.md`
- Work order: `docs/work_orders/CVF_CORE_PIN_WORK_ORDER.md`

## 1. Context

### 1.1 Observed state (INTAKE evidence, captured read-only 2026-07-23)

The CVF workspace doctor
(`.Controlled-Vibe-Framework-CVF/scripts/check_cvf_workspace_agent_enforcement.ps1`,
run with `-ProjectPath` pointed at this project) currently returns:

```
  CVF public core matches origin/main                [FAIL]
         -> BEHIND_PUBLIC_REMOTE. Local: c1076dc4be9ef9058b7c4e7b96def59c26aab148 /
            origin/main: 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2.
            Run scripts/update_cvf_workspace_public_core.ps1.

  RESULT: FAIL (23/24 checks passed, 1 failed)
```

Every other check passes. Supporting facts, each verified by command, not
assumed:

| Fact | Verified value |
|---|---|
| Hidden core remote | `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git` |
| Hidden core local HEAD | `c1076dc4be9ef9058b7c4e7b96def59c26aab148` |
| Hidden core `git status --porcelain` | empty (clean) |
| Public `origin/main` | `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` |
| `.cvf/manifest.json` `cvfCoreCommit` | `c1076dc4be9ef9058b7c4e7b96def59c26aab148` |
| Pin reachability | `c1076dc` is an ancestor of `6ce1cf0` — fast-forward only, no divergence |

The upstream delta `c1076dc..6ce1cf0` is exactly one commit:

```
6ce1cf0 docs: reconcile seven-step loop and provider claims
```

touching exactly four files, all CVF core documentation:

```
M  ARCHITECTURE.md
M  PROVIDERS.md
M  README.md
M  docs/reference/CVF_PROVIDER_LANE_READINESS_MATRIX.md
```

No CVF core script, governance toolkit template, workspace kit file, or
downstream-facing contract changed in this delta.

### 1.2 Why this matters

`AGENTS.md` (First-Request Protocol, step 2) requires that the workspace
doctor confirm the hidden core matches `origin/main` **before material
work**, and instructs the agent to stop and reconcile with
`update_cvf_workspace_public_core.ps1` when it reports stale history. The
project is currently in exactly that stop state. Any subsequent governed
tranche — P2-A incidents/handovers, the `known-principals.yaml` ↔ users
reconciliation, or P2-C frontend — would begin from a failing doctor, which
is not an acceptable starting posture for R2 work.

### 1.3 Concurrent state that constrains this tranche

The project worktree carries an uncommitted P2-B FREEZE batch owned by a
separate agent context:

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

This tranche must coexist with that batch without touching it. Project
commit discipline (`CONTRIBUTING.md`, `ACTIVE_SESSION_STATE.json`
`commit_discipline`) forbids batching two tranches into one commit, so the
core-pin commit must be separate from the P2-B FREEZE commit.

## 2. Decision

**Reconcile the hidden sibling CVF core to public `origin/main`
`6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` using the framework's own
reconciliation script, then update `.cvf/manifest.json`'s `cvfCoreCommit`
to that full 40-character commit hash — and change nothing else in this
repository.**

Decomposed:

- **D1** — Update the hidden core with
  `.Controlled-Vibe-Framework-CVF/scripts/update_cvf_workspace_public_core.ps1`,
  the standard reconciler named by both `WORKSPACE_RULES.md` and the doctor's
  own failure message.
- **D2** — Verify after the update that the core's `origin` is the public CVF
  remote and its HEAD is exactly `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`,
  with a clean worktree.
- **D3** — Edit exactly one line of `.cvf/manifest.json`: `cvfCoreCommit`,
  set to the full hash. No other key, no reformatting, no field addition.
- **D4** — Re-run the workspace doctor and require **24/24**.
- **D5** — Leave the BUILD uncommitted for independent review, and commit it
  separately from the P2-B FREEZE batch.

### 2.1 Full hash, not short hash

`cvfCoreCommit` is stored as the full 40-character hash today, and both the
doctor (`$actualCommit.StartsWith($manifestObj.cvfCoreCommit)`) and
`scripts/initialize_cvf_clone.ps1` (`$head.StartsWith($pin)`) accept a
prefix. A short hash would therefore still pass, but it weakens the pin from
an exact identity to a prefix match. The existing value is full-length; this
tranche preserves that stronger form.

### 2.2 `-UpdateProjectManifests` must NOT be used

The reconciler exposes a `-UpdateProjectManifests` switch that would appear
to automate D3. It is rejected for three independently sufficient reasons,
each read directly from the script source:

1. It writes `git rev-parse --short HEAD` — a **short** hash — contradicting
   §2.1.
2. It injects two additional keys, `cvfPublicRemote` and
   `publicCoreFreshnessRequired`, and re-serializes the whole file through
   `ConvertTo-Json`. That is an unreviewed schema change plus a whole-file
   reformat, far beyond the authorized one-line edit.
3. It gates on `$manifest.cvfCorePath -ne $corePath`. This project's manifest
   is portable schema 2.0 and has **no** `cvfCorePath` key (it has
   `cvfCoreRelativePath`), so the comparison is `$null -ne <path>` and the
   manifest would be **skipped with a warning** anyway — the flag cannot do
   the job even if it were desirable.

D3 is therefore a deliberate, minimal, hand-authored edit.

### 2.3 Ordering is load-bearing

The manifest edit must happen **after** the core update and **before** the
doctor run. `scripts/initialize_cvf_clone.ps1` fails closed if the core HEAD
is ahead of the pin: with HEAD at `6ce1cf0` and the pin still at `c1076dc`,
`$head.StartsWith($pin)` is false, and the fallback
`merge-base --is-ancestor $head $pin` also fails, producing
`Hidden core cannot fast-forward safely to pinned commit`. Running the
project's doctor entrypoint before the manifest edit would abort. The correct
sequence is: **update core → verify core → edit manifest → run doctor**.

## 3. Alternatives considered

### A1 — `git fetch && git merge --ff-only origin/main` inside the hidden core (rejected)

Given that the delta is one documentation commit and a clean fast-forward,
a plain fast-forward would reach the identical tree with a far smaller blast
radius: no re-clone, no backup directory, no workspace-root file rewrites.

**Rejected** because the operator authorized the standard script by name, and
because `update_cvf_workspace_public_core.ps1` additionally re-verifies the
public workspace kit (`$requiredPublicCoreFiles`) and refreshes the root
wrappers — checks a bare fast-forward silently skips. Using the framework's
own reconciler keeps this tranche inside the framework's supported path
rather than inventing a project-local shortcut for a governance-core
operation. A1 is retained here only as the documented fallback if the
reconciler fails mid-run (see WORK_ORDER §8).

### A2 — Update the pin only, without moving the core (rejected)

Editing `cvfCoreCommit` to `6ce1cf0` while the core stays at `c1076dc` would
turn doctor Check 15 (`CVF core commit matches manifest`) into a failure and
leave Check 13 failing as well. It would also make the manifest assert a
state the filesystem does not have — precisely the kind of documentation
overclaim this project's review history repeatedly penalizes.

### A3 — Do nothing and proceed to the next roadmap tranche (rejected)

Leaves the doctor at 23/24 and violates the First-Request Protocol's
pre-work condition. Every subsequent tranche would inherit a failing gate and
an ambiguous starting posture.

### A4 — Fold the core-pin change into the P2-B FREEZE commit (rejected)

Directly violates this project's commit discipline (`no batching of two
tranches`) and would entangle a governance-core pin with an unrelated
authentication closure, making both harder to review or revert.

## 4. Consequences

### 4.1 Accepted

- **In-repository changed set is exactly one file**: `.cvf/manifest.json`,
  one line. This is the entire downstream footprint.
- **`.cvf/local-binding.json` will be rewritten** by the doctor entrypoint
  (`resolvedCoreCommit` moves to `6ce1cf0`). It is git-ignored
  (`.gitignore:16`), so it does not appear in the changed set. This is
  expected and must not be treated as scope creep.
- **Workspace-root side effects, outside this git repository.** The
  reconciler moves the old core into `<workspaceRoot>/_cvf-core-backups/`,
  re-clones, regenerates `WORKSPACE_RULES.md` from a template, and runs
  `install_cvf_workspace_root_wrappers.ps1`. The workspace root is not a git
  repository, so none of this enters any commit — but it is real filesystem
  change and must be captured before/after and reviewed (WORK_ORDER §5).
  `WORKSPACE_RULES.md` in particular will be regenerated with a recomputed
  sibling-project list, which currently omits `shift-operations-workspace`
  and will gain it.
- **Public profile sync will not run.** The reconciler only invokes
  `sync_cvf_workspace_public_profile.ps1` when
  `CVF_RULE_PACKS/ACTIVE_RULE_PACK.json`'s `activeProfile` is `public-free`
  or `paid-user-safe`; the workspace is on `operator-local`. Verified by
  reading both the script and the rule-pack file.
- **The hidden core stays a read-only reference.** No downstream artifact is
  copied into it, consistent with the Workspace Isolation Rule in `AGENTS.md`.

### 4.2 Explicitly not claimed

Moving the pin does **not** re-validate, re-approve, or extend any prior
governance claim. Specifically it does not:

- reopen, alter, or re-close the `P2B-AUTHENTICATION-REPAIR` FREEZE;
- add authority to the live Alibaba identity evidence receipt;
- close High Finding #4 (`known-principals.yaml` ↔ users reconciliation);
- constitute live governance evidence of AI/agent behavior. This tranche
  makes **no** claim about AI governance behavior, so `AGENTS.md`'s Mandatory
  Governance Proof rule is not triggered and no provider API call is required
  or permitted. Doctor PASS proves local enforcement artifacts and public-core
  freshness only — `WORKSPACE_RULES.md` states this boundary itself.

### 4.3 Rollback

Fully reversible and non-destructive:

- The in-repo change is one line in one uncommitted file; reverting is
  restoring the previous hash (or reverting the core-pin commit once made).
- The previous hidden core is preserved verbatim under
  `<workspaceRoot>/_cvf-core-backups/.Controlled-Vibe-Framework-CVF-<timestamp>/`.
- The core move is a fast-forward within public history; `c1076dc` remains
  reachable and checkout-able.
- No project source, schema, migration, or data is touched.

## 5. Compliance notes

- **Phase discipline** — this tranche runs a fresh control chain from INTAKE.
  DESIGN (this ADR), SPEC, and WORK_ORDER are authored and committed as
  authorization artifacts **before** any BUILD action, satisfying the same
  ordering requirement that the `P2B-AUTHENTICATION-REPAIR` tranche was
  created to restore.
- **Role separation** — R2 requires REVIEWER independent from
  IMPLEMENTATION_WORKER (`AGENTS.md` role contract). The WORK_ORDER assigns
  REVIEWER and COMMIT_STEWARD to a context independent from the authoring and
  implementing context.
- **Provider neutrality** — all roles in this ADR and its companion artifacts
  are named by responsibility, never by provider.
- **Secrets** — this tranche performs no provider call and must not read,
  print, log, or persist any API key. Git operations use the public CVF
  remote over HTTPS with no credential.
- **`cd36b27`** — untouched. No rewrite, squash, amend, rebase, or
  force-push by this tranche.
