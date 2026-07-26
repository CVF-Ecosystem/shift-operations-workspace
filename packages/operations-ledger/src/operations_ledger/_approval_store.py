"""SQL user / approval-receipt / task-creation-intent storage mixin.

Split out of ``sql_ledger.py`` (CVF-FILE-SPLIT-GUARD-HARDENING) to keep the
module under the hard line limit. ``_ApprovalStoreMixin`` expects
``self._conn``, ``self._fetch_one``, ``self.models`` and the ``_rows``
row-mapping helpers to already exist (provided by ``SqlLedger``); it owns no
state of its own and is not a second, independent implementation of
persistence - ``SqlLedger`` inherits it directly so every public method keeps
its exact prior name, signature and behavior. User lookups are grouped here
because they are exactly the authority-resolution surface approval receipts
depend on (``authority_for_factory`` / quorum evaluation resolve a fresh
``users`` row, never a stored role). ``_noop_cm`` lives here (not in
``sql_ledger.py``) so both modules can import it from this one direction
without a circular import.
"""

from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import insert, select
from sqlalchemy.engine import Connection

from operations_ledger import _rows
from operations_ledger.tables import approval_receipts, task_creation_intents, users


@contextmanager
def _noop_cm(conn: Connection):
    """Wrap an already-open connection for use in a ``with`` block without
    closing/committing it (the owning ``transaction()`` block does that)."""
    yield conn


class _ApprovalStoreMixin:
    def add_user(self, user, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(insert(users).values(**_rows.user_row(user)))
        return user

    def get_user_by_username(self, username: str, *, unit=None):
        row = self._fetch_one(select(users).where(users.c.username == username), unit=unit)
        return _rows.row_to_user(self.models, row) if row is not None else None

    def get_user_by_id(self, user_id: str, *, unit=None):
        row = self._fetch_one(select(users).where(users.c.user_id == user_id), unit=unit)
        return _rows.row_to_user(self.models, row) if row is not None else None

    def add_approval_receipt(self, receipt, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(insert(approval_receipts).values(**_rows.approval_receipt_row(receipt)))
        return receipt

    def list_approval_receipts_for(
        self,
        *,
        record_type,
        record_id,
        action,
        target_version,
        risk_class,
        payload_digest,
        unit=None,
    ):
        clauses = [
            approval_receipts.c.record_type == record_type,
            approval_receipts.c.record_id == record_id,
            approval_receipts.c.action == action,
            approval_receipts.c.target_version == target_version,
            approval_receipts.c.risk_class == risk_class,
            approval_receipts.c.payload_digest == payload_digest,
        ]
        rows = self._fetch_all(
            select(approval_receipts).where(*clauses),
            unit=unit,
        )
        return [_rows.row_to_approval_receipt(self.models, r) for r in rows]

    def get_approval_receipt(
        self, *, record_type, record_id, action, target_version, approver_id, unit=None
    ):
        row = self._fetch_one(
            select(approval_receipts).where(
                approval_receipts.c.record_type == record_type,
                approval_receipts.c.record_id == record_id,
                approval_receipts.c.action == action,
                approval_receipts.c.target_version == target_version,
                approval_receipts.c.approver_id == approver_id,
            ),
            unit=unit,
        )
        return _rows.row_to_approval_receipt(self.models, row) if row is not None else None

    def add_task_creation_intent(self, intent, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(
                insert(task_creation_intents).values(**_rows.task_creation_intent_row(intent))
            )
        return intent

    def get_task_creation_intent(self, intent_id, *, unit=None):
        row = self._fetch_one(
            select(task_creation_intents).where(task_creation_intents.c.intent_id == intent_id),
            unit=unit,
        )
        if row is None:
            raise KeyError(intent_id)
        return _rows.row_to_task_creation_intent(self.models, row)
