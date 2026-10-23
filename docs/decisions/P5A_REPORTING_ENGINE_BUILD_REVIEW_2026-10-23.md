# P5-A Reporting Engine — Build and Independent Review

Status: LOCAL_REVIEW_PASS_BOUNDED / FULL_GATE_AND_LIVE_PENDING
Risk: R2
Decision owner: root ORCHESTRATOR / independent REVIEWER

## Product Milestone Binding

Full acceptance, current gaps and remaining Phase5 owners/destinations:
`docs/decisions/P5A_REPORTING_ENGINE_INTAKE_DESIGN_2026-10-23.md`.
Acceptance owner: `docs/specs/P5A_REPORTING_ENGINE_SPEC.md` R1-R13.
Authority: `docs/work_orders/P5A_REPORTING_ENGINE_WORK_ORDER.md`.
Paths: `docs/implementation/P5A_REPORTING_ENGINE_MANIFEST.md`.
A0 reuses bounded P2-R input. Current disposition at the end accepts A1-A6
bounded; A7 full material gates and real-provider canary remain open. No package/UI slice closes P5-A alone.
P5-A2/B/C/D stay owner-routed in the binding; Phase5 completion remains 0/5.

## Dispatch and role separation

Approved dispatch material `142052fccb8ebe1070ffccce385f2b5305f2f2e9`;
separate marker/continuity `14ae8e73887564739512cfb56c88f52e77638d0a`.
Each full hook: 3123 passed, 146 skipped, four warnings. Retained earlier
venv-isolation failure and its bounded repair are in the planning review.
Private source moved during marker preparation; two hook refusals were retained
without bypass. Final clean source `3e3023e5aea1c1e949c1fdc78ecc8d62bbd8f708`
was projected through the existing exporter, 1779 files checked against exact
committed blobs; independent Luna review accepted the static reconciliation.
Required closeability/ADIF carriers and exporter were unchanged. No downstream
profile adoption or runtime-governance claim follows from those static checks.

Sol/medium owns backend/render/digest/fonts and their tests. Luna/max owns UI.
Root independently reviews source, API/UI integration and actual browser proof;
another Luna/max independently reviews parsed/raster PDF and structural XLSX.
Specific role transitions were recorded in the active handoff before BUILD.
Workers return without commits. Root owns material/continuity commits.

Historical review/return statuses below are retained at their original checkpoint;
the final local disposition supersedes them without erasing failed attempts.

## Consolidated first source review

R1 findings below are direct P5-A repairs under the same acceptance, path,
risk and external-effect boundaries. No support successor or scope expansion.

| ID | Finding | Required disposition | Status |
|---|---|---|---|
| UI-R1-1 | Cross-origin fetch cannot read unexposed Content-Disposition; mandatory header matching rejected valid files | Safe filename fallback from server-loaded UUID/version plus allowlisted options; validate any exposed header; preserve existing CORS policy | Worker reports repaired; actual browser proof pending |
| BE-R1-1 | Pipe poll bounded first-byte availability, then blocking recv could exceed deadline | Bound complete renderer completion/transfer; terminate timed-out child; no partial bytes | Worker changed to fixed shared buffer and complete child exit; independent proof pending |
| BE-R1-2 | Historical:No appeared on current artifacts; explicit is_current missing | Exact current/history metadata and Historical label iff non-current; parse all eight shapes in both formats | Regenerated packet returned; independent review pending |
| BE-R1-3 | XLSX cell cap also restricted PDF; invalid XML scalar handling incomplete | Format-specific caps and controlled invalid-text refusal, long PDF content within PDF caps | Worker repair/proof pending |
| BE-R1-4 | Unexpected parent renderer/start/IPC error could escape structured JSON mapping; busy/integrity precedence unresolved | Generic EXPORT_FAILED without attachment, exact refusal precedence | Worker repair/proof pending |

## Returned evidence awaiting acceptance

UI worker: 13 focused component/regression tests and typecheck PASS, within
file caps. Node22.17.0 observed; package engines declares22.14.0. These are
component-level results, not actual browser download or governance proof.
Backend midpacket: 16 focused tests; eight status/history PDF/XLSX pairs plus
independent persisted-snapshot JSON oracles in ignored `.venv/p5a-worker-proof/`.
Independent artifact review is in progress; no final PASS claimed here.

## Independent integration proof plan and boundary

