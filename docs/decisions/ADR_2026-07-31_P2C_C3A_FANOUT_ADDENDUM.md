# ADR Addendum — P2-C C3a Fan-out Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

`P2C-WO-FEAS-F1 C3A_ROUTE_ENFORCEMENT_TEST_FANOUT`: source feasibility
inspection found that the original C3a combines two independently risky
changes:

- new assignment model, persistence, staffing control plane and atomic shift
  bootstrap; and
- assignment enforcement across every existing shift-bound route, service and
  legacy fixture.

The enforcement half reaches 24 principal-bearing production files and at
least 38 existing test/support files. Several required seams are already at
or near the hard file-size limit: operations-domain `models.py` is 296 lines,
ledger `tables.py` and `sql_ledger.py` are 300, repository facade is 300, and
handover service is 296. One exact C3a ceiling would therefore be too broad to
review safely and too likely to require an unreviewed path expansion during
BUILD.

## Decision

Split C3a into two independently authorized, reviewed, committed and pushed
sub-checkpoints:

1. **C3a1 — assignment persistence and staffing foundation**: package-owned
   model, migration, ledger parity, staffing APIs, `/auth/me`, assignment
   capabilities, and atomic new-shift creator assignment/audit.
2. **C3a2 — operational assignment enforcement**: apply stored canonical
   shift resolution and ACTIVE-assignment checks across every route named by
   R6/R7, migrate affected legacy fixtures, and prove enumeration-safe and
   cross-shift behavior.

C3a1 MUST NOT claim route-wide operational assignment enforcement. C3a2 MUST
start from a clean pushed C3a1 `REVIEW_PASS`; it may not reopen C3a1 storage or
staffing behavior except through a reviewed repair amendment.

The remaining order stays C3a2 → C3b → C3c → C3d. The final P2-C claim, all
R1-R29 requirements and AC-01..AC-35 remain mandatory. No requirement,
evidence class or claim boundary is waived.

## Authorization boundary

This addendum repairs checkpoint granularity only. It authorizes exact-path
Work Order authoring for C3a1, not BUILD, provider calls, staging, commit of
implementation, or work on C3a2/C3b/C3c/C3d.
