# Work Order — CVF Public-Core Refresh 2026-08-23

- Work order id: `CVF-CORE-REFRESH-WO-2026-08-23`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Execution base: `0b89016df8483a4904d2c64b1a6560ccbc6b27ae`
- Frozen Core target: `3b031fec35473e6ee6a554c4c72400e7a23b06c5`
- Parent SPEC: final `SPEC_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Invariant-family applicability: `NOT_APPLICABLE`
- BUILD authority: `NOT GRANTED`
- Provider/credential/dependency-or-package-install/database/deployment/commit/
  push authority: `0`
- Root-wrapper installer authority: only the reconciler-invoked refresh of the
  exact 17 workspace-root targets below; no dependency/package installation

## Objective

Restore workspace-doctor freshness through the sanctioned backup-and-reclone
flow, exact full downstream pins, ignored local-binding regeneration and
reviewable containment evidence, while preserving parked P4-C and every
unrelated dirty artifact.

## Exact downstream BUILD increment ceiling (12 paths)

1. `.cvf/manifest.json`
2. `AGENTS.md`
3. `knowledge/manifest.json`
4. `IMPLEMENTATION_STATUS.json`
5. `SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
7. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
8. `SESSION/SESSION_MEMORY.md`
9. `SESSION/handoffs/CVF_CORE_REFRESH_2026-08-23.md`
10. `docs/INDEX.md`
11. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json`
12. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md`

The first ten are mutable carriers; the last two are worker-created evidence.
The independent reviewer alone may later create
`docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-23.md`.

## Protected pre-Work-Order state

Before this Work Order existed, the dirty set excluding the assessment was
exactly 26 sorted paths. Its LF-terminated path-list SHA-256 is
`edcb7d6a85efeeb11937898d91f42be314b081883f6452b87235555d9f5820ce`.
No historical content digest is asserted: continuity changed after that path
snapshot and individual byte preimages were not retained. Immediately before
BUILD, the worker freezes the authoritative current per-path raw SHA-256
manifest and byte preimages: only the ten mutable
carriers may later differ, and only for this refresh. All P4-C and pre-BUILD
governance artifacts remain byte-exact; staged set stays empty.

The untracked operator assessment must never be opened, hashed, inventoried,
edited, staged or used as evidence.

## Exact workspace-root effect ceiling (17 paths)

`WORKSPACE_RULES.md`; `New-CVF-Governed-Project.ps1`;
`Run-CVF-NewProject-Enforcement.ps1`; `Update-CVF-Workspace.ps1`;
`Update-CVF-Workspace-Public-Profile.ps1`; `Test-CVF-Workspace.ps1`;
`Repair-CVF-Workspace.ps1`; `Manage-CVF-Workspace.ps1`;
`.agents/workflows/cvf-onboard.md`;
`.agents/workflows/pre-commit-check.md`; `CVF_WORKSPACE_USER_GUIDE.md`;
`CVF_WORKSPACE_HUONG_DAN_SU_DUNG.md`;
`CVF_WORKSPACE_CLASSIFICATION_GUIDE.md`;
`WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json`;
`Get-CVF-Workspace-OverlayProfiles.ps1`;
`Update-CVF-Workspace-Overlay.ps1`; `CVF_WORKSPACE_OVERLAY_STATUS.json`.

The first 14 currently exist; the three obsolete deletion candidates are
absent. Capture existence/hash/preimage for all 17 before action. No other root
path is authorized. Preserve all Core/root/downstream preimages and backups.

## Roles

- `IMPLEMENTATION_WORKER`: separate from authorization/completion reviewers;
  owns only the exact BUILD sequence and 12-path increment.
- `INDEPENDENT_COMPLETION_REVIEWER`: recomputes evidence and owns one doctor
  fetch plus the completion-review artifact.
- `REPAIR_WORKER`: acts only on accepted findings within retained ceiling.
- `COMMIT_STEWARD`: not authorized by this Work Order.

## G6 preflight and BUILD sequence

1. Rehydrate continuity and record BUILD acknowledgment in the active handoff.
2. Verify downstream base/remote equality, staged zero, clean Core at
   `7d9f360...`, exact public remote, fetched frozen target and `0/1` ancestry.
3. Reproduce the frozen 26-path pre-Work-Order path digest; freeze the exact
   current non-assessment dirty inventory and byte preimages for every entry;
   separately freeze byte preimages for all ten mutable carriers, including
   the four Git-clean carriers absent from the dirty inventory.
4. Resolve every Core/root/preimage/failed-delta path and prove containment
   within the exact workspace root before any move.
5. Create timestamped root/downstream preimage trees under
   `_cvf-core-backups`; capture all 17 root states and every current
   non-assessment dirty file plus all ten carrier preimages. The ten carriers
   are the only mutable subset and all ten must be restored on failure.
6. Run exactly:
   `powershell -ExecutionPolicy Bypass -File "<core>\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "<workspace-root>"`.
   No other flag is permitted.
7. Verify clone operation record, new Core remote/HEAD/origin/cleanliness,
   retained prior-Core backup and exact frozen target.
8. Patch only manifest full pin and AGENTS full header pin; update bounded
   maintenance truth and only invalidated knowledge source pins.
9. Run exactly `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`.
   This owns initializer fetch plus initializer-doctor fetch and regenerates
   ignored binding. Successful BUILD network sequence is exactly three ordered
   records: `RECONCILER_CLONE`, `INITIALIZER_FETCH`, `INITIALIZER_DOCTOR_FETCH`.
10. Synchronize the six continuity/index carriers, write root-effects JSON and
    worker return, then run every validator/gate below. Return only
    `READY_FOR_INDEPENDENT_COMPLETION_REVIEW`.

An early failure records only its executed 0..3 prefix. Rollback owns exactly
one conditional `ROLLBACK_VERIFIER` doctor fetch, total at most four; it never
becomes success evidence. Every operation uses only the exact public URL,
without credentials, and observes the frozen full target or triggers rollback.

