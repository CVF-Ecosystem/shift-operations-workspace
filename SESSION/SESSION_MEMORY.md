# Session Memory

Provider-neutral companion to `ACTIVE_SESSION_STATE.json`. Last updated:
2026-09-10. Read only the active handoff and current authority paths by default;
use the archive for a targeted historical lookup.

## Current checkpoint

The first-party CVF provenance-inheritance recovery remains `FREEZE /
CLOSED_BOUNDED`. P4-E implementation and three review rounds now exist as
uncommitted evidence, but completion remains rejected by round-3 findings
`P4E-COMP-REREV2-F1` through `F4`. The operator first absorbed the closeability
failure as CVF learning, then authorized one bounded successor repair. Exact-
manifest Amendment 1 adds fifteen worker paths, fixes role/gate sequencing,
and received independent `AUTHORIZATION_REVIEW_PASS` with no finding or waiver.
Disposition is `BUILD / AMENDMENT_1_REPAIR_READY`; existing product work is not
accepted or committed. The project pins portable public Core
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

Phases 0-3 are closed within their recorded boundaries. Phase 4 is 7/8; P4-E
DESIGN and SPEC remain accepted. Exactly one Claude `REPAIR_WORKER` dispatch is
now authorized for original worker paths 15-80 plus Amendment 1 paths 95-109,
under `WORKER_MUST_NOT_COMMIT`. Independent successor completion review,
closer-owned catalog regeneration, final gates/commit, Phase 5, and external-
repository absorption remain parked.

## Guardrails

- Treat `SESSION/ACTIVE_SESSION_STATE.json` as canonical;
  `CVF_SESSION/ACTIVE_SESSION_STATE.json` is only its compatibility mirror.
- Do not mutate public Core or private provenance from project work.
- Do not turn historical bounded evidence into production-readiness claims.
- Do not expand the P4-E repair beyond its effective worker ceiling, make an
  Alibaba/provider call, pull a Docker image, install a dependency, regenerate
  closer-owned catalog paths, or stage/commit worker changes.
- Do not start Phase 5, catalog schema migration, XR1 repair, or external-
  repository absorption without fresh authority.
- Run `python scripts/check_session_state.py` after changing continuity.

## History

The 2026-08-31 governance-control-loss checkpoint, Core-refresh attempts,
P4-A through P4-D evidence, earlier product tranches, and their claim boundaries
remain immutable in Git and under `SESSION/handoffs/`. Full compacted history:
[`SESSION/archive/SESSION_MEMORY_PRE_T3_2026-08-11.md`](archive/SESSION_MEMORY_PRE_T3_2026-08-11.md).
