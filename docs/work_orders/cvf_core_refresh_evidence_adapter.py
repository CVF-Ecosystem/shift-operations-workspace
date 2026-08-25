"""Read-only raw-evidence adapter for the CVF Core refresh evidence contract."""
from __future__ import annotations

import hashlib, json, os, pathlib, re, subprocess
from datetime import datetime

UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
HEX40, HEX64 = re.compile(r"^[0-9a-f]{40}$"), re.compile(r"^[0-9a-f]{64}$")
REMOTE = "https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git"
TARGET, PROJECT = "3b031fec35473e6ee6a554c4c72400e7a23b06c5", "shift-operations-workspace"
PREFIX = ("RECONCILER_CLONE", "INITIALIZER_FETCH", "INITIALIZER_DOCTOR_FETCH")
OWNERS = {*PREFIX, "ROLLBACK_VERIFIER", "REVIEWER_DOCTOR"}
COMMAND_KEYS = {"owner", "invocationId", "processId", "normalizedCommand", "startedAt", "completedAt", "transcript", "trace2", "exitRecord", "networkOwners"}
OP_KEYS = {"owner", "url", "invocationId", "outerProcessId", "packetProcessId", "sid", "packetSid", "startedAt", "completedAt", "exitCode", "packetTrace"}
EXIT_KEYS = {"owner", "invocationId", "processId", "normalizedCommand", "startedAt", "completedAt", "exitCode", "transcriptSha256", "trace2Sha256", "packetTraceSha256"}
TRANSCRIPT_KEYS = {"owner", "invocationId", "processId", "normalizedCommand", "startedAt", "completedAt", "exitCode"}
BASE_KEYS = {"surface", "buildPriorCandidates", "finalPriorCandidates", "commands", "rollbackCommand", "networkOperations"}
BUILD_KEYS = BASE_KEYS | {"checkpointCandidates", "finalCheckpointCandidates", "checkpointCoreRepository", "finalCheckpointCoreRepository"}
REVIEW_KEYS = {"surface", "reviewCommand", "networkOperations", "priorCommandBundles", "priorReviewState", "finalReviewState"}

def _canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def _sha(data: bytes): return hashlib.sha256(data).hexdigest()
def _time(value):
    assert isinstance(value, str)
    result = datetime.fromisoformat(value.replace("Z", "+00:00")); assert result.tzinfo is not None
    return result

def _layout():
    raw = pathlib.Path(os.environ["CVF_REFRESH_EVIDENCE_ROOT"]); assert not raw.is_symlink()
    evidence = raw.resolve(strict=True); assert evidence.is_dir() and evidence.parent.name == "_cvf-core-backups" and not evidence.parent.is_symlink()
    workspace = evidence.parent.parent.resolve(strict=True); project = (workspace / PROJECT).resolve(strict=True); core = (workspace / ".Controlled-Vibe-Framework-CVF").resolve(strict=True)
    assert project.parent == workspace == core.parent and (workspace / "WORKSPACE_RULES.md").is_file() and (project / "AGENTS.md").is_file()
    return evidence, workspace, project, core

def _contained(value, kind):
    evidence, _, _, _ = _layout(); raw = pathlib.Path(value); assert raw.is_absolute() and not raw.is_symlink()
    path = raw.resolve(strict=True); assert path.is_relative_to(evidence)
    assert (kind == "file" and path.is_file()) or (kind == "dir" and path.is_dir())
    cursor = path
    while cursor != evidence: assert not cursor.is_symlink(); cursor = cursor.parent
    return path

def _file(desc):
    assert isinstance(desc, dict) and set(desc) == {"path", "sha256"} and HEX64.fullmatch(desc["sha256"])
    path = _contained(desc["path"], "file"); assert _sha(path.read_bytes()) == desc["sha256"]
    return path

def _tree_rows(root):
    rows = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        assert not path.is_symlink(); relative = path.relative_to(root).as_posix()
        if path.is_dir():
            children = sorted((child.name, "DIRECTORY" if child.is_dir() else "FILE") for child in path.iterdir())
            rows.append({"path": relative, "type": "DIRECTORY", "size": 0, "sha256": _sha(_canonical(children).encode())})
        else:
            assert path.is_file(); data = path.read_bytes()
            rows.append({"path": relative, "type": "FILE", "size": len(data), "sha256": _sha(data)})
    return rows

