"""Exact metadata-only verifier for the isolated synthetic source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from operations_ledger._proactive_source_types import SourceReadFailure
from reporting_engine.proactive_models import stamp

from workspace_api.application.proactive_source import _candidate_item, _cohort_item
from workspace_api.demo.bundle import P5A2_DEMO_BUNDLE_SHA256

P5A2_DEMO_AUTHORITY_SHA256 = "3ed09877a15b7bbd9ae1178392e6262688607e73a678a95c86e0132e213baecb"


def _digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def load_authority() -> dict:
    raw = Path(__file__).with_name("authority_v1.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != P5A2_DEMO_AUTHORITY_SHA256:
        raise ValueError("synthetic authority integrity failure")
    authority = json.loads(raw)
    if (authority.get("authority_version") != "P5A2-SOURCE-DEMO-AUTHORITY-1"
            or authority.get("fixture_id") != "P5A2-SOURCE-DEMO-1"
            or authority.get("instance_id") != "P5A2-SOURCE-DEMO-LOCAL-1"
            or authority.get("actor_id") != "PUBLIC_ACTOR"
            or authority.get("coverage_mode") != "SYNTHETIC_FIXTURE"
            or authority.get("data_bundle_sha256") != P5A2_DEMO_BUNDLE_SHA256
            or len(authority.get("profiles", [])) != 2):
        raise ValueError("synthetic authority shape failure")
    for profile in authority["profiles"]:
        if _digest(profile["coverage_seed"]) != profile["coverage_seed_digest"]:
            raise ValueError("synthetic coverage seed integrity failure")
    return authority


_DEFAULT = object()


class DemoCoverageVerifier:
    def __init__(self, authority: dict | None = _DEFAULT):
        self.authority = load_authority() if authority is _DEFAULT else authority

    def verify(self, scope, start, end, as_of, cohort, candidates) -> tuple[str, str]:
        authority = self.authority
        try:
            trusted = load_authority()
        except (OSError, ValueError, KeyError, TypeError):
            raise SourceReadFailure("COVERAGE_UNKNOWN")
        if authority is None or authority != trusted:
            raise SourceReadFailure("COVERAGE_UNKNOWN")
        if (scope.instance_id != authority["instance_id"]
                or scope.actor_id != authority["actor_id"]):
            raise SourceReadFailure("COVERAGE_UNKNOWN")
        actual = {
            "fixture_id": authority["fixture_id"],
            "instance_id": scope.instance_id,
            "scope_id": scope.scope_id,
            "actor_id": scope.actor_id,
            "query_start": stamp(start), "query_end": stamp(end),
            "run_as_of": stamp(as_of),
            "cohort_policy_version": scope.cohort_policy_version,
            "numeric_policy_version": scope.numeric_policy_version,
            "eligible_shifts": [_cohort_item(key) for key in cohort],
            "candidate_reports": [_candidate_item(key) for key in candidates],
        }
        for profile in authority["profiles"]:
            seed = profile["coverage_seed"]
            identity = {key: seed[key] for key in seed if key not in
                        ("eligible_shifts", "candidate_reports")}
            if all(actual[key] == value for key, value in identity.items()):
                # Python value equality treats True and 1.0 as equal to the
                # frozen integer 1. Canonical JSON keeps these types distinct.
                if _digest(actual) != profile["coverage_seed_digest"]:
                    raise SourceReadFailure("SCOPE_INCOMPLETE")
                if _digest(seed) != profile["coverage_seed_digest"]:
                    raise SourceReadFailure("COVERAGE_UNKNOWN")
                return authority["fixture_id"], profile["coverage_seed_digest"]
        raise SourceReadFailure("COVERAGE_UNKNOWN")
