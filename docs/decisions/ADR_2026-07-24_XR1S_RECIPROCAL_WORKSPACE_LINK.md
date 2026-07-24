# ADR 2026-07-24 — Shift reciprocal workspace-link authorization (XR1-S)

- ADR id: `ADR-2026-07-24-XR1S-RECIPROCAL-WORKSPACE-LINK`
- Tranche: `XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`
- Control-chain phase at authoring time: `WORK_ORDER`
- Risk: **R2** (governance-core pin + a new tracked cross-repository
  descriptor — the same class of risk as `CVF-CORE-PIN-2026-07-23`)
- Status: **REPAIRED — pending independent XR1-S authorization re-review.**
  No BUILD has been performed. This ADR authorizes planning only.
- Specification: `docs/specs/XR1S_RECIPROCAL_WORKSPACE_LINK_SPEC.md`
- Work order: `docs/work_orders/XR1S_RECIPROCAL_WORKSPACE_LINK_WORK_ORDER.md`

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `REVIEW_FAIL` with three findings, all
repaired without waiver:

- **`XR1S-R1` `IMPOSSIBLE_FULL_DOCTOR_PASS`.** The prior text required a
  fully clean doctor `PASS` after `XR1-S-C2a`/`XR1-S-C2b`, which is
  impossible given this repository's pre-existing, bounded
  `LEGACY_PROJECT: governed downstream catalog kit not present` warning.
  Repaired throughout §2.6: the core/manifest row must become `[PASS]`, no
  new `[FAIL]`/`[WARN]` may appear, and the overall result may stay `PASS
  WITH NOTE` only if the sole remaining note is that exact pre-existing
  warning. Evidence must record the literal doctor summary line.
- **`XR1S-R2` `DETERMINISTIC_CATALOG_GATE_CONFLICT`.** `XR1-S-C2b`'s
  changed-set ceiling gains `docs/catalog/MODULE_REGISTRY.json` and
  `docs/catalog/MODULE_CATALOG.md`, conditionally authorized (§2.3,
  §2.6.1) — a **ceiling**, not a requirement — to reconcile only the exact
  metric drift the two required files may cause, via the repository's
  canonical `scripts/generate_catalog.py` generator, never a hand-edit.
  Removed the prior language that treated a catalog conflict as a
  mid-BUILD stop condition awaiting a future authorization amendment.
- **`XR1S-R3` `UNNECESSARY_RECONCILER_SIDE_EFFECT`.** The hidden CVF core
  is already clean and at the exact target commit, so `XR1-S-C2a`'s normal
  execution is repaired to be verify-only (§2.3.1): no reconciler run, no
  `_cvf-core-backups/` or other out-of-repository side effect. If the core
  has drifted by BUILD time, `XR1-S-C2a` stops and escalates for
  independent review instead of silently reconciling.

All prior decisions are preserved: `XR1-S-C2a`/`XR1-S-C2b` remain separate
commits; the Shift descriptor retains exactly its five fields with no
`sourcePin`/`pinUpdatePolicy`; Operations remains the acceptance-pin owner;
sync/closure commits remain separately bounded; Codex remains independent
`REVIEWER`/`COMMIT_STEWARD`; `P2B-APPROVER-IDENTITY-RECONCILIATION` remains
parked. Repaired exactly the eight paths this round's ceiling permits; no
ninth path; no BUILD, stage, commit, or push occurred; the Operations
repository, the untracked assessment file, and `.cvf/manifest.json` were
not touched. Status: `XR1S_AUTHORIZATION_REPAIRED_PENDING_INDEPENDENT_RE_REVIEW`.

## 1. Context

### 1.1 Why this tranche exists

