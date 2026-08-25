# Specification — CVF Public-Core Refresh 2026-08-23

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Phase: `SPEC`
- Risk: `R2`
- Parent gate: `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Status: `OPEN_FOR_INDEPENDENT_SPEC_REVIEW`
- Frozen target: `3b031fec35473e6ee6a554c4c72400e7a23b06c5`

## Requirements

- `R1`: Before BUILD, downstream `HEAD` and `origin/main` equal
  `0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, staged set is empty, hidden Core
  is clean at `7d9f360a...`, and its fetched `origin/main` equals the frozen
  target with ancestry `0 ahead / 1 behind`.
- `R2`: Freeze existence and raw SHA-256 preimages for all 17 root targets,
  all non-assessment dirty paths, and the ten mutable downstream carriers.
  Never open, hash, stage or use the operator assessment.
- `R3`: Invoke `update_cvf_workspace_public_core.ps1` using only the exact
  workspace root; no overlay, pending-Core override or project-manifest flag.
- `R4`: Successful BUILD performs the ordered three-operation sequence against
  only `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`:
  clone, initializer fetch, initializer-doctor fetch. Early failure records
  only its executed ordered prefix (zero through three). Record owner/command/
  URL/observed full tip/exit code for each; use no credential or secret.
- `R5`: After each network operation, the observed tip equals the frozen
  target. Movement, failure or endpoint mismatch triggers rollback and stop.
- `R6`: Core HEAD, Core `origin/main`, manifest full pin, AGENTS full header
  pin and ignored local-binding full pin equal the frozen target. Core remote
  is exact and worktree clean.
- `R7`: Root-effects evidence covers exactly 17 targets: existence and hash
  before/after, create/delete classification, preimage and backup locations;
  active profile remains `operator-local` and sibling manifests do not change.
- `R8`: BUILD changes only the 12-path incremental ceiling from DESIGN. Ten
  mutable carriers are compared to BUILD-start preimages; two worker evidence
  paths may be created. Every other pre-BUILD path remains byte-exact.
- `R9`: `knowledge/manifest.json` changes only source pins invalidated by
  authorized AGENTS/manifest/implementation changes and passes the knowledge
  guard without classification/owner/policy changes.
- `R10`: `IMPLEMENTATION_STATUS.json` records only bounded maintenance truth;
  module registry, catalog, roadmap and product status do not change.
- `R11`: Canonical state, mirror, bootstrap, memory, handoff and index agree;
  P4-C remains parked and its Work Order/review/handoff remain byte-exact.
- `R12`: Root-effects JSON includes schema/tranche/target/timestamps, all
  R2/R4/R7/R8 evidence, commands with exit codes, backup paths, rollback state,
  staged-zero state and exact incremental comparison. Worker return references
  it and makes only the bounded freshness claim.
- `R13`: Success requires initializer/doctor PASS with only the retained
  legacy-catalog warning, plus session, knowledge, catalog, file-size,
  invariant-family, repository, JSON and `git diff --check` gates.
- `R14`: Independent REVIEW recomputes target, network ownership/count,
  containment, hashes, pins, dirty-baseline preservation, 12-path increment
  and all gates; it owns one separately recorded doctor fetch per review round.
- `R15`: On any post-start failure, execute DESIGN rollback: containment-check,
  preserve failed Core, restore prior Core/root/downstream preimages by hash,
  quarantine newly created root files, preserve all evidence/backups, record
  post-rollback doctor state, and stop without deletion. That verification
  owns exactly one conditional `ROLLBACK_VERIFIER` doctor fetch after restore,
  separate from the R4 prefix, so total worker/rollback operations are at most
  four. It cannot convert failure to success; target mismatch is recorded.
- `R16`: No provider/product API, credential, install, database, deployment,
  commit or push; no AI/agent-governance claim and no live-provider proof.
- `R17`: Invariant-family applicability is `NOT_APPLICABLE` for this
  maintenance-only tranche.

## Acceptance criteria

- `AC-01`: R1-R7 pass with exact full hashes and 17/17 root evidence.
- `AC-02`: R8 comparison proves exactly the authorized incremental worker
  paths; protected P4-C/governance artifacts match their BUILD-start hashes.
- `AC-03`: The named validators and repository commands below all exit zero;
  doctor has no failure and every explicit expected result matches.
- `AC-04`: Independent reviewer reproduces R14 and returns no open finding or
  waiver; reviewer alone creates the completion review.
- `AC-05`: Success satisfies every applicable R1-R17 requirement. Failure must
  still satisfy the always-applicable R1-R5, R7-R12 and R14-R17 precondition,
  exact-command, root/profile/sibling, knowledge/status, ownership, evidence,
  protection and no-effect rules, including complete R15 rollback. Only R6
  refreshed-target equality and R13 success gates are success-only. An
  unauthorized effect can never be accepted merely because restoration later
  succeeded. No partial-success disposition is permitted.

