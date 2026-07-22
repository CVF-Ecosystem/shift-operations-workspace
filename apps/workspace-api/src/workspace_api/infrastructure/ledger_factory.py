"""Selects the Ledger backend based on configuration.

No DATABASE_URL -> InMemoryLedger (tests, offline/degraded mode).
DATABASE_URL set -> SqlLedger (durable, append-only PostgreSQL).

The application always depends on the Ledger Protocol, so the CVF chain is
identical regardless of which backend this returns.
"""

from __future__ import annotations

from functools import lru_cache

from workspace_api.config import settings

# Documented exception E1 (SPEC R5.2): this imports the shim MODULE as a
# namespace object, not a moved domain model. SqlLedger receives it as
# `models=` and operations_ledger._rows.build_user calls `models.User`, so the
# injected namespace must expose both the operational types (re-exported from
# operations_domain) and `User` (which did not move). Only
# workspace_api.domain.models satisfies both. The injection seam itself is
# deliberately NOT refactored by tranche P1B - see ADR section 2.5.
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