`CVF-Operations-Workspace` (a separate, independent Git repository under the
same owner) has authored and pushed `XR1-O-C1`: a portable, tracked
relationship contract (`ADR-OW-006`, `OW-XR1-SPEC-001`, `OW-XR1-WO-001`)
describing this repository (`shift-operations-workspace`) as `PROFILE_SOURCE`
and itself as `PRIMARY_PLATFORM`, plus a governed `scan`/`apply` refresh tool
that will (once built and authorized on the Operations side) read this
repository's Git history read-only and never write to it. Operations'
`IMPLEMENTATION_STATUS.json` `overallStatus` is
`XR1_O_C1_PUSHED_WAITING_SHIFT_AUTHORIZATION` — Operations' own next gate
(`XR1-O-C2` BUILD) is explicitly blocked until this repository closes its own
reciprocal authorization (`XR1-S-C1` through `XR1-S-C3`).

This tranche opens that reciprocal authorization: DESIGN (this ADR), SPEC,
and WORK_ORDER only. It authors no code, creates no `.cvf/workspace-link.json`,
and performs no BUILD.

### 1.2 Observed state (INTAKE evidence, captured read-only 2026-07-24)

| Fact | Verified value |
|---|---|
| Shift HEAD | `f98f29e145fa002be070e9d44520d20f0f82dcb3` |
| Shift `origin/main` | `f98f29e145fa002be070e9d44520d20f0f82dcb3` (HEAD == origin/main) |
| Shift worktree | clean except the one pre-existing untracked assessment file |
| Assessment file | `docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`, `sha256:168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2` — never read, edited, staged, or committed by this tranche |
| Shift `.cvf/manifest.json` `cvfCoreCommit` | `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` |
| Local/public CVF core actual HEAD | `27137db4d9aa2aea931ddd2507185d5c24943080` |
| Workspace doctor | `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` — `CVF core commit matches manifest` reports `[FAIL]` but is explicitly `warn only`, plus one unrelated `[WARN]` for the governed downstream catalog kit not being present (this project predates that kit; bounded legacy compatibility, out of scope here) |
| Test baseline | `python -m pytest -q` → `292 passed` |
| Operations authorization commit (`XR1-O-C1`) | `74170650bd7f2732bc2eec985e5b891df6d45897` |
| Operations post-push continuity commit | `3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a` |
| Ordering | `7417065` is an ancestor of `3ed0fc83` (post-push continuity records the push, does not fold into it); `3ed0fc83` is Operations' current `HEAD == origin/main` |
| Operations `IMPLEMENTATION_STATUS.json` `overallStatus` | `XR1_O_C1_PUSHED_WAITING_SHIFT_AUTHORIZATION` |
| Shift lane 2 | `P2B-APPROVER-IDENTITY-RECONCILIATION` — `docs/decisions/ADR_2026-07-23_P2B_APPROVER_IDENTITY_RECONCILIATION.md`, `docs/specs/P2B_APPROVER_IDENTITY_RECONCILIATION_SPEC.md`, `docs/work_orders/P2B_APPROVER_IDENTITY_RECONCILIATION_WORK_ORDER.md` — committed at Shift `f98f29e145fa002be070e9d44520d20f0f82dcb3` (current HEAD). Work order `Status: DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.` **PARKED** by this tranche: not edited, resumed, superseded, cancelled, or built. |

The manifest/core-pin drift (`6ce1cf0` vs. actual `27137db4`) is real and
verified, exactly as `CVF-CORE-PIN-2026-07-23` previously found and fixed an
earlier instance of this same drift (`c1076dc` → `6ce1cf0`). It is recorded
here as the **`XR1-S-C2a` prerequisite** — a future, separately-gated BUILD
commit — and this ADR does **not** authorize touching `.cvf/manifest.json`
during `XR1-S-C1`.

### 1.3 Scope

Exactly two repositories: `shift-operations-workspace` (this repository) and
`CVF-Operations-Workspace` (read-only reference for verification only — no
write access, no BUILD there from this tranche). CVF Core/bootstrap learning
and every third repository are excluded. Shift's own `P2B-APPROVER-IDENTITY-
RECONCILIATION` (lane 2) authorization is excluded and PARKED, exactly as
`CVF-CORE-PIN-2026-07-23` was previously inserted as its own orthogonal
governance-core tranche without reordering, cancelling, or advancing the
lane sequence.

## 2. Decision

### 2.1 Relationship identity

- `workspaceId`: `cvf-operations-workspace` — one stable identifier shared by
  both repositories' descriptors.
- Shift role: `PROFILE_SOURCE`. Operations role: `PRIMARY_PLATFORM`.
- Relationship direction: `SHIFT_TO_OPERATIONS_GOVERNED_INTAKE` — content
  flows from Shift into Operations only through Operations' own governed
  `scan`/`apply` tool; Shift never receives a write from Operations.
- Canonical remotes (exact, both descriptors must match these literally):
  - Shift: `https://github.com/CVF-Ecosystem/shift-operations-workspace.git`
  - Operations: `https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git`
