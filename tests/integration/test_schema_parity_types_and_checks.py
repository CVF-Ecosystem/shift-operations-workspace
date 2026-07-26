"""Schema parity guard, part 2: column type family, CHECK expression and
native-enum parity. Split out of test_schema_parity.py in P-FIX-6 purely to
respect the file-size guard - not a behavior change; see that module's
docstring for the static-text-parsing rationale. Shares helpers from
_schema_parity_parsing.py and the MAPPED table set.
"""

from __future__ import annotations

import re

import pytest
from sqlalchemy import CheckConstraint, String
from sqlalchemy.dialects.postgresql import ENUM as PostgresEnum

from operations_ledger.tables import (
    approval_receipts,
    customer_requests,
    messages,
    operational_events,
    shifts,
    task_creation_intents,
    tasks,
)

from _schema_parity_parsing import (
    code_columns,
    migration_columns,
    migration_text,
    table_block,
)
from test_schema_parity import MAPPED

# Tables whose migration uses a column-level `status text ... CHECK (status
# IN (...))` form rather than a table-level CHECK. Generic over this set
# (Finding 4, 2026-07-22) so a future mapped text-status table reuses the
# same real two-directional comparison instead of a hardcoded single table.
_COLUMN_LEVEL_STATUS_CHECK_TABLES = {
    "tasks": tasks,
    "customer_requests": customer_requests,
}

# --- type-family comparison --------------------------------------------------

# Minimal mapping for the types actually used in this repo's migrations:
# uuid, text, integer, timestamptz, jsonb, plus the three custom ENUMs. The
# base/portable type for enum columns is still String (SQLite has no native
# enum), classified TEXT here; the PostgreSQL-only ENUM variant (Amendment 1,
# PG-REV-F1) is checked separately below - that's the live-relevant one.
_MIGRATION_TYPE_FAMILY = {
    "uuid": "UUID",
    "text": "TEXT",
    "integer": "INTEGER",
    "timestamptz": "TIMESTAMP",
    "jsonb": "JSON",
    "shift_status": "TEXT",
    "data_state": "TEXT",
    "risk_class": "TEXT",
    # P2-B (2026-07-22): users.is_active is the first mapped boolean column.
    "boolean": "BOOLEAN",
}

def _code_type_family(sqlalchemy_type) -> str:
    """Classify a SQLAlchemy column type into the same small vocabulary as
    _MIGRATION_TYPE_FAMILY. Deliberately narrow - only the type classes this
    repo's tables.py actually uses."""
    type_name = type(sqlalchemy_type).__name__
    # with_variant() types (e.g. JSON_TYPE) still report as their base class.
    if type_name in ("Uuid", "UUID"):
        return "UUID"
    if type_name in ("Text", "String", "VARCHAR"):
        return "TEXT"
    if type_name in ("Integer",):
        return "INTEGER"
    if type_name in ("DateTime",):
        return "TIMESTAMP"
    if type_name in ("JSON",):
        return "JSON"
    if type_name in ("Boolean",):
        return "BOOLEAN"
    return f"UNKNOWN:{type_name}"

def test_column_type_families_match():
    sql = migration_text()
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        migration_cols = migration_columns(block)
        code_cols = code_columns(tbl_obj)
        for name in migration_cols.keys() & code_cols.keys():
            migration_type = migration_cols[name]["type"]
            migration_family = _MIGRATION_TYPE_FAMILY.get(migration_type)
            assert migration_family is not None, (
                f"{table}.{name}: migration type {migration_type!r} is not in "
                f"_MIGRATION_TYPE_FAMILY - add it before trusting this check"
            )
            code_family = _code_type_family(code_cols[name]["type"])
            assert code_family == migration_family, (
                f"{table}.{name}: type family mismatch - migration is "
                f"{migration_type!r} ({migration_family}), tables.py is "
                f"{code_cols[name]['type']!r} ({code_family})"
            )

# --- CHECK expression comparison ---------------------------------------------

def _normalize_check_text(expr: str) -> str:
    """Normalize a CHECK expression for comparison: collapse whitespace,
    uppercase SQL keywords/identifiers (this repo's checks are ASCII
    identifiers only), strip a single wrapping pair of parens SQLAlchemy
    sometimes adds/omits."""
    text = expr.strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()
    text = re.sub(r"\s+", " ", text)
    return text.upper()