Before step 6, record UTC `buildStart`, create a contained raw JSON anchor and
fresh worker trace pair, then set in one PowerShell process:
`GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=Never`, empty credential helper via
`GIT_CONFIG_COUNT/KEY_0/VALUE_0`, fresh UUID-v4 `CVF_TRACE_WINDOW_ID`,
`GIT_TRACE2_ENV_VARS=CVF_TRACE_WINDOW_ID`, `GIT_TRACE2_EVENT` and
`GIT_TRACE_PACKET`. The anchor binds UUID, time, current Work Order/review
hashes and preexisting failed-clone paths. Clone and both initializer fetches
inherit this environment; rollback uses a separate pair in the same window.

Each REVIEW/rereview creates its own process, UUID, anchor and trace pair before
one doctor. No owner inherits or reuses another pair/span/window. Each operation
binds exact trace2 `sid`, argv/start/exit, descendant packet `sid`/PID, complete
advertised main ref, window UUID `def_param`, raw hashes and span fingerprint.
The validator rejects extra clone/fetch sessions, replay, credentials, or any
raw start/exit outside the owner window. Target/zero-exit are success-only;
failure preserves the faithful exit/tip.

After the final owned Git operation, remove parent `GIT_TRACE2_EVENT` and
`GIT_TRACE_PACKET`, record UTC return, then hash/write/validate evidence. Each
reviewer does likewise after doctor. Python also clears both variables and
rehashes all raw evidence after its subprocesses.

## Machine receipt contract and validators

Root-effects JSON carries the fields enforced by `REQUIRED_RECEIPT` below.
Every dirty/root entry records path/status/existence/raw hash/preimage. A
separate exact-ten carrier manifest also captures the four initially clean
files. Success adds exactly those four plus two evidence paths; failure restores
all ten and retains evidence only in receipt/worker return. Only the receipt's
own inventory hash is `SELF`; every other hash is recomputed. Commands bind
invocation/window/PID, exact text/times/exit, derived network owners, JSON exit
record and PowerShell transcript. Network entries bind operation/window ids,
start/end/fingerprint, owner/URL, trace and packet paths/hashes/SIDs, argv/exit,
advertised tips and observed target exactly as the executable schema enforces.

The worker and reviewer run the SPEC-named validators with these frozen
predicates:

- `PIN_EQUALITY_PROBE`: exact remote, clean Core and full Core HEAD,
  `origin/main`, manifest pin, AGENTS header pin and ignored binding pin all
  equal target; binding is ignored; staged set empty.
- `ROOT_EFFECTS_PROBE`: parse receipt; exact 17 unique before/after root paths,
  12 unique increment paths, ten mutable carriers, contained/hash-matching Core,
  root and downstream preimages, recomputed current root state, validated exact
  commands, and either ordered success operations or a faithful failure prefix
  plus one rollback verifier.
- `INCREMENTAL_SCOPE_PROBE`: compare the receipt with actual porcelain-v1 `-z`
  status (excluding only the evidence-ineligible assessment); enforce exact
  unique start/return sets, recompute current/preimage hashes, preserve every
  nonmutable/P4-C byte, and prove the actual changed set is a subset of the 12
  path ceiling with exactly the two worker evidence paths added; staged zero.
- `JSON_PARSE_PROBE`: parse manifest, policy, knowledge, implementation status,
  canonical/mirror/bootstrap state and root-effects receipt.
- `REVIEW_OWNERSHIP_PROBE`: worker return exists, completion review absent at
  worker handoff, and reviewer alone creates its exact path.

The exact frozen arrays and executable validator body are below. Save neither
as a repository file; execute from project root after substituting only the
receipt path argument. Worker mode is the default. Expected output is exactly
`CORE_REFRESH_VALIDATORS_PASS`:

