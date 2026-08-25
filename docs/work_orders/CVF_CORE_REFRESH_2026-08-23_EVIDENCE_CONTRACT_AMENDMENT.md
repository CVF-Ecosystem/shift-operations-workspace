# Work Order Amendment — CVF Core Refresh Evidence Contract

- Amendment id: `CVF-CORE-REFRESH-WO-EVIDENCE-AMEND-2026-08-23`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Status: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- BUILD authority: `NOT GRANTED`
- Parent Work Order: `docs/work_orders/CVF_CORE_REFRESH_2026-08-23_WORK_ORDER.md`
- Parent raw SHA-256:
  `6ab0929b0d1050c6315fe27d1e18124c7e5b1867106312a7a423e4d8ea906a1a`
- DESIGN canonical SHA-256:
  `b15ee41c0ee7d57609bc65a2c5bcbbeb116cb88c9a8a3b55df2191dab7ca5f67`
- SPEC canonical SHA-256:
  `19f7e4cd805aecc6423b17513d10bb3bffe2bb5fc13a25f5eba59c921c8f6bda`
- Invariant family: `CVF-CORE-REFRESH-EVIDENCE-CONTRACT`
- Matrix: `docs/cvf/invariants/cvf-core-refresh-evidence-contract.json`
- Matrix canonical SHA-256:
  `b62eae333a65a6770727abed9348828ac1ca61805f5fc8c48c5fd0e41053228e`

## 1. Authority and precedence

This artifact is a prospective, independently reviewable amendment. It does
not itself authorize reconciliation, network activity or BUILD. It becomes
operative only after an independent authorization review records
`AUTHORIZATION_REVIEW_PASS` for this exact raw-byte artifact and the operator
separately grants BUILD authority.

The parent Work Order remains byte-exact historical evidence. After this
amendment becomes operative, its precedence is:

1. the pinned matrix is the sole semantic owner of terminal outcome fields,
   domains, relations and counters;
2. this amendment replaces the parent sections named below;
3. every parent clause not expressly replaced remains mandatory.

Replaced parent material:

- the protected pre-Work-Order path oracle and its frozen 26-path assumption;
- the evidence-related parts of `G6 preflight and BUILD sequence`;
- the complete `Machine receipt contract and validators` section, including
  its inline Python body;
- the independent REVIEW append protocol;
- candidate-preservation parts of `Mandatory rollback`.

The parent inline Python is historical and **must not be executed** after this
amendment is operative. Requiring both old and amended validators is forbidden.

## 2. Retained ceilings and boundaries

The following parent boundaries remain exact and unchanged:

