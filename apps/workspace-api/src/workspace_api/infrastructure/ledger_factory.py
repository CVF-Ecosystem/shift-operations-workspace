"""Selects the Ledger backend based on configuration.

No DATABASE_URL -> InMemoryLedger (tests, offline/degraded mode).
DATABASE_URL set -> SqlLedger (durable, append-only PostgreSQL).

The application always depends on the Ledger Protocol, so the CVF chain is
identical regardless of which backend this returns.
"""

from __future__ import annotations

from functools import lru_cache

from workspace_api.config import settings
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import ledger as in_memory_ledger


@lru_cache(maxsize=1)
def build_ledger():
    if not settings.database_url:
        return in_memory_ledger
    # Imported lazily so environments without SQLAlchemy/psycopg (or without a
    # database) never pay for the SQL backend.
    from operations_ledger.sql_ledger import SqlLedger

    return SqlLedger(settings.database_url, models=domain_models)