Root prepares a disposable SQLite schema and synthetic users, creates records
and report versions through the real HTTP API, then uses existing project
Playwright with local Chromium to operate actual UI controls across separate
local origins. Ten downloads cover four current views in both formats plus a
historical summary in both formats. Observe exact filenames/MIME, no-store,
nosniff, successful file bytes, CORS-hidden disposition fallback, object-URL
revocation, no orphan anchors and offline refusal without a new download.
Compare full disposable database content digests before/after download flow.
Root will inspect actual bytes; neither echoed receipts nor magic-byte-only
checks satisfy content proof. Temporary harness/output resides under ignored
`.venv/p5a-proof/` until accepted proof is recorded with reproducible commands.

No provider call, credential access, production data, public push or deployment
is authorized by this packet. A7 governance proof requires exact admitted
provider/model/endpoint/quota/cost/key-source authority and one real synthetic
canary; old receipts cannot substitute. Static/format/API observations alone
are not CVF-governance behavior proof. P5-A remains open.

## Consolidated artifact/integration review — repair round 2

Independent artifact review accepted the eight regenerated status/history pairs
for tested top-level membership, metadata, source hashes, Vietnamese extraction,
font/license and long-text coverage. It also tested all four views from the
persisted source fixture. Those accepted observations remain bounded; the
following newly identified root causes prevent final acceptance.

| ID | New root cause / required repair | Owner / destination | Status |
|---|---|---|---|
| F1 | Actual XLSX serialization changes leading CR to LF; preserve exact literal text through XML roundtrip | Sol; XLSX serializer and payload probes | OPEN |
| F2 | Reference receipt omits embedded evidence occurrences and nested Handover-item source refs; compare exact tuple multiplicity/digests parsed from bytes | Sol then independent artifact reviewer; views/invariant proof | OPEN |
| F3 | Every XLSX cell is text despite R7; use controlled numeric cells and explicit date derivatives while preserving canonical ISO precision/timezone | Sol; XLSX/types/proof | OPEN |
| F4 | Root raster confirms page2 begins mid-CustomerRequest without context; repeat continued section/record heading | Sol then root raster review; PDF layout | OPEN |
| F5 | Planned package metadata/README and wheel resource proof missing | Sol; reporting-engine packaging/font distribution | OPEN |
| F6 | Retain explicit old/new aggregate byte-equivalence proof on nonempty fixture | Sol; digest tests | OPEN |
| UI-R2-1 | Actual app requests only current reports; initial source inventory mistook history-capable response schema for history-enabled query | Luna; explicit lazy historical-report read and controls within existing UI family | Worker repaired; final browser pending |
| UI-R2-2 | History tests exceeded200 lines; split exact approved sibling with unchanged behavior | Luna; reportDownloadHistory.test.tsx | OPEN |

These are independent new root causes, not repetition of the same failed
repair. Root consolidated the packet before round2 edits. No semantic contract
relaxation, risk/effect expansion or independent support tranche was admitted.
The Date values worksheet must retain canonical ISO text and label Excel UTC
millisecond precision; no naive timestamp may silently be assumed UTC.

First actual browser attempt halted after eight current downloads when version1
controls were absent. Its failed receipt/log/oracle are retained under ignored
`.venv/p5a-proof/attempt-1/`; it is excluded from final acceptance. The repaired
history UI will be exercised in the next complete pass. Root also found and Sol
repaired quadratic XLSX cell styling: the actual 20k-row limit suite improved
from68.47s to5.94s. This directly supports the existing10-second deadline.

Full frontend before the history split:125/125 on Node22.17.0. Root found the
already installed exact Node22.14.0 and will select it through child-process PATH
only for final web/build/browser proof. No global nvm switch or download needed.

## Typed-value family reassessment before repair round 3

REVIEW_COST_ESCALATION_REQUIRED recorded before further repair. Root stopped
and consolidated the newly exercised family rather than rerunning the same
failed browser flow. The second browser attempt loaded the actual SQLite
Report and downloaded PDF, then received422 for XLSX. Independent diagnostic:
the valid persisted `generated_from_cutoff` reloads with no tzinfo through the
existing SQLite Report mapping; the new Date values helper rejected it. This
is a newly introduced storage-to-presentation assumption, not the prior CR,
reference, process deadline or UI-history root cause.

A second independent emitted-byte probe found numeric precision loss:
18014398509481985 reopened as1.801439850948198e16. R3 must preserve the exact
integer while assigning safe Excel types. Root approves only this same-scope
typed-value repair after consolidated review of these domains: naive SQLite
timestamps, aware UTC/non-UTC timestamps, dates outside Excel/UTC conversion
range, exact15-digit numeric boundaries and large/negative integers. Canonical
ISO and integer text remain exact; date derivatives must label timezone and
millisecond precision. Unspecified timezone is never silently converted to UTC;
unrepresentable Excel derivatives must be explicitly labelled, not corrupted.
Normal small version values remain numeric; integers outside Excel's reliable
precision range use explicit exact-text representation. Add real API XLSX
success coverage for both InMemory and reloaded SQLite, not just direct fixtures.