- frozen target:
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`;
- public remote:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`;
- reconciler source SHA-256:
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`;
- workspace-root effects: exactly the parent Work Order's 17 paths;
- worker repository increment: exactly the parent Work Order's 12 paths;
- mutable carriers: exactly the first ten of those 12 paths;
- successful worker network path: exactly three ordered operations;
- failed worker network prefix: zero through three operations, plus exactly
  one separately owned conditional rollback-verifier doctor fetch;
- independent REVIEW: exactly one separately owned doctor fetch per run;
- provider, credential, dependency/package installation, database, deployment,
  commit and push authority: zero;
- root-wrapper refresh: only the parent's exact 17 root effects;
- assessment access or evidence use: forbidden.

This amendment and its independent review are pre-BUILD governance inputs.
The frozen adapter
`docs/work_orders/cvf_core_refresh_evidence_adapter.py` is a third pre-BUILD
governance input. These inputs do not increase the 12-path worker increment.

## 3. Superseding BUILD-start baseline

Immediately before BUILD acknowledgment, after authorization-review PASS and
before any BUILD mutation, the worker must:

1. derive the exact sorted non-assessment porcelain path set;
2. require staged set empty and downstream `HEAD == origin/main` at the parent
   execution base;
3. require the parent, this amendment, frozen adapter, final DESIGN/SPEC/
   reviews, matrix, registry and Python pin to be present in that set or
   tracked state as applicable;
4. write a contained raw baseline manifest with path, status, existence,
   type, size and raw SHA-256 for every path;
5. preserve a byte preimage for every existing dirty path and independent
   byte preimages for all ten mutable carriers;
6. record the sorted LF path-list digest and baseline-manifest raw digest.

The independent authorization review must freeze the expected path set and LF
digest. BUILD must stop on any later set/digest mismatch. All paths outside the
ten mutable carriers and two worker evidence paths remain byte-exact. The
assessment is excluded without opening, reading, hashing or inventorying it.

`buildStart` occurs only after this baseline, all 17 root preimages, all ten
carrier preimages, containment checks and the failed-candidate inventory below
are complete. A failure after that point and before reconciler invocation is
`PRE_RECONCILER_STOP`; preflight refusal before `buildStart` is not a BUILD
terminal outcome.

## 4. Contained runtime evidence

All amendment-only runtime artifacts live below one freshly created,
containment-checked directory under workspace-root `_cvf-core-backups`. They
must never be written into the repository or any sibling project. The evidence
tree contains, at minimum:

- BUILD-start baseline and preimages;
- complete failed-candidate inventories;
- command envelopes, transcripts and exit records;
- trace2 and packet traces;
- `RECONCILER_RETURN` observation when applicable;
- final candidate/Core inventories;
- `PRIOR_REVIEW_STATE` records;
- review anchors;
- the frozen adapter source, conformance corpus and validator results.

Every evidence path is resolved before use, must remain inside that one tree,
must not be a symlink, and carries a raw SHA-256. No evidence artifact may
contain credentials or authorization headers.

## 5. Exact generic command envelope

One generic PowerShell envelope is mandatory for each outer invocation:

- `RECONCILER` — the parent's exact no-extra-flag reconciler command;
- `INITIALIZER` — the parent's exact initializer command;
- `ROLLBACK_VERIFIER` — the exact workspace-doctor PowerShell command;
- `REVIEWER_DOCTOR` — the same exact doctor command in a fresh reviewer
  process.

Before launching the child, the envelope must create a fresh UUID-v4 and
record its own `$PID`, owner, normalized executable/arguments, UTC start,
transcript path and fresh trace2/packet paths. It sets the parent's
noninteractive/no-credential variables and additionally:

- `CVF_OUTER_INVOCATION_UUID=<uuid>`;
- `CVF_OUTER_POWERSHELL_PID=<$PID>`;
- `GIT_TRACE2_ENV_VARS=CVF_OUTER_INVOCATION_UUID,CVF_OUTER_POWERSHELL_PID`.

After the child exits, the same envelope records UTC exit, exact exit code and
raw transcript/trace hashes, then removes every trace/correlation variable
before any validation Git command. Each governed Git span must expose both
values in exact-SID trace2 `def_param` events, use the expected argv/endpoint,
and have start/exit inside its outer window. The raw outer PID/UUID join,
ordered-prefix mapping, window containment, identity disjointness and exact
command contract are independently recomputed facts. They support only
`DETERMINISTIC_CROSS_SURFACE`, never kernel-attested ancestry.

A direct `git fetch` cannot satisfy either doctor owner. Each rollback/review
doctor requires its exact PowerShell envelope, transcript, exit and the one
doctor-owned fetch. BUILD, rollback and all review UUID/SID/span identities
must be pairwise disjoint.

## 6. Candidate and Core observation

At BUILD start, inventory every preexisting
`.Controlled-Vibe-Framework-CVF-failed-*` directory as contained absolute
path plus complete, sorted relative path/type/size/raw-SHA-256 entries.

If the reconciler is invoked, its outer envelope must write
`RECONCILER_RETURN` immediately after the child exits and before any worker
rollback handler or later project mutation. The raw observation binds the
reconciler UUID/PID/window/exit and inventories:

- canonical Core tracked target, tracked tree and worktree state;
- explicit Git-administrative-delta classification;
- every preexisting failed candidate;
- every newly observed failed candidate.

Final evidence recomputes the same scoped inventories. Candidate preservation
and tracked-Core/admin-delta equality are derived solely through the pinned
matrix. Full `.git` byte equality is neither required nor claimed. When
rollback displaces a replacement, its final failed-Core comparison uses the
same tracked target/tree/worktree plus allowed-admin-delta scope.

`NOT_OBSERVED_AT_RECONCILER_RETURN` is valid only as a point-in-time
observation. Final absence cannot prove continuous historical absence. Every
prior or newly observed candidate must remain contained and preserve the
matrix-required final relation; delete/move-without-record is forbidden.

## 7. Exhaustive terminal routing

Exactly one matrix outcome must match independently derived raw facts:

- `PRE_RECONCILER_STOP`: BUILD started, reconciler was never invoked, worker
  prefix is zero, prior candidates are preserved, one rollback doctor runs,
  and no reconciler envelope/checkpoint fields exist;
- `FAILURE_PREFIX_0`: reconciler envelope returned and
  `RECONCILER_RETURN` exists, but the governed Git prefix is zero;
- `FAILURE_PREFIX_1`, `FAILURE_PREFIX_2`, `FAILURE_PREFIX_3`: exactly the
  executed prefix count, including the matrix-owned PREFIX_1 command variants;
- `SUCCESS`: exact ordered three-operation path and no rollback verifier;
- `FIRST_REVIEW`: reviewer observes absent completion and empty review-anchor
  directory before one run/anchor;
- `REREVIEW_APPEND`: reviewer observes and preserves prior review state before
  one run/anchor append.

No stopped/failure outcome may be upgraded to success by a passing rollback
doctor, candidate preservation or matrix conformance.

## 8. Independent review prestate

Before creating or modifying the completion review, the independent reviewer
writes `PRIOR_REVIEW_STATE` inside the evidence tree. For first review it
records completion absent and anchor inventory empty. For rereview it records:

- current completion raw bytes and SHA-256;
- canonical current `reviewRuns` bytes and SHA-256;
- exact sorted anchor path/type/size/raw-SHA-256 inventory;
- fresh reviewer envelope UUID and observation time.

After the exact doctor run, the reviewer must prove the observed completion
prefix, prior runs and prior anchors byte-exact, then add exactly one new run
and one new anchor. The review projection must match `FIRST_REVIEW` or
`REREVIEW_APPEND`. The only permitted claim is
`REVIEWER_OBSERVED_APPEND_PRESERVATION`; no WORM, signature, external
immutability or pre-observation history claim is allowed.

## 9. Matrix consumption and frozen adapter boundary

The matrix is loaded dynamically and verified against its canonical digest.
Neither the raw receipt, adapter nor validator may redefine matrix fields,
domains, relations, counters or accepted constants. Each surface derives its
projection from raw filesystem/envelope/trace/prestate artifacts; receipt
booleans or enum assertions are not trusted substitutes.

The complete raw-to-projection adapter source is the pre-BUILD governance file
`docs/work_orders/cvf_core_refresh_evidence_adapter.py`, raw SHA-256
`627aa1ef282b0b27987f192ab964861f281e58d6e140c7754b9f73e94277b9d2`.
Independent authorization review verifies those exact bytes. BUILD copies
only those reviewed bytes into the contained evidence tree and rechecks the
same digest before import. The adapter exports:

- `derive_root_effects(raw_case, matrix)`;
- `derive_independent_review(raw_case, matrix)`.

Both exports consume all eight outcome families through the same common
matrix-driven derivation; `surface` identifies an independently collected raw
manifest, not an outcome subset. Raw input forbids `outcomeId`, shape ids,
matrix enum assertions, counters and preservation booleans. Its closed schemas
contain only content-addressed candidate/review trees, contained Core Git
copies, command envelopes, raw transcript/exit/trace2/packet descriptors,
network-operation facts including descendant packet SID/PID, and prior command
bundles. Exact command strings come
from the reviewed workspace layout, never caller-supplied expected values.

The adapter resolves one fresh direct child of workspace-root
`_cvf-core-backups`, rejects symlink/traversal escape, recomputes directory
inventories from actual bytes, runs only read-only local Git queries against
contained Core evidence copies, joins command UUID/PID/windows to exact trace
start/exit/def-param/argv and packet remote/target observations, derives direct
fetch substitution and enforces aggregate identity disjointness. Review cases
scan actual pre/post completion, run and anchor trees; they require exact prior
preservation, one new run and one new anchor whose JSON binds the current
reviewer UUID/PID/SIDs and run digest.

The adapter may normalize raw evidence, but may not call the network, inspect
the repository assessment, mutate repository files or derive expected values
from a test case during validation. Adapter drift or an additional adapter
implementation is a stop condition; the authorization reviewer does not
author or repair adapter code while acting as reviewer.

## 10. Frozen matrix-consumer/conformance runner

The following source is the complete frozen runner. It copies no matrix rule;
it imports the separately reviewed contained adapter, loads the matrix, uses
the repository's generic invariant evaluator and proves both surface routes.

```python
import base64, hashlib, importlib.util, json, os, pathlib, re, sys

