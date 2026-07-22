# Agent Handoff — 2026-07-22 (P2-B Authentication Repair — INTAKE)

Provider-neutral handoff. Supersedes
[`AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION.md`](AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION.md)
as the active handoff. That file is **not deleted or rewritten** — it remains
as the historical record of what commit `cd36b27` claims about itself. This
handoff records the operator-initiated correction of that claim.

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P2B-AUTHENTICATION-REPAIR — corrective control-chain tranche
- **Control-chain phase:** REVIEW complete, REVIEW_PASS recorded; blocked
  before FREEZE on live Alibaba governance evidence (see Update below)
- **Risk:** R2 — changes the authentication/security boundary and the
  `identity` CVF control
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=run `scripts/run_identity_live_governance_evidence.py`
  once `ALIBABA_API_KEY` is available and the parallel Alibaba tranche is
  committed, then FREEZE on PASS; parked checkpoint=waiting on that external
  dependency; active role=ORCHESTRATOR

## Why this tranche exists

`cd36b27` ("P2-B: real authentication...") was built, reviewed, and closed
inside a single commit and a single continuous agent session, with no
recorded DESIGN, no discrete testable SPEC, and no operator-approved
WORK_ORDER preceding BUILD. The ADR written in that commit
(`docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md`) documents a
design rationale, but an ADR is not a substitute for a SPEC or a WORK_ORDER
in this project's seven-step control chain (`AGENTS.md`). No role
transitions were recorded during that work, and the "independent review"
performed was a fresh-context agent probing with `TestClient`/local
mocks — real for what it tested, but it does not satisfy this project's
Mandatory Governance Proof rule (`AGENTS.md`), which requires a real
provider API call for any claim that CVF governs identity/security
behavior.

The operator has since directed a corrective tranche, run through the full
INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW → FREEZE chain, to
address both the process violation and a set of real technical findings a
fresh review of `cd36b27` surfaced (see below).

**`cd36b27` is not reverted, rewritten, squashed, or force-pushed.** It
remains on `main` as historical evidence of an unauthorized build candidate.
Everything it changed (JWT bearer tokens, `users` table, `POST /auth/login`,
etc.) still exists in the working tree; only its *governance disposition* is
downgraded, not its code.

## Governance findings recorded at INTAKE

- **G1 — CONTROL_CHAIN_BYPASS / UNAUTHORIZED_BUILD.** P2-B skipped DESIGN,
  SPEC, and WORK_ORDER. ADR + implementation + tests + review claim +
  closure state all landed in one commit with no recorded role transitions
  or explicit authorization of changed set, evidence, stop conditions, or
  commit ownership.
- **G2 — INVALID CLOSURE CLAIM.** Continuity surfaces (`SESSION/SESSION_MEMORY.md`,
  `SESSION/ACTIVE_SESSION_STATE.json`, `IMPLEMENTATION_STATUS.json`, the
  superseded handoff) asserted "P2-B DONE", "identity load-bearing", and
  "BUILD and independent REVIEW complete". These are downgraded by this
  handoff to **REVIEW_CHANGES_REQUIRED — UNAUTHORIZED BUILD CANDIDATE**.
  `docs/cvf/CVF_CONTROL_MAPPING.md`, `docs/catalog/MODULE_REGISTRY.json`, and
  the original ADR still contain the un-downgraded wording as of this
  commit — **deliberately not edited during INTAKE** (see Scope below); their
  correction is T4 in the corrective SPEC/WORK_ORDER, executed only after
  WORK_ORDER approval, not pre-empted here.
- **G3 — MISSING LIVE GOVERNANCE EVIDENCE.** The prior "independent review"
  used `TestClient`/local probes only. It does not satisfy Mandatory
  Governance Proof for the claim "CVF identity is load-bearing" — that
  requires a real provider API call (Alibaba, credential to be supplied
  later by the operator via environment/secret, never pasted into chat).
  Until that live evidence exists and passes, no surface may say
  `REVIEW_PASS`, `FREEZE`, `DONE`, or "identity load-bearing" — only
  `READY_FOR_LIVE_EVIDENCE` once the rest of the corrective tranche is
  otherwise complete.

## Technical findings to carry into SPEC/WORK_ORDER (not fixed at INTAKE)

- **T1** — `jwt_secret_key: str` in `config.py` has no minimum-strength
  validation: a one-character or placeholder secret is accepted and can sign
  a valid `authorized_executive` token.
