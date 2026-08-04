# ADR — Governed Plan Runner

- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Date: `2026-08-04`
- Risk: `R2`
- Control-chain transition: `INTAKE -> DESIGN`
- Status: `DESIGN_PROPOSED_PENDING_INDEPENDENT_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## INTAKE

### Intent

Create a small, versioned, project-local Python runner that catches mechanical
execution defects before human R2 approval and executes an approved machine
plan without ad-hoc shell text. The operator explicitly requested immediate
helper-based acceleration because P3-A spent disproportionate latency on
PowerShell parsing, Windows wildcard behavior, guessed selectors, wrong script
names, UTF-8 transport, timeout ceilings, line-ending drift and indentation.

### Request boundary

This tranche may add only the runner contract, engine, CLI, schema, tests and
one historical regression plan. It does not alter Refinery/product behavior,
CVF core, `.cvf/policy.json`, `AGENTS.md`, approval risk levels, phase gates,
independent review requirements or the meaning of a consumed R2 invocation.
It makes no claim that a failure after approval can be retried without fresh
authority. Any such semantic change is a separate governed policy tranche and,
if intended for the shared template, requires upstream CVF core authority.

### Evidence boundary

The runner governs deterministic local file and process orchestration only.
It must make no provider, network, remote-ingest or POST call. Its tests do not
assert that CVF controls AI/agent behavior, so no live-provider evidence is
required for this bounded tranche.

### Risk classification

R2 applies because the runner will enforce approved mutations and evidence
gates. The main risks are path escape, executing unintended shell syntax,
partial writes, stale-plan execution, secret leakage in receipts and an
incorrect resume that reruns a completed or failed gate.

## DESIGN transition

INTAKE is complete: intent, scope, exclusions, risk and evidence boundaries are
explicit. The tranche now enters DESIGN; no BUILD authority is implied.

## Decisions

1. Use CPython `>=3.11` and the standard library. Commands are non-empty argv
   arrays passed with `shell=False`; command strings are invalid.
2. The plan is versioned canonical JSON. All repository paths use normalized
   POSIX-relative syntax. Absolute paths, drive-qualified paths, `..`, empty
   components, backslashes, symlinks and glob metacharacters are rejected.
3. `validate` and `dry-run` are zero-write operations intended to run before
   authorization review and human R2. They verify the proposed acknowledgment
   literal/digest self-binding, but do not require or represent its human
   acceptance. They also verify schema, artifact hashes, dirty/staged topology,
   executable/script existence, pytest collection, timeout budget, exact
   replacement occurrence counts and simulated post bytes/hashes without
   invoking any declared evidence gate.
4. Mutations are exact byte replacements. Old/new bytes are base64-encoded;
   each mutation binds an exact pre-hash, post-hash and occurrence count. This
   preserves all unspecified bytes, including CRLF/LF and indentation.
5. Apply precomputes and validates every output in memory before writing. Each
   output is written through a same-directory temporary file and atomic
   replacement. Any write-phase failure rolls all authorized mutation paths
   back to their exact pre-bytes and records rollback truth.
6. Gates execute in declared order with explicit cwd, environment additions
   and per-gate timeout. The runner requires a declared outer budget at least
   the plan's computed minimum plus grace; later gates remain `NOT_RUN` after
   the first non-zero exit or timeout.
7. The receipt is canonical, UTF-8/LF, sorted-key JSON. It binds schema, plan
   and Work Order digests, authority/R2 acknowledgment digests, HEAD, topology,
   mutation hashes, gate argv/status/exit and sanitized stdout/stderr digests.
   It excludes timestamps, durations, environment dumps and raw secret-like
   output so identical controlled outcomes have identical receipt bytes.
8. Resume accepts a prior receipt only when the new reviewed plan explicitly
   references its digest. It rejects repository/plan/mutation drift and may run
   only gates previously marked `NOT_RUN`; `PASS`, `FAIL` and `TIMEOUT` gates
   can never be rerun by resume.
9. Implementation is split before BUILD. Every new Python file targets at most
   250 lines and must remain below the existing 300-line hard limit; no file
   size exception or debt-baseline entry is permitted.

## Alternatives rejected

- More inline PowerShell: repeats the transport and parser failure class.
- Shell command strings with quoting rules: platform-dependent and permits
  accidental expansion.
- Semantic JSON rewriting for byte-bound repairs: can alter indentation,
  ordering or line endings outside the approved bytes.
- Automatic retry after a failure: changes approval semantics and is outside
  this tranche.
- A CVF core edit: unnecessary for a project-local prevention tool and violates
  the downstream isolation boundary.

## Consequences

Authorization artifacts become slightly more structured, but review gains a
machine-checkable plan and a zero-write rehearsal before R2. Mechanical defects
should be rejected during DESIGN/WORK_ORDER review rather than consuming an
approved BUILD invocation. Fail-closed behavior after approval remains intact.

## Proposed exact R2 acknowledgment

Frozen Work Order SHA-256:
`352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`.

Exact proposed single line:

> Tôi phê duyệt R2 cho GOVERNED-PLAN-RUNNER-2026-08-04, Work Order SHA-256 352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327, đúng 8 BUILD paths, zero provider/network/remote-ingest calls.

UTF-8 SHA-256 of that line (without a trailing newline):
`89dac0864b10327c4528905394e5e891c4b22bdf9ae2fc8504afbb87a49b9028`.

The Work Order contains the reproducible calculation procedure. No
acknowledgment is accepted before independent authorization review passes and
the governance-only authority checkpoint is pushed.