```powershell
$env:CVF_REFRESH_RECEIPT = (Resolve-Path 'docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json').Path
@'
import hashlib, json, os, pathlib, re, subprocess
from datetime import datetime, timezone
for _trace_var in ("GIT_TRACE2_EVENT", "GIT_TRACE_PACKET"):
    os.environ.pop(_trace_var, None)
ROOT = pathlib.Path.cwd()
WORKSPACE = ROOT.parent.resolve()
BACKUP_ROOT = (WORKSPACE / "_cvf-core-backups").resolve()
TARGET = "3b031fec35473e6ee6a554c4c72400e7a23b06c5"
CORE_BEFORE = "7d9f360a3df11ac998972728000785799399c02b"
RECONCILER_SHA256 = "96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c"
REMOTE = "https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git"
ASSESSMENT = "docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md"
PROTECTED_PATH_DIGEST = "edcb7d6a85efeeb11937898d91f42be314b081883f6452b87235555d9f5820ce"
PROTECTED = ["CVF_SESSION/ACTIVE_SESSION_STATE.json","docs/cvf/invariants/p4c-ingress-terminal-outcomes.json","docs/cvf/invariants/p4c-outbound-terminal-outcomes.json","docs/cvf/invariants/registry.json","docs/decisions/DESIGN_2026-08-23_CVF_CORE_REFRESH.md","docs/decisions/DESIGN_2026-08-23_P4C_INTEGRATION_EDGE.md","docs/decisions/DESIGN_REVIEW_2026-08-23_CVF_CORE_REFRESH.md","docs/decisions/INTAKE_2026-08-23_CVF_CORE_REFRESH.md","docs/decisions/INTAKE_2026-08-23_P4C_INTEGRATION_EDGE.md","docs/decisions/INTAKE_REVIEW_2026-08-23_CVF_CORE_REFRESH.md","docs/decisions/P4C_INTEGRATION_EDGE_DESIGN_REVIEW_2026-08-23.md","docs/decisions/P4C_INTEGRATION_EDGE_INTAKE_REVIEW_2026-08-23.md","docs/decisions/P4C_INTEGRATION_EDGE_SPEC_REVIEW_2026-08-23.md","docs/decisions/P4C_INTEGRATION_EDGE_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md","docs/decisions/SPEC_REVIEW_2026-08-23_CVF_CORE_REFRESH.md","docs/INDEX.md","docs/specs/CVF_CORE_REFRESH_2026-08-23_SPEC.md","docs/specs/P4C_INTEGRATION_EDGE_INVARIANT_REFERENCE.json","docs/specs/P4C_INTEGRATION_EDGE_SPEC.md","docs/specs/p4c_invariant_pins.py","docs/work_orders/P4C_INTEGRATION_EDGE_WORK_ORDER.md","SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json","SESSION/ACTIVE_SESSION_STATE.json","SESSION/handoffs/CVF_CORE_REFRESH_2026-08-23.md","SESSION/handoffs/P4C_INTEGRATION_EDGE_2026-08-23.md","SESSION/SESSION_MEMORY.md"]
WORK_ORDER_REL = "docs/work_orders/CVF_CORE_REFRESH_2026-08-23_WORK_ORDER.md"
AUTH_REVIEW_REL = "docs/decisions/AUTHORIZATION_REVIEW_2026-08-23_CVF_CORE_REFRESH.md"
ROOTS = ["WORKSPACE_RULES.md","New-CVF-Governed-Project.ps1","Run-CVF-NewProject-Enforcement.ps1","Update-CVF-Workspace.ps1","Update-CVF-Workspace-Public-Profile.ps1","Test-CVF-Workspace.ps1","Repair-CVF-Workspace.ps1","Manage-CVF-Workspace.ps1",".agents/workflows/cvf-onboard.md",".agents/workflows/pre-commit-check.md","CVF_WORKSPACE_USER_GUIDE.md","CVF_WORKSPACE_HUONG_DAN_SU_DUNG.md","CVF_WORKSPACE_CLASSIFICATION_GUIDE.md","WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json","Get-CVF-Workspace-OverlayProfiles.ps1","Update-CVF-Workspace-Overlay.ps1","CVF_WORKSPACE_OVERLAY_STATUS.json"]
CEILING = [".cvf/manifest.json","AGENTS.md","knowledge/manifest.json","IMPLEMENTATION_STATUS.json","SESSION/ACTIVE_SESSION_STATE.json","CVF_SESSION/ACTIVE_SESSION_STATE.json","SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json","SESSION/SESSION_MEMORY.md","SESSION/handoffs/CVF_CORE_REFRESH_2026-08-23.md","docs/INDEX.md","docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json","docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md"]
MUTABLE = CEILING[:10]
CLEAN_TO_MUTATE = MUTABLE[:4]
RECEIPT_REL = CEILING[10]
WORKER_RETURN = CEILING[11]
COMPLETION = "docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-23.md"
P4C = ["SESSION/handoffs/P4C_INTEGRATION_EDGE_2026-08-23.md","docs/work_orders/P4C_INTEGRATION_EDGE_WORK_ORDER.md","docs/decisions/P4C_INTEGRATION_EDGE_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md"]
receipt = json.loads(pathlib.Path(os.environ["CVF_REFRESH_RECEIPT"]).read_text(encoding="utf-8"))
REQUIRED_RECEIPT = {"schemaVersion","tranche","target","outcome","failureTrigger","timestamps","traceWindow","networkOperations","coreBefore","coreAfter","coreBackupPath","rootPreimagePath","downstreamPreimagePath","beforeRootTargets","afterRootTargets","buildStartInventory","buildReturnInventory","mutableCarrierPreimages","incrementCeiling","mutableCarriers","newlyDirtyCarriers","commands","rollback","stagedPaths"}
assert REQUIRED_RECEIPT <= set(receipt)
assert receipt["schemaVersion"] == "1.0" and receipt["tranche"] == "CVF-CORE-REFRESH-2026-08-23"
assert set(receipt["timestamps"]) == {"buildStart","buildReturn"}
MODE = os.environ.get("CVF_REFRESH_REVIEW_MODE", "WORKER")
assert MODE in {"WORKER", "REVIEW"}
HEX = re.compile(r"^[0-9a-f]{64}$")
def parse_time(value):
    assert isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value); return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)
BUILD_WINDOW = (parse_time(receipt["timestamps"]["buildStart"]), parse_time(receipt["timestamps"]["buildReturn"]))
assert BUILD_WINDOW[0] < BUILD_WINDOW[1]
def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def contained_path(path, must_exist=True):
    p = pathlib.Path(path).resolve(strict=must_exist); assert p.is_relative_to(BACKUP_ROOT)
    if must_exist: assert not p.is_symlink()
    return p
def contained(path): return contained_path(path, True)
def unique(entries, key="path"):
    values = [x[key] for x in entries]; assert len(values) == len(set(values)); return values
def inventory(entries): return {x["path"]: x for x in entries}
def current_sha(rel): return sha(ROOT / rel)
def parse_status():
    parts = subprocess.check_output(["git","status","--porcelain=v1","-z","--untracked-files=all"]).split(b"\0"); out = {}; i = 0
    while i < len(parts) and parts[i]:
        item = parts[i].decode("utf-8"); status, path = item[:2], item[3:]; assert "R" not in status and "C" not in status; out[path.replace("\\", "/")] = status; i += 1
    return out
def trace_events(path): return [json.loads(s) for line in contained(path).read_text(encoding="utf-8", errors="strict").splitlines() if (s := line.strip()).startswith("{")]
def assert_no_secret(text):
    low = text.lower(); assert "authorization:" not in low and "private-token" not in low and "password=" not in low and not re.search(r"https?://[^/\s:@]+:[^/\s@]+@", text, re.I)
RAW_EVIDENCE = {}
def validate_op(op, expected_owner, expected_window_id, allowed_trace_pairs):
    required = {"operationId","windowId","startedAt","endedAt","spanFingerprint","owner","url","trace2RawPath","trace2RawSha256","packetRawPath","packetRawSha256","traceSid","packetTraceSid","argv","exitCode","advertisedMainTips","observedTarget"}
    assert set(op) == required and op["owner"] == expected_owner and op["url"] == REMOTE and op["windowId"] == expected_window_id
    t2, pkt = contained(op["trace2RawPath"]), contained(op["packetRawPath"]); assert t2 != pkt and HEX.fullmatch(op["trace2RawSha256"]) and HEX.fullmatch(op["packetRawSha256"]); assert sha(t2) == op["trace2RawSha256"] and sha(pkt) == op["packetRawSha256"]
    for p, expected in ((t2, op["trace2RawSha256"]), (pkt, op["packetRawSha256"])):
        prior = RAW_EVIDENCE.setdefault(str(p), expected); assert prior == expected
    pair = (str(t2), str(pkt)); allowed_trace_pairs.add(pair); t2text, pkttext = t2.read_text(encoding="utf-8", errors="strict"), pkt.read_text(encoding="utf-8", errors="strict"); assert_no_secret(t2text); assert_no_secret(pkttext); events = trace_events(t2)
    defs = [e for e in events if e.get("event") == "def_param" and e.get("sid") == op["traceSid"] and e.get("param") == "CVF_TRACE_WINDOW_ID" and e.get("value") == expected_window_id]
    starts = [e for e in events if e.get("event") == "start" and e.get("sid") == op["traceSid"]]
    exits = [e for e in events if e.get("event") == "exit" and e.get("sid") == op["traceSid"]]
    assert defs and len(starts) == len(exits) == 1 and starts[0].get("argv") == op["argv"] and int(exits[0].get("code")) == int(op["exitCode"]); assert op["packetTraceSid"].startswith(op["traceSid"] + "/")
    packet_starts = [e for e in events if e.get("event") == "start" and e.get("sid") == op["packetTraceSid"]]
    assert len(packet_starts) == 1; pid_match = re.search(r"(?:^|/)P([0-9a-fA-F]+)(?:/|$)", op["packetTraceSid"]); assert pid_match; packet_pid = str(int(pid_match.group(1), 16))
    pid_lines = [line for line in pkttext.splitlines() if re.search(rf"(?<!\d){re.escape(packet_pid)}(?!\d)", line)]
    tips = sorted(set(re.findall(r"\b([0-9a-f]{40}) refs/heads/main\b", "\n".join(pid_lines)))); assert tips == op["advertisedMainTips"]; observed = tips[0] if len(tips) == 1 else None; assert op["observedTarget"] == observed
    argv = [str(v) for v in op["argv"]]
    if expected_owner == "RECONCILER_CLONE": assert "clone" in argv and REMOTE in argv
    else: assert "fetch" in argv and "origin" in argv and "main" in argv
    started, ended = starts[0].get("time"), exits[0].get("time"); assert isinstance(started, str) and re.match(r"^\d{4}-\d{2}-\d{2}T", started)
    assert op["startedAt"] == started and op["endedAt"] == ended and parse_time(started) <= parse_time(ended)
    span = {"traceSid":op["traceSid"],"packetTraceSid":op["packetTraceSid"],"argv":op["argv"],"exitCode":op["exitCode"],"advertisedMainTips":op["advertisedMainTips"],"startedAt":started,"endedAt":ended}
    computed_span = hashlib.sha256(json.dumps(span, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(); assert op["spanFingerprint"] == computed_span
    return events, started
def validate_operation_set(ops, owners, window, window_id, require_fresh_pairs=(), require_fresh_fingerprints=()):
    assert len(ops) == len(owners) and unique(ops, "operationId")
    assert len({x["traceSid"] for x in ops}) == len(ops)
    assert len({x["packetTraceSid"] for x in ops}) == len(ops)
    pairs, fingerprints, all_events, started = set(), set(), {}, []
    for op, owner in zip(ops, owners):
        events, start_time = validate_op(op, owner, window_id, pairs); started.append(start_time)
        fingerprints.add(op["spanFingerprint"])
        all_events.setdefault(str(contained(op["trace2RawPath"])), events)
    assert pairs.isdisjoint(set(require_fresh_pairs)) and fingerprints.isdisjoint(set(require_fresh_fingerprints))
    parsed_started = [parse_time(x) for x in started]
    assert parsed_started == sorted(parsed_started) and len(parsed_started) == len(set(parsed_started))
    assert all(window[0] <= x <= window[1] for x in parsed_started)
    recorded = {(str(contained(x["trace2RawPath"])), x["traceSid"]) for x in ops}
    actual = set()
    for path, events in all_events.items():
        for e in events:
            argv = [str(v) for v in e.get("argv", [])]
            if e.get("event") == "start": assert window[0] <= parse_time(e.get("time")) <= window[1]
            if e.get("event") == "exit": assert window[0] <= parse_time(e.get("time")) <= window[1]
            if e.get("event") == "start" and ("clone" in argv or "fetch" in argv): actual.add((path, e.get("sid")))
    assert actual == recorded
    return pairs, fingerprints
assert receipt["target"] == TARGET and receipt["outcome"] in {"SUCCESS","FAILURE"}
assert receipt["coreBefore"]["head"] == CORE_BEFORE and receipt["coreBefore"]["remote"] == REMOTE
assert receipt["coreAfter"]["remote"] == REMOTE
assert len(ROOTS) == len(set(ROOTS)) == 17 and len(CEILING) == len(set(CEILING)) == 12
assert CLEAN_TO_MUTATE == [".cvf/manifest.json","AGENTS.md","knowledge/manifest.json","IMPLEMENTATION_STATUS.json"]
assert len(PROTECTED) == len(set(PROTECTED)) == 26
assert hashlib.sha256("".join(p + "\n" for p in sorted(PROTECTED, key=str.casefold)).encode()).hexdigest() == PROTECTED_PATH_DIGEST
assert receipt["incrementCeiling"] == CEILING and receipt["mutableCarriers"] == MUTABLE
before_roots, after_roots = receipt["beforeRootTargets"], receipt["afterRootTargets"]
assert len(before_roots) == len(after_roots) == 17
assert unique(before_roots) == ROOTS and unique(after_roots) == ROOTS
root_preimage_tree = contained(receipt["rootPreimagePath"])
downstream_preimage_tree = contained(receipt["downstreamPreimagePath"])
assert len({x["preimagePath"] for x in before_roots if x["preimagePath"]}) == sum(1 for x in before_roots if x["preimagePath"])
for before, after in zip(before_roots, after_roots):
    assert before["path"] == after["path"]
    target_path = WORKSPACE / after["path"]
    assert after["exists"] == target_path.is_file()
    assert after["sha256"] == (sha(target_path) if target_path.is_file() else None)
    if before["exists"]:
        pre = contained(before["preimagePath"]); assert pre.is_relative_to(root_preimage_tree)
        assert HEX.fullmatch(before["sha256"]) and sha(pre) == before["sha256"]
    else: assert before["sha256"] is None and before["preimagePath"] is None
for field in ("rootPreimagePath","downstreamPreimagePath"): contained(receipt[field])
if receipt["outcome"] == "SUCCESS":
    core_backup = contained(receipt["coreBackupPath"])
    assert subprocess.check_output(["git","-C",str(core_backup),"rev-parse","HEAD"], text=True).strip() == receipt["coreBefore"]["head"]
    assert subprocess.check_output(["git","-C",str(core_backup),"remote","get-url","origin"], text=True).strip() == REMOTE
    assert subprocess.check_output(["git","-C",str(core_backup),"status","--porcelain"], text=True).strip() == ""
else:
    core_backup = contained_path(receipt["coreBackupPath"], False)
    assert not core_backup.exists()
start_entries, end_entries = receipt["buildStartInventory"], receipt["buildReturnInventory"]
start_paths, end_paths = unique(start_entries), unique(end_entries)
assert ASSESSMENT not in start_paths and ASSESSMENT not in end_paths
assert set(start_paths) == set(PROTECTED) | {WORK_ORDER_REL, AUTH_REVIEW_REL}
newly_dirty = receipt["newlyDirtyCarriers"]
assert len(newly_dirty) == len(set(newly_dirty)) and set(newly_dirty) <= set(CLEAN_TO_MUTATE)
assert set(end_paths) == set(start_paths) | set(newly_dirty) | {RECEIPT_REL, WORKER_RETURN}
start, end = inventory(start_entries), inventory(end_entries)
assert len({x["preimagePath"] for x in start_entries}) == len(start_entries)
for p, item in start.items():
    assert HEX.fullmatch(item["sha256"])
    pre = contained(item["preimagePath"]); assert pre.is_relative_to(downstream_preimage_tree)
    assert sha(pre) == item["sha256"]
trace_window = receipt["traceWindow"]
assert set(trace_window) == {"windowId","anchorPath","anchorSha256","reviewAnchorDirectory"}
assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", trace_window["windowId"])
anchor_path = contained(trace_window["anchorPath"])
assert HEX.fullmatch(trace_window["anchorSha256"]) and sha(anchor_path) == trace_window["anchorSha256"]
anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
assert set(anchor) == {"windowId","createdAt","workOrderSha256","authorizationReviewSha256","preexistingFailedReplacementPaths"}
assert anchor["windowId"] == trace_window["windowId"] and anchor["createdAt"] == receipt["timestamps"]["buildStart"]
assert anchor["workOrderSha256"] == start[WORK_ORDER_REL]["sha256"] and anchor["authorizationReviewSha256"] == start[AUTH_REVIEW_REL]["sha256"]
assert len(anchor["preexistingFailedReplacementPaths"]) == len(set(anchor["preexistingFailedReplacementPaths"]))
for p in anchor["preexistingFailedReplacementPaths"]: contained(p)
review_anchor_dir = contained(trace_window["reviewAnchorDirectory"])
assert review_anchor_dir.is_dir()
current_failed_candidates = {str(p.resolve()) for p in BACKUP_ROOT.glob(".Controlled-Vibe-Framework-CVF-failed-*") if p.is_dir()}
new_failed_candidates = current_failed_candidates - set(anchor["preexistingFailedReplacementPaths"])
carrier_entries = receipt["mutableCarrierPreimages"]
assert unique(carrier_entries) == MUTABLE
carrier_preimages = inventory(carrier_entries)
assert len({x["preimagePath"] for x in carrier_entries}) == 10
for p, item in carrier_preimages.items():
    assert HEX.fullmatch(item["sha256"])
    pre = contained(item["preimagePath"]); assert pre.is_relative_to(downstream_preimage_tree)
    assert sha(pre) == item["sha256"]
    if p in start: assert item["sha256"] == start[p]["sha256"]
    else:
        assert p in CLEAN_TO_MUTATE
        assert item["sha256"] == hashlib.sha256(subprocess.check_output(["git","show",f"HEAD:{p}"])).hexdigest()
actual_status = parse_status()
actual_status.pop(ASSESSMENT, None)
if MODE == "REVIEW": assert actual_status.pop(COMPLETION, None) in {"??", " M", "M "}
assert actual_status == {p: x["status"] for p, x in end.items()}
for p, item in end.items():
    if p == RECEIPT_REL: assert item["sha256"] == "SELF" and (ROOT / p).is_file()
    else: assert HEX.fullmatch(item["sha256"]) and current_sha(p) == item["sha256"]
for p in set(start) - set(MUTABLE): assert end[p]["sha256"] == start[p]["sha256"]
for p in P4C: assert p in start and end[p]["sha256"] == start[p]["sha256"]
changed = {p for p in start if start[p]["sha256"] != end[p]["sha256"]} | (set(end) - set(start))
assert changed <= set(CEILING) and {RECEIPT_REL, WORKER_RETURN} <= changed
assert receipt["stagedPaths"] == []
assert subprocess.check_output(["git","diff","--cached","--name-only"], text=True).strip() == ""
command_owners = [x["owner"] for x in receipt["commands"]]
assert len(command_owners) == len(set(command_owners))
COMMAND_KEYS = {"invocationId","windowId","processId","owner","text","startedAt","completedAt","exitCode","networkOwners","exitEvidencePath","exitEvidenceSha256","transcriptRawPath","transcriptRawSha256"}
assert all(set(x) == COMMAND_KEYS and isinstance(x["exitCode"], int) for x in receipt["commands"])
assert len({x["invocationId"] for x in receipt["commands"]}) == len(receipt["commands"])
for command in receipt["commands"]:
    assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", command["invocationId"])
    assert command["windowId"] == trace_window["windowId"]
    assert isinstance(command["processId"], int) and command["processId"] > 0
    command_window = (parse_time(command["startedAt"]), parse_time(command["completedAt"]))
    assert BUILD_WINDOW[0] <= command_window[0] < command_window[1] <= BUILD_WINDOW[1]
    evidence_path = contained(command["exitEvidencePath"])
    assert HEX.fullmatch(command["exitEvidenceSha256"]) and sha(evidence_path) == command["exitEvidenceSha256"]
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence == {"invocationId":command["invocationId"],"windowId":command["windowId"],"owner":command["owner"],"startedAt":command["startedAt"],"completedAt":command["completedAt"],"exitCode":command["exitCode"],"commandSha256":hashlib.sha256(command["text"].encode("utf-8")).hexdigest()}
    transcript_path = contained(command["transcriptRawPath"])
    assert HEX.fullmatch(command["transcriptRawSha256"]) and sha(transcript_path) == command["transcriptRawSha256"]
    transcript = transcript_path.read_text(encoding="utf-8", errors="strict"); assert_no_secret(transcript)
    command_sha = hashlib.sha256(command["text"].encode("utf-8")).hexdigest()
    start_marker = f'CVF_COMMAND_START::{command["windowId"]}::{command["invocationId"]}::{command["owner"]}::{command["startedAt"]}::{command["processId"]}::{command_sha}'
    exit_marker = f'CVF_COMMAND_EXIT::{command["windowId"]}::{command["invocationId"]}::{command["owner"]}::{command["completedAt"]}::{command["processId"]}::{command["exitCode"]}'
    assert transcript.count(start_marker) == transcript.count(exit_marker) == 1 and command["text"] in transcript
expected_commands = ["RECONCILER","INITIALIZER"]
if receipt["outcome"] == "SUCCESS": assert command_owners == expected_commands and all(x["exitCode"] == 0 for x in receipt["commands"])
else:
    assert command_owners == expected_commands[:len(command_owners)] and receipt["failureTrigger"]
    bad_commands = [i for i, x in enumerate(receipt["commands"]) if x["exitCode"] != 0]
    assert not bad_commands or bad_commands == [len(receipt["commands"]) - 1]
binding_now = json.loads((ROOT/".cvf/local-binding.json").read_text(encoding="utf-8-sig"))
core = pathlib.Path(binding_now["cvfCorePath"])
expected_reconciler = f'powershell -ExecutionPolicy Bypass -File "{core}\\scripts\\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "{WORKSPACE}"'
for command in receipt["commands"]:
    text = command["text"]
    if command["owner"] == "RECONCILER": assert text.casefold() == expected_reconciler.casefold()
    if command["owner"] == "INITIALIZER": assert text == "powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1"
ops = receipt["networkOperations"]
names = [x["owner"] for x in ops]
success = ["RECONCILER_CLONE","INITIALIZER_FETCH","INITIALIZER_DOCTOR_FETCH"]
if receipt["outcome"] == "SUCCESS":
    assert newly_dirty == CLEAN_TO_MUTATE
    assert names == success and all(x["exitCode"] == 0 and x["observedTarget"] == TARGET for x in ops)
else:
    assert names and names[-1] == "ROLLBACK_VERIFIER" and names[:-1] == success[:len(names)-1] and len(names) <= 4
    prefix = ops[:-1]
    bad = [i for i, x in enumerate(prefix) if x["exitCode"] != 0 or x["observedTarget"] != TARGET]
    assert not bad or bad == [len(prefix) - 1]
    rollback = receipt["rollback"]
    assert rollback["attempted"] is True and rollback["trigger"] == receipt["failureTrigger"]
    failed_delta = contained(rollback["failedRootDeltaPath"])
    delta_actual = {str(p.relative_to(failed_delta)).replace("\\", "/"): sha(p) for p in failed_delta.rglob("*") if p.is_file()}
    delta_receipt = {x["path"]: x["sha256"] for x in rollback["failedRootDeltaInventory"]}
    assert len(delta_receipt) == len(rollback["failedRootDeltaInventory"]) and delta_actual == delta_receipt
    replacement = rollback["replacementCorePreservedPath"]
    clone_op = next((x for x in ops[:-1] if x["owner"] == "RECONCILER_CLONE"), None)
    stamp_match = re.fullmatch(r"\.Controlled-Vibe-Framework-CVF-(\d{8}-\d{6})", core_backup.name)
    assert stamp_match
    derived_failed = contained_path(core_backup.parent / f".Controlled-Vibe-Framework-CVF-failed-{stamp_match.group(1)}", False)
    if clone_op and clone_op["exitCode"] == 0:
        assert replacement and pathlib.Path(replacement).resolve() == derived_failed
        assert new_failed_candidates == {str(derived_failed)} and rollback["replacementDisposition"] == "PRESERVED_COMPLETE"
    elif clone_op:
        if derived_failed.exists():
            assert replacement and pathlib.Path(replacement).resolve() == derived_failed
            assert new_failed_candidates == {str(derived_failed)} and rollback["replacementDisposition"] == "PRESERVED_PARTIAL"
        else:
            assert replacement is None and not new_failed_candidates and rollback["replacementDisposition"] == "NOT_CREATED"
    else:
        assert replacement is None and not new_failed_candidates and rollback["replacementDisposition"] == "NOT_CREATED"
    if replacement:
        replacement = contained(replacement)
        replacement_actual = {str(p.relative_to(replacement)).replace("\\", "/"): sha(p) for p in replacement.rglob("*") if p.is_file()}
        replacement_receipt = {x["path"]: x["sha256"] for x in rollback["replacementCoreInventory"]}
        assert len(replacement_receipt) == len(rollback["replacementCoreInventory"]) and replacement_actual == replacement_receipt
        head_probe = subprocess.run(["git","-C",str(replacement),"rev-parse","HEAD"], text=True, capture_output=True)
        if head_probe.returncode == 0:
            assert head_probe.stdout.strip() == rollback["replacementCoreHead"]
            if clone_op and clone_op["exitCode"] == 0: assert rollback["replacementCoreHead"] == clone_op["observedTarget"]
        else: assert rollback["replacementCoreHead"] is None
    else:
        assert rollback["replacementCoreHead"] is None and rollback["replacementCoreInventory"] == []
    assert rollback["restoredRootTargets"] == ROOTS
    assert rollback["verifierExitCode"] == ops[-1]["exitCode"]
build_pairs, build_fingerprints = validate_operation_set(ops, names, BUILD_WINDOW, trace_window["windowId"])
network_prefix = names if receipt["outcome"] == "SUCCESS" else names[:-1]
expected_network_owners = {
    "RECONCILER": [x for x in network_prefix if x == "RECONCILER_CLONE"],
    "INITIALIZER": [x for x in network_prefix if x.startswith("INITIALIZER_")],
}
for command in receipt["commands"]: assert command["networkOwners"] == expected_network_owners[command["owner"]]
op_by_owner = {x["owner"]: x for x in ops}
for command in receipt["commands"]:
    owned_ops = [op_by_owner[x] for x in command["networkOwners"]]
    assert all(parse_time(command["startedAt"]) <= parse_time(x["startedAt"]) <= parse_time(x["endedAt"]) <= parse_time(command["completedAt"]) for x in owned_ops)
    if any(x["exitCode"] != 0 for x in owned_ops): assert command["exitCode"] != 0
    if command["exitCode"] == 0: assert all(x["exitCode"] == 0 for x in owned_ops)
if "RECONCILER_CLONE" in network_prefix: assert "RECONCILER" in command_owners
if any(x.startswith("INITIALIZER_") for x in network_prefix):
    assert command_owners == ["RECONCILER","INITIALIZER"]
    assert receipt["commands"][0]["exitCode"] == 0
clone_op = next((x for x in ops if x["owner"] == "RECONCILER_CLONE"), None)
if clone_op and clone_op["exitCode"] != 0:
    assert command_owners == ["RECONCILER"] and receipt["commands"][0]["exitCode"] != 0
if receipt["outcome"] == "FAILURE" and len(ops) > 1:
    rollback_pair = (str(contained(ops[-1]["trace2RawPath"])), str(contained(ops[-1]["packetRawPath"])))
    assert all(rollback_pair != (str(contained(x["trace2RawPath"])), str(contained(x["packetRawPath"]))) for x in ops[:-1])
def git(*a): return subprocess.check_output(["git","-C",str(core),*a], text=True).strip()
manifest = json.loads((ROOT/".cvf/manifest.json").read_text(encoding="utf-8"))
binding = json.loads((ROOT/".cvf/local-binding.json").read_text(encoding="utf-8-sig"))
assert sha(core / "scripts" / "update_cvf_workspace_public_core.ps1") == RECONCILER_SHA256
header = re.search(r"CVF Commit: ([0-9a-f]{40})", (ROOT/"AGENTS.md").read_text(encoding="utf-8")).group(1)
assert git("remote","get-url","origin") == REMOTE
assert git("status","--porcelain") == ""
assert subprocess.run(["git","check-ignore","-q",".cvf/local-binding.json"]).returncode == 0
if receipt["outcome"] == "SUCCESS":
    assert git("rev-parse","HEAD") == git("rev-parse","origin/main") == manifest["cvfCoreCommit"] == binding["resolvedCoreCommit"] == header == TARGET
    assert receipt["coreAfter"]["head"] == receipt["coreAfter"]["originMain"] == TARGET
    assert receipt["rollback"]["attempted"] is False
    assert not new_failed_candidates
    assert set(MUTABLE) <= changed
else:
    assert git("rev-parse","HEAD") == receipt["coreBefore"]["head"]
    assert receipt["coreAfter"]["head"] == receipt["coreBefore"]["head"]
    for before, after in zip(before_roots, after_roots): assert (before["exists"], before["sha256"]) == (after["exists"], after["sha256"])
    assert receipt.get("failureEvidenceCarriers", []) == [] and newly_dirty == []
    assert changed == {RECEIPT_REL, WORKER_RETURN}
    for p in MUTABLE:
        assert current_sha(p) == carrier_preimages[p]["sha256"]
        if p in start: assert end[p]["sha256"] == start[p]["sha256"]
        else: assert p not in end
for p in [".cvf/manifest.json",".cvf/policy.json","knowledge/manifest.json","IMPLEMENTATION_STATUS.json","SESSION/ACTIVE_SESSION_STATE.json","CVF_SESSION/ACTIVE_SESSION_STATE.json","SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json",os.environ["CVF_REFRESH_RECEIPT"]]: json.loads(pathlib.Path(p).read_text(encoding="utf-8-sig"))
worker_text = (ROOT / WORKER_RETURN).read_text(encoding="utf-8")
assert "IMPLEMENTATION_WORKER" in worker_text
if MODE == "WORKER":
    assert not (ROOT / COMPLETION).exists()
    assert not any(p.is_file() for p in review_anchor_dir.rglob("*"))
else:
    completion = (ROOT / COMPLETION).read_text(encoding="utf-8")
    assert "INDEPENDENT_COMPLETION_REVIEWER" in completion
    begin, finish = "<!-- CVF_REVIEW_RECEIPT_BEGIN -->", "<!-- CVF_REVIEW_RECEIPT_END -->"
    assert completion.count(begin) == completion.count(finish) == 1
    review_receipt = json.loads(completion.split(begin, 1)[1].split(finish, 1)[0].strip())
    assert set(review_receipt) == {"authorRole","reviewRuns"}
    assert review_receipt["authorRole"] == "INDEPENDENT_COMPLETION_REVIEWER"
    runs = review_receipt["reviewRuns"]
    assert runs and len({x["reviewRunId"] for x in runs}) == len(runs) and len({x["windowId"] for x in runs}) == len(runs)
    assert trace_window["windowId"] not in {x["windowId"] for x in runs}
    run_anchor_paths = {str(contained(x["anchorPath"])) for x in runs}
    actual_review_anchor_paths = {str(p.resolve()) for p in review_anchor_dir.rglob("*") if p.is_file()}
    assert run_anchor_paths == actual_review_anchor_paths
    prior_pairs, prior_fingerprints = set(), set()
    prior_ids, prior_return = {x["operationId"] for x in ops}, BUILD_WINDOW[1]
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    for index, run in enumerate(runs):
        assert set(run) == {"reviewRunId","windowId","authorRole","reviewStart","reviewReturn","priorReviewRunsSha256","anchorPath","anchorSha256","networkOperation"}
        assert run["authorRole"] == "INDEPENDENT_COMPLETION_REVIEWER"
        assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", run["windowId"])
        expected_prior = hashlib.sha256(canonical(runs[:index])).hexdigest()
        assert run["priorReviewRunsSha256"] == expected_prior
        window = (parse_time(run["reviewStart"]), parse_time(run["reviewReturn"]))
        assert prior_return < window[0] < window[1]
        review_anchor_path = contained(run["anchorPath"])
        assert HEX.fullmatch(run["anchorSha256"]) and sha(review_anchor_path) == run["anchorSha256"]
        review_anchor = json.loads(review_anchor_path.read_text(encoding="utf-8"))
        assert review_anchor == {"reviewRunId":run["reviewRunId"],"windowId":run["windowId"],"createdAt":run["reviewStart"],"priorReviewRunsSha256":expected_prior,"workOrderSha256":start[WORK_ORDER_REL]["sha256"]}
        review_op = run["networkOperation"]
        assert review_op["owner"] == "REVIEWER_DOCTOR" and review_op["exitCode"] == 0 and review_op["observedTarget"] == TARGET
        assert review_op["operationId"] not in prior_ids
        run_pairs, run_fingerprints = validate_operation_set([review_op], ["REVIEWER_DOCTOR"], window, run["windowId"], build_pairs | prior_pairs, build_fingerprints | prior_fingerprints)
        prior_pairs |= run_pairs; prior_fingerprints |= run_fingerprints
        prior_ids.add(review_op["operationId"]); prior_return = window[1]
for raw_path, expected_hash in RAW_EVIDENCE.items(): assert sha(raw_path) == expected_hash
print("CORE_REFRESH_VALIDATORS_PASS")
'@ | python -
if ($LASTEXITCODE -ne 0) { throw 'Core refresh validators failed' }
```

