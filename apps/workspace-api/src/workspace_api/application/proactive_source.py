"""Fixture-scoped, count-first native history admission; no route or action write."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from cvf_runtime.identity import Principal
from operations_ledger._proactive_source_types import CandidateKey, CohortKey, SourceReadFailure
from reporting_engine.proactive_history import _validate_report, select_history
from reporting_engine.proactive_models import HistoryInput, ProactiveRefusal, aware_utc, stamp

from .proactive_source_receipt import (
    COHORT_VERSION, NUMERIC_VERSION, SourceQueryResult, emit_source_ready,
    emit_source_refused,
)


@dataclass(frozen=True)
class TrustedSourceScope:
    """Server-composed internal scope; public request construction is outside this slice."""

    scope_id: str
    actor_id: str
    instance_id: str
    cohort_policy_version: str = COHORT_VERSION
    numeric_policy_version: str = NUMERIC_VERSION


class CoverageVerifier(Protocol):
    def verify(self, scope: TrustedSourceScope, start: datetime, end: datetime,
               as_of: datetime, cohort: tuple[CohortKey, ...],
               candidates: tuple[CandidateKey, ...]) -> tuple[str, str]: ...


def _cohort_item(key: CohortKey) -> dict:
    return {
        "shift_id": str(key.shift_id), "ends_at": stamp(key.ends_at),
        "assignment_id": str(key.assignment_id), "assignment_version": key.assignment_version,
    }


def _candidate_item(key: CandidateKey) -> dict:
    return {
        "shift_id": str(key.shift_id), "report_id": str(key.report_id),
        "version": key.version, "generated_from_cutoff": stamp(key.cutoff),
        "created_at": stamp(key.created_at), "snapshot_digest": key.snapshot_digest,
    }


def _fail(reason: str) -> SourceQueryResult:
    return SourceQueryResult(emit_source_refused(reason), None)


def query_source(principal: Principal, scope: TrustedSourceScope, start: datetime,
                 end: datetime, as_of: datetime, ledger, coverage: CoverageVerifier | None = None
                 ) -> SourceQueryResult:
    """Build a fixture HistoryInput only after bounded native and fresh-access proof."""
    if (not isinstance(principal, Principal) or not isinstance(scope, TrustedSourceScope)
            or not isinstance(principal.user_id, str) or not principal.user_id
            or scope.actor_id != principal.user_id or not scope.scope_id or not scope.instance_id):
        return _fail("ACCESS_DENIED")
    try:
        try:
            start, end, as_of = (aware_utc(x) for x in (start, end, as_of))
        except ProactiveRefusal:
            return _fail("TIME_AMBIGUOUS")
        if not start < end <= as_of:
            return _fail("INVALID_WINDOW")
        if (scope.cohort_policy_version, scope.numeric_policy_version) != (COHORT_VERSION, NUMERIC_VERSION):
            return _fail("INCOMPATIBLE_POLICY")
        if coverage is None:
            return _fail("COVERAGE_UNKNOWN")
        with ledger.scoped_source_read(principal.user_id, start, end, as_of) as unit:
            cohort = unit.cohort()
            if not 0 < len(cohort) <= 500:
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            shift_ids = tuple(key.shift_id for key in cohort)
            if len(set(shift_ids)) != len(shift_ids) or shift_ids != tuple(sorted(shift_ids, key=str)):
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            for key in cohort:
                aware_utc(key.ends_at)
                if not start <= aware_utc(key.ends_at) < end:
                    raise SourceReadFailure("SCOPE_INCOMPLETE")
            candidates = unit.candidates(shift_ids)
            if not 0 < len(candidates) <= 500:
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            report_ids = tuple(key.report_id for key in candidates)
            if len(set(report_ids)) != len(report_ids):
                raise SourceReadFailure("INVALID_LINEAGE")
            if any(key.shift_id not in shift_ids for key in candidates):
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            for key in candidates:
                if aware_utc(key.cutoff) > aware_utc(key.created_at) or aware_utc(key.created_at) > as_of:
                    raise SourceReadFailure("TIME_AMBIGUOUS")
            refs = unit.incident_ref_counts(report_ids)
            if set(refs) != set(report_ids):
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            if any(not all(type(n) is int and 0 <= n <= 500 for n in pair) for pair in refs.values()):
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            max_refs = max((max(pair) for pair in refs.values()), default=0)
            reports = unit.load_reports(report_ids)
            if len(reports) != len(candidates):
                raise SourceReadFailure("SCOPE_INCOMPLETE")
            by_id = {r.report_id: r for r in reports}
            if set(by_id) != set(report_ids):
                raise SourceReadFailure("INVALID_LINEAGE")
            for key in candidates:
                report = by_id[key.report_id]
                if (report.shift_id != key.shift_id or report.version != key.version
                        or report.generated_from_cutoff != key.cutoff
                        or report.created_at != key.created_at
                        or report.content.snapshot_digest != key.snapshot_digest):
                    raise SourceReadFailure("INVALID_LINEAGE")
                # Validate every loaded immutable candidate, including superseded versions.
                if _validate_report(report, as_of) is None:
                    raise SourceReadFailure("TIME_AMBIGUOUS")
            payload = HistoryInput(scope.scope_id, principal.user_id, start, end, as_of,
                                   shift_ids, tuple(reports), True, True)
            selected = select_history(payload, as_of, require_complete=True)
            if len(selected) != len(cohort):
                raise SourceReadFailure("SCOPE_INCOMPLETE")
        # This must be a NEW current view, never a second query in the sealed unit.
        fresh = ledger.fresh_scoped_cohort(principal.user_id, start, end, shift_ids)
        if not set(shift_ids) <= fresh.prior_active:
            raise SourceReadFailure("ACCESS_DENIED")
        if fresh.cohort != cohort:
            raise SourceReadFailure("SCOPE_INCOMPLETE")
        fixture_id, coverage_digest = coverage.verify(scope, start, end, as_of, cohort, candidates)
        if not isinstance(fixture_id, str) or not fixture_id or not isinstance(coverage_digest, str):
            raise SourceReadFailure("COVERAGE_UNKNOWN")
        manifest = {
            "scope_id": scope.scope_id, "actor_id": principal.user_id,
            "query_start": stamp(start), "query_end": stamp(end), "run_as_of": stamp(as_of),
            "cohort_policy_version": COHORT_VERSION, "numeric_policy_version": NUMERIC_VERSION,
            "coverage_fixture_id": fixture_id, "coverage_manifest_digest": coverage_digest,
            "eligible_shifts": [_cohort_item(key) for key in cohort],
            "candidate_reports": [_candidate_item(key) for key in candidates],
            "selected_reports": [item.lineage_item() for item in selected],
        }
        return SourceQueryResult(emit_source_ready(manifest, len(cohort), len(candidates), max_refs), payload)
    except SourceReadFailure as exc:
        return _fail(exc.reason)
    except ProactiveRefusal as exc:
        return _fail({"LINEAGE_INVALID": "INVALID_LINEAGE", "INPUT_INVALID": "INVALID_LINEAGE"}.get(exc.reason, exc.reason))
    except Exception:
        return _fail("SOURCE_UNAVAILABLE")
