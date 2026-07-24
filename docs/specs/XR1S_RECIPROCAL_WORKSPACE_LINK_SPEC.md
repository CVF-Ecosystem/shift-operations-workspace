# Specification: Shift Reciprocal Workspace-Link Authorization (XR1-S)

- Spec id: `SPEC-XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`
- Tranche: `XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`
- Control-chain phase at authoring time: `WORK_ORDER`
- Risk: **R2**
- Status: **REPAIRED — pending independent XR1-S authorization re-review.**
  No BUILD has occurred.
- Design: `docs/decisions/ADR_2026-07-24_XR1S_RECIPROCAL_WORKSPACE_LINK.md`
- Work order: `docs/work_orders/XR1S_RECIPROCAL_WORKSPACE_LINK_WORK_ORDER.md`

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `REVIEW_FAIL` with three findings
(`XR1S-R1` `IMPOSSIBLE_FULL_DOCTOR_PASS`, `XR1S-R2`
`DETERMINISTIC_CATALOG_GATE_CONFLICT`, `XR1S-R3`
`UNNECESSARY_RECONCILER_SIDE_EFFECT`), all repaired without waiver — full
detail in `ADR-2026-07-24-XR1S-RECIPROCAL-WORKSPACE-LINK`'s repair note.
This spec is repaired accordingly: R-11 rewritten as verify-only, no
reconciler run (`XR1S-R3`); new R-36 requires stopping for independent
review if the core has drifted by BUILD time; R-25/R-29 rewritten and new
R-37/R-38 authorize a bounded, conditional catalog-reconciliation ceiling
for `XR1-S-C2b` (`XR1S-R2`); R-31 rewritten and new R-39 repair the
impossible-full-doctor-PASS requirement to the exact `PASS WITH NOTE`
condition (`XR1S-R1`). AC-7, AC-18, AC-19, and AC-21 are corrected to match;
new AC-22/AC-23 bind R-36 and R-37/R-38. Role: `REPAIR_WORKER`. Codex
retains independent `REVIEWER`/`COMMIT_STEWARD` authority; this round does
not self-grant REVIEW_PASS. Status:
`XR1S_AUTHORIZATION_REPAIRED_PENDING_INDEPENDENT_RE_REVIEW`.

This document states intended behavior for two **future** BUILD commits
(`XR1-S-C2a`, `XR1-S-C2b`), neither of which is authorized to begin until
this package and its work order are independently reviewed and `XR1-S-C1`
is committed and pushed. §2 records current, read-only-verified truth so it
is never conflated with intended post-BUILD state.

## 1. Scope

### 1.1 In scope (this authoring round, `XR1-S-C1`)

- Authoring this ADR, this SPEC, and the companion WORK_ORDER.
- Recording the authorization in continuity (`SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json` mirror, `SESSION/SESSION_MEMORY.md`,
  `IMPLEMENTATION_STATUS.json`) and in a new handoff.

### 1.2 In scope (future, gated on independent review of this package)

- `XR1-S-C2a`: verify-only repair of `.cvf/manifest.json`'s `cvfCoreCommit`
  drift — no reconciler run (`XR1S-R3`, §3.3).
- `XR1-S-C2b`: creating `.cvf/workspace-link.json` and its descriptor test,
  plus a bounded, conditional catalog-metric reconciliation limited to the
  exact drift those two files cause, if any (`XR1S-R2`, §3.6, R-37/R-38).

### 1.3 Out of scope

- Any change to `CVF-Operations-Workspace` or the CVF core repository.
- Any change to `P2B-APPROVER-IDENTITY-RECONCILIATION` (ADR, SPEC, WORK_ORDER,
  or its BUILD) — its WORK_ORDER remains `DRAFT — NOT APPROVED`, PARKED by
  this tranche.
- Any change to application source, tests (other than the one new descriptor
  test file at `XR1-S-C2b`), migrations, schema, or data.
- Any change to `docs/catalog/**` beyond the two paths conditionally
  authorized for `XR1-S-C2b` (R-37/R-38), `docs/implementation/EXECUTION_ROADMAP.md`,
  `docs/cvf/CVF_CONTROL_MAPPING.md`, `docs/INDEX.md`, `.gitignore`,
  `AGENTS.md`, or the untracked assessment file.
