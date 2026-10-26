# P5-A2 G04/G05 source and coverage — intake/design

Status: DESIGN_COMPLETE_STAGE_A_ADMISSION_PENDING
Date2026-10-26; baseline674d98e35f0fbafa868c34d3c3adbdd215ef3aa5; R2.
Root ORCHESTRATOR/SPEC_AUTHOR; DESIGN only, no runtime BUILD/effect admission.

## Product Milestone Binding

P5-A2 at docs/implementation/EXECUTION_ROADMAP.md Phase5. Complete user outcome:
integrated authorized scheduled signals/forecasts/history/lineage/freshness/
uncertainty/abstention, followed by exact human run/version/source approval
before durable recommendation/action. Full acceptance remains parent proactive
SPEC; operator owns business acceptance. Root accountable/contracts/effects/
commit, backend worker implementation, independent reviewer acceptance,
UI owner/operator application/business remainders.

| Gap | Current truth and remaining work | This slice / owner / destination |
|---|---|---|
| G01/A7 | One provider401 spent; A7 acceptance BLOCKED | NO; Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | NO; backend/Root, P5-A2 context |
| G03 | Pure numerical policy accepted; business fit open | NO; backend/operator, P5-A2 method |
| G04 | Native fixture memory/PG source accepted; operational integration open | YES finite source/coverage DESIGN; implementation/effects not yet authorized, backend/Root, P5-A2 source |
| G05 | Fixture coverage accepted; production mode/authority/retention/SQLite positive UNKNOWN | YES identify synthetic authority contract and operational unknowns; backend/Root/operator, P5-A2 coverage |
| G06 | Native and bounded HTTP identity/fresh-release source accepted; later use/approval access open | NO; accepted source slice inherited, later use-time backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery open | NO; backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational quality open | NO; backend/operator, P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy open | NO; backend/operator, P5-A2 forecasting |
| G10 | Pure residual/drift accepted; monitoring/display open | NO; backend/UI/Root, P5-A2 quality/P5-B |
| G11 | Bounded source API and manual source UI accepted; other integrated flows open | NO new UI implementation; remaining application owner UI/Root, P5-A2 application |
| G12 | Exact human approval open | NO; backend/UI/operator, P5-A2 approval |
| G13 | Native fixture failures accepted; integrated drills open | NO new HTTP behavior; source UI stale/session drills only, integrated remainder backend/Root P5-A2 drills |
| G14 | Live AI-governance proof HELD | NO; Root/operator, separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability: backend/UI/Root; P5-C backup/resilience/
security/performance: backend/Root/operator; P5-D deployment/Shadow Mode/release:
Root/operator. Phase5 stays0/5; no whole milestone or entire gap closes here.



This assignment is finite verification and DESIGN for G04/G05: establish which
existing repository contracts can support a coherent synthetic PostgreSQL source,
what authority would be needed to admit that source at runtime, and which
operational coverage/retention/business facts remain UNKNOWN. Root accountable/
contract/commit, bounded read-only advisory source mapping, independent reviewer
design acceptance; backend/UI/operator remainder owners remain in the table.
No integrated forecasting BUILD may depend on UNKNOWN operational completeness.
Known synthetic source mechanics may support a separately reviewed development
integration without pretending to establish operational truth or accuracy.

Observable next proposed outcome: an isolated local development backend with
known coherent synthetic history, real JWT/native source query and the accepted
source UI clearly labeled synthetic. Mock data is useful for deterministic
calculations, data formats and integration; it cannot establish business forecast
accuracy or complete operational history. Mock provider output remains forbidden
as AI governance evidence. Real-provider A7/G14 checkpoints stay held.

## Inherited accepted evidence / current implementation truth

Source API a141156/355ff938 closed bounded exact36+5; real signed JWT/current
user/action/server self-scope, bounded native query/fresh release, exact source
receipts/84 native and HTTP mutations accepted. One physical synthetic PG16.15
source rehearsal was accepted and its owned resources cleaned; old attempts
are SPENT, no rerun is authorized here. It does not prove a standing backend.
G11 source UI a637e96/674d98e closed bounded exact33+5, frontend145PASS/typecheck/
production build, full84 flat mutations/privacy/session drills. Both normal
UI hooks3397PASS148skip. Known normal source composition defaults to refusal;
no production coverage authority is installed by those accepted tranches.

## Operator intent and bounded next decision

The operator earlier asked for Docker as data backend, directed implementation,
and asked whether mock data could be used. Preserve that intent across tranches;
do not ask routine permission to audit or prepare a concrete solution. Recommend
coherent synthetic data for development while production authority remains
UNKNOWN. This DESIGN does not reuse old one-shot execution budgets. Any new
runtime/physical effect needs its own bounded reviewed Work Order, actual
dispatch/continuity, source admission and lifecycle/effect budget before action.
Assess existing operator authority and actual effect class at that concrete
point; do not infer a global Docker ban from a spent historical attempt.

