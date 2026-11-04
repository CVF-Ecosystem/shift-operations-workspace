"""One locked, transaction-owned synthetic seed or sole timestamp correction."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime

from sqlalchemy import insert, update

from workspace_api.demo.seed_recovery_compare import compare_rows

EXPECTED_TABLE_NAMES_DIGEST = "d771d18008d63ecc5c775a96d91f6b7cda7187394298ec797fdeb6ecaaf1ca69"


def database_fingerprint(conn) -> str:
    """Read identity inside the same transaction that may write."""
    if conn.dialect.name != "postgresql":
        raise RuntimeError("owned PostgreSQL required")
    database, version = conn.exec_driver_sql("SELECT current_database(), version()").one()
    if database != "shiftops_p5a2_source_demo" or "PostgreSQL 16" not in version:
        raise RuntimeError("database identity changed")
    system_id = str(conn.exec_driver_sql(
        "SELECT system_identifier FROM pg_control_system()").scalar_one())
    raw = json.dumps({"database": database, "system_identifier": system_id},
                     sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def lock_tables(conn, names: frozenset[str]) -> None:
    """Lock the complete application table set before reading predicates."""
    if conn.dialect.name != "postgresql":
        raise RuntimeError("owned PostgreSQL required")
    for name in sorted(names):
        conn.exec_driver_sql(f'LOCK TABLE public."{name}" IN SHARE ROW EXCLUSIVE MODE')


def read_rows(conn, names: frozenset[str]) -> dict[str, list[dict]]:
    from operations_ledger.tables import users, shifts, shift_assignments, reports

    target_columns = {table.name: set(table.columns.keys())
                      for table in (users, shifts, shift_assignments, reports)}
    rows = {}
    schema = "public." if conn.dialect.name == "postgresql" else ""
    for name in sorted(names):
        result = conn.exec_driver_sql(f'SELECT * FROM {schema}"{name}"')
        if name in target_columns and set(result.keys()) != target_columns[name]:
            raise RuntimeError("raw schema columns changed")
        rows[name] = [dict(row) for row in result.mappings().all()]
    return rows


def installed_tables(conn) -> frozenset[str]:
    if conn.dialect.name == "postgresql":
        result = conn.exec_driver_sql(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    else:  # inert SQLite transaction tests only; public runtime is PG-gated
        result = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'")
    return frozenset(row[0] for row in result)


def schema_digest(conn, names: frozenset[str]) -> str:
    if conn.dialect.name == "postgresql":
        result = conn.exec_driver_sql(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public'")
        pairs = result.all()
    else:  # inert SQLite transaction tests only
        pairs = [(name, row[1]) for name in sorted(names)
                 for row in conn.exec_driver_sql(f'PRAGMA table_info("{name}")').all()]
    columns = {name: set() for name in names}
    for name, column in pairs:
        if name in columns:
            columns[name].add(column)
    raw = json.dumps({name: sorted(columns[name]) for name in sorted(names)},
                     sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def family_record(result: str, fingerprint: str,
                  old_created_at: str | None = None,
                  new_created_at: str | None = None) -> dict:
    """Emit a secret-free terminal result after an established commit."""
    outcomes = {"SEEDED": ("SEEDED_ATOMIC", 110),
                "VERIFY": ("EXACT_VERIFIED", 0),
                "CREATED_AT_REPAIRED": ("CREATED_AT_REPAIRED", 1)}
    outcome, writes = outcomes[result]
    record = {"outcome": outcome, "profile_id": "P5A2-SOURCE-DEMO-LOCAL-1",
              "db_fingerprint": fingerprint,
              "durable_application_writes": writes,
              "exact_rows_verified": True}
    if result == "CREATED_AT_REPAIRED":
        if old_created_at is None or new_created_at is None:
            raise RuntimeError("timestamp receipt incomplete")
        record.update({"changed_user_id": "PUBLIC_ACTOR",
                       "old_created_at_digest": hashlib.sha256(
                           old_created_at.encode()).hexdigest(),
                       "new_created_at_digest": hashlib.sha256(
                           new_created_at.encode()).hexdigest()})
    return record


def proven_refusal_record(fingerprint: str, reason: str) -> dict:
    """Only call after proved prewrite refusal or verified rollback."""
    if len(fingerprint) != 64 or not reason:
        raise RuntimeError("refusal receipt incomplete")
    return {"outcome": "REFUSED_ZERO_WRITE",
            "profile_id": "P5A2-SOURCE-DEMO-LOCAL-1",
            "db_fingerprint": fingerprint,
            "durable_application_writes": 0,
            "exact_rows_verified": False, "reason": reason}


def seed_transaction(ledger, bundle: dict, authority: dict,
                     viewer_password: str, expected_prewrite: dict) -> dict:
    """Compare the RO snapshot again under locks; verify before commit."""
    from operations_ledger.tables import users
    from workspace_api.demo.seed import _models

    if authority.get("data_bundle_sha256") is None:
        raise RuntimeError("synthetic authority unavailable")
    if not isinstance(expected_prewrite, dict) or set(expected_prewrite) != {
            "classification", "state_digest", "db_fingerprint",
            "observed_created_at", "table_names", "schema_digest"}:
        raise RuntimeError("prewrite snapshot invalid")
    if expected_prewrite["classification"] not in {
            "EMPTY_COMPATIBLE", "EXACT_SEEDED", "SOLE_CREATED_AT_MISMATCH"}:
        raise RuntimeError("prewrite classification invalid")
    table_names = expected_prewrite["table_names"]
    if (type(table_names) is not list or len(table_names) != 31
            or any(type(name) is not str or
                   re.fullmatch(r"[a-z][a-z0-9_]*", name) is None
                   for name in table_names)
            or len(set(table_names)) != 31
            or hashlib.sha256(json.dumps(sorted(table_names), sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
            != EXPECTED_TABLE_NAMES_DIGEST
            or not {"users", "shifts", "shift_assignments", "reports"}.issubset(table_names)):
        raise RuntimeError("table set invalid")
    names = frozenset(table_names)
    with ledger.engine.begin() as conn:
        lock_tables(conn, names)
        if installed_tables(conn) != names:
            raise RuntimeError("table set changed")
        if schema_digest(conn, names) != expected_prewrite["schema_digest"]:
            raise RuntimeError("schema columns changed")
        if database_fingerprint(conn) != expected_prewrite["db_fingerprint"]:
            raise RuntimeError("database identity changed")
        # Every count, raw column, native model, password and report body is
        # checked after all table locks, before branch selection or writes.
        before = compare_rows(read_rows(conn, names), bundle, viewer_password,
                              ledger.models.User)
        if any(before[key] != expected_prewrite[key] for key in (
                "classification", "state_digest", "observed_created_at")):
            raise RuntimeError("prewrite snapshot changed")
        branch = before["classification"]
        if branch == "EMPTY_COMPATIBLE":
            user, shifts, assignments, reports = _models(
                bundle, viewer_password, ledger.models.User)
            # Shared ledger.add_user omits created_at and would use DB now().
            # This explicit demo-only insert preserves the frozen timestamp.
            conn.execute(insert(users).values(**user.model_dump()))
            for shift in shifts:
                ledger.create_shift(shift, unit=conn)
            for assignment in assignments:
                ledger.add_assignment(assignment, unit=conn)
            for report in reports:
                ledger.add_report(report, unit=conn)
            result = "SEEDED"
        elif branch == "SOLE_CREATED_AT_MISMATCH":
            current = read_rows(conn, names)["users"][0]
            observed = datetime.fromisoformat(expected_prewrite["observed_created_at"])
            expected = datetime.fromisoformat(bundle["user"]["created_at"].replace("Z", "+00:00"))
            predicate = (users.c.user_id == "PUBLIC_ACTOR") & (
                users.c.username == current["username"]) & (
                users.c.role == current["role"]) & (
                users.c.is_active == current["is_active"]) & (
                users.c.password_hash == current["password_hash"]) & (
                users.c.created_at == observed)
            changed = conn.execute(update(users).where(predicate).values(
                created_at=expected)).rowcount
            if changed != 1:
                raise RuntimeError("synthetic timestamp CAS failed")
            result = "CREATED_AT_REPAIRED"
        else:
            result = "VERIFY"
        after = compare_rows(read_rows(conn, names), bundle, viewer_password,
                             ledger.models.User)
        if after["classification"] != "EXACT_SEEDED":
            raise RuntimeError("synthetic exact readback failed")
        if database_fingerprint(conn) != expected_prewrite["db_fingerprint"]:
            raise RuntimeError("database identity changed after write")
        if schema_digest(conn, names) != expected_prewrite["schema_digest"]:
            raise RuntimeError("schema columns changed after write")
        # Leaving the engine.begin context is the sole commit point. Any
        # exception above rolls back seed/CAS and emits no success receipt.
    return {"result": result, "state_digest": after["state_digest"],
            "db_fingerprint": expected_prewrite["db_fingerprint"],
            "family_record": family_record(result, expected_prewrite["db_fingerprint"],
                                           expected_prewrite["observed_created_at"],
                                           bundle["user"]["created_at"])}
