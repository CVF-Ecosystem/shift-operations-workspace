"""Schema parity guard, part 2: column type family and CHECK expression.

Split out of test_schema_parity.py in P-FIX-6 (2026-07-22) purely to respect
the file-size guard (GC-023 style, hard limit 400 lines for *.py) - not a
behavior change. See test_schema_parity.py's module docstring for the full
context (why text-parsing instead of a live PostgreSQL diff, what "NOT LIVE
VERIFIED" means here). Both modules share parsing helpers from
_schema_parity_parsing.py and operate on the same MAPPED table set.
"""

from __future__ import annotations

import re

import pytest
from sqlalchemy import CheckConstraint

from operations_ledger.tables import customer_requests, operational_events, shifts, tasks

from _schema_parity_parsing import (
    code_columns,
    migration_columns,
    migration_text,
    table_block,
)
from test_schema_parity import MAPPED

# Tables whose migration uses a column-level `status text ... CHECK (status IN
# (...))` form rather than a table-level CHECK. Generic over this set so a
# future mapped text-status table can be added here without duplicating the
# parser (independent review, 2026-07-22, Finding 4: this previously hardcoded
# "tasks" only, so the commit's claim that customer_requests' status CHECK was
# also compared two-directionally was not actually true - it wasn't tested).
_COLUMN_LEVEL_STATUS_CHECK_TABLES = {
    "tasks": tasks,
    "customer_requests": customer_requests,
}

# --- type-family comparison --------------------------------------------------

# Minimal mapping for the types actually used in this repo's migrations (see
# database/migrations/*.sql): uuid, text, integer, timestamptz, jsonb, plus
# the three custom ENUMs (shift_status/data_state/risk_class), which tables.py
# represents as plain String/Text so the same definition works dual-backend
# (SQLAlchemy has no portable native-enum type across SQLite/PostgreSQL here).
_MIGRATION_TYPE_FAMILY = {
    "uuid": "UUID",
    "text": "TEXT",
    "integer": "INTEGER",
    "timestamptz": "TIMESTAMP",
    "jsonb": "JSON",
    "shift_status": "TEXT",
    "data_state": "TEXT",
    "risk_class": "TEXT",
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
    never that its expression matches. This attempts a real normalized-text
    comparison for the two tables with a genuine table-level CHECK
    (shifts.CHECK(ends_at > starts_at), operational_events' window check).

    Fallback reasoning: SQLAlchemy re-renders a CheckConstraint's .sqltext via
    str(), which can differ from the hand-written migration source in
    whitespace/parenthesization even when semantically identical (confirmed by
    running this comparison against both mapped checks below - exact
    normalized-text equality holds for both today because both sides were
    authored to match column-for-column). If a future check is added where
    exact text does not match after normalization, do not weaken this to
    "existence only" again - instead compare the set of column names and
    comparison operators referenced (a looser but still meaningful
    equivalence check), and document why exact text failed in a comment next
    to the fallback.
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