ROOT = pathlib.Path.cwd().resolve()
BACKUP = (ROOT.parent / "_cvf-core-backups").resolve()
EVIDENCE = pathlib.Path(os.environ["CVF_REFRESH_EVIDENCE_ROOT"]).resolve(strict=True)
MATRIX_PATH = ROOT / "docs/cvf/invariants/cvf-core-refresh-evidence-contract.json"
REVIEW_PATH = ROOT / "docs/decisions/CVF_CORE_REFRESH_EVIDENCE_CONTRACT_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md"
ADAPTER_PATH = ROOT / "docs/work_orders/cvf_core_refresh_evidence_adapter.py"
MATRIX_SHA = "b62eae333a65a6770727abed9348828ac1ca61805f5fc8c48c5fd0e41053228e"
ADAPTER_SHA = "627aa1ef282b0b27987f192ab964861f281e58d6e140c7754b9f73e94277b9d2"
OUTCOMES = {
    "PRE_RECONCILER_STOP", "SUCCESS", "FAILURE_PREFIX_0",
    "FAILURE_PREFIX_1", "FAILURE_PREFIX_2", "FAILURE_PREFIX_3",
    "FIRST_REVIEW", "REREVIEW_APPEND",
}
SURFACES = {"ROOT_EFFECTS_VALIDATOR", "INDEPENDENT_REVIEW_VALIDATOR"}

