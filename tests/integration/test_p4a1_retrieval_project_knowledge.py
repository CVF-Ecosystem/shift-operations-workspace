"""F4/RR1-F3/RR3-F1-F3 companion of test_p4a1_retrieval_ledger_parity.py
(Amendment 5 test-only structural split): whole-manifest fail-closed on a
malformed entry, the initial ordinary-exception boundary and symlinked-base
rejection, and strict owner/retention/consumer admission rules."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS))

import pytest

from governed_retrieval.result_models import CorpusUnavailableV1

from workspace_api.application.governed_retrieval import execute_governed_retrieval

from _p4a1_retrieval_fixtures import NOW, AssignedWorkspace, request_body
from _p4a1_retrieval_fixtures import execution_metadata as _base_execution_metadata

def _advancing_utc_now(*, start=NOW):
    """RR3-F4 - each call returns `start` plus a strictly increasing offset."""
    calls = [0]
    def clock():
        calls[0] += 1
        return start + timedelta(microseconds=calls[0])
    return clock

def execution_metadata(**overrides):
    overrides.setdefault("utc_now", _advancing_utc_now())
    return _base_execution_metadata(**overrides)

def _isolated_knowledge_root(tmp_path):
    """A self-contained, pin-correct one-entry corpus, independent of the
    live repo's manifest/pin state; `path` relative to `knowledge/`,
    `sourcePins[].path` relative to the repository root."""
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

# --- F4: real, non-fabricated owner and retention from manifest truth ---

def test_one_valid_one_malformed_entry_fails_whole_corpus_no_partial_candidate(tmp_path) -> None:
    """Amendment 4 5.5.1-2: a manifest with one otherwise-valid entry plus
    one entry invalidated by missing owner, empty/wrong retention, wrong
    owner, malformed consumer, malformed pin, duplicate id/path, or unsafe
    (absolute/parent/symlink) path each raises KnowledgeCorpusUnavailable
    for the WHOLE manifest - the valid entry is never exposed as a partial
    candidate; RR3-F1 applies identically to a lone single-entry manifest."""
    from workspace_api.application._governed_retrieval_knowledge import (
        KnowledgeCorpusUnavailable, _admissible_entries,
    )

    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "doc.md").write_text("x", encoding="utf-8")
    (tmp_path / "secret.md").write_text("outside", encoding="utf-8")
    valid = _pk_entry(id="valid", path="doc.md", sourcePins=[{"path": "knowledge/doc.md", "sha256": _sha256_of("x")}])
    no_owner = _pk_entry(id="bad0", path="doc.md")
    del no_owner["owner"]
    bad_variants = [
        no_owner,
        _pk_entry(id="bad0b", path="doc.md", retentionPolicy=""),
        _pk_entry(id="bad1", path="doc.md", owner="NOT_ALLOWLISTED"),
        _pk_entry(id="bad2", path="doc.md", allowedConsumers=[{"x": 1}]),
        _pk_entry(id="bad3", path="doc.md", sourcePins=[{"path": "doc.md", "sha256": "not-hex"}]),
        _pk_entry(id="valid", path="dup.md"),  # duplicate id with the valid entry
        _pk_entry(id="bad5", path="../secret.md"),
        _pk_entry(id="bad6", path=str(tmp_path / "secret.md")),
        _pk_entry(id="../escaped-id", path="doc2.md"),
        _pk_entry(id="bad8", path="doc.md", sourcePins=[{"path": "../secret.md", "sha256": "y"}]),
    ]
    for bad in bad_variants:
        with pytest.raises(KnowledgeCorpusUnavailable):
            _admissible_entries({"classification": "INTERNAL", "entries": [valid, bad]}, tmp_path)
        with pytest.raises(KnowledgeCorpusUnavailable):  # lone single-entry manifest, same rule
            _admissible_entries({"classification": "INTERNAL", "entries": [bad]}, tmp_path)
    try:  # descendant/in-root symlink escape, single-entry manifest
        (tmp_path / "knowledge" / "linked.md").symlink_to(tmp_path / "secret.md")
        with pytest.raises(KnowledgeCorpusUnavailable):
            _admissible_entries({"classification": "INTERNAL", "entries": [_pk_entry(path="linked.md")]}, tmp_path)
    except OSError:
        pass  # symlink unsupported here; the other escape shapes above still prove RR1-F3

def _sha256_of(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def test_initial_exception_boundary_and_symlinked_base_rejection(monkeypatch, tmp_path) -> None:
    """Amendment 4 5.5.3-4: unreadable manifest / injected `refine` or
    `construct_retrieval_contract` exception -> typed CORPUS_UNAVAILABLE (an
    injected BaseException is not swallowed); a symlinked `knowledge` base
    is rejected whether it resolves inside or outside, with a
    platform-neutral monkeypatched seam for systems without symlinks."""
    from workspace_api.application import _governed_retrieval_sources as sources_mod
    from workspace_api.application import _governed_retrieval_knowledge as knowledge_mod
    from workspace_api.application._governed_retrieval_knowledge import _resolve_contained

    ws = AssignedWorkspace()
    body = request_body(query="governance", shift_ids=(str(ws.shift.shift_id),))

    def run(root):
        return execute_governed_retrieval(
            raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
            ledger=ws.ledger, metadata=execution_metadata(repository_root=root),
        )

    assert isinstance(run(tmp_path / "empty"), CorpusUnavailableV1)  # no manifest.json
    monkeypatch.setattr(knowledge_mod, "refine", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert isinstance(run(_isolated_knowledge_root(tmp_path / "a")), CorpusUnavailableV1)
    monkeypatch.undo()
    monkeypatch.setattr(
        knowledge_mod, "construct_retrieval_contract", lambda *a, **k: (_ for _ in ()).throw(ValueError("boom")),
    )
    assert isinstance(run(_isolated_knowledge_root(tmp_path / "b")), CorpusUnavailableV1)
    monkeypatch.undo()

    class _Escaping(BaseException):
        pass

    monkeypatch.setattr(sources_mod.knowledge, "list_admissible_knowledge_entries", lambda *a, **k: (_ for _ in ()).throw(_Escaping()))
    with pytest.raises(_Escaping):
        run(_isolated_knowledge_root(tmp_path / "c"))
    monkeypatch.undo()

    real_dir = tmp_path / "real_knowledge"
    real_dir.mkdir()
    (real_dir / "doc.md").write_text("x", encoding="utf-8")
    linked_base = tmp_path / "knowledge"
    try:
        linked_base.symlink_to(real_dir)
        assert _resolve_contained(linked_base, "doc.md") is None
    except OSError:
        pass  # symlink unsupported; the monkeypatched seam below still proves the check
    from pathlib import Path as _Path

    original_is_symlink, calls = _Path.is_symlink, {"n": 0}

    def fake_is_symlink(self):
        calls["n"] += 1
        return calls["n"] == 1  # only the base (first check) reports True

    monkeypatch.setattr(_Path, "is_symlink", fake_is_symlink)
    other_root = tmp_path / "other"
    other_root.mkdir()
    assert _resolve_contained(other_root, "doc.md") is None
    monkeypatch.setattr(_Path, "is_symlink", original_is_symlink)

def _pk_entry(**overrides) -> dict:
    """RR2-F2 - exact _ENTRY_FIELDS shape, so failures below prove
    containment/owner/consumer logic, not an incidental shape mismatch."""
    from workspace_api.application._governed_retrieval_knowledge import _ACTIVE_RETENTION_POLICY

    e = {
        "id": "x", "path": "doc.md", "owner": "ORCHESTRATOR", "classification": "INTERNAL",
        "disposition": "ACTIVE", "dispositionReason": None, "purpose": "p",
        "allowedConsumers": ["LOCAL_GOVERNED_AGENT"], "sourcePins": [{"path": "doc.md", "sha256": "y"}],
        "reviewedAt": "2026-08-10", "refreshTriggers": [], "retentionPolicy": _ACTIVE_RETENTION_POLICY,
        "correctionPolicy": "c", "eligibleForLocalIndex": True,
    }
    e.update(overrides)
    return e

def test_owner_retention_and_consumer_admission_rules_are_strict(tmp_path) -> None:
    """RR1-F3/RR2-F2/RR2-F6: only the EXACT active-retention literal counts
    as active AND owner must be in the exact OWNERS allowlist; unknown owner
    and malformed (unhashable) consumer are rejected via `_entry_admissible`
    - never a raw TypeError, never accepted merely for being non-empty
    (whole-manifest fail-closed coverage for these same classes lives in
    test_one_valid_one_malformed_entry_fails_whole_corpus_no_partial_candidate)."""
    from workspace_api.application._governed_retrieval_knowledge import (
        _ACTIVE_RETENTION_POLICY, _entry_admissible, _has_active_owner_and_retention,
    )

    assert _has_active_owner_and_retention({"owner": "ORCHESTRATOR", "retentionPolicy": _ACTIVE_RETENTION_POLICY}) is True
    for bad in (
        {"owner": "x", "retentionPolicy": _ACTIVE_RETENTION_POLICY}, {"owner": "", "retentionPolicy": _ACTIVE_RETENTION_POLICY},
        {"owner": "ORCHESTRATOR", "retentionPolicy": "y"}, {"owner": "ORCHESTRATOR", "retentionPolicy": "DELETED"},
        {"owner": "ORCHESTRATOR", "retentionPolicy": ""}, {"owner": "ORCHESTRATOR"},
    ):
        assert _has_active_owner_and_retention(bad) is False

    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "doc.md").write_text("x", encoding="utf-8")
    assert _entry_admissible(_pk_entry(path="doc.md", allowedConsumers=[{"x": 1}]), tmp_path) is False
