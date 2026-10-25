# P5-A2 independent source/history/numeric review

Disposition: SOURCE_REVIEW_PASS_BOUNDED
Date: 2026-10-24; risk R2; root independent REVIEWER, separate from worker.
Dispatch125868a; pre-BUILD continuityaf4e668. Source is local uncommitted BUILD.
Whole product binding and14gap remainder:
docs/decisions/P5A2_PROACTIVE_REPORTING_INTAKE_DESIGN_2026-10-24.md.
Scope/acceptance: docs/work_orders/P5A2_PROACTIVE_HISTORY_NUMERIC_WORK_ORDER.md.
Frozen SPECfd35641c/matrix4ff48756 retained; no new contract or live authority.

## Consolidated review round1

Root read all5 product modules, helper, unit and integration tests, README and
worker return/evidence against H1-P2. Numerical oracle values are fixed before
BUILD in .venv/p5a2-prebuild-numeric-oracles.json (SHAd8744f24).
Existing worker18focused/41withsnapshot passes are consumed as bounded evidence;
no duplicate broad suite was run. Targeted independent probes address actual
contradictions and missing contract evidence, not generic extra hardening.
Inheritance/closeability0/0 before review/repair routing. No live action.

| Finding | Observed evidence | Required same-scope repair |
|---|---|---|
| NUM-R1-1 H1/H2 | Same shift/version/report ID/times/digest, but altered record bytes in a second candidate returns READY when the valid copy is first. Identity comparison trusts the digest string and silently selects one conflicting value. | Compare immutable content as well as metadata for visible duplicate versions; reject conflicting bytes deterministically in either order. Lifecycle-only flags may differ without implying historical approval. Add both-order regressions and keep future versions excluded. |
| NUM-R1-2 H1/H4 | `complete='no'` returns READY. Malformed copied Report.content raises AttributeError, and mixed scalar version types raise TypeError instead of abstention. | Require actual boolean True completeness/retention assertions. Validate input containers, selected metadata and canonical content shape before dereferencing/hashing/sorting. Malformed supplied values return a controlled closed reason; do not hide arbitrary programming bugs with an indiscriminate success/fallback path. Add meaningful negative regressions. |
| NUM-R1-3 N4/R1 | Training lineage silently changes query_end from supplied18:00 to origin05:59:59.999999, while the SPEC payload names the source query window. Independent expected digest a21de6a5 versus emitted39156882. This can also claim an end-exclusive fold window that excludes a selected cutoff equal to origin. | Preserve supplied query bounds in the lineage preimage, with separate run_as_of origin and visible training IDs. Expose an inspectable canonical lineage payload/history context, including source/actor assertion and selected refs, rather than only unverifiable digest strings. This is supplied-input traceability, not actual auth or cohort proof. Test exact independently constructed outer/training/evaluation payloads and equal-origin boundary. |
| NUM-R1-4 N2/N3/P1 | Late-correction tests assert only outcome in READY or ABSTAINED; that cannot prove fold selection or future-data exclusion. Current digest tests check only sensitivity. Freshness proof checks2days, not exact24h. | Replace permissive assertions with actual fold target/order, origin-visible versions and independently expected predictions/digests. Prove latest12 with >18 observations, insufficient historical training, correction/status/target exclusion, exact24h and drift threshold equality. Keep before/after nonmutation on both READY and refusal; preserve unrelated valid tests. |
| NUM-R1-5 R2 diagnostics | Insufficient history returns observation_count11 but no required count; calibration failures similarly omit required evidence counts. | Record available/required observation or fold/training counts for insufficiency/calibration abstention. These are bounded diagnostics, not published forecast or signals. Test the actual fields. |

Raw first root probes: .venv/p5a2-first-source-review-probes.json. Exact outcomes:
truthy_complete READY; duplicate_conflicting_bytes READY; malformed_content
AttributeError; mixed_version_types TypeError; short_history missing required
count. These failures remain historical evidence after repair. Root found no
new method-selection or source-authority root cause requiring SPEC expansion.

## Authority, risk and next governed move

One consolidated repair under the existing H1-P2 objective/path families/R2
ceiling/effect class and root commit ownership. Worker must not edit frozen
SPEC/matrix, guards, credentials, existing reporting semantics or unrelated tests.
Update return/evidence with truthful repaired-source hashes, actual focused
commands/results and limitations; don't present the first packet as final proof.
Root owns catalog regeneration after the source settles and normal full hook.

All14 product gaps remain open/blocked/held. Supplied history/numeric work has
not yet been accepted. G01/A7 and G02 operational context remain dependencies;
G06 actual scoped query, G07 scheduler, G11 API/UI, G12 human approval and G13
integration/drills remain with backend/UI workers and root at their P5-A2 gates.
G14/live/key/model/CSV is held. G03-G05/G08-G10/G13 numerical portions remain
under this repair. P5-B/C/D owners and concrete destinations stay in the binding.
No package test pass closes P5-A2 or Phase5 (still0/5).

## Repaired source rereview and final boundary correction

Root consumes repaired24focused/47withsnapshot results and recomputed source
hashes. NUM-R1-1..5 are substantively repaired: original independent failure
probes now abstain; nested invalid sections refuse; required counts and actual
outer/training/evaluation preimages are exposed; source-window bounds remain
fixed; latest12/late-version/target exclusion and exact freshness/drift tests
assert actual values. No algorithm, invariant or integrated-scope change.

