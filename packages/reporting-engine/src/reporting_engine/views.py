"""Deterministic display rows selected from the immutable report."""

import json

from operations_domain.models import Report

from .model import TEMPLATE_VERSION, VIEWS

STATUS_LABELS = {
    "DRAFT": "Draft", "IN_REVIEW": "In review",
    "APPROVED": "Approved", "FROZEN": "Frozen",
}


def selected_rows(report: Report, view: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    selected = VIEWS[view]
    sections = [s for s in report.content.sections if selected is None or s.section_type == selected]
    records = [r for section in sections for r in section.records]
    identities = {(r["record_type"], r["record_id"]) for r in records}
    refs = [m for m in report.content.source_manifest if (m.record_type, str(m.record_id)) in identities]
    rows: list[tuple[str, str]] = []
    for section in sections:
        rows.append(("Section", section.section_type))
        if not section.records:
            rows.append(("Empty", "No records"))
        for record in section.records:
            rows.append(("Record", f"{record['record_type']}/{record['record_id']}"))
            for field, value in record.items():
                if field not in {"record_type", "record_id"}:
                    display = value if isinstance(value, str) else json.dumps(
                        value, ensure_ascii=False, sort_keys=True,
                    )
                    rows.append((field, display))
            for evidence in record.get("evidence", []):
                rows.append(("Evidence", json.dumps({
                    "record_type": record["record_type"], "record_id": record["record_id"],
                    "item_id": None, **evidence,
                }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))))
            for item in record.get("items", []):
                rows.append(("Handover source", json.dumps({
                    "handover_id": record["record_id"], "item_id": item["item_id"],
                    "source_record_type": item["source_record_type"],
                    "source_record_id": item["source_record_id"],
                    "source_digest": item["source_digest"],
                }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))))
                for evidence in item.get("evidence", []):
                    rows.append(("Evidence", json.dumps({
                        "record_type": record["record_type"], "record_id": record["record_id"],
                        "item_id": item["item_id"], **evidence,
                    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))))
    for ref in refs:
        rows.append(("Source", "/".join((ref.record_type, str(ref.record_id),
                     str(ref.source_version), ref.source_digest))))
    metadata = [
        ("report_id", str(report.report_id)), ("shift_id", str(report.shift_id)),
        ("report_type", str(report.report_type)), ("version", str(report.version)),
        ("status", STATUS_LABELS[str(report.status)]),
        ("is_current", "Yes" if report.is_current else "No"),
        ("generated_from_cutoff", report.generated_from_cutoff.isoformat()),
        ("snapshot_digest", report.content.snapshot_digest),
        ("view", view), ("template_version", TEMPLATE_VERSION),
    ]
    if not report.is_current:
        metadata.append(("Historical", "Yes"))
    return metadata, rows
