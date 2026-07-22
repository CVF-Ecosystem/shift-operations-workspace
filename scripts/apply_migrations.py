#!/usr/bin/env python3
"""Apply database/migrations/*.sql to an existing database, idempotently.

P2B-AUTHENTICATION-REPAIR (T3). docker-compose.yml mounts
database/migrations into /docker-entrypoint-initdb.d, which PostgreSQL only
executes when the data directory is initialized for the FIRST time. A
deployment whose postgres_data volume predates 003_users.sql therefore never
gains the `users` table, and login/seed fail with "users table does not
exist". This script is the upgrade path for that case.

Idempotency is enforced HERE, at the runner, not by assuming the SQL is
self-guarding:

* `CREATE TABLE IF NOT EXISTS` (every table in every migration) is already
  safe to re-run - verified by tests/integration/test_migration_idempotency_guard.py.
* `CREATE TYPE ... AS ENUM` (001_foundation.sql lines 3-5) is NOT and cannot
  be: PostgreSQL has no `CREATE TYPE IF NOT EXISTS`. Re-running 001 against
  an existing database raises duplicate_object (SQLSTATE 42710).

So this runner executes statement-by-statement and treats "this object
already exists" as success. That makes re-application safe without editing
the migration files themselves (which are the schema authority and are
deliberately not modified by this tranche).

NOT a migration-tracking system: there is no schema_migrations table and no
applied-hash bookkeeping. It re-runs everything and relies on the tolerance
above. That is proportionate for this schema's size; if migrations ever gain
destructive or non-repeatable statements (ALTER/DROP/INSERT), this approach
stops being safe and a real tracking table becomes necessary.

RUNBOOK
-------
Upgrading an existing deployment that predates 003_users.sql (the case that
motivated this script - symptom: login/seed fail with "users table does not
exist"), WITHOUT deleting the postgres_data volume:

    # 1. See what would run; confirms the file list and statement counts.
    python scripts/apply_migrations.py --dry-run

    # 2. Apply. Safe to run against a database that already has 001+002:
    #    existing tables/types are detected and skipped, not recreated.
    python scripts/apply_migrations.py

    # Or apply just the new migration:
    python scripts/apply_migrations.py --only 003_users.sql

    # 3. Verify, then seed dev users if this is a dev/test environment:
    python scripts/seed_dev_users.py

Re-running step 2 any number of times is a no-op. No data is modified: every
statement in these migrations is CREATE-only (no ALTER/DROP/INSERT).

PostgreSQL only. These migrations use PostgreSQL-specific syntax
(CREATE EXTENSION, custom ENUM types, gen_random_uuid(), jsonb,
DEFAULT now()) and will NOT run against SQLite - confirmed by attempting it.
SQLite development uses metadata.create_all() from tables.py instead.

DATABASE_URL is read from the environment when --database-url is omitted.
The URL is never printed in full (it usually embeds a password).

NOT LIVE VERIFIED: no PostgreSQL is available in this environment, so this
script's real end-to-end behaviour against a running 001+002 database has
never been executed - only its statement splitting, error-tolerance decision
logic, and redaction are covered by tests
(tests/integration/test_migration_idempotency_guard.py). A live run remains a
pre-ship gate, consistent with every other PostgreSQL claim in this repo.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = REPO_ROOT / "database" / "migrations"

# Same standalone-script bootstrap scripts/seed_dev_users.py already uses:
# this file is run directly (not via pytest, which supplies these roots from
# pyproject.toml), so the package source dirs must be added explicitly.
for _rel in ("packages/operations-ledger/src", "packages/cvf-runtime/src"):
    sys.path.insert(0, str(REPO_ROOT / _rel))

# PostgreSQL SQLSTATEs meaning "the thing you asked me to create is already
# there". Treated as success so re-application is a no-op.
_ALREADY_EXISTS_SQLSTATES = {
    "42710",  # duplicate_object   - e.g. CREATE TYPE of an existing enum
    "42P07",  # duplicate_table    - e.g. CREATE TABLE without IF NOT EXISTS
    "42P06",  # duplicate_schema
    "42723",  # duplicate_function
}


def redact_url(url: str) -> str:
    """Show driver and host/database, never credentials."""
    return re.sub(r"//[^@/]*@", "//<redacted>@", url)


def split_statements(sql: str) -> list[str]:
    """Split a migration file into top-level statements.

    Semicolon-delimited, but ignoring semicolons inside parentheses (CHECK
    constraints), single-quoted literals (enum values), and dollar-quoted
    blocks. These migrations use no dollar-quoted bodies today; the branch
    exists so adding one later does not silently corrupt the split.
    """
    statements: list[str] = []
    current: list[str] = []
    depth = 0
    in_single_quote = False
    in_dollar_block = False
    i = 0
    while i < len(sql):
        ch = sql[i]

        if in_dollar_block:
            current.append(ch)
            if sql.startswith("$$", i):
                current.append(sql[i + 1])
                i += 2
                in_dollar_block = False
                continue
            i += 1
            continue

        if in_single_quote:
            current.append(ch)
            if ch == "'":
                in_single_quote = False
            i += 1
            continue

        if sql.startswith("$$", i):
            current.append(sql[i])
            current.append(sql[i + 1])
            i += 2
            in_dollar_block = True
            continue

        if ch == "'":
            in_single_quote = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == ";" and depth == 0:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return [s for s in statements if not _is_comment_only(s)]


def _is_comment_only(statement: str) -> bool:
    for line in statement.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            return False
    return True


def migration_files(only: str | None = None) -> list[Path]:
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if only:
        files = [p for p in files if p.name == only]
        if not files:
            raise SystemExit(f"no migration named {only!r} in {MIGRATIONS_DIR}")
    return files


def _sqlstate_of(exc: BaseException) -> str | None:
    orig = getattr(exc, "orig", exc)
    return getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)


def apply_all(database_url: str, only: str | None = None, dry_run: bool = False) -> int:
    files = migration_files(only)
    if dry_run:
        for path in files:
            statements = split_statements(path.read_text(encoding="utf-8"))
            print(f"{path.name}: {len(statements)} statement(s)")
        print(f"DRY RUN - nothing executed against {redact_url(database_url)}")
        return 0

    try:
        from sqlalchemy import text

        from operations_ledger.sql_ledger import make_engine
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise SystemExit(
            f"SQLAlchemy (and a driver such as psycopg for PostgreSQL) is required: {exc}"
        ) from exc

    engine = make_engine(database_url)
    applied = skipped = 0
    print(f"applying {len(files)} migration file(s) to {redact_url(database_url)}")
    for path in files:
        statements = split_statements(path.read_text(encoding="utf-8"))
        for index, statement in enumerate(statements, start=1):
            # Each statement gets its own transaction so that tolerating one
            # "already exists" failure does not abort the rest of the file
            # (PostgreSQL aborts the whole transaction after an error).
            try:
                with engine.begin() as conn:
                    conn.execute(text(statement))
                applied += 1
            except Exception as exc:  # noqa: BLE001 - re-raised unless tolerated
                if _sqlstate_of(exc) in _ALREADY_EXISTS_SQLSTATES:
                    skipped += 1
                    continue
                preview = " ".join(statement.split())[:80]
                print(
                    f"FAILED {path.name} statement {index}: {preview}...",
                    file=sys.stderr,
                )
                raise
        print(f"  {path.name}: ok")
    print(f"done - {applied} statement(s) applied, {skipped} already present")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL", ""))
    parser.add_argument("--only", help="apply a single migration file by name")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL is not set (pass --database-url or set the env var)")
    return apply_all(args.database_url, only=args.only, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
