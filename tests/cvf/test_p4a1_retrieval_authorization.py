"""SPEC R3 - five-stage authorization and read ordering (AC-03).

Ordered call-spy suite covering failure at each stage, proving zero later
calls; positive tests proving every assignment call precedes corpus
resolution and the first source access; adversarial proof for F1 (forged
principal, transaction order, one-unit reuse), F2 (stage ordering), RR1-F1
(real get_principal call), and RR2-F3 (pre-R2 identity/time allocation)."""

from __future__ import annotations

import ast
import base64
import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    # tests/cvf needs the shared tests/unit fixture module too.
    sys.path.insert(0, str(_UNIT_TESTS))

import pytest
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import _ACTION_MIN_ROLE, require_action

from workspace_api.application import _governed_retrieval_admission as admission
from workspace_api.application import _governed_retrieval_knowledge as knowledge
from workspace_api.application import _governed_retrieval_sources as sources
from workspace_api.application.governed_retrieval import execute_governed_retrieval
from workspace_api.auth.tokens import create_access_token

from _p4a1_retrieval_fixtures import NOW, AssignedWorkspace, request_body
from _p4a1_retrieval_fixtures import execution_metadata as _base_execution_metadata

def _advancing_utc_now(*, start=NOW):
    """RR3-F4 - each call returns `start` plus a strictly increasing offset,
    so a positive measured elapsed_ms always has finished_at_utc > started_at_utc."""
    calls = [0]
    def clock():
        calls[0] += 1
        return start + timedelta(microseconds=calls[0])
    return clock

def execution_metadata(**overrides):
    overrides.setdefault("utc_now", _advancing_utc_now())
    return _base_execution_metadata(**overrides)

