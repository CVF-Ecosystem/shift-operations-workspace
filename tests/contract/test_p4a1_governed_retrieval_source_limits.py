"""SPEC F10 companion of test_p4a1_governed_retrieval_schema.py (Amendment 5
test-only structural split): manifest-entry and document-length boundaries at
N/N+1, never a silent truncation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

def _minimal_manifest_entries(n: int) -> list[dict]:
    return [{
        "id": f"e{i}", "path": f"e{i}.md", "owner": "ORCHESTRATOR", "classification": "INTERNAL",
        "disposition": "ACTIVE", "eligibleForLocalIndex": True, "retentionPolicy": "RETAIN_WHILE_CURRENT",
        "allowedConsumers": ["LOCAL_GOVERNED_AGENT"], "sourcePins": [],
    } for i in range(n)]

def test_manifest_entry_boundary_99_100_101_no_silent_truncation(tmp_path) -> None:
    """The 100-entry count ceiling is enforced by `_load_manifest_within_ceiling`
    BEFORE any per-entry admission check, independent of entry validity - so
    at/below 100 (RR3-F1 whole-manifest fail-closed) these deliberately
    minimal/malformed entries correctly raise KnowledgeCorpusUnavailable
    (never ManifestEntryLimitExceeded), and above 100 the ceiling always
    fires first regardless of entry shape."""
    from workspace_api.application._governed_retrieval_knowledge import (
        KnowledgeCorpusUnavailable, ManifestEntryLimitExceeded, list_admissible_knowledge_entries,
    )

    (tmp_path / "knowledge").mkdir()
    for n, expected in ((99, KnowledgeCorpusUnavailable), (100, KnowledgeCorpusUnavailable), (101, ManifestEntryLimitExceeded)):
        manifest = {
            "schemaVersion": "1.0", "packId": "shift-operations-project-knowledge",
            "classification": "INTERNAL", "reviewedAt": "2026-08-10", "entries": _minimal_manifest_entries(n),
        }
        (tmp_path / "knowledge" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(expected):
            list_admissible_knowledge_entries(tmp_path)

def test_document_length_boundary_65535_65536_65537_no_silent_truncation(tmp_path) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "unit"))
    from _p4a1_retrieval_fixtures import NOW, control_bundle, dedupe_context, quarantine_route
    from workspace_api.application._governed_retrieval_knowledge import (
        DocumentLimitExceeded, ProjectKnowledgeExecutionContext, build_ready_contract,
    )

    (tmp_path / "knowledge").mkdir()
    ctx = ProjectKnowledgeExecutionContext(
        repository_root=tmp_path, control_bundle=control_bundle(), now=NOW, dedupe_context=dedupe_context(NOW),
        quarantine_route=quarantine_route(), anchor_shift=None, anchor_principal_user_id="",
    )
    for length, should_raise in ((65535, False), (65536, False), (65537, True)):
        (tmp_path / "knowledge" / "doc.md").write_text("a" * length, encoding="utf-8")
        entry = {"id": "doc", "path": "doc.md", "owner": "x", "retentionPolicy": "RETAIN"}
        if should_raise:
            with pytest.raises(DocumentLimitExceeded):
                build_ready_contract(entry, ctx)
        else:
            build_ready_contract(entry, ctx)  # may return None (refinery quality gate); must not raise