def _directory(desc):
    assert isinstance(desc, dict) and set(desc) == {"path", "treeSha256"} and HEX64.fullmatch(desc["treeSha256"])
    path = _contained(desc["path"], "dir"); assert _sha(_canonical(_tree_rows(path)).encode()) == desc["treeSha256"]
    return path

def _json(desc): return json.loads(_file(desc).read_text(encoding="utf-8"))
def _jsonl(desc):
    result = []
    for line in _file(desc).read_text(encoding="utf-8").splitlines():
        if line.strip(): item = json.loads(line); assert isinstance(item, dict); result.append(item)
    return result
def _inventory(desc): return _canonical(_tree_rows(_directory(desc)))

def _shapes(matrix):
    assert isinstance(matrix, dict) and isinstance(matrix.get("outcomes"), list); result, labels = [], set()
    for outcome in matrix["outcomes"]:
        assert set(outcome) >= {"outcomeId", "shapes"} and len(outcome["shapes"]) == 1
        shape = outcome["shapes"][0]; assert shape["fieldDomains"]["outcome"]["const"] == outcome["outcomeId"] and outcome["outcomeId"] not in labels
        labels.add(outcome["outcomeId"]); result.append(shape)
    assert len(result) == 8
    return result

def _shape(matrix, **constants):
    found = [shape for shape in _shapes(matrix) if all(shape["fieldDomains"].get(field, {}).get("const") == value for field, value in constants.items())]
    assert len(found) == 1
    return found[0]
def _const(shape, field): assert "const" in shape["fieldDomains"][field]; return shape["fieldDomains"][field]["const"]

def _commands():
    _, workspace, project, core = _layout()
    doctor = f'powershell -ExecutionPolicy Bypass -File "{core}\\scripts\\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "{project}"'
    return {"RECONCILER": f'powershell -ExecutionPolicy Bypass -File "{core}\\scripts\\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "{workspace}"', "INITIALIZER": "powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1", "ROLLBACK_VERIFIER": doctor, "REVIEWER_DOCTOR": doctor}

def _argv(owner):
    _, _, _, core = _layout()
    return ["git", "-c", "core.longpaths=true", "clone", REMOTE, str(core)] if owner == PREFIX[0] else ["git", "-C", str(core), "fetch", "origin", "main", "--quiet"]

def _params(events, sid):
    found = {}
    for event in events:
        if event.get("sid") == sid and event.get("event") == "def_param":
            key = event.get("param") or event.get("key")
            if key in {"CVF_OUTER_INVOCATION_UUID", "CVF_OUTER_POWERSHELL_PID"}: assert key not in found; found[key] = str(event.get("value"))
    return found

def _operation_rows(raw):
    assert isinstance(raw, list); result = []
    for item in raw:
        assert isinstance(item, dict) and set(item) == OP_KEYS and item["owner"] in OWNERS
        assert isinstance(item["invocationId"], str) and UUID4.fullmatch(item["invocationId"])
        assert all(isinstance(item[key], int) and item[key] > 0 for key in ("outerProcessId", "packetProcessId")) and item["outerProcessId"] != item["packetProcessId"]
        assert item["url"] == REMOTE and isinstance(item["sid"], str) and item["sid"] and isinstance(item["packetSid"], str) and item["packetSid"].startswith(item["sid"] + "/")
        pid_match = re.search(r"(?:^|/)P([0-9a-fA-F]+)(?:/|$)", item["packetSid"]); assert pid_match and int(pid_match.group(1), 16) == item["packetProcessId"]
        assert isinstance(item["exitCode"], int) and _time(item["startedAt"]) < _time(item["completedAt"])
        result.append(item)
    assert len({item["owner"] for item in result}) == len(result) and len({item["packetSid"] for item in result}) == len(result)
    return result