- GitHub remains the only synchronization transport — no direct filesystem
  sync, no shared network-drive assumption.
- The two repositories keep fully independent Git histories. No atomic
  cross-repository commit is claimed or possible; every commit named in
  §2.5 is a single-repository action.

### 2.2 Role-specific Shift descriptor (authorized shape, built at `XR1-S-C2b`)

This ADR authorizes the exact future shape of Shift's own reciprocal
descriptor. It is **not** created this round:

```json
{
  "schemaVersion": "1.0",
  "workspaceId": "cvf-operations-workspace",
  "thisRepo": {
    "repoId": "shift-operations-workspace",
    "role": "PROFILE_SOURCE",
    "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"
  },
  "peerRepo": {
    "repoId": "cvf-operations-workspace",
    "role": "PRIMARY_PLATFORM",
    "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"
  },
  "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE"
}
```

Five top-level fields, no more, no fewer: `schemaVersion`, `workspaceId`,
`thisRepo`, `peerRepo`, `relationshipDirection`. Compare against Operations'
own descriptor (`ADR-OW-006` section A), which additionally carries
`sourcePin` and `pinUpdatePolicy` — **the Shift descriptor intentionally
omits both**, for reasons that are load-bearing, not stylistic:

- Operations is the **consumer** of Shift content through the `scan`/`apply`
  cycle; only the consumer can meaningfully assert "the exact Shift commit I
  have reviewed and accepted." Shift asserting its own `sourcePin` would be
  asserting Operations' acceptance state on Operations' behalf — a category
  error Shift has no standing to make.
- Shift must remain free to advance its own `HEAD` (new commits, new
  tranches, its own lane sequence) at its own pace, without that advancement
  ever reading as "Operations reviewed and consumed this new commit." A
  `sourcePin` field on the Shift side would create exactly that false
  implication the moment Shift's `HEAD` moved past it.
- No field may hold an absolute filesystem path, a hostname, a username, or
  any other machine-local value — this descriptor must be byte-identical
  and valid from a fresh clone on any machine, exactly like Operations'
  `.cvf/workspace-link.json`.

`.cvf/workspace-link.json` is **not created during `XR1-S-C1`.** It is
authored exactly as shown above, at `XR1-S-C2b`, only after this
authorization package is independently reviewed.

### 2.3 Core-pin prerequisite separation (repaired, `XR1S-R2`/`XR1S-R3`)

Two separate future BUILD commits are authorized, **never combined into
one**:

