# Independent Work Order Authorization Review - P4-E Identity Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING`
- Review role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Phase reviewed: `WORK_ORDER` pending `PRE_EXECUTION_REVIEW`
- Risk ceiling: `R2`
- Date: `2026-09-09`
- Execution HEAD: `b5eb07188ee66f9190c20fdd75dedda58641f1a4`
- Branch: `docs/p4e-spec`
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`
- Findings: 3
- Waivers: NONE

## Startup Acknowledgment

Mode `p4e_identity_conversation_routing_work_order_ready_for_independent_authorization_review`;
active handoff `SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC_2026-09-09.md`;
next allowed move is independent P4-E Work Order authorization review only;
parked operator checkpoint is that P4-E BUILD is not authorized and Phase 5,
external-repository absorption, governed-catalog schema migration, and XR1
historical-object debt remain parked. Active role declared:
`INDEPENDENT_AUTHORIZATION_REVIEWER`.

`SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json` and canonical
`SESSION/ACTIVE_SESSION_STATE.json` agree on mode, active handoff, and next
allowed move. `AGENTS.md`, the accepted DESIGN, the accepted SPEC, the DESIGN
review, and the SPEC rereview named by `requiredReads` were read.

## Independence And Review Boundary

This reviewer authored the P4-E SPEC Generation 1 review and Generation 2
rereview. This reviewer did not author the Work Order, the paired GC-018
baseline, the exact manifest, the SPEC, the DESIGN, or any matrix, and will
implement nothing. `AGENTS.md` requires REVIEWER independence from
`IMPLEMENTATION_WORKER`, which is satisfied. Continuity of the same reviewer
across SPEC and Work Order phases is a governance routing choice for the
ORCHESTRATOR; it is recorded here, not asserted as sufficient by this reviewer.

All actions were read-only except creating this artifact at exact manifest path
81, the only file this lane is permitted to author. No implementation, product
source repair, dependency install, provider call, network, live, deploy,
database, staging, commit, or push action was performed.

## Before / After Status

| Field | Value |
| --- | --- |
| Branch before | `docs/p4e-spec` |
| HEAD before | `b5eb07188ee66f9190c20fdd75dedda58641f1a4` |
| `git status --short` before | empty |
| Staging before | empty |
| HEAD after | `b5eb07188ee66f9190c20fdd75dedda58641f1a4` (unchanged) |
| Changed manifest after | exactly one added untracked path: `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_WORK_ORDER_AUTHORIZATION_REVIEW_2026-09-09.md` (manifest path 81) |
| Staging after | empty |
| `git diff --check` | clean |

## Recomputed Source Hashes

Every hash below was recomputed from the working tree at the execution HEAD.

| Artifact | Recomputed SHA-256 | Required value | Result |
| --- | --- | --- | --- |
| Work Order | `26418059877a6705e1205a8c41b91d9413959637f84e913efe9ef754a5fbf175` | as assigned | MATCH |
| Exact manifest | `edb56012d87e7c4e9b3c715feba6d32a65a90b70064c9fa7d0d3b2abdc03a846` | as assigned | MATCH |
| GC-018 baseline | `6ed63ee7648bfbe93ab9cfdd111f68fd15ef19030b0cea8b47974a2899ad8500` | not pre-supplied | RECORDED |
| SPEC | `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618` | Work Order pin | MATCH |
| DESIGN | `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9` | Work Order pin | MATCH |
| SPEC rereview | `e9c21bd7c5627a0529b4d15d5a1533bd834ec886d13002c77ecdaa2a8094c3cc` | Work Order pin | MATCH |
| SPEC review Gen 1 | `a4ee2f643186ca11be7d08c8e555aa55372c63b20d58bb3ab81b24e5b83d17f8` | prior review record | MATCH |
| Mapping matrix | `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a` | Work Order pin | MATCH |
| Resolution matrix | `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc` | Work Order pin | MATCH |
| Placement matrix | `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56` | Work Order pin | MATCH |

The `exactManifestSha256` recorded inside the Work Order equals the
independently recomputed manifest hash. The Work Order, the baseline, and
`docs/specs/p4e_invariant_pins.py` all carry the same three matrix digests.

### Dispatch pin sequencing

`dispatchBaseHead` is `e367bc99...` while execution HEAD is `b5eb0718...`. This
gap was examined specifically for the pin-then-edit defect class:

- `82e00a2` added the baseline, manifest, Work Order, and the Generation 2
  rereview. `git log --diff-filter=M` shows the rereview has **no** modifying
  commit; it entered as a pure addition, so no pinned artifact was edited after
  its hash was pinned.
- `b5eb071` touched only continuity surfaces (session state, bootstrap,
  handoff, index, roadmap, knowledge, implementation status).
- `git diff --stat e367bc9 b5eb071 -- docs/specs/ docs/cvf/` is empty: the SPEC,
  all three matrices, and the pin module are byte-identical to the dispatch
  base.

No pin drift exists. The Work Order correctly instructs the worker to capture
`executionBaseHead` fresh and never substitute the older dispatch anchor.

## Verification Results Against Assigned Checks

| # | Check | Result |
| --- | --- | --- |
| 1 | Work Order SHA-256 | PASS - exact match |
| 2 | Exact-manifest SHA-256 | PASS - exact match |
| 3 | 94 sequential unique paths, role ownership | PASS - see below |
| 4 | Worker ownership limited to 15-80 | PASS |
| 5 | Customer/vessel scaffolds protected | PASS |
| 6 | AC-16 requires a real probe | PASS on substance; see Finding 1 for path numbers |
| 7 | `TOKEN_KEY_RETIREMENT_BLOCKED` single named owner | PASS |
| 8 | SQL atomicity, failure semantics, evidence, ceiling, no-commit | PASS |
| 9 | No undocumented path, authority expansion, orphan artifact | PASS with Finding 3 |

### Check 3 - path accounting (mechanically verified)

Parsing the manifest yields exactly 94 numbered rows, numbered `1..94` with no
gap or repeat, and 94 distinct paths with zero duplicates. Band boundaries were
confirmed by index: path 15 `pyproject.toml`, path 80 the worker return, path 81
this artifact, path 82 the completion review, path 83 `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
path 94 `docs/catalog/MODULE_CATALOG.md`.

