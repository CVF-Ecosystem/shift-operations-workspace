"""Migration re-application safety guard (P2B-AUTHENTICATION-REPAIR, T3).

AC-11 of docs/specs/P2B_AUTHENTICATION_REPAIR_SPEC.md.

Context: docker-compose.yml mounts database/migrations into
/docker-entrypoint-initdb.d, which PostgreSQL runs ONLY on first-time data
directory initialization. An existing postgres_data volume predating
003_users.sql never gains the users table, so an upgrade path is needed -
scripts/apply_migrations.py. That runner re-applies every migration, which
is only safe if re-application is a no-op.

This module pins the two halves of that safety property:

1. Every CREATE TABLE is IF NOT EXISTS guarded (true today; must stay true).
2. CREATE TYPE ... AS ENUM is NOT guarded and cannot be (PostgreSQL has no
   CREATE TYPE IF NOT EXISTS) - which is exactly why the runner tolerates
   duplicate_object rather than assuming the SQL is self-guarding.

NOT LIVE VERIFIED: this is static parsing, like the rest of this repo's
schema-parity suite. No PostgreSQL is available in this environment, so the
live "apply 003 onto a running 001+002 database, then apply again" round
trip remains a pre-ship gate. This module does not claim to have run it.
"""

from __future__ import annotations

import re
import sys

import pytest

from _schema_parity_parsing import MIGRATIONS_DIR, REPO_ROOT

# scripts/ is not on pytest's pythonpath (pyproject.toml lists only the app
# and package source roots, and is outside this tranche's authorized changed
# set). Add it here rather than widening the global test configuration for
# one module's import.
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from apply_migrations import (  # noqa: E402
    _ALREADY_EXISTS_SQLSTATES,
    _sqlstate_of,
    redact_url,
    split_statements,
)

