# Work Order: P2-B Authentication Repair

- Work order: `WO-P2B-AUTHENTICATION-REPAIR-2026-07-22`
- Risk: R2
- Status: **AUTHORIZED** (operator-approved 2026-07-22, exactly as written —
  changed set, acceptance criteria, stop conditions, role separation, and
  commit discipline; see §13). BUILD may now proceed under §1's authorized
  changed set. FREEZE is still gated by §11 — REVIEW_PASS and live Alibaba
  evidence PASS are both required before FREEZE.
- Design: `docs/decisions/ADR_2026-07-22_P2B_AUTHENTICATION_REPAIR.md`
- Specification: `docs/specs/P2B_AUTHENTICATION_REPAIR_SPEC.md`
- Corrects: commit `cd36b27` ("P2-B: real authentication"), currently
  disposed REVIEW_CHANGES_REQUIRED — UNAUTHORIZED BUILD CANDIDATE

## 1. Authorized changed set

**Code:**
- `apps/workspace-api/src/workspace_api/config.py` — add
  `jwt_secret_key` validation (SPEC §4.1).
- `apps/workspace-api/src/workspace_api/auth/router.py` — add
  `LoginInput.password` length validation (SPEC §4.2).
- `scripts/apply_migrations.py` (new) — migration runner/runbook (SPEC §5).
- One new standalone live-evidence script (new; exact path decided by
  IMPLEMENTATION_WORKER, must live under `scripts/` and must NOT be
  registered as a FastAPI router/endpoint) implementing SPEC §1.5/§7.

**Tests:**
- `tests/cvf/test_auth_config_secret_validation.py` (new) — AC-1..AC-5.
- `tests/cvf/test_auth_login.py` (extend, not replace) — AC-6..AC-10.
- `tests/integration/test_migration_idempotency_guard.py` (new) — AC-11.

**Documentation — authorized to touch ONLY after REVIEW_PASS is recorded
(§9), not before, per SPEC §8:**
- `cvf_runtime/identity.py` (docstring only).
- `docs/cvf/CVF_CONTROL_MAPPING.md` (identity row, permission row).
- `docs/catalog/MODULE_REGISTRY.json` + regenerated `MODULE_CATALOG.md`
  (via `python scripts/generate_catalog.py --write`).
- `docs/implementation/EXECUTION_ROADMAP.md`.
- `IMPLEMENTATION_STATUS.json`.
- `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`.
- One closing handoff under `SESSION/handoffs/`.
- One live-evidence receipt (new file, sanitized) under `docs/decisions/`.

**Authorization artifacts (this INTAKE/DESIGN/SPEC/WORK_ORDER set) are
committed separately from BUILD — see §10.**

## 2. Explicit exclusions

- `packages/ai-providers/alibaba/**` and any file belonging to the
  parallel `WO-PROVIDER-ALIBABA-LIVE-CONFIG-2026-07-22` work order — this
  tranche only *reads* `ALIBABA_API_KEY` (presence check only) and calls
  `select_model.py` as a library; it does not modify that tranche's files.
- `packages/cvf-application-profile/known-principals.yaml`,
  `packages/cvf-runtime/src/cvf_runtime/approval.py` — High Finding #4 is
  out of scope.
- Any refresh-token, revocation, self-service registration, password
  reset, or rate-limiting code.
- Any new FastAPI router/endpoint (the live-evidence script is a
  standalone script, not an API surface addition).
- The pinned CVF core (`.Controlled-Vibe-Framework-CVF/`) — read-only
  reference only.
- Commit `cd36b27` itself — no rewrite, squash, amend, or force-push.
- Any file not listed in §1. If implementation discovers a genuine need to
  touch something outside this list, STOP (see §7) and return to
  WORK_ORDER_AUTHOR for an amendment — do not silently expand scope.

## 3. Roles and ownership

- **IMPLEMENTATION_WORKER:** implements exactly the authorized changed set
  in §1, adds the tests in §1, runs the checks in §6.
- **REVIEWER:** independent from IMPLEMENTATION_WORKER (§8) — required
  because this is R2 (`AGENTS.md` role contract).
- **COMMIT_STEWARD:** verifies the changed set matches §1 exactly before
  each commit and owns the commit action (§10).
- **SESSION_SYNC_STEWARD:** performs the documentation/continuity sync in
  §1's "after REVIEW_PASS" list and re-runs `check_session_state.py`.