- **T2** — `LoginInput.password` is unbounded; bcrypt 5.0.0 raises
  `ValueError` (uncaught → HTTP 500) for passwords over 72 UTF-8 bytes, for
  both existing and unknown usernames.
- **T3** — `database/migrations/003_users.sql` is only picked up by
  PostgreSQL on first-time volume initialization
  (`docker-entrypoint-initdb.d` semantics); an existing `postgres_data`
  volume from before this migration will not gain the `users` table, so
  login/seed would fail with "users table does not exist" against a real
  pre-existing deployment.
- **T4** — Documentation/continuity drift beyond what this INTAKE handoff
  corrects: `cvf_runtime/identity.py`'s docstring still describes
  header-based/non-authenticated identity; `CVF_CONTROL_MAPPING.md`'s
  identity row cites 4 login tests (actual: 5) and the permission row still
  says it depends on unauthenticated identity; `EXECUTION_ROADMAP.md`,
  `IMPLEMENTATION_STATUS.json`, `MODULE_REGISTRY.json`, `MODULE_CATALOG.md`
  need a full pass once repair is authorized — none of these may be restored
  to DONE/load-bearing wording until REVIEW and live evidence both pass.

Full technical detail and acceptance criteria for T1-T4 belong in the
corrective SPEC (next phase), not this handoff.

## Explicit scope boundaries (not opened by this corrective tranche)

Unchanged from the original tranche's own documented boundaries — this
corrective tranche repairs P2-B's process and defects, it does not expand
scope to: `known-principals.yaml` reconciliation / approval High Finding #4,
refresh tokens/revocation, self-service registration, password reset, login
rate limiting, production admin provisioning, PostgreSQL production
verification, `data_scope`/`cost`/`termination` runtime callers, or refusal
routing/recording.

## What this INTAKE phase did and did not do

Did: record R2, record `cd36b27` as an unauthorized build candidate,
downgrade `SESSION/ACTIVE_SESSION_STATE.json` / `SESSION/SESSION_MEMORY.md`
/ `IMPLEMENTATION_STATUS.json` claims, record active role ORCHESTRATOR,
create this handoff.

Did NOT: touch any implementation file, test file, `CVF_CONTROL_MAPPING.md`,
`MODULE_REGISTRY.json`/`MODULE_CATALOG.md`, `.env.example`, or the original
ADR. Those are in scope for the corrective SPEC/WORK_ORDER (T4), authorized
and executed only after WORK_ORDER approval.

## Update — DESIGN, SPEC, WORK_ORDER completed; operator approval GRANTED (2026-07-22)