## Required commands

- `powershell -ExecutionPolicy Bypass -File "<core>\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "<exact-workspace-root>"`
- `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`
- `powershell -ExecutionPolicy Bypass -File "<core>\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "<exact-project-root>"`
- `python scripts/check_session_state.py`
- `python scripts/check_project_knowledge.py`
- `python scripts/generate_catalog.py --check`
- `python scripts/check_file_size.py`
- `python scripts/check_invariant_families.py --json`
- `python scripts/testing/validate_repository.py`
- `git diff --check`

The Work Order must bind exact paths into these named deterministic validators;
it may not change their predicates:

- `PIN_EQUALITY_PROBE`: one PowerShell invocation reads Core remote/HEAD/
  `origin/main`/status, manifest `cvfCoreCommit`, AGENTS header and ignored
  local-binding `resolvedCoreCommit`; exits zero only for exact URL, clean Core
  and five full values equal to the frozen target. It also requires
  `git check-ignore .cvf/local-binding.json` success and staged output empty.
- `ROOT_EFFECTS_PROBE`: one `python -c` JSON parser exits zero only when the
  root-effects receipt has the R12 schema fields, exact target, exactly 17
  unique before and after root paths, exact 12 unique incremental ceiling,
  ten mutable preimage/return entries, two worker evidence paths, preserved
  backup paths, and either the exact successful R4 three-operation sequence or
  a valid zero-to-three prefix plus exactly one R15 rollback-verifier record.
- `INCREMENTAL_SCOPE_PROBE`: one PowerShell invocation hashes current files
  against the receipt's BUILD-start inventory; exits zero only when every
  protected path is byte-identical, all worker deltas are within the 12-path
  ceiling, both worker evidence paths exist, staged set is empty, P4-C handoff/
  Work Order/review match their frozen hashes, and the assessment path was
  neither inventoried nor hashed.
- `JSON_PARSE_PROBE`: one Python invocation loads `.cvf/manifest.json`, policy,
  knowledge manifest, implementation status, canonical/mirror/bootstrap state
  and root-effects receipt; exits zero only when all parse.
- `REVIEW_OWNERSHIP_PROBE`: exits zero only when worker return names
  `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md`, the completion
  artifact is absent at worker handoff, and only the independent reviewer later
  creates `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-23.md`.

The exact inline command bodies and frozen path arrays belong in the Work
Order, but these validator names, inputs, predicates and expected zero/nonzero
semantics are the SPEC acceptance oracle.

## Claim boundary

PASS proves only local public-Core freshness, full pin/binding consistency,
bounded workspace-root refresh containment and synchronized project
continuity. It neither proves CVF controls AI/agent behavior nor opens P4-C
BUILD.

## Evidence-contract SPEC amendment — 2026-08-23

- Parent gate: evidence-contract DESIGN amendment `AMENDMENT_PASS`, findings/
  waivers `NONE/NONE`
- Amendment status: `OPEN_FOR_INDEPENDENT_SPEC_AMENDMENT_REVIEW`
- Author role: `SPEC_AUTHOR`
- Scope: replace only the proof semantics implicated by the three retained
  provenance blockers; all unaffected R1-R16 and ceilings remain in force

### Registered invariant family

The original `R17 NOT_APPLICABLE` decision is superseded for this amendment.
The materially changed R2 evidence contract triggers the invariant-family
standard through a shared receipt across terminal outcomes, outcome-controlled
fields, two validator surfaces and prior adjacent-family findings.

- Family id: `CVF-CORE-REFRESH-EVIDENCE-CONTRACT`
- Matrix: `docs/cvf/invariants/cvf-core-refresh-evidence-contract.json`
- Canonical SHA-256: `b62eae333a65a6770727abed9348828ac1ca61805f5fc8c48c5fd0e41053228e`
- Contract-source DESIGN canonical SHA-256:
  `b15ee41c0ee7d57609bc65a2c5bcbbeb116cb88c9a8a3b55df2191dab7ca5f67`
- Pin consumer: `docs/specs/cvf_core_refresh_evidence_contract_pin.py`
- Surfaces: `ROOT_EFFECTS_VALIDATOR`, `INDEPENDENT_REVIEW_VALIDATOR`
- Mutation exclusions: `NONE`

The matrix is the sole semantic owner of its eight terminal outcome shapes:
`PRE_RECONCILER_STOP`, `SUCCESS`, `FAILURE_PREFIX_0..3`, `FIRST_REVIEW` and
`REREVIEW_APPEND`. Later
Work Order and review artifacts must reference the family id and digest; they
must not copy or redefine its field, domain, relation or mutation rules.

### Amended requirements

