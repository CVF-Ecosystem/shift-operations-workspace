# Session Memory

Provider-neutral companion to `ACTIVE_SESSION_STATE.json`. Last updated:
2026-09-10. Read only the active handoff and current authority paths by default;
use the archive for a targeted historical lookup.

## Current checkpoint

External-repository absorption is `INTAKE_READY / SOURCE_SET_REQUIRED` after
the operator selected return to that work. No repository URL/path set or
intended absorption outcome is yet present in current authority, so no clone,
fetch, enumeration, scan, absorption, or promotion has started.

The preceding operator-local ADIF-0057 machine-inheritance refresh is `FREEZE /
CLOSED_BOUNDED`. Private CVF provenance commit
`e4c055484f813b6d7bda6ed9249664908ccca087` supplies the downstream-aware
closeability checker and its standard/defect record through a refreshed
31-artifact rule pack. Project material commit
`d64530fcdc244d7080fbc1b04fd41956bf2c914a` binds the exact pins, adds a
fail-closed project adapter and tests, updates Project Knowledge, and invokes
the guard from `.githooks/pre-commit`. Local Git configuration records
`core.hooksPath=.githooks`.

Positive binding proof passes. A temporary active Work Order without its
closeability contract was rejected as `contract_missing` and then removed.
The project focused suite passed 88 tests; full pre-commit passed 3121 tests
with 146 skipped and two existing serializer warnings. Catalog, session,
file-size, knowledge, and inheritance gates pass.

P4-E remains closed bounded at its accepted product/review/catalog and
continuity commits. The inheritance refresh changed no product behavior.

## Product roadmap

Phases 0-3 are closed within their recorded boundaries. Phase 4 is 8/8 and
`CLOSED_BOUNDED`. External-repository absorption INTAKE is open only to obtain
the exact source set and desired outcome, then author a bounded corpus receipt.
Phase 5, governed-catalog schema migration, and XR1 debt remain parked.

## Guardrails

- Treat `SESSION/ACTIVE_SESSION_STATE.json` as canonical;
  `CVF_SESSION/ACTIVE_SESSION_STATE.json` is only its compatibility mirror.
- Do not mutate public Core or private provenance from project work.
- Run `python scripts/check_cvf_core_machine_inheritance.py --enforce` before
  dispatch, redispatch, review, or commit.
- Do not turn configured repository-gate evidence into a universal tool
  interception or agent-comprehension claim.
- Do not turn historical bounded evidence into production-readiness claims.
- Do not reopen P4-E without a new admitted finding.
- Do not clone, fetch, scan, or absorb until the exact repository source set,
  desired outcome, and bounded corpus receipt are established.
- Do not start any remaining parked tranche without explicit operator selection.
- Run `python scripts/check_session_state.py` after changing continuity.

## Claim boundary

This checkpoint proves static operator-local rule-pack binding and configured
project repository enforcement. The closed eight-commit project range was
pushed to `origin/docs/p4e-spec`. No Alibaba/provider call, product mutation,
Docker/database action, dependency install, deployment, public-Core sync, or
production action was performed.

## History

The previous active handoff is
`SESSION/handoffs/CVF_CORE_MACHINE_INHERITANCE_REFRESH_2026-09-10.md`.
Full compacted history remains at
`SESSION/archive/SESSION_MEMORY_PRE_T3_2026-08-11.md`.
