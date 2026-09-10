# Session Memory

Provider-neutral companion to `ACTIVE_SESSION_STATE.json`. Last updated:
2026-09-10. Read only the active handoff and current authority paths by default;
use the archive for a targeted historical lookup.

## Current checkpoint

The first-party CVF provenance-inheritance recovery remains `FREEZE /
CLOSED_BOUNDED`. P4-E Amendment 1 repair is independently technically accepted:
all product findings, including successor `P4E-AM1-REV-F1`, are closed without
waiver; focused tests passed 219/2 and disposable PostgreSQL passed 12 with
verified cleanup. Catalog paths 93-94 are canonical. Material commit
`131a38b0c817903df2148107078c25dbe50d5f38` records the accepted packet. A machine-reproduced
catalog-to-Project-Knowledge phase-order cycle required Amendment 2; independent
authorization review passed with findings/waivers `NONE/NONE`; control commits
are `c82d9e0` and `9809852`. Disposition is `FREEZE / CLOSED_BOUNDED`, subject
to the post-material gates/review and exact evidence/continuity commits recorded
in the active handoff. The project pins portable public Core
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4` and requires the operator-local
rule pack materialized from private provenance
`fe62894f861c34a25a16c6267f557bf771ea9e2c`. Both repositories remain read-only
authority for application work; their content was not copied into this repo.

The recovery refreshed the manifest, policy, AGENTS carrier, bootstrap record,
Project Knowledge pins, invariant fixtures and continuity. A repository-wide
LF policy removed platform-dependent digest drift. Product behavior and module
statuses did not change.

All blocking local checks pass. The doctor returns `PASS WITH NOTE` (24 pass,
one bounded legacy-catalog note). The note is deliberate: catalog kit 1.1 and
this mature project's 26-module registry claim the same canonical paths with
different schemas. Automatic installation would replace implementation truth;
that schema migration is separately parked.

## Product roadmap

Phases 0-3 are closed within their recorded boundaries. Phase 4 is 8/8 and
`CLOSED_BOUNDED`; P4-E is parked at its deterministic local contract boundary.
The next governed work is outside this project: the operator returns to CVF
Core for a separate ADIF-0057 machine-enforcement tranche. Phase 5 and
external-repository absorption remain parked.

## Guardrails

- Treat `SESSION/ACTIVE_SESSION_STATE.json` as canonical;
  `CVF_SESSION/ACTIVE_SESSION_STATE.json` is only its compatibility mirror.
- Do not mutate public Core or private provenance from project work.
- Do not turn historical bounded evidence into production-readiness claims.
- Do not reopen P4-E product repair or make an Alibaba/provider call, pull a
  Docker image, install a dependency, use a shared database, deploy, push, or
  write outside Amendment 2's exact role-owned paths.
- Do not start Phase 5, catalog schema migration, XR1 repair, or external-
  repository absorption without fresh authority.
- Run `python scripts/check_session_state.py` after changing continuity.

## History

The 2026-08-31 governance-control-loss checkpoint, Core-refresh attempts,
P4-A through P4-D evidence, earlier product tranches, and their claim boundaries
remain immutable in Git and under `SESSION/handoffs/`. Full compacted history:
[`SESSION/archive/SESSION_MEMORY_PRE_T3_2026-08-11.md`](archive/SESSION_MEMORY_PRE_T3_2026-08-11.md).