def _command(raw, operations, owner=None):
    assert isinstance(raw, dict) and set(raw) == COMMAND_KEYS
    actual, invocation, pid = raw["owner"], raw["invocationId"], raw["processId"]
    assert actual in _commands() and (owner is None or actual == owner) and isinstance(invocation, str) and UUID4.fullmatch(invocation) and isinstance(pid, int) and pid > 0
    start, end, exact = _time(raw["startedAt"]), _time(raw["completedAt"]), _commands()[actual]
    assert start < end and raw["normalizedCommand"] == exact and isinstance(raw["networkOwners"], list) and len(raw["networkOwners"]) == len(set(raw["networkOwners"]))
    transcript_path = _file(raw["transcript"]); transcript = json.loads(transcript_path.read_text(encoding="utf-8")); exit_record = _json(raw["exitRecord"])
    assert set(transcript) == TRANSCRIPT_KEYS and set(exit_record) == EXIT_KEYS
    for document in (transcript, exit_record):
        assert document["owner"] == actual and document["invocationId"] == invocation and document["processId"] == pid and document["normalizedCommand"] == exact
        assert document["startedAt"] == raw["startedAt"] and document["completedAt"] == raw["completedAt"] and isinstance(document["exitCode"], int)
    trace_path = _file(raw["trace2"]); assert transcript["exitCode"] == exit_record["exitCode"] and exit_record["transcriptSha256"] == _sha(transcript_path.read_bytes()) and exit_record["trace2Sha256"] == _sha(trace_path.read_bytes())
    owned = [item for item in operations if item["owner"] in raw["networkOwners"]]; assert [item["owner"] for item in owned] == raw["networkOwners"]
    events = _jsonl(raw["trace2"]); expected_sids = {item["sid"] for item in owned}; event_sids = {item.get("sid") for item in events if item.get("sid")}
    assert (expected_sids and expected_sids <= event_sids and all(sid in expected_sids or any(sid.startswith(parent + "/") for parent in expected_sids) for sid in event_sids)) or (not expected_sids and not event_sids)
    packets = {}
    for operation in owned:
        assert operation["invocationId"] == invocation and operation["outerProcessId"] == pid
        sid = operation["sid"]; assert _params(events, sid) == {"CVF_OUTER_INVOCATION_UUID": invocation, "CVF_OUTER_POWERSHELL_PID": str(pid)}
        starts = [item for item in events if item.get("sid") == sid and item.get("event") == "start"]; exits = [item for item in events if item.get("sid") == sid and item.get("event") == "exit"]
        assert len(starts) == len(exits) == 1 and starts[0].get("argv") == _argv(operation["owner"]) and int(exits[0].get("code")) == operation["exitCode"]
        assert len([item for item in events if item.get("sid") == operation["packetSid"] and item.get("event") == "start"]) == 1
        op_start, op_end = _time(operation["startedAt"]), _time(operation["completedAt"]); assert start <= op_start == _time(starts[0]["time"]) < op_end == _time(exits[0]["time"]) <= end
        packet_path = _file(operation["packetTrace"]); packet = packet_path.read_text(encoding="utf-8")
        tips = sorted(set(re.findall(r"\b([0-9a-f]{40}) refs/heads/main\b", packet)))
        assert re.search(rf"(?<!\d){operation['packetProcessId']}(?!\d)", packet) and (operation["exitCode"] != 0 or tips == [TARGET]) and len(tips) <= 1
        packets[operation["owner"]] = _sha(packet_path.read_bytes())
    assert exit_record["packetTraceSha256"] == packets
    assert (exit_record["exitCode"] == 0 and all(item["exitCode"] == 0 for item in owned)) or exit_record["exitCode"] != 0
    if any(item["exitCode"] != 0 for item in owned): assert exit_record["exitCode"] != 0
    return {"owner": actual, "uuid": invocation, "pid": pid, "exitCode": exit_record["exitCode"], "sids": [item["sid"] for item in owned], "networkOwners": raw["networkOwners"]}

def _identities(commands, operations):
    groups = ([item["uuid"] for item in commands], [item["pid"] for item in commands], [item["sid"] for item in operations], [item["packetSid"] for item in operations], [item["packetProcessId"] for item in operations], [(item["uuid"], item["pid"]) for item in commands])
    assert all(len(group) == len(set(group)) for group in groups) and set(groups[1]).isdisjoint(groups[4])
