# Work Order — Governed Plan Runner

- Work id: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Design: `docs/decisions/ADR_2026-08-04_GOVERNED_PLAN_RUNNER.md`
- Spec: `docs/specs/GOVERNED_PLAN_RUNNER_SPEC.md`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Authority boundary

This Work Order authorizes BUILD only after independent authorization review,
a pushed governance-only authority checkpoint and a fresh exact human R2 bound
to this file's final SHA-256. It does not authorize implementation now.

The runner prevents reviewable mechanical defects before R2. It does not alter
stop-first/no-retry semantics after approval, does not allow reuse of consumed
R2 and does not change CVF core, `AGENTS.md` or `.cvf/policy.json`.

## Exact eight BUILD paths

BUILD may create exactly these eight paths and no others:

1. `scripts/run_governed_plan.py`
2. `scripts/_governed_plan_contract.py`
3. `scripts/_governed_plan_engine.py`
4. `docs/reference/GOVERNED_PLAN_SCHEMA.json`
5. `tests/unit/test_governed_plan_contract.py`
6. `tests/unit/test_governed_plan_engine.py`
7. `tests/unit/test_governed_plan_resume.py`
8. `tests/fixtures/governed_plan/a28_indent_plan.json`

Governance review and continuity artifacts are checkpoint-owned surfaces, not
BUILD paths. They must be staged separately from the exact-eight candidate.

## File ownership and split contract

- `run_governed_plan.py`: CLI parsing, exit-code mapping and dependency wiring.
- `_governed_plan_contract.py`: schema parsing, normalization and validation.
- `_governed_plan_engine.py`: dry-run simulation, transaction, gates, receipt
  and resume primitives.
- `GOVERNED_PLAN_SCHEMA.json`: normative JSON contract matching SPEC R1-R7.
- Three test modules: contract, execution/receipt, and resume/timeout coverage.
- A28 fixture: non-secret historical two-space/newline regression plan only.

Every Python file targets <=250 lines and must remain <=300. No compressed
syntax, generated executable, exception or debt-baseline mutation is allowed.

## Required implementation behavior

The IMPLEMENTATION_WORKER must satisfy SPEC R1-R20 and AC-1 through AC-10,
including:

1. argv arrays with `shell=False`; explicit paths only; no shell/glob/path
   escape;
2. zero-write `validate` and `dry-run` before R2-capable execution;
3. executable, script, pytest collection and outer-timeout-budget validation;
4. byte-exact simulation with occurrence/pre/post hash, CRLF/LF and indentation
   metrics;
5. all-output precomputation, same-directory atomic replacement and verified
   rollback on partial write failure;
6. first-failure stop with later gates `NOT_RUN` and owned process-tree timeout
   cleanup;
7. canonical deterministic sanitized receipt with no timestamp, duration,
   absolute host path, inherited environment or raw secret;
8. drift-bound resume of only prior `NOT_RUN` gates; no rerun of any terminal
   gate status;
9. exactly zero provider/network/remote-ingest calls and no package install;
10. no policy-semantic or product-code change.

## BUILD sequence

After fresh R2 only:

1. rehydrate continuity and verify HEAD/origin, exact authority artifacts,
   acknowledgment digest, clean staged set and clean working tree;
2. create only the exact eight BUILD paths with `apply_patch`;
3. run focused tests for the three runner test modules;
4. run `python scripts/check_file_size.py` before any full suite;
5. run full non-live pytest, repository validator, session checker, schema/JSON
   parses, secret scan and `git diff --check`;
6. audit exact-eight dirty paths, zero staged paths and zero calls;
7. transfer to an independent BUILD REVIEWER. No self-approval or BUILD commit
   occurs before that disposition.

Stop at the first failure. The current R2 is then consumed under existing
policy; there is no retry or alternate repair authority in this Work Order.

## Mandatory tests

The exact-eight candidate must prove:

- schema unknown-field, duplicate/order and unsafe-path rejection;
- valid paths containing spaces remain single argv values;
- missing executable/script and invalid pytest selectors fail in dry-run;
- dry-run never writes target or receipt;
- exact occurrence and post-hash simulation, indentation and CRLF/LF stability;
- precomputed multi-file apply and injected atomic rollback;
- gate failure keeps applied bytes while later gates remain `NOT_RUN`;
- timeout terminates only the owned process tree;
- receipt canonical determinism, sanitization, bounded output and atomic write;
- resume rejects every binding drift and runs only the exact never-run suffix;
- A28 historical regression metrics;
- CLI exit-code classes and unknown-option failure.

## Failure and stop conditions

Stop immediately on any unauthorized path, staged residue, hash/topology drift,
schema mismatch, test/gate failure, receipt leakage, rollback uncertainty,
provider/network attempt or file-size violation. Findings require a fresh
bounded repair amendment, independent review and fresh human R2.

## Evidence and claim ceiling

Allowed claim after independent final review: this project has a deterministic
local runner that validates and simulates reviewed argv/byte plans before R2,
then applies exact authorized bytes and records fail-closed local gate truth.

Disallowed claims include: no future mechanical failure is possible; failed R2
can be retried; CVF governs AI behavior; the runner is production-ready; or P3
is complete.

## Independent authorization review

The REVIEWER must reproduce the exact-eight ceiling, inspect every SPEC
requirement/acceptance criterion, validate the zero-call/non-policy boundary,
check the file split against the 300-line hard limit, and return explicit PASS
or FAIL with findings and waivers. BUILD is forbidden before PASS is pushed.

## Fresh exact R2 calculation

After this file is frozen and independently reviewed:

```powershell
$wo = 'docs/work_orders/GOVERNED_PLAN_RUNNER_WORK_ORDER.md'
$woSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $wo).Hash.ToLowerInvariant()
$ack = "Tôi phê duyệt R2 cho GOVERNED-PLAN-RUNNER-2026-08-04, Work Order SHA-256 $woSha, đúng 8 BUILD paths, zero provider/network/remote-ingest calls."
$ackSha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData(
  [Text.Encoding]::UTF8.GetBytes($ack)
)).ToLowerInvariant()
$ack
$ackSha
```

The exact printed single line and UTF-8 digest must be copied into the
governance authority surfaces only after the independent review and pushed
authority checkpoint. Any character, whitespace, path count or digest change
requires rejection and recalculation; chat intent is not a substitute.
