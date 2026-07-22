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

2026-07-22 P-FIX-6 correction: after the P-FIX-5 closure claim was rejected by
a second independent review, this guard was widened per EXECUTION_ROADMAP.md
P-FIX-6 / task 5. This file now covers: table existence, exact column-name
match, nullability, primary key, foreign key (table+column), and default
compatibility (has_default now distinguishes client-side vs. server-side
defaults instead of collapsing both into one bool). Type-family and CHECK
-expression comparisons live in the sibling module
test_schema_parity_types_and_checks.py - split out purely to respect the
file-size guard (GC-023 style hard limit), not a behavior change; both modules
share parsing helpers from _schema_parity_parsing.py.

STILL NOT LIVE VERIFIED: everything here is static text-parsing of the
migration SQL compared against SQLAlchemy Table objects in memory. No
migration has ever been run against a live PostgreSQL instance in this
environment (no Docker daemon available) and this test module does not claim
otherwise. A live PostgreSQL round-trip (create schema from migration,
insert/read through SqlLedger, diff live pg_catalog against tables.py) remains
a PRE-SHIP GATE, run separately when Docker is available - not required for
ordinary SQLite-based development, and not something this test suite performs
or should be read as having performed.
"""

from __future__ import annotations

import re

from operations_ledger.tables import (
    corrections,
    metadata,
    operational_events,
    shifts,
    tasks,
)

from _schema_parity_parsing import (
    code_columns,
    migration_columns,
    migration_text,
    table_block,
)

# Tables tables.py currently maps -> their SQLAlchemy Table object.
MAPPED = {
    "shifts": shifts,
    "operational_events": operational_events,
    "corrections": corrections,
    "tasks": tasks,
}


def test_mapped_tables_exist_in_migration():
    sql = migration_text()
    for table in MAPPED:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql, table


def test_column_sets_match_exactly():
    """The Codex-found bug: tasks.version existed in tables.py but not in the
    migration. This asserts the two column NAME sets are identical."""
    sql = migration_text()
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        migration_cols = set(migration_columns(block))
        code_cols = set(code_columns(tbl_obj))
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
    sql = migration_text()
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        migration_cols = migration_columns(block)
        code_cols = code_columns(tbl_obj)
        for name in migration_cols.keys() & code_cols.keys():
            assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], (
                f"{table}.{name}: nullable mismatch - migration says "
                f"nullable={migration_cols[name]['nullable']}, tables.py says "
                f"nullable={code_cols[name]['nullable']}"
            )


# Primary-key UUID columns: the migration declares DEFAULT gen_random_uuid()
# as a safety net, but every INSERT this runtime issues supplies the value
# explicitly (Pydantic model_id fields use `Field(default_factory=uuid4)`,
# and _rows.py always includes the id in the row dict - verified by reading
# shift_row()/event_row()/task_row()/correction_row() in
# packages/operations-ledger/src/operations_ledger/_rows.py). That is a THIRD
# category beyond client-side-default/server-side-default: "always explicitly
# supplied by the row-builder before every INSERT", which SQLAlchemy has no
# `default=`/`server_default=` marker for because it isn't a SQLAlchemy-level
# default at all. Column-name allowlist, not a blanket PK exemption, so a
# newly added PK column without this same guarantee still gets checked.
_ALWAYS_EXPLICITLY_SUPPLIED_PK = {
    ("shifts", "shift_id"),
    ("operational_events", "event_id"),
    ("corrections", "correction_id"),
    ("tasks", "task_id"),
}


def test_column_defaults_compatible():
    """P-FIX-6: has_default was parsed for both sides but never compared.

    Compatibility rule (see _schema_parity_parsing.code_columns docstring):
    only require the migration's DEFAULT clause to line up with a SQLAlchemy
    server_default. A client-side-only default (col.default is not None,
    server_default is None) is fine whether or not the migration has a
    DEFAULT, because the app always supplies the value on INSERT and never
    relies on the database filling it in. Primary-key id columns get a third
    allowance - see _ALWAYS_EXPLICITLY_SUPPLIED_PK above.
    """
    sql = migration_text()
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        migration_cols = migration_columns(block)
        code_cols = code_columns(tbl_obj)
        for name in migration_cols.keys() & code_cols.keys():
            migration_has_default = migration_cols[name]["has_default"]
            code_has_server_default = code_cols[name]["has_default"]
            if code_has_server_default:
                assert migration_has_default, (
                    f"{table}.{name}: tables.py declares server_default= but "
                    f"the migration has no DEFAULT clause - a bare INSERT "
                    f"omitting this column would fail against a "
                    f"migration-created PostgreSQL database"
                )
            elif migration_has_default and not code_cols[name]["client_default"]:
                if (table, name) in _ALWAYS_EXPLICITLY_SUPPLIED_PK:
                    continue
                # Migration promises a DEFAULT that neither server_default=
                # nor a client-side default= backs up, and this column isn't
                # on the verified always-supplied-by-row-builder allowlist.
                # Not necessarily a bug (the runtime may still always supply
                # it), but worth flagging loudly rather than silently
                # ignoring - this is the same class of silent-drift Codex
                # found. If this is legitimately safe, verify it the same way
                # _ALWAYS_EXPLICITLY_SUPPLIED_PK was verified (read the row
                # builder) and add it there with a comment, rather than
                # weakening this branch.
                assert False, (
                    f"{table}.{name}: migration has DEFAULT but tables.py has "
                    f"neither server_default= nor a client-side default= - "
                    f"verify the runtime always supplies this column"
                )


def _migration_primary_key(block: str) -> set[str]:
    """Parse PRIMARY KEY column(s) from a CREATE TABLE body.

    Every mapped table in this repo's migrations uses the inline
    `col_name TYPE PRIMARY KEY` form (checked against database/migrations/*.sql
    directly - none use the table-level `PRIMARY KEY (col1, col2)` form), so
    only that form is parsed. If a future migration adds a table-level
    PRIMARY KEY, this function should be extended rather than silently
    returning an incomplete set.
    """
    inline_pk = {
        name for name, meta in migration_columns(block).items() if meta["is_pk"]
    }
    table_level = re.search(r"PRIMARY KEY\s*\(([^)]+)\)", block, re.IGNORECASE)
    if table_level:
        table_level_cols = {c.strip() for c in table_level.group(1).split(",")}
        return inline_pk | table_level_cols
    return inline_pk


def test_primary_key_matches():
    sql = migration_text()
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        migration_pk = _migration_primary_key(block)
        code_pk = set(tbl_obj.primary_key.columns.keys())
        assert migration_pk == code_pk, (
            f"{table}: primary key mismatch - migration says {sorted(migration_pk)}, "
            f"tables.py says {sorted(code_pk)}"
        )


def test_foreign_keys_match_migration():
    """Two-directional: a migration FK missing from tables.py silently drops a
    referential-integrity guarantee the runtime relies on (original P-FIX-6
    check); a tables.py FK the migration does NOT declare would make SQLite
    (which we run in dev/test) enforce a constraint PostgreSQL never will,
    passing tests locally while behaving differently in production - this
    second direction was missing until this closure-cleanup pass."""
    sql = migration_text()
    for table, tbl_obj in MAPPED.items():
        block = table_block(sql, table)
        # Referenced table+column pairs named in the migration's REFERENCES
        # clauses, e.g. "shift_id uuid NOT NULL REFERENCES shifts(shift_id)".
        migration_refs = {
            (ref_table, ref_col)
            for ref_table, ref_col in re.findall(
                r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", block
            )
        }
        code_refs = {
            (fk.column.table.name, fk.column.name)
            for col in tbl_obj.columns
            for fk in col.foreign_keys
        }
        missing_from_code = migration_refs - code_refs
        assert not missing_from_code, (
            f"{table}: migration has FK -> {missing_from_code} but tables.py "
            f"does not map a matching (table, column) foreign key"
        )
        missing_from_migration = code_refs - migration_refs
        assert not missing_from_migration, (
            f"{table}: tables.py declares FK -> {missing_from_migration} that "
            f"the migration does not - SQLite would enforce a constraint "
            f"PostgreSQL never will, diverging between dev/test and production"
        )
        # database/migrations/*.sql does not use ON DELETE/ON UPDATE anywhere
        # (verified by grep across both migration files) - no behavior to
        # compare here. If a future migration adds one, extend this test
        # rather than assuming FK-target parity is the whole story.
        assert "ON DELETE" not in block.upper() and "ON UPDATE" not in block.upper(), (
            f"{table}: migration now uses ON DELETE/ON UPDATE - extend "
            f"test_foreign_keys_match_migration to compare that behavior "
            f"against tables.py, this was not needed when the check was written"
        )