def sha_bytes(value): return hashlib.sha256(value).hexdigest()
def sha(path): return sha_bytes(pathlib.Path(path).read_bytes())
def canonical_sha(document):
    raw = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha_bytes(raw.encode("utf-8"))
def contained(value, file=True):
    raw = pathlib.Path(value); assert raw.is_absolute() and not raw.is_symlink()
    path = raw.resolve(strict=True); assert path.is_relative_to(EVIDENCE)
    assert path.is_file() if file else path.is_dir()
    return path
def materialize(bundle, bundle_sha):
    target = EVIDENCE / "corpus" / bundle_sha
    target.mkdir(parents=True, exist_ok=True)
    assert isinstance(bundle["files"], dict)
    for rel, encoded in bundle["files"].items():
        assert pathlib.PurePosixPath(rel).as_posix() == rel and ".." not in pathlib.PurePosixPath(rel).parts
        path = (target / pathlib.PurePosixPath(rel)).resolve()
        assert path.is_relative_to(target.resolve())
        data = base64.b64decode(encoded, validate=True); path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists(): assert path.is_file() and path.read_bytes() == data
        else: path.write_bytes(data)
    return target
def expand(value, base):
    if isinstance(value, list): return [expand(item, base) for item in value]
    if not isinstance(value, dict): return value
    result = {key: expand(item, base) for key, item in value.items()}
    if set(result) in ({"path", "sha256"}, {"path", "treeSha256"}):
        rel = pathlib.PurePosixPath(result["path"]); assert rel.as_posix() == result["path"] and ".." not in rel.parts
        result["path"] = str((base / rel).resolve())
    return result

assert EVIDENCE.parent == BACKUP and EVIDENCE.is_dir() and not EVIDENCE.is_symlink()
matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
assert matrix["familyId"] == "CVF-CORE-REFRESH-EVIDENCE-CONTRACT"
assert canonical_sha(matrix) == MATRIX_SHA and {item["outcomeId"] for item in matrix["outcomes"]} == OUTCOMES
assert sha(ADAPTER_PATH) == ADAPTER_SHA
spec = importlib.util.spec_from_file_location("cvf_refresh_frozen_adapter", ADAPTER_PATH)
assert spec and spec.loader
adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
sys.path.insert(0, str(ROOT))
from scripts.invariant_family_contract import generate_mutations, matches_shape_exactly
surfaces = {"ROOT_EFFECTS_VALIDATOR": adapter.derive_root_effects, "INDEPENDENT_REVIEW_VALIDATOR": adapter.derive_independent_review}

