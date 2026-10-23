# P5-A Reporting Engine — Proposed Specification

Status: PROPOSED_REVIEWED_PLANNING
Risk: R2
Authority: docs/decisions/P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md
Product Milestone Binding: canonical table in that decision, A0-A7 and remainder.
No BUILD authority from this specification.

## Requirements and acceptance

R1. Render only canonical persisted Report data through a fresh primitive
roundtrip validation. Never trust model_construct or mutated nested fields.
Keep P2-R schemas, snapshot selection and status transitions authoritative.
Model roundtrip alone checks digest shape, NOT aggregate equality. Extract the
existing canonical aggregate digest calculation into a pure operations-domain
report_digest helper; both P2-R build_snapshot and export validation use it.
The helper hashes schema_version, enclosing shift_id, report_type, persisted
sections and source_manifest with the exact existing UTF-8/sort/separator rules.
Prove byte-identical old/new snapshot results. Reject valid-looking wrong hex,
changed enclosing shift/type, malformed records or changed content before any
attachment; never rebuild from fresh ledger to hide a mismatch.

R2. View set: shift-summary, customer-report, incident-report, handover-report.
PDF and XLSX support each view. Summary covers all six sections in canonical
order; other views state their exact subset and never imply a complete shift.
Records and evidence cannot silently vanish because of wrapping, missing fields,
length limits, empty strings, Unicode, pagination or zero records.

R3. Header/footer or XLSX Metadata sheet carries report_id, shift_id, report_type,
version, status, is_current/history, generated_from_cutoff, snapshot_digest,
view and template version. Printed labels distinguish draft/in-review/approved/
frozen and historical snapshot; render neither new approval nor current truth.
Exact labels: DRAFT -> Draft; IN_REVIEW -> In review (never Reviewed);
APPROVED -> Approved; FROZEN -> Frozen. is_current=false adds Historical.
Include displayed source type/id/version/digest and evidence references in a
readable appendix/sheet; verify exact membership against canonical manifest.

R4. Export neither alters domain/ledger rows nor appends approval, changes freeze,
creates a version, runs retrieval/LLM, or fetches an evidence URL. Historical
versions use the same read authorization as current ones.

R5. HTTP export authenticates via existing verified bearer dependency, loads the
Report server-side, applies canonical AssignmentScope and validates format/view.
Missing/inaccessible report: enumeration-safe 404; absent/invalid JWT: 401;
invalid format/view: 422. Renderer-invalid snapshot: controlled failure, no bytes;
error messages contain no raw record contents, stack trace or credential.
Stable mapping: invalid snapshot/aggregate mismatch -> 422 EXPORT_INVALID_SNAPSHOT;
unsupported glyph/control -> 422 EXPORT_UNSUPPORTED_TEXT; resource/size/row/cell
limit -> 422 EXPORT_LIMIT_EXCEEDED; unexpected render failure -> 500 EXPORT_FAILED.
Every refusal has JSON error only, no attachment Content-Disposition or binary
body; missing/inaccessible record uses identical 404, missing/invalid JWT 401,
invalid parameter 422. Precedence: auth -> assignment/read -> parameters ->
snapshot integrity -> text/resource/render. Matrix must test combinations.

R6. Binary MIME types: application/pdf and
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet. Fixed safe
filename from UUID/version/view, no user-controlled path/header characters.
Cache-Control no-store; X-Content-Type-Options nosniff. Cross-origin deployment
uses existing configured origin policy; never widen CORS. Safe UI binary helper
preserves bearer/error handling and abort behavior without JSON-decoding bytes.

R7. XLSX text is literal, including leading =,+,-,@, tab, CR and suspicious URLs;
never formula, automatic hyperlink, macro, external link or worksheet-name input.
Numbers/dates use explicit controlled types; invalid XML controls rejected with
bounded public error. Sheet rows are within Excel limits; overflow rejects before
response. No silent cell-length clipping. Formatting/header/width/wrapping usable.

R8. PDF Vietnamese diacritics must survive Unicode extraction and visual rendering.
Approved bundled font bytes/license/SHA are explicit inputs. Missing font/glyph
fails closed. Escape markup; no external resources, scripts or attachment embeds.
Long paragraphs and long unbroken values wrap; tables paginate with repeated
headers; every displayed record/reference remains represented. Empty content
still renders valid labeled output. No dependency on machine-local font fallback.

R9. Renderer output must be bounded: canonical input limits reused; reject oversized
render/output with a stable reason before returning an attachment. Concrete byte,
page/time/row caps and their resource proof are settled in active Work Order;
limits may reject, never silently truncate. No unbounded temporary files/cache.

R10. Web UI exposes format/view, report version/status and historical warning,
busy/error/success states. Failed, unauthorized, cancelled or offline requests do
not say download succeeded. Revoke object URLs and avoid hidden auto-downloads.
Report generation/approval/freeze controls keep current behavior.

R11. Tests must read generated XLSX structurally and render/inspect generated PDFs,
not just check magic bytes. Cases: empty/full six sections, mixed status/history,
Vietnamese/Unicode, multiline/long unbroken text, special markup/formula payloads,
invalid/tampered snapshot (including aggregate hex and enclosing identity), input/output overflow and missing font/glyph.
Compare record/ref membership and metadata with source snapshot. Test both real
InMemoryLedger and SQLite auth/API paths and regression of P2-R lifecycle;
no new schema migration. Browser verifies authenticated actual file downloads,
feedback and cleanup. Mock rendering/UI checks do not prove governance.

R12. Governance-behavior claims need a separately admitted real provider canary
per AGENTS.md, with sanitized request/response bound to actual application gate
observations, never operational report data. Proposed ceiling: one call only,
synthetic PUBLIC token, max output 64 tokens, zero retries. Provider/model/endpoint,
credential source and quota/cost authority must be current, exact and human-approved
before access. No such call is authorized or attempted by this draft.

R13. Before implementation register P5A-EXPORT-OUTCOMES under
docs/cvf/INVARIANT_FAMILY_STANDARD.md. Required applicability: shared format/status/
view outcomes, conditional payload fields, cross-representation membership and
non-mutation evidence. Matrix, independent contract hash, validator/emitter adapter
and mutation tests must be reviewed before renderer BUILD; do not derive expected
outcomes from renderer outputs. This proposed ID is NOT registered or proof today.

## Full completion and remainder

A0 is reused bounded; A1-A7 must all be verified before P5-A completion. Pure
package success does not close API/UI/integrated proof gaps. Any slice closure
updates the canonical gap table; it cannot tick P5-A or Phase 5 DONE.
P5-A2/P5-B/P5-C/P5-D remain separate owner-routed milestones in the binding.
No deployment/production/custom live customer report proof is included.