DESIGN (`docs/decisions/ADR_2026-07-22_P2B_AUTHENTICATION_REPAIR.md`)
independently re-verified T1 (one-character secret signs a valid
`authorized_executive` token), T2 (73-byte password crashes `POST
/auth/login` with an uncaught 500 for both existing and unknown usernames),
and T3 (docker-compose's `initdb.d` mount is first-init-only) directly
against the running code, not by trusting the finding text. SPEC
(`docs/specs/P2B_AUTHENTICATION_REPAIR_SPEC.md`) converted this into 14
testable acceptance criteria plus a CURRENT-vs-DESIRED table. WORK_ORDER
(`docs/work_orders/P2B_AUTHENTICATION_REPAIR_WORK_ORDER.md`) bounded the
changed set, stop conditions, review requirement, live-evidence plan, and
FREEZE definition.

**Operator approved the WORK_ORDER exactly as written** (changed set,
acceptance criteria, stop conditions, role separation, commit discipline) —
see WORK_ORDER §13 for the verbatim approval text. Approval explicitly
reiterates: commit authorization artifacts separately, then proceed to
BUILD; **no FREEZE before independent REVIEW_PASS and live Alibaba evidence
PASS**, both per WORK_ORDER §11.

Role transition recorded: WORK_ORDER_AUTHOR → COMMIT_STEWARD (to commit
authorization artifacts) → IMPLEMENTATION_WORKER (to begin BUILD).

## Update — BUILD, REPAIR, and REVIEW_PASS (2026-07-23)

BUILD (commit `2c397f7`) implemented exactly WORK_ORDER §1's authorized
changed set: T1 (`Settings.jwt_secret_key` fails closed via a plain
`__init__` override — not a pydantic validator, because those wrap
exceptions into a `ValidationError` that echoes the rejected value
regardless of message, SI-2), T2 (`LoginInput.password` rejected above 72
UTF-8 bytes before any ledger/bcrypt call), T3
(`scripts/apply_migrations.py` + a static idempotency-guard test — with a
correction to the DESIGN ADR's own claim: `CREATE TYPE ... AS ENUM` in
`001_foundation.sql` has no `IF NOT EXISTS` form, so the runner tolerates
`duplicate_object`/etc. SQLSTATEs rather than assuming the SQL fully
self-guards), and `scripts/run_identity_live_governance_evidence.py` (binds
the real identity gate to one real Alibaba call, so the evidence is about
*this* control, not a generic provider canary).

An independent REVIEWER (fresh agent context) found 8 real defects: a
denylist checked after the length rule, making it unreachable dead code;
self-contradictory docstrings left over from an earlier iteration of the
T1 fix; `redact_url` only redacting up to the *first* `@`, leaking the rest
of a password containing one; the evidence receipt's "Claim boundary"
claiming a real provider call happened even when the request never reached
the server; the T2 length check (a pydantic `field_validator`) causing
FastAPI to echo the over-long password back into the 422 response body;
and the SPEC specifying a pydantic `ValidationError` where the (correct,
SI-2-driven) implementation used a custom exception instead. Verdict:
**REVIEW_CHANGES_REQUIRED**.

REPAIR (commit `10e57e1`) fixed all 8: denylist now checked before length;
docstrings rewritten to agree with each other and the code; `redact_url`
now matches greedily to the *last* `@`; the receipt now tracks whether the
call actually reached the provider and words the claim accordingly (PASS /
reached-but-error / never-reached); the T2 check moved to a manual
`HTTPException` raised as the first statement in the route handler (fixed
`{"detail": ...}` body, no echo, same before-any-lookup timing guarantee);
the SPEC amended (§4.1, §4.2, new SI-6) to describe what was actually built.
This same commit also corrected its own predecessor's claim that the red
catalog gate was "not from this commit" — independently recomputed:
workspace-api's +108 LOC delta *is* this tranche's own code; only the
`ai-providers` +102 LOC/+1 file is the separate, uncommitted
`PROVIDER-ALIBABA-LIVE-CONFIG` tranche's.

A second independent REVIEWER re-verified all 8 fixes with fresh probes
(not by re-reading the first repair's own tests) and found no new defects.
Verdict: **REVIEW_PASS** (2026-07-23).

Live evidence (`scripts/run_identity_live_governance_evidence.py`) was then
run: the in-process identity-gate checks both pass, but no
`ALIBABA_API_KEY`/`DASHSCOPE_API_KEY` is set and the sibling Alibaba
tranche has not yet committed. The script correctly exits 2 and prints
`READY_FOR_LIVE_EVIDENCE` — no receipt was written, no pass was fabricated.
**This tranche cannot reach FREEZE by itself**; the remaining dependency
belongs to the operator (supplying the key) and to the separate, already
-authorized Alibaba tranche (committing its infrastructure).

## Next allowed move

Once `ALIBABA_API_KEY` (or `DASHSCOPE_API_KEY`) is set in the environment
and the sibling `PROVIDER-ALIBABA-LIVE-CONFIG` tranche has committed, run
`python scripts/run_identity_live_governance_evidence.py`. On a PASS
receipt, transition to CLOSER and complete FREEZE: sync
`docs/cvf/CVF_CONTROL_MAPPING.md`, `docs/catalog/MODULE_REGISTRY.json`
(+regenerate `MODULE_CATALOG.md`), `docs/implementation/EXECUTION_ROADMAP.md`,
`IMPLEMENTATION_STATUS.json`, and the session files per WORK_ORDER §1's
post-REVIEW_PASS list, then commit and push. On failure, keep the tranche
at its current disposition and record the failure plainly — do not
reframe it.

## Blocked

Everything in the superseded handoff's "Blocked" section still applies. In
addition, as of this INTAKE: do not claim P2-B is DONE, do not claim
identity is load-bearing in an approved sense, do not claim BUILD or REVIEW
are complete for this tranche, do not skip DESIGN/SPEC/WORK_ORDER, do not
use mock/TestClient probes as governance evidence for the eventual
live-evidence requirement, and do not rewrite/squash/force-push `cd36b27`.
