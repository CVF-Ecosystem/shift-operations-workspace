"""Schema parity: shift_assignments table (P2C-MUTATION-FULL-UI-C3A1).

Mirrors test_schema_parity_incidents.py's self-contained pattern: column set,
nullability, PK, FK, defaults, CHECK values and default-compatibility, scoped
to `shift_assignments` only, sharing the generic text-parsing helpers from
`_schema_parity_parsing.py`.
"""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint

from operations_ledger.tables import shift_assignments

from _schema_parity_parsing import (
    code_columns,
    migration_columns,
    migration_text,
    table_block,
)

_TABLE = "shift_assignments"


def _block() -> str:
    return table_block(migration_text(), _TABLE)


def test_shift_assignments_table_exists_in_migration():
    assert f"CREATE TABLE IF NOT EXISTS {_TABLE}" in migration_text()


def test_shift_assignments_column_sets_match_exactly():
    migration_cols = set(migration_columns(_block()))
    code_cols = set(code_columns(shift_assignments))
    assert not (code_cols - migration_cols), sorted(code_cols - migration_cols)
    assert not (migration_cols - code_cols), sorted(migration_cols - code_cols)


def test_shift_assignments_column_nullability_matches():
    migration_cols = migration_columns(_block())
    code_cols = code_columns(shift_assignments)
    for name in migration_cols.keys() & code_cols.keys():
        assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], name


def test_shift_assignments_primary_key_matches():
    migration_pk = {n for n, meta in migration_columns(_block()).items() if meta["is_pk"]}
    code_pk = set(shift_assignments.primary_key.columns.keys())
    assert migration_pk == code_pk == {"assignment_id"}


def test_shift_assignments_foreign_keys_match_migration():
    block = _block()
    migration_refs = {
        (ref_table, ref_col)
        for ref_table, ref_col in re.findall(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", block)
    }
    code_refs = {
        (fk.column.table.name, fk.column.name)
        for col in shift_assignments.columns
        for fk in col.foreign_keys
    }
    assert migration_refs == code_refs == {("shifts", "shift_id"), ("users", "user_id")}


def test_shift_assignments_status_check_values_two_directional():
    m = re.search(r"status\s+text[^,]*CHECK\s*\(status IN \(([^)]+)\)\)", _block(), re.IGNORECASE)
    assert m, "expected a column-level status CHECK (status IN (...)) in migration"
    migration_values = {v.strip().strip("'") for v in m.group(1).split(",")}

    code_checks = [c for c in shift_assignments.constraints if isinstance(c, CheckConstraint)]
    assert code_checks, "shift_assignments: tables.py has no CheckConstraint"
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    code_values = set(re.findall(r"'([A-Z]+)'", code_text))

    assert migration_values == code_values == {"ACTIVE", "REVOKED"}


def test_shift_assignments_version_check_present_two_directional():
    block = _block()
    assert re.search(r"version\s+integer[^,]*CHECK\s*\(\s*version\s*>=\s*1\s*\)", block, re.IGNORECASE), (
        "expected a column-level version CHECK (version >= 1) in migration"
    )
    code_checks = [c for c in shift_assignments.constraints if isinstance(c, CheckConstraint)]
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    assert re.search(r"version\s*>=\s*1", code_text), "shift_assignments: tables.py has no version >= 1 CheckConstraint"


def test_shift_assignments_default_compatible():
    migration_cols = migration_columns(_block())
    code_cols = code_columns(shift_assignments)
    for name in ("status", "assigned_at", "version"):
        assert migration_cols[name]["has_default"]
        assert code_cols[name]["has_default"], f"shift_assignments.{name}: tables.py has no server_default"


def test_shift_assignments_active_unique_index_present_in_migration():
    """R2: at most one ACTIVE assignment per (shift_id, user_id)."""
    assert "shift_assignments_active_unique" in migration_text()
    assert re.search(
        r"CREATE UNIQUE INDEX IF NOT EXISTS shift_assignments_active_unique",
        migration_text(),
        re.IGNORECASE,
    )
