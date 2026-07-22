# Project Documentation Index

## Start Here

- Session front door (canonical): [`SESSION/SESSION_MEMORY.md`](../SESSION/SESSION_MEMORY.md)
- Active state (canonical, machine): [`SESSION/ACTIVE_SESSION_STATE.json`](../SESSION/ACTIVE_SESSION_STATE.json)
- Active handoff: file under [`SESSION/handoffs/`](../SESSION/handoffs/) named by
  `active_handoff` in the active state above
- Implementation truth: [`IMPLEMENTATION_STATUS.json`](../IMPLEMENTATION_STATUS.json)
- Machine module registry: [`docs/catalog/MODULE_REGISTRY.json`](catalog/MODULE_REGISTRY.json)
- Human module catalog: [`docs/catalog/MODULE_CATALOG.md`](catalog/MODULE_CATALOG.md)
- Contribution / workflow front door: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- Agent operating contract: [`AGENTS.md`](../AGENTS.md)
- Docs entry point (general orientation): [`docs/README.md`](README.md)

## Governed Artifact Families

- Decisions **and review evidence** (this project keeps both together, not in
  a separate `docs/reviews/`): [`docs/decisions/`](decisions/)
- Business/delivery roadmap (five-phase model, distinct from the AGENTS.md
  seven-step control chain): [`docs/implementation/EXECUTION_ROADMAP.md`](implementation/EXECUTION_ROADMAP.md)
  and [`docs/implementation/IMPLEMENTATION_PHASES.md`](implementation/IMPLEMENTATION_PHASES.md)
- Specifications (new family, stub — not yet populated as a discrete
  per-tranche artifact; spec content currently lives inline in handoffs and
  the roadmap): [`docs/specs/`](specs/)
- Work orders (new family, stub — same status as specs above): [`docs/work_orders/`](work_orders/)
- CVF control mapping: [`docs/cvf/CVF_CONTROL_MAPPING.md`](cvf/CVF_CONTROL_MAPPING.md)
- Architecture / boundary rules: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](architecture/FRONTEND_BACKEND_BOUNDARY.md)
- File size guard: [`docs/reference/FILE_SIZE_GUARD.md`](reference/FILE_SIZE_GUARD.md)

Plans describe intended work. `IMPLEMENTATION_STATUS.json`, source, tests, and
review evidence (currently under `docs/decisions/`) determine what is actually
implemented.

## Note on continuity naming

This project predates the `CVF_SESSION/` naming convention introduced by the
CVF Project Bootstrap Continuity Contract. Its canonical continuity system
lives under `SESSION/`. `CVF_SESSION_MEMORY.md` at the project root is a
pointer file only, and `CVF_SESSION/ACTIVE_SESSION_STATE.json` **does exist**
as a compatibility mirror required by
`scripts/check_cvf_workspace_agent_enforcement.ps1` (which checks that exact
literal path) — see `CVF_SESSION_MEMORY.md` or `AGENTS.md` for the full
explanation. Do not treat `CVF_SESSION/ACTIVE_SESSION_STATE.json` as a second
canonical active-state source; only `SESSION/ACTIVE_SESSION_STATE.json` is
canonical, and `scripts/check_session_state.py` verifies the two stay in
agreement.