Existence by band: all 14 settled governance paths exist; all 12 closer/steward
paths exist; both reviewer paths (81, 82) correctly do not yet exist; in the
worker band, 24 paths exist and 42 are to be created. A forward-looking
changed-set ceiling legitimately names paths that do not yet exist, and the
Work Order forbids creating a placeholder solely to satisfy the list.

`database/migrations/011_p4e_identity_conversation_routing.sql` is the correct
next migration number; the highest existing is `010_integration_edge.sql`.

### Check 4 - worker band containment

`Work-Order Fulfillment Manifest` groups every worker obligation inside 15-80.
`Protected And Forbidden Scope` forbids worker edits to paths 1-14 and 81-94.
`Reviewer Closure Conversion` reserves 81-82 to reviewers and 83-94 to the
closer and session sync steward. `laneOwnedPaths` restricts the current review
lane to path 81 only. No worker obligation was found that requires a path
outside 15-80.

### Check 5 - scaffold protection

Both scaffold directories were inspected and contain only their README. The
manifest names both READMEs as protected and forbids any new path under either
directory. The Work Order repeats the prohibition in `Protected And Forbidden
Scope` and binds it in `Carry-Forward Resolution` with exact-diff/path-scan and
dependency-import negative-test evidence. This closes the Generation 2
carry-forward.

### Check 6 - AC-16 probe substance

The Work Order requires the probe to import the real Workspace API composition
root, instantiate the production composition with injected stores, inspect bound
proposal/placement repository types, and fail if the process-local repository is
reachable from production composition. It states twice that a source-comment
assertion is forbidden and that scanning comments, checking a string, or
asserting a constructor exists does not satisfy AC-16. `InMemoryExternalIngressRepository`
is a required literal in the Required Proof Manifest. The substance of this
carry-forward is properly closed; only the cited path numbers are wrong
(Finding 1).

### Check 7 - secret-authority ownership

A repository-wide search for `TOKEN_KEY_RETIREMENT_BLOCKED` returns only
governed documentation: SPEC R19, the rework response, the Work Order, the
handoff, and `IMPLEMENTATION_STATUS.json`. It appears in none of the three
invariant matrices, which is required. The Work Order names
`apps/integration-edge/src/integration_edge/verification/sender_keys.py`
(manifest path 39) as sole runtime owner of `TokenKeyRetirementReadinessV1` and
`SenderTokenKeyAuthority.retire_previous`, restricts the record to non-secret
fields, and forbids identity-mapping and conversation-routing from importing it.
This closes the third Generation 2 carry-forward.

### Check 8 - boundaries and evidence

- SQL atomicity: named in the autonomy rule, the escalation condition, the
  ordered BUILD plan, the review gate, and the stop conditions. Inability to
  prove SQLite/PostgreSQL atomicity is an explicit stop.
