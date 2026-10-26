from __future__ import annotations

import copy
from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

from cvf_runtime.identity import Principal
from workspace_api.application.proactive_source import TrustedSourceScope, query_source
from workspace_api.application.proactive_source_receipt import (
    P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST, canonical_json,
    emit_source_refused, validate_source_receipt,
)

from p5a2_scoped_source_helpers import FixtureCoverage, oracle, public_ledger

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from invariant_family_contract import canonical_digest, generate_mutations  # noqa: E402


def _runtime_matrix():
    # Root binds the planned ownership matrix before the focused Stage A run.
    path = ROOT / "docs/cvf/invariants/p5a2-scoped-source-outcomes.json"
    assert canonical_digest(path) == P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST
    return json.loads(path.read_text(encoding="utf-8"))


def _native_samples():
    case = oracle()["cases"][0]
    seed = case["coverage_seed"]
    from datetime import datetime
    start, end, as_of = (datetime.fromisoformat(seed[k].replace("Z", "+00:00"))
                         for k in ("query_start", "query_end", "run_as_of"))
    ready = query_source(
        Principal(user_id=seed["actor_id"], role="operator"),
        TrustedSourceScope(seed["scope_id"], seed["actor_id"], seed["instance_id"]),
        start, end, as_of, public_ledger(), FixtureCoverage(case),
    )
    assert ready.payload is not None and ready.receipt == case["expected_receipt"]
    refused = emit_source_refused("ACCESS_DENIED")
    assert refused == oracle()["refusals"][0]["expected_receipt"]
    return ready.receipt, refused


def test_actual_emitters_and_native_consumer_reject_complete_matrix_mutations():
    matrix = _runtime_matrix()
    ready, refused = _native_samples()
    totals = {}
    for shape_id, sample in (("P5A2_SOURCE_READY", ready), ("P5A2_SOURCE_REFUSED", refused)):
        validate_source_receipt(sample)
        mutations = generate_mutations(matrix, shape_id, sample)
        assert mutations
        for mutation in mutations:
            with pytest.raises(ValueError, match="source|receipt|coverage|report|candidate|selected|manifest|count|mode|version|refusal|timestamp"):
                validate_source_receipt(mutation.payload)
        totals[shape_id] = len(mutations)
    assert all(count > 0 for count in totals.values())


@pytest.mark.parametrize("change", [
    "header", "count", "lineage", "coverage_digest", "source_bytes",
    "selected_created", "selected_cutoff", "malformed_ref", "assignment_uuid",
    "calendar", "candidate_future", "nonpositive_version", "selected_outside_window",
    "ref_bool_version", "ref_float_version", "ref_string_version",
])
def test_native_consumer_rejects_parsed_manifest_corruption(change):
    ready, _ = _native_samples()
    wrong = copy.deepcopy(ready)
    manifest = json.loads(wrong["canonical_manifest"])
    if change == "header":
        manifest["actor_id"] = "OTHER"
    elif change == "count":
        manifest["eligible_shifts"].pop()
    elif change == "lineage":
        manifest["selected_reports"][0]["report_id"] = "other"
    elif change == "coverage_digest":
        manifest["coverage_manifest_digest"] = "invalid"
    elif change == "selected_created":
        manifest["selected_reports"][0]["created_at"] = "2026-01-02T00:00:00Z"
    elif change == "selected_cutoff":
        manifest["selected_reports"][0]["generated_from_cutoff"] = "2026-01-01T01:00:00Z"
    elif change == "malformed_ref":
        manifest["selected_reports"][0]["source_manifest"] = [{"record_type": "Incident"}]
    elif change == "assignment_uuid":
        manifest["eligible_shifts"][0]["assignment_id"] = "not-a-uuid"
    elif change == "calendar":
        manifest["query_start"] = wrong["query_start"] = "2026-99-99T99:99:99Z"
    elif change == "candidate_future":
        manifest["candidate_reports"][0]["created_at"] = "2026-01-03T00:00:00Z"
    elif change == "nonpositive_version":
        manifest["candidate_reports"][0]["version"] = 0
    elif change == "selected_outside_window":
        selected = manifest["selected_reports"][0]
        selected["generated_from_cutoff"] = "2025-12-31T23:00:00Z"
        candidate = next(x for x in manifest["candidate_reports"]
                         if x["report_id"] == selected["report_id"])
        candidate["generated_from_cutoff"] = selected["generated_from_cutoff"]
    elif change in {"ref_bool_version", "ref_float_version", "ref_string_version"}:
        manifest["selected_reports"][0]["source_manifest"][0]["source_version"] = {
            "ref_bool_version": True, "ref_float_version": 1.0,
            "ref_string_version": "1",
        }[change]
    elif change == "source_bytes":
        wrong["canonical_manifest"] += " "
        with pytest.raises(ValueError):
            validate_source_receipt(wrong)
        return
    wrong["canonical_manifest"] = canonical_json(manifest)
    wrong["source_digest"] = sha256(wrong["canonical_manifest"].encode()).hexdigest()
    with pytest.raises(ValueError):
        validate_source_receipt(wrong)


def test_utf8_canonical_source_encoding():
    assert canonical_json({"scope_id": "Ca đêm"}) == '{"scope_id":"Ca đêm"}'
