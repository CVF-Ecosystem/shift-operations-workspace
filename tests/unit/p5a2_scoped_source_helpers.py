"""HARNESS-only fixture authority, independent of the production coverage default."""

from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import NAMESPACE_DNS, uuid5

from operations_domain.models import Shift
from operations_domain.assignment_models import ShiftAssignment
from operations_ledger._proactive_source_types import SourceReadFailure
from workspace_api.infrastructure.repository import InMemoryLedger

from workspace_api.application.proactive_source_receipt import canonical_json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "unit"))
from proactive_helpers import START, report  # noqa: E402

ORACLE = ROOT / "tests/fixtures/p5a2_scoped_source_oracle.json"
ORACLE_SHA = "0f79676b627aceebd5e83a4b8143d29feda8deaad9392ad52cdd7204b593a044"


def oracle() -> dict:
    raw = ORACLE.read_bytes()
    assert sha256(raw).hexdigest() == ORACLE_SHA
    return json.loads(raw)


def public_ledger() -> InMemoryLedger:
    ledger = InMemoryLedger()
    for index in range(36):
        item = report(index, 4)
        cutoff = START + timedelta(hours=index)
        starts = cutoff - timedelta(hours=1)
        shift = Shift(shift_id=item.shift_id, name=f"PUBLIC-{index}",
                      starts_at=starts, ends_at=cutoff,
                      created_at=starts - timedelta(hours=1))
        assignment = ShiftAssignment(
            assignment_id=uuid5(NAMESPACE_DNS, f"p5a2-source-assignment-{item.shift_id}"),
            shift_id=item.shift_id, user_id="PUBLIC_ACTOR", assigned_by="PUBLIC_ACTOR",
            assigned_at=starts - timedelta(hours=1),
        )
        ledger.shifts[shift.shift_id] = shift
        ledger.assignments[assignment.assignment_id] = assignment
        if index == 0:
            item = item.model_copy(update={"is_current": False})
        ledger.reports[item.report_id] = item
    successor = report(0, 9, version=2, created_offset=timedelta(hours=37))
    ledger.reports[successor.report_id] = successor
    return ledger


class FixtureCoverage:
    """Private test attestation matched to the Root-frozen pre-loader seed."""

    def __init__(self, case: dict):
        self.case = case

    def verify(self, scope, start, end, as_of, cohort, candidates):
        def stamp(value):
            return value.isoformat().replace("+00:00", "Z")

        actual = {
            "fixture_id": oracle()["fixture_id"], "instance_id": scope.instance_id,
            "scope_id": scope.scope_id, "actor_id": scope.actor_id,
            "query_start": stamp(start), "query_end": stamp(end), "run_as_of": stamp(as_of),
            "cohort_policy_version": scope.cohort_policy_version,
            "numeric_policy_version": scope.numeric_policy_version,
            "eligible_shifts": [
                {"shift_id": str(k.shift_id), "ends_at": stamp(k.ends_at),
                 "assignment_id": str(k.assignment_id), "assignment_version": k.assignment_version}
                for k in cohort
            ],
            "candidate_reports": [
                {"shift_id": str(k.shift_id), "report_id": str(k.report_id),
                 "version": k.version, "generated_from_cutoff": stamp(k.cutoff),
                 "created_at": stamp(k.created_at), "snapshot_digest": k.snapshot_digest}
                for k in candidates
            ],
        }
        if actual != self.case["coverage_seed"]:
            raise SourceReadFailure("SCOPE_INCOMPLETE")
        digest = sha256(canonical_json(actual).encode()).hexdigest()
        assert digest == self.case["coverage_seed_digest"]
        return actual["fixture_id"], digest
