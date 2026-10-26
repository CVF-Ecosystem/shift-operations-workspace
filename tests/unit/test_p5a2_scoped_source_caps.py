from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
import json
from uuid import NAMESPACE_DNS, uuid5

import pytest

from cvf_runtime.identity import Principal
from operations_domain.models import Shift
from operations_domain.assignment_models import ShiftAssignment
from operations_ledger._proactive_source_types import SourceReadFailure
from workspace_api.application.proactive_source import TrustedSourceScope, query_source
from workspace_api.infrastructure._proactive_source_memory import MemorySourceUnit
from workspace_api.infrastructure.repository import InMemoryLedger

from p5a2_scoped_source_helpers import START, oracle, report


PRINCIPAL = Principal(user_id="PUBLIC_ACTOR", role="operator")
SCOPE = TrustedSourceScope("PUBLIC_SCOPE", "PUBLIC_ACTOR", "CAP-FIXTURE")


class BoundaryCoverage:
    def __init__(self, ledger, scope, start, end, as_of):
        stamp = lambda value: value.isoformat().replace("+00:00", "Z")
        active = {a.shift_id: a for a in ledger.assignments.values()
                  if a.user_id == scope.actor_id and str(a.status) == "ACTIVE"}
        shifts = sorted((s for s in ledger.shifts.values()
                         if s.shift_id in active and start <= s.ends_at < end), key=lambda s: str(s.shift_id))
        shift_ids = {s.shift_id for s in shifts}
        reports = sorted((r for r in ledger.reports.values()
                          if r.shift_id in shift_ids and str(r.report_type) == "END_SHIFT"
                          and r.created_at <= as_of),
                         key=lambda r: (str(r.shift_id), r.version, str(r.report_id)))
        self.seed = {
            "fixture_id": "CAP-FIXTURE", "instance_id": scope.instance_id,
            "scope_id": scope.scope_id, "actor_id": scope.actor_id,
            "query_start": stamp(start), "query_end": stamp(end), "run_as_of": stamp(as_of),
            "cohort_policy_version": scope.cohort_policy_version,
            "numeric_policy_version": scope.numeric_policy_version,
            "eligible_shifts": [{"shift_id": str(s.shift_id), "ends_at": stamp(s.ends_at),
                "assignment_id": str(active[s.shift_id].assignment_id),
                "assignment_version": active[s.shift_id].version} for s in shifts],
            "candidate_reports": [{"shift_id": str(r.shift_id), "report_id": str(r.report_id),
                "version": r.version, "generated_from_cutoff": stamp(r.generated_from_cutoff),
                "created_at": stamp(r.created_at), "snapshot_digest": r.content.snapshot_digest}
                for r in reports],
        }
        self.digest = sha256(json.dumps(self.seed, sort_keys=True, separators=(",", ":"),
                                        allow_nan=False, ensure_ascii=False).encode("utf-8")).hexdigest()

    def verify(self, scope, start, end, as_of, cohort, candidates):
        stamp = lambda value: value.isoformat().replace("+00:00", "Z")
        actual = {
            "fixture_id": "CAP-FIXTURE", "instance_id": scope.instance_id,
            "scope_id": scope.scope_id, "actor_id": scope.actor_id,
            "query_start": stamp(start), "query_end": stamp(end), "run_as_of": stamp(as_of),
            "cohort_policy_version": scope.cohort_policy_version,
            "numeric_policy_version": scope.numeric_policy_version,
            "eligible_shifts": [{"shift_id": str(k.shift_id), "ends_at": stamp(k.ends_at),
                "assignment_id": str(k.assignment_id), "assignment_version": k.assignment_version}
                for k in cohort],
            "candidate_reports": [{"shift_id": str(k.shift_id), "report_id": str(k.report_id),
                "version": k.version, "generated_from_cutoff": stamp(k.cutoff),
                "created_at": stamp(k.created_at), "snapshot_digest": k.snapshot_digest}
                for k in candidates],
        }
        if actual != self.seed:
            raise SourceReadFailure("SCOPE_INCOMPLETE")
        return self.seed["fixture_id"], self.digest