- Running the sanctioned CVF-core reconciler at `XR1-S-C2a` — the core is
  already reconciled (§2, C-5); re-running it is out of scope (`XR1S-R3`).
- Any provider API call, any read of a real secret, any real Shift
  `scan`/`apply` execution.
- Any claim about AI/agent governance behavior.

## 2. Current implementation truth (verified 2026-07-24, read-only)

| # | Property | Current value |
|---|---|---|
| C-1 | Shift HEAD / `origin/main` | `f98f29e145fa002be070e9d44520d20f0f82dcb3` (equal) |
| C-2 | Shift worktree | clean except the one pre-existing untracked assessment file |
| C-3 | Assessment file SHA-256 | `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2` |
| C-4 | `.cvf/manifest.json` `cvfCoreCommit` | `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` |
| C-5 | Local/public CVF core actual HEAD | `27137db4d9aa2aea931ddd2507185d5c24943080` |
| C-6 | Workspace doctor | `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` — `CVF core commit matches manifest` `[FAIL]` (warn only, C-4/C-5 drift), plus one unrelated `[WARN]` (governed downstream catalog kit not present, bounded legacy compatibility) |
| C-7 | Test baseline | `python -m pytest -q` → `292 passed` |
| C-8 | Operations authorization commit | `74170650bd7f2732bc2eec985e5b891df6d45897` |
| C-9 | Operations post-push continuity commit | `3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a` (Operations `HEAD == origin/main`) |
| C-10 | Ordering | C-8 is an ancestor of C-9 |
| C-11 | Operations `IMPLEMENTATION_STATUS.json` `overallStatus` | `XR1_O_C1_PUSHED_WAITING_SHIFT_AUTHORIZATION` |
| C-12 | `P2B-APPROVER-IDENTITY-RECONCILIATION` work order status | `DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.` — untouched, PARKED |

## 3. Functional requirements

### 3.1 Relationship identity (bound at `XR1-S-C1`, static facts — no code)

- **R-1** — `workspaceId` is exactly `cvf-operations-workspace` everywhere
  this tranche states it.
- **R-2** — Shift's role is stated exactly as `PROFILE_SOURCE`; Operations'
  role is stated exactly as `PRIMARY_PLATFORM`.
- **R-3** — `relationshipDirection` is stated exactly as
  `SHIFT_TO_OPERATIONS_GOVERNED_INTAKE` everywhere this tranche references
  it.
- **R-4** — Both canonical remotes are stated exactly and identically to
  `ADR-OW-006` section A: Shift
  `https://github.com/CVF-Ecosystem/shift-operations-workspace.git`,
  Operations `https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git`.

### 3.2 Reciprocal descriptor schema (bound at `XR1-S-C2b`)

- **R-5** — `.cvf/workspace-link.json` MUST contain exactly the five fields
  in `ADR-2026-07-24-XR1S-RECIPROCAL-WORKSPACE-LINK` §2.2: `schemaVersion`,
  `workspaceId`, `thisRepo` (`repoId`, `role`, `remote`), `peerRepo`
  (`repoId`, `role`, `remote`), `relationshipDirection`. No sixth field.
- **R-6** — `.cvf/workspace-link.json` MUST NOT contain a `sourcePin` field,
  a `pinUpdatePolicy` field, or any other field asserting consumer
  acceptance state.
- **R-7** — No value in `.cvf/workspace-link.json` may be, or contain, an
  absolute filesystem path, a drive letter, a UNC path, a hostname, or a
  username.
- **R-8** — `.cvf/workspace-link.json` MUST be created only at `XR1-S-C2b`,
  never at `XR1-S-C1`.

### 3.3 Core-pin repair (bound at `XR1-S-C2a`, verify-only, `XR1S-R3`)

