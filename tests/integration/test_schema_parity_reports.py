"""Schema parity guard for the `reports` table (P2R-OPERATIONAL-REPORT-
FREEZE-PREREQUISITE, SPEC R24).

`reports` is defined across TWO migrations: the base CREATE TABLE in
002_tasks_customers_reports.sql, then is_current/CHECK/UNIQUE/partial-index
additions in 007_report_history_constraints.sql. The generic
`_schema_parity_parsing.table_block()` regex only matches a single
`CREATE TABLE IF NOT EXISTS ... );` statement, so it cannot see 007's ALTER
statements - this module parses both migrations directly rather than
stretching that shared helper to a shape it was not built for (SPEC R24
requires exact two-directional parity, not an approximation).
"""

from __future__ import annotations

import re
import pytest

from operations_ledger.tables import reports

from _schema_parity_parsing import code_columns, constraint_names, migration_columns, migration_text, table_block

_BASE_COLUMNS = {"report_id", "shift_id", "report_type", "version", "status", "content", "generated_from_cutoff", "created_at"}


def test_reports_table_exists_in_migration_002():
    sql = migration_text()
    assert "CREATE TABLE IF NOT EXISTS reports" in sql


def test_is_current_column_added_by_migration_007():
    sql = migration_text()
    assert re.search(r"ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_current boolean", sql), (
        "migration 007 must add the is_current column exactly this way"
    )


def test_column_sets_match_exactly_across_both_migrations():
    """The base CREATE TABLE columns plus 007's is_current must exactly match
    the SQLAlchemy Table object - no drift in either direction."""
    sql = migration_text()
    block = table_block(sql, "reports")
    migration_cols = set(migration_columns(block)) | {"is_current"}
    code_cols = set(code_columns(reports))

    code_only = code_cols - migration_cols
    migration_only = migration_cols - code_cols
    assert not code_only, (
        f"reports: tables.py declares columns neither migration has: {sorted(code_only)}"
    )
    assert not migration_only, (
        f"reports: migrations declare columns tables.py does not map: {sorted(migration_only)}"
    )


def test_base_column_nullability_matches():
    sql = migration_text()
    block = table_block(sql, "reports")
    migration_cols = migration_columns(block)
    code_cols = code_columns(reports)
    for name in _BASE_COLUMNS:
        assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], (
            f"reports.{name}: nullable mismatch - migration says "
            f"nullable={migration_cols[name]['nullable']}, tables.py says "
            f"nullable={code_cols[name]['nullable']}"
        )


def test_is_current_not_null_with_default_true():
    """Migration 007 sets is_current NOT NULL DEFAULT true; tables.py must
    declare a matching server_default so a bare INSERT omitting it succeeds
    against a migration-created PostgreSQL database."""
    sql = migration_text()
    assert re.search(r"ALTER TABLE reports ALTER COLUMN is_current SET NOT NULL", sql)
    assert re.search(r"ALTER TABLE reports ALTER COLUMN is_current SET DEFAULT true", sql)
    is_current_col = reports.c.is_current
    assert not is_current_col.nullable
    assert is_current_col.server_default is not None


def test_version_check_constraint_present_in_both():
    sql = migration_text()
    assert re.search(r"reports_version_check", sql), "migration 007 must name the version CHECK constraint"
    assert "reports_version_check" in constraint_names(reports, "CheckConstraint")


def test_status_check_constraint_present():
    sql = migration_text()
    block = table_block(sql, "reports")
    assert "DRAFT" in block and "IN_REVIEW" in block and "APPROVED" in block and "FROZEN" in block
    assert "reports_status_check" in constraint_names(reports, "CheckConstraint")


def test_shift_type_version_unique_constraint_present_in_both():
    sql = migration_text()
    assert re.search(r"reports_shift_type_version_unique", sql)
    assert "reports_shift_type_version_unique" in constraint_names(reports, "UniqueConstraint")


def test_current_partial_unique_index_present_in_both():
    sql = migration_text()
    assert re.search(r"CREATE UNIQUE INDEX IF NOT EXISTS reports_current_unique", sql)
    index_names = {idx.name for idx in reports.indexes}
    assert "reports_current_unique" in index_names


