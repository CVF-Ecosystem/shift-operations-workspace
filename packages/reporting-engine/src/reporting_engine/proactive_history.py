"""Canonical report validation and point-in-time supplied-history selection."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import ValidationError
from pydantic_core import PydanticSerializationError
from operations_domain.report_digest import aggregate_digest, canonical_bytes
from operations_domain.report_models import Report, ReportContent, ReportSection, ReportSourceRef, ReportType

from .proactive_models import HistoryInput, Observation, ProactiveRefusal, aware_utc, digest, stamp, POLICY_VERSION


def validate_input(source: HistoryInput) -> tuple[datetime, datetime, datetime]:
    start, end, as_of = map(aware_utc, (source.query_start, source.query_end, source.run_as_of))
    if not isinstance(source.scope_id, str) or not source.scope_id or not isinstance(source.actor_id, str) or not source.actor_id:
        raise ProactiveRefusal("INPUT_INVALID")
    if start >= end or end > as_of:
        raise ProactiveRefusal("TIME_AMBIGUOUS")
    if source.complete is not True or source.retention_complete is not True:
        raise ProactiveRefusal("SCOPE_INCOMPLETE")
    ids = source.eligible_shift_ids
    if not isinstance(ids, tuple) or not isinstance(source.candidates, tuple):
        raise ProactiveRefusal("INPUT_INVALID")
    if len(ids) > 500 or len(source.candidates) > 500:
        raise ProactiveRefusal("SCOPE_INCOMPLETE")
    if not ids or any(not isinstance(i, UUID) for i in ids):
        raise ProactiveRefusal("SCOPE_INCOMPLETE")
    keys = [str(i) for i in ids]
    if keys != sorted(set(keys)):
        raise ProactiveRefusal("SCOPE_INCOMPLETE")
    for report in source.candidates:
        if not isinstance(report, Report) or not isinstance(report.shift_id, UUID) or not isinstance(report.report_id, UUID):
            raise ProactiveRefusal("INPUT_INVALID")
        if type(report.version) is not int or report.version < 1 or not isinstance(report.content, ReportContent):
            raise ProactiveRefusal("INPUT_INVALID")
        if report.shift_id not in ids or report.report_type != ReportType.END_SHIFT:
            raise ProactiveRefusal("SCOPE_INCOMPLETE")
        if not isinstance(report.created_at, datetime) or not isinstance(report.generated_from_cutoff, datetime):
            raise ProactiveRefusal("TIME_AMBIGUOUS")
    return start, end, as_of


def _check_content_shape(content: ReportContent) -> None:
    if (not isinstance(content.sections, list)
            or any(not isinstance(s, ReportSection) or not isinstance(s.records, list)
                   for s in content.sections)
            or not isinstance(content.source_manifest, list)
            or any(not isinstance(ref, ReportSourceRef) for ref in content.source_manifest)):
        raise ProactiveRefusal("LINEAGE_INVALID")
    if any(len(section.records) > 500 for section in content.sections):
        raise ProactiveRefusal("SCOPE_INCOMPLETE")


def _validate_report(report: Report, as_of: datetime) -> Observation | None:
    created = aware_utc(report.created_at)
    if created > as_of:
        return None  # Future correction is outside this historical origin.
    cutoff = aware_utc(report.generated_from_cutoff)
    if cutoff > as_of:
        return None
    if cutoff > created:
        raise ProactiveRefusal("TIME_AMBIGUOUS")
    _check_content_shape(report.content)
    incident_input = next((s for s in report.content.sections if s.section_type == "incidents"), None)
    if incident_input is None:
        raise ProactiveRefusal("LINEAGE_INVALID")
    for row in incident_input.records:
        try:
            event_at = aware_utc(datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")))
        except (KeyError, AttributeError, TypeError, ValueError) as exc:
            raise ProactiveRefusal("TIME_AMBIGUOUS") from exc
        if event_at > cutoff:
            raise ProactiveRefusal("TIME_AMBIGUOUS")
    # model_copy(update=...) can evade Pydantic; reconstruct the *whole* value.
    try:
        canonical = Report.model_validate(report.model_dump(mode="json"))
        if aggregate_digest(canonical.shift_id, canonical.report_type, canonical.content) != canonical.content.snapshot_digest:
            raise ProactiveRefusal("LINEAGE_INVALID")
    except ProactiveRefusal:
        raise
    except (ValidationError, PydanticSerializationError, ValueError, TypeError, AttributeError) as exc:
        raise ProactiveRefusal("LINEAGE_INVALID") from exc
    incident_section = next(s for s in canonical.content.sections if s.section_type == "incidents")
    seen: set[str] = set()
    for row in incident_section.records:
        rid = row["record_id"]
        if rid in seen or row["shift_id"] != str(canonical.shift_id):
            raise ProactiveRefusal("LINEAGE_INVALID")
        seen.add(rid)
    refs = tuple(ref.model_dump(mode="json") for ref in canonical.content.source_manifest)
    return Observation(canonical.shift_id, canonical.report_id, canonical.version, cutoff,
                       created, canonical.content.snapshot_digest, refs, len(seen))


def select_history(source: HistoryInput, as_of: datetime, *, require_complete: bool,
                   before: tuple[datetime, str] | None = None,
                   exclude_shift: UUID | None = None) -> list[Observation]:
    start, end, _ = validate_input(source)
    by_shift: dict[UUID, list[Report]] = {i: [] for i in source.eligible_shift_ids}
    versions: dict[tuple[UUID, int], tuple] = {}
    for report in source.candidates:
        created = aware_utc(report.created_at)
        if created > as_of:
            continue
        cutoff = aware_utc(report.generated_from_cutoff)
        if cutoff > as_of or not start <= cutoff < end:
            continue
        if cutoff > created:
            raise ProactiveRefusal("TIME_AMBIGUOUS")
        _check_content_shape(report.content)
        key = (report.shift_id, report.version)
        try:
            immutable_bytes = canonical_bytes(report.content.model_dump(mode="json"))
        except (PydanticSerializationError, ValueError, TypeError, AttributeError) as exc:
            raise ProactiveRefusal("LINEAGE_INVALID") from exc
        identity = (report.report_id, cutoff, created, immutable_bytes)
        if key in versions and versions[key] != identity:
            raise ProactiveRefusal("LINEAGE_INVALID")
        versions[key] = identity
        if before is not None and (cutoff, str(report.shift_id)) >= before:
            continue
        if report.shift_id == exclude_shift:
            continue
        by_shift[report.shift_id].append(report)
    selected: list[Observation] = []
    for shift_id, candidates in by_shift.items():
        if not candidates:
            if require_complete:
                raise ProactiveRefusal("SCOPE_INCOMPLETE")
            continue
        report = max(candidates, key=lambda r: (r.version, aware_utc(r.created_at), str(r.report_id)))
        observation = _validate_report(report, as_of)
        if observation is None:
            raise ProactiveRefusal("TIME_AMBIGUOUS")
        selected.append(observation)
    return sorted(selected, key=lambda o: o.order)


def lineage_payload(source: HistoryInput, selected: list[Observation], *, as_of: datetime,
                    training: bool = False) -> dict:
    return {
        "scope_id": source.scope_id, "query_start": stamp(source.query_start),
        "query_end": stamp(source.query_end),
        "run_as_of": stamp(as_of), "policy_version": POLICY_VERSION,
        "eligible_shift_ids": sorted(str(o.shift_id) for o in selected) if training else [str(i) for i in source.eligible_shift_ids],
        "selected_reports": [o.lineage_item() for o in selected],
    }


def lineage_digest(source: HistoryInput, selected: list[Observation], *, as_of: datetime,
                   training: bool = False) -> str:
    return digest(lineage_payload(source, selected, as_of=as_of, training=training))
