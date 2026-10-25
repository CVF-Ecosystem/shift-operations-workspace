"""Deterministic synthetic PostgreSQL seeds; expectations predate reader calls."""
from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import NAMESPACE_DNS, uuid5

from sqlalchemy import insert, select

from cvf_runtime.identity import Principal
from operations_domain.assignment_models import ShiftAssignment
from operations_domain.models import Shift
from operations_ledger._proactive_source_types import SourceReadFailure
from operations_ledger.tables import users
from workspace_api.application.proactive_source import TrustedSourceScope
from workspace_api.application.proactive_source_receipt import canonical_json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/unit"))
from p5a2_scoped_source_helpers import public_ledger  # noqa: E402
from proactive_helpers import START, report  # noqa: E402

PG_ORACLE = ROOT / "tests/fixtures/p5a2_scoped_source_pg_oracle.json"
PG_SHA = "0b69156fcb09a6b65a25c437320a5f4001f4068284d5bcf8b88438700a92f44f"
SOURCE_ORACLE = ROOT / "tests/fixtures/p5a2_scoped_source_oracle.json"
SOURCE_SHA = "0f79676b627aceebd5e83a4b8143d29feda8deaad9392ad52cdd7204b593a044"
BODY_ORACLE = ROOT / "tests/fixtures/p5a2_docker_backend_oracle.json"
BODY_SHA = "12ad36cbd335a8def5e7ac9a6ade6f0bf542cb45af4cec1760a7291a8f6973c0"


def oracle(path: Path, digest: str) -> dict:
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest
    return json.loads(raw)