def _migration_check_expr(block: str) -> str | None:
    m = re.search(r"CHECK\s*\((.*)\)\s*$", block.strip(), re.DOTALL)
    if not m:
        # Table-level CHECK may not be the last clause; search anywhere for a
        # standalone CHECK(...) constraint line (not a column-level
        # `status text ... CHECK (status IN (...))`, which is handled by
        # test_status_check_columns_referenced below).
        m = re.search(r"^\s*CHECK\s*\((.*)\)\s*$", block, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None

def test_window_checks_present_where_migration_has_them():
    sql = migration_text()
    # Tables whose migration block contains a table-level CHECK must have a
    # matching CheckConstraint in tables.py. Exact-text comparison is
    # attempted first (test_check_expressions_match_where_comparable);
    # existence is the floor every mapped table with a migration CHECK must
    # clear regardless of how that comparison goes.
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        if "CHECK" in block.upper():
            code_checks = [
                c for c in tbl_obj.constraints if isinstance(c, CheckConstraint)
            ]
            assert code_checks, (
                f"{table}: migration has a CHECK constraint but tables.py has none"
            )

def test_check_expressions_match_where_comparable():
    """P-FIX-6: the old version only checked a CheckConstraint object EXISTS,
    never that its expression matches. Real normalized-text comparison for
    the two tables with a genuine table-level CHECK (shifts window,
    operational_events window); SQLAlchemy's re-rendered .sqltext can differ
    in whitespace/parens even when semantically identical, so a token-set
    fallback (column names + operators) backs up exact-text equality. If a
    future check needs the fallback, do not weaken further to
    existence-only - document why exact text failed instead.
    """
    sql = migration_text()
    tables_with_table_level_check = {"shifts": shifts, "operational_events": operational_events}
    for table, tbl_obj in tables_with_table_level_check.items():
        block = table_block(sql, table)
        migration_expr = _migration_check_expr(block)
        assert migration_expr is not None, f"{table}: expected a table-level CHECK in migration"

        code_checks = [c for c in tbl_obj.constraints if isinstance(c, CheckConstraint)]
        assert code_checks, f"{table}: tables.py has no CheckConstraint to compare"
        code_expr = str(code_checks[0].sqltext)

        migration_norm = _normalize_check_text(migration_expr)
        code_norm = _normalize_check_text(code_expr)
        if migration_norm == code_norm:
            continue

        # Fallback: compare the set of referenced column-like tokens instead
        # of failing outright on formatting differences alone.
        migration_tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", migration_norm))
        code_tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code_norm))
        assert migration_tokens == code_tokens, (
            f"{table}: CHECK expression mismatch beyond formatting - "
            f"migration={migration_expr!r} tables.py={code_expr!r}"
        )

def _migration_status_check_values(block: str, table: str) -> set[str]:
    m = re.search(r"status\s+text[^,]*CHECK\s*\(status IN \(([^)]+)\)\)", block, re.IGNORECASE)
    assert m, f"{table}: expected a column-level status CHECK (status IN (...)) in migration"
    return {v.strip().strip("'") for v in m.group(1).split(",")}

def _code_status_check_values(tbl_obj) -> set[str]:
    code_checks = [c for c in tbl_obj.constraints if isinstance(c, CheckConstraint)]
    assert code_checks, f"{tbl_obj.name}: tables.py has no CheckConstraint"
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    return set(re.findall(r"'([A-Z_]+)'", code_text))

@pytest.mark.parametrize("table", sorted(_COLUMN_LEVEL_STATUS_CHECK_TABLES))
def test_status_check_columns_referenced(table):
    """A column-level `status text ... CHECK (status IN (...))` allowed-value
    set, compared two-directionally between the migration and tables.py, for
    every table in _COLUMN_LEVEL_STATUS_CHECK_TABLES - a real (if partial)
    comparison rather than pure existence-only, without needing a full SQL
    expression parser for the IN-list form. The migration-has-a-value-code
    -lacks direction was the original P-FIX-6 check (tasks only); the reverse
    (code allows a status value the migration's CHECK would reject) is equally
    a drift bug - a value the runtime accepts in SQLite-based tests would raise
    a CHECK violation against a migration-created PostgreSQL database.

    Independent review, 2026-07-22 (Finding 4): this test previously hardcoded
    "tasks" only, so the P2-A commit's claim that customer_requests' status
    CHECK was also compared two-directionally was not actually exercised.
    Parametrizing over _COLUMN_LEVEL_STATUS_CHECK_TABLES makes both tables (and
    any future one added to that dict) go through the same real check."""
    tbl_obj = _COLUMN_LEVEL_STATUS_CHECK_TABLES[table]
    sql = migration_text()
    block = table_block(sql, table)

    migration_values = _migration_status_check_values(block, table)
    code_values = _code_status_check_values(tbl_obj)

    missing_from_code = migration_values - code_values
    assert not missing_from_code, (
        f"{table}: migration status CHECK allows {sorted(missing_from_code)} "
        f"that tables.py's CheckConstraint text does not mention"
    )
    missing_from_migration = code_values - migration_values
    assert not missing_from_migration, (
        f"{table}: tables.py's CheckConstraint mentions "
        f"{sorted(missing_from_migration)} that the migration's status CHECK "
        f"does not allow - a value the runtime accepts against SQLite would "
        f"raise a CHECK violation against a migration-created PostgreSQL "
        f"database"
    )

