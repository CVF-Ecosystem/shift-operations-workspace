"""Schema parity: handovers/handover_items tables (P2A-HANDOVER-VERTICAL).

Self-contained module - like test_schema_parity_incidents.py, this does not
extend the shared ``MAPPED`` dict (outside this tranche's authorized changed
set). Performs the SAME class of two-directional checks - column set,
nullability, PK, FK, defaults, CHECK values, native PostgreSQL enum parity -
scoped to ``handovers``/``handover_items``, sharing only the generic
text-parsing helpers from ``_schema_parity_parsing.py``.
"""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint

from operations_ledger.tables import handover_items, handovers

from _schema_parity_parsing import (
    code_columns,
    migration_columns,
    migration_text,
    table_block,
)


def _block(table: str) -> str:
    return table_block(migration_text(), table)


def test_handovers_and_handover_items_tables_exist_in_migration():
    assert "CREATE TABLE IF NOT EXISTS handovers" in migration_text()
    assert "CREATE TABLE IF NOT EXISTS handover_items" in migration_text()


def test_handovers_column_sets_match_exactly():
    migration_cols = set(migration_columns(_block("handovers")))
    code_cols = set(code_columns(handovers))
    assert not (code_cols - migration_cols), sorted(code_cols - migration_cols)
    assert not (migration_cols - code_cols), sorted(migration_cols - code_cols)


def test_handover_items_column_sets_match_exactly():
    migration_cols = set(migration_columns(_block("handover_items")))
    code_cols = set(code_columns(handover_items))
    assert not (code_cols - migration_cols), sorted(code_cols - migration_cols)
    assert not (migration_cols - code_cols), sorted(migration_cols - code_cols)


def test_handovers_column_nullability_matches():
    migration_cols = migration_columns(_block("handovers"))
    code_cols = code_columns(handovers)
    for name in migration_cols.keys() & code_cols.keys():
        assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], name


def test_handovers_primary_key_matches():
    migration_pk = {n for n, meta in migration_columns(_block("handovers")).items() if meta["is_pk"]}
    code_pk = set(handovers.primary_key.columns.keys())
    assert migration_pk == code_pk == {"handover_id"}


def test_handover_items_primary_key_matches():
    migration_pk = {n for n, meta in migration_columns(_block("handover_items")).items() if meta["is_pk"]}
    code_pk = set(handover_items.primary_key.columns.keys())
    assert migration_pk == code_pk == {"item_id"}


def test_handovers_foreign_keys_match_migration():
    block = _block("handovers")
    migration_refs = {
        (ref_table, ref_col)
        for ref_table, ref_col in re.findall(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", block)
    }
    code_refs = {
        (fk.column.table.name, fk.column.name)
        for col in handovers.columns
        for fk in col.foreign_keys
    }
    assert migration_refs == code_refs == {("shifts", "shift_id")}


def test_handover_items_foreign_key_matches_migration():
    block = _block("handover_items")
    migration_refs = {
        (ref_table, ref_col)
        for ref_table, ref_col in re.findall(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", block)
    }
    code_refs = {
        (fk.column.table.name, fk.column.name)
        for col in handover_items.columns
        for fk in col.foreign_keys
    }
    assert migration_refs == code_refs == {("handovers", "handover_id")}


def test_handover_items_source_type_check_two_directional():
    m = re.search(
        r"source_record_type\s+text[^,]*CHECK\s*\(source_record_type IN \(([^)]+)\)\)",
        _block("handover_items"), re.IGNORECASE,
    )
    assert m, "expected a column-level source_record_type CHECK in migration"
    migration_values = {v.strip().strip("'") for v in m.group(1).split(",")}

    code_checks = [c for c in handover_items.constraints if isinstance(c, CheckConstraint)]
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    code_values = set(re.findall(r"'([A-Za-z]+)'", code_text))

    assert migration_values == code_values == {"Task", "CustomerRequest", "Incident"}


def test_handovers_version_check_present_two_directional():
    block = _block("handovers")
    assert re.search(r"version\s+integer[^,]*CHECK\s*\(\s*version\s*>=\s*1\s*\)", block, re.IGNORECASE)
    code_checks = [c for c in handovers.constraints if isinstance(c, CheckConstraint)]
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    assert re.search(r"version\s*>=\s*1", code_text)


def test_handovers_shift_pair_check_present_two_directional():
    block = _block("handovers")
    assert re.search(r"CHECK\s*\(\s*from_shift_id\s*<>\s*to_shift_id\s*\)", block, re.IGNORECASE)
    code_checks = [c for c in handovers.constraints if isinstance(c, CheckConstraint)]
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    assert re.search(r"from_shift_id\s*<>\s*to_shift_id", code_text)


def test_handover_items_unique_source_per_handover_two_directional():
    block = _block("handover_items")
    assert re.search(
        r"UNIQUE\s*\(\s*handover_id\s*,\s*source_record_type\s*,\s*source_record_id\s*\)",
        block, re.IGNORECASE,
    )
    unique_cols = {tuple(c.columns.keys()) for c in handover_items.constraints if hasattr(c, "columns") and c.__class__.__name__ == "UniqueConstraint"}
    assert ("handover_id", "source_record_type", "source_record_id") in unique_cols


def test_handovers_status_column_is_native_postgresql_enum():
    """Mirrors the incident risk-column pattern: handovers.status must carry a
    native PostgreSQL ENUM variant bound to the migration-owned
    ``handover_status`` type, not a bare portable String."""
    mapping = getattr(handovers.c.status.type, "_variant_mapping", None)
    assert mapping and "postgresql" in mapping, "handovers.status: no postgresql ENUM variant"
    pg_type = mapping["postgresql"]
    assert pg_type.name == "handover_status"
    assert pg_type.create_type is False
    expected = [v.strip().strip("'") for v in re.search(
        r"CREATE TYPE handover_status AS ENUM \(([^)]+)\)", migration_text(), re.IGNORECASE
    ).group(1).split(",")]
    assert list(pg_type.enums) == expected


def test_handover_items_risk_column_is_native_postgresql_enum():
    mapping = getattr(handover_items.c.risk.type, "_variant_mapping", None)
    assert mapping and "postgresql" in mapping
    pg_type = mapping["postgresql"]
    assert pg_type.name == "risk_class"
    assert pg_type.create_type is False


def test_handovers_default_compatible():
    migration_cols = migration_columns(_block("handovers"))
    code_cols = code_columns(handovers)
    for name in ("status", "version", "created_at"):
        assert migration_cols[name]["has_default"]
        assert code_cols[name]["has_default"], f"handovers.{name}: tables.py has no server_default"
