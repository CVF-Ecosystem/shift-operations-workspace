"""Exact native key comparison against independently frozen authority."""

from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from uuid import UUID
from hashlib import sha256
import json

import pytest

from operations_ledger._proactive_source_types import CandidateKey, CohortKey, SourceReadFailure
from workspace_api.application.proactive_source import TrustedSourceScope
from workspace_api.demo.coverage import DemoCoverageVerifier, load_authority


def _time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _case(profile):
    seed = profile["coverage_seed"]
    scope = TrustedSourceScope(seed["scope_id"], seed["actor_id"], seed["instance_id"])
    cohort = tuple(CohortKey(UUID(row["shift_id"]), _time(row["ends_at"]),
                             UUID(row["assignment_id"]), row["assignment_version"])
                   for row in seed["eligible_shifts"])
    candidates = tuple(CandidateKey(UUID(row["shift_id"]), UUID(row["report_id"]),
                                    row["version"], _time(row["generated_from_cutoff"]),
                                    _time(row["created_at"]), row["snapshot_digest"])
                       for row in seed["candidate_reports"])
    return scope, _time(seed["query_start"]), _time(seed["query_end"]), _time(seed["run_as_of"]), cohort, candidates


@pytest.mark.parametrize("profile", load_authority()["profiles"], ids=lambda row: row["case"])
def test_exact_frozen_metadata(profile):
    assert DemoCoverageVerifier().verify(*_case(profile)) == (
        "P5A2-SOURCE-DEMO-1", profile["coverage_seed_digest"])


def test_candidate_mutation_refuses_incomplete():
    args = list(_case(load_authority()["profiles"][0]))
    key = args[-1][0]
    args[-1] = (CandidateKey(key.shift_id, key.report_id, key.version, key.cutoff,
                             key.created_at, "0" * 64),) + args[-1][1:]
    with pytest.raises(SourceReadFailure, match="SCOPE_INCOMPLETE"):
        DemoCoverageVerifier().verify(*args)


def test_absent_authority_refuses_unknown():
    args = _case(load_authority()["profiles"][0])
    with pytest.raises(SourceReadFailure, match="COVERAGE_UNKNOWN"):
        DemoCoverageVerifier(None).verify(*args)


@pytest.mark.parametrize("field,value", [
    ("fixture_id", "FORGED"), ("instance_id", "FORGED"),
    ("actor_id", "FORGED"), ("coverage_mode", "OPERATIONAL"),
    ("data_bundle_sha256", "0" * 64),
])
def test_modified_descriptor_refuses_unknown(field, value):
    authority = deepcopy(load_authority())
    authority[field] = value
    with pytest.raises(SourceReadFailure, match="COVERAGE_UNKNOWN"):
        DemoCoverageVerifier(authority).verify(*_case(load_authority()["profiles"][0]))


@pytest.mark.parametrize("field,value", [
    ("scope_id", "FORGED"), ("actor_id", "FORGED"),
    ("cohort_policy_version", "FORGED"),
    ("numeric_policy_version", "FORGED"),
    ("query_start", "2026-01-01T01:00:00Z"),
    ("query_end", "2026-01-02T11:00:00Z"),
    ("run_as_of", "2026-01-02T13:00:00Z"),
])
def test_recomputed_forged_seed_still_refuses_unknown(field, value):
    authority = deepcopy(load_authority())
    profile = authority["profiles"][0]
    profile["coverage_seed"][field] = value
    profile["coverage_seed_digest"] = sha256(json.dumps(
        profile["coverage_seed"], sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    with pytest.raises(SourceReadFailure, match="COVERAGE_UNKNOWN"):
        DemoCoverageVerifier(authority).verify(*_case(load_authority()["profiles"][0]))


@pytest.mark.parametrize("field,value", [
    ("shift_id", UUID(int=1)), ("ends_at", datetime.fromisoformat("2026-01-01T01:00:00+00:00")),
    ("assignment_id", UUID(int=1)), ("assignment_version", 2),
])
def test_each_cohort_key_field_is_bound(field, value):
    args = list(_case(load_authority()["profiles"][0]))
    args[-2] = (replace(args[-2][0], **{field: value}),) + args[-2][1:]
    with pytest.raises(SourceReadFailure, match="SCOPE_INCOMPLETE"):
        DemoCoverageVerifier().verify(*args)


@pytest.mark.parametrize("field,value", [
    ("shift_id", UUID(int=1)), ("report_id", UUID(int=1)),
    ("version", 2), ("cutoff", datetime.fromisoformat("2026-01-01T01:00:00+00:00")),
    ("created_at", datetime.fromisoformat("2026-01-01T01:00:00+00:00")),
    ("snapshot_digest", "0" * 64),
])
def test_each_candidate_key_field_is_bound(field, value):
    args = list(_case(load_authority()["profiles"][0]))
    args[-1] = (replace(args[-1][0], **{field: value}),) + args[-1][1:]
    with pytest.raises(SourceReadFailure, match="SCOPE_INCOMPLETE"):
        DemoCoverageVerifier().verify(*args)


@pytest.mark.parametrize("field,index,version", [
    ("assignment_version", -2, True),
    ("assignment_version", -2, 1.0),
    ("version", -1, True),
    ("version", -1, 1.0),
])
def test_native_metadata_rejects_bool_and_float_versions(field, index, version):
    args = list(_case(load_authority()["profiles"][0]))
    args[index] = (replace(args[index][0], **{field: version}),) + args[index][1:]
    with pytest.raises(SourceReadFailure, match="SCOPE_INCOMPLETE"):
        DemoCoverageVerifier().verify(*args)