def _insert(ledger, item):
    cutoff = item.generated_from_cutoff
    if item.shift_id not in ledger.shifts:
        ledger.shifts[item.shift_id] = Shift(
            shift_id=item.shift_id, name="BOUNDARY", starts_at=cutoff - timedelta(hours=1),
            ends_at=cutoff, created_at=cutoff - timedelta(hours=2),
        )
        assignment_id = uuid5(NAMESPACE_DNS, f"boundary-assignment-{item.shift_id}")
        ledger.assignments[assignment_id] = ShiftAssignment(
            assignment_id=assignment_id, shift_id=item.shift_id,
            user_id=PRINCIPAL.user_id, assigned_by=PRINCIPAL.user_id,
            assigned_at=cutoff - timedelta(hours=2),
        )
    ledger.reports[item.report_id] = item


@pytest.mark.parametrize("dimension", ["eligible", "candidates", "refs"])
def test_valid_500_each_dimension_is_admissible(dimension):
    assert oracle()["boundary_cases"][{"eligible": "eligible_500", "candidates": "candidate_versions_500", "refs": "incident_refs_500"}[dimension]].startswith("SOURCE_READY")
    ledger = InMemoryLedger()
    if dimension == "eligible":
        for i in range(500):
            _insert(ledger, report(i, 0))
        end = START + timedelta(hours=500)
    elif dimension == "candidates":
        for version in range(1, 501):
            _insert(ledger, report(0, 0, version=version))
        end = START + timedelta(hours=1)
    else:
        _insert(ledger, report(0, 500))
        end = START + timedelta(hours=1)
    result = query_source(PRINCIPAL, SCOPE, START, end, end, ledger,
                          BoundaryCoverage(ledger, SCOPE, START, end, end))
    assert result.receipt["outcome"] == "SOURCE_READY"
    assert result.payload is not None
    if dimension == "eligible":
        assert result.receipt["eligible_count"] == 500
    elif dimension == "candidates":
        assert result.receipt["candidate_version_count"] == 500
    else:
        assert result.receipt["max_snapshot_incident_refs"] == 500


@pytest.mark.parametrize("dimension,case", [
    ("eligible", "eligible_501"), ("candidates", "candidate_versions_501"),
    ("refs", "incident_refs_501"),
])
def test_501_refuses_before_any_body(dimension, case, monkeypatch):
    ledger = InMemoryLedger()
    if dimension == "eligible":
        for i in range(501):
            _insert(ledger, report(i, 0))
        end = START + timedelta(hours=501)
    elif dimension == "candidates":
        for version in range(1, 502):
            _insert(ledger, report(0, 0, version=version))
        end = START + timedelta(hours=1)
    else:
        _insert(ledger, report(0, 501))
        end = START + timedelta(hours=1)
    copies = []
    def no_body(*args, **kwargs):
        copies.append(1)
        raise AssertionError("body fetched before cap refusal")
    monkeypatch.setattr(MemorySourceUnit, "load_reports", no_body)
    monkeypatch.setattr(type(next(iter(ledger.reports.values()))), "model_copy", no_body)
    row = next(x for x in oracle()["refusals"] if x["case"] == case)
    result = query_source(PRINCIPAL, SCOPE, START, end, end, ledger,
                          BoundaryCoverage(ledger, SCOPE, START, end, end))
    assert result.receipt == row["expected_receipt"] and result.payload is None
    assert copies == []


@pytest.mark.parametrize("field", ["actor_id", "assignment_version", "snapshot_digest"])
def test_boundary_attestor_rejects_seed_mismatch(field):
    ledger = InMemoryLedger()
    _insert(ledger, report(0, 0))
    end = START + timedelta(hours=1)
    verifier = BoundaryCoverage(ledger, SCOPE, START, end, end)
    if field == "actor_id":
        verifier.seed[field] = "OTHER_ACTOR"
    elif field == "assignment_version":
        verifier.seed["eligible_shifts"][0][field] += 1
    else:
        verifier.seed["candidate_reports"][0][field] = "f" * 64
    result = query_source(PRINCIPAL, SCOPE, START, end, end, ledger, verifier)
    assert result.receipt["reason"] == "SCOPE_INCOMPLETE"
