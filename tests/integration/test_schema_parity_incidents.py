"""Schema parity: incidents table (fifth vertical, P2-A).

Self-contained module - unlike the sibling tables in test_schema_parity.py /
test_schema_parity_types_and_checks.py, this does not extend the shared
``MAPPED`` dict (that module is outside this tranche's authorized changed
set). It performs the SAME class of two-directional checks - column set,
nullability, PK, FK, defaults, type family, CHECK values, native PostgreSQL
enum parity - scoped to `incidents` only, sharing only the generic text-parsing
helpers from `_schema_parity_parsing.py`.
"""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint

from operations_ledger.tables import incidents

from _schema_parity_parsing import (
    code_columns,
    migration_columns,
    migration_text,
    table_block,
)

_TABLE = "incidents"


def _block() -> str:
    return table_block(migration_text(), _TABLE)


def test_incidents_table_exists_in_migration():
    assert f"CREATE TABLE IF NOT EXISTS {_TABLE}" in migration_text()


def test_incidents_column_sets_match_exactly():
    migration_cols = set(migration_columns(_block()))
    code_cols = set(code_columns(incidents))
    assert not (code_cols - migration_cols), sorted(code_cols - migration_cols)
    assert not (migration_cols - code_cols), sorted(migration_cols - code_cols)


def test_incidents_column_nullability_matches():
    migration_cols = migration_columns(_block())
    code_cols = code_columns(incidents)
    for name in migration_cols.keys() & code_cols.keys():
        assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], name


def test_incidents_primary_key_matches():
    migration_pk = {n for n, meta in migration_columns(_block()).items() if meta["is_pk"]}
    code_pk = set(incidents.primary_key.columns.keys())
    assert migration_pk == code_pk == {"incident_id"}


def test_incidents_foreign_key_matches_migration():
    block = _block()
    migration_refs = {
        (ref_table, ref_col)
        for ref_table, ref_col in re.findall(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", block)
    }
    code_refs = {
        (fk.column.table.name, fk.column.name)
        for col in incidents.columns
        for fk in col.foreign_keys
    }
    assert migration_refs == code_refs == {("shifts", "shift_id")}


def test_incidents_status_check_values_two_directional():
    m = re.search(r"status\s+text[^,]*CHECK\s*\(status IN \(([^)]+)\)\)", _block(), re.IGNORECASE)
    assert m, "expected a column-level status CHECK (status IN (...)) in migration"
    migration_values = {v.strip().strip("'") for v in m.group(1).split(",")}

    code_checks = [c for c in incidents.constraints if isinstance(c, CheckConstraint)]
    assert code_checks, "incidents: tables.py has no CheckConstraint"
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    code_values = set(re.findall(r"'([A-Z_]+)'", code_text))

    assert migration_values == code_values == {
        "REPORTED", "ACKNOWLEDGED", "MITIGATING", "RESOLVED", "CLOSED",
    }


def test_incidents_risk_column_is_native_postgresql_enum():
    """Amendment 1 pattern (PG-REV-F1): the risk column must carry a native
    PostgreSQL ENUM variant bound to the exact migration-owned `risk_class`
    type, not a bare portable String, so real PostgreSQL accepts inserts."""
    mapping = getattr(incidents.c.risk.type, "_variant_mapping", None)
    assert mapping and "postgresql" in mapping, "incidents.risk: no postgresql ENUM variant"
    pg_type = mapping["postgresql"]
    assert pg_type.name == "risk_class"
    assert pg_type.create_type is False
    expected = [v.strip().strip("'") for v in re.search(
        r"CREATE TYPE risk_class AS ENUM \(([^)]+)\)", migration_text(), re.IGNORECASE
    ).group(1).split(",")]
    assert list(pg_type.enums) == expected


def test_incidents_version_check_present_two_directional():
    """INC-REV-F4: `version >= 1` must exist identically on both sides - a
    migration CHECK the SQLAlchemy CheckConstraint doesn't mirror would let
    SQLite accept a row a real PostgreSQL database would reject, and vice
    versa."""
    block = _block()
    assert re.search(r"version\s+integer[^,]*CHECK\s*\(\s*version\s*>=\s*1\s*\)", block, re.IGNORECASE), (
        "expected a column-level version CHECK (version >= 1) in migration"
    )
    code_checks = [c for c in incidents.constraints if isinstance(c, CheckConstraint)]
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    assert re.search(r"version\s*>=\s*1", code_text), "incidents: tables.py has no version >= 1 CheckConstraint"


def test_incidents_default_compatible():
    migration_cols = migration_columns(_block())
    code_cols = code_columns(incidents)
    for name in ("risk", "status", "version", "created_at"):
        assert migration_cols[name]["has_default"]
        assert code_cols[name]["has_default"], f"incidents.{name}: tables.py has no server_default"