def test_foreign_key_to_shifts_matches():
    sql = migration_text()
    block = table_block(sql, "reports")
    migration_refs = {
        (ref_table, ref_col)
        for ref_table, ref_col in re.findall(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", block)
    }
    code_refs = {
        (fk.column.table.name, fk.column.name)
        for col in reports.columns
        for fk in col.foreign_keys
    }
    assert migration_refs == code_refs == {("shifts", "shift_id")}


def test_primary_key_matches():
    sql = migration_text()
    block = table_block(sql, "reports")
    migration_pk = {name for name, meta in migration_columns(block).items() if meta["is_pk"]}
    code_pk = set(reports.primary_key.columns.keys())
    assert migration_pk == code_pk == {"report_id"}


def test_tightened_json_schema_preserves_the_five_original_required_names():
    """SPEC R28/ADR Decision 8: the pre-P2R loose schema required exactly
    report_id/shift_id/version/status/sections. This tranche tightens the
    schema in place (additionalProperties, formats, enums, the new R2
    fields) but must never silently drop any of the five original names."""
    import json
    from pathlib import Path

    schema_path = (
        Path(__file__).resolve().parents[2]
        / "packages" / "workspace-contracts" / "reports" / "shift-report.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    # The historical pre-P2R fixture, byte-for-byte as it existed before this
    # tranche (verified against git history) - proves the ORIGINAL contract,
    # not a re-derived approximation of it.
    historical_pre_p2r_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "shift-report.schema",
        "type": "object",
        "required": ["report_id", "shift_id", "version", "status", "sections"],
        "properties": {
            "report_id": {"type": "string"},
            "shift_id": {"type": "string"},
            "version": {"type": "integer"},
            "status": {"type": "string"},
            "sections": {"type": "array"},
        },
    }

    assert set(historical_pre_p2r_schema["required"]) <= set(schema["required"]), (
        "tightened schema dropped an original required field"
    )
    for name in historical_pre_p2r_schema["properties"]:
        assert name in schema["properties"], f"tightened schema dropped original property {name!r}"

    # New R2 additions beyond the five original names.
    assert set(schema["required"]) - set(historical_pre_p2r_schema["required"]) == {
        "report_type", "is_current", "source_manifest", "snapshot_digest",
        "generated_from_cutoff", "created_at",
    }
    assert schema["additionalProperties"] is False


def test_migration_007_never_deletes_or_rewrites_existing_report_data():
    """SPEC R23: no destructive statement against pre-existing rows."""
    from pathlib import Path

    path_007 = Path(__file__).resolve().parents[2] / "database" / "migrations" / "007_report_history_constraints.sql"
    text_007 = path_007.read_text(encoding="utf-8").upper()
    assert "DELETE FROM REPORTS" not in text_007
    assert "DROP TABLE" not in text_007
    assert "TRUNCATE" not in text_007


# --- F5 (repair): JSON Schema must reject free-form/mismatched records -----

def _load_schema():
    import json
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2]
        / "packages" / "workspace-contracts" / "reports" / "shift-report.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _real_public_document():
    """A genuine ReportResponse-shaped document (SPEC R2: the flat public
    shape the router exposes, content unpacked) built from a real Task via
    the real build_snapshot engine - not a hand-typed fixture."""
    from uuid import uuid4
    from datetime import datetime, timezone

    from operations_domain.models import Task
    from workspace_api.application import report_snapshot

    shift_id = uuid4()
    now = datetime.now(timezone.utc)
    task = Task(shift_id=shift_id, title="Check pumps", created_at=now)
    content = report_snapshot.build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[task],
        customer_requests=[], incidents=[], handovers=[],
    )
    return {
        "report_id": str(uuid4()), "shift_id": str(shift_id), "report_type": "END_SHIFT",
        "version": 1, "status": "DRAFT", "is_current": True,
        "sections": [s.model_dump(mode="json") for s in content.sections],
        "source_manifest": [m.model_dump(mode="json") for m in content.source_manifest],
        "snapshot_digest": content.snapshot_digest,
        "generated_from_cutoff": now.isoformat(),
        "created_at": now.isoformat(),
    }


def test_json_schema_accepts_a_real_generated_report():
    import jsonschema

    jsonschema.validate(_real_public_document(), _load_schema())


def test_json_schema_rejects_a_free_form_record_object():
    """The gap this repair closes: records.items used to be a bare
    {"type": "object"} - any object at all passed. A record with none of the
    real Task fields must now fail validation."""
    import jsonschema

    doc = _real_public_document()
    doc["sections"][2]["records"] = [{"anything": "goes", "record_type": "Task"}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, _load_schema())


def test_json_schema_rejects_record_with_extra_field():
    import jsonschema

    doc = _real_public_document()
    doc["sections"][2]["records"][0]["bogus_extra_field"] = "x"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, _load_schema())


def test_json_schema_rejects_record_type_mismatched_with_its_section():
    import jsonschema

    doc = _real_public_document()
    doc["sections"][2]["records"][0]["record_type"] = "Incident"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, _load_schema())


def test_json_schema_rejects_sections_out_of_order():
    import jsonschema

    doc = _real_public_document()
    doc["sections"] = list(reversed(doc["sections"]))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, _load_schema())


# Finding 1's four probe regressions (WRONG_FIELD_TYPES, SOURCE_VERSION_
# MISMATCH, SOURCE_DIGEST_MISMATCH, REVERSED_CANONICAL_ORDER), at the
# canonical model layer, live in tests/cvf/test_report_approval.py
# (file-size budget) - see _real_content()/test_probe_*/
# test_build_snapshot_output_is_accepted_by_the_canonical_model there.


def test_reversed_nested_handover_item_evidence_order_rejected():
    """Finding 1 (second repair): R7 evidence order enforced inside a
    Handover item's nested evidence list, not just a top-level record's."""
    from uuid import uuid4
    from operations_domain.models import ReportSection

    def _ev(n):
        return {"evidence_id": f"{n * 8}-{n * 4}-{n * 4}-{n * 4}-{n * 12}", "source_type": "doc", "source_id": "1", "sha256": None}

    item = {
        "item_id": str(uuid4()), "source_record_type": "Task", "source_record_id": str(uuid4()),
        "source_digest": "a" * 64, "summary": "s", "owner_id": None, "due_at": None,
        "risk_class": "R1", "evidence": [_ev("2"), _ev("1")],
    }
    record = {
        "record_type": "Handover", "record_id": str(uuid4()), "from_shift_id": str(uuid4()),
        "to_shift_id": str(uuid4()), "status": "DRAFT", "created_by": "op1", "reviewed_by": None,
        "reviewed_at": None, "received_by": None, "acknowledged_at": None, "version": 1,
        "created_at": "2026-01-01T00:00:00Z", "items": [item],
    }
    with pytest.raises(Exception):
        ReportSection(section_type="handovers", records=[record])