review = REVIEW_PATH.read_text(encoding="utf-8")
blocks = re.findall(r"<!-- CVF_CORPUS_BUNDLE_BEGIN -->\s*([A-Za-z0-9+/=]+)\s*<!-- CVF_CORPUS_BUNDLE_END -->", review)
pins = re.findall(r"CVF_CORPUS_BUNDLE_SHA256::([0-9a-f]{64})", review)
assert len(blocks) == len(pins) == 1
bundle_bytes = base64.b64decode(blocks[0], validate=True); assert sha_bytes(bundle_bytes) == pins[0]
bundle = json.loads(bundle_bytes.decode("utf-8")); assert set(bundle) == {"schemaVersion", "files", "positiveCases", "negativeCases"}
assert bundle["schemaVersion"] == "1.0" and set(bundle["positiveCases"]) == OUTCOMES
corpus_root = materialize(bundle, pins[0])

def matches(projection):
    found = []
    for outcome in matrix["outcomes"]:
        for shape in outcome["shapes"]:
            if matches_shape_exactly(shape, projection, matrix): found.append((outcome["outcomeId"], shape["shapeId"]))
    return found

for expected_outcome, case in sorted(bundle["positiveCases"].items()):
    assert set(case) == SURFACES
    projections = {}
    for surface_name, derive in surfaces.items():
        raw_case = expand(case[surface_name], corpus_root)
        projection = derive(raw_case, matrix); projections[surface_name] = projection
        matched = matches(projection); assert len(matched) == 1 and matched[0][0] == expected_outcome
        for mutation in generate_mutations(matrix, matched[0][1], projection):
            assert mutation.payload != derive(raw_case, matrix) and matches(mutation.payload) == []
    assert projections["ROOT_EFFECTS_VALIDATOR"] == projections["INDEPENDENT_REVIEW_VALIDATOR"]

for negative in bundle["negativeCases"]:
    assert set(negative) == {"surface", "rawCase"} and negative["surface"] in SURFACES
    try: surfaces[negative["surface"]](expand(negative["rawCase"], corpus_root), matrix)
    except (AssertionError, KeyError, ValueError, OSError): pass
    else: raise AssertionError("raw-negative case accepted")