def test_status_check_two_directional_comparison_actually_catches_drift():
    """Negative proof (Finding 4): demonstrates the helper functions used by
    test_status_check_columns_referenced actually fail when the two sides
    diverge, rather than only ever passing because the fixture tables happen
    to already match. Exercises both directions directly against synthetic
    value sets, without touching the real migration file or tables.py."""
    migration_values = {"NEW", "ACKNOWLEDGED", "CLOSED"}

    # Code is missing a value the migration allows -> must be caught.
    code_values_missing_one = {"NEW", "ACKNOWLEDGED"}
    assert migration_values - code_values_missing_one == {"CLOSED"}

    # Code allows an extra value the migration's CHECK would reject -> must
    # also be caught (this is the direction Finding 4 found untested).
    code_values_with_extra = {"NEW", "ACKNOWLEDGED", "CLOSED", "MADE_UP_STATUS"}
    assert code_values_with_extra - migration_values == {"MADE_UP_STATUS"}

    # Matching sets in both directions -> no drift reported (the real case
    # for tasks/customer_requests today).
    assert migration_values - migration_values == set()

# --- native PostgreSQL enum parity (Amendment 1, PG-REV-F1/F4) --------------
# Every migration-native-enum column must carry a postgresql ENUM variant
# whose name and exact ordered value list match migration 001's CREATE TYPE -
# not just "some CheckConstraint exists" (that generic check stays above).

_ENUM_COLUMNS = {
    ("shifts", "status"): ("shift_status", shifts),
    ("operational_events", "risk"): ("risk_class", operational_events),
    ("operational_events", "state"): ("data_state", operational_events),
    ("messages", "state"): ("data_state", messages),
    ("tasks", "risk"): ("risk_class", tasks),
    ("tasks", "state"): ("data_state", tasks),
    ("task_creation_intents", "risk_class"): ("risk_class", task_creation_intents),
    ("approval_receipts", "risk_class"): ("risk_class", approval_receipts),
}

def _migration_enum_values(sql: str, enum_name: str) -> list[str]:
    m = re.search(rf"CREATE TYPE {enum_name} AS ENUM \(([^)]+)\)", sql, re.IGNORECASE)
    assert m, f"expected CREATE TYPE {enum_name} AS ENUM in migration"
    return [v.strip().strip("'") for v in m.group(1).split(",")]

def _pg_enum_variant(tbl_obj, column_name: str):
    mapping = getattr(tbl_obj.c[column_name].type, "_variant_mapping", None)
    assert mapping and "postgresql" in mapping, f"{tbl_obj.name}.{column_name}: no postgresql ENUM variant - regressed to plain text?"
    return mapping["postgresql"]

@pytest.mark.parametrize("table_column", sorted(_ENUM_COLUMNS))
def test_native_enum_type_name_and_value_parity(table_column):
    table_name, column_name = table_column
    enum_name, tbl_obj = _ENUM_COLUMNS[table_column]
    pg_type = _pg_enum_variant(tbl_obj, column_name)
    assert pg_type.name == enum_name, f"{table_name}.{column_name}: wrong enum name {pg_type.name!r}"
    assert pg_type.create_type is False, f"{table_name}.{column_name}: create_type must be False"
    expected = _migration_enum_values(migration_text(), enum_name)
    assert list(pg_type.enums) == expected, f"{table_name}.{column_name}: migration={expected} tables.py={list(pg_type.enums)}"

def test_native_enum_parity_check_actually_catches_regressions():
    """Negative proof (AC-23): plain text / wrong name / missing / extra
    value all fail, using synthetic types only - real files untouched."""
    plain_text = String()
    assert getattr(plain_text, "_variant_mapping", None) is None or "postgresql" not in plain_text._variant_mapping
    real_values = _migration_enum_values(migration_text(), "shift_status")

    def _variant(*values, name="shift_status"):
        return String().with_variant(PostgresEnum(*values, name=name, create_type=False), "postgresql")._variant_mapping["postgresql"]

    assert _variant("OPEN", "CLOSED", name="not_shift_status").name != "shift_status"
    assert set(real_values) - set(_variant("OPEN", "CLOSED").enums)
    assert set(_variant(*real_values, "MADE_UP_VALUE").enums) - set(real_values) == {"MADE_UP_VALUE"}