def _direct(commands, operations):
    joined, observed = [owner for command in commands for owner in command["networkOwners"]], [item["owner"] for item in operations]
    assert len(joined) == len(set(joined)) and all(owner in observed for owner in joined)
    return len([owner for owner in observed if owner not in joined])

def _git(repo, *args):
    env = os.environ.copy(); env.update({"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    done = subprocess.run(["git", *args], cwd=repo, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False); assert done.returncode == 0, done.stderr
    return done.stdout.strip()

def _core(desc):
    repo = _directory(desc); assert (repo / ".git").is_dir() and not (repo / ".git").is_symlink() and not (repo / ".git/objects/info/alternates").exists()
    target, tree = _git(repo, "rev-parse", "HEAD").lower(), _git(repo, "rev-parse", "HEAD^{tree}").lower(); porcelain = _git(repo, "status", "--porcelain=v1", "--untracked-files=all").replace("\r\n", "\n")
    assert HEX40.fullmatch(target) and HEX40.fullmatch(tree) and _git(repo, "remote", "get-url", "origin").rstrip("/").casefold() == REMOTE.rstrip("/").casefold() and _git(repo, "rev-parse", "origin/main").lower() == TARGET
    return _canonical({"target": target, "tree": tree, "worktree": _sha(porcelain.encode()), "adminDeltaClass": "CLEAN_PUBLIC_TARGET" if not porcelain and target == TARGET else "OBSERVED_GIT_DELTA"})

def _contract(shape, commands, count):
    owners = [item["owner"] for item in commands]; assert owners in (["RECONCILER"], ["RECONCILER", "INITIALIZER"])
    domain = shape["fieldDomains"]["outer_command_contract"]; options = [domain["const"]] if "const" in domain else list(domain["enum"])
    choices = [value for value in options if ("+" not in value if len(owners) == 1 else ("BEFORE_FETCH" in value if count == 1 else "+" in value and "BEFORE_FETCH" not in value))]
    assert len(choices) == 1
    return choices[0]

def _build(raw, matrix):
    assert set(raw) in (BASE_KEYS, BUILD_KEYS); operations = _operation_rows(raw["networkOperations"]); worker = [item for item in operations if item["owner"] in PREFIX]; rollback_ops = [item for item in operations if item["owner"] == "ROLLBACK_VERIFIER"]
    assert [item["owner"] for item in worker] == list(PREFIX[:len(worker)]) and operations == worker + rollback_ops
    prior, final_prior = _inventory(raw["buildPriorCandidates"]), _inventory(raw["finalPriorCandidates"])
    if not raw["commands"]:
        assert set(raw) == BASE_KEYS and not worker; shape = [item for item in _shapes(matrix) if "stop_stage" in item["requiredFields"]]; assert len(shape) == 1; shape = shape[0]
        rollback = _command(raw["rollbackCommand"], operations, "ROLLBACK_VERIFIER"); assert rollback["networkOwners"] == ["ROLLBACK_VERIFIER"] and rollback["exitCode"] == 0 and len(rollback_ops) == 1; _identities([rollback], operations)
        return _finish({"outcome": _const(shape, "outcome"), "stop_stage": _const(shape, "stop_stage"), "network_prefix_count": len(worker), "rollback_verifier_count": len(rollback_ops), "build_prior_candidates": prior, "final_prior_candidates": final_prior, "rollback_envelope_uuid": rollback["uuid"], "rollback_trace_uuid": rollback["uuid"], "rollback_envelope_pid": rollback["pid"], "rollback_trace_sid": _canonical(rollback["sids"]), "rollback_doctor_contract": _const(shape, "rollback_doctor_contract"), "direct_fetch_substitution_count": _direct([rollback], operations), "append_count": 0, "stop_state": _const(shape, "stop_state")}, shape)
    assert set(raw) == BUILD_KEYS and len(worker) <= 3; build = [_command(item, operations) for item in raw["commands"]]; assert all(item["owner"] in {"RECONCILER", "INITIALIZER"} for item in build) and [owner for item in build for owner in item["networkOwners"]] == [item["owner"] for item in worker]
    if raw["rollbackCommand"] is None:
        assert len(worker) == 3 and not rollback_ops and [item["exitCode"] for item in build] == [0, 0]; shape = _shape(matrix, network_prefix_count=3, rollback_verifier_count=0); rollback, all_commands = None, build
    else:
        assert len(rollback_ops) == 1 and all(item["exitCode"] == 0 for item in build[:-1]); shape = _shape(matrix, checkpoint_label="RECONCILER_RETURN", network_prefix_count=len(worker), rollback_verifier_count=1)
        rollback = _command(raw["rollbackCommand"], operations, "ROLLBACK_VERIFIER"); assert rollback["networkOwners"] == ["ROLLBACK_VERIFIER"] and rollback["exitCode"] == 0; all_commands = build + [rollback]
    _identities(all_commands, operations)
    projection = {"outcome": _const(shape, "outcome"), "correlation_claim": _const(shape, "correlation_claim"), "network_prefix_count": len(worker), "checkpoint_label": _const(shape, "checkpoint_label"), "checkpoint_scope": _const(shape, "checkpoint_scope"), "absence_claim_scope": _const(shape, "absence_claim_scope"), "build_prior_candidates": prior, "final_prior_candidates": final_prior, "checkpoint_candidates": _inventory(raw["checkpointCandidates"]), "final_checkpoint_candidates": _inventory(raw["finalCheckpointCandidates"]), "checkpoint_core": _core(raw["checkpointCoreRepository"]), "final_checkpoint_core": _core(raw["finalCheckpointCoreRepository"]), "outer_command_contract": _contract(shape, build, len(worker)), "build_envelope_uuid_set": _canonical([item["uuid"] for item in build]), "build_trace_uuid_set": _canonical([item["uuid"] for item in build]), "build_envelope_pid_set": _canonical([item["pid"] for item in build]), "build_trace_sid_set": _canonical([item["sid"] for item in worker]), "prefix_mapping": _const(shape, "prefix_mapping"), "window_relation": _const(shape, "window_relation"), "identity_relation": _const(shape, "identity_relation"), "direct_fetch_substitution_count": _direct(all_commands, operations), "rollback_verifier_count": len(rollback_ops), "append_count": 0}
    if rollback: projection.update({"rollback_envelope_uuid": rollback["uuid"], "rollback_trace_uuid": rollback["uuid"], "rollback_envelope_pid": rollback["pid"], "rollback_trace_sid": _canonical(rollback["sids"]), "rollback_doctor_contract": _const(shape, "rollback_doctor_contract"), "stop_state": _const(shape, "stop_state")})
    return _finish(projection, shape)

def _review_state(desc):
    root = _directory(desc); assert {item.name for item in root.iterdir()} <= {"completion.json", "runs", "anchors"}; runs, anchors, completion = root / "runs", root / "anchors", root / "completion.json"
    assert runs.is_dir() and anchors.is_dir() and not runs.is_symlink() and not anchors.is_symlink()
    return {"completion": completion.read_text(encoding="utf-8") if completion.is_file() else None, "runs": _tree_rows(runs), "anchors": _tree_rows(anchors), "runsRoot": runs, "anchorsRoot": anchors}
def _preserved(prior, final):
    before, after = {item["path"]: item for item in prior}, {item["path"]: item for item in final}; assert len(before) == len(prior) and len(after) == len(final) and all(after.get(path) == row for path, row in before.items())
    return [after[path] for path in sorted(before)], [row for path, row in after.items() if path not in before]
def _added(rows, root):
    assert len(rows) == 1 and rows[0]["type"] == "FILE"; path = (root / rows[0]["path"]).resolve(strict=True); assert path.is_relative_to(root.resolve(strict=True)) and path.is_file() and not path.is_symlink()
    return path, _sha(path.read_bytes())
def _review_record(path, keys):
    record = json.loads(path.read_text(encoding="utf-8")); assert isinstance(record, dict) and set(record) == keys and UUID4.fullmatch(record["reviewRunId"]) and UUID4.fullmatch(record["commandInvocationId"])
    assert isinstance(record["commandProcessId"], int) and record["commandProcessId"] > 0 and isinstance(record["commandTraceSids"], list) and record["commandTraceSids"] and len(record["commandTraceSids"]) == len(set(record["commandTraceSids"])); return record

def _review(raw, matrix):
    assert set(raw) == REVIEW_KEYS; operations = _operation_rows(raw["networkOperations"]); assert [item["owner"] for item in operations] == ["REVIEWER_DOCTOR"]
    command = _command(raw["reviewCommand"], operations, "REVIEWER_DOCTOR"); assert command["networkOwners"] == ["REVIEWER_DOCTOR"] and command["exitCode"] == 0
    prior, final = _review_state(raw["priorReviewState"]), _review_state(raw["finalReviewState"]); assert final["completion"] == prior["completion"]
    kept_runs, added_runs = _preserved(prior["runs"], final["runs"]); kept_anchors, added_anchors = _preserved(prior["anchors"], final["anchors"])
    run_path, run_digest = _added(added_runs, final["runsRoot"]); anchor_path, anchor_digest = _added(added_anchors, final["anchorsRoot"]); run_count = sum(row["type"] == "FILE" for row in prior["runs"]); anchor_count = sum(row["type"] == "FILE" for row in prior["anchors"])
    assert sum(row["type"] == "FILE" for row in final["runs"]) == run_count + 1 and sum(row["type"] == "FILE" for row in final["anchors"]) == anchor_count + 1
    prior_commands, prior_ops = [], []
    assert isinstance(raw["priorCommandBundles"], list) and raw["priorCommandBundles"]
    for bundle in raw["priorCommandBundles"]:
        assert isinstance(bundle, dict) and set(bundle) == {"commands", "networkOperations"}; bundle_ops = _operation_rows(bundle["networkOperations"]); bundle_commands = [_command(item, bundle_ops) for item in bundle["commands"]]; owners, op_owners = [item["owner"] for item in bundle_commands], [item["owner"] for item in bundle_ops]
        assert (owners == ["RECONCILER", "INITIALIZER"] and op_owners == list(PREFIX) and [item["exitCode"] for item in bundle_commands] == [0, 0]) or (owners == ["REVIEWER_DOCTOR"] and op_owners == ["REVIEWER_DOCTOR"] and bundle_commands[0]["exitCode"] == 0)
        assert [owner for item in bundle_commands for owner in item["networkOwners"]] == op_owners and _direct(bundle_commands, bundle_ops) == 0; prior_commands += bundle_commands; prior_ops += bundle_ops
    assert len(raw["priorCommandBundles"]) == run_count + 1 and [item["owner"] for item in prior_commands[:2]] == ["RECONCILER", "INITIALIZER"] and all(item["owner"] == "REVIEWER_DOCTOR" for item in prior_commands[2:]) and sum(item["owner"] == "REVIEWER_DOCTOR" for item in prior_commands) == run_count; _identities(prior_commands + [command], prior_ops + operations)
    run_keys = {"reviewRunId", "commandInvocationId", "commandProcessId", "commandTraceSids", "anchorRelativePath"}; anchor_keys = {"reviewRunId", "commandInvocationId", "commandProcessId", "commandTraceSids", "runRelativePath", "runSha256"}
    old_runs = sorted(path for path in prior["runsRoot"].rglob("*") if path.is_file()); assert len(old_runs) == len(prior_commands[2:])
    for path, old_command in zip(old_runs, prior_commands[2:]):
        old = _review_record(path, run_keys); assert (old["commandInvocationId"], old["commandProcessId"], old["commandTraceSids"]) == (old_command["uuid"], old_command["pid"], old_command["sids"])
    run, anchor = _review_record(run_path, run_keys), _review_record(anchor_path, anchor_keys)
    assert run["reviewRunId"] == anchor["reviewRunId"] and run["commandInvocationId"] == anchor["commandInvocationId"] == command["uuid"] and run["commandProcessId"] == anchor["commandProcessId"] == command["pid"] and run["commandTraceSids"] == anchor["commandTraceSids"] == command["sids"]
    assert run["anchorRelativePath"] == anchor_path.relative_to(final["anchorsRoot"]).as_posix() and anchor["runRelativePath"] == run_path.relative_to(final["runsRoot"]).as_posix() and anchor["runSha256"] == run_digest
    if prior["completion"] is None:
        assert not prior["runs"] and not prior["anchors"]; shape = _shape(matrix, prior_run_count=0, prior_anchor_count=0); completion, final_completion = _const(shape, "prior_completion_payload"), _const(shape, "final_prior_completion_payload"); runs, final_runs = _const(shape, "prior_review_runs"), _const(shape, "final_prior_review_runs"); anchors, final_anchors = _const(shape, "prior_anchor_inventory"), _const(shape, "final_prior_anchor_inventory")
    else:
        assert run_count > 0 and anchor_count > 0; candidates = [item for item in _shapes(matrix) if "preserved_prior_run_count" in item["requiredFields"]]; assert len(candidates) == 1; shape = candidates[0]
        completion, final_completion, runs, final_runs, anchors, final_anchors = prior["completion"], final["completion"], _canonical(prior["runs"]), _canonical(kept_runs), _canonical(prior["anchors"]), _canonical(kept_anchors)
    projection = {"outcome": _const(shape, "outcome"), "review_claim": _const(shape, "review_claim"), "review_envelope_uuid": command["uuid"], "review_trace_uuid": command["uuid"], "review_envelope_pid": command["pid"], "review_trace_sid": _canonical(command["sids"]), "review_doctor_contract": _const(shape, "review_doctor_contract"), "window_relation": _const(shape, "window_relation"), "identity_relation": _const(shape, "identity_relation"), "direct_fetch_substitution_count": _direct([command], operations), "prior_completion_payload": completion, "final_prior_completion_payload": final_completion, "prior_review_runs": runs, "final_prior_review_runs": final_runs, "prior_anchor_inventory": anchors, "final_prior_anchor_inventory": final_anchors, "prior_run_count": run_count, "prior_anchor_count": anchor_count, "new_run_digest": run_digest, "new_anchor_digest": anchor_digest, "append_count": len(added_runs), "new_anchor_count": len(added_anchors)}
    if "preserved_prior_run_count" in shape["requiredFields"]: projection.update({"prior_completion_sha256": _sha(completion.encode()), "prior_review_runs_sha256": _sha(runs.encode()), "prior_anchor_inventory_sha256": _sha(anchors.encode()), "preserved_prior_run_count": sum(row["type"] == "FILE" for row in kept_runs), "preserved_prior_anchor_count": sum(row["type"] == "FILE" for row in kept_anchors)})
    return _finish(projection, shape)

def _finish(projection, shape):
    assert set(projection) == set(shape["requiredFields"]) and not set(projection) & set(shape["forbiddenFields"])
    for field, domain in shape["fieldDomains"].items():
        value = projection[field]; assert "const" not in domain or value == domain["const"]; assert "enum" not in domain or value in domain["enum"]
        assert domain.get("type") != "STRING" or isinstance(value, str); assert domain.get("type") != "INTEGER" or isinstance(value, int) and not isinstance(value, bool); assert "minLength" not in domain or len(value) >= domain["minLength"]; assert "pattern" not in domain or re.fullmatch(domain["pattern"], value)
    for relation in shape["relations"]:
        if relation["kind"] == "COUNTER_EQUALITY": assert projection[relation["field"]] == relation["value"]
        elif relation["kind"] == "FIELD_EQUALITY": assert projection[relation["sourceField"]] == projection[relation["targetField"]]
        elif relation["kind"] == "DIGEST_EQUALITY": assert relation["function"] == "SHA256_UTF8" and _sha(projection[relation["sourceField"]].encode()) == projection[relation["targetField"]]
        else: raise AssertionError(f"unsupported matrix relation: {relation['kind']}")
    return projection

def _derive(raw, matrix):
    assert isinstance(raw, dict) and "outcomeId" not in raw; _shapes(matrix)
    return _review(raw, matrix) if "reviewCommand" in raw else _build(raw, matrix)
def derive_root_effects(raw_case, matrix): assert raw_case.get("surface") == "ROOT_EFFECTS_VALIDATOR"; return _derive(raw_case, matrix)
def derive_independent_review(raw_case, matrix): assert raw_case.get("surface") == "INDEPENDENT_REVIEW_VALIDATOR"; return _derive(raw_case, matrix)
