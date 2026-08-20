# Specification — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-20`
- Phase: `SPEC`
- Risk: `R2`
- Status: `AUTHORIZATION_REVIEW_PASS`
- Author role transition: `SPEC_AUTHOR` after DESIGN was authored; BUILD
  authority remains absent until independent authorization `PASS`

## Requirements

- `R1`: Core remote equals the public CVF URL; Core worktree is clean before
  and after reconciliation.
- `R2`: target Core HEAD and local `origin/main` equal full hash
  `7d9f360a3df11ac998972728000785799399c02b` after reconciliation.
- `R3`: `.cvf/manifest.json.cvfCoreCommit` and the `AGENTS.md` header equal R2;
  no unrelated content changes in either file.
- `R4`: `.cvf/local-binding.json.resolvedCoreCommit` is regenerated and equals
  R2; local binding, Core HEAD, Core origin/main, and manifest pin are equal.
- `R5`: all named workspace-root targets have existence/SHA-256 pre/post
  evidence in `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-20.json`
  and restorable preimages; all backup/failed-state directories are preserved.
- `R6`: active profile remains `operator-local`; public profile sync does not
  run.
- `R7`: workspace doctor exits zero with no failure; the bounded legacy catalog
  warning may remain.
- `R8`: these exact commands pass from the project root:
  `python scripts/check_session_state.py`;
  `python scripts/check_project_knowledge.py`;
  `python scripts/check_file_size.py`;
  `python scripts/testing/validate_repository.py`;
  `git diff --check`; and a Python `json.loads` pass over `.cvf/manifest.json`,
  `.cvf/policy.json`, `IMPLEMENTATION_STATUS.json`, `knowledge/manifest.json`,
  both active-state JSON files, the bootstrap JSON and the root-effects JSON.
- `R9`: no product/runtime/catalog/roadmap/provider/database/deployment path
  changes and no provider secret/API call occurs.
- `R10`: independent REVIEW recomputes the target, containment, hashes, backup
  evidence and gates before any commit.
- `R11`: root-effects JSON contains `schemaVersion`, tranche/target fields,
  timestamps, `before` and `after` arrays of `{path, existed, sha256}`, Core and
  root-preimage backup paths, allowed network operations/endpoints, observed
  tips, commands with exit codes, rollback status, and downstream changed-set
  comparison.
- `R12`: at worker handoff, `git status --short` matches the exact 17-path
  worker-stage set defined by WORK_ORDER (the reviewer-owned completion review
  does not exist yet); `git diff --cached --name-only` is empty; and
  `.cvf/local-binding.json` is ignored, absent from status/commit, and changed
  from `27137db4...` to the frozen full target only after pinning. At
  pre-commit closure, the independent reviewer recomputes the final exact
  18-path set by adding only its completion-review artifact.

## Claim boundary

PASS proves only local public-Core freshness, portable pin/binding equality,
workspace-root refresh containment, and synchronized downstream continuity.
It is not live evidence that CVF controls AI/agent behavior and does not open
P4-A or P4-A2.
