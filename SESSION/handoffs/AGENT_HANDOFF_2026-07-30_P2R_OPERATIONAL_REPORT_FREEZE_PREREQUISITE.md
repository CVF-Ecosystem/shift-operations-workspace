# Agent Handoff — P2-R Operational Report and Freeze Prerequisite

## Disposition

- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Control-chain phase: `DESIGN`
- Risk: `R2`
- Active role: `DESIGN_AUTHOR`
- Status: `DESIGN RECORDED — SPEC NEXT; BUILD NOT AUTHORIZED`

## Settled predecessor

`MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30` is `FREEZE /
CLOSED_BOUNDED`:

- C3 `ab92f51be5b00740f2316b6e1b1c81aa186c753f`;
- C4 `5924d420e39ef2f542314ede2237d0fa70c81c24`;
- roadmap/catalog truth sync `ba9917a06dc8f2ff04bd5c42fb6b59f0d94d8590`;
- `MAR-BUILD-REV-F1..F5` closed without waiver;
- `HEAD == origin/main` was clean before this intake opened.

Do not reopen or batch predecessor work into P2-R.

## Operator sequence

The selected roadmap order is:

`P2-R → P2-C mutation/full UI → P2-D offline/realtime → full-shift exit gate`.

Only P2-R is active. Later items remain unopened and have no inherited
authority.

## Intake evidence

Source inspection confirmed:

- migration 002 has a reports table and four-state lifecycle;
- operations-domain, Ledger implementations and workspace-api have no Report
  runtime vertical;
- the JSON contract and migration shapes materially differ;
- report workflow prose requires cutoff/version/approval/evidence;
- freeze policy names `report_approved`, but ShiftService can satisfy it only
  via explicit audited override;
- approval receipts have no Report action;
- no deterministic/unique approved-report selection rule exists;
- reporting-engine and worker report generation remain stubs.

No provider call, external service, secret read, Docker/PostgreSQL run,
production data access, source/test/schema edit, stage, commit, or push
occurred during intake inspection.

## DESIGN disposition

All intake findings `P2R-INTAKE-F1..F9` are resolved without waiver in:

`docs/decisions/ADR_2026-07-30_P2R_OPERATIONAL_REPORT_FREEZE_PREREQUISITE.md`.

The selected design:

- implements only fixed operational type `END_SHIFT`;
- makes every server-derived snapshot/version immutable and preserves
  non-current history;
- requires a new migration for version uniqueness and exactly one current
  report per shift/type;
- uses exact canonical sections, source-manifest digests and one overall
  snapshot digest;
- reuses durable R2 approval receipts bound to Report id, version and digest;
- retires the report override;
- atomically binds handover readiness, one current approved Report, Report
  freeze, Shift freeze and both actor-bound audits;
- preserves the old public contract field names while tightening the
  previously loose pre-runtime schema;
- requires InMemory/SQLite/disposable-PostgreSQL parity plus fresh
  provider-backed governance evidence.

P5-A rendering/export, P2-C, P2-D and the full-shift exit gate remain outside
this tranche.

## Next governed move

Author SPEC only from the canonical intake and ADR. Freeze exact requirements,
API/contract shapes, lifecycle, canonical snapshot encoding, migration
constraints, backend parity, failure matrix, evidence cases and claim
boundary.

No WORK_ORDER, BUILD, source/test/schema/migration/contract edit, provider
call, Docker/PostgreSQL run, stage, commit, or push authority exists from this
handoff.
