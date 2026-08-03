from __future__ import annotations
import base64
import copy
import inspect
import json
import multiprocessing
import os
import sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path: sys.path.insert(0, str(SCRIPTS))
import _project_operations_skill_live_evidence_support as support  # noqa: E402
import run_project_operations_skill_live_evidence as runner  # noqa: E402
def evidence_paths(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    return {"state_path": root / "state.json", "receipt_path": root / "receipt.md", "lock_path": root / ".lock",
            "state_temp": root / ".state.tmp", "receipt_temp": root / ".receipt.tmp"}
def failed3_state_bytes() -> bytes:
    raw = runner.STATE.read_bytes()
    if (len(raw), support.sha(raw)) == support.FAILED3_STATE: return raw
    return base64.b64decode(json.loads(raw)["replacement_3_snapshot"]["data"], validate=True)
def failed3_receipt_bytes() -> bytes:
    return runner.RECEIPT.read_bytes()[:support.FAILED3_RECEIPT[0]]
def migrated(tmp_path: Path) -> dict:
    p = evidence_paths(tmp_path)
    p["state_path"].write_bytes(failed3_state_bytes()); p["receipt_path"].write_bytes(failed3_receipt_bytes())
    runner.migrate_amendment4(run_preflight=False, **p)
    return p
def valid_response(ft_id: str) -> dict:
    values = {
        "FT-1": ("SPEC", "SPEC", False, "NONE", ["BUILD", "PROVIDER_CALL"]),
        "FT-2": ("WORK_ORDER", "STOP_AT_INTAKE", True, "CONTINUITY_DRIFT", ["BUILD"]),
        "FT-3": ("SPEC", "WORK_ORDER", True, "MISSING_WORK_ORDER", ["BUILD"]),
        "FT-4": ("REVIEW", "REPAIR_CLEANUP", True, "INCOMPLETE_CLOSURE_OR_GATE", ["FREEZE"]),
    }[ft_id]
    return {"current_phase": values[0], "next_allowed_move": values[1], "stop": values[2],
            "stop_reason": values[3], "forbidden_actions_avoided": values[4],
            "authority_source": support.AUTHORITY_SOURCE, "claim_boundary": support.CLAIM_BOUNDARY}
def fake_provider() -> tuple[str, str, str]:
    return "sentinel-test-key", "https://example.invalid/v1/chat/completions", "test-model"
def current_identity() -> tuple[str, str]:
    return support.bundle_digest(runner.BUNDLE_PATHS), support.digest(runner.SKILL.read_bytes())
def test_public_request_has_structural_noninterference() -> None:
    source = inspect.getsource(support.build_request)
    assert "EXPECTATIONS" not in source and list(inspect.signature(support.build_request).parameters) == ["ft_id", "skill_text"]
    skill = runner.SKILL.read_text(encoding="utf-8")
    canaries = [next(iter(expected["private_canary"].items())) for expected in support.EXPECTATIONS.values()]
    assert len({key for key, _ in canaries}) == len(canaries) == len({value for _, value in canaries})
    for ft_id, expected in support.EXPECTATIONS.items():
        serialized = support.canonical(support.build_request(ft_id, skill))
        assert not any(token in serialized for token in next(iter(expected["private_canary"].items())))
        assert '"expected"' not in serialized and '"target"' not in serialized
        assert support.PUBLIC_FIXTURES[ft_id] == json.loads(serialized)["fixture"]
        schema = json.loads(serialized)["response_schema"]
        assert schema["forbidden_actions_avoided"] == {"type": "array", "uniqueItems": True, "items": {"enum": sorted(support.ACTIONS)}}
        assert schema["current_phase"] == {"enum": sorted(support.PHASES)} and schema["next_allowed_move"] == {"enum": sorted(support.NEXT_MOVES)}
        assert schema["stop_reason"] == {"enum": sorted(support.STOP_REASONS)}
    instruction = support.build_request("FT-1", skill)["instruction"].lower()
    assert not any(phrase in instruction for phrase in ("phase must", "next must", "stop must", "list exactly", "authority_source must", "claim_boundary must"))
def test_response_requires_exact_types_before_semantics() -> None:
    for ft_id in support.PUBLIC_FIXTURES:
        raw = json.dumps(valid_response(ft_id)); assert support.validate_response(ft_id, raw) == valid_response(ft_id)
    for wrong in (0, 1, "false", None):
        response = valid_response("FT-1"); response["stop"] = wrong
        with pytest.raises(support.EvidenceError, match="types"): support.validate_response("FT-1", json.dumps(response))
    response = valid_response("FT-1"); response["forbidden_actions_avoided"] = [1]
    with pytest.raises(support.EvidenceError, match="types/labels"): support.validate_response("FT-1", json.dumps(response))
    with pytest.raises(support.SemanticError): support.validate_response("FT-2", json.dumps({**valid_response("FT-2"), "next_allowed_move": "INTAKE"}))
@pytest.mark.parametrize("ft,next_move", [("FT-1", "WORK_ORDER"), ("FT-2", "STOP_AT_INTAKE"), ("FT-4", "REVIEW"), ("FT-4", "REPAIR"), ("FT-4", "CLEANUP")])
def test_private_equivalence_classes_are_deterministic(ft: str, next_move: str) -> None:
    response = valid_response(ft); response["next_allowed_move"] = next_move
    assert support.validate_response(ft, json.dumps(response)) == response
def test_every_private_rejection_neighbor_is_deterministic() -> None:
    for ft, expected in support.EXPECTATIONS.items():
        base = valid_response(ft); cases = [("current_phase", v) for v in support.PHASES - {expected["phase"]}]
        cases += [("next_allowed_move", v) for v in support.NEXT_MOVES - expected["next"]]
        cases += [("stop_reason", v) for v in support.STOP_REASONS - {expected["reason"]}] + [("stop", not expected["stop"])]
        candidates = [{**base, field: value} for field, value in cases]
        candidates += [{**base, "forbidden_actions_avoided": [v for v in base["forbidden_actions_avoided"] if v != action]} for action in expected["avoid"]]
        for response in candidates:
            with pytest.raises(support.SemanticError) as caught: support.validate_response(ft, json.dumps(response))
            assert caught.value.candidate == response
def test_migration_preserves_failed_v4_and_nested_v3_v2_v1(tmp_path: Path) -> None:
    p = migrated(tmp_path); state = json.loads(p["state_path"].read_text(encoding="utf-8")); snap = state["replacement_3_snapshot"]
    decoded = base64.b64decode(snap["data"], validate=True)
    assert (len(decoded), support.sha(decoded)) == support.FAILED3_STATE and decoded == failed3_state_bytes()
    old = support.validate_failed3(decoded); assert support.validate_failed2(base64.b64decode(old["replacement_2_snapshot"]["data"], validate=True))
    receipt = p["receipt_path"].read_bytes(); assert receipt.startswith(failed3_receipt_bytes())
    assert state["replacement_3_invalidated"]["mechanical_accepted"] == 1 and state["replacement_3_invalidated"]["governance_accepted"] == 0
    old_keys = {r["lineage_key"] for r in state["replacement_3_invalidated"]["records"].values()}
    lineages = [support.replacement_lineage(ft, state["replacement_4_final"]["bundle_digest"]) for ft in support.PUBLIC_FIXTURES]
    assert len(set(lineages)) == 4 and not set(lineages) & old_keys
    assert runner.summary(state)["history"] == {"physical": 8, "invalidated": 8, "accepted": 0}
    runner.validate_receipt(state, p["receipt_path"])
def test_success_dispatches_before_transport_and_finishes_history_12_8_4(tmp_path: Path) -> None:
    p = migrated(tmp_path); calls = []
    def transport(**kwargs) -> str:
        ft = kwargs["request_object"]["scenario_id"]; state = json.loads(p["state_path"].read_text())
        assert state["replacement_4_final"]["records"][ft]["status"] == "DISPATCHED"
        assert state["replacement_4_final"]["records"][ft]["physical_call"] == 1
        calls.append(ft); return json.dumps(valid_response(ft))
    result = runner.run(transport=transport, provider=fake_provider(), run_preflight=False, **p)
    assert calls == list(support.PUBLIC_FIXTURES) and result["history"] == {"physical": 12, "invalidated": 8, "accepted": 4}
    assert not any(p[key].exists() for key in ("lock_path", "state_temp", "receipt_temp"))
    with pytest.raises(support.EvidenceError): runner.run(transport=transport, provider=fake_provider(), run_preflight=False, **p)
    assert len(calls) == 4
def _crash_worker(root: str, point: str) -> None:
    p = evidence_paths(Path(root))
    def transport(**kwargs) -> str:
        if point == "post_dispatch": os._exit(21)
        return json.dumps(valid_response(kwargs["request_object"]["scenario_id"]))
    def before(_ft: str) -> None:
        if point == "pre_dispatch": os._exit(20)
    def after(_ft: str) -> None:
        if point == "post_return": os._exit(22)
    runner.run(transport=transport, provider=fake_provider(), run_preflight=False, before_dispatch=before, after_transport=after, **p)
@pytest.mark.parametrize("point,expected,physical", [("pre_dispatch", "RESERVED", 0), ("post_dispatch", "DISPATCHED", 1), ("post_return", "DISPATCHED", 1)])
def test_subprocess_crash_accounting(tmp_path: Path, point: str, expected: str, physical: int) -> None:
    p = migrated(tmp_path); ctx = multiprocessing.get_context("spawn"); proc = ctx.Process(target=_crash_worker, args=(str(tmp_path), point)); proc.start(); proc.join(15)
    assert proc.exitcode in {20, 21, 22}
    state = json.loads(p["state_path"].read_text()); record = state["replacement_4_final"]["records"]["FT-1"]
    assert (record["status"], record["physical_call"]) == (expected, physical)
    runner.validate_receipt(state, p["receipt_path"])
    assert not p["lock_path"].exists()
def mutate_state(p: dict, mutation) -> None:
    state = json.loads(p["state_path"].read_text()); mutation(state); p["state_path"].write_text(json.dumps(state), encoding="utf-8")
@pytest.mark.parametrize("mutation", [
    lambda s: s.update(extra=1),
    lambda s: s.update(schema_version=2),
    lambda s: s["replacement_4_final"]["records"].pop("FT-4"),
    lambda s: s["replacement_4_final"]["records"].update({"FT-5": {}}),
    lambda s: s["replacement_4_final"].update(extra=1),
    lambda s: s["replacement_4_final"].update(skill_digest=1),
    lambda s: s["replacement_4_final"]["records"]["FT-1"].update(extra=1),
    lambda s: s["replacement_4_final"]["records"]["FT-1"].update(lineage_key="tampered"),
    lambda s: s["replacement_4_final"]["records"]["FT-1"].update(bundle_digest="tampered"),
    lambda s: s["replacement_4_final"]["records"]["FT-1"].update(physical_call=False),
    lambda s: s["replacement_4_final"]["records"]["FT-1"].update(transitions=[]),
    lambda s: s["replacement_4_final"]["records"]["FT-1"].update(status="ACCEPTED", physical_call=0),
    lambda s: s["replacement_4_final"]["fixtures"].update({"FT-1": "bad"}),
    lambda s: s["replacement_3_snapshot"].update(length=1),
    lambda s: s["replacement_3_invalidated"].update(disposition="ACTIVE"),
    lambda s: s["replacement_3_invalidated"]["records"].pop("FT-4"),
])
def test_state_mutation_matrix_fails_closed(tmp_path: Path, mutation) -> None:
    p = migrated(tmp_path); bundle, skill = current_identity(); mutate_state(p, mutation)
    with pytest.raises((support.EvidenceError, ValueError, KeyError)): support.load_v5(p["state_path"], bundle, skill)
def test_receipt_mismatch_fails_closed(tmp_path: Path) -> None:
    p = migrated(tmp_path); state = json.loads(p["state_path"].read_text()); content = p["receipt_path"].read_bytes().replace(b'"physical":0', b'"physical":9', 1); p["receipt_path"].write_bytes(content)
    with pytest.raises(support.EvidenceError, match="invalid|coherence"): runner.validate_receipt(state, p["receipt_path"])
@pytest.mark.parametrize("kind", ["missing_key", "bad_base", "model", "validator", "secret_fixture", "residue"])
def test_preflight_failures_are_zero_call_zero_mutation(tmp_path: Path, monkeypatch, kind: str) -> None:
    p = migrated(tmp_path); before_state = p["state_path"].read_bytes(); before_receipt = p["receipt_path"].read_bytes(); calls = 0
    def transport(**_kwargs) -> str:
        nonlocal calls; calls += 1; return "{}"
    if kind == "missing_key":
        for name in runner.KEYS: monkeypatch.delenv(name, raising=False)
    elif kind == "bad_base":
        monkeypatch.setenv("ALIBABA_API_KEY", "x"); monkeypatch.setenv("ALIBABA_BASE_URL", "not-a-url")
    elif kind == "model":
        monkeypatch.setenv("ALIBABA_API_KEY", "x"); monkeypatch.setattr(runner, "select_model", lambda: (_ for _ in ()).throw(ValueError("no model")))
    elif kind == "validator": monkeypatch.setattr(runner, "validator_path", lambda: tmp_path / "missing")
    elif kind == "secret_fixture": monkeypatch.setitem(support.PUBLIC_FIXTURES["FT-1"]["facts"], "note", "sk-SUPERSECRET123")
    else: p["lock_path"].write_text("residue")
    with pytest.raises((support.EvidenceError, ValueError)):
        if kind in {"validator", "secret_fixture"}: runner.preflight(run_tests=False)
        else: runner.run(transport=transport, run_preflight=False, **p)
    assert calls == 0 and p["state_path"].read_bytes() == before_state and p["receipt_path"].read_bytes() == before_receipt
    if kind != "residue": assert not any(p[key].exists() for key in ("lock_path", "state_temp", "receipt_temp"))
def test_provider_precedence_and_safe_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("ALIBABA_API_KEY", "first"); monkeypatch.setenv("DASHSCOPE_API_KEY", "second")
    monkeypatch.setenv("ALIBABA_BASE_URL", "https://user:pass@example.test/v1?secret=x"); monkeypatch.setattr(runner, "select_model", lambda: "model")
    key, endpoint, model = runner.resolve_provider(); assert (key, model) == ("first", "model")
    assert endpoint == support.safe_endpoint(endpoint) == "https://example.test/v1/chat/completions"
@pytest.mark.parametrize("kind,status", [(k, "INDETERMINATE" if k in {"http", "timeout"} else "FAILED") for k in
    ("http", "timeout", "malformed", "semantic", "missing", "extra", "type", "enum", "duplicate", "secret", "envelope")])
def test_transport_and_response_failures_consume_without_retry(tmp_path: Path, kind: str, status: str) -> None:
    p = migrated(tmp_path); calls = []
    def transport(**_kwargs) -> str:
        calls.append(kind)
        if kind == "http": raise runner.ProviderFailure("provider_http_500")
        if kind == "timeout": raise TimeoutError("sentinel transport detail")
        if kind == "malformed": return "not-json"
        response = valid_response("FT-1")
        if kind == "semantic": response["current_phase"] = "BUILD"
        elif kind == "missing": response.pop("stop_reason")
        elif kind == "extra": response["provider_envelope_sentinel"] = "never-retain"
        elif kind == "type": response["stop"] = 1
        elif kind == "enum": response["current_phase"] = "UNKNOWN_ENUM"
        elif kind == "duplicate": response["forbidden_actions_avoided"].append("BUILD")
        elif kind == "secret": response["authority_source"] = "sk-NEVERRETAIN123"
        elif kind == "envelope": response = {"choices": [{"message": {"content": "provider-envelope-sentinel"}}]}
        return json.dumps(response)
    with pytest.raises(support.EvidenceError) as caught: runner.run(transport=transport, provider=fake_provider(), run_preflight=False, **p)
    record = json.loads(p["state_path"].read_text())["replacement_4_final"]["records"]["FT-1"]
    assert (record["status"], record["physical_call"], len(calls)) == (status, 1, 1)
    if kind == "semantic": assert record["candidate_response"] == {**valid_response("FT-1"), "current_phase": "BUILD"}
    elif status == "FAILED": assert "candidate_response" not in record
    blob = p["state_path"].read_bytes() + p["receipt_path"].read_bytes() + str(caught.value).encode()
    assert not any(token in blob for token in (b"not-json", b"never-retain", b"UNKNOWN_ENUM", b"NEVERRETAIN", b"provider-envelope-sentinel"))
    with pytest.raises(support.EvidenceError): runner.run(transport=transport, provider=fake_provider(), run_preflight=False, **p)
    assert len(calls) == 1 and not any(p[key].exists() for key in ("lock_path", "state_temp", "receipt_temp"))
def reserve_first(p: dict) -> tuple[str, str]:
    bundle, skill = current_identity(); request = support.build_request("FT-1", runner.SKILL.read_text(encoding="utf-8"))
    state = support.reserve(state_path=p["state_path"], state_temp=p["state_temp"], lock_path=p["lock_path"],
                            bundle=bundle, skill=skill, ft_id="FT-1", attempt_id="attempt", request=request,
                            model="model", endpoint="https://example.invalid/v1/chat/completions")
    p["receipt_path"].write_bytes(runner.receipt_bytes(state, p["receipt_path"])); return bundle, skill
@pytest.mark.parametrize("field,value", [("attempt_id", 1), ("model", 1), ("endpoint", "https://user:pass@example.test/v1"), ("request", {})])
def test_reserved_metadata_tamper_is_rejected(tmp_path: Path, field: str, value) -> None:
    p = migrated(tmp_path); bundle, skill = reserve_first(p); state = json.loads(p["state_path"].read_text())
    state["replacement_4_final"]["records"]["FT-1"][field] = value; p["state_path"].write_text(json.dumps(state), encoding="utf-8")
    with pytest.raises((support.EvidenceError, TypeError)): support.load_v5(p["state_path"], bundle, skill)
@pytest.mark.parametrize("kind", ["response", "error"])
def test_terminal_response_or_error_tamper_is_rejected(tmp_path: Path, kind: str) -> None:
    p = migrated(tmp_path); runner.run(transport=lambda **kw: json.dumps(valid_response(kw["request_object"]["scenario_id"])), provider=fake_provider(), run_preflight=False, **p)
    bundle, skill = current_identity(); state = json.loads(p["state_path"].read_text()); record = state["replacement_4_final"]["records"]["FT-1"]
    if kind == "response": record["response"]["stop"] = 1
    else: record["status"] = record["transitions"][-1] = "FAILED"; record["error"] = 1; record.pop("response")
    p["state_path"].write_text(json.dumps(state), encoding="utf-8")
    with pytest.raises(support.EvidenceError): support.load_v5(p["state_path"], bundle, skill)
@pytest.mark.parametrize("truncate", [None, "v4", "v3", "v2", "v1"])
def test_reset_shaped_and_coherent_rollback_block_transport(tmp_path: Path, truncate: str | None) -> None:
    p = migrated(tmp_path); bundle, skill = reserve_first(p); state = json.loads(p["state_path"].read_text())
    fresh = support.new_v5(failed3_state_bytes(), bundle, skill)["replacement_4_final"]["records"]["FT-1"]
    state["replacement_4_final"]["records"]["FT-1"] = fresh; p["state_path"].write_text(json.dumps(state), encoding="utf-8")
    if truncate == "v4": p["receipt_path"].write_bytes(failed3_receipt_bytes())
    if truncate == "v3": p["receipt_path"].write_bytes(failed3_receipt_bytes()[:support.FAILED2_RECEIPT[0]])
    if truncate == "v2": p["receipt_path"].write_bytes(failed3_receipt_bytes()[:support.FAILED_RECEIPT[0]])
    if truncate == "v1": p["receipt_path"].write_bytes(failed3_receipt_bytes()[:support.ORIGINAL_RECEIPT[0]])
    with pytest.raises(support.EvidenceError, match="rollback|coherence|anchor"):
        p["receipt_path"].write_bytes(runner.receipt_bytes(state, p["receipt_path"]))
    calls = []
    with pytest.raises(support.EvidenceError): runner.run(transport=lambda **kw: calls.append(kw), provider=fake_provider(), run_preflight=False, **p)
    assert calls == []
@pytest.mark.parametrize("kind", ["reserved", "stale_receipt", "digest"])
def test_nonunused_stale_and_digest_state_block_transport(tmp_path: Path, kind: str) -> None:
    p = migrated(tmp_path)
    if kind in {"reserved", "stale_receipt"}:
        before_receipt = p["receipt_path"].read_bytes(); reserve_first(p)
        if kind == "stale_receipt": p["receipt_path"].write_bytes(before_receipt)
    else:
        mutate_state(p, lambda s: s["replacement_4_final"].update(bundle_digest="bad"))
    before = (p["state_path"].read_bytes(), p["receipt_path"].read_bytes()); calls = []
    with pytest.raises(support.EvidenceError): runner.run(transport=lambda **kw: calls.append(kw), provider=fake_provider(), run_preflight=False, **p)
    assert calls == [] and before == (p["state_path"].read_bytes(), p["receipt_path"].read_bytes())
@pytest.mark.parametrize("target", ["state", "receipt"])
def test_atomic_replace_failure_never_calls_or_fabricates_pass(tmp_path: Path, monkeypatch, target: str) -> None:
    p = migrated(tmp_path); before_state = p["state_path"].read_bytes(); before_receipt = p["receipt_path"].read_bytes(); calls = []
    real_replace = support.os.replace
    def fail_selected(src, dst):
        if Path(dst) == p[f"{target}_path"]: raise OSError("replace failed")
        return real_replace(src, dst)
    monkeypatch.setattr(support.os, "replace", fail_selected)
    with pytest.raises(OSError): runner.run(transport=lambda **kw: calls.append(kw), provider=fake_provider(), run_preflight=False, **p)
    assert calls == [] and p["receipt_path"].read_bytes() == before_receipt
    if target == "state": assert p["state_path"].read_bytes() == before_state
    else: assert json.loads(p["state_path"].read_text())["replacement_4_final"]["records"]["FT-1"]["status"] == "RESERVED"
    assert not any(p[key].exists() for key in ("lock_path", "state_temp", "receipt_temp"))
@pytest.mark.parametrize("fail_at", [0, 1])
def test_failing_validator_subprocess_is_zero_call_and_safe(tmp_path: Path, monkeypatch, fail_at: int) -> None:
    p = migrated(tmp_path); before = (p["state_path"].read_bytes(), p["receipt_path"].read_bytes())
    calls = []
    def fake_run(*args, **kwargs): calls.append(args); return type("Result", (), {"returncode": int(len(calls) - 1 == fail_at)})()
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    with pytest.raises(support.EvidenceError, match="pre-network"): runner.preflight()
    assert before == (p["state_path"].read_bytes(), p["receipt_path"].read_bytes())
def test_sentinel_transport_detail_never_reaches_state_receipt_or_exception(tmp_path: Path) -> None:
    p = migrated(tmp_path); sentinel = "sk-NEVERPERSIST123"
    with pytest.raises(support.EvidenceError) as caught:
        runner.run(transport=lambda **_kw: (_ for _ in ()).throw(RuntimeError(sentinel)), provider=fake_provider(), run_preflight=False, **p)
    blob = p["state_path"].read_bytes() + p["receipt_path"].read_bytes()
    assert sentinel not in str(caught.value) and sentinel.encode() not in blob
@pytest.mark.parametrize("error_type", [support.EvidenceError, ValueError])
def test_main_suppresses_secret_like_exception(monkeypatch, capsys, error_type) -> None:
    sentinel = "sk-NEVERPRINT123"; monkeypatch.setattr(sys, "argv", ["runner", "--json"])
    monkeypatch.setattr(runner, "run", lambda: (_ for _ in ()).throw(error_type(sentinel)))
    assert runner.main() == 1 and sentinel not in capsys.readouterr().out
def _contention_worker(root: str, calls_path: str) -> None:
    p = evidence_paths(Path(root))
    def transport(**kwargs) -> str:
        with Path(calls_path).open("a", encoding="utf-8") as stream: stream.write(kwargs["request_object"]["scenario_id"] + "\n")
        return json.dumps(valid_response(kwargs["request_object"]["scenario_id"]))
    try: runner.run(transport=transport, provider=fake_provider(), run_preflight=False, **p)
    except Exception: pass
def test_two_process_contention_calls_each_lineage_at_most_once(tmp_path: Path) -> None:
    migrated(tmp_path); calls = tmp_path / "calls.txt"; ctx = multiprocessing.get_context("spawn")
    processes = [ctx.Process(target=_contention_worker, args=(str(tmp_path), str(calls))) for _ in range(2)]
    for process in processes: process.start()
    for process in processes: process.join(20)
    assert all(not process.is_alive() for process in processes)
    seen = calls.read_text().splitlines() if calls.exists() else []
    assert seen and all(seen.count(ft) <= 1 for ft in support.PUBLIC_FIXTURES)
def test_no_fifth_batch_raw_or_retry_route() -> None:
    assert set(support.PUBLIC_FIXTURES) == {"FT-1", "FT-2", "FT-3", "FT-4"}
    source = inspect.getsource(runner.run)
    assert "retry" not in source.lower() and "for ft_id in PUBLIC_FIXTURES" in source
    assert '"messages": [{"role": "user"' in inspect.getsource(runner.http_transport)