current = {
    "ROOT_EFFECTS_VALIDATOR": json.loads(contained(os.environ["CVF_REFRESH_CURRENT_ROOT_RAW_PATH"]).read_text(encoding="utf-8")),
    "INDEPENDENT_REVIEW_VALIDATOR": json.loads(contained(os.environ["CVF_REFRESH_CURRENT_REVIEW_RAW_PATH"]).read_text(encoding="utf-8")),
}
current_projections = {name: surfaces[name](raw, matrix) for name, raw in current.items()}
assert current_projections["ROOT_EFFECTS_VALIDATOR"] == current_projections["INDEPENDENT_REVIEW_VALIDATOR"]
assert len(matches(current_projections["ROOT_EFFECTS_VALIDATOR"])) == 1
print("CVF_CORE_REFRESH_EVIDENCE_CONTRACT_PASS")
```

The reviewer extracts this block byte-exactly, compiles it, records its raw
SHA-256, and uses the same bytes for BUILD/REVIEW. Any source drift is a stop.
During the bounded rereview it independently freezes exactly one canonical
content-addressed corpus bundle between the runner's literal markers and its
raw digest as `CVF_CORPUS_BUNDLE_SHA256::<digest>` in the review artifact. The
bundle contains eight named positive cases, two independently collected surface
manifests per case, deduplicated base64 raw files, and raw-negative cases for
outcome injection, missing/empty trace or packet, command/exit/endpoint/target
mismatch, UUID/PID/SID reuse, direct-fetch substitution, traversal, candidate/
Core drift, missing prestate and zero/multiple/replayed review appends.

Expected outcome labels exist only in the bundle's outer positive-case index;
they are never passed to the adapter. BUILD decodes only those reviewed bytes,
verifies their review-owned digest, and materializes them only below the active
contained evidence tree. It may not regenerate the bundle or expectations from
the matrix or adapter. Both surfaces must derive byte-identical projections for
all eight positives; every raw negative must fail before projection.

## 11. Exact probes A–F

All probes are mandatory and fail closed:

- **A — `MATRIX_PIN_PROBE`:** recompute matrix canonical digest; require exact
  family id, eight outcome ids, registry path, SPEC declaration, Python pin and
  frozen adapter raw digest.
- **B — `RAW_EVIDENCE_PROJECTION_PROBE`:** both independently collected
  surfaces run the frozen adapter/runner on the same BUILD or REVIEW terminal
  event, derive byte-identical projections and match exactly one shape.
- **C — `REVIEW_PROJECTION_PROBE`:** for review terminals, scan actual pre/post
  completion/run/anchor trees, prior command bundles and current doctor raw
  evidence; require exact preservation plus one UUID/PID/SID-bound append.
- **D — `EIGHT_OUTCOME_CORPUS_PROBE`:** both surfaces accept all eight
  independently frozen positives, reject every matrix mutation by comparison
  with fresh raw derivation, and reject the frozen provenance-negative corpus.
  Runtime counts/digests are recorded, never copied expectations.
- **E — `RETAINED_SCOPE_PROBE`:** rerun the retained pin, incremental-scope,
  JSON, staged-zero, parent 17/12/10, P4-C, assessment-exclusion, session,
  knowledge, catalog, invariant-family, file-size, repository and diff guards.
- **F — `COMMAND_WRAPPER_PROBE`:** parse every outer transcript/exit/trace2/
  packet artifact; require exact owner command and argv, public endpoint and
  target observation, UUID/PID exact-SID join, full window/exit containment,
  allowed ordered prefix, global identity disjointness and derived zero direct-
  fetch substitution for rollback/review doctor owners.

Probe B supersedes the parent's old `ROOT_EFFECTS_PROBE`; Probe C supersedes
its old review-chain semantics. Probe E retains the unaffected parent gates.

## 12. Worker and reviewer returns

The worker may write only the parent's existing root-effects receipt and worker
return repository paths. Those artifacts reference raw contained evidence,
matrix/adapter/runner digests, the matched outcome/shape and A–F results. They
must not copy matrix rules. Worker return is
`READY_FOR_INDEPENDENT_COMPLETION_REVIEW` only on SUCCESS; every stopped or
failure outcome records its trigger, completes mandatory restoration/evidence,
and returns `STOPPED`.

The independent completion reviewer alone owns the parent's existing
completion-review path. It reruns A–F from raw evidence, adds exactly one
review run/anchor, and records the invariant-family proof fields: applicability,
matrix id/digest, raw positive sampled per outcome, mutation results for both
surfaces, findings, waivers and claim boundary.

## 13. Stop conditions

Stop before external effect on any pin/digest/baseline/containment mismatch,
dirty or moved Core, changed target/remote, missing preimage, assessment access,
adapter/runner drift, matrix ambiguity, missing outcome, surface disagreement,
trusted receipt assertion, undeclared path/root/network effect, credential
material, bare-fetch doctor substitution, PID/UUID/SID/window mismatch,
candidate loss, prior-review drift, staged content, failed restoration, failed
probe, or need for provider/install/database/deployment/commit/push authority.

At most one bounded repair/rereview cycle is authorized after the first
independent amendment review. A new root cause, expanded path/effect ceiling or
second residual cycle requires fresh operator direction.

## 14. Disposition and claim boundary

Disposition: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`.

The independent review is created only at
`docs/decisions/CVF_CORE_REFRESH_EVIDENCE_CONTRACT_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md`.
It freezes this amendment's raw digest, adapter raw digest, runner digest,
exact current non-assessment protected path set/LF digest and the byte-exact
base64 conformance bundle/digest. On rereview it may append only its disposition,
evidence and the one corpus marker block; it does not edit the parent,
amendment, adapter, matrix or SPEC.

This amendment does not grant BUILD. BUILD and reconciliation remain
unauthorized until an independent review passes this exact artifact and the
operator explicitly grants BUILD authority.

Later PASS proves only deterministic consistency among named local filesystem
checkpoints, outer command envelopes/Git trace surfaces and reviewer-observed
pre/post append state within the exact retained scope. It does not prove
continuous absence, kernel ancestry, WORM/external immutability, CVF control of
AI/agents, provider behavior, production readiness or deployment readiness.
