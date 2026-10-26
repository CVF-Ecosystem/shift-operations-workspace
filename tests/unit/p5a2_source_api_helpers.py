"""Test-only HTTP composition using real JWT and native fixture ports."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

from cvf_runtime.identity import Principal
from operations_ledger._proactive_source_types import SourceReadFailure
from workspace_api.auth.tokens import create_access_token
from workspace_api.config import settings
from workspace_api.dependencies import (
    get_ledger, get_proactive_source_clock, get_proactive_source_coverage,
)
from workspace_api.domain.models import User
from workspace_api.main import app
from workspace_api.application.proactive_source_receipt import canonical_json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "unit"))
from p5a2_scoped_source_helpers import public_ledger  # noqa: E402

API_ORACLE = ROOT / "tests/fixtures/p5a2_source_api_oracle.json"
API_ORACLE_SHA = "5cc32b1a0484460c7eafb8d23d7112f19ae713699dfd560bb98c4b00411e49fe"
OLD_ORACLE = ROOT / "tests/fixtures/p5a2_scoped_source_oracle.json"


def api_oracle() -> dict:
    raw = API_ORACLE.read_bytes()
    assert sha256(raw).hexdigest() == API_ORACLE_SHA
    return json.loads(raw)


def frozen_refusal(reason: str) -> dict:
    rows = json.loads(OLD_ORACLE.read_text(encoding="utf-8"))["refusals"]
    return next(row["expected_receipt"] for row in rows
                if row["expected_receipt"]["reason"] == reason)


class ApiFixtureCoverage:
    def __init__(self, case: dict):
        self.case = case

    def verify(self, scope, start, end, as_of, cohort, candidates):
        def stamp(value):
            return value.isoformat().replace("+00:00", "Z")

        actual = {
            "fixture_id": self.case["coverage_seed"]["fixture_id"],
            "instance_id": scope.instance_id, "scope_id": scope.scope_id,
            "actor_id": scope.actor_id, "query_start": stamp(start),
            "query_end": stamp(end), "run_as_of": stamp(as_of),
            "cohort_policy_version": scope.cohort_policy_version,
            "numeric_policy_version": scope.numeric_policy_version,
            "eligible_shifts": [
                {"shift_id": str(key.shift_id), "ends_at": stamp(key.ends_at),
                 "assignment_id": str(key.assignment_id),
                 "assignment_version": key.assignment_version} for key in cohort
            ],
            "candidate_reports": [
                {"shift_id": str(key.shift_id), "report_id": str(key.report_id),
                 "version": key.version, "generated_from_cutoff": stamp(key.cutoff),
                 "created_at": stamp(key.created_at), "snapshot_digest": key.snapshot_digest}
                for key in candidates
            ],
        }
        if actual != self.case["coverage_seed"]:
            raise SourceReadFailure("SCOPE_INCOMPLETE")
        digest = sha256(canonical_json(actual).encode("utf-8")).hexdigest()
        assert digest == self.case["coverage_seed_digest"]
        return actual["fixture_id"], digest


def headers(actor="PUBLIC_ACTOR", role="viewer") -> dict:
    token = create_access_token(Principal(user_id=actor, role=role))
    return {"Authorization": f"Bearer {token}"}


def params(case: dict) -> dict:
    seed = case["coverage_seed"]
    return {key: seed[key] for key in ("query_start", "query_end", "run_as_of")}


@contextmanager
def source_client(*, case=None, coverage=False, actor="PUBLIC_ACTOR", role="viewer",
                  instance="PUBLIC-SOURCE-INSTANCE-1", ledger=None, clock=None):
    ledger = ledger or public_ledger()
    ledger.add_user(User(user_id=actor, username=actor, password_hash="x", role=role))
    old_instance = settings.proactive_source_instance_id
    settings.proactive_source_instance_id = instance
    app.dependency_overrides[get_ledger] = lambda: ledger
    app.dependency_overrides[get_proactive_source_coverage] = (
        lambda: ApiFixtureCoverage(case) if coverage else None
    )
    app.dependency_overrides[get_proactive_source_clock] = (
        lambda: clock or (lambda: datetime.now(timezone.utc))
    )
    try:
        with TestClient(app) as client:
            yield client, ledger
    finally:
        settings.proactive_source_instance_id = old_instance
        for dependency in (get_ledger, get_proactive_source_coverage,
                           get_proactive_source_clock):
            app.dependency_overrides.pop(dependency, None)


def assert_private_headers(response):
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
