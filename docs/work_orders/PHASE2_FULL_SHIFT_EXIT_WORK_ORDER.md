# Work Order — Phase 2 Full-Shift Exit Gate

- Work Order id: `P2-FULL-SHIFT-EXIT-WO-001`
- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `PROPOSED_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- Source parent: `e1ac14beaf426ded1b763ff3373b238a065c4694`
- INTAKE: `docs/decisions/INTAKE_2026-08-02_PHASE2_FULL_SHIFT_EXIT.md`
- DESIGN: `docs/decisions/ADR_2026-08-02_PHASE2_FULL_SHIFT_EXIT.md`
- SPEC: `docs/specs/PHASE2_FULL_SHIFT_EXIT_SPEC.md`

## 1. Authority and roles

An independent `AUTHORIZATION_REVIEWER` must compare current source, P2-D C4,
ADR/SPEC and this inventory. BUILD requires explicit `REVIEW_PASS`, pushed
authorization artifacts, a separate pushed pre-BUILD continuity checkpoint and
fresh G6. The later `IMPLEMENTATION_WORKER` may edit only the exact paths below
and must not stage, commit, push, self-review or FREEZE.

## 2. Exact 15-path BUILD ceiling

Every listed path must change materially unless marked NEW. Any outside path,
unnecessary listed edit or missing needed path is
`BLOCKED_WORK_ORDER_CEILING` and requires a reviewed amendment.

### Browser composition — 2 paths

1. `apps/workspace-web/e2e/phase2-full-shift-exit-helpers.ts` — NEW
2. `apps/workspace-web/e2e/phase2-full-shift-exit.spec.ts` — NEW

### Browser runner and contract tests — 2 paths

3. `scripts/testing/run_phase2_full_shift_exit_web_evidence.py` — NEW
4. `tests/integration/test_phase2_full_shift_exit_web_evidence_runner.py` — NEW

### PostgreSQL composition — 2 paths

5. `tests/integration/test_phase2_full_shift_exit_postgres_live.py` — NEW
6. `scripts/run_postgres_live_roundtrip.py`

### Live governance runner and tests — 4 paths

7. `scripts/run_phase2_full_shift_live_governance_evidence.py` — NEW
8. `scripts/_phase2_full_shift_live_evidence_support.py` — NEW
9. `tests/integration/test_phase2_full_shift_live_evidence_runner.py` — NEW
10. `tests/unit/test_phase2_full_shift_live_evidence_support.py` — NEW

### Receipts and truth surfaces — 5 paths

11. `docs/decisions/PHASE2_FULL_SHIFT_BUILD_EVIDENCE_RECEIPT.md` — NEW
12. `docs/decisions/PHASE2_FULL_SHIFT_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md` — NEW
13. `docs/cvf/CVF_CONTROL_MAPPING.md`
14. `docs/catalog/MODULE_REGISTRY.json`
15. `docs/catalog/MODULE_CATALOG.md`

## 3. Implementation contract

The browser spec implements SPEC R2-R6/R9-R10 in one lineage. Initially
unassigned `sup1` uses the always-rendered supervisor staffing controls to
assign both `sup1` and `sup2` to source and destination; every staffing and
operational action uses rendered UI, with no bootstrap action via API. The operator
page observes `sup1`'s event confirmation through polling while its task remains
`IN_PROGRESS`. The new wrapper reuses the existing shared harness unchanged,
selects only this spec with `bounded_exercised_and_cleaned`, and writes an
optional sanitized temporary evidence JSON for later provider admission.

The PostgreSQL test uses the existing `LIVE_POSTGRES_DATABASE_URL`, migration-
created schema, real FastAPI/JWT routes and `SqlLedger`. It must verify SPEC R7
after engine reconnect. The existing one-shot runner adds exactly this target
to its pinned suite and preserves unique container, loopback port, sanitization
and anonymous-volume cleanup semantics.

The governance runner owns a fresh provider counter, executes only the API/
governance refusal cases assigned to it by SPEC R8 with observed zero-call
deltas, and performs one genuine integrated durable scenario. Browser-owned
transport ambiguity is not attributed to that counter: the runner validates
the wrapper's temporary JSON PASS result and references it in the live receipt.
That browser case proves one request/no retry/no queue, visible ambiguity and
authoritative-state reconciliation, not that the intended request never
committed. Only after exact-parent rehearsal does the runner call the provider
once. Support code remains unit-testable without network. No prior receipt is
reused.

## 4. Protected boundary

Zero diff is mandatory for all product source under `apps/workspace-web/src/**`,
`apps/workspace-api/**`, `packages/**`, database/migrations/OpenAPI, dependency
manifests/lockfile, auth/CVF policy/config, provider configuration, CI,
Docker/deployment, roadmap/status/continuity and prior tranche receipts during
BUILD. Phase-2 roadmap/status/continuity closure is a separate C4.

## 5. Fresh G6 before BUILD

From a clean pushed pre-BUILD checkpoint:

1. verify `HEAD == origin/main`, exact authorization ancestry and clean tree;
2. rehydrate mandatory continuity and all five authorization/review artifacts;
3. verify P2-D BUILD `6fc4359` and C4 `e1ac14b` are ancestors;
4. record fresh Python/frontend baselines and exact tool versions;
5. verify Chromium, Docker/PostgreSQL and provider prerequisites with zero
   owned residue, without making a provider call;
6. pass JSON/session/catalog/file-size/repository/diff and doctor 24/1-only;
7. stop `BLOCKED_G6` on any failure before source edit/provider call.

## 6. Required evidence order

```powershell
pnpm install --frozen-lockfile
pnpm --filter workspace-web typecheck
pnpm --filter workspace-web test
pnpm --filter workspace-web build
python -m pytest -q tests/integration/test_phase2_full_shift_exit_web_evidence_runner.py tests/integration/test_phase2_full_shift_live_evidence_runner.py tests/unit/test_phase2_full_shift_live_evidence_support.py
python scripts/testing/run_phase2_full_shift_exit_web_evidence.py --json --evidence-json <owned-temp-json>
python -m pytest -q
python scripts/run_postgres_live_roundtrip.py --json
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
# AC-14: exact-parent detached rehearsal + verified worktree cleanup occurs here
python scripts/run_phase2_full_shift_live_governance_evidence.py --browser-evidence-json <owned-temp-json>
# validate sanitized receipts/final diff, then remove the exact owned temp JSON
```

AC-14 exact-parent detached rehearsal must reproduce G6 baselines and remove its
verified temporary worktree before provider admission. The real provider command
above is the last behavioral execution; only receipt validation, final diff/
changed-set inspection and exact owned-temp cleanup may follow it. The worker
reports exact counts, receipts, container/process/volume cleanup, exact 15-path
set, zero staged files and:

`READY_FOR_INDEPENDENT_PHASE2_FULL_SHIFT_BUILD_REVIEW`

## 7. Review, failure and closure

Independent BUILD review compares source, browser trace, durable records,
audits, receipts and every AC. Any hidden API substitution, identity collapse,
empty/stale handover snapshot, provider-before-admission call, protected diff,
cleanup residue or overclaim requires changes. After reviewed BUILD push, only
a separate C4 may mark the exit gate and Phase 2 `CLOSED_BOUNDED` and activate
the parked post-Phase-2 queue. No subsequent BUILD authority carries forward.
