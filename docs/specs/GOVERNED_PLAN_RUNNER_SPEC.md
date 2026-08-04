# Governed Plan Runner Specification

- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Risk / phase: `R2 / SPEC`
- Status: `PENDING_INDEPENDENT_SPEC_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## 1. Purpose and claims

The implementation MUST provide a project-local deterministic runner for
machine-readable mutation and evidence plans. It prevents known mechanical
failures before R2 when they are detectable by validation or byte simulation.
It MUST NOT change approval, retry, stop-first, independent-review or CVF core
semantics. It MUST NOT claim that all future mechanical failures are impossible.

## 2. Plan contract

R1. A plan MUST be UTF-8 JSON with `schemaVersion: "1.0"`, unique `planId`,
Work Order path/SHA-256, exact authority binding, proposed acknowledgment
literal/SHA-256, source HEAD, exact dirty/staged path arrays, call budget fixed
to zero, mutation list, ordered gate list, receipt path and timeout budget.

R2. Unknown fields MUST fail closed at every contract object. Lists whose order
is semantic MUST retain order; path sets MUST be unique and ordinal-sorted.

R3. Every path MUST be a normalized repository-relative POSIX path. The runner
MUST reject absolute/UNC/drive-qualified paths, backslashes, `.`/`..`, empty
components, NUL, symlinks and `*`, `?`, `[` or `]` glob characters. Resolution
MUST remain under the resolved repository root.

R4. Each mutation MUST contain one path, SHA-256 pre/post bindings, base64
`oldBytes`/`newBytes`, and exact positive `occurrences`. Duplicate mutation
paths and overlapping ambiguous replacements MUST fail validation.

R5. Each gate MUST contain a unique ordinal id, argv array, repository-relative
cwd, explicit environment additions, positive timeout seconds and output limit.
argv MUST be passed directly with `shell=False`. Empty argv, shell built-ins,
PowerShell/cmd/bash/sh launchers and redirection/control tokens MUST fail.

R6. A pytest gate MUST use explicit files/node ids, never globs. Dry-run MUST
derive and run a zero-test-execution `--collect-only` command and prove every
requested node/file resolves. Script arguments ending in `.py` MUST resolve to
regular files. The first executable MUST resolve via the current interpreter or
`PATH` without downloading/installing anything.

R7. `requiredOuterTimeoutSeconds` MUST be at least the sum of per-gate timeouts
plus a documented fixed grace. Apply/run MUST require a caller-declared outer
budget not less than this value and record the declared value. This is a
fail-fast contract check, not a claim that an external tool cannot terminate.

## 3. Validate and dry-run

R8. `validate PLAN` MUST parse/validate only and write zero bytes. `dry-run PLAN`
MUST additionally verify plan/Work Order/authority hashes, proposed R2 literal
and digest self-consistency, HEAD, exact dirty and staged topology,
path/executable/collection availability and current mutation preconditions.
Preapproval dry-run MUST NOT require or claim human R2 acceptance. Neither mode
may execute evidence gates.

R9. Dry-run MUST read targets as bytes, require exact pre-hashes and occurrence
counts, simulate replacements in memory, then require exact post-hashes. It MUST
report old/new occurrence counts plus CRLF, LF and leading-space deltas so
newline and indentation changes are review-visible. No text-mode write is
allowed.

R10. Any validation/dry-run failure MUST exit non-zero with zero target/receipt
writes. Diagnostics MUST name a stable error code and sanitized path/gate id.

## 4. Apply and gates

R11. Apply MUST repeat every R8-R9 check and additionally require canonical
continuity to contain the exact accepted acknowledgment literal/digest and
pushed authority/acknowledgment checkpoints. It MUST precompute all final bytes
before creating temporary files. A same-directory temporary file MUST be
flushed, fsynced where supported and atomically replace its target.

R12. Before the first write, exact pre-bytes for all mutation paths MUST be held
for rollback. A write-phase exception MUST restore every already-replaced path,
verify all restored pre-hashes and emit `APPLY_ROLLED_BACK` or
`ROLLBACK_FAILED`. Gate failure does not roll back a successfully applied,
authorized candidate.

R13. Gates MUST run once in order. On the first non-zero exit, timeout or runner
exception, that gate receives `FAIL`, `TIMEOUT` or `ERROR`; every later gate is
`NOT_RUN`. A timeout MUST terminate the owned process tree without targeting
unrelated processes.

R14. The runner itself MUST contain no provider/network/remote-ingest client and
MUST never invoke a shell. The bounded Work Order gate argv is independently
reviewed for the zero-call claim.

## 5. Receipt and resume

R15. Receipt JSON MUST use UTF-8, LF, sorted keys and compact deterministic
separators. It MUST bind plan/Work Order/authority/R2/HEAD/topology, every
mutation pre/post/actual hash, rollback status and each gate's argv, status,
exit code, stdout/stderr SHA-256 and sanitized bounded tail.

R16. Receipt MUST omit timestamp, duration, inherited environment and absolute
host paths. Sanitization MUST replace secret-like bearer/JWT/API-key patterns
before both hashing and storing output; the raw output MUST not be persisted.

R17. Receipt writes MUST themselves be atomic. Receipt path MUST be explicitly
authorized by the plan. A receipt write failure after a gate MUST return error
without changing historical gate truth in memory or rerunning anything.

R18. `resume PLAN --receipt PRIOR` MUST require exact prior-receipt SHA in the
reviewed plan and verify all immutable bindings/current hashes. It MUST reject
any drift and MUST select only prior `NOT_RUN` gates. It MUST reject attempts to
rerun `PASS`, `FAIL`, `TIMEOUT` or `ERROR` gates.

## 6. CLI and modularity

R19. CLI subcommands are exactly `validate`, `dry-run`, `apply` and `resume`.
Unknown options fail. Exit codes MUST distinguish contract, precondition,
apply/rollback, gate and receipt failures.

R20. Implementation MUST be split into CLI, contract and engine modules. Each
new Python source/test file MUST target <=250 lines and MUST remain <=300 lines.
No exception/debt entry is allowed.

## 7. Acceptance criteria

AC-1. Contract tests reject every R2-R7 unsafe shape, including a path with
spaces that remains valid and is passed as one argv item.

AC-2. Dry-run exact-byte tests cover single-occurrence success, zero/multiple
occurrence rejection, post-hash mismatch, two-space indentation correction and
mixed CRLF/LF preservation with zero writes.

AC-3. Apply tests prove all outputs are precomputed, success uses atomic
replacement, injected second-write failure restores all pre-hashes and a gate
failure retains the successfully applied candidate.

AC-4. Process tests prove `shell=False`, explicit argv/cwd/env, missing
executable/script and invalid pytest selection are rejected before apply/R2
execution, and timeout marks later gates `NOT_RUN` after owned-tree cleanup.

AC-5. Receipt tests prove canonical byte-identical output for identical inputs,
secret sanitization before hash/storage, bounded tails and atomic write failure.

AC-6. Resume tests reject plan/receipt/HEAD/topology/hash drift and any request
to rerun a non-`NOT_RUN` gate; exact never-run suffix execution passes.

AC-7. Historical A28 regression plan proves a two-space-only simulated repair
and locks the expected pre/post occurrence, indentation and newline metrics.

AC-8. Focused runner tests, full non-live suite, repository validator, session,
file-size, JSON/schema, secret scan and `git diff --check` pass. All eight BUILD
paths are exact; staged paths are zero before BUILD commit.

AC-9. Provider/network/remote-ingest calls are exactly zero. No live AI
governance claim or provider evidence is made.

AC-10. Independent BUILD review compares plan contract, source, tests, receipt
behavior and exact changed set before any BUILD commit/FREEZE.

## 8. Out of scope

CVF core/template edits, policy changes, automatic retry, automatic approval,
provider gating, production execution, arbitrary shell compatibility, package
installation and changes to P3-A/P3-B/P3-C product code are excluded.
