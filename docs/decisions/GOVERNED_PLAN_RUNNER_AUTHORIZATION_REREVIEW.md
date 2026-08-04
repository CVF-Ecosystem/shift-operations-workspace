# Governed Plan Runner — Independent Authorization Re-review

- Review date: `2026-08-04`
- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Role: `REVIEWER` (fresh and independent from authority authorship and the
  failed initial review invocation)
- Risk / phase: `R2 / WORK_ORDER`
- Baseline: `HEAD == origin/main == 3c53882f37cda6ba1ac48eb335f88e56b89cd471`
- ADR SHA-256:
  `4adebea9aac3d078e0a97c7eb2fec04f41bbbdeb54f59d2cc477f4f82c9a8492`
- SPEC SHA-256:
  `b26b90388e5b41c58aa11d2f245a3ee590fb82fafd347c496c6b7187f1611260`
- Work Order SHA-256:
  `352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`
- Initial FAIL review SHA-256:
  `57e1ead6ba5b36d862b4c2ab58fd995290c46173c185e6818db90d7962f9fe63`
- Findings: `GPR-AUTH-F2`
- Waivers: `NONE`
- Review calls: `0 provider / 0 network / 0 remote-ingest`

## Disposition

`WORK_ORDER_AUTHORIZATION_REREVIEW_FAIL`

The reviewed design is bounded and its behavioral contracts are substantively
testable, but the frozen execution contract is not locally executable under its
own no-install boundary. The ADR requires CPython `>=3.12`; the available
dependency-complete project interpreter is CPython `3.11.9`, while the locally
registered CPython `3.13.12` has no `pytest`. The Work Order requires focused
pytest plus the full non-live suite and explicitly prohibits package install.
Consequently the authorized BUILD sequence cannot satisfy both the interpreter
floor and evidence commands without an unreviewed dependency-resolution step.

No authority checkpoint, R2 acceptance, BUILD, stage, commit, push or FREEZE is
authorized by this disposition.

## GPR-AUTH-F1 closure

`GPR-AUTH-F1` is `CLOSED_WITHOUT_WAIVER` for this fresh review invocation.

- `.venv` is absent.
- `uv.lock` is absent.
- No recent repository `__pycache__` residue was created.
- The reviewer used tracked local reads, PowerShell, Git read-only inspection,
  the Windows Python launcher for local interpreter enumeration, and direct
  `-B` interpreter probes only.
- No `uv` command, initializer, doctor, package manager, install, fetch, push,
  provider, network or remote-ingest action ran.

The initial FAIL remains immutable historical evidence. Closing its process
finding does not convert that artifact into PASS and does not waive its call.

## Finding

### GPR-AUTH-F2 — frozen Python floor and no-install evidence path conflict

- Severity: `HIGH` authorization/executability
- Status: `OPEN`
- Waiver: `NONE`
- Evidence:
  - default project Python is `3.11.9` and locally imports `pytest 8.3.5` and
    `pydantic 2.10.3`;
  - locally registered CPython `3.13.12` starts successfully but raises
    `ModuleNotFoundError: No module named 'pytest'`;
  - ADR Decision 1 requires CPython `>=3.12`;
  - the Work Order requires focused and full pytest evidence while prohibiting
    package installation.
- Required repair: freeze one executable, zero-network toolchain. The smallest
  correction is to lower the runner floor to the repository's already working
  CPython `>=3.11` if the implementation uses only compatible standard-library
  features. Otherwise, separately provision and review a dependency-complete
  CPython `>=3.12` environment before this Work Order. Recompute every changed
  artifact hash and obtain another fresh independent authorization review.

## Independent scope and contract assessment

Apart from `GPR-AUTH-F2`, the authority is sufficient and non-expansive:

- The exact-eight BUILD ceiling contains eight unique, currently absent paths:
  three runner modules, one JSON schema, three test modules and one historical
  A28 fixture. All governance paths remain separately owned and staged paths
  are zero.
- The split assigns CLI/wiring, closed contract parsing, and engine primitives
  to separate modules. Every new Python source/test file targets at most 250
  lines, is hard-limited to 300, and receives no compression, exception or debt
  authorization.
- SPEC R1-R7 plus AC-1 close unknown fields, ordering, path containment,
  mutation ambiguity, direct argv, pytest collection and timeout budgeting.
- R8-R10 plus AC-2/AC-4/AC-7 keep `validate` and `dry-run` zero-write,
  pre-approval and gate-free while requiring byte simulation, occurrence,
  pre/post hash, indentation and mixed-newline evidence.
- R11-R14 plus AC-3/AC-4/AC-9 separately require accepted canonical R2 and
  pushed checkpoints for `apply`, precompute every output, use same-directory
  atomic replacement, restore and verify all pre-hashes on partial write
  failure, retain a successfully applied candidate on gate failure, stop first,
  terminate only the owned process tree and make zero external calls.
- R15-R18 plus AC-5/AC-6 bind canonical deterministic sanitized receipts,
  atomic receipt writes and exact prior-receipt resume. Resume can select only
  a reviewed prior `NOT_RUN` suffix and cannot rerun `PASS`, `FAIL`, `TIMEOUT`
  or `ERROR` truth.
- R19-R20 plus AC-8/AC-10 bind the four-command CLI, exit-code classes,
  modularity, exact local gates and independent BUILD review before commit.
- ADR, SPEC and Work Order consistently preserve stop-first/no-retry and fresh
  R2 semantics. Git shows no change to CVF core, `AGENTS.md`, `.cvf/policy.json`
  or `.cvf/manifest.json`; product code is outside the exact-eight ceiling.

## R2 digest reproduction — not authorized

For the unchanged frozen Work Order, the proposed acknowledgment independently
reproduces `201` Unicode code points, `207` UTF-8 bytes and SHA-256:

`89dac0864b10327c4528905394e5e891c4b22bdf9ae2fc8504afbb87a49b9028`

Because this disposition is FAIL, the acknowledgment literal is deliberately
not presented as usable authority. A repaired Work Order changes its SHA and
requires a newly calculated literal and digest after a fresh PASS.

## Exact checkpoint boundary

No authority checkpoint is allowed now. For comparison only, if the repaired
authority later receives a fresh PASS, the governance-only checkpoint must
contain exactly these nine unique paths, including both historical review
records:

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `SESSION/SESSION_MEMORY.md`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-04_GOVERNED_PLAN_RUNNER.md`
5. `docs/decisions/ADR_2026-08-04_GOVERNED_PLAN_RUNNER.md`
6. `docs/decisions/GOVERNED_PLAN_RUNNER_AUTHORIZATION_REVIEW.md`
7. `docs/decisions/GOVERNED_PLAN_RUNNER_AUTHORIZATION_REREVIEW.md`
8. `docs/specs/GOVERNED_PLAN_RUNNER_SPEC.md`
9. `docs/work_orders/GOVERNED_PLAN_RUNNER_WORK_ORDER.md`

No exact-eight BUILD path may enter that checkpoint.

## Claim boundary

This re-review proves only local authority inspection and closure of the fresh
review process violation. It does not prove the runner exists, authorize BUILD,
change approval semantics, permit retry of consumed R2, claim CVF controls AI,
establish production readiness or complete Phase 3.