_CREATE_TABLE_RE = re.compile(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?(\w+)", re.IGNORECASE)


def _migration_paths():
    paths = sorted(MIGRATIONS_DIR.glob("*.sql"))
    assert paths, "no migration files found - the guard would vacuously pass"
    return paths


def _unguarded_create_tables(sql: str) -> list[str]:
    return [
        match.group(2)
        for match in _CREATE_TABLE_RE.finditer(sql)
        if match.group(1) is None
    ]


# --- AC-11: every CREATE TABLE is re-application safe ------------------------


def test_every_create_table_is_if_not_exists_guarded():
    offenders: list[str] = []
    for path in _migration_paths():
        for table in _unguarded_create_tables(path.read_text(encoding="utf-8")):
            offenders.append(f"{path.name}:{table}")
    assert not offenders, (
        "these CREATE TABLE statements lack IF NOT EXISTS, so re-applying "
        f"their migration against an existing database fails: {offenders}. "
        "scripts/apply_migrations.py's upgrade path depends on this guard."
    )


def test_users_table_specifically_is_guarded():
    """003_users.sql is the migration that motivated this whole upgrade
    path - if its own CREATE TABLE were unguarded, re-applying it to a
    database that already has users would fail."""
    sql = (MIGRATIONS_DIR / "003_users.sql").read_text(encoding="utf-8")
    assert _unguarded_create_tables(sql) == []
    assert "CREATE TABLE IF NOT EXISTS users" in sql


# --- negative proof: the guard actually catches drift ------------------------


def test_guard_detects_an_unguarded_create_table():
    """Proves this check fails on drift rather than only ever passing
    because the current files happen to comply - the same negative-test
    discipline the schema-parity suite already uses."""
    bad_sql = "CREATE TABLE users (\n  user_id text PRIMARY KEY\n);\n"
    assert _unguarded_create_tables(bad_sql) == ["users"]

    good_sql = "CREATE TABLE IF NOT EXISTS users (\n  user_id text PRIMARY KEY\n);\n"
    assert _unguarded_create_tables(good_sql) == []


# --- the CREATE TYPE exception the runner must tolerate ----------------------


def test_create_type_statements_are_not_guarded_which_the_runner_must_tolerate():
    """PostgreSQL has no CREATE TYPE IF NOT EXISTS, so 001's three enum
    types raise duplicate_object (42710) on re-application. This test pins
    that reality so nobody later reads "idempotency guard" as a claim that
    the raw SQL is fully re-runnable - it is not, and
    scripts/apply_migrations.py compensates by treating 42710 as success.

    If a future migration ever makes these idempotent (e.g. via a DO block
    with an exception handler), this test should be updated deliberately,
    not deleted silently."""
    sql = (MIGRATIONS_DIR / "001_foundation.sql").read_text(encoding="utf-8")
    create_types = re.findall(r"CREATE\s+TYPE\s+(\w+)", sql, re.IGNORECASE)
    assert sorted(create_types) == ["data_state", "risk_class", "shift_status"]
    assert "CREATE TYPE IF NOT EXISTS" not in sql.upper()

    # duplicate_object is what such a re-run raises, and the runner tolerates it.
    assert "42710" in _ALREADY_EXISTS_SQLSTATES


# --- statement splitting the runner relies on --------------------------------


@pytest.mark.parametrize("path", _migration_paths(), ids=lambda p: p.name)
def test_statements_split_without_losing_any_create_statement(path):
    """The runner executes statement-by-statement (so one tolerated
    'already exists' does not abort the rest of the file). Verify the
    splitter does not drop or merge statements - semicolons inside CHECK
    constraints and quoted enum values must not split a statement early."""
    sql = path.read_text(encoding="utf-8")
    statements = split_statements(sql)

    expected_creates = len(re.findall(r"CREATE\s+(TABLE|TYPE|EXTENSION)", sql, re.IGNORECASE))
    actual_creates = sum(
        1
        for s in statements
        if re.match(r"CREATE\s+(TABLE|TYPE|EXTENSION)", s.strip(), re.IGNORECASE)
    )
    assert actual_creates == expected_creates, (
        f"{path.name}: splitter produced {actual_creates} CREATE statements, "
        f"expected {expected_creates} - statements were dropped or merged"
    )
    for statement in statements:
        assert statement.count("(") == statement.count(")"), (
            f"{path.name}: unbalanced parentheses in a split statement, which "
            f"means the splitter cut inside a CHECK constraint: {statement[:80]}"
        )


# --- duplicate-tolerance mechanism -------------------------------------------
#
# The tolerance path cannot be exercised end-to-end here: these migrations are
# PostgreSQL-only (DEFAULT now(), gen_random_uuid(), custom ENUMs, jsonb) and
# no PostgreSQL is available in this environment - confirmed by attempting the
# real apply against SQLite, which fails on `DEFAULT now()`. So the decision
# logic is tested directly instead of being left as untested code behind an
# unverifiable claim.


class _FakePsycopg3Error(Exception):
    """psycopg3 exposes the SQLSTATE as .sqlstate."""

    def __init__(self, sqlstate: str):
        super().__init__(f"fake error {sqlstate}")
        self.sqlstate = sqlstate


class _FakePsycopg2Error(Exception):
    """psycopg2 exposes it as .pgcode - both must be recognized."""

    def __init__(self, pgcode: str):
        super().__init__(f"fake error {pgcode}")
        self.pgcode = pgcode


class _FakeSqlAlchemyWrapper(Exception):
    """SQLAlchemy wraps the driver error and exposes it as .orig."""

    def __init__(self, orig: Exception):
        super().__init__("wrapped")
        self.orig = orig


def test_duplicate_object_sqlstate_is_recognized_through_sqlalchemy_wrapping():
    """42710 is what re-running 001's CREATE TYPE raises - the single most
    important case for this runner, since that statement cannot be guarded
    in SQL."""
    wrapped = _FakeSqlAlchemyWrapper(_FakePsycopg3Error("42710"))
    assert _sqlstate_of(wrapped) == "42710"
    assert _sqlstate_of(wrapped) in _ALREADY_EXISTS_SQLSTATES


def test_psycopg2_style_pgcode_is_also_recognized():
    wrapped = _FakeSqlAlchemyWrapper(_FakePsycopg2Error("42P07"))
    assert _sqlstate_of(wrapped) in _ALREADY_EXISTS_SQLSTATES


def test_unrelated_error_is_not_tolerated():
    """A real failure (e.g. syntax error 42601, or an undefined table) must
    still propagate - tolerating everything would turn a broken migration
    into a silent no-op, which is worse than the bug being fixed."""
    wrapped = _FakeSqlAlchemyWrapper(_FakePsycopg3Error("42601"))
    assert _sqlstate_of(wrapped) not in _ALREADY_EXISTS_SQLSTATES

    bare = _FakeSqlAlchemyWrapper(Exception("no sqlstate at all"))
    assert _sqlstate_of(bare) not in _ALREADY_EXISTS_SQLSTATES


# --- credentials must never be printed ---------------------------------------


def test_database_url_password_is_redacted():
    """The runner prints the target URL; DATABASE_URL normally embeds a
    password, which must not reach stdout or a log."""
    redacted = redact_url("postgresql+psycopg://workspace:hunter2@db.internal:5432/workspace")
    assert "hunter2" not in redacted
    assert "workspace:hunter2" not in redacted
    assert "db.internal" in redacted, "host/database should stay visible to be useful"


def test_redaction_leaves_credential_free_urls_readable():
    url = "postgresql+psycopg://localhost:5432/workspace"
    assert redact_url(url) == url
