# P5-A2 scoped source PostgreSQL — independent planning review

docType: completion_review
Status: EFFECT_AUTHORIZATION_PASS_BOUNDED
Date: 2026-10-26
Reviewer: independent REVIEWER; no SPEC, oracle, Work Order, harness or effect ownership

## Initial pre-dispatch decision (superseded by rereview below)

`CHANGES_REQUIRED_BOUNDED`. The source Work Order is not yet authorized for
dispatch, and the effect Work Order remains DRAFT/HELD. The accepted Stage A
source and prior PostgreSQL substrate evidence support one *new* synthetic
physical experiment after a corrected source packet, source review, sealed
effect admission, normal commits and dedicated actual-SHA continuity. The old
physical ceiling is spent; this packet proposes a separate finite attempt.

| Finding | Evidence | Finite correction before source dispatch |
|---|---|---|
| PG-PLAN-F1 — unfrozen physical case context | The new pre-harness oracle raw SHA256 `5a6a2e28c07e1cec20a6a009f329cdda5f2ad124e85c4d79c25835973310404b` freezes six cap sizes/outcomes and four race reason classes, but none of its cap/race cases records actor, scope, instance, query window, as-of or policy pair. The SPEC claims these are explicit in the oracle. Its recipe says “Separate PUBLIC actor per case,” while both inherited full source-oracle receipts require exact `PUBLIC_ACTOR`/`PUBLIC_SCOPE`/`PUBLIC-SOURCE-INSTANCE-1` and their fixed windows. A worker could choose those identifiers and timings during BUILD and generate matching expectations from its new fixture helper. | Freeze a concrete baseline-context reference to the existing full oracle and exact deterministic context/mutation inputs for each disjoint cap/race/negative case (actor/scope/instance/window/as-of/policies and relevant assignment/shift/report IDs, versions and changed values). Distinguish the two inherited full-receipt cases from separately named auxiliary actors. Keep expected source receipts tied to the already frozen `0f79676b...` oracle; the additional case oracle may use compact deterministic seed inputs and expected counts/reasons rather than duplicating 500 bodies. Recompute the new oracle raw pin and synchronize SPEC, both WOs, admission sourcePins and continuity before independent rereview. |
| PG-PLAN-F2 — cached-image-only boundary is not enforced by inherited creation helper | The packet forbids image pulls and says to reuse old lifecycle helpers unchanged. `base.start_container()` calls `base.docker_run_cmd()`, which invokes `docker run ... postgres:16-alpine` without `--pull=never`; Docker can acquire the tag if it is missing between inspect and run. Prohibiting `base.ensure_image()` alone does not enforce zero pulls. | Require the new runner to start only the exact inspected cached image with Docker `--pull=never` (or equivalent no-pull creation bound to the pinned image ID), with an inert unit assertion on the actual create command. It may reuse the old readiness/migration/owned-cleanup helpers; do not modify the old runners. If the pinned image is absent or changes, spend/record the attempt and stop without pull or retry. Record actual container image identity and preserve the one-owned-container cleanup fence. |

## Authority, invariant and product boundary assessed

The source WO names exactly one runner, two fixture/probe helpers, one opt-in
live target, one inert runner test and a worker return, each executable <=300
lines. Its active closeability graph passes the installed pinned Core guard.
The effect WO is DRAFT and the admission JSON is `PLANNING_NO_EFFECT` with empty
`harnessPins`; the native checker correctly reports that the DRAFT closeability
contract was not checked. Thus no Docker, install, pull, provider or credential
action is released. Source BUILD requires independent authorization, a normal
dispatch commit and dedicated actual-SHA continuity. After independent source
review, Root must seal the exact harness hashes and effect budget, obtain
independent effect authorization, commit source plus admission through normal
hooks, review the actual commit, then commit dedicated actual-SHA continuity
and verify the clean range before the one physical invocation. The effect WO's
generic `DISPATCH_COMMIT` graph can refer to that same sealed source/admission
commit while the source WO calls it `MATERIAL_COMMIT`; Root should record that
cross-WO interpretation at sealing so no extra or skipped authority step is
inferred. Result evidence, owned cleanup, independent review and normal
result/continuity commits remain separate after the one spent attempt.

