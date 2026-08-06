# Governed Plan Runner — Independent BUILD Review

- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Role: `REVIEWER` (independent from the implementation worker)
- Risk / phase: `R2 / REVIEW`
- Reviewed source HEAD: `f338a90510e8cacce57c37f1782fa86e43051159`
- Work Order SHA-256: `352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`
- Calls: `0 provider / 0 network / 0 remote-ingest`
- Disposition: `REVIEW_CHANGES_REQUIRED`
- Waivers: `NONE`

## Scope and evidence

The review inspected all exact-eight BUILD paths against SPEC R1-R20 and
AC-1 through AC-10. It ran only local system-Python tests and read-only probes.

- `HEAD == origin/main`: PASS at `f338a90510e8cacce57c37f1782fa86e43051159`.
- Focused tests: `52 passed, 1 skipped`.
- File-size guard: PASS.
- `git diff --check`: PASS.
- Exact-eight BUILD files: present and unstaged.
- Canonical fresh R2 / acknowledgment checkpoint: FAIL; active state still has
  `freshR2Accepted: false`, `authorityCheckpointCommit: null`, and says no BUILD
  path is authorized before the acknowledgment.

Passing unit tests do not override the findings below because direct probes
reproduced unsafe acceptance cases not covered by those tests.

## Blocking findings

### GPR-BUILD-F1 — R8/R11 authority and repository bindings are not verified

`scripts/run_governed_plan.py::_verify_preconditions` only simulates mutations
and checks gate availability. It does not verify the Work Order file hash,
authority checkpoint, acknowledgment acceptance, acknowledgment literal/digest,
Git HEAD/origin, or exact dirty/staged topology. `apply` calls this incomplete
function and can therefore write after receiving invented binding strings.

Evidence: `scripts/run_governed_plan.py:49-53`, `75-79`; SPEC R8 and R11.

Direct probe: a plan whose acknowledgment literal is `NOT THE HASHED TEXT` and
whose digest is `111...111` parsed successfully. The parser validates only the
digest shape at `scripts/_governed_plan_contract.py:240-245`.

Impact: CRITICAL. The runner's central claim—fail-closed proof of approval and
repository state before mutation—is not implemented.

### GPR-BUILD-F2 — `sourceHead` contract is incompatible with Git HEAD

The contract validates `sourceHead` with the 64-hex SHA-256 validator at
`scripts/_governed_plan_contract.py:273-276`. The current Git commit is a
40-hex object id. A direct probe rejected the real HEAD with
`PLAN_SOURCE_HEAD`, while accepting a synthetic 64-hex value.

Impact: HIGH. A real repository HEAD cannot satisfy the schema, while a fake
SHA-shaped string can.

### GPR-BUILD-F3 — Zero-network is declarative, not capability-enforced

The contract fixes call-budget integers to zero but allows network/package
manager executables. A direct probe accepted
`["curl", "https://example.com"]`. Gate execution inherits the complete host
environment and runs the argv (`scripts/_governed_plan_engine.py:166-172`).
Nothing blocks `curl`, `git fetch`, `pip`, `uv`, or equivalent clients.

Impact: CRITICAL for the promised zero-network execution boundary. The exact
historical class of accidental package installation/network use remains
possible.

### GPR-BUILD-F4 — Resume does not verify immutable bindings/current hashes

Resume checks only the prior receipt byte hash, then checks that prior gate ids
are a subset of current gate ids (`scripts/run_governed_plan.py:99-119`). It
does not compare prior plan/Work Order/authority/R2/HEAD/dirty/staged/mutation
or ordered-gate bindings with the current plan. The receipt path supplied on
the CLI is also not constrained to the repository. Prior receipt JSON has no
strict receipt schema/status validation
(`scripts/_governed_plan_engine.py:286-299`).

Impact: HIGH. A hash-bound but semantically unrelated receipt can influence a
resume, contrary to SPEC R18 and AC-6.

### GPR-BUILD-F5 — Receipt evidence can report unverified post-state

`_mutation_hash_map` assigns the planned post-hash as `actualSha256` whenever
the status is `APPLIED`, without rereading the files after gates
(`scripts/run_governed_plan.py:71-72`). Gates may change those files. Receipt
gate records also omit the required argv binding. Output is truncated before
sanitization and hashing (`scripts/_governed_plan_engine.py:180-184`), so the
stored digest is not a digest of the full sanitized output required by R15-R16.

Impact: HIGH. The receipt can overstate actual filesystem and evidence truth.

### GPR-BUILD-F6 — Outer timeout and timeout cleanup are incomplete

The CLI exposes no caller-declared outer timeout and does not enforce it,
contrary to R7. On Windows, process-tree termination ignores `taskkill` result,
then waits without a timeout (`scripts/_governed_plan_engine.py:155-179`).

Impact: MEDIUM/HIGH. A timed-out gate can hang the runner and the required
outer execution budget is not proven.

### GPR-BUILD-F7 — Rollback is not fail-safe for write-phase exceptions

`apply_mutations` catches only `OSError` (`scripts/_governed_plan_engine.py:
222-246`). An independent injected second-write `RuntimeError` escaped and left
the first file changed (`FIRST_FILE_RESTORED=False`). The transaction also
rereads pre-bytes after simulation without verifying that they still match,
does not verify every successful final post-hash, and can leave a fixed-name
temporary file after failure.

Impact: CRITICAL. R12 requires rollback for a write-phase exception, not only
one Python exception subclass; partial mutations may survive a failed apply.

## Material test gaps

- The zero-write filesystem assertion compares the same post-run enumeration
  to itself (`tests/unit/test_governed_plan_engine.py:74-83`).
- Tests use synthetic mismatched acknowledgment hashes and synthetic 64-hex
  `sourceHead` values as successful fixtures, encoding F1/F2 as expected
  behavior.
- The A28 fixture carries synthetic Work Order/source/mutation bindings rather
  than demonstrating the actual historical repository bindings.
- No adversarial tests prove rejection of network/package-manager argv, forged
  canonical authority, full resume-binding drift, post-gate mutation drift, or
  caller-declared outer-timeout absence.

## Cost/value decision

These findings are worth fixing because F1-F5 and F7 invalidate the main security and
governance value of the runner; they are not cosmetic edge cases. Conversely,
running the full repository suite now has low value: the focused suite already
passes while direct contract probes fail. Stop-first disposition avoids further
latency until a bounded repair amendment addresses the blocking semantics.

## Required next move

Do not commit or FREEZE the exact-eight candidate. Create one bounded repair
amendment covering F1-F7 and the corresponding adversarial tests, obtain
independent authorization review and a fresh exact R2, then run one repair
sequence. The existing candidate must remain preserved and unstaged until the
human chooses repair or discard; it cannot be cleanly parked on `main` as a
valid BUILD result under the current evidence.
