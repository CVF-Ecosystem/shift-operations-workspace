# Session Memory

Provider-neutral companion to `ACTIVE_SESSION_STATE.json`. Last updated: 2026-09-26.
Read the active handoff and current authority paths first; use history only for a targeted missing fact.

## Current checkpoint

CVF catalog kit v1.1 migration is implemented and locally verified on a clean worktree based on project `origin/main` commit `84cd7e4458ecbdff771e8f9929a5a741eed0a48a`. Independent completion review PASS; commit and GitHub push pending. Current handoff: `SESSION/handoffs/CVF_CATALOG_KIT_MIGRATION_2026-09-26.md`. Decision record: `docs/decisions/CVF_CATALOG_KIT_MIGRATION_2026-09-26.md`.

The kit has artifact and module registries, schemas, a PowerShell manager, a Python projection adapter, and a Windows CI check. Detailed project catalog data remains in `docs/catalog/MODULE_REGISTRY_DETAIL.json` and the detailed catalog and project index. All 26 module records were preserved. Public Core pin: `19386f64e6bc36d1dcdbadca6ff97253feefb1bf`; private provenance pin: `4567d750087d47f369939a0e9891ca6fcb596034`.

Local validation passed: full pytest 3121 passed, 146 skipped; catalog generation and kit checks, project knowledge, inheritance, workspace doctor, file size, and repository validation. This is local evidence until commit and remote push finish.

## Product roadmap and next move

Phases 0-3 are closed within recorded boundaries. Phase 4 is 8/8 and `CLOSED_BOUNDED`. Commit the independently accepted catalog migration and fast-forward push to project `origin/main`. External-repository absorption still needs the exact source repository set and intended outcome before a bounded corpus receipt or scan. Phase 5 and XR1 debt remain parked.

## Guardrails

- `SESSION/ACTIVE_SESSION_STATE.json` is canonical; the `CVF_SESSION/` state is its compatibility mirror.
- Do not infer runtime, provider, deployment, or production readiness from this static catalog migration.
- Run `python scripts/check_cvf_core_machine_inheritance.py --enforce` before review or commit and `python scripts/check_session_state.py` after continuity changes.
- Do not start parked work without fresh operator selection.

## History

Prior active handoff: `SESSION/handoffs/EXTERNAL_REPOSITORY_ABSORPTION_INTAKE_2026-09-10.md`.
Historical memory: `SESSION/archive/SESSION_MEMORY_PRE_T3_2026-08-11.md`.