The no-new-family applicability decision is coherent for this planning
packet: actual READY/REFUSED remain governed by the registered
`P5A2-SCOPED-SOURCE-OUTCOMES` matrix canonical digest `9b3ba818...`; the
runner summary and immutable attempt marker are evidence-only, with no new
shared product receipt or mutable state grammar. This acceptance is limited
to that representation. A new outcome-controlled shared result contract
during BUILD would require its own reviewed family decision. The existing
native emitter/validator and 84-mutation corpus remain required. Static
matrix checks do not prove physical SQL or AI governance.

The admission JSON's 15 inherited source pins match current files; the new
PG oracle raw pin matches its file and links frozen source oracle
`0f79676b...` and old body oracle `12ad36cb...`. The old Docker runner's
cached image inspection, minimal child environment, sanitization, loopback,
migrations and owned container/anonymous-volume cleanup are reusable facts,
but its old 36/37 target seeds shifts/reports without ACTIVE assignments and
never invokes the new native query. The Stage B target must seed those
assignments and prove both full receipts, real 500/501 SQL caps before bodies,
transaction isolation/read-only, a separate fresh view with committed writer
races, denial/foreign exclusion and closed refusals under the new oracle. No
physical run was made for this review.

P5-A2's user outcome remains integrated authorized scheduled forecasts,
history, freshness and exact human approval before durable action. This slice
can advance only physical fixture G04–G06 and partial G13. G01/A7 and G02
remain blocked; G03 business fit, G05 production retention/coverage, G06 API
identity/use-time access, G07 scheduler, G08–G10 operational quality, G11
API/UI, G12 approval and G13 runtime drills remain open/unknown; G14 provider
proof is held. Root/backend, independent reviewer, UI roadmap owner and
operator retain the named P5-A2 and P5-B/C/D destinations in the accepted
source SPEC/roadmap. Phase 5 remains 0/5. No production, real-provider or
whole-milestone claim follows from a synthetic PostgreSQL rehearsal.

Ordinary pinned-Core closeability, session and invariant-family guards passed.
This was read-only packet review; no broad test suite or external effect ran.

## Planning-stage closeability history

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: YES

## Independent planning repair 1 rereview — current decision

`AUTHORIZATION_REVIEW_PASS_BOUNDED`; PG-PLAN-F1 and PG-PLAN-F2 are resolved,
with no open source-dispatch finding or waiver. The original findings above
remain as review history. This PASS authorizes only Root's normal source
dispatch commit and dedicated actual-dispatch-SHA continuity. It does not
activate the DRAFT effect WO or allow Docker, provider, install or image pull.

The revised pre-harness PG oracle raw SHA256 is
`0b69156fcb09a6b65a25c437320a5f4001f4068284d5bcf8b88438700a92f44f`.
Its two baseline contexts exactly retain the inherited source-oracle
`PUBLIC_ACTOR`/`PUBLIC_SCOPE`/`PUBLIC-SOURCE-INSTANCE-1`, aware windows,
as-of instants and policy pair. All six cap cases, four race cases, three
negative cases and the RR snapshot case now have explicit actor, scope,
instance, fixture, window, as-of and policy context. The race cases also
freeze the changed status/version/shift-time or added member. Auxiliary
actors are distinct; the foreign actor shares the baseline time window to
test the authorization filter. The compact case oracle freezes inputs,
counts, reasons and pre-body expectations while the old `0f79676b...` source
oracle retains both complete ready receipts. Admission `sourcePins` now lists
38 inherited and new paths with no hash mismatch; its `harnessPins` remains
empty and status remains `PLANNING_NO_EFFECT`.