## Current bounded move / stop condition

Read only relevant source coverage ports, fixture contracts, current settings/
composition, schema/seed tools and existing project Docker artifacts. No Docker
CLI, server, network/provider, package installation, credential/.env read/change,
production data, public release or other runtime effect. Do not inspect private
provenance; installed selected public Core remains the only control binding.
Return one concise recommendation with exact source facts, missing runtime
synthetic authority, proposed smallest path set/evidence/stop condition and
remaining operator-owned operational decisions. Then Root writes a testable
SPEC/WO; no repeated support audit loop or premature implementation claim.

## Decisions pending finite source audit

- Exact data mode, trusted seed/enrollment contract and instance/actor/window/
  policy binding that preserves normal refusal and avoids runtime test-oracle
  imports, client complete flags or unverified history completeness.
- Smallest reproducible development backend configuration and lifecycle,
  local persistence/process/credential handling and owned resource boundary.
- Exact code/contract/evidence paths, necessary invariant-family routing and
  Stage A static implementation versus Stage B physical execution admission.
- Operational source enrollment/retention, business cohort fit/quality and
  provider-backed AI proof remain separate UNKNOWN/HELD remainders.

## Finite audit result / selected development direction

The source facts below were checked against the repository, not inferred from
module status. This completes the finite source map; no further survey is needed.

| Source | Current fact / design implication |
|---|---|
| `apps/workspace-api/src/workspace_api/application/proactive_source.py` | Existing `CoverageVerifier.verify` receives server scope, window/as-of, bounded cohort and candidate metadata after native validation. A frozen metadata descriptor can supply development-only synthetic authority. |
| `apps/workspace-api/src/workspace_api/dependencies.py` | Normal coverage dependency is deliberately None. Preserve this normal refusal. |
| `apps/workspace-api/src/workspace_api/config.py` | Module-level settings read `.env`; a narrow explicit isolated-demo seam is necessary before importing authenticated routes. Never reuse/read the operator's `.env` for this profile. |
| `apps/workspace-api/src/workspace_api/main.py` | Module-level normal application and unrelated composition must remain unchanged. Prefer a separate demo factory using existing real auth and explicit read/source route composition. |
| `docker-compose.yml` | Full stack includes other services, wildcard host ports, `.env` and API image package installation. Do not start or repurpose it for this bounded source demo. |
| `tests/unit/proactive_helpers.py`, scoped/API/PG frozen source oracles | Coherent accepted synthetic history has36 shifts/37 immutable report versions, two as-of contexts and known exact lineage/content metadata. Development inputs and expectations can be frozen independently before new loaders. Runtime must not import these test helpers/oracles. |

Decision: prepare a dedicated PostgreSQL-only local development profile with a
runtime-owned synthetic dataset and metadata authority, fixed server instance/
actor/window/policy and exact candidate digests, real login/JWT and native source
query feeding the accepted UI. Keep production/normal coverage None. No client
complete flag, arbitrary descriptor path or magic operational-complete setting.
Dataset and authority artifacts contain synthetic data and no real credentials.

Synthetic data in a real PostgreSQL instance CAN prove the bounded SQL schema,
snapshot/query mechanics and API/UI data flow actually exercised. A mocked
database/provider response cannot prove that physical integration. Neither
establishes operational completeness, retention or business forecast accuracy.

Prepare an exact testable SPEC/Work Order and independent pre-code dataset,
authority metadata and new server-scope HTTP expectations. Stage A implements
and tests static/runtime composition without physical effects. Stage B requires
separate admitted lifecycle/budget, committed dispatch/continuity and accepted
source before any container, volume, server, seed write or generated local
credential. Use only an already-local approved PostgreSQL image; no pull or
package installation. Bind listeners to loopback, own only new namespaced
resources, preserve unrelated resources and keep volume deletion separate.
The concrete implementation/port/credential/lifecycle decisions are to be
bounded in that SPEC/WO, not silently executed by this DESIGN.

## Design disposition

Finite source audit complete; exact synthetic development contract and Stage A
Work Order now in docs/specs/P5A2_SYNTHETIC_BACKEND_SPEC.md and
docs/work_orders/P5A2_SYNTHETIC_BACKEND_BUILD_WORK_ORDER.md. Independent frozen
36/36/37 dataset, metadata authority, two complete new-scope HTTP expectations
and eight lifecycle shape samples precede code. No physical effect admitted.
Current continuity is the named synthetic-backend successor in SESSION state.
All operational UNKNOWN/G01-G14 remainders and Phase5 0/5 retained.
