#!/usr/bin/env python3
"""Migrate retained evidence and run four authorized replacement sessions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PROVIDER = ROOT / "packages" / "ai-providers" / "alibaba"
for bootstrap in (SCRIPTS, PROVIDER):
    if str(bootstrap) not in sys.path: sys.path.insert(0, str(bootstrap))

from _project_operations_skill_live_evidence_support import (  # noqa: E402
    EvidenceError, SemanticError, FAILED3_RECEIPT, FAILED3_STATE, PUBLIC_FIXTURES, assert_safe,
    atomic_bytes, build_request, bundle_digest, canonical, digest, dispatch, finish,
    load_v5, new_v5, reserve, runtime_lock, safe_endpoint, sha, validate_public_fixtures,
    validate_response,
)
from select_model import select_model  # noqa: E402

SKILL = ROOT / "skills" / "operate-shift-workspace" / "SKILL.md"
OPENAI = SKILL.parent / "agents" / "openai.yaml"
CONTRACT_TEST = ROOT / "tests" / "unit" / "test_project_operations_skill_contract.py"
LIVE_TEST = ROOT / "tests" / "unit" / "test_project_operations_skill_live_evidence.py"
RUNNER = Path(__file__).resolve()
SUPPORT = SCRIPTS / "_project_operations_skill_live_evidence_support.py"
BUNDLE_PATHS = [SKILL, OPENAI, CONTRACT_TEST, RUNNER, SUPPORT, LIVE_TEST]
STATE = ROOT / "docs" / "decisions" / "PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json"
RECEIPT = ROOT / "docs" / "decisions" / "PROJECT_OPERATIONS_SKILL_FORWARD_TEST_RECEIPT.md"
LOCK = ROOT / "docs" / "decisions" / ".PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE.lock"
STATE_TEMP = ROOT / "docs" / "decisions" / ".PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json.tmp"
RECEIPT_TEMP = ROOT / "docs" / "decisions" / ".PROJECT_OPERATIONS_SKILL_FORWARD_TEST_RECEIPT.md.tmp"
KEYS, BASES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY"), ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
SUMMARY_RE = re.compile(rb"<!-- PROJECT_OPERATIONS_SKILL_AMENDMENT_4_SUMMARY\n(.+?)\n-->", re.S)


class ProviderFailure(RuntimeError):
    pass


def resolve_provider() -> tuple[str, str, str]:
    key = next((os.environ[n].strip() for n in KEYS if os.environ.get(n, "").strip()), "")
    if not key: raise EvidenceError("provider key is unavailable")
    base = next((os.environ[n].strip() for n in BASES if os.environ.get(n, "").strip()), DEFAULT_BASE)
    parsed = urlsplit(base)
    endpoint = urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/") + "/chat/completions", "", ""))
    endpoint = safe_endpoint(endpoint); model = select_model(); assert_safe(model)
    return key, endpoint, model


def http_transport(*, endpoint: str, key: str, model: str, request_object: dict[str, Any]) -> str:
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": canonical(request_object)}],
                       "temperature": 0, "response_format": {"type": "json_object"}}, ensure_ascii=False).encode()
    request = urllib.request.Request(endpoint, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            if response.status != 200: raise ProviderFailure(f"provider_http_{response.status}")
            payload = json.loads(response.read().decode())
            return str(payload["choices"][0]["message"]["content"])
    except urllib.error.HTTPError as exc: raise ProviderFailure(f"provider_http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError): raise ProviderFailure("provider_transport_failure") from None
    except (KeyError, IndexError, TypeError, json.JSONDecodeError): raise ProviderFailure("provider_envelope_invalid") from None


def validator_path() -> Path:
    configured = os.environ.get("SKILL_CREATOR_ROOT", "").strip()
    root = Path(configured) if configured else Path.home() / ".codex" / "skills" / ".system" / "skill-creator"
    return root / "scripts" / "quick_validate.py"


def preflight(*, run_tests: bool = True) -> None:
    if not all(path.is_file() for path in BUNDLE_PATHS): raise EvidenceError("evidence bundle path missing")
    if any(path.exists() for path in (LOCK, STATE_TEMP, RECEIPT_TEMP)): raise EvidenceError("runtime residue exists")
    validate_public_fixtures()
    validator = validator_path()
    if not validator.is_file(): raise EvidenceError("skill validator unavailable")
    if run_tests:
        commands = [[sys.executable, str(validator), str(SKILL.parent)],
                    [sys.executable, "-m", "pytest", "-q", str(CONTRACT_TEST), str(LIVE_TEST)]]
        for command in commands:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120, check=False)
            if result.returncode: raise EvidenceError("pre-network validation failed")


def _prefix(receipt_path: Path) -> bytes:
    content = receipt_path.read_bytes(); length, expected = FAILED3_RECEIPT
    prefix = content[:length]
    if len(prefix) != length or sha(prefix) != expected: raise EvidenceError("failed receipt prefix mismatch")
    return prefix


def summary(state: dict[str, Any]) -> dict[str, Any]:
    records = state["replacement_4_final"]["records"]
    physical = sum(record["physical_call"] for record in records.values())
    accepted = sum(record["status"] == "ACCEPTED" for record in records.values())
    return {"disposition": "PASS" if (physical, accepted) == (4, 4) else "INCOMPLETE_OR_FAIL",
            "original": {"physical": 4, "invalidated": 4, "accepted": 0},
            "replacement_1": {"physical": 1, "invalidated": 1, "accepted": 0},
            "replacement_2": {"physical": 1, "invalidated": 1, "accepted": 0,
                              "statuses": {"FT-1": "FAILED", "FT-2": "UNUSED", "FT-3": "UNUSED", "FT-4": "UNUSED"}},
            "replacement_3": {"physical": 2, "mechanical_accepted": 1, "failed": 1, "governance_accepted": 0,
                              "statuses": {ft: record["status"] for ft, record in state["replacement_3_invalidated"]["records"].items()}},
            "replacement_4": {"physical": physical, "accepted": accepted,
                              "statuses": {ft: record["status"] for ft, record in records.items()}},
            "history": {"physical": 8 + physical, "invalidated": 8, "accepted": accepted},
            "replacement_bundle": state["replacement_4_final"]["bundle_digest"]}


def _receipt_summary(content: bytes) -> dict[str, Any] | None:
    matches = SUMMARY_RE.findall(content[FAILED3_RECEIPT[0]:])
    if not matches: return None
    if len(matches) != 1: raise EvidenceError("receipt summary count invalid")
    try: value = json.loads(matches[0])
    except json.JSONDecodeError as exc: raise EvidenceError("receipt summary JSON invalid") from exc
    if type(value) is not dict or matches[0].decode() != canonical(value): raise EvidenceError("receipt summary encoding invalid")
    _validate_aggregate(value)
    return value


def _validate_aggregate(value: dict[str, Any]) -> None:
    if set(value) != {"disposition", "original", "replacement_1", "replacement_2", "replacement_3", "replacement_4", "history", "replacement_bundle"}: raise EvidenceError("receipt summary schema invalid")
    original, first, second, prior, replacement, history = value["original"], value["replacement_1"], value["replacement_2"], value["replacement_3"], value["replacement_4"], value["history"]
    if type(value["disposition"]) is not str or type(value["replacement_bundle"]) is not str: raise EvidenceError("receipt summary scalar invalid")
    if type(original) is not dict or original != {"physical": 4, "invalidated": 4, "accepted": 0} or any(type(v) is not int for v in original.values()): raise EvidenceError("receipt original counters invalid")
    if first != {"physical": 1, "invalidated": 1, "accepted": 0} or any(type(first[k]) is not int for k in first): raise EvidenceError("receipt first failed-set invalid")
    failed_statuses = {"FT-1": "FAILED", "FT-2": "UNUSED", "FT-3": "UNUSED", "FT-4": "UNUSED"}
    if second != {"physical": 1, "invalidated": 1, "accepted": 0, "statuses": failed_statuses} or any(type(second[k]) is not int for k in ("physical", "invalidated", "accepted")): raise EvidenceError("receipt second failed-set invalid")
    prior_statuses = {"FT-1": "ACCEPTED", "FT-2": "FAILED", "FT-3": "UNUSED", "FT-4": "UNUSED"}
    if prior != {"physical": 2, "mechanical_accepted": 1, "failed": 1, "governance_accepted": 0, "statuses": prior_statuses} or any(type(prior[k]) is not int for k in ("physical", "mechanical_accepted", "failed", "governance_accepted")): raise EvidenceError("receipt third failed-set invalid")
    if type(replacement) is not dict or set(replacement) != {"physical", "accepted", "statuses"}: raise EvidenceError("receipt replacement schema invalid")
    statuses = replacement["statuses"]
    if type(statuses) is not dict or set(statuses) != set(PUBLIC_FIXTURES) or any(type(v) is not str for v in statuses.values()): raise EvidenceError("receipt statuses invalid")
    physical = sum(v in {"DISPATCHED", "ACCEPTED", "FAILED", "INDETERMINATE"} for v in statuses.values()); accepted = sum(v == "ACCEPTED" for v in statuses.values())
    if any(type(replacement[k]) is not int for k in ("physical", "accepted")) or (replacement["physical"], replacement["accepted"]) != (physical, accepted): raise EvidenceError("receipt replacement counters invalid")
    expected_history = {"physical": 8 + physical, "invalidated": 8, "accepted": accepted}
    if type(history) is not dict or any(type(v) is not int for v in history.values()) or history != expected_history: raise EvidenceError("receipt history invalid")
    if value["disposition"] != ("PASS" if (physical, accepted) == (4, 4) else "INCOMPLETE_OR_FAIL"): raise EvidenceError("receipt disposition invalid")


def _monotonic(previous: dict[str, Any] | None, current: dict[str, Any]) -> None:
    if previous is None: return
    _validate_aggregate(current)
    allowed = {"UNUSED": {"UNUSED", "RESERVED"}, "RESERVED": {"RESERVED", "DISPATCHED"},
               "DISPATCHED": {"DISPATCHED", "ACCEPTED", "FAILED", "INDETERMINATE"},
               "ACCEPTED": {"ACCEPTED"}, "FAILED": {"FAILED"}, "INDETERMINATE": {"INDETERMINATE"}}
    try:
        if any(canonical(previous[k]) != canonical(current[k]) for k in ("original", "replacement_1", "replacement_2", "replacement_3")) or previous["replacement_bundle"] != current["replacement_bundle"]: raise KeyError
        old, new = previous["replacement_4"]["statuses"], current["replacement_4"]["statuses"]
        if set(old) != set(PUBLIC_FIXTURES) or set(new) != set(PUBLIC_FIXTURES): raise KeyError
        if any(new[ft] not in allowed[old[ft]] for ft in PUBLIC_FIXTURES): raise KeyError
    except (KeyError, TypeError): raise EvidenceError("receipt progress rollback/tamper invalid") from None


def _render_receipt(state: dict[str, Any], prefix: bytes) -> bytes:
    records = state["replacement_4_final"]["records"]; aggregate = summary(state)
    lines = ["", "", "# Amendment 4 evidence disposition", "",
             "The complete prior receipt above is retained byte-for-byte; all four older evidence generations are invalidated and cannot dispatch.", "",
             f"- Historical accounting: `{aggregate['history']['physical']} physical / {aggregate['history']['invalidated']} invalidated / {aggregate['history']['accepted']} final accepted`",
             f"- Final-set verdict: `{aggregate['disposition']}`", "", "## Amendment 4 final scenarios", ""]
    for ft_id, record in records.items():
        lines.extend([f"### {ft_id} final", "", f"- Status: `{record['status']}`", f"- Lineage: `{record['lineage_key']}`"])
        for field in ("attempt_id", "model", "endpoint", "reserved_at", "dispatched_at", "finished_at"):
            if field in record: lines.append(f"- {field}: `{record[field]}`")
        if "request" in record: lines.extend(["", "Canonical request:", "", "```json", canonical(record["request"]), "```"])
        if "response" in record: lines.extend(["", "Validated assistant JSON:", "", "```json", canonical(record["response"]), "```"])
        if "candidate_response" in record: lines.extend(["", "Safe parsed candidate (semantic failure only):", "", "```json", canonical(record["candidate_response"]), "```"])
        if "error" in record: lines.append(f"- Safe error: `{record['error']}`")
        lines.append("")
    lines.extend(["<!-- PROJECT_OPERATIONS_SKILL_AMENDMENT_4_SUMMARY", canonical(aggregate), "-->", ""])
    appendix = "\n".join(lines).encode(); assert_safe(appendix.decode())
    return prefix + appendix


def receipt_bytes(state: dict[str, Any], receipt_path: Path) -> bytes:
    content = receipt_path.read_bytes(); previous = _receipt_summary(content)
    if previous is None: raise EvidenceError("migrated receipt anchor missing")
    _monotonic(previous, summary(state)); return _render_receipt(state, _prefix(receipt_path))


def validate_receipt(state: dict[str, Any], receipt_path: Path) -> None:
    content = receipt_path.read_bytes(); marker = _receipt_summary(content)
    if marker != summary(state) or content != receipt_bytes(state, receipt_path): raise EvidenceError("state/receipt coherence invalid")


def migrate_amendment4(*, state_path: Path = STATE, receipt_path: Path = RECEIPT, lock_path: Path = LOCK,
                     state_temp: Path = STATE_TEMP, receipt_temp: Path = RECEIPT_TEMP,
                     run_preflight: bool = True) -> dict[str, Any]:
    if run_preflight: preflight()
    raw_state, raw_receipt = state_path.read_bytes(), receipt_path.read_bytes()
    if (len(raw_state), sha(raw_state)) != FAILED3_STATE or (len(raw_receipt), sha(raw_receipt)) != FAILED3_RECEIPT:
        raise EvidenceError("failed evidence pin mismatch")
    skill = digest(SKILL.read_bytes()); bundle = bundle_digest(BUNDLE_PATHS)
    state = new_v5(raw_state, bundle, skill)
    with runtime_lock(lock_path):
        atomic_bytes(state_path, state_temp, (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode())
        atomic_bytes(receipt_path, receipt_temp, _render_receipt(state, raw_receipt))
    load_v5(state_path, bundle, skill); validate_receipt(state, receipt_path)
    return summary(state)


def run(*, transport: Callable[..., str] = http_transport, state_path: Path = STATE, receipt_path: Path = RECEIPT,
        lock_path: Path = LOCK, state_temp: Path = STATE_TEMP, receipt_temp: Path = RECEIPT_TEMP,
        provider: tuple[str, str, str] | None = None, attempt_factory: Callable[[], str] = lambda: uuid.uuid4().hex,
        before_dispatch: Callable[[str], None] = lambda _ft: None, after_transport: Callable[[str], None] = lambda _ft: None,
        run_preflight: bool = True) -> dict[str, Any]:
    if run_preflight: preflight()
    if any(path.exists() for path in (lock_path, state_temp, receipt_temp)): raise EvidenceError("runtime residue exists")
    key, endpoint, model = provider or resolve_provider()
    skill_text = SKILL.read_text(encoding="utf-8"); skill = digest(SKILL.read_bytes()); bundle = bundle_digest(BUNDLE_PATHS)
    state = load_v5(state_path, bundle, skill); validate_receipt(state, receipt_path)
    for ft_id in PUBLIC_FIXTURES:
        request = build_request(ft_id, skill_text); attempt = attempt_factory()
        state = reserve(state_path=state_path, state_temp=state_temp, lock_path=lock_path, bundle=bundle, skill=skill,
                        ft_id=ft_id, attempt_id=attempt, request=request, model=model, endpoint=endpoint)
        atomic_bytes(receipt_path, receipt_temp, receipt_bytes(state, receipt_path))
        before_dispatch(ft_id)
        state = dispatch(state_path=state_path, state_temp=state_temp, lock_path=lock_path, bundle=bundle, skill=skill, ft_id=ft_id)
        atomic_bytes(receipt_path, receipt_temp, receipt_bytes(state, receipt_path))
        try:
            raw = transport(endpoint=endpoint, key=key, model=model, request_object=request)
            after_transport(ft_id)
        except Exception as exc:
            error = str(exc) if isinstance(exc, ProviderFailure) else "provider_indeterminate_failure"
            state = finish(state_path=state_path, state_temp=state_temp, lock_path=lock_path, bundle=bundle, skill=skill,
                           ft_id=ft_id, status="INDETERMINATE", error=error)
            atomic_bytes(receipt_path, receipt_temp, receipt_bytes(state, receipt_path)); raise EvidenceError(error) from None
        try: response = validate_response(ft_id, raw)
        except SemanticError as exc:
            state = finish(state_path=state_path, state_temp=state_temp, lock_path=lock_path, bundle=bundle, skill=skill,
                           ft_id=ft_id, status="FAILED", error=str(exc), candidate_response=exc.candidate)
            atomic_bytes(receipt_path, receipt_temp, receipt_bytes(state, receipt_path)); raise
        except EvidenceError as exc:
            state = finish(state_path=state_path, state_temp=state_temp, lock_path=lock_path, bundle=bundle, skill=skill,
                           ft_id=ft_id, status="FAILED", error=str(exc))
            atomic_bytes(receipt_path, receipt_temp, receipt_bytes(state, receipt_path)); raise
        state = finish(state_path=state_path, state_temp=state_temp, lock_path=lock_path, bundle=bundle, skill=skill,
                       ft_id=ft_id, status="ACCEPTED", response=response)
        atomic_bytes(receipt_path, receipt_temp, receipt_bytes(state, receipt_path))
    validate_receipt(state, receipt_path); aggregate = summary(state)
    if aggregate["history"] != {"physical": 12, "invalidated": 8, "accepted": 4}: raise EvidenceError("final history is not 12/8/4")
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--json", action="store_true"); parser.add_argument("--migrate-amendment-4", action="store_true"); args = parser.parse_args()
    try: result = migrate_amendment4() if args.migrate_amendment_4 else run()
    except EvidenceError as exc:
        error = str(exc)
        try: assert_safe(error)
        except EvidenceError: error = "evidence failure (detail suppressed)"
        print(json.dumps({"verdict": "FAIL", "error": error}) if args.json else f"FAIL: {error}"); return 1
    except Exception:
        error = "operational failure (detail suppressed)"
        print(json.dumps({"verdict": "FAIL", "error": error}) if args.json else f"FAIL: {error}"); return 1
    print(json.dumps(result) if args.json else f"PASS: {result}"); return 0


if __name__ == "__main__": raise SystemExit(main())