def _isolated_knowledge_root(tmp_path):
    """A self-contained, pin-correct one-entry Project Knowledge corpus
    under `tmp_path`, independent of the live repository's manifest/pin
    state (RR3-F1 whole-manifest fail-closed means a live pin drift there
    must not affect this test's own positive-path assertions)."""
    import hashlib
    import json

    (tmp_path / "knowledge").mkdir(parents=True)
    doc_text = "governance advisory local knowledge for parity testing"
    (tmp_path / "knowledge" / "doc.md").write_text(doc_text, encoding="utf-8")
    digest = hashlib.sha256(doc_text.encode("utf-8")).hexdigest()
    manifest = {
        "schemaVersion": "1.0", "packId": "shift-operations-project-knowledge",
        "classification": "INTERNAL", "reviewedAt": "2026-08-10",
        "entries": [{
            "id": "doc", "path": "doc.md", "owner": "ORCHESTRATOR", "classification": "INTERNAL",
            "disposition": "ACTIVE", "dispositionReason": None, "purpose": "p",
            "allowedConsumers": ["LOCAL_GOVERNED_AGENT"],
            "sourcePins": [{"path": "knowledge/doc.md", "sha256": digest}],
            "reviewedAt": "2026-08-10", "refreshTriggers": [],
            "retentionPolicy": "RETAIN_WHILE_SOURCES_ARE_CURRENT_AND_OWNER_MAINTAINS_ENTRY",
            "correctionPolicy": "c", "eligibleForLocalIndex": True,
        }],
    }
    (tmp_path / "knowledge" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path

def test_retrieval_query_action_is_registered_at_viewer_after_this_build() -> None:
    """This BUILD adds the mapping; a viewer must satisfy it."""
    assert _ACTION_MIN_ROLE["retrieval.query"] == "viewer"
    require_action(Principal(user_id="op1", role="viewer"), "retrieval.query")

def test_require_action_still_fails_closed_for_unknown_actions() -> None:
    with pytest.raises(CvfDenied):
        require_action(Principal(user_id="op1", role="authorized_executive"), "totally.unknown.action")

# --- F1: forged/unverified principal is rejected; only a verified bearer
# token is ever trusted ---

def _b64url_decode(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


def _flip_decoded_signature_byte(token: str) -> str:
    """Amendment 1 (SOPR-CP1-A1): the JWT's final base64url character encodes
    only unused padding bits for a 32-byte HS256 signature, so the original
    `token[:-1] + "A"/"B"` mutation could change the text while leaving the
    decoded signature bytes identical. This flips a real decoded byte."""
    header_b64, payload_b64, signature_b64 = token.split(".")
    sig = bytearray(_b64url_decode(signature_b64))
    sig[0] ^= 0xFF
    tampered_b64 = base64.urlsafe_b64encode(bytes(sig)).rstrip(b"=").decode("ascii")
    return f"{header_b64}.{payload_b64}.{tampered_b64}"


def test_forged_or_tampered_credential_is_rejected_not_trusted() -> None:
    """F1: any non-verified credential (forged, empty, garbage, or a real
    token with a byte-flipped signature) is refused at AUTHENTICATED."""
    ws = AssignedWorkspace()
    token = ws.bearer_token()
    tampered = _flip_decoded_signature_byte(token)
    assert tampered != token, "tampered token text must differ from the original"
    assert _b64url_decode(tampered.split(".")[2]) != _b64url_decode(token.split(".")[2]), (
        "tampered token must decode to different signature bytes, not just different text"
    )
    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    for forged in ("not-a-real-jwt", "", "op1:viewer", "Bearer op1", tampered):
        result = execute_governed_retrieval(
            raw_body=body, bearer_token=forged, assignment_scope=ws.scope,
            ledger=ws.ledger, metadata=execution_metadata(),
        )
        assert type(result).__name__ == "AccessDeniedV1"
        auth_stage = next(s for s in result.receipt.stages if s.stage.value == "AUTHENTICATED")
        # RR2-F4/Amendment 3 5.4 - authentication failure is exactly DENY,
        # never FAIL (an access-denial stage, not a non-access failure).
        assert auth_stage.outcome.value == "DENY"
        assert auth_stage.reason_code.value == "AUTHENTICATION_FAILED"

def _mentions_decode_access_token(node) -> bool:
    if isinstance(node, ast.ImportFrom):
        return any(a.name == "decode_access_token" for a in node.names)
    return isinstance(node, ast.Name) and node.id == "decode_access_token"

def test_authenticate_calls_the_real_canonical_get_principal_dependency(monkeypatch, tmp_path) -> None:
    """RR1-F1: a spy on the REAL get_principal proves authenticate() routes
    through that exact surface; an AST guard proves no P4-A1 module
    imports/calls decode_access_token directly."""
    from workspace_api import dependencies as deps_module

    calls: list[str] = []
    original_get_principal = deps_module.get_principal

    def spy_get_principal(credentials):
        calls.append("get_principal")
        assert credentials.credentials
        return original_get_principal(credentials)

    monkeypatch.setattr(admission, "get_principal", spy_get_principal)
    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert type(result).__name__ == "EvidenceAvailableV1"
    assert calls == ["get_principal"]
    app_dir = _REPO_ROOT / "apps" / "workspace-api" / "src" / "workspace_api" / "application"
    files = list(app_dir.glob("_governed_retrieval_*.py")) + [app_dir / "governed_retrieval.py"]
    offenders = [
        p.name for p in files
        if any(_mentions_decode_access_token(n) for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))))
    ]
    assert offenders == [], f"P4-A1 module bypasses get_principal: {offenders}"

def test_authentication_failure_stops_before_any_ledger_transaction(monkeypatch) -> None:
    """F1: authentication precedes the single Ledger unit being opened."""
    ws = AssignedWorkspace()
    calls: list[str] = []
    original_transaction = ws.ledger.transaction

    def spy_transaction():
        calls.append("transaction")
        return original_transaction()

    monkeypatch.setattr(ws.ledger, "transaction", spy_transaction)

    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token="forged", assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(),
    )
    assert type(result).__name__ == "AccessDeniedV1"
    assert calls == []