- **`XR1-S-C2a` — core-pin repair, verify-only (`XR1S-R3`).** The hidden
  sibling CVF core is **already** reconciled: §1.2 verifies its `origin`,
  `HEAD`, and `origin/main` are all `27137db4d9aa2aea931ddd2507185d5c24943080`
  with a clean worktree. Because reconciliation has already occurred,
  `XR1-S-C2a`'s normal execution is **verify-only** (§2.3.1) — the
  sanctioned reconciler (`update_cvf_workspace_public_core.ps1`) **MUST
  NOT** be run as part of this commit, and no out-of-repository side
  effect (a fresh core clone, a `_cvf-core-backups/` entry, or otherwise)
  is expected or authorized. Exactly one implementation path:
  `.cvf/manifest.json`. Exactly one value changes: `cvfCoreCommit` from
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` to
  `27137db4d9aa2aea931ddd2507185d5c24943080`.
- **`XR1-S-C2b` — reciprocal descriptor, plus bounded conditional catalog
  reconciliation (`XR1S-R2`).** `.cvf/workspace-link.json` (new, §2.2's
  exact shape) and exactly one descriptor test path,
  `tests/integration/test_xr1s_workspace_link_descriptor.py`, are the two
  **required** paths. `docs/catalog/MODULE_REGISTRY.json` and
  `docs/catalog/MODULE_CATALOG.md` are additionally authorized as a
  **ceiling, not a requirement** — see §2.6.1 for the exact, bounded
  condition under which either may actually change.

#### 2.3.1 `XR1-S-C2a` verify-only execution (`XR1S-R3`)

1. Read-only verify the hidden core's `origin` remote identity.
2. Verify the hidden core's `HEAD` equals its `origin/main` equals
   `27137db4d9aa2aea931ddd2507185d5c24943080` exactly.
3. Verify the hidden core's worktree is clean.
4. Only if steps 1–3 all hold: edit `.cvf/manifest.json`'s `cvfCoreCommit`
   to `27137db4d9aa2aea931ddd2507185d5c24943080`. Nothing else in the file
   changes.
5. Run the required validation (`WO-XR1S-...-WORK_ORDER` §7).

If, at `XR1-S-C2a` BUILD time, the hidden core is **not** clean, **not** at
the target commit, or its `HEAD` no longer equals `origin/main` — **stop
and escalate for independent review.** Do not run the reconciler to repair
it silently, and do not create `_cvf-core-backups/` or any other
out-of-repository side effect as part of this commit; a drifted core is a
new fact requiring its own reviewed decision, not something this ceiling
may silently absorb.

`XR1-S-C2a` and `XR1-S-C2b` are independently reviewable, independently
revertible, and independently committed. Combining them into a single commit
is a stop condition, not a convenience.

### 2.4 Descriptor tests (bound at `XR1-S-C2b`)

`tests/integration/test_xr1s_workspace_link_descriptor.py` must prove, at
minimum:

1. The descriptor's field set is exactly the five §2.2 fields, no more, no
   fewer, and every value is exactly the §2.1/§2.2 literal (no
   transformation, no template placeholder left unresolved).
2. Role complementarity: `thisRepo.role` is `PROFILE_SOURCE`,
   `peerRepo.role` is `PRIMARY_PLATFORM`, and the two are recognized as
   complementary, not merely both-present.
3. Both canonical remotes match §2.1 literally.
4. No `sourcePin` field, and no other consumer-acceptance-state field
   (present or with any other name), exists anywhere in the descriptor.
5. No absolute path (`[A-Za-z]:\`, `/home/`, `/Users/`), no hostname, and no
   username-bearing string appears anywhere in the descriptor.
6. Standalone peer discovery: given only this descriptor (no Operations
   clone present, no other file read), the peer's exact `repoId` and
   `remote` are recoverable from `peerRepo` alone.
7. The descriptor is byte-for-byte identical when read from a fresh clone —
   no field is regenerated, templated, or machine-specific.
8. The descriptor is compatible with Operations' own contract as authorized
   at Operations commit `74170650bd7f2732bc2eec985e5b891df6d45897`
   (`ADR-OW-006` section A), checked read-only against that repository —
   this test never writes into `CVF-Operations-Workspace`.
9. No file from `CVF-Operations-Workspace` is required to exist locally for
   Shift's own descriptor to validate on its own — the compatibility check
   in item 8 is an additional, optional cross-check, not a hard dependency
   of Shift's descriptor being well-formed.
10. Negative cases fail closed: a malformed field, an extra/unknown field, a
    wrong role, a wrong `relationshipDirection`, a wrong remote, a wrong
    `workspaceId`, and any local/absolute path are each individually
    rejected.

### 2.5 Commit plan

| Commit | Content |
|---|---|
| `XR1-S-C1` | This authorization package (ADR + SPEC + WORK_ORDER) plus authorization continuity — exactly the eight paths in `OW-XR1S-...-WORK_ORDER`'s changed-set ceiling. |
| `XR1-S-C2a` | `.cvf/manifest.json` — one-line core-pin repair only (§2.3). |
| `XR1-S-C2a-SYNC` | Continuity-only receipt recording `XR1-S-C2a`'s closure (canonical + mirror state). No implementation path. |
| `XR1-S-C2b` | `.cvf/workspace-link.json` + `tests/integration/test_xr1s_workspace_link_descriptor.py` (required, §2.2, §2.4), plus `docs/catalog/MODULE_REGISTRY.json`/`docs/catalog/MODULE_CATALOG.md` only if §2.6.1's bounded condition actually applies. |
| `XR1-S-C2b-SYNC` | Continuity-only receipt recording `XR1-S-C2b`'s closure. No implementation path. |
| `XR1-S-C3` | Codex-owned independent review receipt and FREEZE continuity. |

An optional post-push synchronization, if ever needed, is its own separate
continuity-only commit — never folded into the commit whose push it
records, exactly mirroring both `CVF-CORE-PIN-2026-07-23`'s and Operations'
own F1A/XR1 precedent. Codex exclusively owns staging, commits, rehearsals,
and pushes. Explicit-path staging only; `git add .` and `git add -A` are
never used.

### 2.6 BUILD gates (authorized ahead of time; not executed by this round; repaired `XR1S-R1`/`XR1S-R2`)

**`XR1-S-C2a` gates:**

- `.cvf/manifest.json` `cvfCoreCommit`, the hidden core's `HEAD`, and the
  hidden core's `origin/main` are all exactly
  `27137db4d9aa2aea931ddd2507185d5c24943080`.
- Workspace doctor's `CVF core commit matches manifest` row becomes
  `[PASS]`.
- **No new `[FAIL]` and no new `[WARN]` is introduced.** The overall doctor
  result may remain `PASS WITH NOTE` **only** if the sole remaining note is
  the exact pre-existing `LEGACY_PROJECT: governed downstream catalog kit
  not present` warning already recorded in §1.2 — any different or
  additional warning or failure blocks this gate (`XR1S-R1`).
- Fresh-clone initialization (`scripts/initialize_cvf_clone.ps1`) and the
  portable relative-path binding remain valid.
- No `P2B-APPROVER-IDENTITY-RECONCILIATION`, source, catalog, or roadmap
  path changes.
- Evidence records the exact doctor summary line (e.g. `RESULT: PASS WITH
  NOTE (24 passed, 1 warning(s))` or `RESULT: PASS (25 passed)`, whichever
  is literally true at BUILD time) and names the one accepted remaining
  warning, if any.

**`XR1-S-C2b` gates:**

- Changed set is exactly the two required paths
  (`.cvf/workspace-link.json`,
  `tests/integration/test_xr1s_workspace_link_descriptor.py`) plus, only
  to the extent §2.6.1's condition actually applies,
  `docs/catalog/MODULE_REGISTRY.json` and/or `docs/catalog/MODULE_CATALOG.md`
  — nothing else.
- Full then-current regression baseline passes — **292 tests** as of this
  round, whatever the real count is at `XR1-S-C2b` BUILD time (never assumed
  to still be 292).
- `python scripts/generate_catalog.py --check` PASS. Regeneration is
  permitted **only** as §2.6.1 describes, bounded to the exact metric
  changes the two required files cause — never a hand-edit, never an
  unrelated field change.
- `python scripts/check_session_state.py` PASS (no canonical/mirror drift).
- `python scripts/testing/validate_repository.py` PASS.
- File-size guard PASS.
- Workspace doctor's core/manifest row remains `[PASS]` (from
  `XR1-S-C2a`); the overall result stays `PASS WITH NOTE` with, at most,
  the same single pre-existing legacy catalog-kit note as `XR1-S-C2a`'s
  gate — no new warning or failure introduced by `XR1-S-C2b` either
  (`XR1S-R1`).
- No real AI/agent provider call, no real Shift `scan`/`apply` execution,
  and no secret-content inspection of any kind — this tranche and its
  future BUILD commits assert no AI-governance behavior, so `AGENTS.md`'s
  Mandatory Governance Proof is not triggered and no live provider evidence
  is required.

#### 2.6.1 Bounded, pre-authorized catalog reconciliation for `XR1-S-C2b` (`XR1S-R2`)

Adding `.cvf/workspace-link.json` and its descriptor test can change this
repository's computed tracked-file/LOC metrics, which the hardened catalog
generator (`scripts/generate_catalog.py`) recomputes from source per
registered module path — so `generate_catalog.py --check` could fail to
stay clean while the catalog is forbidden outright. Rather than treat this
as a mid-BUILD stop condition awaiting a later authorization amendment (as
`P1B-OPERATIONS-DOMAIN-EXTRACTION`'s catalog-gate conflict once was), this
ADR authorizes the reconciliation **up front**, bounded exactly as follows:

1. Author `.cvf/workspace-link.json` and
   `tests/integration/test_xr1s_workspace_link_descriptor.py` first.
2. Run the focused descriptor tests; they must pass before anything else
   proceeds.
3. If, and only if, `generate_catalog.py --check` then reports drift caused
   by those two files: update **only** the exact registry metrics/
   source-of-truth fields the two new files actually change, using the
   repository's canonical catalog generator
   (`python scripts/generate_catalog.py --write`) — never a hand-edit of
   `docs/catalog/MODULE_REGISTRY.json`.
4. Regenerate `docs/catalog/MODULE_CATALOG.md` canonically from the same
   generator run — never hand-edited.
5. Run `python scripts/generate_catalog.py --check` again; it must report
   clean against what was just written.
6. Run the repository validator and the full test suite.

No unrelated module's identity, ownership, lifecycle, status, or catalog
field may change as a side effect. This is a **ceiling, not a mandate** to
manufacture unnecessary catalog changes: if step 2's fresh `--check` reports
zero drift caused by the two required files, the catalog paths are not
touched at all and are absent from `XR1-S-C2b`'s actual changed set.
`docs/INDEX.md`, the roadmap, `P2B-APPROVER-IDENTITY-RECONCILIATION`, and
every other file outside this ADR's named paths remain forbidden.

### 2.7 Claim boundary

XR1-S proves, once fully closed (`XR1-S-C3`):

- A portable, machine-readable relationship identity, valid from a fresh
  clone on either repository.
- Shift's `PROFILE_SOURCE` role, stated reciprocally and consistently with
  Operations' own `PRIMARY_PLATFORM` descriptor.
- A clean separation between Shift's own source authority (its `HEAD`
  advances freely) and Operations' exclusively-owned acceptance pin (no
  `sourcePin` duplicated or asserted on the Shift side).
- A repaired CVF core pin (`XR1-S-C2a`) and reciprocal descriptor mechanics
  (`XR1-S-C2b`), each independently built, tested, and reviewed.

XR1-S does **not** prove:

- That Operations imported, accepted, or reviewed any Shift commit newer
  than its own `sourcePin`.
- That any refresh/`scan`/`apply` tooling exists or has run — that tooling
  is entirely Operations-side (`XR1-O-C2`, blocked on this tranche's
  closure) and is never built or executed here.
- Runtime compatibility, MVP completion, or production readiness of either
  repository.
- Closure of High Finding #4 (`known-principals.yaml` ↔ `users`
  reconciliation) — `P2B-APPROVER-IDENTITY-RECONCILIATION` remains its own,
  separately-gated, currently PARKED tranche.
- Completion of `P2B-APPROVER-IDENTITY-RECONCILIATION`'s BUILD — its
  WORK_ORDER remains `DRAFT — NOT APPROVED`, untouched by this ADR.
- Any AI/agent governance behavior. No live provider call is required or
  permitted because `XR1-S-C1`/`XR1-S-C2a`/`XR1-S-C2b` assert no
  AI-governance claim.

## 3. Alternatives considered

1. **Fold the core-pin repair into the descriptor commit (`XR1-S-C2a` +
   `XR1-S-C2b` combined).** Rejected: couples an unrelated governance-core
   pin fix with a new tracked contract file, making both harder to review
   or revert independently — exactly the anti-pattern `CVF-CORE-PIN-2026-
   07-23`'s own commit discipline (§2 D5) was designed to avoid.
2. **Add `sourcePin` to the Shift descriptor for symmetry with Operations'
   descriptor.** Rejected (§2.2): Shift has no standing to assert
   Operations' acceptance state, and doing so would create a false
   "Operations has reviewed up to here" implication every time Shift's own
   `HEAD` advances.
3. **Resume or fold `P2B-APPROVER-IDENTITY-RECONCILIATION`'s BUILD into this
   tranche's scope, since both touch continuity.** Rejected: explicitly
   out of scope and explicitly PARKED by this ADR; the two tranches share
   no requirement and combining them would violate this project's
   commit-discipline rule against batching unrelated tranches.
4. **Let this tranche edit `.cvf/manifest.json` now, since the drift is
   already verified.** Rejected: the drift is recorded as the `XR1-S-C2a`
   prerequisite, not permission to edit the manifest during `XR1-S-C1` —
   authorization must precede BUILD, exactly as `CVF-CORE-PIN-2026-07-23`'s
   own control chain required.
5. **Do nothing and let Operations' `XR1-O-C2` stay blocked indefinitely.**
   Rejected: leaves a cross-repository program permanently stalled on a
   reciprocal authorization that costs nothing to open at DESIGN/SPEC/
   WORK_ORDER level.

## 4. Consequences

Positive: Operations' `XR1-O-C2` gains a concrete, named prerequisite path
to unblock (`XR1-S-C1` → `XR1-S-C2a`/`XR1-S-C2b` → `XR1-S-C3`); the Shift
core-pin drift gets a scoped, reviewable repair plan mirroring a precedent
this repository has already used successfully; the reciprocal descriptor
makes the two-repository relationship symmetric and machine-verifiable from
either side.

Costs: two more future BUILD commits and one new tracked file plus one new
test file to maintain; `P2B-APPROVER-IDENTITY-RECONCILIATION` stays parked
one tranche longer in wall-clock terms (though it was already DRAFT/
NOT APPROVED and untouched either way); this repository now carries two
independent core-pin-style drift-repair precedents to keep consistent if a
third such drift is ever found.

## 5. Compliance notes

- **Phase discipline** — this tranche runs a fresh, dedicated authorization
  sequence (DESIGN → SPEC → WORK_ORDER) before any BUILD, exactly the
  ordering `CVF-CORE-PIN-2026-07-23` and `P1B-OPERATIONS-DOMAIN-EXTRACTION`
  both used.
- **Role separation** — R2 requires REVIEWER independent from
  IMPLEMENTATION_WORKER and from this authoring context. The WORK_ORDER
  assigns REVIEWER and COMMIT_STEWARD to Codex, independent of this
  ORCHESTRATOR/SPEC_AUTHOR/WORK_ORDER_AUTHOR context.
- **Provider neutrality** — every role in this ADR and its companion
  artifacts is named by responsibility, never by provider.
- **Secrets** — this tranche performs no provider call and reads, prints,
  logs, or persists no secret. All Git operations are read-only against
  `CVF-Operations-Workspace` (verification only) or local to this
  repository.
- **`P2B-APPROVER-IDENTITY-RECONCILIATION`** — untouched. Its WORK_ORDER
  stays `DRAFT — NOT APPROVED. BUILD IS NOT AUTHORIZED.`; this ADR does not
  edit, resume, supersede, cancel, or begin its BUILD.
- **`cd36b27`, prior FREEZE tranches** — untouched. No rewrite, squash,
  amend, rebase, or force-push by this tranche.

## 6. Gate

This ADR authorizes planning and work-order construction only. `XR1-S-C2a`
and `XR1-S-C2b` BUILD begin only after `docs/specs/XR1S_RECIPROCAL_WORKSPACE_LINK_SPEC.md`
and `docs/work_orders/XR1S_RECIPROCAL_WORKSPACE_LINK_WORK_ORDER.md` are
independently reviewed and authorized, and this package's own commit
(`XR1-S-C1`) is rehearsed and pushed. `XR1-S-C3` (independent review receipt
and FREEZE continuity) closes the tranche and unblocks Operations'
`XR1-O-C2`.
