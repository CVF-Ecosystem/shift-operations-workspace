"""Shared migration-SQL text parsing for the schema-parity test modules.

Split out of test_schema_parity.py in P-FIX-6 (2026-07-22) purely to respect
the file-size guard (GC-023 style, hard limit 400 lines for *.py) after adding
type-family/default-compatibility/CHECK-expression checks - not a behavior
change. See test_schema_parity.py and test_schema_parity_types_and_checks.py
for the actual assertions; this module only has the text-parsing helpers both
share.

Not a general SQL parser - it is deliberately strict about the small, known
SQL dialect this repo's own migrations use (see database/migrations/*.sql).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "database" / "migrations"

# Table-level constraint keywords that are NOT column definitions.
_CONSTRAINT_KEYWORDS = ("CHECK", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CONSTRAINT")


def migration_text() -> str:
    # Concatenate all migration files so a mapped table can live in any of them.
    return "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(MIGRATIONS_DIR.glob("*.sql"))
    )


def table_block(sql: str, table: str) -> str:
    """Return the CREATE TABLE (...) body for one table."""
    m = re.search(
        rf"CREATE TABLE IF NOT EXISTS {table}\s*\((.*?)\);",
        sql,
        re.DOTALL | re.IGNORECASE,
    )
    assert m, f"table {table} not found in migration"
    return m.group(1)


def split_column_lines(block: str) -> list[str]:
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


def migration_columns(block: str) -> dict[str, dict]:
    """Parse column name -> {nullable, has_default, type, is_pk} from a
    CREATE TABLE body."""
    columns: dict[str, dict] = {}
    for line in split_column_lines(block):
        stripped = line.strip()
        upper = stripped.upper()
        if any(upper.startswith(kw) for kw in _CONSTRAINT_KEYWORDS):
            continue
        m = re.match(r"(\w+)\s+(\w+)", stripped)
        if not m:
            continue
        name, sql_type = m.group(1), m.group(2)
        # A PRIMARY KEY column is implicitly NOT NULL in SQL even when the
        # migration doesn't spell out "NOT NULL" (Postgres enforces this
        # regardless of whether it's written).
        is_pk = "PRIMARY KEY" in upper
        nullable = not is_pk and "NOT NULL" not in upper
        has_default = "DEFAULT" in upper
        columns[name] = {
            "nullable": nullable,
            "has_default": has_default,
            "type": sql_type.lower(),
            "is_pk": is_pk,
        }
    return columns


def code_columns(tbl_obj) -> dict[str, dict]:
    """Column name -> {nullable, has_default, type, is_pk}.

    has_default compatibility rule (P-FIX-6): a client-side SQLAlchemy
    ``default=`` (Python-side, e.g. ``default_factory=uuid4`` on the Pydantic
    model feeding a plain INSERT) legitimately does NOT need a matching
    PostgreSQL ``DEFAULT`` clause in the migration - the app always supplies
    the value before INSERT. A ``server_default=`` SHOULD correspond to an
    actual ``DEFAULT`` in the migration SQL, because it is a promise that the
    database itself will fill the value in when the app omits it. So
    ``has_default`` here reflects ``server_default`` only; ``client_default``
    is tracked separately and is deliberately never compared against the
    migration's has_default (see test_column_defaults_compatible).
    """
    return {
        col.name: {
            "nullable": bool(col.nullable),
            "has_default": col.server_default is not None,
            "client_default": col.default is not None,
            "type": col.type,
            "is_pk": bool(col.primary_key),
        }
        for col in tbl_obj.columns
    }
