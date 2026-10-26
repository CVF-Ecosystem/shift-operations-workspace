"""Metadata-only cohort probe, native source read and fresh release check."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from uuid import UUID

from operations_ledger._proactive_source_types import CohortKey, SourceReadFailure

from .proactive_source import TrustedSourceScope, query_source
from .proactive_source_receipt import emit_source_refused, validate_source_receipt


@dataclass(frozen=True)
class SourcePreview:
    receipt: dict
    cohort: tuple[CohortKey, ...] | None


def _refused(reason: str, cohort: tuple[CohortKey, ...] | None = None) -> SourcePreview:
    return SourcePreview(emit_source_refused(reason), cohort)


def preview_source(principal, scope: TrustedSourceScope, start: datetime,
                   end: datetime, as_of: datetime, ledger, coverage) -> SourcePreview:
    """Probe the native bounded cohort before coverage or report-body reads."""
    try:
        with ledger.scoped_source_read(principal.user_id, start, end, as_of) as unit:
            cohort = unit.cohort()
        if not cohort:
            return _refused("ACCESS_DENIED")
        if len(cohort) > 500:
            return _refused("SCOPE_INCOMPLETE")
        result = query_source(principal, scope, start, end, as_of, ledger, coverage)
        validate_source_receipt(result.receipt)
        if result.receipt["outcome"] == "SOURCE_READY":
            manifest = json.loads(result.receipt["canonical_manifest"])
            expected = tuple(
                CohortKey(
                    UUID(item["shift_id"]),
                    datetime.fromisoformat(item["ends_at"].replace("Z", "+00:00")),
                    UUID(item["assignment_id"]),
                    item["assignment_version"],
                ) for item in manifest["eligible_shifts"]
            )
            return SourcePreview(result.receipt, expected)
        return SourcePreview(result.receipt, cohort)
    except SourceReadFailure as exc:
        reason = exc.reason if exc.reason in {
            "ACCESS_DENIED", "SCOPE_INCOMPLETE", "SNAPSHOT_UNAVAILABLE",
            "TIME_AMBIGUOUS", "SOURCE_UNAVAILABLE",
        } else "SOURCE_UNAVAILABLE"
        return _refused(reason)
    except Exception:
        return _refused("SOURCE_UNAVAILABLE")


def fresh_release(preview: SourcePreview, principal, start: datetime,
                  end: datetime, ledger) -> dict:
    """Compare the entire current cohort with the proven membership."""
    cohort = preview.cohort
    if cohort is None:
        return preview.receipt
    try:
        shift_ids = tuple(item.shift_id for item in cohort)
        fresh = ledger.fresh_scoped_cohort(principal.user_id, start, end, shift_ids)
        if not set(shift_ids) <= fresh.prior_active:
            return emit_source_refused("ACCESS_DENIED")
        if fresh.cohort != cohort:
            return emit_source_refused("SCOPE_INCOMPLETE")
        return preview.receipt
    except SourceReadFailure as exc:
        reason = exc.reason if exc.reason in {"ACCESS_DENIED", "SCOPE_INCOMPLETE",
                                             "SNAPSHOT_UNAVAILABLE"} else "SOURCE_UNAVAILABLE"
        return emit_source_refused(reason)
    except Exception:
        return emit_source_refused("SOURCE_UNAVAILABLE")