NUM-R2-1 H4 is a repair-introduced ordering regression: comparing duplicate
immutable bytes now serializes a501-incident visible candidate before its cap
refusal. Root instrumented ReportContent.model_dump: actual calls begin[501,0,
0,0], although the final result is SCOPE_INCOMPLETE. Cap refusal after allocating
the disallowed value does not satisfy the pre-materialization requirement.
Move bounded shape/count admission before any such serialization, retain
future-created exclusion and duplicate-byte refusal, and add one focused
no-materialization regression. This is repair round2 with a named new root
cause, under the same admitted path family and H4 contract, not a new tranche.
No further broad hardening or method expansion is requested.

## Final source acceptance within supplied-input boundary

NUM-R1-1..5 and NUM-R2-1 are resolved without waiver. Root reran all original
contradiction probes plus nested-shape refusals, independently verified7fixed
pre-BUILD numerical oracles, and observed0serializercalls for501refs. Frozen
SPEC/matrix pins MATCH. Static source review covers all5modules and finds no
network/credential/environment/ledger/database/subprocess/action imports or
file/eval/exec calls in this bounded changed set. This is source inspection,
not a universal effect-interception claim. Local detail is
.venv/p5a2-final-independent-review.json. Worker final25new/48withsnapshot
PASS is consumed; exact numerical, chronological fold, digest and24h/drift
boundaries were inspected. Old18/41 and24/47 packets/failures remain historical.

H1-H4/N1-N4/P1 pass for supplied canonical inputs only. P2 material completion
requires normal full pre-commit, committed material and actual-SHA continuity;
root records observed full results/SHAs in active handoff after those commits.
No required full-gate result is invented here. Root REVIEWER transitions to
COMMIT_STEWARD for the accepted finite source set and truthful metadata only.

G03-G05/G08-G10/G13 now have accepted pure-input numerical portions, with actual
ledger/auth/retention/SQL/operational-quality/integration portions still open.
No whole G01-G14 product criterion or Phase5 milestone is closed by this subset.
Remainder ownership/destinations in the binding and worker return remain valid.
Next product move after committed completion: bounded source verification and
contract/WO for actual assignment-scoped ledger history (G04-G06), keeping the
G01/G02/G14 integrated/live gates and all remaining product work visible.

## Actual final preflight disposition

Material commit was not attempted: inheritance rejects private297b3ac7 versus
projectpin721f98de. Pure source acceptance above remains bounded/local only.
No post-BUILD full suite result or material SHA exists; P2 and tranche completion
remain open. Finite source-churn stop applied, no further repin or bypass.
Session/implementation truth/index/roadmap record LOCAL_UNCOMMITTED source and
blocker. Next material action requires stable binding before normal full hook,
material commit and actual-SHA continuity. No operator approval is requested.

## User-directed final material resumption

Operator continues roadmap. Exact10 returned product/test hashes MATCH and
frozen SPEC remainsfd35641c. Accepted review25/48+7oracle evidence inherited,
not recreated. Bounded current reference932b1ab2 verified against1779committed
projections; protected5carriers unchanged. Resume final normal full source hook
and material/actualSHAcontinuity under same objective/path/R2/effects/owner.
No new BUILD, provider or whole-milestone closure. Prior blocked receipt is
historical; actual full gate and material SHA are recorded only after completion.

## Stable-source completion resumption — 2026-10-25

Operator reports source stable. Exact provenance 6d5c4a5de4b23e4ec5cb5a54fb8f0c8e6a71fd2c; 1779 committed projected files verified, selected source paths clean; all10accepted source/test hashes MATCH. Native exporter/Report contracts/gates and existing independent25/48+7oracle evidence reused. Only current static binding and truthful metadata changed. Independent reference review and normal material full hook/commit remain pending; then actual-SHA continuity and bounded G04-G06 source verification. All14gap owners and held live dependencies unchanged; no whole milestone closure.

## Independent reference/completion review acknowledgment — 2026-10-25

Role transition: canonical state ORCHESTRATOR context to delegated INTERNAL_AGENT
independent REVIEWER for this R2 REVIEW-only assignment; decision owner remains
Root. Scope is static binding/reference pins, refreshed knowledge, completion
metadata and full-gap remainder consistency. Accepted H1-P2 source evidence is
inherited without rerunning product tests; no source, test, continuity, guard,
provider or commit action is authorized here.

## Independent reference/completion review disposition — 2026-10-25

Disposition: `REVIEW_PASS_BOUNDED`; blocking findings: NONE. Project HEAD at review:
`af4e668556b53a2cdb2588dc9d08a45590bcc4ca`; accepted source/test bytes remain
unchanged (10/10 SHA-256 values match the worker return). Provenance and rule-pack
pin resolve to `6d5c4a5de4b23e4ec5cb5a54fb8f0c8e6a71fd2c`; operator-local profile,
1779 projection receipt, current references and refreshed knowledge dates align.
The Phase 5 roadmap/status now agree on `IN_PROGRESS (0/5)`; the Work Order's
pre-dispatch “no worker” note is explicitly historical. Catalog verify PASS,
Project Knowledge PASS, inheritance/closeability 0/0; workspace doctor PASS WITH
NOTE (24 pass, two bounded legacy warnings). No product tests were rerun.

Consumed accepted evidence: worker 25/48 focused results and root 7 independent
oracles; evidence and return artifacts preserve their actual limits. Pure supplied
history/numeric portions of G03-G05/G08-G10/G13 are accepted within H1-P2. All 14
integrated P5-A2 criteria remain open with remainder owners/destinations in the
Product Milestone Binding; P5-B/C/D remain open. No provider or AI-governance
behavior proof is claimed. Tranche source acceptance is bounded; normal material
full hook/commit and actual-SHA continuity remain pending. After that, return to
bounded G04-G06 scoped-history verification; no P5-A2 or Phase 5 closure is implied.