At each independent REVIEW/rereview, preserve the existing marker payload,
append exactly one new item to its `reviewRuns` array, create a fresh reviewer
trace pair, set
the five prompt/credential variables and the two trace variables in that
reviewer's new process, run exactly one doctor, and embed its complete operation
object plus `"authorRole":"INDEPENDENT_COMPLETION_REVIEWER"` between literal
`<!-- CVF_REVIEW_RECEIPT_BEGIN -->` / `<!-- CVF_REVIEW_RECEIPT_END -->` markers
in the reviewer-owned completion artifact. Each run records unique
`reviewRunId`, `authorRole`, `reviewStart`, `reviewReturn` and one complete
`networkOperation`, plus a fresh UUID-v4 `windowId`, contained/hash-bound raw
window anchor and SHA-256 of the canonical prior `reviewRuns` array. The anchor
binds that prior digest and the BUILD-start Work Order hash; the trace carries
the UUID through `GIT_TRACE2_ENV_VARS`. Windows are UTC, strictly
non-overlapping, later than BUILD return and bind every raw trace start event.
Set
`CVF_REFRESH_REVIEW_MODE=REVIEW` and rerun the same body. Review mode proves the
completion author role, parses its raw trace separately, rejects reuse of any
BUILD trace pair, and leaves every other predicate identical.

