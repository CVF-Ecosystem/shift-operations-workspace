from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import NAMESPACE_DNS, uuid5

import pytest

from cvf_runtime.identity import Principal
from operations_domain.models import Shift
from operations_domain.assignment_models import ShiftAssignment
from operations_ledger._proactive_source_types import SourceReadFailure
from reporting_engine.proactive_analysis import analyze
from reporting_engine.proactive_history import select_history
from workspace_api.application.proactive_source import TrustedSourceScope, query_source

from p5a2_scoped_source_helpers import FixtureCoverage, START, oracle, public_ledger, report


def _context(case):
    seed = case["coverage_seed"]
    principal = Principal(user_id=seed["actor_id"], role="operator")
    scope = TrustedSourceScope(seed["scope_id"], seed["actor_id"], seed["instance_id"])
    start, end, as_of = (datetime.fromisoformat(seed[key].replace("Z", "+00:00"))
                         for key in ("query_start", "query_end", "run_as_of"))
    return principal, scope, start, end, as_of


@pytest.mark.parametrize("case", oracle()["cases"], ids=lambda c: c["case"])
def test_frozen_full_ready_receipt_lineage_and_analysis(case):
    ledger = public_ledger()
    principal, scope, start, end, as_of = _context(case)
    result = query_source(principal, scope, start, end, as_of, ledger, FixtureCoverage(case))
    assert result.receipt == case["expected_receipt"]
    assert result.payload is not None
    selected = select_history(result.payload, as_of, require_complete=True)
    assert [item.lineage_item() for item in selected] == case["expected_selected_reports"]
    analysis = analyze(result.payload)
    assert {k: v for k, v in analysis.items() if k != "history_context"} == case["expected_analysis"]
    # Returned Report bodies are isolated copies, not mutable ledger-owned objects.
    result.payload.candidates[0].content.sections[4].records.clear()
    assert len(ledger.reports[result.payload.candidates[0].report_id].content.sections[4].records) == 4


NON_CAP = [row for row in oracle()["refusals"] if row["case"] not in
           {"eligible_501", "candidate_versions_501", "incident_refs_501"}]


