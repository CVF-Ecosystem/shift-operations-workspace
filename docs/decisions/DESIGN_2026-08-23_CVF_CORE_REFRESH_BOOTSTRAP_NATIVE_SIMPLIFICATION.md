# DESIGN Amendment — Bootstrap-Native CVF Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_DESIGN_REVIEW`
- Authority: operator directed removal of low-value over-engineering and focus
  on the blocked project lane.

## Decision

Use the repository's sanctioned bootstrap path as the only implementation:

1. run the existing public-Core reconciler;
2. run `scripts/initialize_cvf_clone.ps1`, accepting its built-in doctor as the
   worker's post-refresh doctor result;
3. have the independent completion reviewer run the doctor once after a
   successful worker return;
4. return to the parked P4-C authorization rereview after Core refresh closes.

There is no separate worker-owned doctor after the initializer.

The custom eight-outcome/two-surface evidence contract, synthetic corpus,
trace2/packet ancestry model, byte-frozen runner and adapter are rejected as
disproportionate to this documentation-only Core update. They remain historical
evidence and are not executable inputs to the simplified path.

## Retained safety boundary

- Frozen public target:
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`.
- Public remote only:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`.
- Use only the existing reconciler, initializer and doctor scripts.
- Preserve the already accepted exact `17` workspace-root effect ceiling,
  `12` downstream worker-path ceiling and `10` mutable carriers.
- Preserve preexisting dirty downstream bytes, all ten mutable-carrier
  preimages, all 17 root-target existence/byte preimages and the old Core before
  mutation. On any failure, rollback must restore and verify the old Core, the
  captured existence/bytes of all 17 root targets and the bytes of all ten
  carriers before returning failure; preserved backups/evidence are not
  deleted.
- The operator assessment is excluded without opening, reading, hashing,
  inventorying, staging or using it.
- No credentials, provider call, package installation, database, deployment,
  commit or push.

## Minimum useful evidence

Evidence is proportional to the actual risk and consists only of:

- preflight Core `HEAD`, `origin/main`, remote and clean status;
- preflight downstream `HEAD`, `origin/main`, staged-empty state and exact
  non-assessment dirty-path list;
- preimages/hashes for affected root files and mutable downstream carriers;
- one transcript and exit code for each sanctioned script invocation;
- post-run Core/manifest/binding/AGENTS pin equality;
- post-run doctor result;
- actual root/downstream changed-path comparison against the retained ceilings;
- on failure, rollback result and preservation of the old Core/preexisting
  downstream bytes, including explicit `17/17` root and `10/10` carrier restore
  verification.

## Minimal network graph

The successful worker path permits exactly the three public Git operations
already inherent in the first two sanctioned scripts: reconciler clone,
initializer fetch and initializer-owned doctor fetch. The worker does not run a
fourth doctor operation. After success, the independent completion reviewer
owns exactly one fresh doctor invocation and therefore one separate public
fetch.

A failed worker records only the actually reached zero-to-three prefix. After
restoration it permits exactly one rollback-verifier doctor invocation; failure
never becomes success, and no completion-review doctor runs for that failed
attempt. Every permitted network operation is unauthenticated, targets only the
exact public remote, and stops if the advertised `main` target differs from the
frozen target. Plain script transcripts, exit codes and the final doctor result
are sufficient evidence; trace ancestry is not required.

The worker return is concise Markdown with links to raw local evidence under a
single contained `_cvf-core-backups` directory. It makes no claim about kernel
ancestry, continuous absence, immutable audit storage, AI governance, provider
behavior, deployment or production readiness.

## Review and latency contract

One independent authorization review checks the exact commands, ceilings,
rollback steps and evidence checklist. One independent completion review reruns
the doctor and direct post-state/path checks. No synthetic outcome corpus,
duplicate semantic matrix, validator-of-validator, exhaustive trace lineage or
additional rereview loop is required unless execution exposes a new safety-
relevant root cause.

Quota and latency are acceptance constraints: evidence that does not protect
the retained path, rollback, target, credential or external-effect boundaries
is out of scope.

## Phase routing

After independent DESIGN PASS, SPEC will express the checklist above as a
small set of testable requirements and explicitly retire the evidence-contract
matrix from this tranche. WORK_ORDER then authorizes the exact scripts and
retained ceilings. This DESIGN does not itself authorize network or BUILD.

## Target-rebase amendment — 2026-08-24

Following the verified `TARGET_MOVEMENT` rollback and accepted INTAKE
amendment, the frozen public target is rebased from `3b031fec...` to
`864c4e0e6139f3e32067dea41f43f240e505c0d8`. The sanctioned two-script design,
minimal success graph, failure-prefix plus one rollback-verifier doctor,
`17/12/10` ceilings, full preservation-first rollback and direct evidence
remain unchanged. Execution must still stop and roll back if advertised
`main` differs from this new frozen target.

## Pin-carrier sequencing repair — 2026-08-24

The target-rebased attempt proved one bootstrap ordering gap: the reconciler
installs the new Core but does not update this portable schema v2 manifest, and
the initializer consumes rather than changes `cvfCoreCommit`. Therefore, after
the reconciler exits zero and direct checks show clean Core
`HEAD == origin/main == 864c4e0...`, the worker must locally replace exactly:

1. `.cvf/manifest.json` `cvfCoreCommit`; and
2. the `AGENTS.md` `CVF Commit` header,

from the old full pin to the new full pin before invoking the initializer.
Each replacement must occur exactly once or trigger rollback. This uses two of
the already-authorized ten carrier paths, adds no network operation and makes
the initializer/doctor equality contract reachable. Normal post-command
continuity, Project Knowledge and direct evidence synchronization remains
inside the existing carrier ceiling. All other design boundaries are unchanged.

## Completion F1 acceptance amendment — 2026-08-24

With explicit operator approval, completion no longer requires an unavailable
BUILD-start byte preimage for each of the 33 dirty paths outside the ten carrier
surfaces. It instead requires the already-recorded frozen 39-path/status set and
digest, unchanged membership/status for those non-carriers, exact command and
local-patch transcripts, the exact 12-path worker ceiling, and absence of any
new dirty path outside that ceiling. The ten mutable carriers retain full byte
preimage/postimage proof.

This amendment does not assert byte equality for the 33 non-carrier paths; that
claim is explicitly withdrawn. It accepts only that no observed path/status or
authorized command/patch surface indicates worker mutation there. All Core,
pin, root, carrier, command, doctor and prohibited-effect requirements remain
unchanged. BUILD and the reviewer doctor are not rerun.
