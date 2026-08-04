# Governed Plan Runner — Independent Authorization Review

- Review date: `2026-08-04`
- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Role: `REVIEWER` (independent from authority authorship)
- Risk / phase: `R2 / WORK_ORDER`
- Baseline: `HEAD == origin/main == 3c53882f37cda6ba1ac48eb335f88e56b89cd471`
- ADR SHA-256:
  `4adebea9aac3d078e0a97c7eb2fec04f41bbbdeb54f59d2cc477f4f82c9a8492`
- SPEC SHA-256:
  `b26b90388e5b41c58aa11d2f245a3ee590fb82fafd347c496c6b7187f1611260`
- Work Order SHA-256:
  `352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`
- Findings: `GPR-AUTH-F1`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AUTHORIZATION_REVIEW_FAIL`

The authority content is necessary, bounded and substantively sufficient, but
this review invocation cannot authorize it. During independent executability
checking, the reviewer ran `uv run python --version`. `uv` created a local
`.venv` and reported downloading `pydantic-core` from a package registry. That
is a nonzero external network/package-resolution action and violates the
explicit zero-network review boundary. It cannot be erased, waived or relabeled
as a zero-call review.

No BUILD, authority checkpoint, R2 acceptance, implementation, stage, commit,
push or FREEZE is authorized by this failed disposition. A fresh independent
review must rehydrate and reproduce the assessment using read-only local tools
that cannot resolve or download dependencies.

## Finding

### GPR-AUTH-F1 — review evidence violates zero-network boundary

- Severity: `HIGH` governance/evidence integrity
- Status: `OPEN`
- Waiver: `NONE`
- Evidence: the local command output included `Creating virtual environment at:
  .venv`, `Downloading pydantic-core`, and `Installed 26 packages`.
- Repository impact: no tracked BUILD/authority file was changed by the
  command. The generated `.venv` is ignored by Git. An attempted bounded
  cleanup was rejected by the execution policy, so its filesystem presence
  must be handled explicitly outside this review.
- Required closure: remove or deliberately retain the generated ignored
  environment under operator control, then obtain a fresh independent
  zero-provider/zero-network/zero-remote-ingest authorization review.

## Substantive authority assessment

Apart from GPR-AUTH-F1, no content finding was identified:

- The ADR, SPEC and Work Order raw SHA-256 values reproduce exactly.
- The project requires CPython `>=3.12`; an already installed CPython 3.13.12
  interpreter is enumerated locally, so the version requirement is feasible
  without changing the eight-path BUILD ceiling. A fresh review must avoid
  environment creation or dependency resolution when confirming this fact.
- The exact eight BUILD paths are unique, currently absent and confined to
  three runner modules, one JSON schema, three test modules and one historical
  A28 regression fixture.
- Each new Python file is explicitly capped at 300 lines, targets 250 lines,
  and receives no exception/debt entry.
- SPEC R1-R20 and AC-1 through AC-10 are testable: closed schemas, ordinal path
  sets, normalized containment, no symlink/glob/path escape, direct argv with
  `shell=False`, explicit pytest collection, byte simulation, timeout budgets,
  all-output precomputation, atomic replacement, verified rollback, owned-tree
  termination, stop-first status, canonical sanitized receipts and drift-bound
  resume are each paired with mandatory evidence.
- Pre-R2 `validate`/`dry-run` verify the proposed acknowledgment binding but do
  not require or claim human acceptance. `apply` separately requires canonical
  accepted acknowledgment and pushed authority/acknowledgment checkpoints.
- Apply rollback covers write-phase partial mutation only; an authorized gate
  failure retains the applied candidate and marks all later gates `NOT_RUN`.
- Resume may select only a prior `NOT_RUN` suffix. It cannot rerun `PASS`,
  `FAIL`, `TIMEOUT` or `ERROR` truth and requires a newly reviewed plan binding
  the exact prior receipt digest.
- The receipt contract is deterministic UTF-8/LF sorted-key JSON; it excludes
  time, duration, inherited environment and absolute host paths, sanitizes
  output before hashing/storage, bounds tails and writes atomically.
- The implementation boundary contains no shell, provider, network or
  remote-ingest client and changes no product or CVF policy semantics. Gate
  argv remains independently reviewable under the zero-call claim.

This substantive assessment does not override the failed review process and
does not grant conditional BUILD authority.

## Proposed R2 reproduction — not authorized

The proposed single-line acknowledgment independently reproduces 201 Unicode
code points, 207 UTF-8 bytes and SHA-256:

`89dac0864b10327c4528905394e5e891c4b22bdf9ae2fc8504afbb87a49b9028`

Because the disposition is FAIL, the literal is deliberately not presented as
an accepted or usable acknowledgment. It must be reproduced again by the fresh
reviewer from the unchanged final Work Order.

## Expected authority checkpoint set after a future PASS

The current unstaged authority candidate has exactly seven paths and staged
paths zero. A future passing authorization review would make the exact
governance-only checkpoint set these eight unique paths:

1. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `SESSION/SESSION_MEMORY.md`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-04_GOVERNED_PLAN_RUNNER.md`
5. `docs/decisions/ADR_2026-08-04_GOVERNED_PLAN_RUNNER.md`
6. `docs/decisions/GOVERNED_PLAN_RUNNER_AUTHORIZATION_REVIEW.md`
7. `docs/specs/GOVERNED_PLAN_RUNNER_SPEC.md`
8. `docs/work_orders/GOVERNED_PLAN_RUNNER_WORK_ORDER.md`

This list is recorded for scope comparison only. The present FAIL does not
authorize staging or pushing it as a passing authority checkpoint. No exact
eight BUILD path may be added to that governance checkpoint.

## Claim boundary

The proposed runner is only a deterministic project-local file/process
orchestrator. It does not change CVF core or policy semantics, make approval
automatic, permit retry of consumed authority, prove CVF controls AI behavior,
provide production execution, change P3-A/P3-B/P3-C product code, or complete
Phase 3.
