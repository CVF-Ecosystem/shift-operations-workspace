# Independent Authorization Review — P4-C full-suite external-failure acceptance amendment

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Reviewer role: `INDEPENDENT_AMENDMENT_AUTHORIZATION_REVIEWER`
- Reviewed packet SHA-256:
  `19a82ca0f251841ad2d701444724e3dfe3957739c8122ece57d140ee447fc8c4`
- Review date: `2026-08-25`
- Findings: `P4C-A2-AUTH-F1..F2 OPEN`
- Waivers: `NONE`
- Disposition: `AMENDMENT_AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

## Read-only evidence

No full suite, fetch, provider call, install, deployment, database action,
commit or push was performed. The Operations sibling remains clean and
unstaged at branch `main`, with
`HEAD == origin/main == 3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a`.
Read-only `git cat-file` checks still return exit 128 for both `f99b3bf...`
and `a944b72e...`.

The exact XR1 test source attempts `git cat-file -t f99b3bf...` before it
reads the sibling contract. Therefore the currently proved missing-object
failure precedes P4-C behavior. The completion review already accepted the
exact-67 implementation, its Knowledge pins and both invariant families.
This amendment authorizes no changed path or contract mutation. The session
guard and invariant-family guard pass in this review.

The packet correctly limits the exception to one fully qualified XR1 node,
requires the P4-A1 timing node to pass in the same amended run, expects
`2836 passed, 132 skipped, 1 deselected`, preserves every other test and
guard, and retains XR1 as unresolved environmental debt. This bounded test
acceptance does not create a CVF governance-behavior claim, so no live
provider proof is required.

## Findings

### P4C-A2-AUTH-F1 — The sole amended full-suite command is not executable-exact

The SPEC forbids every additional deselection/filter, but the WORK_ORDER does
not state the exact command that the reviewer is authorized to execute. It
only refers to “the amended full-suite command.” Add the complete command,
including exactly:

`--deselect tests/integration/test_xr1s_workspace_link_descriptor.py::test_operations_authorized_contract_is_reciprocal_when_sibling_present`

and prohibit all other selection, ignore, marker, keyword, max-failure or
collection-altering options. Without an exact command, the claimed one-node
boundary cannot be reproduced from the authorization packet alone.

### P4C-A2-AUTH-F2 — Mandatory doctor evidence conflicts with zero network effect

A2-R5 retains workspace-doctor evidence as mandatory while A2-R6 authorizes
zero network effect. The repository's doctor executes `git fetch origin main`
against the shared Core, so a fresh doctor run would violate the amendment's
network boundary and can also update Git metadata. The WORK_ORDER does not say
whether the already accepted doctor receipt may be retained or whether a new
run is required.

Resolve the ambiguity without expanding the zero-network boundary: explicitly
retain the accepted doctor evidence from the existing completion review and
forbid a doctor rerun under this amendment, while requiring the local Core
pin/HEAD/origin checks and all genuinely deterministic offline guards. If a
fresh doctor is instead required, that is a boundary change needing separate
network authority.

## Disposition

`AMENDMENT_AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

Return only `P4C-A2-AUTH-F1..F2` for bounded packet repair and independent
rereview. No amended test run or P4-C `REVIEW_PASS`/FREEZE is authorized yet.
The single XR1 node remains unresolved, and findings/waivers are
`P4C-A2-AUTH-F1..F2 OPEN` / `NONE`.

## Bounded amendment authorization rereview — F1–F2

- Repaired packet SHA-256:
  `a00006f2239c371f0d3ee31430a3002067fee6d7917e05f0100e33d051f39119`
- Findings `P4C-A2-AUTH-F1..F2`: `CLOSED`
- Findings: `NONE`
- Waivers: `NONE`
- Disposition: `AMENDMENT_AUTHORIZATION_REVIEW_PASS`

F1 is closed. A2-R3 now supplies the sole executable command:

`python -m pytest -q --deselect tests/integration/test_xr1s_workspace_link_descriptor.py::test_operations_authorized_contract_is_reciprocal_when_sibling_present`

It explicitly prohibits every other collection/filter option, including a
second `--deselect`, `--ignore`, `-k`, `-m`, `--lf`, `--ff` and `--maxfail`.
The WORK_ORDER binds the reviewer to this exact A2-R3 command.

F2 is closed without expanding the network budget. A2-R5 retains the accepted
`24 PASS + 1` bounded-warning doctor receipt and explicitly forbids a doctor
rerun. The replacement offline check passes: the Core worktree is clean, and
Core `HEAD`, local `origin/main`, the manifest pin and the AGENTS header all
equal `9c01832930226f2f770eafa346e01279160f22cb`. Session-state and
invariant-family guards also pass.

Bounded textual comparison confirmed the repair changed only the executable
command/filter prohibition and doctor/offline-equality handling requested by
F1–F2. The exact one-node exception, expected `2836 passed, 132 skipped, 1
deselected`, same-run P4-A1 timing requirement, exact-67 and invariant
contracts, zero changed-file/external-effect ceiling, stop conditions and
unresolved XR1 claim remain unchanged.

No full suite, isolated test, doctor, fetch, provider call, install,
deployment, database action, commit or push was performed during this
rereview. The prior changes-required result remains as history and is
superseded by this bounded PASS. The independent completion reviewer may now
run only the authorized amended evidence sequence; `REVIEW_PASS` still depends
on its observed results.
