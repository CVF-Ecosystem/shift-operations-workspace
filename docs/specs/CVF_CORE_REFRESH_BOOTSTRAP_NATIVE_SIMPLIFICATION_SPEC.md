# SPEC — Bootstrap-Native CVF Core Refresh Simplification

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Phase: `SPEC`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_SPEC_REVIEW`
- DESIGN:
  `docs/decisions/DESIGN_2026-08-23_CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION.md`
- Accepted DESIGN raw SHA-256:
  `7a6634c831013b55464d61cb32cc020b5f64eeca704dea5213e182a27aee9efa`

## Requirements

### S1 — Fixed source and target

The only remote is
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`; the only
accepted target is `3b031fec35473e6ee6a554c4c72400e7a23b06c5`. Every fetch/clone is
unauthenticated and stops on target movement.

### S2 — Exact worker commands

The worker runs only, in order:

1. `powershell -ExecutionPolicy Bypass -File "<core>\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "<workspace-root>"`
2. `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`

There is no extra worker doctor; the initializer's built-in doctor is the
worker post-refresh doctor.

### S3 — Preflight

Before mutation, require downstream staged set empty, `HEAD == origin/main`,
Core clean at the recorded old pin, the reconciler hash unchanged, exact remote
and fetched target unchanged. Record the exact non-assessment downstream dirty
path set without opening, reading, hashing or inventorying the assessment.

### S4 — Recovery preimages

Before mutation, preserve the complete old Core, existence/bytes for all exact
17 workspace-root targets, and bytes for all exact ten mutable downstream
carriers inside one containment-checked `_cvf-core-backups` directory.

### S5 — Path ceilings

Workspace-root effects remain exactly the parent Work Order's 17 paths.
Downstream worker changes remain within its exact 12 paths: the first ten are
mutable carriers and the last two are worker evidence. No other project or
workspace-root path may change.

### S6 — Successful network ceiling

Success contains exactly three worker-owned public Git operations already
performed by S2: reconciler clone, initializer fetch and initializer-owned
doctor fetch. After worker success, the independent completion reviewer runs
the exact doctor command once and owns one separate public fetch.

### S7 — Failure and rollback

A failed S3 preflight is a refusal: it stops with zero external effect, zero
mutation and no rollback doctor. Only after worker mutation or external
execution begins does failure record the reached `0..3` worker prefix, restore
and verify the old Core, `17/17` captured root existence/bytes and `10/10`
carrier bytes, preserve backups/evidence, then run exactly one rollback-
verifier doctor. Failure never becomes success and has no completion-review
doctor.

### S8 — Minimum evidence

Evidence consists only of pre/post Git/pin/path observations, preimage hashes,
plain transcripts and exit codes for sanctioned script invocations, doctor
result, actual changed-path comparison and rollback verification when needed.
It is stored under the contained backup directory plus a concise Markdown
worker return. No trace2/packet ancestry, synthetic corpus, frozen adapter,
byte-frozen runner or validator-of-validator is required.

### S9 — Success state

Success requires Core `HEAD == origin/main == manifest.cvfCoreCommit ==
local-binding.resolvedCoreCommit == AGENTS CVF Commit == target`, Core clean,
doctor PASS, staged set empty, exact path ceilings respected, and preserved
preexisting downstream bytes outside authorized carriers.

### S10 — Independent completion review

The reviewer directly reruns the doctor once, recomputes S9 and changed paths,
checks the worker transcript/exit evidence and returns PASS or findings. It does
not create another evidence framework or repeat already proven static checks.

### S11 — Prohibited effects and claims

Credentials, provider calls, dependency installation, database, deployment,
commit and push are forbidden. Evidence proves only this local Core refresh;
it does not prove AI governance, provider behavior, kernel ancestry, immutable
audit storage, deployment or production readiness.

### S12 — Latency and quota

No check may be added unless it protects target/remote, path ceiling, rollback,
credentials or a required phase gate. Duplicate doctor calls, duplicate
semantic models and repeated review of unchanged evidence are failures of this
SPEC.

## Acceptance criteria

- `AC1`: S1-S5 preflight and preimages PASS before the first external effect.
- `AC2`: success shows exactly the S6 graph, all exits zero and S9 equality.
- `AC3`: preflight refusal stops zero-effect; any post-execution failure
  satisfies the restore-and-verifier branch of S7 before returning control.
- `AC4`: worker return contains every S8 item and no prohibited evidence layer.
- `AC5`: independent review satisfies S10 with findings/waivers explicit.
- `AC6`: assessment exclusion and all S11-S12 boundaries remain intact.

## Historical evidence-contract disposition

The earlier `CVF-CORE-REFRESH-EVIDENCE-CONTRACT` matrix, adapter, runner and
8x2 Work Order amendment remain byte-exact historical review evidence but are
non-operative for this simplified path. No new shared receipt model, outcome-
controlled schema or multiple validator surface is introduced; invariant-
family applicability for this SPEC is therefore `NOT_APPLICABLE`.

This SPEC does not authorize network or BUILD. A bounded Work Order and
independent authorization review remain required.

## Target-rebase amendment — 2026-08-24

Accepted DESIGN raw SHA-256 is now
`3028a5741cd28a8f3868d267e882660704064497b32833797734a2c84552a24d`.
For S1 and every dependent equality or movement check, the accepted target is
`864c4e0e6139f3e32067dea41f43f240e505c0d8`, superseding `3b031fec...` only
for the next attempt. S2-S12 and AC1-AC6 otherwise remain unchanged. Any
different advertised `main` triggers the existing stop/rollback branch.

## Pin-carrier sequencing repair — 2026-08-24

Accepted DESIGN raw SHA-256 is now
`695565e6ab9137f6d6366a9e683d176a6225140462ca5ae3d100911681d02c35`.
After the reconciler exits zero and before initializer invocation, require:

- Core is clean and `HEAD == origin/main == 864c4e0...`;
- exactly one old-full-pin occurrence is replaced by the new full pin in the
  `.cvf/manifest.json` `cvfCoreCommit` value;
- exactly one old-full-pin occurrence is replaced by the new full pin in the
  `AGENTS.md` `CVF Commit` header; and
- both files parse/match the target before initializer starts.

Zero or multiple matches, write failure, parse failure or target movement uses
the existing post-execution rollback branch. This local step adds no public
operation and remains covered by S5/S7 carrier preimages. AC2 additionally
requires the two replacements before command 2 and final four-way pin equality.
All other S/AC clauses remain unchanged.

## Completion F1 acceptance amendment — 2026-08-24

Accepted DESIGN raw SHA-256 is now
`0db70eb33acbfbe5e0e0a449846d370da43e8de71519b26885dfa539f6c877d8`.
For the 33 frozen dirty paths outside the ten carriers, S9 no longer requires
unavailable BUILD-start byte hashes. Replace only that predicate with:

1. the canonical frozen 39-path/status set and LF digest match the authorized
   baseline;
2. all 33 non-carrier members and statuses remain present unchanged;
3. command transcripts, the scoped local-pin record and direct changed-path
   comparison expose no worker surface outside the exact 12 paths; and
4. no new dirty path exists outside the exact worker ceiling.

Ten-carrier byte preimage/postimage and all other S/AC requirements remain
mandatory. Completion explicitly does not claim byte equality for the 33
non-carriers. The prior successful BUILD and sole completion doctor are fixed
evidence and must not be rerun for this amendment.
