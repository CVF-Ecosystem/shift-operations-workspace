# Session Memory

Provider-neutral companion to `ACTIVE_SESSION_STATE.json`. Last updated:
2026-09-09. Read only the active handoff and current authority paths by default;
use the archive for a targeted historical lookup.

## Current checkpoint

The first-party CVF provenance-inheritance recovery is `FREEZE /
CLOSED_BOUNDED`. The project pins portable public Core
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4` and requires the operator-local
rule pack materialized from private provenance
`bee38695ebac452e0ea6b3487706ed5c84f5fc2e`. Both repositories remain read-only
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
identity/conversation routing remains at independently accepted
`DESIGN_REVIEW_PASS`. Its former Core-refresh prerequisite is now satisfied.
The next allowed move is a fresh explicit transition to P4-E SPEC, followed by
independent SPEC and Work Order review before any BUILD. Phase 5 and external-
repository absorption remain parked.

## Guardrails

- Treat `SESSION/ACTIVE_SESSION_STATE.json` as canonical;
  `CVF_SESSION/ACTIVE_SESSION_STATE.json` is only its compatibility mirror.
- Do not mutate public Core or private provenance from project work.
- Do not turn historical bounded evidence into production-readiness claims.
- Do not start P4-E BUILD, Phase 5, catalog schema migration, XR1 repair, or
  external-repository absorption without their stated fresh authority.
- Run `python scripts/check_session_state.py` after changing continuity.

## History

The 2026-08-31 governance-control-loss checkpoint, Core-refresh attempts,
P4-A through P4-D evidence, earlier product tranches, and their claim boundaries
remain immutable in Git and under `SESSION/handoffs/`. Full compacted history:
[`SESSION/archive/SESSION_MEMORY_PRE_T3_2026-08-11.md`](archive/SESSION_MEMORY_PRE_T3_2026-08-11.md).
