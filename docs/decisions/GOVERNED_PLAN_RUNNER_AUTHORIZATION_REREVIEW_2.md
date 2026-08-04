# Governed Plan Runner — Independent Authorization Re-review 2

- Review date: `2026-08-04`
- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Role: `REVIEWER` (fresh independent final authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- Baseline: `HEAD == origin/main == 3c53882f37cda6ba1ac48eb335f88e56b89cd471`
- Corrected ADR SHA-256:
  `4c273fc8f0fb984ffa4b2ce0061b981ccb89efd6097ddb873780f82aefa9ed97`
- Unchanged SPEC SHA-256:
  `b26b90388e5b41c58aa11d2f245a3ee590fb82fafd347c496c6b7187f1611260`
- Unchanged Work Order SHA-256:
  `352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`
- Initial FAIL review SHA-256:
  `57e1ead6ba5b36d862b4c2ab58fd995290c46173c185e6818db90d7962f9fe63`
- First local-only re-review SHA-256:
  `7357cd562b25a28762a8c22216f75969904384dd4e88e1f9306ceb19be96d409`
- Findings: `NONE`
- Waivers: `NONE`
- Review calls: `0 provider / 0 network / 0 remote-ingest`

## Disposition

`WORK_ORDER_AUTHORIZATION_REVIEW_PASS`

The corrected authority is necessary, sufficient, executable and
non-expansive. The only substantive finding from the first local-only
re-review is repaired: the ADR now binds CPython `>=3.11`, which matches the
already available dependency-complete project interpreter. SPEC and Work
Order bytes remain unchanged. No package resolution or environment creation is
needed or authorized.

This PASS authorizes only the exact governance checkpoint below. BUILD remains
blocked until that checkpoint is pushed and the operator sends the exact fresh
R2 acknowledgment reproduced below.

## Finding closure

### GPR-AUTH-F1

Status: `CLOSED_WITHOUT_WAIVER`.

The failed initial review remains immutable evidence of its prohibited `uv`
network/package action. In both fresh review invocations, `.venv` and `uv.lock`
are absent and no doctor, initializer, `uv`, package manager, install, fetch,
push, provider, network or remote-ingest action ran. No repository cache or
lock residue was created.

### GPR-AUTH-F2

Status: `CLOSED_WITHOUT_WAIVER`.

- Corrected ADR Decision 1 says `CPython >=3.11` and standard library.
- No `>=3.12` floor remains in the corrected ADR.
- System Python `3.11.9` satisfies the corrected floor and locally imports the
  existing `pytest 8.3.5` and `pydantic 2.10.3` dependencies.
- The unchanged Work Order's focused and full test evidence can therefore run
  without package installation or dependency resolution.

No open finding or waiver remains.

## Exact-eight and split verification

The eight BUILD paths are unique, currently absent and exact:

1. `scripts/run_governed_plan.py`
2. `scripts/_governed_plan_contract.py`
3. `scripts/_governed_plan_engine.py`
4. `docs/reference/GOVERNED_PLAN_SCHEMA.json`
5. `tests/unit/test_governed_plan_contract.py`
6. `tests/unit/test_governed_plan_engine.py`
7. `tests/unit/test_governed_plan_resume.py`
8. `tests/fixtures/governed_plan/a28_indent_plan.json`

The source split remains explicit: CLI/wiring, closed contract parsing and
engine primitives are separate modules. The three test concerns and historical
A28 fixture are also separated. Every new Python source/test file targets at
most 250 lines, is hard-limited to 300 and has no compression, exception or
debt-baseline authority. Staged paths are zero.

## Requirements and acceptance verification

- R1-R7 and AC-1 bind closed canonical plan objects, ordinal unique path sets,
  containment/symlink/glob rejection, byte mutation bindings, direct argv with
  `shell=False`, explicit pytest collection and outer-timeout budgeting.
- R8-R10 and AC-2/AC-4/AC-7 keep `validate` and pre-R2 `dry-run` zero-write,
  gate-free and independent from human acceptance. Dry-run must reproduce
  occurrence, pre/post hash, indentation and mixed-newline effects in memory.
- R11-R14 and AC-3/AC-4/AC-9 require `apply` to revalidate accepted canonical
  R2 and pushed checkpoints, precompute all output, atomically replace from
  same-directory temporary files and restore/verify every pre-hash after a
  partial write exception. Gate failure retains the authorized candidate,
  marks the remaining gates `NOT_RUN` and never retries.
- R15-R18 and AC-5/AC-6 require deterministic UTF-8/LF sorted-key receipts,
  sanitization before output hashing/storage, bounded tails, atomic receipt
  writes and exact receipt-digest-bound resume. Resume may run only the prior
  `NOT_RUN` suffix and rejects every terminal gate or binding drift.
- R19-R20 and AC-8/AC-10 bind the exact four CLI commands, distinct exit-code
  classes, module/file-size limits, exact local evidence gates and independent
  BUILD review before commit.
- The Work Order preserves the zero provider/network/remote-ingest budget,
  exact stop-first semantics and fresh authority after every failure. It does
  not permit shell command strings, automatic approval or retry.

Git inspection shows no change to CVF core, `AGENTS.md`, `.cvf/policy.json`,
`.cvf/manifest.json` or product code. The authority makes no live AI-governance
claim, so provider evidence is neither required nor authorized.

## Exact authority checkpoint

`COMMIT_STEWARD` may partial-stage, commit and push exactly these ten unique
governance paths, with all exact-eight BUILD paths absent and staged-excluded:

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `SESSION/SESSION_MEMORY.md`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-04_GOVERNED_PLAN_RUNNER.md`
5. `docs/decisions/ADR_2026-08-04_GOVERNED_PLAN_RUNNER.md`
6. `docs/decisions/GOVERNED_PLAN_RUNNER_AUTHORIZATION_REVIEW.md`
7. `docs/decisions/GOVERNED_PLAN_RUNNER_AUTHORIZATION_REREVIEW.md`
8. `docs/decisions/GOVERNED_PLAN_RUNNER_AUTHORIZATION_REREVIEW_2.md`
9. `docs/specs/GOVERNED_PLAN_RUNNER_SPEC.md`
10. `docs/work_orders/GOVERNED_PLAN_RUNNER_WORK_ORDER.md`

No BUILD path, generated environment, cache, lock, product, policy or core path
may enter that checkpoint.

## Exact fresh R2

After the exact-ten authority checkpoint is pushed, the only accepted
acknowledgment is this single line with no leading/trailing whitespace or
newline:

> Tôi phê duyệt R2 cho GOVERNED-PLAN-RUNNER-2026-08-04, Work Order SHA-256 352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327, đúng 8 BUILD paths, zero provider/network/remote-ingest calls.

- Unicode code points: `201`
- UTF-8 bytes: `207`
- SHA-256 over the exact UTF-8 bytes:
  `89dac0864b10327c4528905394e5e891c4b22bdf9ae2fc8504afbb87a49b9028`

Chat intent or altered wording is not a substitute. The acknowledgment grants
one stop-first/no-retry exact-eight BUILD invocation only after its separate
governance checkpoint is pushed. It grants no provider/network/remote-ingest
call, BUILD commit, self-review, FREEZE or later-lane authority.

## Claim boundary

This review authorizes only the bounded deterministic local runner BUILD
process. It does not prove the runner exists, change CVF policy semantics,
permit retry of consumed R2, prove AI governance behavior, establish production
readiness, change P3 product code or complete Phase 3.
