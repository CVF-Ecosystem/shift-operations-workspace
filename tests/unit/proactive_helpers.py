"""Deterministic PUBLIC canonical reports for the bounded P5-A2 tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import NAMESPACE_DNS, uuid5

from operations_domain.report_digest import aggregate_digest, canonical_bytes
from operations_domain.report_models import Report, ReportContent, ReportSection, ReportSourceRef
from reporting_engine.proactive_models import HistoryInput

START = datetime(2026, 1, 1, tzinfo=timezone.utc)
SECTIONS = ("operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers")


def report(index: int, count: int, *, version: int = 1, created_offset: timedelta = timedelta(),
           event_offset: timedelta = timedelta(minutes=-1)) -> Report:
    shift_id = uuid5(NAMESPACE_DNS, f"shift-{index}")
    cutoff = START + timedelta(hours=index)
    records = []
    refs = []
    for number in range(count):
        rid = uuid5(NAMESPACE_DNS, f"incident-{index}-{number}-v{version}")
        row = {
            "record_type": "Incident", "record_id": str(rid), "shift_id": str(shift_id),
            "risk_class": "R1", "summary": "synthetic", "description": None,
            "status": "REPORTED", "owner_id": None, "version": version,
            "created_at": (cutoff + event_offset).isoformat().replace("+00:00", "Z"), "evidence": [],
        }
        records.append(row)
        refs.append(ReportSourceRef(record_type="Incident", record_id=rid, source_version=version,
                                    source_digest=sha256(canonical_bytes(row)).hexdigest()))
    ordered = sorted(zip(records, refs), key=lambda pair: (pair[0]["created_at"], pair[0]["record_id"]))
    records = [row for row, _ in ordered]
    refs = [ref for _, ref in ordered]
    sections = [ReportSection(section_type=name, records=records if name == "incidents" else []) for name in SECTIONS]
    content = ReportContent(sections=sections, source_manifest=refs, snapshot_digest="0" * 64)
    content = content.model_copy(update={"snapshot_digest": aggregate_digest(shift_id, "END_SHIFT", content)})
    return Report(report_id=uuid5(NAMESPACE_DNS, f"report-{index}-v{version}"), shift_id=shift_id,
                  version=version, generated_from_cutoff=cutoff,
                  created_at=cutoff + created_offset, content=content)


def history(counts: list[int]) -> HistoryInput:
    reports = tuple(report(i, count) for i, count in enumerate(counts))
    ids = tuple(sorted((r.shift_id for r in reports), key=str))
    return HistoryInput("PUBLIC_SCOPE", "PUBLIC_ACTOR", START, START + timedelta(hours=len(counts)),
                        START + timedelta(hours=len(counts)), ids, reports, True, True)
