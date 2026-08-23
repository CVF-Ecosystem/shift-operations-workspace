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
- Active learning INTAKE:
  [`INTAKE_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`](decisions/INTAKE_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md)
- Independent learning INTAKE review (`PASS`, `NONE/NONE`):
  [`CROSS_AGENT_INVARIANT_LEARNING_INTAKE_REVIEW_2026-08-22.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_INTAKE_REVIEW_2026-08-22.md)
- Accepted learning DESIGN:
  [`DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`](decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md)
- Independent learning DESIGN review (`PASS`, `NONE/NONE`):
  [`CROSS_AGENT_INVARIANT_LEARNING_DESIGN_REVIEW_2026-08-22.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_DESIGN_REVIEW_2026-08-22.md)
- Accepted learning SPEC v1.0:
  [`CROSS_AGENT_INVARIANT_LEARNING_SPEC.md`](specs/CROSS_AGENT_INVARIANT_LEARNING_SPEC.md)
- Independent learning SPEC review (`PASS`, `NONE/NONE`, `OBS-1..3`):
  [`CROSS_AGENT_INVARIANT_LEARNING_SPEC_REVIEW_2026-08-23.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_SPEC_REVIEW_2026-08-23.md)
- Exact-27 learning Work Order (`AUTHORIZATION_REVIEW_PASS`):
  [`CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER.md`](work_orders/CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER.md)
- Invariant-family standard, schema, registry and shared template:
  [`docs/cvf/INVARIANT_FAMILY_STANDARD.md`](cvf/INVARIANT_FAMILY_STANDARD.md),
  [`docs/cvf/invariants/registry.json`](cvf/invariants/registry.json),
  [`docs/cvf/invariants/invariant-family.schema.json`](cvf/invariants/invariant-family.schema.json),
  [`docs/templates/INVARIANT_FAMILY_PROOF.md`](templates/INVARIANT_FAMILY_PROOF.md)
- Learning worker lineage and independent final review (`REVIEW_PASS_ROUND_10`,
  `NONE/NONE`, `FREEZE / CLOSED_BOUNDED`):
  [`CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md),
  [`CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`](decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md)

## Governed Artifact Families

- Decisions **and review evidence** (this project keeps both together, not in
  a separate `docs/reviews/`): [`docs/decisions/`](decisions/)
- Business/delivery roadmap (five-phase model, distinct from the AGENTS.md
  seven-step control chain): [`docs/implementation/EXECUTION_ROADMAP.md`](implementation/EXECUTION_ROADMAP.md)
  and [`docs/implementation/IMPLEMENTATION_PHASES.md`](implementation/IMPLEMENTATION_PHASES.md)
- Specifications — populated with discrete per-tranche artifacts
  (`P2B_AUTHENTICATION_REPAIR_SPEC.md`,
  `ALIBABA_LIVE_PROVIDER_CONFIGURATION_SPEC.md`, `CVF_CORE_PIN_SPEC.md`,
  `P4A3_APPLICATION_MEMORY_SPEC.md`, `P4B_AI_PROVIDERS_SPEC.md`):
  [`docs/specs/`](specs/). These are **per-tranche** governance specifications
  — testable requirements, acceptance criteria and claim boundaries for one
  bounded unit of work — not a complete specification of the system. Tranches
  predating this family still carry their spec content inline in handoffs and
  the roadmap.
- Work orders — populated alongside the specs above
  (`P2B_AUTHENTICATION_REPAIR_WORK_ORDER.md`,
  `ALIBABA_LIVE_PROVIDER_CONFIGURATION_WORK_ORDER.md`,
  `CVF_CORE_PIN_WORK_ORDER.md`, `P4A3_APPLICATION_MEMORY_WORK_ORDER.md`,
  `P4B_AI_PROVIDERS_WORK_ORDER.md`):
  [`docs/work_orders/`](work_orders/). Each
  authorizes one bounded changed set with its roles, required evidence, stop
  conditions and commit ownership; the same per-tranche scope caveat applies.
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