- `AR1 — semantic ownership`: The pinned matrix alone owns exact outcome
  fields, domains, counters and preservation/correlation relations. DESIGN and
  this SPEC state architecture and claim boundaries only; later Work Order,
  validators and reviews consume the matrix without restating its rules.
- `AR2 — raw derivation`: Both declared validator surfaces independently derive
  every matrix field from raw filesystem inventories, command transcripts,
  trace2/packet records and reviewer-observed prestate. Matrix enum facts for
  checkpoint scope, ordered-prefix mapping, execution-window containment,
  identity disjointness and exact command contracts are recomputed predicates,
  never trusted receipt assertions.
- `AR3 — exhaustive stopped outcomes`: `PRE_RECONCILER_STOP` covers a failure
  after BUILD start but before reconciler invocation and therefore forbids a
  reconciler-return checkpoint while preserving prior candidates and owning a
  separate rollback verifier. `FAILURE_PREFIX_0` begins only after the exact
  reconciler envelope returns with a `RECONCILER_RETURN` checkpoint but no Git
  operation completed. The remaining prefix outcomes own counts one to three.
- `AR4 — conformance`: Both surfaces reject every matrix-generated negative
  mutation and accept exactly one independently emitted raw positive for each
  of the eight outcomes against the pinned digest. No expectation may be
  derived or changed during BUILD.
- `AR5 — failure remains failure`: Candidate preservation, a passing rollback
  verifier or matrix conformance cannot convert any `FAILURE_PREFIX_*` into
  success; the same applies to `PRE_RECONCILER_STOP`. Existing R15 stop
  semantics remain mandatory.
- `AR6 — unchanged boundaries`: The exact frozen target, 17 root effects,
  12 worker paths, ten carrier restoration, three-operation success path,
  zero-to-three failure prefix, one conditional rollback fetch, separately
  owner-scoped review fetches, no credentials and no provider/product/install/
  database/deployment/commit/push boundary remain unchanged.

### Amended acceptance criteria

- `AAC-01`: Each surface derives a receipt that matches exactly one pinned
  matrix shape and recomputes every matrix relation from raw evidence; no
  matrix-owned field or relation exists only in prose or validator code.
- `AAC-02`: Honest positives exist for all eight outcomes, including the two
  distinct zero-Git cases in AR3, and every generated mutation is rejected.
- `AAC-03`: Matrix-owned command-contract and zero-direct-fetch predicates make
  a bare fetch ineligible for rollback/reviewer-doctor outcomes; the claim
  remains deterministic correlation, not OS ancestry.
- `AAC-04`: Matrix-owned first-review and rereview pre/post fields and equality/
  digest/count relations support only reviewer-observed append preservation,
  not external immutability.
- `AAC-05`: `python scripts/check_invariant_families.py --json` returns PASS;
  the reviewer recomputes both canonical digests, verifies the pin, runs the
  full eight-outcome positive/mutation corpus against both surfaces and records
  the shared invariant-family proof fields.
- `AAC-06`: AR5-AR6 and all unaffected original acceptance criteria pass.
  Any digest drift, missing outcome, surface disagreement, ownership reuse,
  overclaim or unauthorized effect is `CHANGES_REQUIRED`, never a waiver-by-
  receipt.

### Invariant-family proof routing

- Applicability: `CVF-CORE-REFRESH-EVIDENCE-CONTRACT`, mandatory.
- Matrix/digest: exact values above.
- Adapter: deterministic pre-BUILD fixture/emitter owned by the later Work
  Order; no real service/provider emitter is claimed.
- Evidence tests: `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`, plus the
  later Work Order's exact inline eight-outcome corpus command.
- Evidence owner: worker for root-effects conformance; independent reviewer for
  reviewer-surface conformance and digest recomputation.
- Reviewer duty: recompute matrix and DESIGN digests, verify the pin, rerun all
  positives/mutations on both surfaces, sample one raw positive per outcome,
  and confirm the matrix was fixed before BUILD.

### Amended claim boundary and next move

Repair clarification: the matrix's `checkpoint_core` equality is a canonical
tracked target/tree/worktree comparison with an allowed Git-admin-delta
classification; it is not full `.git` byte equality. For
`FAILURE_PREFIX_1`, the matrix admits either reconciler-only failure or the
exact initializer envelope failing before its fetch, while retaining network
prefix count one. These are matrix-owned semantics under the digest above.

PASS of this amendment proves only deterministic consistency between named
filesystem checkpoints, command envelopes/Git trace surfaces and a reviewer's
observed pre/post append relation. It does not prove continuous filesystem
absence, kernel process ancestry, externally immutable history, CVF control of
AI/agents, provider behavior or production readiness.

Next move is independent SPEC amendment review only. The current Work Order is
not amended by this SPEC authority. Work Order repair, reconciliation, network
and BUILD remain unauthorized.