- PostgreSQL honesty: the packet forbids installing, connecting to a shared or
  production database, or substituting a mock while claiming AC-05/AC-10, and
  requires an honest environment blocker instead.
- Failure semantics: fail-closed direction is preserved - ambiguity, corruption,
  stale version, unavailable authority, lineage mismatch, and unknown claim
  state never degrade to a privileged route. This is consistent with the
  accepted SPEC R15 and with the F2 repair verified in Generation 2.
- External-effect ceiling: `externalInvocationCeiling: 0`,
  `cumulativeExternalInvocationCount: 0`, `invocationBoundary` zero for provider,
  network, credential, database, install, deployment, and external agent; the
  pre-BUILD gate initializes eight effect counters to zero.
- Commit boundary: `WORKER_MUST_NOT_COMMIT` appears six times; worker staging,
  commit, and push are `FORBIDDEN`; commit authority passes to `COMMIT_STEWARD`
  only after `COMPLETION_REVIEW_PASS`; the worker may not perform destructive
  Git rollback.
- Source Verification Block: all five implementation-source rows were checked
  line by line and every cited line number and symbol resolves exactly -
  `repository.py:13 InMemoryExternalIngressRepository`,
  `main.py:41 include_router(external_ingress_router)`,
  `hmac.py:86 verify_hmac`, `routing/service.py:7 RoutingService`,
  `permission.py:28 _ACTION_MIN_ROLE`.

### Check 9 - undocumented paths and orphans

Every project-relative path cited in the Work Order that is absent from the
manifest was enumerated and classified. All 20 are read-only references:
governance checkers, two reference standards, protected scaffold READMEs,
existing gate scripts, and existing invariant tests. None is a changed-set
member, so none is an orphan or an undocumented change path. The eight cited
project-local scripts and two existing invariant tests all exist. No authority
expansion beyond the accepted SPEC was found.

## Gate Evidence (independently rerun, read-only)

```text
python scripts/check_invariant_families.py      -> INVARIANT FAMILY CHECK: PASS
python scripts/check_session_state.py           -> SESSION STATE: PASS
python scripts/check_project_knowledge.py       -> PROJECT KNOWLEDGE: PASS
python scripts/check_file_size.py               -> FILE SIZE GUARD: PASS
python scripts/generate_catalog.py --check      -> CATALOG VERIFY: PASS
git diff --check                                -> clean
git status --short                              -> empty before authoring
```

No product test suite was executed: this is authorization review of an
unimplemented tranche, and the P4-E test paths do not yet exist.

## Findings

### Finding 1 - Four path citations contradict the manifest (MAJOR, blocking)

**Where:** Work Order lines 271, 272, and 387.

**Problem:** Four normative path-number citations disagree with the manifest
they are pinned to. In each case the Work Order names the correct filename but
the wrong ordinal, and each is off by one:

| Work Order text | Cited number resolves to (manifest) | File the same sentence names | Correct number |
| --- | --- | --- | --- |
| AC-16 "path 75 must import the real Workspace API composition root" | `tests/integration/test_p4e_backend_parity.py` | `tests/integration/test_p4e_workspace_composition.py` | 76 |
| AC-16 "negative import test at path 78" | `tests/integration/test_p4e_postgres_live.py` | `tests/unit/test_p4e_dependency_boundary.py` | 79 |
| Retirement "unit test at path 70" | `tests/unit/test_p4e_conversation_routing.py` | `tests/unit/test_p4e_sender_key_retirement.py` | 71 |
| Invariant proof "Evidence: path 66" | `contracts/conversation/conversation-placement.schema.json` | `tests/unit/test_p4e_invariants.py` | 67 |

**Why this blocks:** The manifest is declared "an indivisible part of this Work
Order" and the sole controller of path membership and owner class, and the Work
Order says owner-class change or manifest drift stops work. A worker following
the cited ordinals would put the AC-16 composition probe in the backend-parity
file and the negative-import test in the PostgreSQL live file, then report
AC-16 satisfied. The AC-16 command block does name the correct two filenames,
so intent is recoverable - but a normative packet that requires exact path
accounting must not require the worker to notice and silently correct four
internal contradictions. This is precisely the ambiguity class the exact
manifest exists to eliminate.

**Required repair:** Correct the four ordinals to 76, 79, 71, and 67. No
manifest change is needed; the manifest is correct and its hash should not
change.

### Finding 2 - Review Gate says "93 paths" vs the 94 ceiling (MINOR, blocking)

