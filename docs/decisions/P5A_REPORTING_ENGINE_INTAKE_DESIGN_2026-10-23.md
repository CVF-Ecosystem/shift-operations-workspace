# P5-A Reporting Engine — Intake and Design

Status: PLANNING_REVIEW_PASS_BOUNDED
Risk: R2
Execution base: db6e12c

## INTAKE

Operator directed returning to the roadmap and continuing under mandatory Product
Milestone Binding. Select P5-A, first open Phase 5 item; do not open a new Core
maintenance or repository-absorption lane. This packet advances product planning,
not product BUILD, release readiness or milestone completion.

## Product Milestone Binding

Milestone: P5-A in docs/implementation/EXECUTION_ROADMAP.md, Phase 5 (base db6e12c).
User outcome: an assigned operator/supervisor can generate the existing end-shift
snapshot and download readable Vietnamese PDF and real XLSX through the workspace,
with the exact report/version/status/cutoff/source lineage visible.
Acceptance: renderer correctness, complete intended content, evidence lineage,
existing read-authorization parity, safe formats, working browser download and
required tests/review; acceptance owner is product operator with independent R2 review.
Current truth: reporting-engine is stub (MODULE_REGISTRY entry); P2-R supplies
immutable END_SHIFT snapshots, six typed sections, source manifest/digest, existing
lifecycle and generate/read endpoints; web ReportActions has generate/version/submit
but no download. No PDF/XLSX dependencies are declared in root pyproject.

| Criterion / dependency | Current evidence / limitation | Gap ID / status | This assignment | Owner | Concrete destination |
|---|---|---|---|---|---|
| Canonical report draft | report_service.generate/build_current_content; P2-R Report model | A0 ACCEPTED_BOUNDED | Reuse, do not replace | Report domain owner | P2-R contract remains owner |
| Input selection semantics | report_snapshot filters OperationalEvent; other sections retain typed operational state | A1 OPEN | Specify exact reuse and labels | SPEC_AUTHOR | P5A_REPORTING_ENGINE_SPEC.md R1-R3 |
| PDF, XLSX and report views | reporting-engine only README scaffolds | A2 OPEN | Specify renderers and views | IMPLEMENTATION_WORKER after authorization | P5-A BUILD, reporting-engine |
| Traceability / validation / complete output | P2-R hashes exist, no export artifact | A3 OPEN | Specify integrity and output metadata | SPEC_AUTHOR / REVIEWER | P5-A BUILD + export conformance evidence |
| Authenticated application download | reports GET exists, no binary route | A4 OPEN | Specify assignment parity and response | API implementation owner | P5-A BUILD API/export contract |
| Product UI download and errors | ReportActions lacks download | A5 OPEN | Specify browser flow | UI implementation owner | P5-A BUILD download controls |
| Vietnamese font and dependency distribution | local reportlab 4.4.4/openpyxl 3.1.5; not project deps; no font asset | A6 BLOCKED_READINESS | Inventory and explicit pre-BUILD decisions | ORCHESTRATOR + operator | Work Order readiness conditions; no install/import yet |
| Conformance/integrated and governance evidence | No P5-A evidence yet | A7 OPEN | Define proof; no false reuse of P2-R proof | independent REVIEWER | P5-A BUILD evidence + bounded live authority |
| Deployment, operational pilot, backup, analytics | Phase5 rows not started | OUTSIDE_P5A OPEN | Route remainder, do not implement | ORCHESTRATOR + product operator | P5-A2 forecasting; P5-B observability; P5-C resilience; P5-D release/pilot |

All P5-A criteria and discovered dependencies are represented; no claim of a
complete repo scan. UNKNOWN or readiness-blocked items prohibit dependent BUILD.
Planning assignment owns this design/spec/draft execution scope and source
verification only. Product gaps A1-A7 remain open until implementation evidence.
No automatic successor authority. Stop planning at one independently reviewed
packet and human R2/external-effect checkpoint; no unrelated governance expansion.

## Source verification

- docs/implementation/EXECUTION_ROADMAP.md Phase5: P5-A output; forecasting separate.
- docs/catalog/MODULE_REGISTRY.json reporting-engine: status stub, zero code.
- packages/reporting-engine/README.md plus pdf/excel/templates/validation README:
  scaffold intent only, not implementation.