No acceptance weakening, new data store, schema migration, risk/effect change,
provider access or support tranche is admitted. Root ORCHESTRATOR authorizes
the bounded repair under existing authority; independent review remains open.
The failed second attempt is retained under `.venv/p5a-browser-1792769673106137900/`.

## Repeated external-reference movement and cost disposition

REVIEW_COST_ESCALATION_REQUIRED: private source HEAD moved repeatedly during
P5-A dispatch/repair. Root stopped dependent repair at the failed guard and
reviewed the common cause: a separate source session continued committing.
No product defect or new downstream guard adoption caused these refusals.
The 3e3023e5a-to-abf57900d delta changes only source continuity and the unrelated
NCR HTML delivery roadmap; mandatory carriers/exporter remain unchanged.
Root resumes only a bounded static projection/pin synchronization under the
existing same-scope authority, without another support tranche or intermediate
full-hook commit. Product repairs release after the exact guard passes and
independent binding review. Final material/closure gates remain mandatory;
future source movement can still block them. No guard weakening or source edit.

## Final local review disposition — 2026-10-23

Root independent REVIEWER accepts the local implementation boundary A1-A6.
Sol/medium authored backend; Luna/max authored UI; neither committed. Root
reviewed digest extraction, snapshot validation, authorization/refusal order,
killable process, serialization, resource/typed-value boundaries and UI lifecycle.
Independent artifact Luna accepted all8 final status/history pairs against exact
oracle hashes and record/reference Counters, including embedded evidence and
nested Handover sources; independently generated focused-view outputs matched
those Counters in PDF and XLSX. CR, aware/naive dates, exact large integers,
15-digit numeric values and formula-like literal text passed emitted-byte probes.
Final wheel isolated import/resources and font/license SHA matched SPEC.

Resolved without waiver: UI-R1-1, BE-R1-1..4, F1..F6, UI-R2-1..2, plus the
consolidated R3 SQLite-naive-date/Excel-large-integer defects. No semantic
acceptance weakening, provider access, schema/lifecycle or scope expansion.
The separate artifact reviewer also found inherited child env/dotenv and harness
hash omissions. Root repaired the proof harness before the successful pass:
OS/runtime env allowlist, root/web dotenv refusal (inert .env.example excluded),
harness source and generatedJS hashes included/checked. That source review was
independent of its author. Browser byte checks prove records/subset metadata;
exact evidence/nested-reference claims come from the separate artifact probes.

Evidence retained in P5A_REPORTING_ENGINE_LOCAL_EVIDENCE_2026-10-23.json:
- Sol final relevant backend/P2-R221 PASS in36.39s; Ruff/file-size PASS.
- Root full frontend128/21files plus tsc/vite build PASS on exact Node22.14.0.
- Mandatory independent matrix/SPEC digest recomputation matches frozen pins;
  full P5-A outcome/mutation corpus13/13 PASS in13.69s. Flat-receipt nested
  mutation exclusions accepted only because emitted bytes were independently
  parsed for actual records, references, evidence, metadata and nonmutation.
- Actual local Chromium151.0.7922.34 and HTTP API/SQLite, synthetic-only input:
  ten downloads across four current views/two formats plus historical summary;
  safe filenames/MIME/no-store/nosniff, CORS-hidden disposition fallback,
  offline refusal,10 URL create/revoke, no anchors/page errors and process cleanup.
  Full disposable DB digest before/after92291b5448ff6d35da6a8f8a9206679e1ef34c31d186b812ea8ec3b8a88c53b3.
- Root raster inspected all3 final full-draft-current PDF pages and actual UI
  panel: readable Vietnamese, long text wrapped, continuation section/record
  and source-manifest context visible; no clipping on inspected pages.
- Offline final wheel SHA bec322f04443d9ef2b008d435e2c7d02cde9a5db78719bb797d7618aab58ca3f;
  final XLSX source matches wheel; exact font/license hashes and isolated import.

