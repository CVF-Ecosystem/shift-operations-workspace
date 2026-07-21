"""Both ledger backends must satisfy the same Ledger Protocol.

This guards the substitutability promise: services depend on the Protocol, so
swapping InMemoryLedger for SqlLedger must not require any service change.

Note: SqlLedger's live behaviour against PostgreSQL is NOT exercised here (no
database in this environment). This test only proves structural conformance to
the Protocol; a live integration test belongs in a separate DB-backed suite.
"""

from operations_ledger import Ledger
from operations_ledger.sql_ledger import SqlLedger

from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger


def test_in_memory_ledger_is_a_ledger():
    assert isinstance(InMemoryLedger(), Ledger)


def test_sql_ledger_is_a_ledger():
    # Inject a throwaway engine so no PostgreSQL driver/connection is needed to
    # assert structural conformance. No DB round-trip occurs.
    from sqlalchemy import create_engine

    sql = SqlLedger(
        "postgresql+psycopg://unused",
        models=domain_models,
        engine=create_engine("sqlite://"),
    )
    assert isinstance(sql, Ledger)


def test_both_backends_expose_the_same_ledger_methods():
    required = {
        "create_shift", "get_shift", "list_shifts", "freeze_shift",
        "add_message", "add_event", "get_event", "put_event",
        "add_correction", "corrections_for",
    }
    for backend in (InMemoryLedger, SqlLedger):
        missing = {m for m in required if not hasattr(backend, m)}
        assert not missing, f"{backend.__name__} missing {missing}"
