"""Operations Ledger: the source-of-truth persistence boundary.

Defines a single :class:`Ledger` Protocol implemented by two backends:

* ``InMemoryLedger`` (in workspace-api) — fast, for tests and offline/degraded
  mode.
* ``SqlLedger`` (here) — append-only PostgreSQL persistence for production.

Application services depend on the Protocol, never on a concrete backend, so
the CVF chain is identical regardless of where records live.
"""

from operations_ledger.ledger import Ledger

__all__ = ["Ledger"]