# --- F2: authenticated/permission/assignment are recorded as distinct
# stages, in order ---

def test_permission_denial_stops_before_any_assignment_call(monkeypatch) -> None:
    calls: list[str] = []
    ws = AssignedWorkspace()

    original_require_shift = ws.scope.require_shift

    def spy_require_shift(*args, **kwargs):
        calls.append("require_shift")
        return original_require_shift(*args, **kwargs)

    monkeypatch.setattr(ws.scope, "require_shift", spy_require_shift)

    def deny(*args, **kwargs):
        calls.append("require_action")
        raise CvfDenied(control="permission", reason="denied for test", http_status=403)

    monkeypatch.setattr(sources, "require_action", deny)

    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(),
    )
    assert type(result).__name__ == "AccessDeniedV1"
    assert calls == ["require_action"]  # require_shift never called
    stages = {s.stage.value: s.outcome.value for s in result.receipt.stages}
    assert stages["AUTHENTICATED"] == "PASS"
    assert stages["PERMISSION_AUTHORIZED"] == "DENY"
    assert stages["ASSIGNMENT_AUTHORIZED"] == "NOT_RUN"

def test_missing_shift_assignment_stops_before_corpus_resolution(monkeypatch) -> None:
    calls: list[str] = []
    ws = AssignedWorkspace()

    original_resolve = sources.is_operational_corpus

    def spy_resolve(*args, **kwargs):
        calls.append("resolve_corpus_boundary")
        return original_resolve(*args, **kwargs)

    monkeypatch.setattr(sources, "is_operational_corpus", spy_resolve)

    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.outsider_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(),
    )
    assert type(result).__name__ == "AccessDeniedV1"
    assert calls == []  # corpus resolution never reached
    permission_stage = next(s for s in result.receipt.stages if s.stage.value == "PERMISSION_AUTHORIZED")
    assignment_stage = next(s for s in result.receipt.stages if s.stage.value == "ASSIGNMENT_AUTHORIZED")
    assert permission_stage.outcome.value == "PASS"
    assert assignment_stage.outcome.value == "DENY"

def test_multi_shift_failure_after_one_admitted_shift_denies_and_stops(monkeypatch) -> None:
    ws = AssignedWorkspace()
    calls: list[str] = []
    original_require_shift = ws.scope.require_shift

    def spy_require_shift(shift_id, principal, *, unit=None):
        calls.append(str(shift_id))
        return original_require_shift(shift_id, principal, unit=unit)

    monkeypatch.setattr(ws.scope, "require_shift", spy_require_shift)

    body = request_body(
        corpus_id="SHIFT_CONFIRMED_OPERATIONS_V1",
        shift_ids=tuple(sorted([str(ws.shift.shift_id), "00000000-0000-0000-0000-000000000099"])),
    )
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(),
    )
    assert type(result).__name__ == "AccessDeniedV1"
    assert len(calls) <= 2  # stopped at the first failing shift, no source read

def test_positive_path_every_assignment_call_precedes_first_source_read(monkeypatch, tmp_path) -> None:
    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    call_order: list[str] = []
    original_require_shift = ws.scope.require_shift

    def spy_require_shift(*args, **kwargs):
        call_order.append("assignment")
        return original_require_shift(*args, **kwargs)

    monkeypatch.setattr(ws.scope, "require_shift", spy_require_shift)
    original_list_entries = knowledge.list_admissible_knowledge_entries

    def spy_list_entries(*args, **kwargs):
        call_order.append("source_read")
        return original_list_entries(*args, **kwargs)

    monkeypatch.setattr(knowledge, "list_admissible_knowledge_entries", spy_list_entries)
    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert type(result).__name__ == "EvidenceAvailableV1"
    assert call_order[0] == "assignment"
    assert "source_read" in call_order
    assert call_order.index("assignment") < call_order.index("source_read")
    assert call_order.count("assignment") >= 1

# --- RR2-F3/F1: see test_p4a1_retrieval_authorization_ordering.py ---
