"""Transaction-owned exact synthetic seed. This module is inert until invoked."""

from __future__ import annotations

import os
import re

from sqlalchemy import inspect

from workspace_api.demo.bundle import load_bundle
from workspace_api.demo.coverage import load_authority

PROFILE = "P5A2-SOURCE-DEMO-LOCAL-1"
DB_NAME = "shiftops_p5a2_source_demo"


def _owned_url(database_url: str):
    from sqlalchemy.engine import make_url

    try:
        url = make_url(database_url)
        if (not url.drivername.startswith("postgresql")
                or url.host not in {"127.0.0.1", "localhost"}
                or url.port != 5433 or url.database != DB_NAME):
            raise ValueError("database identity")
    except Exception as exc:
        raise RuntimeError("invalid owned demo database") from exc
    return url


def _owned_ledger(database_url: str):
    """Use the one existing SqlLedger/User injection seam, never a fallback."""
    from operations_ledger.sql_ledger import SqlLedger
    from workspace_api.config import settings
    from workspace_api.infrastructure.ledger_factory import build_ledger

    expected_url = _owned_url(database_url)
    if settings.database_url != database_url:
        raise RuntimeError("configured demo database differs")
    ledger = build_ledger()
    if (not isinstance(ledger, SqlLedger)
            or ledger.engine.url != expected_url
            or ledger.engine.dialect.name != "postgresql"):
        raise RuntimeError("owned PostgreSQL ledger required")
    return ledger


def _models(bundle: dict, password: str, user_type):
    from workspace_api.auth.passwords import hash_password
    from operations_domain.models import Shift, Report
    from operations_domain.assignment_models import ShiftAssignment

    if not 12 <= len(password.encode("utf-8")) <= 72:
        raise ValueError("demo viewer password length invalid")
    user = user_type(**bundle["user"], password_hash=hash_password(password))
    shifts = [Shift(**row) for row in bundle["shifts"]]
    assignments = [ShiftAssignment(**row) for row in bundle["assignments"]]
    reports = [Report(**row) for row in bundle["reports"]]
    if (len({s.shift_id for s in shifts}) != 36
            or len({a.assignment_id for a in assignments}) != 36
            or len({r.report_id for r in reports}) != 37):
        raise ValueError("duplicate synthetic record identity")
    return user, shifts, assignments, reports


def _schema_and_counts(conn, engine) -> dict[str, int]:
    from operations_ledger.tables import shifts, users
    from operations_ledger._assignment_store import shift_assignments
    from operations_ledger._report_store import reports

    required = (shifts, users, shift_assignments, reports)
    inspector = inspect(engine)
    if any(not inspector.has_table(table.name) for table in required):
        raise RuntimeError("synthetic database schema incomplete")
    expected_columns = {table.name: set(table.columns.keys()) for table in required}
    for name, columns in expected_columns.items():
        installed = {col["name"] for col in inspector.get_columns(name)}
        if not columns <= installed:
            raise RuntimeError("synthetic database schema mismatch")
    names = inspector.get_table_names()
    if any(re.fullmatch(r"[a-z][a-z0-9_]*", name) is None for name in names):
        raise RuntimeError("unexpected synthetic schema table")
    return {name: conn.exec_driver_sql(f'SELECT COUNT(*) FROM "{name}"').scalar_one()
            for name in names}


def _verify_existing(ledger, user, shifts, assignments, reports, password):
    from workspace_api.auth.passwords import verify_password

    stored = ledger.get_user_by_id(user.user_id)
    if (stored is None or not verify_password(password, stored.password_hash)
            or stored.model_copy(update={"password_hash": user.password_hash}).model_dump()
            != user.model_dump()):
        raise RuntimeError("existing synthetic user differs")
    if any(ledger.get_shift(item.shift_id) != item for item in shifts):
        raise RuntimeError("existing synthetic shifts differ")
    if any(ledger.get_assignment(item.assignment_id) != item for item in assignments):
        raise RuntimeError("existing synthetic assignments differ")
    if any(ledger.get_report(item.report_id) != item for item in reports):
        raise RuntimeError("existing synthetic reports differ")


