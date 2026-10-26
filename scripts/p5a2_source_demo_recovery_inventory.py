"""One read-only PostgreSQL snapshot before any retained-volume seed write."""
from __future__ import annotations

import os
import re
import sys

from p5a2_source_demo_common import ROOT, digest, fail
from p5a2_source_demo_bootstrap import source_path

DATABASE = "shiftops_p5a2_source_demo"
TARGET = {"users": 1, "shifts": 36, "shift_assignments": 36, "reports": 37}
TABLE_RE = re.compile(r"\bCREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+([a-z][a-z0-9_]*)\b", re.I)


def expected_tables() -> frozenset[str]:
    migrations = sorted((ROOT / "database/migrations").glob("[0-9][0-9][0-9]_*.sql"))
    if len(migrations) != 11:
        raise fail("MIGRATION_SET_INVALID")
    names = []
    for path in migrations:
        names.extend(TABLE_RE.findall(path.read_text(encoding="utf-8")))
    if len(names) != 31 or len(set(names)) != 31:
        raise fail("MIGRATION_TABLE_SET_INVALID")
    return frozenset(names)


def required_columns() -> dict[str, set[str]]:
    for path in reversed(source_path().split(os.pathsep)):
        if path not in sys.path:
            sys.path.insert(0, path)
    from operations_ledger.tables import metadata
    return {name: set(table.columns.keys()) for name, table in metadata.tables.items()}


def classify_counts(counts: dict[str, int]) -> str:
    if set(counts) != expected_tables() or any(type(n) is not int or n < 0 for n in counts.values()):
        raise fail("TABLE_COUNT_SET_INVALID")
    if all(value == 0 for value in counts.values()):
        return "EMPTY_COMPATIBLE"
    if all(value == TARGET.get(name, 0) for name, value in counts.items()):
        return "EXACT_SEEDED"
    raise fail("PARTIAL_OR_FOREIGN_DATA")


def inventory(dsn: str) -> dict:
    import psycopg

    expected = expected_tables()
    native = required_columns()
    if not set(native).issubset(expected):
        raise fail("NATIVE_TABLE_SET_INVALID")
    # Autocommit prevents psycopg from implicitly beginning a prior default
    # transaction. BEGIN is the first database statement on this connection.
    with psycopg.connect(dsn, connect_timeout=5, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
            try:
                cur.execute("SHOW transaction_isolation")
                if cur.fetchone()[0] != "repeatable read":
                    raise fail("SQL_ISOLATION_INVALID")
                cur.execute("SHOW transaction_read_only")
                if cur.fetchone()[0] != "on":
                    raise fail("SQL_READ_ONLY_INVALID")
                cur.execute("SELECT current_database(), version()")
                database, version = cur.fetchone()
                if database != DATABASE or "PostgreSQL 16" not in version:
                    raise fail("DB_IDENTITY_INVALID")
                cur.execute("SELECT system_identifier FROM pg_control_system()")
                system_id = str(cur.fetchone()[0])
                cur.execute("SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname <> 'information_schema'")
                if {row[0] for row in cur.fetchall()} != {"public"}:
                    raise fail("SCHEMA_NAMESPACE_INVALID")
                cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                tables = {row[0] for row in cur.fetchall()}
                if tables != expected:
                    raise fail("SCHEMA_TABLE_SET_INVALID")
                cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public'")
                columns: dict[str, set[str]] = {}
                for table, column in cur.fetchall():
                    columns.setdefault(table, set()).add(column)
                if any(not required.issubset(columns.get(table, set()))
                       for table, required in native.items()):
                    raise fail("SCHEMA_COLUMNS_INVALID")
                counts = {}
                for name in sorted(expected):
                    cur.execute(f'SELECT count(*) FROM "{name}"')
                    counts[name] = cur.fetchone()[0]
                classification = classify_counts(counts)
            finally:
                cur.execute("ROLLBACK")
    return {"database": database, "postgresql_major": 16,
            "postgresql_version": version,
            "transaction_isolation": "repeatable read",
            "transaction_read_only": "on",
            "db_fingerprint": digest({"database": database,
                                      "system_identifier": system_id}),
            "schema_table_count": len(expected), "counts": counts,
            "classification": classification}


def post_seed_summary(dsn: str, expected_fingerprint: str) -> dict:
    """The one separately budgeted post-seed SQL summary connection."""
    import psycopg

    with psycopg.connect(dsn, connect_timeout=5, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
            try:
                cur.execute("SHOW transaction_isolation")
                isolation = cur.fetchone()[0]
                cur.execute("SHOW transaction_read_only")
                read_only = cur.fetchone()[0]
                cur.execute("SELECT current_database(), version()")
                database, version = cur.fetchone()
                cur.execute("SELECT system_identifier FROM pg_control_system()")
                system_id = str(cur.fetchone()[0])
                if (isolation != "repeatable read" or read_only != "on"
                        or database != DATABASE or "PostgreSQL 16" not in version
                        or digest({"database": database,
                                   "system_identifier": system_id}) != expected_fingerprint):
                    raise fail("POST_SEED_IDENTITY_INVALID")
                counts = {}
                for name in sorted(expected_tables()):
                    cur.execute(f'SELECT count(*) FROM "{name}"')
                    counts[name] = cur.fetchone()[0]
                if classify_counts(counts) != "EXACT_SEEDED":
                    raise fail("POST_SEED_COUNTS_INVALID")
            finally:
                cur.execute("ROLLBACK")
    return {"database": database, "postgresql_major": 16,
            "postgresql_version": version,
            "transaction_isolation": isolation,
            "transaction_read_only": read_only,
            "db_fingerprint": expected_fingerprint, "counts": counts}
