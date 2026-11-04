# CVF Core binding adoption — 2026-11-04

Status: REVIEWER_ACCEPTED_BOUNDED

## INTAKE / DESIGN / SPEC / WORK_ORDER

Operator instruction: “xử lý đi, cho phép”, following the reported mismatch
between the installed public Core and this project's pin. Scope is an explicit
reviewed adoption of the already installed, clean public Core at
`c4c8767ac8861854f40d466ba338ffd11eb9558e`. The previous pin was
`aa672d11910ae1982557e4810a2a8002a611e9e6`. The selected native
closeability checker and standard have no diff between these commits; their
LF SHA-256 pins remain unchanged. Public origin is the declared repository.
No Core checkout, fetch, source modification, product runtime, provider call,
deployment, push or AM4 retry is authorized by this work order.

Risk R2. Roles: ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR →
IMPLEMENTATION_WORKER → independent REVIEWER → SESSION_SYNC_STEWARD →
COMMIT_STEWARD. The minimal bootstrap mutation to the manifest was necessary
to restore the binding preflight; the normal preflight returned COMPLIANT/0
before the remaining project reconciliation.

## Product Milestone Binding

- **Milestone:** P5-A2, `docs/implementation/EXECUTION_ROADMAP.md`, current
  source/review state at `a3bb6d1`.
- **User outcome:** authorized users receive source-linked proactive
  reporting through integrated SQL, API and UI flows, with human control before
  durable action. This milestone remains application level and OPEN.
- **Acceptance:** complete P5-A2 reporting, source, quality, scheduler,
  approval, integration and live provider governance evidence; independent
  review and operator acceptance. Mock output cannot prove AI governance.
- **Current truth:** AM4 SQL read-only snapshots and JWT login passed; the first
  UI request failed before source GET or screenshot. UI acceptance is UNMET,
  attempt SPENT, physical cause UNKNOWN. Phase 5 remains 0/5.
- **This assignment:** unblock the mandatory pinned-Core preflight used for
  finite G04/G05 readiness diagnosis. Allowed paths are the project manifest,
  AGENTS.md installed-pin header, this packet, review,
  continuity/status/index/catalog records and the two current project
  knowledge records `knowledge/PROJECT_CONTEXT.md` and
  `knowledge/manifest.json`. Stop when
  exact Core binding, session/catalog checks and independent review pass.
- **Product return:** restore governed local work eligibility, then return to
  bounded G04/G05 UI readiness diagnosis/planning. No new UI execution authority.

| Gap | Current evidence / limitation | In assignment | Owner / destination |
|---|---|---|---|
| G01/A7 | Provider 401, BLOCKED | NO | Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/citations BLOCKED | NO | Backend/Root, P5-A2 context |
| G03 | Business/cohort fit UNKNOWN | NO | Backend/operator, P5-A2 method |
| G04 | SQL/JWT accepted; UI failed; integration UNKNOWN | Support preflight only | Backend/Root, P5-A2 source |
| G05 | Synthetic coverage accepted; production/authority/retention/SQLite UNKNOWN; UI missing | Support preflight only | Backend/Root/operator, P5-A2 coverage |
| G06 | Later use-time access OPEN | NO | Backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery OPEN | NO | Backend/Root, P5-A2 runtime |
| G08 | Signal quality OPEN | NO | Backend/operator, P5-A2 signals |
| G09 | Forecast accuracy OPEN | NO | Backend/operator, P5-A2 forecasting |
| G10 | Drift display OPEN | NO | Backend/UI/Root, P5-A2 quality and P5-B |
| G11 | Source API/manual UI accepted; panel evidence failed; other flows OPEN | NO | UI/Root/operator, P5-A2 application |
| G12 | Human approval OPEN | NO | Backend/UI/operator, P5-A2 approval |
| G13 | Integrated drills OPEN | NO | Backend/Root, P5-A2 drills and P5-C |
| G14 | Live AI governance proof HELD | NO | Root/operator, separately admitted P5-A2 REVIEW |

## BUILD / REVIEW boundary

The project pin changes to the installed exact Core commit. Historical
receipts retain their historical commit values. Current continuity points to
a new handoff; the existing AM4 return remains immutable. Review checks the
actual Core commit/origin/selected bytes, exact changed paths, preflight,
catalog, knowledge-pack and session consistency, and confirms no milestone
closure claim. The normal hook runs in a credential-free child environment;
this removes ambient `DASHSCOPE_API_KEY` and `ALIBABA_API_KEY` names before pytest while retaining
the mandatory hook and all tests. No credential value is read or recorded.
This is support work with a finite stop condition, not another AM4 attempt.