Repository commands: session state, project knowledge, catalog `--check`, file
size, invariant-family JSON guard, repository validator, JSON parse and
`git diff --check`. Initializer-owned doctor is the success doctor. Independent
REVIEW reruns the doctor once and records its separately owned fetch.

## Mandatory rollback

On any post-start failure: containment-check all named paths; move/preserve the
replacement Core; restore prior Core; hash-restore existing root targets;
move newly created root targets to a preserved failed-root-delta tree; restore
all ten mutable downstream carriers byte-exactly from their independent
preimages; retain failure evidence only in the root-effects receipt and worker
return; delete nothing; run/record the single conditional rollback doctor;
record trigger/moves/hashes/final state and stop. Failure must still satisfy
SPEC AC-05's always-applicable R1-R5, R7-R12 and R14-R17 boundaries.

## Stop conditions

Stop on source/remote/target movement, dirty Core, baseline/hash mismatch,
path 13 or root target 18, sibling-manifest change, assessment access,
undeclared network/credential/root effect, missing backup, failed validator,
staged content, rollback failure, provider/product/install/database/deployment
need, third same-root repair round, or need for commit/push authority. The
authorized root-wrapper refresh is not a dependency/package install.

## Disposition

`READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`. BUILD and reconciliation remain
unauthorized until independent `AUTHORIZATION_REVIEW_PASS` and explicit BUILD
authority are both recorded.
