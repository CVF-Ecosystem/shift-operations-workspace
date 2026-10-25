"""PostgreSQL scalar JSONB preflight before bounded Report body loading."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, text

from operations_ledger._proactive_source_types import SourceReadFailure
from operations_ledger._report_store import _row_to_report
from operations_ledger.tables import reports


def incident_ref_counts(conn, report_ids: tuple[UUID, ...]) -> dict[UUID, tuple[int, int]]:
    if not report_ids:
        return {}
    # A scalar result only: no JSONB body is transferred to Python before caps.
    stmt = text("""
        SELECT report_id,
          (SELECT count(*) FROM jsonb_array_elements(
             CASE WHEN jsonb_typeof(content->'source_manifest') = 'array'
               THEN content->'source_manifest' ELSE '[]'::jsonb END) ref
             WHERE ref->>'record_type' = 'Incident') AS manifest_refs,
          (SELECT count(*) FROM jsonb_array_elements(
             CASE WHEN jsonb_typeof(content->'sections') = 'array'
               THEN content->'sections' ELSE '[]'::jsonb END) section,
             LATERAL jsonb_array_elements(
               CASE WHEN jsonb_typeof(section->'records') = 'array'
                 THEN section->'records' ELSE '[]'::jsonb END) item
             WHERE section->>'section_type' = 'incidents') AS section_records
        FROM reports WHERE report_id = ANY(:ids)
    """)
    # SQLAlchemy UUID bind adaptation is dialect-owned; IDs are native UUIDs.
    rows = conn.execute(stmt, {"ids": list(report_ids)}).all()
    result = {UUID(str(row[0])): (int(row[1]), int(row[2])) for row in rows}
    if set(result) != set(report_ids):
        raise SourceReadFailure("SCOPE_INCOMPLETE")
    return result


def load_reports(conn, models, report_ids: tuple[UUID, ...]) -> tuple:
    if not report_ids:
        return ()
    rows = conn.execute(select(reports).where(reports.c.report_id.in_(report_ids))).mappings().all()
    by_id = {row["report_id"]: row for row in rows}
    if set(by_id) != set(report_ids):
        raise SourceReadFailure("SCOPE_INCOMPLETE")
    try:
        return tuple(_row_to_report(models, by_id[rid]) for rid in report_ids)
    except (TypeError, ValueError, KeyError, AttributeError) as exc:
        raise SourceReadFailure("INVALID_LINEAGE") from exc