def verify_owned_database(ledger, bundle: dict) -> None:
    """Fail startup before listener if owned rows/schema differ from the pin."""
    _owned_url(ledger.engine.url)
    from operations_domain.models import Shift, Report
    from operations_domain.assignment_models import ShiftAssignment

    with ledger.engine.begin() as conn:
        if conn.exec_driver_sql("SELECT current_database()").scalar_one() != DB_NAME:
            raise RuntimeError("owned database identity mismatch")
        counts = _schema_and_counts(conn, ledger.engine)
    required = {"users": 1, "shifts": 36, "shift_assignments": 36, "reports": 37}
    if any(counts.get(name) != count for name, count in required.items()):
        raise RuntimeError("synthetic database row count mismatch")
    if any(count for name, count in counts.items() if name not in required):
        raise RuntimeError("foreign synthetic database row")
    expected_user = bundle["user"]
    stored_user = ledger.get_user_by_id(expected_user["user_id"])
    if stored_user is None:
        raise RuntimeError("synthetic user mismatch")
    expected_user_model = ledger.models.User(**expected_user,
                                            password_hash=stored_user.password_hash)
    if stored_user != expected_user_model:
        raise RuntimeError("synthetic user mismatch")
    for row in bundle["shifts"]:
        expected = Shift(**row)
        if ledger.get_shift(expected.shift_id) != expected:
            raise RuntimeError("synthetic shift mismatch")
    for row in bundle["assignments"]:
        expected = ShiftAssignment(**row)
        if ledger.get_assignment(expected.assignment_id) != expected:
            raise RuntimeError("synthetic assignment mismatch")
    for row in bundle["reports"]:
        expected = Report(**row)
        if ledger.get_report(expected.report_id) != expected:
            raise RuntimeError("synthetic report mismatch")


def seed_owned_database(database_url: str, viewer_password: str) -> str:
    """Write exactly once, accept exact repeat, refuse any partial prior state."""
    if os.environ.get("P5A2_SOURCE_DEMO_PROFILE") != PROFILE:
        raise RuntimeError("synthetic profile marker required")
    _owned_url(database_url)
    bundle, authority = load_bundle(), load_authority()
    if authority["data_bundle_sha256"] is None:
        raise RuntimeError("synthetic authority unavailable")
    ledger = _owned_ledger(database_url)
    user, shifts, assignments, reports = _models(bundle, viewer_password,
                                                  ledger.models.User)
    with ledger.engine.begin() as conn:
        db_name = conn.exec_driver_sql("SELECT current_database()").scalar_one()
        if db_name != DB_NAME:
            raise RuntimeError("owned database identity mismatch")
        counts = _schema_and_counts(conn, ledger.engine)
        desired = {name: {"users": 1, "shifts": 36,
                          "shift_assignments": 36, "reports": 37}.get(name, 0)
                   for name in counts}
        if counts == desired:
            # Close this read transaction before method-level reads.
            state = "VERIFY"
        elif all(count == 0 for count in counts.values()):
            ledger.add_user(user, unit=conn)
            for shift in shifts:
                ledger.create_shift(shift, unit=conn)
            for assignment in assignments:
                ledger.add_assignment(assignment, unit=conn)
            for report in reports:
                ledger.add_report(report, unit=conn)
            state = "SEEDED"
        else:
            raise RuntimeError("partial or foreign synthetic data")
    _verify_existing(ledger, user, shifts, assignments, reports, viewer_password)
    return state


def main() -> None:
    if os.environ.get("P5A2_SOURCE_DEMO_PROFILE") != PROFILE:
        raise RuntimeError("synthetic profile marker required")
    from workspace_api.config import settings

    password = os.environ.get("P5A2_SOURCE_DEMO_VIEWER_PASSWORD", "")
    result = seed_owned_database(settings.database_url, password)
    print(result)


if __name__ == "__main__":
    main()
