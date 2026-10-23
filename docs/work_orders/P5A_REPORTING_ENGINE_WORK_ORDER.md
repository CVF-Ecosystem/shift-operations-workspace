# P5-A Reporting Engine — Draft Execution Scope

Status: DRAFT
Risk: R2

## Product Milestone Binding

Canonical current source and full gap set:
docs/decisions/P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md,
section Product Milestone Binding. Assign A1-A7 only after readiness and approval;
A0 reused. All remaining Phase5 milestones keep the owners/destinations there.
Acceptance: docs/specs/P5A_REPORTING_ENGINE_SPEC.md R1-R13.

## Authority and readiness

Operator authorized roadmap continuation, source inspection and planning.
This is not APPROVED_FOR_EXECUTION. No implementation/provider/install authority
is inferred from a draft or a planning review. Before activation:
1. Human R2 review accepts concrete product scope and any external effects.
2. Choose and verify redistributable Vietnamese font, license, bytes and source;
   choose exact dependencies and reproducible project installation method.
3. Set render input/output/page/time limits against accepted full input bounds.
4. Register/review the export invariant family and contract-source hash before
   renderer implementation; use docs/cvf/INVARIANT_FAMILY_STANDARD.md.
5. If governance proof is to be claimed, admit exact provider/model/endpoint,
   secret source, current quota/cost ceiling and one-call/64-token/no-retry envelope.
6. Materialize exact implementation manifest and compliant gate-to-role graph,
   review it, record activation SHA in active handoff before any product BUILD.

## Bounded proposed mutation families

- packages/reporting-engine/src/reporting_engine/**: pure rendering, metadata,
  validation, formats and bounded file splits under Python 300-line hard guard.
- packages/reporting-engine/pyproject.toml and package README; approved font/license
  under that package only, digest-pinned after source/license verification.
- packages/operations-domain/src/operations_domain/report_digest.py and
  apps/workspace-api/src/workspace_api/application/report_snapshot.py only to
  extract/reuse identical aggregate digest algorithm; no selection/schema/lifecycle
  change. Existing byte-equivalence regressions and new mismatch tests required.
- apps/workspace-api/src/workspace_api/application/report_export*.py;
  apps/workspace-api/src/workspace_api/api/reports/export*.py and router.py;
  apps/workspace-api/src/workspace_api/main.py only for router registration if needed.
- apps/workspace-web/src/features/operator-actions/ReportActions.tsx plus bounded
  ReportDownload*.tsx split; services/reportExport.ts; existing session/error owners
  only if an exact approved manifest proves necessary, not a blanket rewrite.
- packages/workspace-contracts/reports/**: binary/export contract documentation;
  no changes to canonical P2-R Report fields or status values.
- tests/unit/test_report_export*.py; tests/integration/test_report_export*.py;
  tests/cvf/test_report_export*.py; web tests/reportDownload*.test.tsx;
  bounded browser evidence fixtures; synthetic inputs only.
- pyproject.toml: reporting package path and exact approved dependencies only.
- Invariant family/matrix/adapter/tests exact paths determined by readiness,
  no new generic framework or unrelated guard changes.
- Product evidence/catalog/status/roadmap/index/knowledge and canonical continuity
  as required for truthful changes. Existing core/provenance/policies read-only.

## Evidence, failure and ownership

IMPLEMENTATION_WORKER changes authorized paths only, returns without commit.
Independent REVIEWER checks full milestone coverage and returned artifacts;
COMMIT_STEWARD owns material commits; SESSION_SYNC_STEWARD records actual SHAs in
separate continuity commit; CLOSER closes only after clean committed-range checks.
R2 human acceptance cannot be replaced by implementation worker self-approval.

Stop on unresolved readiness, scope/risk/external-effect expansion, unknown
coverage needed by implementation, changed source authority or failed mandatory
gates. Same-scope repairs obey consolidated-review/round-three escalation rules.
Do not weaken P2-R validators, golden contracts, permissions, assignment or tests.

Required proof: focused format/contract/authorization/browser tests, meaningful
PDF visual and XLSX structure inspection, P2-R regressions, invariant family gate,
repository/catalog/knowledge/session/file-size gates, full configured pre-commit,
independent final review and admitted live receipt for governance claims.
No pure unit/mock results may be promoted to governance proof.

## Planning checkpoint and return

This draft is reviewable scope only; build activation is pending the explicit
readiness items above. Product milestone remains 0 completed criteria newly
proved by this packet. No separate support tranche is opened; readiness is part
of the same P5-A work. On approval, settle readiness in DESIGN/SPEC and activate
exact bounded scope; return to user-downloadable reporting, not Core maintenance.