The revised SPEC and source WO require Docker creation with `--pull=never`
and the exact admitted cached image ID, not a mutable image tag; the new
runner's inert unit test must assert the actual create command. The old
base runner remains read-only. A missing or changed cached image stops the
single spent attempt without acquisition or retry. The admission JSON records
this creation policy. Root also records that one eventual sealed source/
effect-admission commit serves as source `MATERIAL_COMMIT` and effect
`DISPATCH_COMMIT`, followed by the dedicated actual-SHA continuity and clean
range before effect. Effect review and seal still require a separate decision
after implementation source review; the effect WO's DRAFT closeability graph
has not been machine-enforced and confers no effect authority.

No-new-family applicability remains accepted under the existing native
`P5A2-SCOPED-SOURCE-OUTCOMES` matrix `9b3ba818...`: the new experiment
adds evidence and an immutable attempt reservation, not a second business
receipt or mutable outcome grammar. The complete P5-A2 G01–G14 remainder,
owners and P5-A2/P5-B/C/D destinations above remain current, with only
physical synthetic G04–G06/partial G13 selected and Phase 5 still 0/5.
Ordinary pinned-Core closeability, session and invariant-family guards pass.
No physical PostgreSQL, Docker, provider, install or network effect occurred
in this rereview.

## Independent inert source review — current decision

`SOURCE_REVIEW_CHANGES_REQUIRED_BOUNDED`. The planning authorization and actual
dispatch/continuity remain valid; the five-file harness is not yet accepted for
source/effect sealing. The effect Work Order remains DRAFT and admission remains
`PLANNING_NO_EFFECT` with empty `harnessPins`. No physical invocation is allowed.
All corrections fit the existing five harness paths and their inert tests; the
frozen Stage A source, 38 inherited pins, PG/source/body oracles and family
matrix require no change.

| Finding | Independent evidence | Finite correction and proof |
|---|---|---|
| PG-SRC-F1 — second golden baseline is guaranteed to refuse | `seed_baseline()` constructs one `ExpectedFixture` from `baselineContexts[0]`, and `_baseline()` passes it to both queries. Pure reconstruction from unchanged `public_ledger()` gives case 0 seed 36 candidates at `2026-01-02T12:00:00Z`, while case 1 requires 37 at `2026-01-02T14:00:00Z`. Independently constructing a verifier from context 1 matches the second frozen source-oracle `coverage_seed`; reusing context 0 does not. `ExpectedFixture.verify()` therefore raises `SCOPE_INCOMPLETE` on the later query before either asserted ready result. | Derive one independent verifier per frozen baseline context from the same pre-query seed inputs. Inertly assert **both** context seeds and digests equal their corresponding complete old oracle cases, then exercise both in `_baseline()`. |
| PG-SRC-F2 — seal and child ownership fences are incomplete | `sealed_admission()` searches for `Status: APPROVED_FOR_EXECUTION` anywhere in the effect WO text, so an explanatory paragraph can satisfy it while the top-level status remains DRAFT. It checks a clean current tree and 38 pins but never enforces the SPEC's baseline `8dc39e1` protected-diff rule; it also leaves several finite admission fields and the fixed attempt/observation paths unchecked. `_owned_context()` compares nonce/name/image/host-port from marker and environment plus Docker ID/image, but does not prove the inspected container's actual `127.0.0.1:<host_port>:5432` mapping; replay/direct-target context is not tied to the single runner target invocation. | Require exact standalone active effect status, fixed baseline and permitted changed-set/path/effect-budget fields before reservation. In the runner and child, verify actual Docker port binding and strengthen the owned one-target context/marker fence against stale or direct replay. Add inert negative probes for draft text containing the approval phrase, protected baseline drift, altered admission/path, wrong mapping and replay. Do not add general Docker or network access. |
| PG-SRC-F3 — failed invocation can evade the spent record, and partial evidence is not durable | `main()` checks the driver and Docker daemon before `_reserve()`. A failed prerequisite exits without the immutable marker, although the one wrapper invocation is spent under the SPEC. Failures after reservation are returned only via process stdout; `run_once()` never writes the authorized evidence JSON, so a failed/uncertain cleanup has no guaranteed retained partial result beyond the marker. | Once sealed admission passes, reserve before the invocation's remaining prerequisites. Preserve one marker on every later failure and retain sanitized partial result in the exact authorized evidence path, or make the Root effect command's capture into that path a reviewed, mandatory part of the sealed packet. Inertly prove prerequisite failure, child failure, uncertain cleanup and replay all retain spent state and nonsecret partial evidence. |
| PG-SRC-F4 — physical observation assertions have gaps that would consume the only run | `repeatable_read_probe()` and `race_query()` infer a *new* transaction from unequal snapshot text; two fresh transactions without an intervening write may have the same snapshot. The race writer uses the reader engine after its source unit closes, so its asserted PID difference depends on pool reuse. The reportless case checks only the fixture seed's enrolled count, not the native observed cohort/candidate counts. Baseline trace asserts source stage PID/snapshot but does not record an explicit distinct fresh transaction boundary when no writer intervenes. | Make writer backend distinct by construction while keeping committed writer/barrier semantics; observe a separate transaction boundary directly without requiring different snapshot text where none is guaranteed. Record native reportless cohort=1/candidates=0 before refusal, and keep exact 500/501 zero-body, foreign exclusion, full receipts, closed refusal and four mutation assertions. Add inert trace/fixture probes for these conditions before burning the single physical attempt. |