@pytest.mark.parametrize("row", NON_CAP, ids=lambda row: row["case"])
def test_all_noncap_frozen_refusals(row):
    case = oracle()["cases"][0]
    ledger = public_ledger()
    principal, scope, start, end, as_of = _context(case)
    coverage = FixtureCoverage(case)
    name = row["case"]
    if name == "untrusted_context":
        principal = "PUBLIC_ACTOR"
    elif name in {"spoofed_scope", "denied_actor_with_bad_time_and_overflow"}:
        scope = TrustedSourceScope(scope.scope_id, "OTHER_ACTOR", scope.instance_id)
        if name.startswith("denied"):
            start = start.replace(tzinfo=None)
            for version in range(2, 503):
                item = report(0, 0, version=version)
                ledger.reports[item.report_id] = item
            assert sum(r.shift_id == report(0, 0).shift_id for r in ledger.reports.values()) > 501
            def no_read(*_args):
                raise AssertionError("denied actor entered source read")
            ledger.scoped_source_read = no_read
    elif name == "invalid_aware_window":
        end = start
    elif name == "naive_input_or_sqlite_timestamp":
        start = start.replace(tzinfo=None)
    elif name == "causal_time_violation":
        item = next(iter(ledger.reports.values()))
        item.created_at = item.generated_from_cutoff - timedelta(hours=1)
    elif name == "missing_production_coverage":
        coverage = None
    elif name == "missing_coherent_snapshot":
        def unavailable(*_args):
            raise SourceReadFailure("SNAPSHOT_UNAVAILABLE")
        ledger.scoped_source_read = unavailable
    elif name == "missing_fresh_current_view":
        def unavailable(*_args):
            raise SourceReadFailure("SNAPSHOT_UNAVAILABLE")
        ledger.fresh_scoped_cohort = unavailable
    elif name == "reportless_enrolled_shift":
        ledger.reports.pop(next(iter(ledger.reports)))
    elif name == "zero_eligible":
        ledger.assignments.clear()
    elif name == "attested_manifest_mismatch":
        coverage.case = dict(case, coverage_seed={})
    elif name == "post_seal_revoke":
        original = ledger.fresh_scoped_cohort
        def revoked(*args):
            ledger.assignments.clear()
            return original(*args)
        ledger.fresh_scoped_cohort = revoked
    elif name == "post_seal_assignment_add":
        original = ledger.fresh_scoped_cohort
        def added(*args):
            rid = uuid5(NAMESPACE_DNS, "post-seal-added")
            ledger.shifts[rid] = Shift(shift_id=rid, name="ADDED", starts_at=start,
                                       ends_at=start + timedelta(minutes=1), created_at=start)
            aid = uuid5(NAMESPACE_DNS, "post-seal-assignment")
            ledger.assignments[aid] = ShiftAssignment(assignment_id=aid, shift_id=rid,
                user_id=principal.user_id, assigned_by=principal.user_id, assigned_at=start)
            return original(*args)
        ledger.fresh_scoped_cohort = added
    elif name == "post_seal_assignment_version":
        original = ledger.fresh_scoped_cohort
        def changed(*args):
            next(iter(ledger.assignments.values())).version += 1
            return original(*args)
        ledger.fresh_scoped_cohort = changed
    elif name == "post_seal_shift_enrollment":
        original = ledger.fresh_scoped_cohort
        def shifted(*args):
            next(iter(ledger.shifts.values())).ends_at = end + timedelta(hours=1)
            return original(*args)
        ledger.fresh_scoped_cohort = shifted
    elif name == "invalid_content_digest":
        next(iter(ledger.reports.values())).content.snapshot_digest = "0" * 64
    elif name == "unsupported_policy":
        scope = TrustedSourceScope(scope.scope_id, scope.actor_id, scope.instance_id,
                                   cohort_policy_version="OLD")
    elif name == "storage_exception":
        def broken(*_args):
            raise RuntimeError("secret-bearing driver detail")
        ledger.scoped_source_read = broken
    else:
        raise AssertionError(name)
    result = query_source(principal, scope, start, end, as_of, ledger, coverage)
    assert result.receipt == row["expected_receipt"]
    assert result.payload is None


def test_foreign_bad_time_and_oversized_content_excluded_from_authorized_history(monkeypatch):
    case = oracle()["cases"][0]
    ledger = public_ledger()
    principal, scope, start, end, as_of = _context(case)
    foreign = report(1000, 501)
    foreign.created_at = foreign.created_at.replace(tzinfo=None)
    ledger.reports[foreign.report_id] = foreign
    ledger.shifts[foreign.shift_id] = Shift(
        shift_id=foreign.shift_id, name="FOREIGN", starts_at=start,
        ends_at=start + timedelta(minutes=1), created_at=start,
    )
    aid = uuid5(NAMESPACE_DNS, "foreign-assignment")
    ledger.assignments[aid] = ShiftAssignment(
        assignment_id=aid, shift_id=foreign.shift_id, user_id="OTHER_ACTOR",
        assigned_by="OTHER_ACTOR", assigned_at=start,
    )
    model = type(foreign)
    original = model.model_copy
    copied = []
    def guarded(self, *args, **kwargs):
        copied.append(self.report_id)
        if self.report_id == foreign.report_id:
            raise AssertionError("foreign Report body copied")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(model, "model_copy", guarded)
    result = query_source(principal, scope, start, end, as_of, ledger, FixtureCoverage(case))
    assert result.receipt == case["expected_receipt"]
    assert result.payload is not None
    assert foreign.report_id not in copied
    assert foreign.report_id not in {r.report_id for r in result.payload.candidates}
