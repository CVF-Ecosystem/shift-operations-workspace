"""Schema parity guard: tables.py must not drift from the SQL migration.

The SQL migration (database/migrations/001_foundation.sql) is the schema
authority. SqlLedger's tables.py mirrors part of it for the dual-backend
runtime. If someone adds a FK or CHECK to the migration but forgets tables.py
(or vice versa), SQLite and PostgreSQL would enforce different rules — the
drift that causes hard-to-debug integrity bugs later.

This test parses the migration and asserts that, for every table tables.py
*does* define, the referential (FK) and window CHECK constraints present in the
migration are also present in tables.py. Tables not yet mapped (messages,
approvals, tasks, ...) are out of scope until a tranche wires them.
"""

from __future__ import annotations

import re
from pathlib import Path

from operations_ledger.tables import (
    corrections,
    metadata,
    operational_events,
    shifts,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "database" / "migrations" / "001_foundation.sql"

# Tables tables.py currently maps -> their SQLAlchemy Table object.
MAPPED = {
    "shifts": shifts,
    "operational_events": operational_events,
    "corrections": corrections,
}


def _migration_text() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def _table_block(sql: str, table: str) -> str:
    """Return the CREATE TABLE (...) body for one table."""
    m = re.search(
        rf"CREATE TABLE IF NOT EXISTS {table}\s*\((.*?)\);",
        sql,
        re.DOTALL | re.IGNORECASE,
    )
    assert m, f"table {table} not found in migration"
    return m.group(1)


def test_mapped_tables_exist_in_migration():
    sql = _migration_text()
    for table in MAPPED:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql, table


def test_foreign_keys_match_migration():
    sql = _migration_text()
    for table, tbl_obj in MAPPED.items():
        block = _table_block(sql, table)
        # Referenced tables named in the migration's REFERENCES clauses.
        migration_refs = set(re.findall(r"REFERENCES\s+(\w+)\s*\(", block))
        code_refs = {
            fk.column.table.name
            for col in tbl_obj.columns
            for fk in col.foreign_keys
        }
        missing = migration_refs - code_refs
        assert not missing, (
            f"{table}: migration has FK -> {missing} but tables.py does not"
        )


def test_window_checks_present_where_migration_has_them():
    sql = _migration_text()
    # Tables whose migration block contains a CHECK must have >=1 CheckConstraint
    # in tables.py (we match on presence, not exact text, since dialects render
    # differently).
    from sqlalchemy import CheckConstraint

    for table, tbl_obj in MAPPED.items():
        block = _table_block(sql, table)
        if "CHECK" in block.upper():
            code_checks = [
                c for c in tbl_obj.constraints if isinstance(c, CheckConstraint)
            ]
            assert code_checks, (
                f"{table}: migration has a CHECK constraint but tables.py has none"
            )
