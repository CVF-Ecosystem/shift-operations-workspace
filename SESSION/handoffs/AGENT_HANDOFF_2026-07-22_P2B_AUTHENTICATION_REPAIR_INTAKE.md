# Agent Handoff — 2026-07-22 (P2-B Authentication Repair — INTAKE)

Provider-neutral handoff. Supersedes
[`AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION.md`](AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION.md)
as the active handoff. That file is **not deleted or rewritten** — it remains
as the historical record of what commit `cd36b27` claims about itself. This
handoff records the operator-initiated correction of that claim.

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P2B-AUTHENTICATION-REPAIR — corrective control-chain tranche
- **Control-chain phase:** INTAKE (this handoff)
- **Risk:** R2 — changes the authentication/security boundary and the
  `identity` CVF control
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=DESIGN (corrective ADR); parked checkpoint=none; active
  role=ORCHESTRATOR

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

## Next allowed move

BUILD — implement exactly WORK_ORDER §1's authorized changed set (T1-T3
code fixes, their tests, and the live-evidence script), per SPEC. Then
independent REVIEW, then live Alibaba evidence, then — only if both pass —
FREEZE.

## Blocked

Everything in the superseded handoff's "Blocked" section still applies. In
addition, as of this INTAKE: do not claim P2-B is DONE, do not claim
identity is load-bearing in an approved sense, do not claim BUILD or REVIEW
are complete for this tranche, do not skip DESIGN/SPEC/WORK_ORDER, do not
use mock/TestClient probes as governance evidence for the eventual
live-evidence requirement, and do not rewrite/squash/force-push `cd36b27`.