- packages/operations-domain/src/operations_domain/report_models.py:
  ReportContent validates six sections, manifest correspondence/per-record digest;
  aggregate snapshot_digest is shape-only and requires explicit verification.
- apps/workspace-api/src/workspace_api/application/report_snapshot.py:
  eligibility, ordering, limits (500/section, 2 MiB) and canonical digest owner.
- apps/workspace-api/src/workspace_api/application/report_service.py:
  authoritative current-content generation and CLOSED-shift generate chain.
- apps/workspace-api/src/workspace_api/api/reports/router.py:
  JWT dependency, assignment-scoped GET and flat ReportResponse.
- apps/workspace-api/src/workspace_api/application/assignment_scope.py:
  stored ACTIVE assignment / enumeration-safe inaccessible record boundary.
- apps/workspace-web/src/features/operator-actions/ReportActions.tsx:
  current report metadata and mutation controls, no export.
- apps/workspace-web/src/services/api.ts: session bearer and error handling;
  response.json contract requires a separate supported binary request helper.
- docs/decisions/ADR_2026-07-30_P2R_OPERATIONAL_REPORT_FREEZE_PREREQUISITE.md:
  P2-R excludes P5-A output; historical versions remain read-only history.

## DESIGN decisions

D1. Reuse persisted P2-R Report; pure renderer takes a revalidated Report primitive
roundtrip and never queries ledger, changes lifecycle or invokes AI. Aggregate digest
verification is explicit: extract the existing unchanged aggregate calculation
into operations_domain/report_digest.py shared by snapshot builder and export;
roundtrip alone does not validate aggregate equality. API owns auth
and ledger reads. Do not duplicate snapshot selection, make a new truth store,
change approved/frozen state or invent an LLM narrative.

D2. Initial report templates are four views of the existing END_SHIFT record:
shift-summary (all six sections), customer-report, incident-report, handover-report
(the corresponding sections). A view is not a new canonical ReportType. Every view
carries report/shift/version/status/current/history/cutoff/digest/template version
and exact source references of displayed records; clearly state view scope and
empty sections. All operational state/evidence remains as stored.

D3. Export historically readable versions as snapshots, not fresh operational truth.
DRAFT/IN_REVIEW watermarks remain explicit; APPROVED/FROZEN labels reflect stored
state, never a new approval. A historical version is visibly non-current. Existing
model/digest validation is mandatory; no implicit regeneration during download.

D4. API proposal: GET /reports/{report_id}/export?format=pdf|xlsx&view=...
Same principal/assignment and enumeration-safe read boundary as canonical GET.
No new permission or mutation/audit action is silently introduced. No store/cache
or background queue; bounded in-memory response; no-store/nosniff/attachment headers.
Response preserves generated_from_cutoff; report body is never sent to a provider.

D5. PDF uses an approved redistributable Unicode font; reject missing glyphs or
unsupported characters before delivering output. Do not rely on a local Windows
font or silently replace Vietnamese. XLSX stores untrusted text as literal text,
never formulas, hyperlinks or external references. PDF escapes markup and does
not interpret HTML, fetch URLs or embed attachments. No partial/truncated success.

D6. UI adds separate non-mutating download controls with format/view choice, busy
state, accessible feedback, credentialed binary helper and object-URL cleanup.
Keep Generate/Submit and approval/freeze semantics unchanged. No offline export
queue or cached authenticated artifacts. Visible failed download, no false success.

D7. Dependency proposal: exact reportlab==4.4.4 and openpyxl==3.1.5 (locally present,
not an approval or supply-chain/security claim). License/font asset and clean
reproducible install verification must be settled in readiness before BUILD.

## Boundary and next move

No provider/credential access, dependency install, asset import, app code change,
Docker/database action, deployment or push performed. Human R2 approval must
accept the concrete scope/readiness before activating the draft Work Order.
Independent planning review checks product coverage and source claims. P5-A stays
NOT STARTED until BUILD begins; no closure from these documents alone.

## Consolidated planning repair response

P5A-PLAN-F1: corrected source claim and R1/R3/R11. Shared domain digest extraction
preserves the existing algorithm and P2-R output bytes, adds explicit aggregate
and enclosing identity mismatch checks, never regenerates current ledger content.
This is a direct P5-A integrity dependency A3, not a general domain refactor.
P5A-PLAN-F2: canonical state/bootstrap/memory/new named active handoff now select
P5-A DESIGN/SPEC; implementation remains stub and Phase5 0/5.
P5A-PLAN-F3: exact status labels, bounded public error mapping and refusal
precedence/combination matrix requirements specified. All other pre-activation
readiness items remain explicit blockers, not waived or claimed resolved.