**Where:** Work Order line 517, `## Review Gate`: "must first verify exact
source hashes, all 93 paths".

**Problem:** Every other statement in both artifacts says 94 - the Work Order
heading `Exact Final Changed-Set Ceiling - 94 Paths`, `changedSetScope(phase)`,
the manifest heading and purpose, and the mechanically counted 94 rows. This
lone `93` is an isolated numeric error in the clause that defines the
authorization reviewer's own obligation, so it understates the ceiling that a
future reviewer is told to verify.

**Required repair:** Change `93` to `94`.

### Finding 3 - Two cited standards unresolvable project-locally (MINOR)

**Where:** Work Order `Agent Handoff Contract Control Block` contract source
`docs/reference/CVF_AHB_T2_AGENT_HANDOFF_CONTRACT_RATIFICATION_2026-06-16.md`
and `Semantic Convergence Outcome` standard
`docs/reference/semantic_convergence_control/CVF_SEMANTIC_CONVERGENCE_AND_ESCALATION_CONTROL_STANDARD.md`.

**Problem:** Neither path exists in this project or in the resolved CVF Core at
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4`. Both were located in the private
provenance repository. The Work Order already annotates two other
private-provenance paths inline
(`governance/compat/run_agent_autorun_workflow_gate.py` and
`run_worker_return_fast_gate.py` are each marked "private-provenance reference
only"), so the convention exists and these two were simply not given it. A
worker performing the required first action of reading the named standards will
find both missing and cannot tell whether that is expected or a broken pin.

**Required repair:** Annotate both citations as private-provenance references
not present in the project working tree, matching the existing convention.

## Disposition

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

- Findings: 3 (1 MAJOR blocking, 2 MINOR of which Finding 2 is blocking)
- Waivers: NONE

`AUTHORIZATION_REVIEW_PASS` requires findings and waivers `NONE/NONE`, so BUILD
is not authorized. All three repairs are documentation-only edits confined to
the Work Order at manifest path 14, which is amendable by the manifest's own
terms. No manifest edit, no matrix edit, and no repin is required, so the three
matrix digests and the manifest hash must remain unchanged; only the Work Order
hash will change and must be recomputed and re-pinned wherever it is cited.

Substantively, the packet is sound. The path ceiling is exact and internally
consistent, owner bands are clean, the external-effect ceiling is zero, the
no-commit boundary is unambiguous, the fail-closed semantics match the accepted
SPEC, every source pin recomputes correctly, no pin drift exists across the
dispatch gap, and all three Generation 2 carry-forwards have binding resolutions
with named evidence. The findings are citation-integrity defects in an otherwise
well-formed R2 dispatch packet, not design or authority defects.

A rereview limited to the three repairs should be sufficient to reach
`AUTHORIZATION_REVIEW_PASS`.

## Lane Release

The `INDEPENDENT_AUTHORIZATION_REVIEWER` lane is released back to the
ORCHESTRATOR with disposition `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`. The lane
is **not** released to `IMPLEMENTATION_WORKER`, because release to the worker is
conditioned on `AUTHORIZATION_REVIEW_PASS` with findings and waivers
`NONE/NONE`.

- Final HEAD: `b5eb07188ee66f9190c20fdd75dedda58641f1a4`
- `git status --short`: one untracked path, this artifact at manifest path 81
- Staging: empty
- Exact changed set: `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_WORK_ORDER_AUTHORIZATION_REVIEW_2026-09-09.md`
- Commit action: none performed; `WORKER_MUST_NOT_COMMIT` and reviewer
  no-commit boundaries observed

## External Effect Counters

| Counter | Value |
| --- | --- |
| providerCallCount | 0 |
| externalNetworkCallCount | 0 |
| credentialReadCount | 0 |
| dependencyInstallCount | 0 |
| deploymentCount | 0 |
| databaseMutationCount | 0 |
| stageCount | 0 |
| commitCount | 0 |
| pushCount | 0 |

## Claim Boundary

This artifact is an independent authorization review of dispatch documentation
only. It authorizes nothing, implements nothing, and asserts no runtime,
provider-governance, deployment, public-sync, or production-readiness claim. It
does not claim any P4-E implementation path exists or works. Verification
covered hash recomputation, dispatch-pin sequencing, mechanical path accounting,
owner-band containment, source line/symbol resolution, carry-forward closure,
boundary/ceiling inspection, and read-only gate reruns at HEAD
`b5eb07188ee66f9190c20fdd75dedda58641f1a4`. BUILD remains prohibited.
