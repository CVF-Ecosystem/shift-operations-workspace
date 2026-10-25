# P5-A2 scoped source PostgreSQL — independent planning review

docType: completion_review
Status: AUTHORIZATION_REVIEW_PASS_BOUNDED
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

## Return-Time Closeability Recheck

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
