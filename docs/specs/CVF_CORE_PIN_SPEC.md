# Specification: CVF Core Pin Synchronization

- Spec id: `SPEC-CVF-CORE-PIN-2026-07-23`
- Tranche: `CVF-CORE-PIN-2026-07-23`
- Control-chain phase at authoring time: `SPEC`
- Risk: **R2**
- Status: **BUILD COMPLETE AND COMMITTED (`da9a122`); §9 FREEZE ADDENDUM
  PROPOSED** — §1-§8 were approved on 2026-07-23, implemented, independently
  reviewed, and committed. §9 (added 2026-07-23) authorizes the continuity
  work that §1.2 deliberately deferred until the P2-B FREEZE batch was
  committed; it is **not yet reviewed and not yet implemented**.
- Design: `docs/decisions/ADR_2026-07-23_CVF_CORE_PIN.md`
- Work order: `docs/work_orders/CVF_CORE_PIN_WORK_ORDER.md`

This document states **intended behavior after the change**. It is separate
from current implementation truth; §2 records current truth explicitly so the
two are never conflated.

## 1. Scope

### 1.1 In scope

- Reconciling the hidden sibling CVF core at
  `<workspaceRoot>/.Controlled-Vibe-Framework-CVF` from
  `c1076dc4be9ef9058b7c4e7b96def59c26aab148` to
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`.
- Updating exactly one value in `.cvf/manifest.json`.
- Re-establishing workspace doctor 24/24.
- Producing the verification evidence enumerated in §6.

### 1.2 Out of scope

- Any change to project source, tests, migrations, schema, or data.
- Any change to the uncommitted `P2B-AUTHENTICATION-REPAIR` FREEZE batch
  present in the worktree.
- Any change to continuity surfaces (`SESSION/**`, `CVF_SESSION/**`,
  `IMPLEMENTATION_STATUS.json`, `docs/catalog/**`, `docs/INDEX.md`,
  `docs/implementation/**`, `docs/cvf/**`) as part of BUILD. Continuity
  synchronization for this tranche, if required, is a separate FREEZE-phase
  activity that must not be started while the P2-B batch owns those files.
- Any provider API call, any read of `ALIBABA_API_KEY` or any other secret.
- Any modification to the CVF core repository's contents (it is a read-only
  reference; only its checked-out commit changes, via the sanctioned
  reconciler).
- Commit `cd36b27` — no rewrite, squash, amend, rebase, or force-push.
- Any claim about AI/agent governance behavior. This tranche makes none, so
  no live provider evidence is required (`AGENTS.md` Mandatory Governance
  Proof is not triggered).

## 2. Current implementation truth (verified 2026-07-23, read-only)

| # | Property | Current value |
|---|---|---|
| C-1 | Workspace doctor result | `FAIL (23/24 checks passed, 1 failed)` |
| C-2 | Failing check | `CVF public core matches origin/main` → `BEHIND_PUBLIC_REMOTE` |
| C-3 | Hidden core `git remote get-url origin` | `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git` |
| C-4 | Hidden core `git rev-parse HEAD` | `c1076dc4be9ef9058b7c4e7b96def59c26aab148` |
| C-5 | Hidden core `git status --porcelain` | empty |
| C-6 | Hidden core `git rev-parse origin/main` | `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` |
| C-7 | `.cvf/manifest.json` `cvfCoreCommit` | `c1076dc4be9ef9058b7c4e7b96def59c26aab148` |
| C-8 | `.cvf/local-binding.json` `resolvedCoreCommit` | `c1076dc4be9ef9058b7c4e7b96def59c26aab148` (git-ignored) |
| C-9 | Upstream delta `c1076dc..6ce1cf0` | 1 commit, 4 files, all CVF core documentation |
| C-10 | Relationship | `c1076dc` is an ancestor of `6ce1cf0` (clean fast-forward) |
| C-11 | Project worktree | 9 modified + 2 untracked files belonging to the P2-B FREEZE batch |
| C-12 | Workspace root | not a git repository |
| C-13 | `CVF_RULE_PACKS/ACTIVE_RULE_PACK.json` `activeProfile` | `operator-local` |

## 3. Functional requirements

### 3.1 Hidden core state

- **R-1** — After BUILD, `git -C <corePath> remote get-url origin` MUST equal
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`.
- **R-2** — After BUILD, `git -C <corePath> rev-parse HEAD` MUST equal
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` exactly (full 40 characters, not
  a prefix comparison).
- **R-3** — After BUILD, `git -C <corePath> rev-parse origin/main` MUST equal
  the same hash as R-2.
- **R-4** — After BUILD, `git -C <corePath> status --porcelain` MUST be empty.
- **R-5** — The core MUST be reached by the sanctioned reconciler
  `.Controlled-Vibe-Framework-CVF/scripts/update_cvf_workspace_public_core.ps1`.
  Ad-hoc `git reset --hard`, manual file copying into the core, or deleting
  the core by hand are all prohibited.
- **R-6** — No downstream project artifact may exist inside the core after
  BUILD. `git -C <corePath> status --porcelain` being empty (R-4) is the
  operative check; the reconciler's fresh clone makes contamination
  structurally impossible, and R-4 detects it if it somehow occurs.

### 3.2 Manifest state

- **R-7** — `.cvf/manifest.json` `cvfCoreCommit` MUST equal
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` — full 40-character lowercase
  hex, matching the existing storage form.
- **R-8** — Every other key in `.cvf/manifest.json` MUST be byte-identical to
  its pre-BUILD value: `schemaVersion`, `cvfCoreRepository`,
  `workspaceLayout`, `cvfCoreRelativePath`, `workspaceRulesRelativePath`,
  `projectRelativePath`, `phaseModel`, `liveGovernanceEvidenceRequired`,
  `mockAllowedOnlyForUi`, `requiredDocs`, `bootstrapDate`,
  `enforcementVersion`, `bootstrapScript`, `bootstrapMode`, `note`,
  `canonicalContinuityPaths`, `knowledgePath`.
- **R-9** — No key may be added to or removed from `.cvf/manifest.json`. In
  particular `cvfPublicRemote` and `publicCoreFreshnessRequired` MUST NOT
  appear (see ADR §2.2).
- **R-10** — File formatting MUST be preserved: 2-space indentation, key
  order, line endings, trailing newline, and UTF-8 without BOM. The diff MUST
  be a single changed line.
- **R-11** — `.cvf/manifest.json` MUST remain valid JSON, parseable by
  `json.loads`.

### 3.3 Doctor and enforcement state

- **R-12** — `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`
  MUST exit 0 and print `FRESH_CLONE_CONTINUITY_PASS`.
- **R-13** — The workspace doctor MUST report `RESULT: PASS (24/24 checks passed)`.
- **R-14** — Specifically, `CVF public core matches origin/main`,
  `CVF public core worktree clean`, `CVF core commit matches manifest`,
  `CVF core origin is public remote`, `Public workspace kit is complete`, and
  `Pinned CVF core commit is public-remote reachable` MUST each be `[PASS]`.

### 3.4 Changed-set containment

- **R-15** — `git status --porcelain` after BUILD MUST show exactly the
  pre-existing P2-B FREEZE entries (C-11) **plus** `M .cvf/manifest.json`,
  and nothing else.
- **R-16** — The 9 modified and 2 untracked P2-B files MUST be byte-identical
  before and after BUILD. No stage, stash, checkout, restore, reset, clean, or
  commit may be applied to them.
- **R-17** — `git add -A` and `git add .` MUST NOT be used at any point. Only
  explicit single-path staging is permitted, and only by COMMIT_STEWARD.
- **R-18** — `.cvf/local-binding.json` will be rewritten by R-12's entrypoint
  and MUST NOT appear in `git status` output, because it is git-ignored
  (`.gitignore:16`). If it does appear, the ignore rule has regressed and
  BUILD MUST stop.

### 3.5 Ordering

- **R-19** — Steps MUST execute in this order:
  1. capture pre-state (§6.1),
  2. run the reconciler (R-5),
  3. verify core state (R-1..R-4),
  4. edit the manifest (R-7..R-11),
  5. run the doctor entrypoint (R-12..R-14),
  6. run repository validation (§4),
  7. capture post-state and review the changed set (R-15..R-18).

  Step 5 before step 4 is a defined failure: with HEAD at `6ce1cf0` and the
  pin still at `c1076dc`, `initialize_cvf_clone.ps1` evaluates
  `$head.StartsWith($pin)` as false, then
  `merge-base --is-ancestor $head $pin` also fails, and the script throws
  `Hidden core cannot fast-forward safely to pinned commit`. This is
  fail-closed behavior working as designed, not a defect — but it means the
  order is load-bearing, not stylistic.

### 3.6 Reconciler invocation constraints

- **R-20** — The reconciler MUST be invoked with `-WorkspaceRoot` set to the
  workspace root resolved from the manifest
  (`workspaceRulesRelativePath`'s parent), and with **no** other switch.
- **R-21** — `-UpdateProjectManifests` MUST NOT be passed (ADR §2.2: it
  writes a short hash, injects two keys, reformats the file, and would in any
  case skip this schema-2.0 manifest).
- **R-22** — `-AllowPendingCoreBackup` MUST NOT be passed. The core is clean
  (C-5); if the reconciler reports pending changes in the core, that
  contradicts INTAKE evidence and is a stop condition, not something to
  override.
- **R-23** — `-OverlaySourcePath` MUST NOT be passed. No local overlay is
  authorized; the core must be exactly public `origin/main`.

## 4. Required repository validation

All of the following MUST pass after the manifest edit. They are listed as
requirements, not suggestions, and MUST be run rather than assumed:

- **R-24** — `python scripts/check_session_state.py` PASS (no mirror drift
  between `SESSION/ACTIVE_SESSION_STATE.json` and
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`).
- **R-25** — `python scripts/generate_catalog.py --check` PASS with no
  regeneration written.
- **R-26** — `python scripts/testing/validate_repository.py` PASS.
- **R-27** — `python -c "import json;json.load(open('.cvf/manifest.json',encoding='utf-8'))"`
  succeeds (R-11).

R-24/R-25/R-26 are expected to pass **unchanged** — this tranche touches
nothing they inspect. Their role is regression detection: if any of them
changes state relative to the pre-BUILD baseline, the changed set exceeded
its boundary and BUILD must stop.

## 5. Non-functional requirements

- **R-28** — No secret may be read, printed, logged, or persisted. No
  `ALIBABA_API_KEY` access. No `Authorization` header anywhere in output or
  evidence.
- **R-29** — A secret scan over the changed set MUST find nothing. The
  changed set is a single hash value, so this is expected to be trivially
  clean; it is still required, not waived.
- **R-30** — All roles are provider-neutral: named by responsibility, never by
  provider name.
- **R-31** — No network call other than `git fetch`/`git clone` against the
  public CVF remote over HTTPS, unauthenticated.
- **R-32** — Workspace isolation holds: the working directory for project
  commands stays this project root; no downstream artifact is written into
  the core.

## 6. Evidence contract

### 6.1 Pre-BUILD capture (baseline)

- **E-1** — `git status --porcelain` in the project (baseline changed set).
- **E-2** — `git -C <corePath> remote -v`, `rev-parse HEAD`,
  `rev-parse origin/main`, `status --porcelain`.
- **E-3** — `git -C <corePath> diff --name-status c1076dc4be9ef9058b7c4e7b96def59c26aab148 6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`
  and the corresponding `git log --oneline` range.
- **E-4** — Directory listing of the workspace root and the SHA-256 (or
  content) of `<workspaceRoot>/WORKSPACE_RULES.md`, so its regeneration is
  reviewable rather than silent.
- **E-5** — Baseline run of the doctor (already captured: 23/24, C-1/C-2).

### 6.2 Post-BUILD evidence (required for REVIEW)

- **E-6** — Core remote/commit verification output proving R-1..R-4.
- **E-7** — Full workspace doctor output proving R-13/R-14 (24/24).
- **E-8** — `python scripts/check_session_state.py` output (R-24).
- **E-9** — `python scripts/generate_catalog.py --check` output (R-25).
- **E-10** — `python scripts/testing/validate_repository.py` output (R-26).
- **E-11** — JSON parse result for `.cvf/manifest.json` (R-27).
- **E-12** — Secret scan result over the changed set (R-29).
- **E-13** — `git status --porcelain` and `git diff -- .cvf/manifest.json`
  proving R-15/R-10 — exact changed set, single-line diff.
- **E-14** — Post-run workspace-root listing and `WORKSPACE_RULES.md`
  comparison against E-4, so out-of-repo side effects are stated, not hidden.

Evidence MUST be real command output. Paraphrase, expected output, or
"should pass" is not evidence.

## 7. Acceptance criteria

| AC | Statement | Verifies |
|---|---|---|
| AC-1 | Hidden core origin is the public CVF remote | R-1 |
| AC-2 | Hidden core HEAD is exactly `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` | R-2 |
| AC-3 | Hidden core HEAD equals `origin/main` | R-3 |
| AC-4 | Hidden core worktree is clean, no downstream artifact present | R-4, R-6 |
| AC-5 | Core reached via the sanctioned reconciler with no prohibited switch | R-5, R-20..R-23 |
| AC-6 | `cvfCoreCommit` is the full 40-character new hash | R-7 |
| AC-7 | All other manifest keys byte-identical; no key added or removed | R-8, R-9 |
| AC-8 | Manifest diff is exactly one line; formatting/encoding preserved | R-10 |
| AC-9 | Manifest parses as valid JSON | R-11, R-27 |
| AC-10 | `initialize_cvf_clone.ps1` exits 0 with `FRESH_CLONE_CONTINUITY_PASS` | R-12 |
| AC-11 | Workspace doctor reports 24/24 with the six named checks PASS | R-13, R-14 |
| AC-12 | Changed set is exactly the P2-B baseline plus `M .cvf/manifest.json` | R-15 |
| AC-13 | All 11 P2-B files byte-identical; never staged, stashed, or reset | R-16, R-17 |
| AC-14 | `.cvf/local-binding.json` absent from `git status` | R-18 |
| AC-15 | Steps executed in the R-19 order | R-19 |
| AC-16 | `check_session_state.py`, `generate_catalog.py --check`, `validate_repository.py` all PASS | R-24..R-26 |
| AC-17 | Secret scan clean; no secret read, printed, or persisted | R-28, R-29 |
| AC-18 | Out-of-repo workspace-root side effects captured and reviewed | E-4, E-14 |
| AC-19 | Core-pin change is committed separately from the P2-B FREEZE batch | ADR §2 D5 |

## 8. Explicit non-claims

On completion, this tranche establishes **only** that the hidden CVF core
matches public `origin/main` at `6ce1cf0`, that the manifest pin matches it,
and that local enforcement artifacts pass 24/24. It does **not** establish
and MUST NOT be described as establishing:

- that any CVF control is load-bearing or newly enforced;
- any live governance evidence of AI/agent behavior;
- any change to the `P2B-AUTHENTICATION-REPAIR` FREEZE disposition or its
  Alibaba evidence receipt;
- closure of High Finding #4;
- that PostgreSQL, approval quorum, or any roadmap tranche advanced;
- that the four upstream documentation changes were reviewed for content
  correctness — they are accepted as the public core's own state, not
  audited by this project.

---

# §9 — FREEZE Addendum (added 2026-07-23)

- Addendum status: **REVIEW_PASS — AUTHORIZED_AFTER_ADDENDUM_COMMIT**.
  Independently reviewed on 2026-07-23. Continuity work remains prohibited
  until the addendum authorization commit hash is supplied.

§1.2 placed continuity synchronization out of scope for BUILD, because the
same continuity files were held by the uncommitted P2-B FREEZE batch. That
batch is now committed (`4e15ea4`), so the deferral condition has expired.
This addendum authorizes **only** that deferred continuity work. It opens no
feature tranche, changes no §1-§8 requirement, and revises no claim already
established by `da9a122`.

## 9.1 Verified preconditions (captured read-only 2026-07-23)

| # | Property | Verified value |
|---|---|---|
| C-14 | Authorization-artifacts commit | `76e73606d9f7d4a5e4203816d18bd20101860532` — 3 files (ADR, SPEC, WORK_ORDER), 0 implementation files |
| C-15 | BUILD / REVIEW_PASS core-pin commit | `da9a1223bb9940769c38c1dbbea3b64c9898175a` — `.cvf/manifest.json` only, 1 insertion / 1 deletion |
| C-16 | P2-B FREEZE commit, separate | `4e15ea4260817a07e4db11543fc8ffa0aff7f4f1` — 11 files, none of them `.cvf/manifest.json` |
| C-17 | Commit order | `76e7360` → `da9a122` → `4e15ea4`, each an ancestor of `HEAD`; AC-19 therefore already satisfied |
| C-18 | Hidden core HEAD / `origin/main` / manifest `cvfCoreCommit` | all three = `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` |
| C-19 | Hidden core worktree | clean |
| C-20 | Project worktree | clean (`git status --porcelain` empty) |
| C-21 | Workspace doctor | `RESULT: PASS (24/24 checks passed)` |
| C-22 | Active handoff | still points at the P2-B FREEZE handoff — no core-pin closing handoff exists yet |
| C-23 | `docs/INDEX.md` lines 23-26 | still describe `docs/specs/` and `docs/work_orders/` as "stub — not yet populated", which is now false |

## 9.2 Authorized changed set — exactly six paths

- **F-1** `SESSION/SESSION_MEMORY.md` (edit)
- **F-2** `SESSION/ACTIVE_SESSION_STATE.json` (edit)
- **F-3** `CVF_SESSION/ACTIVE_SESSION_STATE.json` (edit — compatibility mirror)
- **F-4** `IMPLEMENTATION_STATUS.json` (edit)
- **F-5** `docs/INDEX.md` (edit)
- **F-6** `SESSION/handoffs/AGENT_HANDOFF_2026-07-23_CVF_CORE_PIN_FREEZE.md` (new)

Nothing else. Explicitly **not** authorized: application source, tests,
migrations, schema, `docs/catalog/MODULE_REGISTRY.json`,
`docs/catalog/MODULE_CATALOG.md`, `docs/implementation/EXECUTION_ROADMAP.md`,
`docs/cvf/CVF_CONTROL_MAPPING.md`, any `packages/ai-providers/**` or other
provider file, and **`.cvf/manifest.json`** — the manifest pin is already
committed at `da9a122` and MUST NOT be touched again by this addendum.

## 9.3 Content requirements

### 9.3.1 Disposition

- **R-33** — The core-pin tranche MUST be recorded as
  `FREEZE` / `CLOSED_BOUNDED`. Not `CLOSED`, not `DONE`.

### 9.3.2 Facts that MUST appear, exactly and verifiably

- **R-34** — Authorization-artifacts commit `76e7360`.
- **R-35** — BUILD / REVIEW_PASS core-pin commit `da9a122`.
- **R-36** — Core and manifest pin `6ce1cf0`
  (`6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`).
- **R-37** — Workspace doctor `24/24`.
- **R-38** — P2-B FREEZE recorded as a **separate** commit `4e15ea4`, with the
  fact that the two tranches were never batched stated plainly.

Each of R-34..R-38 must be checkable against `git log` / the doctor, not
asserted from memory.

### 9.3.3 Continuity pointers

- **R-39** — `active_handoff` (F-2) and `activeHandoff`
  (F-2's `cvf_bootstrap_continuity_contract` block, and F-3) MUST point at
  F-6, the new core-pin closing handoff.
- **R-40** — F-6 MUST exist, and MUST record: tranche id, disposition
  (R-33), the R-34..R-38 facts, the verified boundary, the drift in §9.3.6,
  and the next governed move (R-47).
- **R-41** — F-2's `required_reads` MUST include F-6. The superseded P2-B
  FREEZE handoff MUST remain listed and MUST NOT be deleted from
  `SESSION/handoffs/` — superseded handoffs are retained history.
- **R-42** — F-3 MUST stay a pointer mirror only. Its `canonicalSource` MUST
  remain `SESSION/ACTIVE_SESSION_STATE.json`, and it MUST NOT gain
  independent long-form content. F-2 and F-3 MUST agree such that
  `scripts/check_session_state.py` passes.

### 9.3.4 Status file

- **R-43** — F-4 MUST record the core-pin tranche closure (R-33..R-38) as a
  governance/tooling event.
- **R-44** — F-4 MUST NOT change any roadmap feature status. Specifically,
  `status`, the `cvf_enforcement` findings blocks, `p2a_customer_request`,
  and `p2b_authentication` dispositions MUST retain their present meaning. No
  roadmap item may be marked done, opened, reordered, or reprioritized.

### 9.3.5 Index correction

- **R-45** — F-5 MUST stop describing `docs/specs/` and `docs/work_orders/`
  as "stub — not yet populated". Both families are now populated by real
  per-tranche artifacts (`P2B_AUTHENTICATION_REPAIR_*`,
  `ALIBABA_LIVE_PROVIDER_CONFIGURATION_*`, `CVF_CORE_PIN_*`). The replacement
  wording MUST describe actual current contents and MUST NOT overstate them
  (they are per-tranche governance artifacts, not a complete specification of
  the system).

### 9.3.6 Continuity drift that MUST be recorded, not resolved

A real, verified disagreement exists between the roadmap-ordering rule and
the recorded next move:

- `CONTRIBUTING.md` line 21 states the ordering rule: take the next `[ ]`
  item in order (`lấy item [ ] kế tiếp theo thứ tự`).
- The first `[ ]` item in `docs/implementation/EXECUTION_ROADMAP.md` is line
  207, **P1-B** (extracting domain models into `operations-domain`).
- `SESSION/ACTIVE_SESSION_STATE.json`'s `next_allowed_move` offers only
  P2-A (remaining incidents/handovers), `known-principals.yaml` ↔ users
  (High Finding #4), and P2-C — **P1-B is absent from that list.**

Therefore:

- **R-46** — F-1, F-2, and F-6 MUST record this drift explicitly, citing both
  sides (the ordering rule and the three-lane list) and naming P1-B as the
  item the rule would select.
- **R-47** — The recorded next allowed move after core-pin FREEZE MUST be
  **INTAKE for an operator-confirmed lane**. No agent may resolve this drift
  by choosing a lane, by reprioritizing the roadmap, by editing the roadmap,
  or by declaring the rule or the list authoritative over the other. The
  drift MUST be presented to the operator as an open question to decide.
- **R-48** — Resolving the drift is explicitly OUT of scope for this
  addendum. Recording it accurately is the deliverable.

### 9.3.7 Claim boundaries that MUST be preserved

- **R-49** — Nothing written under this addendum may claim the core-pin
  tranche demonstrates, verifies, or evidences AI/agent governance behavior.
  It synchronized a documentation-only core delta and a manifest pin; the
  doctor proves local enforcement artifacts and public-core freshness only.
- **R-50** — No provider API call may be made, and no secret may be read,
  printed, logged, or persisted. `AGENTS.md` Mandatory Governance Proof is
  not triggered because no AI-governance claim is made.
- **R-51** — All P2-B bounded claims MUST be preserved verbatim in meaning:
  identity is load-bearing and governance-approved **within the receipt
  boundary only**; no refresh tokens, revocation, self-service registration,
  password reset, login rate-limiting, or real admin provisioning exist;
  PostgreSQL has never been round-trip verified live.
- **R-52** — High Finding #4 MUST remain recorded as **OPEN**.
  `known-principals.yaml` is still a registry check, not authentication, and
  was not reconciled with the `users` table.
- **R-53** — `cd36b27` MUST remain described as the original unauthorized
  build candidate, retained unrewritten as historical evidence.

## 9.4 Required checks

All MUST be run and MUST pass, with real output captured:

- **R-54** — `python -m pytest -q`
- **R-55** — `python scripts/testing/validate_repository.py`
- **R-56** — `python scripts/check_session_state.py`
- **R-57** — `python scripts/generate_catalog.py --check`
- **R-58** — Workspace doctor via
  `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`
  → `24/24` and `FRESH_CLONE_CONTINUITY_PASS`
- **R-59** — JSON parse of every JSON file in the changed set
  (`SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`, `IMPLEMENTATION_STATUS.json`)
- **R-60** — Exact changed-set review: `git status --porcelain` shows the six
  §9.2 paths and nothing else
- **R-61** — Secret scan over the full changed set — clean

R-57 is a containment check as much as a validation: the catalog is **not**
in the authorized changed set, so `--check` must pass without any
regeneration. If it reports drift, the changed set escaped its boundary.

## 9.5 Evidence contract

- **E-15** — Pre-change `git status --porcelain` proving a clean start.
- **E-16** — Commit-order verification for `76e7360`, `da9a122`, `4e15ea4`,
  plus `git show --stat` for `da9a122` and `4e15ea4` proving the two tranches
  were committed separately.
- **E-17** — Core/manifest/`origin/main` triple-equality at `6ce1cf0` and a
  clean core worktree.
- **E-18** — Output of R-54..R-59.
- **E-19** — Post-change `git status --porcelain` plus `git diff --stat`
  proving R-60.
- **E-20** — Secret-scan output (R-61).
- **E-21** — The drift citation (R-46) reproduced from the real files:
  `CONTRIBUTING.md:21`, `EXECUTION_ROADMAP.md:207`, and the
  `next_allowed_move` text.

Evidence MUST be real command output. Paraphrase is not evidence.

## 9.6 Acceptance criteria

| AC | Statement | Verifies |
|---|---|---|
| AC-20 | Changed set is exactly the six §9.2 paths; nothing else added, modified, or deleted | §9.2, R-60 |
| AC-21 | `.cvf/manifest.json` is untouched by this addendum | §9.2 |
| AC-22 | Disposition recorded as `FREEZE` / `CLOSED_BOUNDED` | R-33 |
| AC-23 | `76e7360`, `da9a122`, `6ce1cf0`, doctor 24/24, and separate P2-B commit `4e15ea4` all recorded and independently checkable | R-34..R-38 |
| AC-24 | Active handoff (canonical and mirror) points at the new core-pin closing handoff, which exists and is complete | R-39, R-40, R-41 |
| AC-25 | Mirror stays a pointer only; `check_session_state.py` PASS | R-42, R-56 |
| AC-26 | `IMPLEMENTATION_STATUS.json` records closure without altering any roadmap feature status | R-43, R-44 |
| AC-27 | `docs/INDEX.md` no longer calls specs/work_orders stubs, and does not overstate them | R-45 |
| AC-28 | Drift recorded in memory, active state, and handoff, citing both sides and naming P1-B | R-46 |
| AC-29 | Next allowed move is INTAKE for an operator-confirmed lane; no lane chosen, no roadmap reprioritized | R-47, R-48 |
| AC-30 | No AI-governance claim; no provider call; no secret touched | R-49, R-50, R-61 |
| AC-31 | P2-B bounded claims preserved; High Finding #4 still OPEN; `cd36b27` still the unauthorized build candidate | R-51, R-52, R-53 |
| AC-32 | All of R-54..R-59 pass with captured output | §9.4 |
| AC-33 | Catalog `--check` passes with no regeneration, proving the changed set stayed inside its boundary | R-57 |
| AC-34 | FREEZE changes left uncommitted for independent review | §9.7 |
| AC-35 | FREEZE commit is separate; no amend, rebase, or force-push | §9.7 |

## 9.7 Commit discipline for this addendum

1. This addendum (the SPEC §9 and WORK_ORDER §13 edits) is reviewed and
   committed **before** any continuity change, as its own authorization
   commit.
2. The continuity FREEZE work begins only after that authorization commit
   hash is supplied.
3. The continuity changes are left **uncommitted** for independent review.
4. The FREEZE commit is **separate** from `76e7360`, `da9a122`, and
   `4e15ea4`. No amend, rebase, or force-push. `cd36b27` is never rewritten.
5. Staging is explicit per-path only. `git add -A` and `git add .` remain
   prohibited.

## 9.8 Non-claims of this addendum

Completing §9 records closure of a tooling/governance tranche and repairs
continuity accuracy. It does **not**:

- advance, close, open, or reorder any roadmap feature item;
- resolve the P1-B / three-lane ordering drift;
- alter the P2-B FREEZE disposition or its live-evidence receipt;
- close High Finding #4;
- establish any AI-governance behavior claim;
- re-open or re-verify `da9a122`, whose REVIEW_PASS already stands.
