# P5-A2 G11 — bounded source-inspection UI

Status: SOURCE_UI_IMPLEMENTATION_CONTRACT
Date2026-10-26; Root SPEC_AUTHOR/WORK_ORDER_AUTHOR; R2.
Baseline355ff938ce3beb532f32c60b7d9780147ed469bc; accepted source API materiala1411561950229b0f8761cab8cfc897afe874f79.

## INTAKE / DESIGN and earliest open stage

Operator requests continued roadmap execution without routine tranche waits.
API closure is inherited bounded evidence, not a full milestone. This tranche
records new UI intent/design/spec and awaits independent WORK_ORDER admission.
No operational completeness, forecast result, approval or durable action is added.

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
| G04 | Native fixture memory/PG source accepted; operational integration open | NO; bounded HTTP composition inherited, operational remainder backend/Root, P5-A2 source |
| G05 | Fixture coverage accepted; production mode/authority/retention/SQLite positive UNKNOWN | Default refusal only; backend/Root/operator, P5-A2 coverage |
| G06 | Native and bounded HTTP identity/fresh-release source accepted; later use/approval access open | NO; accepted source slice inherited, later use-time backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery open | NO; backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational quality open | NO; backend/operator, P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy open | NO; backend/operator, P5-A2 forecasting |
| G10 | Pure residual/drift accepted; monitoring/display open | NO; backend/UI/Root, P5-A2 quality/P5-B |
| G11 | Bounded mounted source route accepted; source inspection UI and all other integrated flows open | YES source caller/rendering only; UI/Root, P5-A2 application |
| G12 | Exact human approval open | NO; backend/UI/operator, P5-A2 approval |
| G13 | Native fixture failures accepted; integrated drills open | NO new HTTP behavior; source UI stale/session drills only, integrated remainder backend/Root P5-A2 drills |
| G14 | Live AI-governance proof HELD | NO; Root/operator, separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability: backend/UI/Root; P5-C backup/resilience/
security/performance: backend/Root/operator; P5-D deployment/Shadow Mode/release:
Root/operator. Phase5 stays0/5; no whole milestone or entire gap closes here.


This assignment: G11 source-inspection caller/rendering and its stale/session
drills only, Root accountable/contract/commit, UI worker implementation,
independent reviewer acceptance. Concrete caller can manually inspect its own
authorized window, see a safe refusal or explicitly synthetic counts, and cannot
retain a prior window/session result. API coverage=None refusal is known; this
UI does not depend on UNKNOWN operational coverage becoming available. Complete
milestone acceptance remains integrated source/context/scheduler/quality/exact
human approval under parent proactive SPEC and operator business acceptance.
Stop at accepted bounded source UI after normal closure; next governed product
move is operational source/coverage design, with real effects separately admitted.

## Acceptance and exact integration contract

Use a source panel after ShiftSelector in OperationsConsole, independent of
selectedShiftId. Manual-only three explicit UTC datetime-local inputs. Never
refresh on mount, shift selection, polling or global refresh; no offline queue.
Empty initial inputs. Parse the local-looking strings explicitly as UTC, reject
invalid calendar dates/ordering locally without echoing server diagnostics.

Use current session helpers and a small source-specific signed-bearer GET
adapter, AbortSignal and fetch no-store. Keep shared api.ts unchanged. Current expected
principal comes from verified auth/me session state; missing identity refuses
locally. Capture token/principal/window per request and recheck all before any
success/error publication. Add subscribeSessionChange to existing session.ts:
new listeners notified on changed token/principal and clear, preserving existing
termination behavior. Source hook subscribes; abort/clear/invalidate immediately
on notification, input/resubmit/termination/unmount. Suppress late completion
even if fetch ignores abort. Never permit a late 401 from an old request to
clear a newer session: source adapter checks captured token/principal before
clearing and throws a canceled result for stale requests. No generic auth or
other route transport behavior changes; no client-side JWT authority invented.

The browser receives authorized raw source receipt fields from the existing
backend. Runtime modules never load or select frozen fixtures; only tests may
import fixture JSON. Normal server coverage remains unknown and refuses.
Validate only the registered flat contract, current actor/window,
integer domains/relations and WebCrypto SHA256 of exact UTF8 canonical_manifest.
Drop raw receipt/private fields before React state. Do not parse or claim deep
backend manifest/lineage semantics; native validator remains its owner. Missing
crypto, unknown/malformed receipt or transport error yields fixed generic safe
unavailable text. No raw exception/detail/IDs/digest/manifest/body in DOM, logs,
local/sessionStorage, serviceworker cache or offlinequeue. Raw request token
handled only via existing authentication helper; no new credential persistence.