## Local font source candidate (not imported or activated)

Existing local Matplotlib data contains DejaVuSans.ttf and LICENSE_DEJAVU.
Font SHA256: 3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22.
License SHA256: d75938dec098f06f0ac3c00853065d94f020be1c3c62ef1dc2975ba15b4d9b0e.
Read-only license inventory identifies accompanying reproduction/distribution
terms and required notices. No asset was copied into this project; packaging,
character-coverage tests and approved source/license notice remain pre-BUILD
readiness. This candidate avoids a required font network download; it is not
proof of renderer correctness or legal/security approval.

## Planning disposition

Independent consolidated planning review and rereview:
docs/decisions/P5A_REPORTING_ENGINE_PLANNING_REVIEW_2026-10-23.md,
PLANNING_REVIEW_PASS_BOUNDED. F1-F3 resolved at contract level. R2 human scope
review and concrete readiness remain before execution. No P5-A product criteria
newly satisfied; all A1-A7 remain OPEN/BLOCKED for implementation/proof.

## Current REVIEW acceptance checkpoint — supersedes planning inventory

Dispatch142052f/marker14ae8e7 activated product BUILD. Independent local review
accepted the repaired product boundary. P5-A remains REVIEW, not FREEZE/DONE;
Phase5 remains0/5. Historical planning tables above are source-at-planning.

| Criterion | Current evidence / remaining gap | Status | Current owner / concrete destination |
|---|---|---|---|
| A0 canonical draft | Existing P2-R snapshot lifecycle retained | ACCEPTED_BOUNDED_REUSED | P2-R domain owner; existing lifecycle |
| A1 input/labels | Same aggregate recipe; all8 status/history pairs parsed; exact metadata | ACCEPTED_BOUNDED | Root independent REVIEWER; renderer/source tests and local receipt |
| A2 four-view PDF/XLSX | Both formats/four views; CR, numeric/date types, long text and continued-page context reviewed | ACCEPTED_BOUNDED | Root and independent artifact REVIEWER; build review and parsed bytes |
| A3 complete lineage | Exact record, manifest, embedded evidence and Handover-source tuple multiplicities; focused/full views; substitution negatives | ACCEPTED_BOUNDED | Independent artifact REVIEWER; packet oracle/hash/counter checks |
| A4 API download | Auth/refusals and binary route; accurate required query/binary OpenAPI metadata,63+2 focused tests and fresh10-download source-bound browser pass | ACCEPTED_BOUNDED | Root independent REVIEWER; API/OpenAPI tests, AST comparison and browser receipt |
| A5 real UI current/history | Actual10 downloads, CORS-hidden disposition fallback, offline refusal,10 URL revocations;128 tests/build on Node22.14.0 | ACCEPTED_BOUNDED | Root independent REVIEWER; browser receipt and UI tests |
| A6 environment/distribution | Locked Python3.13.12, font/license hashes, offline wheel and isolated resource import | ACCEPTED_BOUNDED | Root and independent artifact REVIEWER; package/wheel evidence |
| A7 full conformance/live | Local3173PASS/source3199PASS; exact1 real call401invalid_api_key,accepted0. Retain failed receipt/review/commit; valid selected-endpoint credential + new bounded attempt required before live acceptance | BLOCKED_CREDENTIAL_AND_SPENT_ONE_CALL | Luna SPEC_AUTHOR, Sol IMPLEMENTATION_WORKER after contract review; root independent REVIEWER/COMMIT_STEWARD/effect owner; independent result REVIEWER |
| Remaining Phase5 | Forecasting, dashboard/observability, resilience, pilot/release unchanged | OUTSIDE_P5A OPEN | Existing roadmap owners/destinations: P5-A2, P5-B, P5-C, P5-D respectively |

All P5-A gaps and Phase5 remainders stay represented. Local acceptance does not
close A7, P5-A or Phase5. User-admitted one call is spent:1key/1POST/1response/0accepted,401invalid_api_key;no retry. No public/deploy effect.
Evidence: docs/decisions/P5A_REPORTING_ENGINE_LOCAL_EVIDENCE_2026-10-23.json.