Both failed browser attempts remain retained and excluded from final PASS.
Current local material is reviewable and ready for full normal pre-commit;
full hook result and actual material SHA belong to the subsequent continuity
receipt. Do not claim those gates before they return. Reporting-engine stays
partial; A7 remains BLOCKED_LIVE_AUTHORITY and Phase5 remains0/5. SPEC R12
requires current exact human-approved provider/key-source/endpoint/cost authority;
expired local quota records and prior provider receipts do not satisfy it.
The concrete proposed one-call envelope is unactivated in the Work Order.
No operational report data, secret read, provider call, public push, production,
deployment, broad AI-governance or milestone completion claim is made.

Independent artifact/harness final return: ACCEPTED_LOCAL_BOUNDED at private
pin91174b47c/publicb69e108. It also parsed all10 actual browser downloads for
exact record/ref Counters: full5/13, customer1/1, incident1/2, handover1/6,
including embedded/nested refs and canonical SQLite cutoff/date derivative.
All21 selected source hashes and generatedJS/download hashes matched the
receipt, as did stable DB/URL/process cleanup. Later unrelated private HEAD
movement is reconciled separately by root; it does not invalidate unchanged
product bytes or promote the historical checked pin to a newer review.

Staged source binding verified against all21 observed browser source hashes;
Git CRLF-to-LF text normalization is recorded explicitly with staged SHA-256
values in the local receipt. Assets remain byte-exact. git diff --check reports
only two inherited trailing spaces in the exact pinned third-party license;
those bytes are preserved to retain the required license hash. No policy or
code whitespace exception was added.

## Full material gate refusal and consolidated OpenAPI repair

The first material commit did not occur: normal hook returned13 failures,
3156 passed,146 skipped,4 warnings in174.46s. All13 failures share one new
integration root cause: the P5-A export path remains in legacy OpenAPI hash
chains, which strip only their known historical deltas. Adding it only to the
P2-R report-path set did not cover the later/earlier chain owners. No runtime
or artifact failure is inferred from that proof-wiring defect.

REVIEW_COST_ESCALATION_REQUIRED: root stopped before further repair and
consolidated the whole chain. Same-scope continuation is justified by this
independent new cause, with all historical baselines immutable. Scope is only
the new exact P5-A export delta test/helper and minimal linkage in
test_c3b2_mutation_openapi_contract.py and test_p2b_openapi_contract.py; restore
the original P2-R report-path set. Cover all13 failures together, including
both full-document golden checks and earlier shared strip callers. Preserve
negative unrelated-path/route-removal checks and add export-surface protection.
No blind golden refresh, broad removal, product/source change, generic test
filtering, hook weakening, provider access or new tranche is admitted.

Root REVIEWER to ORCHESTRATOR; Sol REPAIR_WORKER owns this bounded proof repair.
Root independently reviews before reattempting the full configured hook. A1-A6
local acceptance remains bounded, while A7 conformance is again explicitly
OPEN_FAILED_FULL_GATE plus held canary. The exact reviewed24 artifacts were
preserved before pytest regenerated mutable outputs; browser source unchanged.

The consolidated chain repair exposed an API-documentation discrepancy:
generated OpenAPI says nullable/optional format/view and JSON200, while the
admitted endpoint requires both options and returns PDF/XLSX. Root retains
this under A4/A7, not an unowned later tranche. Authorize only new-route
documentation annotations: hide the auto-generated optional query schemas,
declare exact required allowlisted query parameters, binary PDF/XLSX200 content
and Response class through route metadata. Preserve manual runtime validation,
auth/assignment/refusal order and all response bytes. Router remains under300.
Recheck focused OpenAPI and API outcomes; root independently reviews and makes
one fresh browser/source-bound pass before full hook. Renderer/wheel/artifact
source unchanged, so accepted format evidence is consumed without regeneration.

## OpenAPI amendment independent acceptance

Sol returned63 OpenAPI tests and2 InMemory/SQLite API outcome tests PASS. Root verified exact new export query enums/required flags, HTTPBearer and binary MIME schemas; historical SHA literals unchanged. Independent AST comparison found every route function body identical to the accepted runtime. Negative missing/extra-method/changed auth/enum/MIME plus unrelated path/legacy change checks remain active. P2-R path set restored; no historical baseline refresh. Fresh browser .venv/p5a-browser-1792772279328042000 passed10/10 with unchanged DB digest cec14da13d7263f314980483950f0d1c5cedcb3fc7907395150ef4f70cc25bc8, URL/process cleanup and offline/CORS behavior. Only route metadata source hash changed; renderer/UI/harness/wheel evidence remains valid. A4 reaccepted bounded. Root REVIEWER to SESSION_SYNC_STEWARD to COMMIT_STEWARD for normal full-hook retry; A7 live authority held.