Current SOURCE_READY coverage is only SYNTHETIC_FIXTURE, always label 'Dữ liệu
thử nghiệm', show safe counts and submitted UTC times only. SOURCE_REFUSED is
an honest status rather than HTTP failure; all nine reasons have fixed safe
Vietnamese labels. Distinguish loading/idle/auth-required/forbidden/network/
invalid and unknown without displaying arbitrary payload fields. No forecasting
result, report generation/export, approval, durable action or operational claim.

Same P5A2-SCOPED-SOURCE-OUTCOMES family, HTTP_JSON representation already present.
Add real TypeScript digest-bound consumer/test paths plus this SPEC as a contract
source; shapes/domains/relations/mutation rules stay unchanged. TypeScript digest
symbol must be a real valid TS runtime assignment recognized by existing native
static guard (let declaration then bare assignment, exported identifier). Keep
no comments pretending to bind a nonexistent consumer. Root freezes full exact
metadata patch/native LF digest before BUILD; old family stays through dispatch;
real TS files first, then Root exact matrix/three old literal pin updates and
independent materialization before tests. No fake evidence placeholder files.

Root prefreezes compact native84 mutation descriptors from the initial frozen
API READY case and an old frozen refusal before UI code: delete/set diffs,
mutation IDs, shape; tests separately accept both full positive contexts. Retain
baseline family/old API oracle hashes. Independent reviewer recomputes all
descriptors from the matrix and checks unchanged semantic values. TS tests
reconstruct full fixtures, reject54 READY/30 REFUSED, sample both full positives,
all9 refusals, no arbitrary detail, current actor/window. WebCrypto test uses
installed Node builtin crypto; no new packages. Native existing corpus retained.

Exact proposed worker paths (every TS/TSX <=200 lines; tests split upfront):
- apps/workspace-web/src/types/proactiveSource.ts
- apps/workspace-web/src/features/proactive-source/sourceReceipt.ts
- apps/workspace-web/src/services/proactiveSourceApi.ts
- apps/workspace-web/src/features/proactive-source/useProactiveSourceRead.ts
- apps/workspace-web/src/features/proactive-source/ProactiveSourcePanel.tsx
- apps/workspace-web/src/app/OperationsConsole.tsx (mount only,185 ->187)
- apps/workspace-web/src/features/authentication/session.ts (change notification only)
- apps/workspace-web/src/app/styles.css (scoped styles only)
- apps/workspace-web/src/tests/proactiveSourceTestData.ts
- apps/workspace-web/src/tests/proactiveSourceReceipt.test.ts
- apps/workspace-web/src/tests/proactiveSourceApi.test.ts
- apps/workspace-web/src/tests/proactiveSourcePanel.test.tsx
- apps/workspace-web/src/tests/proactiveSourceRaces.test.tsx
- apps/workspace-web/src/tests/proactiveSourceConsole.test.tsx

This explicit small source transport adapter shares existing session helpers
and ApiError types, without taking authentication authority. It avoids changing
the 198-line generic api.ts or its other callers while enforcing conditional
401 cleanup on this source UI path. The session notification extension has
focused listener/unsubscribe/change/nochange tests plus full frontend regression.

Validate installed exact cached Node22.14.0 using process-local PATH only; no
global NVM switch/install/network. Full frontend tests/typecheck/build once,
independent source review with focused meaningful tests then normal full Python
hooks, module-detail/catalog-kit checks, invariant/session/knowledge/size guards,
normal material/actual review/dedicated actual-SHA continuity/clean range.


## Frozen independent input / invariant-family proof

Follow docs/cvf/INVARIANT_FAMILY_STANDARD.md and existing family
P5A2-SCOPED-SOURCE-OUTCOMES. The registered matrix remains the semantic owner;
local render states are not durable business receipts. Root compact mutation
oracle tests/fixtures/p5a2_source_ui_mutations.json rawSHA3afadb388ecd0c70708f1e350bf40ad4c608e7c9b7a150f6663cc20242db27e4 was prepared from old matrix/native mutation
generator and independently frozen API/source oracle before UI code. Its84
descriptors reconstruct full54READY/30REFUSED payloads. Expectations never come
from the UI under test. Admission records complete recoverable exact metadata
patch, rendering recipe and native LF final digest before BUILD. Independent
review verifies all descriptors, full patch and staging, not hashes alone.