The worker return raw SHA-256 is `e1125095dd9b200b40e444de8da15312f706e394e8066dc38d1f2517875ab221`;
its five declared source hashes match the actual files, and all 38 admission
source pins match. The frozen PG oracle remains `0b69156f...`, source oracle
`0f79676b...`, body oracle `12ad36cb...` and source family `9b3ba818...`.
Independent focused inert run of the two new test paths, four existing source
paths and two generic family paths returned **101 passed, 3 skipped**; the
physical target was skipped without owned context. This supports safe inert
collection, not the unrun PostgreSQL claims. Pinned Core and invariant-family
guards passed, and native `check_recheck` of the worker return returned `[]`.
No Docker, database, provider, network, image pull or install was invoked.

The accepted P5-A2 Product Milestone Binding remains unchanged: only synthetic
physical G04–G06 and partial G13 are selected. G01/A7/G02 remain blocked;
G03 business fit, G05 operational retention/coverage, G06 API/use-time
authorization, G07 scheduler, G08–G10 operational quality, G11 API/UI, G12
human approval and G13 runtime drills remain open/unknown; G14 provider proof
is held. Root/backend, independent reviewer, UI roadmap owner and operator
retain the P5-A2/P5-B/C/D destinations in the SPEC. Phase 5 remains 0/5.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: YES

## Independent inert source repair 1 rereview — current decision

`SOURCE_REVIEW_PASS_BOUNDED`. PG-SRC-F1–F4 are resolved within the original five
harness paths; the initial findings above remain as review history. This PASS
permits Root to prepare exact five-hash source/effect sealing and a **separate**
independent effect admission review. It does not activate the DRAFT effect Work
Order or authorize Docker, PostgreSQL, a provider call, image pull or install.

- F1: `baseline_expectations()` independently constructs and checks both old
  oracle coverage seeds/digests before SQL, with 36 candidates at the first
  as-of and 37 at the later as-of. `_baseline()` uses the matching verifier for
  each complete frozen receipt.
- F2: the runner requires the standalone active effect status, exact baseline,
  fixed finite admission fields/paths, canonical 38-pin set and hashes, clean
  worktree and a Git changed set confined to the admitted paths. Parent and
  child verify the actual Docker loopback port binding; the child atomically
  claims its one target observation before database work, so replay fails.
- F3: after successful seal validation, the immutable attempt is reserved
  before driver/daemon prerequisites. Every subsequent result is written as
  sanitized partial or complete evidence to the fixed exact path; failure
  retains the spent marker. Inert negatives cover prerequisite failure and
  duplicate reservation.