- **R-9** — `.cvf/manifest.json` `cvfCoreCommit` MUST change from
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` to
  `27137db4d9aa2aea931ddd2507185d5c24943080` — full 40-character lowercase
  hex, matching existing storage form.
- **R-10** — Every other key in `.cvf/manifest.json` MUST be byte-identical
  to its pre-BUILD value. No key added, no key removed, no re-serialization.
- **R-11** — The hidden sibling CVF core MUST already be reconciled to
  `27137db4d9aa2aea931ddd2507185d5c24943080` before `XR1-S-C2a` begins (C-5
  verifies this now). `XR1-S-C2a` performs **read-only verification only** —
  core `origin` identity, `HEAD == origin/main == 27137db4d9aa2aea931ddd2507185d5c24943080`,
  and a clean worktree (`ADR-2026-07-24-XR1S-RECIPROCAL-WORKSPACE-LINK`
  §2.3.1 steps 1–3) — before editing the manifest (step 4). `XR1-S-C2a`
  MUST NOT invoke the sanctioned reconciler and MUST NOT produce any
  out-of-repository side effect (a fresh core clone, a
  `_cvf-core-backups/` entry, or otherwise); reconciliation already
  happened and re-running it is unnecessary scope.
- **R-12** — After `XR1-S-C2a`, workspace doctor's `CVF core commit matches
  manifest` row MUST read `[PASS]`, not `[FAIL]`/`warn only`.
- **R-13** — `XR1-S-C2a`'s changed set is exactly one file, one line diff.

### 3.4 Separation of `XR1-S-C2a` and `XR1-S-C2b`

- **R-14** — `XR1-S-C2a` and `XR1-S-C2b` MUST be independent commits. Neither
  commit's changed set may contain any path from the other's.
- **R-15** — Each of `XR1-S-C2a` and `XR1-S-C2b` MUST receive its own
  continuity-synchronization commit, its own post-commit/pre-push
  direct-sibling-worktree rehearsal, and its own push, before the other's
  BUILD begins or independently of it.

### 3.5 Descriptor tests (bound at `XR1-S-C2b`)

`tests/integration/test_xr1s_workspace_link_descriptor.py` MUST prove:

- **R-16** — The descriptor's field set is exactly R-5's five fields with
  exactly R-1..R-4's literal values; a test asserts both the field set and
  every value.
- **R-17** — `thisRepo.role`/`peerRepo.role` are recognized as complementary
  (`PROFILE_SOURCE` ↔ `PRIMARY_PLATFORM`), not merely both present.
- **R-18** — No `sourcePin`, no consumer-acceptance-state field of any name,
  is present (R-6).
- **R-19** — No absolute/local-machine path, hostname, or username string
  appears anywhere in the descriptor (R-7).
- **R-20** — Given only `.cvf/workspace-link.json` (no Operations clone
  present locally), the peer's exact `repoId` and `remote` are recoverable
  from `peerRepo` alone.
- **R-21** — The descriptor is asserted to be identical across a fresh-clone
  simulation (re-reading the same tracked bytes) — no field is templated,
  regenerated, or machine-specific at read time.
- **R-22** — A read-only compatibility check against Operations' own
  descriptor contract as authorized at Operations commit
  `74170650bd7f2732bc2eec985e5b891df6d45897` (`ADR-OW-006` section A) is
  present as its own test, and is skipped (not failed) if the Operations
  sibling clone is not present locally — R-20 must hold independently of
  this test's outcome.
- **R-23** — Negative cases are each individually tested and rejected:
  a malformed field type, an extra/unknown field, a wrong role value, a
  wrong `relationshipDirection`, a wrong remote, a wrong `workspaceId`, and
  any absolute/local path.

### 3.6 BUILD gates and containment (bound at `XR1-S-C2a`/`XR1-S-C2b`; repaired `XR1S-R1`/`XR1S-R2`)

- **R-24** — The full then-current regression suite passes — 292 tests as of
  this authoring round, whatever the real count is at BUILD time.
- **R-25** — `python scripts/generate_catalog.py --check` PASSes at both
  `XR1-S-C2a` and `XR1-S-C2b`. At `XR1-S-C2a`, nothing is regenerated. At
  `XR1-S-C2b`, regeneration is permitted only under R-37's bounded
  condition.
- **R-26** — `python scripts/check_session_state.py` PASSes (no
  canonical/mirror drift), at both `XR1-S-C2a` and `XR1-S-C2b`.
- **R-27** — `python scripts/testing/validate_repository.py` PASSes, at both
  `XR1-S-C2a` and `XR1-S-C2b`.
- **R-28** — The file-size guard PASSes, at both `XR1-S-C2a` and
  `XR1-S-C2b`.
- **R-29** — Workspace doctor's `CVF core commit matches manifest` row
  remains `[PASS]` after both `XR1-S-C2a` and `XR1-S-C2b` are built; the
  overall doctor result stays `PASS WITH NOTE` with, at most, the same
  single pre-existing `LEGACY_PROJECT: governed downstream catalog kit not
  present` warning as `XR1-S-C2a`'s own gate (R-39) — `XR1-S-C2b`
  introduces no new warning or failure.
- **R-30** — No provider/AI call, no real Shift `scan`/`apply` execution, and
  no secret-content inspection occurs in either future BUILD.
- **R-31** — A catalog change at `XR1-S-C2b` touching any path, field, or
  module outside exactly what R-37 authorizes is a stop condition, not a
  judgment call `IMPLEMENTATION_WORKER` may waive or silently expand.
- **R-36** (`XR1S-R3`) — If, at `XR1-S-C2a` BUILD time, the hidden core's
  `origin` identity, `HEAD == origin/main == 27137db4d9aa2aea931ddd2507185d5c24943080`,
  or worktree cleanliness (R-11) does not hold, `XR1-S-C2a` MUST stop and
  escalate for independent review. It MUST NOT run the reconciler to repair
  the drift within this commit and MUST NOT create `_cvf-core-backups/` or
  any other out-of-repository side effect as a silent remedy.
- **R-37** (`XR1S-R2`) — Bounded catalog reconciliation for `XR1-S-C2b`:
  after authoring `.cvf/workspace-link.json` and its descriptor test and
  passing the focused descriptor tests, if and only if
  `python scripts/generate_catalog.py --check` then reports drift caused by
  those two files, `IMPLEMENTATION_WORKER` MAY update the exact affected
  registry metrics using `python scripts/generate_catalog.py --write` (never
  a hand-edit) and MAY regenerate `docs/catalog/MODULE_CATALOG.md`
  canonically from the same run, then MUST re-run `--check` clean, the
  repository validator, and the full test suite. If `--check` reports zero
  drift from the two required files, neither catalog path is touched.
- **R-38** (`XR1S-R2`) — `docs/catalog/MODULE_REGISTRY.json` and
  `docs/catalog/MODULE_CATALOG.md` are additionally authorized paths for
  `XR1-S-C2b`, strictly conditioned on R-37; no unrelated module's identity,
  ownership, lifecycle, status, or other catalog field may change.
- **R-39** (`XR1S-R1`) — No new `[FAIL]` or `[WARN]` beyond the exact
  pre-existing `LEGACY_PROJECT: governed downstream catalog kit not
  present` warning (C-6) may appear in the workspace doctor result at
  either `XR1-S-C2a` or `XR1-S-C2b`; if one does, that BUILD stops.

## 4. Acceptance criteria

| AC | Statement | Verifies |
|---|---|---|
| AC-1 | Relationship identity fields stated exactly and consistently across ADR, SPEC, WORK_ORDER | R-1..R-4 |
| AC-2 | `.cvf/workspace-link.json` (once built) has exactly the five authorized fields, no more, no fewer | R-5 |
| AC-3 | No `sourcePin`/`pinUpdatePolicy`/consumer-acceptance field on the Shift descriptor | R-6, R-18 |
| AC-4 | No absolute path/hostname/username anywhere in the descriptor | R-7, R-19 |
| AC-5 | `.cvf/workspace-link.json` does not exist after `XR1-S-C1` | R-8 |
| AC-6 | `.cvf/manifest.json` `cvfCoreCommit` becomes the full new hash; no other key changes | R-9, R-10 |
| AC-7 | Core verified already clean/at-target/origin-correct before the manifest edit; no reconciler run | R-11 |
| AC-8 | Doctor's core/manifest row reaches `[PASS]` after `XR1-S-C2a` | R-12 |
| AC-9 | `XR1-S-C2a` changed set is exactly one file, one line | R-13 |
| AC-10 | `XR1-S-C2a` and `XR1-S-C2b` never share a changed path; each gets its own sync/rehearsal/push | R-14, R-15 |
| AC-11 | Descriptor test asserts exact field set/values | R-16 |
| AC-12 | Descriptor test asserts role complementarity | R-17 |
| AC-13 | Descriptor test asserts standalone peer discovery from `peerRepo` alone | R-20 |
| AC-14 | Descriptor test asserts fresh-clone identity (no templating/regeneration) | R-21 |
| AC-15 | Read-only Operations-compatibility test exists and never requires a local Operations clone to pass R-20 | R-22 |
| AC-16 | Every negative case in R-23 is individually tested and rejected | R-23 |
| AC-17 | Full then-current test baseline passes at each future BUILD | R-24 |
| AC-18 | `generate_catalog.py --check`, `check_session_state.py`, `validate_repository.py`, and the file-size guard all PASS at each future BUILD | R-25..R-28 |
| AC-19 | Doctor's core/manifest row stays PASS after both future commits; overall result stays PASS WITH NOTE with at most the one pre-existing legacy catalog-kit warning, no new one | R-29, R-39 |
| AC-20 | No provider call, no real scan/apply, no secret inspection in either future BUILD | R-30 |
| AC-21 | A catalog change at `XR1-S-C2b` outside R-37's exact bound is a stop condition, never silently resolved or expanded | R-31 |
| AC-22 | A drifted hidden core at `XR1-S-C2a` BUILD time stops for independent review; no silent reconciler run or out-of-repository side effect | R-36 |
| AC-23 | Catalog metric reconciliation at `XR1-S-C2b`, if it occurs at all, is exactly bounded to the two required files' drift, uses the canonical generator only, and touches no unrelated module field | R-37, R-38 |

## 5. Non-functional requirements

- **R-32** — No secret may be read, printed, logged, or persisted by any
  artifact this tranche authors or builds.
- **R-33** — All roles are provider-neutral: named by responsibility, never
  by provider.
- **R-34** — No network call other than `git fetch`/`git clone` against the
  public CVF remote or read-only inspection of `CVF-Operations-Workspace`,
  both unauthenticated.
- **R-35** — Workspace isolation holds: no downstream artifact is written
  into the CVF core, and no write of any kind is made into
  `CVF-Operations-Workspace`.

## 6. Out-of-scope restatement

- `P2B-APPROVER-IDENTITY-RECONCILIATION` — untouched, PARKED, its WORK_ORDER
  remains `DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.`
- Any Operations-side BUILD (`XR1-O-C2`) — that remains exclusively
  Operations' own governed action, blocked on this tranche's closure, never
  performed from this repository.
- `docs/catalog/**` beyond `docs/catalog/MODULE_REGISTRY.json` and
  `docs/catalog/MODULE_CATALOG.md`, and even those two only under R-37's
  bounded condition; `docs/implementation/EXECUTION_ROADMAP.md`,
  `docs/cvf/CVF_CONTROL_MAPPING.md`, `docs/INDEX.md`, `.gitignore`,
  `AGENTS.md`, the untracked assessment file, CVF Core/bootstrap-learning
  content, and every third repository.
- Running the sanctioned CVF-core reconciler at `XR1-S-C2a` (R-11, R-36).

## 7. Claim boundary

Satisfying every criterion above proves: a portable, machine-readable,
reciprocal relationship identity between the two repositories; a repaired
Shift-side CVF core pin; and descriptor mechanics that are internally
consistent, symmetric with Operations' own descriptor, and correctly
withhold consumer-acceptance state. It does not prove Operations' import or
acceptance of any Shift commit, the existence or correctness of any
refresh/`scan`/`apply` tooling, runtime compatibility of either repository,
closure of High Finding #4, completion of `P2B-APPROVER-IDENTITY-
RECONCILIATION`, or any AI/agent governance behavior.