- **CLOSER:** decides FREEZE only once §11's criteria are all met.
- A single agent may hold multiple of these roles in sequence (this
  project's `roleRoute: SINGLE_AGENT_MULTI_ROLE_ALLOWED`), but each
  transition must be stated and recorded before acting in the new role,
  per `AGENTS.md`.

## 4. Test and probe matrix

| Acceptance criterion | Verification method |
|---|---|
| AC-1..AC-5 (T1 secret validation) | `tests/cvf/test_auth_config_secret_validation.py`, run by IMPLEMENTATION_WORKER, independently re-run by REVIEWER |
| AC-6..AC-10 (T2 password boundary) | `tests/cvf/test_auth_login.py` additions; REVIEWER independently probes with a live `TestClient` call (not just re-reading the builder's test), matching how the original P2-B review found the timing side-channel by probing directly rather than trusting existing tests |
| AC-11 (T3 idempotency guard) | `tests/integration/test_migration_idempotency_guard.py`; REVIEWER independently confirms by hand-editing a temp migration file to drop `IF NOT EXISTS` and confirming the test fails (negative-tested, matching this project's established practice) |
| AC-12 (T4 doc accuracy) | REVIEWER greps `tests/cvf/test_auth_login.py` for the actual test count and diffs it against the doc claim; reads `cvf_runtime/identity.py`'s docstring directly |
| AC-13 (full regression) | IMPLEMENTATION_WORKER runs all four commands in §6 and pastes real output; REVIEWER re-runs them independently, does not trust pasted output alone |
| AC-14 (live evidence) | §5 below |

## 5. Live Alibaba evidence plan

1. Precondition check (boolean only, never print the value): is
   `ALIBABA_API_KEY` set in the environment?
   - **No:** stop here. Record disposition `READY_FOR_LIVE_EVIDENCE`
     (assuming §1's code/test/doc work and REVIEW otherwise pass). This is
     a pause, not a failure — the key arrives from the operator later, out
     of band. Do not write REVIEW_PASS/FREEZE/DONE/"identity load-bearing"
     while in this state.
   - **Yes:** proceed.
2. Run the live-evidence script (SPEC §1.5): in-process valid-token and
   forged-token checks against the real `get_principal`/`decode_access_token`
   path, then — only after the valid-token check passes — one real,
   minimal call through `packages/ai-providers/alibaba/select_model.py`'s
   selection logic to the live Alibaba API.
3. On success: write one sanitized receipt (timestamp, provider, model,
   HTTP outcome, truncated response excerpt — never the key or an
   `Authorization` header) to a new file under `docs/decisions/`.
4. On failure (auth/quota/model-not-found/expiration/any other error):
   record the failure plainly in the same location; the tranche stays open
   at its current disposition. Do not retry repeatedly against a paid API
   without a clear reason to expect a different result (mirrors the
   sibling Alibaba work order's own stop condition).
5. This plan depends entirely on the separate `PROVIDER-ALIBABA-LIVE-CONFIG`
   tranche being committed first. If it is not yet committed when this
   tranche reaches this step, stop here and record
   `READY_FOR_LIVE_EVIDENCE` — do not re-implement its scope to unblock
   this one.

## 6. Required checks (IMPLEMENTATION_WORKER runs first; REVIEWER re-runs independently)

```
python -m pytest -q
python scripts/testing/validate_repository.py
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
```
Plus the CVF workspace doctor:
```
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```
All four commands plus the doctor must pass before REVIEW is requested, and
must be re-run (not re-read) by the REVIEWER.

## 7. Stop conditions

Stop and report a blocker (do not silently work around, do not
self-approve past it) if:

- Any authorized change requires touching a file outside §1's list.
- A fix for one AC breaks a previously-passing test — repair before
  proceeding, do not mark BUILD complete with a known regression.
- No independent reviewer (separate agent/session/human context) is
  available at REVIEW time — STOP, report `BLOCKED_NO_INDEPENDENT_REVIEWER`,
  do not self-approve.
- `python scripts/check_session_state.py` reports drift between
  `SESSION/ACTIVE_SESSION_STATE.json` and `CVF_SESSION/ACTIVE_SESSION_STATE.json`
  at any point — resync before continuing.
- `ALIBABA_API_KEY` is absent, or the parallel Alibaba tranche is not yet
  committed — record `READY_FOR_LIVE_EVIDENCE` and stop before FREEZE, per
  §5.
- The live Alibaba call fails — record the failure, keep the tranche open,
  do not reframe as pass.
- Any command would print, log, or persist the JWT secret or the Alibaba
  key/Authorization header.

## 8. Review requirement

REVIEWER must be independent from IMPLEMENTATION_WORKER (R2 rule,
`AGENTS.md`). The mechanism used for the original P2-B tranche's technical
review — a freshly spawned agent context with no memory of the
implementation session — is acceptable for the *source/spec/test*
independence requirement, but does **not** by itself satisfy §5's live
Alibaba evidence requirement, which is a separate, additional gate. The
REVIEWER must:

- Independently verify every row of §4's test/probe matrix (re-run, not
  re-read).
- Confirm the changed set matches §1 exactly (no files touched outside the
  authorized list).
- Confirm no secret (JWT or Alibaba) appears anywhere in the diff,
  evidence, or command output.
- Confirm the migration runner script is correct for real Postgres use,
  even though it cannot be live-tested in this environment.
- Confirm documentation changes (once authorized, post-REVIEW_PASS per §1)
  do not overclaim beyond what REVIEW and live evidence actually
  established.

Findings must be repaired by a REPAIR_WORKER role transition, then
re-reviewed — do not mark REVIEW_PASS with open findings.

## 9. Definition of REVIEW_PASS

REVIEW_PASS is recorded only when: all of §4's criteria are independently
verified (not merely re-read), the changed set matches §1 exactly, no
secret leakage is found, and any findings raised during review have been
repaired and re-verified. REVIEW_PASS covers the T1-T4 technical/process
repair. **REVIEW_PASS alone does not authorize FREEZE** — §11 additionally
requires live evidence.

## 10. Commit ownership and sequencing

1. **Authorization-artifacts commit** (COMMIT_STEWARD, after operator
   approval of this WORK_ORDER, before any BUILD change): this INTAKE
   handoff, the corrective ADR, the SPEC, and this WORK_ORDER (with the
   operator's approval recorded in it and in the active handoff) — no
   implementation files. This proves DESIGN/SPEC/WORK_ORDER preceded BUILD
   in the commit graph itself, addressing G1 directly.
2. **BUILD commit(s)** (COMMIT_STEWARD, after REVIEW_PASS): the §1 code and
   test changes. May be one commit or split logically (e.g. T1+T2 together,
   T3 separate) but must not be batched with the authorization-artifacts
   commit or with unrelated roadmap tranches, per this project's existing
   commit discipline (`CONTRIBUTING.md`).
3. **FREEZE commit** (COMMIT_STEWARD, only once §11 is fully satisfied): the
   documentation/continuity sync listed in §1, plus the live-evidence
   receipt.
4. `cd36b27` is never amended, rebased onto, or force-pushed over by any of
   the above. Push to `origin main` only after each corresponding commit's
   gates pass, per this project's existing discipline.

## 11. Definition of FREEZE

FREEZE may be recorded only when **all** of the following hold
simultaneously:

- This WORK_ORDER was approved by the operator before BUILD began (§ this
  document, recorded in the active handoff).
- Implementation matches the SPEC (§1-§6 of the SPEC), verified, not
  assumed.
- Independent REVIEW_PASS is recorded (§9), with no open findings.
- All four regression/validation commands in §6 pass, re-run by the
  reviewer, not just the implementer.
- Live Alibaba governance evidence (§5, SPEC §7) PASSES with a real,
  non-mocked response recorded.
- The sanitized evidence artifact exists and contains no secret.
- Catalog, `IMPLEMENTATION_STATUS.json`, `SESSION/SESSION_MEMORY.md`,
  `SESSION/ACTIVE_SESSION_STATE.json`, `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
  and the active handoff are mutually synchronized
  (`check_session_state.py` PASS).
- No T1-T4 finding remains open.

Only at that point may any surface in this repository say "identity is
load-bearing," "P2-B is DONE," or "P2B-AUTHENTICATION-REPAIR FREEZE." Prior
to that point, the correct disposition to record is
`REVIEW_CHANGES_REQUIRED` (before REVIEW_PASS) or `READY_FOR_LIVE_EVIDENCE`
(after REVIEW_PASS but before live evidence).

## 12. Rollback

All §1 code changes are additive/stricter (fail-closed secret validation,
stricter request-boundary rejection, a new opt-in migration script) — none
are schema- or data-destructive. Rollback is reverting the specific
BUILD/FREEZE commit(s) this work order produces; `cd36b27` remains
available as an unaffected floor regardless. No data migration rollback is
needed since `003_users.sql` itself is unchanged by this tranche (only how
it gets *applied* to a pre-existing volume is addressed).

## 13. Approval

- Operator approval: **GRANTED** — "Tôi phê chuẩn WO-P2B-AUTHENTICATION-REPAIR-2026-07-22
  đúng theo changed set, acceptance criteria, stop conditions, role
  separation và commit discipline đã ghi. Cho phép commit authorization
  artifacts riêng, sau đó chuyển sang BUILD. Không được FREEZE trước
  independent review và live Alibaba evidence PASS."
- Approval date: 2026-07-22
- Approved scope: §1/§2 exactly as written, no amendment requested.
- Approval explicitly reiterates the §11 FREEZE gate (independent REVIEW_PASS
  and live Alibaba evidence PASS both required) — this is not a new
  condition, it restates what §11 already required, and is recorded here
  verbatim so the approval and the gate it defers to are never read apart
  from each other.
