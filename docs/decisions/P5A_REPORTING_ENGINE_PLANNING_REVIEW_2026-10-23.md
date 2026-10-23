# P5-A Reporting Engine — Independent Planning Review

Date: 2026-10-23
Reviewer: inheritance_review, independent of planning author / implementation worker.
Verdict: CHANGES_REQUIRED before activation; no BUILD, provider, installer or asset-import authority.

## Product Milestone Binding

Reviewed canonical binding in P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md
against proposed specification R1-R13 and draft Work Order. Product outcome is
real authenticated application/browser PDF and XLSX downloads, not package-only
success. A0 reuse is bounded; A1-A7 remain open, including font/dependency and
evidence readiness. Phase5 remainder routes to P5-A2/B/C/D and is not silently
closed or pulled into this assignment. Review makes no complete repository-scan
or runtime-governance claim. Fresh inheritance guard reports zero violations;
DRAFT Work Order closeability is explicitly NOT checked by that guard.

## Consolidated findings

P5A-PLAN-F1 — Snapshot integrity contract is incomplete (blocking).
Source: operations_domain/report_models.py, ReportContent validators and Report.
Primitive roundtrip verifies record structure, membership/order, per-record source
digests and top-level snapshot_digest shape, but does NOT recompute/compare the
top-level snapshot digest. report_snapshot.build_snapshot owns the aggregate
algorithm including shift_id and report_type. Thus proposed R1 plus reused model
validation alone can export a syntactically valid altered snapshot digest or a
changed enclosing shift_id while presenting integrity metadata as validated.
Amend design/source claims and R1/R3/R11 to explicitly recompute the aggregate
using the canonical P2-R algorithm over the persisted snapshot (not fresh ledger
state), reject mismatch before bytes, and test wrong-but-valid 64-hex digest and
enclosing identity mismatch. Preserve historical snapshot semantics and P2-R owner;
no silent regeneration or unrelated domain repair is authorized.

P5A-PLAN-F2 — Current planning continuity is not yet recorded (activation blocker).
Canonical bootstrap/state/memory and active handoff still route operator product
selection after REPIN; the new decision records the operator-selected P5-A planning
lane. Before activation synchronize selection, planning status, active artifacts,
role, next move and parked conditions across these canonical surfaces. Keep P5-A
NOT STARTED until BUILD as stated; no milestone tick from planning.

P5A-PLAN-F3 — Make intended read/status and format failures fully testable.
R3 uses the word reviewed although the stored state is IN_REVIEW, which is not
completed review. Require exact enum-to-label mapping (DRAFT, IN_REVIEW, APPROVED,
FROZEN) without an implied approval. R5 leaves renderer-invalid HTTP mapping and
stable public error codes unspecified; settle explicit bounded mappings for
invalid snapshot, unsupported glyph/control, resource rejection and unexpected
renderer failure before activation. Include unauthorized/inaccessible/invalid
parameter combinations and zero attachment bytes on every refusal in the matrix.

## Remaining readiness blockers before activation

- Resolve F1-F3 in the canonical spec/design and have the changes reviewed.
- Obtain human R2 scope/external-effect disposition; draft does not grant it.
- Choose approved redistributable Unicode font: exact source/license/bytes/hash,
  supported-character policy and missing-glyph behavior; no machine font fallback.
- Set exact dependency and reproducible install plan; local presence is not
  project distribution/readiness or security approval. No install/import here.
- Fix concrete input/output/page/time/row/cell caps and resource enforcement proof,
  including highly expanded layout at accepted canonical input bounds.
- Register/review invariant family, independent source/digest, exact adapters and
  mutation corpus before renderer implementation under the existing standard.
- Materialize exact allowed implementation/evidence paths and gate-to-role graph;
  plan how intentional export-route OpenAPI changes satisfy existing golden-contract
  delta requirements rather than weakening or blindly refreshing golden hashes.
- Admit exact live provider/cost/credential/canary authority before any applicable
  governance claim or call; never include operational report data. This review
  makes no provider call and grants none.
- Require independent final format visual/structural, actual authenticated browser
  download, API authorization/non-mutation, lifecycle regression and full applicable
  gate evidence. Planning/source evidence is not implementation completion.

## Source assessment and limits

Inspected report_snapshot.py, report_service.py, reports/router.py, Report domain
models, ReportActions.tsx, package scaffold and root pyproject. Source supports six
canonical sections, filtered eligible OperationalEvents with other typed sections,
existing report read boundary and lack of downloads/dependencies. PDF/XLSX view
mapping and renderer resource behavior remain intended design, not proven code.
No application edits, outputs, provider calls, installations or broad tests were
performed by reviewer. Only this review record was authored.

## Consolidated Repair Rereview

Verdict: PLANNING_REVIEW_PASS_BOUNDED. F1-F3 are resolved in the authored planning
contract; this supersedes CHANGES_REQUIRED for planning prose only, not readiness
or BUILD authorization. No implementation behavior or evidence is accepted here.

F1: design/source claims now distinguish roundtrip validation from aggregate
verification; R1 pins exact aggregate inputs/encoding, shared canonical helper,
old/new digest equivalence and enclosing identity/wrong-hex failure tests with no
fresh-ledger regeneration. Direct A3 helper extraction and limited builder reuse
are explicitly scoped. These remain mandatory implementation proof obligations.
F2: fresh canonical bootstrap/memory and newly named active P5-A handoff agree
DESIGN/SPEC planning and held readiness; session checker PASS.
F3: exact stored-state labels, stable bounded failures, no attachment on refusal,
and authentication/read/parameter/integrity/render precedence are testable in R3/R5.
Implementers must preserve this precedence even with framework query validation.

Fresh inheritance guard: zero binding/closeability violations; DRAFT closeability
is explicitly not validated. No broad tests, product code, output rendering,
provider, installer or asset import performed by reviewer. Only this review file
was appended. All earlier readiness bullets remain activation conditions except
F1-F3 prose corrections, which are now resolved. Human R2/external-effect review,
font/dependency distribution, concrete resource caps, reviewed invariant family,
exact manifest/gate graph and applicable separately admitted live proof remain
held. P5-A A1-A7 remain OPEN/BLOCKED; Phase5 completion remains 0/5.