- F4: source/fresh transaction objects are retained and compared directly;
  identical snapshot text alone is no longer treated as the transaction
  boundary. A separately constructed writer engine supplies a distinct
  backend for the committed races. The reportless probe observes one native
  enrolled cohort member and zero candidates before its closed refusal.

The current worker return raw SHA-256 is
`2b6d0845980aa64d56322416a3a384682f83996bdd4e3ada4ac47956772dcefa`.
Its five declared file hashes and line counts match the actual files (all
under 300 lines); all 38 inherited source pins match, with canonical pin-set
digest `57e2855582dc88e2d72d69e3b6dd396ac61513a414868efa219a04ce85dce62a`.
The frozen PG oracle remains raw `0b69156f...`, and the old source/body
oracles and source family remain at `0f79676b...`/`12ad36cb...`/`9b3ba818...`.
Independent exact inert corpus (new unit, safe live collection, four existing
source tests and two generic family tests): **107 passed, 3 skipped** in
18.07 s. Pinned Core guard, invariant-family guard, native worker-return
`check_recheck` and diff check passed. The physical target remains unrun; no
claim of actual PostgreSQL outcome, cleanup, production coverage, API
authorization, scheduler, approval or AI governance follows.

Product binding stays at only synthetic physical G04–G06/partial G13;
G01/A7/G02 remain blocked, G03/G05 production retention/G06 API-use-time/G07/
G08–G13 operational product gaps remain open or unknown, G14 provider proof
held. Root/backend, independent reviewer, UI owner and operator retain the
P5-A2/P5-B/C/D destinations in the SPEC. Phase 5 remains 0/5.

## Independent sealed effect admission review — current decision

`EFFECT_AUTHORIZATION_PASS_BOUNDED`. No new source finding or waiver. The
source review above remains accepted. The admission is `SOURCE_REVIEWED`,
names the fixed baseline `8dc39e1`, and has exactly 38 inherited and five
reviewed harness pins; all 43 raw file digests match. Its protected 38-pin-set
digest matches the runner's frozen digest, and the PG oracle remains raw
`0b69156f...`. The attempt, ignored observation and fixed evidence JSON do
not exist yet. The candidate changed paths are within the runner's exact
permitted baseline set; the committed dispatch range is a 16-path subset.

The effect Work Order has the standalone `APPROVED_FOR_EXECUTION` candidate
status and an active closeability graph; the source Work Order records
`IMPLEMENTED_BOUNDED` and no further worker authority. The effect order now
names the single exact command
`.venv/Scripts/python.exe scripts/run_p5a2_scoped_source_postgres.py --json`.
The executable exists. The runner is pinned, requires a clean committed tree,
strict active effect status, unchanged admission fields/pins, the cached exact
image ID and driver version, and spends the O_EXCL marker before remaining
prerequisites. It creates with `--pull=never` and the image ID, allows only
one target/owned container on dynamic loopback, retains sanitized partial
result at the fixed evidence path, and treats uncertain owned cleanup as
failure. No generic direct URL/target/force command or retry is authorized.

This PASS authorizes Root's **normal joint source MATERIAL / effect DISPATCH
commit only**. Independent review of the actual committed range, dedicated
five-path actual-SHA continuity and clean split-range verification remain
mandatory before the one physical invocation. Its result and named container/
volume cleanup require a separate independent review, result material commit
and continuity. This review did not invoke Docker, connect to PostgreSQL,
acquire an image/package, use credentials, call a provider or rerun the full
suite. Pinned Core active effect guard and invariant-family guard passed; the
source WO's inactive-status notice is explicitly reported by the guard.

The full P5-A2 milestone binding remains as recorded above and in the Stage B
SPEC: this can close only synthetic physical portions G04–G06 and partial G13
after a real result. G01/A7/G02 are blocked, G14 is held, all other
operational, retention, API/use-time, scheduler, quality, UI and approval gaps
remain open/unknown with Root/backend/UI/operator owners and P5-A2/P5-B/C/D
destinations. Phase 5 remains 0/5.