def when(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def stamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def context(row: dict):
    ctx = row["context"] if "context" in row else row
    principal = Principal(user_id=ctx["actor_id"], role="operator")
    scope = TrustedSourceScope(ctx["scope_id"], ctx["actor_id"], ctx["instance_id"],
                               ctx["cohort_policy_version"], ctx["numeric_policy_version"])
    return principal, scope, *(when(ctx[k]) for k in ("query_start", "query_end", "run_as_of"))


def _shift(item, name: str, *, ends_at=None) -> Shift:
    end = ends_at or item.generated_from_cutoff
    start = end - timedelta(hours=1)
    return Shift(shift_id=item.shift_id, name=name, starts_at=start, ends_at=end,
                 created_at=start - timedelta(hours=1))


def _user(writer, actor: str) -> None:
    with writer.engine.begin() as conn:
        if conn.execute(select(users.c.user_id).where(users.c.user_id == actor)).first() is None:
            conn.execute(insert(users).values(user_id=actor, username=actor.lower(),
                                              password_hash="synthetic-fixture", role="operator"))


def _assignment(item, actor: str, case_id: str) -> ShiftAssignment:
    return ShiftAssignment(
        assignment_id=uuid5(NAMESPACE_DNS, f"pg-source-{case_id}-{item.shift_id}"),
        shift_id=item.shift_id, user_id=actor, assigned_by=actor,
        assigned_at=item.starts_at - timedelta(hours=1),
    )


class ExpectedFixture:
    def __init__(self, row: dict, shifts: list[Shift], assignments: list[ShiftAssignment], reports: list):
        self.row = row
        self.shifts, self.assignments, self.reports = shifts, assignments, reports
        ctx = row["context"] if "context" in row else row
        start, end, as_of = (when(ctx[k]) for k in ("query_start", "query_end", "run_as_of"))
        active = {a.shift_id: a for a in assignments if str(a.status) == "ACTIVE"}
        eligible = sorted((s for s in shifts if s.shift_id in active and start <= s.ends_at < end),
                          key=lambda s: str(s.shift_id))
        ids = {s.shift_id for s in eligible}
        candidates = sorted((r for r in reports if r.shift_id in ids and r.created_at <= as_of),
                            key=lambda r: (str(r.shift_id), r.version, str(r.report_id)))
        self.seed = {
            "fixture_id": ctx["fixture_id"], "instance_id": ctx["instance_id"],
            "scope_id": ctx["scope_id"], "actor_id": ctx["actor_id"],
            "query_start": ctx["query_start"], "query_end": ctx["query_end"],
            "run_as_of": ctx["run_as_of"],
            "cohort_policy_version": ctx["cohort_policy_version"],
            "numeric_policy_version": ctx["numeric_policy_version"],
            "eligible_shifts": [{"shift_id": str(s.shift_id), "ends_at": stamp(s.ends_at),
                "assignment_id": str(active[s.shift_id].assignment_id),
                "assignment_version": active[s.shift_id].version} for s in eligible],
            "candidate_reports": [{"shift_id": str(r.shift_id), "report_id": str(r.report_id),
                "version": r.version, "generated_from_cutoff": stamp(r.generated_from_cutoff),
                "created_at": stamp(r.created_at), "snapshot_digest": r.content.snapshot_digest}
                for r in candidates],
        }
        self.digest = sha256(canonical_json(self.seed).encode("utf-8")).hexdigest()

    def verify(self, scope, start, end, as_of, cohort, candidates):
        actual = {
            "fixture_id": self.seed["fixture_id"], "instance_id": scope.instance_id,
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


def baseline_expectations(memory=None) -> dict[str, ExpectedFixture]:
    memory = memory or public_ledger()
    shifts = list(memory.shifts.values())
    assignments = list(memory.assignments.values())
    reports = list(memory.reports.values())
    rows = oracle(PG_ORACLE, PG_SHA)["baselineContexts"]
    cases = oracle(SOURCE_ORACLE, SOURCE_SHA)["cases"]
    fixtures = {}
    for row, frozen in zip(rows, cases):
        assert row["case"] == frozen["case"]
        fixture = ExpectedFixture(row, shifts, assignments, reports)
        assert fixture.seed == frozen["coverage_seed"]
        assert fixture.digest == frozen["coverage_seed_digest"]
        fixtures[row["case"]] = fixture
    assert set(fixtures) == {"initial_asof36", "later_asof38"}
    return fixtures


def seed_baseline(writer) -> dict[str, ExpectedFixture]:
    _user(writer, "PUBLIC_ACTOR")
    memory = public_ledger()
    shifts = list(memory.shifts.values())
    assignments = list(memory.assignments.values())
    reports = list(memory.reports.values())
    for shift in shifts:
        writer.create_shift(shift)
    for assignment in assignments:
        writer.add_assignment(assignment)
    for item in reports:
        writer.add_report(item)
    return baseline_expectations(memory)


def build_aux(row: dict) -> tuple[list[Shift], list[ShiftAssignment], list]:
    case_id, actor, index = row["id"], row["context"]["actor_id"], row["index"]
    count = row.get("shiftCount", 1)
    versions = row.get("reportVersions", 1)
    incidents = row.get("incidentCount", 0)
    shifts, assignments, reports = [], [], []
    for offset in range(count):
        position = index + offset
        initial = report(position, incidents if offset == 0 else 0)
        shift = _shift(initial, f"PG-SOURCE-{case_id}-{offset}")
        shifts.append(shift)
        assignments.append(_assignment(shift, actor, case_id))
        for version in range(1, versions + 1):
            item = initial if version == 1 else report(position, incidents, version=version)
            reports.append(item.model_copy(update={"is_current": version == versions}))
    if case_id == "foreign":
        foreign_end = START + timedelta(hours=row["endsAtHour"])
        item = reports[0].model_copy(update={
            "generated_from_cutoff": START + timedelta(hours=row["reportCutoffHour"]),
            "created_at": START + timedelta(hours=row["reportCreatedHour"]),
        })
        reports[0] = item
        shifts[0] = _shift(item, "FOREIGN-IN-BASELINE-WINDOW", ends_at=foreign_end)
        assignments[0] = _assignment(shifts[0], actor, case_id)
    return shifts, assignments, reports


def seed_aux(writer, row: dict) -> ExpectedFixture:
    shifts, assignments, reports = build_aux(row)
    _user(writer, row["context"]["actor_id"])
    for shift in shifts:
        writer.create_shift(shift)
    for assignment in assignments:
        writer.add_assignment(assignment)
    for item in reports:
        writer.add_report(item)
    fixture = ExpectedFixture(row, shifts, assignments, reports)
    assert len(shifts) == row["shiftCount"] and len(reports) == row["shiftCount"] * row["reportVersions"]
    return fixture


def validate_all_auxiliary_fixtures() -> None:
    expected = oracle(PG_ORACLE, PG_SHA)
    rows = expected["capCases"] + expected["raceCases"] + expected["negativeCases"] + [expected["snapshotCase"]]
    all_ids = set()
    for row in rows:
        shifts, assignments, reports = build_aux(row)
        assert len(shifts) == row["shiftCount"] and len(assignments) == len(shifts)
        assert len(reports) == row["shiftCount"] * row["reportVersions"]
        assert all(s.starts_at < s.ends_at for s in shifts)
        assert all(a.shift_id == s.shift_id for a, s in zip(assignments, shifts))
        assert len({s.shift_id for s in shifts}) == len(shifts)
        assert not all_ids.intersection({s.shift_id for s in shifts})
        all_ids.update(s.shift_id for s in shifts)
        fixture = ExpectedFixture(row, shifts, assignments, reports)
        if row["id"] != "foreign":
            assert len(fixture.seed["eligible_shifts"]) == row["shiftCount"]
            start, end = when(row["context"]["query_start"]), when(row["context"]["query_end"])
            assert all(start <= s.ends_at < end for s in shifts)
            assert all(start <= r.generated_from_cutoff < end for r in reports)
        else:
            start, end = when(row["context"]["query_start"]), when(row["context"]["query_end"])
            assert start <= shifts[0].ends_at < end
        assert sum(r.is_current for r in reports) == len(shifts) if reports else True
        assert all(a.assignment_id == uuid5(NAMESPACE_DNS,
                   f"pg-source-{row['id']}-{a.shift_id}") for a in assignments)
        assert all(r.generated_from_cutoff.tzinfo is not None and r.created_at.tzinfo is not None
                   for r in reports)
