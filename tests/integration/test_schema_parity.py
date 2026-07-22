"""Schema parity guard: tables.py must not drift from the SQL migration.

The SQL migration (database/migrations/*.sql) is the schema authority
(PostgreSQL). SqlLedger's tables.py mirrors part of it for the dual-backend
runtime. If someone adds a column, FK, or CHECK to the migration but forgets
tables.py (or vice versa), SQLite and PostgreSQL enforce different rules and
INSERT/UPDATE statements the runtime always sends can fail against a
migration-created database - the drift that causes hard-to-debug integrity
bugs later.

2026-07-22 correction (Codex independent review, High Finding #3): the
previous version of this test only checked "table name exists", "FK target
table matches", and "at least one CheckConstraint exists" - it did NOT compare
columns, so it passed while tables.py declared a `version` column for `tasks`
that the migration did not have. A real PostgreSQL insert would have failed.
This version parses each migration table's column list (name, nullable,
has-default) and asserts an EXACT column-name match against tables.py, plus
matching nullability and FK targets. Running the raw migration SQL against a
throwaway database is not possible here: it uses PostgreSQL-only syntax
(CREATE EXTENSION, custom ENUM types, gen_random_uuid(), jsonb) that does not
parse on SQLite, and no PostgreSQL is available in this environment (see
docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md and
EXECUTION_ROADMAP.md P-FIX-4/P1-A). Column-level text parsing is therefore the
strongest check available without a live PostgreSQL instance; a live
migration-vs-tables.py verification remains the pre-ship gate once Docker is
available (see the database operating model in the Codex review).
"""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import CheckConstraint

from operations_ledger.tables import (
    corrections,
    metadata,
    operational_events,
    shifts,
    tasks,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "database" / "migrations"

# Tables tables.py currently maps -> their SQLAlchemy Table object.
MAPPED = {
    "shifts": shifts,
    "operational_events": operational_events,
    "corrections": corrections,
    "tasks": tasks,
}


def _migration_text() -> str:
    # Concatenate all migration files so a mapped table can live in any of them.
    return "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(MIGRATIONS_DIR.glob("*.sql"))
    )


def _table_block(sql: str, table: str) -> str:
    """Return the CREATE TABLE (...) body for one table."""
    m = re.search(
        rf"CREATE TABLE IF NOT EXISTS {table}\s*\((.*?)\);",
        sql,
        re.DOTALL | re.IGNORECASE,
    )
    assert m, f"table {table} not found in migration"
    return m.group(1)


def _split_column_lines(block: str) -> list[str]:
    """Split a CREATE TABLE body into one logical line per column/constraint,
    respecting parentheses (e.g. CHECK (...) may itself contain commas)."""
    lines: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in block:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            lines.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        lines.append(tail)
    return [ln for ln in lines if ln]


# Table-level constraint keywords that are NOT column definitions.
_CONSTRAINT_KEYWORDS = ("CHECK", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CONSTRAINT")


def _migration_columns(block: str) -> dict[str, dict]:
    """Parse column name -> {nullable, has_default} from a CREATE TABLE body.

    This is a text parser for a small, known SQL dialect (our own migrations),
    not a general SQL parser - it is deliberately strict about the patterns
    our migrations actually use.
    """
    columns: dict[str, dict] = {}
    for line in _split_column_lines(block):
        stripped = line.strip()
        upper = stripped.upper()
        if any(upper.startswith(kw) for kw in _CONSTRAINT_KEYWORDS):
            continue
        m = re.match(r"(\w+)\s+", stripped)
        if not m:
            continue
        name = m.group(1)
        # A PRIMARY KEY column is implicitly NOT NULL in SQL even when the
        # migration doesn't spell out "NOT NULL" (Postgres enforces this
        # regardless of whether it's written).
        is_pk = "PRIMARY KEY" in upper
        nullable = not is_pk and "NOT NULL" not in upper
        has_default = "DEFAULT" in upper
        columns[name] = {"nullable": nullable, "has_default": has_default}
    return columns


def _code_columns(tbl_obj) -> dict[str, dict]:
    return {
        col.name: {
            "nullable": bool(col.nullable),
            "has_default": col.server_default is not None or col.default is not None,
        }
        for col in tbl_obj.columns
    }


def test_mapped_tables_exist_in_migration():
    sql = _migration_text()
    for table in MAPPED:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql, table


def test_column_sets_match_exactly():
    """The Codex-found bug: tasks.version existed in tables.py but not in the
    migration. This asserts the two column NAME sets are identical."""
    sql = _migration_text()
    for table, tbl_obj in MAPPED.items():
        block = _table_block(sql, table)
        migration_cols = set(_migration_columns(block))
        code_cols = set(_code_columns(tbl_obj))
        code_only = code_cols - migration_cols
        migration_only = migration_cols - code_cols
        assert not code_only, (
            f"{table}: tables.py declares columns the migration does not have: "
            f"{sorted(code_only)} - a real PostgreSQL statement using these "
            f"columns will fail against a migration-created database"
        )
        assert not migration_only, (
            f"{table}: migration has columns tables.py does not map: "
            f"{sorted(migration_only)} - reads/writes silently ignore this data"
        )


def test_column_nullability_matches():
    sql = _migration_text()
    for table, tbl_obj in MAPPED.items():
        block = _table_block(sql, table)
        migration_cols = _migration_columns(block)
        code_cols = _code_columns(tbl_obj)
        for name in migration_cols.keys() & code_cols.keys():
            assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], (
                f"{table}.{name}: nullable mismatch - migration says "
                f"nullable={migration_cols[name]['nullable']}, tables.py says "
                f"nullable={code_cols[name]['nullable']}"
            )


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
    for table, tbl_obj in MAPPED.items():
        block = _table_block(sql, table)
        if "CHECK" in block.upper():
            code_checks = [
                c for c in tbl_obj.constraints if isinstance(c, CheckConstraint)
            ]
            assert code_checks, (
                f"{table}: migration has a CHECK constraint but tables.py has none"
            )
