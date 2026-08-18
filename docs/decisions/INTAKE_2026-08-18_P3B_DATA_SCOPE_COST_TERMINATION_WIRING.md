# INTAKE - P3-B Wire data_scope/cost/termination Into a Real Call Site

- Tranche: `P3B-GATE-WIRING-2026-08-18`
- Execution base: `da85889`
- Parent closure: SOPR-CP1 core-pin reconciliation `CLOSED_BOUNDED /
  REVIEWER_ACCEPTED`; P4-A1 governed retrieval `CLOSED_BOUNDED` at reviewed
  BUILD `4cc0691`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INTAKE_REVIEW`
- Active roles: `ORCHESTRATOR`, `INTAKE_AUTHOR`
- Provider/product-API/POST calls: `0/0/0`
- Runtime, database and source changes: `NONE`
- Operator direction: continue the roadmap; this INTAKE targets the sole
  remaining open item in Phase 3 (`5/6` -> `6/6`)

## Request and roadmap position

`docs/implementation/EXECUTION_ROADMAP.md:426-427` names P3-B as: "Wire các
gate data_scope/cost/termination vào một điểm gọi thật (khi Phase 4 AI bật) —
hết trạng thái 'AI-gated only'." This is the only unchecked item in Phase 3
(`PARTIAL 5/6`). The session's `next_allowed_move`
(`SESSION/ACTIVE_SESSION_STATE.json`) parks all downstream lanes pending fresh
authority; the operator has now granted that authority for this specific
INTAKE only.

## Current implementation truth

| Current fact | Verified source | Consequence for P3-B |
|---|---|---|
| `data_scope`, `cost` (budget), and `termination` gates are fully implemented and unit-tested, each documented as "runs and is tested now; becomes load-bearing when an AI mode beyond NO_AI is enabled." | `packages/cvf-runtime/src/cvf_runtime/data_scope.py:14-16`, `budget.py:6-8`, `termination.py:6-7` | The gate logic itself needs no new implementation. The gap is entirely the absence of a caller. |
| `ai-gateway` (the roadmap's own P4-A owner for "model router, context builder... calls cvf-runtime gates") contains only READMEs and one provider-neutral contract (`ProviderInterface` with `generate_structured_output`/`health_check`/`cancel_request`); zero implementation, zero caller. | `packages/ai-gateway/**` (13 files, 12 are bare `README.md`); `packages/ai-gateway/contracts/provider_interface.py:20-22` | There is no real outbound-AI call site anywhere in this repository today. P4-A is `[ ]` NOT STARTED in the roadmap. |
| P4-A1 governed retrieval (`governed-retrieval` package) is explicitly local/deterministic/provider-free; its own INTAKE recorded the identical P3-B dependency map and concluded "this dependency map does not close P3-B. P3-B remains open until a later authorized real call site invokes the controls." | `docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md:157-170`; `packages/governed-retrieval/src/governed_retrieval/**` (no provider import) | P3-B cannot reuse P4-A1 as its real call site; P4-A1 was designed specifically to avoid becoming one. |
| Canonical operational records fail closed with `SOURCE_DIGEST_OWNER_MISSING` in the retrieval-ready contract layer. | `packages/retrieval-contracts/src/retrieval_contracts/constructor.py:182` | Even if a caller existed, most canonical record types could not reach it yet — a second, independent blocker upstream of P3-B. |
| `data_scope.assert_placement_allowed` requires a `classification` and a `placement` (`external`/`enterprise`/`local`) that only make sense at the moment content is about to leave the process boundary toward a provider. | `packages/cvf-runtime/src/cvf_runtime/data_scope.py:37-66` | Any call site must sit immediately before an outbound provider call, not inside retrieval, storage, or UI code. |
| `budget.assert_within_budget` consumes `BudgetState` "supplied by the caller (e.g. from a usage ledger)" and `termination.assert_not_terminated` consumes `TaskState` describing an in-flight task's elapsed time/tokens/failures. | `budget.py:19-24`; `termination.py:17-28` | Both gates assume a running AI task with real usage/timing data. No such task exists in this codebase; synthesizing fake `BudgetState`/`TaskState` would not be a real call site, only a test double dressed as one. |
| Existing CVF gates that *do* have real callers (`domain_lock`, `risk`, `approval`, `evidence`, `audit`) are invoked from application services (e.g. `ShiftService`, `TaskService`) inside `apps/workspace-api`, not from `packages/cvf-runtime` itself. | `docs/implementation/EXECUTION_ROADMAP.md` P-FIX/P2-A sections; `packages/cvf-runtime` README pattern | The project's own precedent is: gates live in `cvf-runtime`, callers live in application services that perform the governed action. There is no application service yet that performs an AI action. |

## Problem statement

P3-B asks to remove the "AI-gated only" qualifier from three controls by
wiring them into a real call site. But no real call site exists in this
codebase: `ai-gateway` is scaffold, P4-A1 governed retrieval was deliberately
built provider-free, and P4-A (the roadmap's own designated owner of "model
router, context builder... calls cvf-runtime gates") is `NOT STARTED`.

Two ways to fail this INTAKE quietly:

- accept a synthetic/test-only caller as "a real call site" and mark P3-B
  `CLOSED_BOUNDED`, which would misrepresent the gates as load-bearing when no
  actual AI action depends on them;
- build a minimal AI Gateway scoped as "just enough to close P3-B," which
  would silently open Phase 4 (P4-A) without its own INTAKE/DESIGN/SPEC/
  WORK_ORDER chain, provider credentials, and live-governance-evidence
  obligations (`AGENTS.md` Mandatory Governance Proof: any claim of CVF
  governing AI behavior "must use a real provider API call").

## Proposed bounded objective for this INTAKE

This INTAKE does not authorize implementation. It exists to reach one of two
honest dispositions:

**Option A — DESIGN a minimal real call site scoped as P4-A's first bounded
slice**, explicitly opening Phase 4 (not just P3-B), with:

1. one governed application service that performs a single, narrow AI action
   (e.g., a NO_AI/RULES_ONLY-first "structured suggestion" endpoint per
   `ai-providers` roadmap ordering: "NO_AI, RULES_ONLY, mock trước");
2. `data_scope.assert_placement_allowed` called immediately before any
   placement decision, using real classification from confirmed operational
   records (not a synthetic value);
3. `budget.assert_within_budget` called with a real `BudgetState` sourced
   from an actual usage ledger (new, minimal, append-only);
4. `termination.assert_not_terminated` called across the real task's
   execution, with evidence preservation on termination;
5. live governance evidence per `AGENTS.md`: a real provider API call (or an
   explicit `NO_AI` mode proof that still exercises the three gates against
   a real — not mocked — decision path) recorded in the evidence artifact;
6. explicit non-goals: no RAG, no P4-A2, no multi-provider routing, no
   production deployment.

**Option B — record P3-B as blocked-not-closeable** until P4-A DESIGN opens
on its own authority, and remove it from being treated as a standalone
closeable roadmap line item; update the roadmap and session state to say so
explicitly instead of leaving it as an apparently-independent `[ ]` that
implies it can close without touching Phase 4.

Independent review at DESIGN must choose between A and B; INTAKE does not
pre-decide it, because Option A has real scope/cost/authority consequences
(it opens Phase 4 AI Gateway work under a Phase-3-labeled tranche) that this
project's governance treats as a boundary change requiring explicit
escalation (`AGENTS.md` "Escalate only at a real boundary change: objective
or acceptance contract... provider or network use").

## Hard boundaries

This INTAKE authorizes no implementation. Regardless of which option DESIGN
selects, this tranche must not:

- call an LLM, provider, network service, product API, POST route or browser;
- add provider credentials, models, or deployment configuration;
- implement P4-A2, RAG, embeddings, reranking, vector search, or learning;
- treat a synthetic/mocked `BudgetState`/`TaskState`/classification as
  sufficient evidence that a gate is load-bearing;
- mutate, confirm, correct, approve, close or freeze operational truth;
- claim P3-B `CLOSED_BOUNDED` without fresh live governance evidence per
  `AGENTS.md` Mandatory Governance Proof.

## Cheap-alternative inventory

| Alternative | Default disposition | Reason |
|---|---|---|
| Reuse `governed-retrieval` as the call site by adding a provider call to it. | `REJECT` | Its INTAKE explicitly scoped it provider-free; retrofitting a provider call there violates its own closed claim boundary and would require reopening a `CLOSED_BOUNDED` tranche. |
| Build a synthetic internal "AI task simulator" purely to exercise the three gates. | `REJECT` | Not a real call site; would let P3-B claim load-bearing status without a genuine AI action depending on it — the exact over-claim pattern P-FIX-0/P-FIX-5 were created to stop. |
| Open a minimal P4-A slice (Option A above) scoped to the smallest real AI action. | `PREFER_IF_DESIGN_ACCEPTS_SCOPE_EXPANSION` | Only path that makes the gates genuinely load-bearing; must be explicit that it opens Phase 4, not just Phase 3. |
| Leave P3-B recorded as blocked-not-closeable and update roadmap wording (Option B above). | `PREFER_IF_OPERATOR_WANTS_PHASE_4_DEFERRED` | Cheapest, most honest option if Phase 4 AI work is not yet wanted; avoids a governance-document-only tranche that changes nothing runtime-relevant. |

## Decisions required before DESIGN closes

1. **Option A vs Option B** — does this tranche open Phase 4's first bounded
   AI action, or does it stop at correcting the roadmap's claim boundary?
2. If Option A: which single AI action is smallest and lowest-risk (roadmap
   favors `NO_AI`/`RULES_ONLY`/mock-provider-first ordering under `P4-B`)?
3. If Option A: where does the new minimal usage ledger live, and does it
   reuse `operations-ledger` patterns or need a new package?
4. If Option A: what live governance evidence satisfies `AGENTS.md` for a
   `NO_AI`/`RULES_ONLY` path where no real provider call is possible by
   design — is a real provider call still required, or does the mandatory
   governance proof rule only bite once a provider mode is enabled?
5. If Option B: exact wording change to
   `docs/implementation/EXECUTION_ROADMAP.md` and `SESSION/ACTIVE_SESSION_STATE.json`
   so P3-B no longer reads as an independently closeable Phase-3 checkbox.

## Acceptance criteria for this INTAKE

INTAKE is acceptable only if independent review confirms:

- the request matches P3-B's exact roadmap wording and cites its source line;
- the absence of any real call site in the current codebase is verified
  against `packages/ai-gateway`, `packages/governed-retrieval`, and the
  P4-A1 INTAKE's own P3-B dependency-map disclaimer;
- the INTAKE does not pre-select Option A or B — it leaves that choice to
  DESIGN with the tradeoffs stated;
- no implementation, provider credential, or live evidence claim is made;
- the boundary-escalation consequence of Option A (opening Phase 4 under a
  Phase-3 tranche) is explicit, not silently absorbed.

## Governance cost and latency controls

- One consolidated INTAKE review must report all foreseeable boundary and
  source findings in one pass.
- Same-scope corrections remain under this INTAKE review authority.
- At repair round three without a new independent root cause, stop with
  `REVIEW_COST_ESCALATION_REQUIRED`.
- No test matrix, provider budget, deployment lane or implementation path set
  opens before DESIGN is accepted.

## Risk and evidence posture

`R2` is retained: while this INTAKE itself makes no runtime change, its
DESIGN decision (Option A) directly controls whether/how INTERNAL operational
data may later reach an external provider placement. This INTAKE needs no
provider, network, database, runtime or product API call.

## Stop conditions

Stop and return to the orchestrator if review finds:

- a real call site already exists elsewhere in the codebase that this INTAKE
  missed (would change the problem statement entirely);
- Option A's minimal AI action cannot be scoped below P4-A2/RAG complexity;
- the live-governance-evidence question (decision 4 above) cannot be resolved
  without contradicting `AGENTS.md`;
- continuity, project/core boundary or classification evidence drifts.

These are DESIGN blockers, not permission to widen this tranche.

## Independent review contract

The next role is `INDEPENDENT_INTAKE_REVIEWER`. Review this artifact against
the cited project source, active handoff and roadmap. Preserve disagreements
and return exactly one disposition:

- `INTAKE_REVIEW_PASS`
- `INTAKE_REVIEW_CHANGES_REQUIRED`
- `INTAKE_BLOCKED_SOURCE_OR_OWNER`

The reviewer may perform local read-only source checks. The reviewer may not
design, implement, call providers/network/product APIs, modify the database,
stage, commit, push or infer later-phase authority.

## Claim boundary

This artifact only bounds P3-B INTAKE. It does not prove a real call site
exists, that any gate is load-bearing, that Phase 4 is open, or that P3-B is
closer to `CLOSED_BOUNDED`. It documents that P3-B as literally worded cannot
close without either opening Phase 4 (Option A) or being re-worded to no
longer imply independent closeability (Option B).

## Next governed move

Obtain one consolidated independent INTAKE review. Only
`INTAKE_REVIEW_PASS` may transfer the Option A/B decision packet to
`DESIGN_AUTHOR`. No DESIGN drafting, source change, provider/network/product
API call, database change, staging, commit of later-phase artifacts or BUILD
is authorized by this INTAKE alone.
