"""SQL message storage mixin (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30).

Split out of ``sql_ledger.py`` (same file-size-guard pattern as
``_incident_store.py``/``_handover_store.py``) to keep that host module a
thin wiring surface under the hard 300-line guard. ``_MessageStoreMixin``
expects ``self._open`` and ``self._assert_shift_not_frozen`` to already exist
(provided by ``SqlLedger``); it owns no state of its own.

Row<->model mapping lives in ``_rows.py`` (SPEC/WO authorize that shared
module for this tranche, unlike ``_incident_store.py`` which predates it
being an authorized changed set and so maps rows locally).

Duplicate ``message_id`` raises the SAME controlled ``ValueError`` shape
``add_task``/``add_incident`` already use on a primary-key collision — never a
raw, backend-specific ``IntegrityError`` reaching the application layer.
Non-empty evidence is refused, not silently dropped, because the ``messages``
table has no evidence column (SPEC R10).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from operations_ledger import _rows
from operations_ledger.tables import messages


class _MessageStoreMixin:
    def add_message(self, message, *, unit=None):
        with self._open(unit) as c:
            self._assert_shift_not_frozen(c, message.shift_id, "add message to a frozen shift")
            if message.evidence:
                raise ValueError("message evidence is not supported by the persisted schema")
            try:
                c.execute(insert(messages).values(**_rows.message_row(message)))
            except IntegrityError as exc:
                raise ValueError(f"duplicate message_id: {message.message_id}") from exc
        return message

    def get_message(self, message_id: UUID, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(messages).where(messages.c.message_id == message_id)
            ).mappings().first()
            if row is None:
                raise KeyError(message_id)
        return _rows.row_to_message(self.models, row)

    def list_messages_for_shift(self, shift_id: UUID, *, unit=None):
        """P2C-MUTATION-FULL-UI-C3B1 (SPEC R11/R36): every Message bound to
        ``shift_id``, ascending ``(created_at, message_id)`` — cross-backend
        equivalent to ``_MessageRepositoryMixin.list_messages_for_shift``."""
        with self._open(unit) as c:
            rows = c.execute(
                select(messages).where(messages.c.shift_id == shift_id)
                .order_by(messages.c.created_at, messages.c.message_id)
            ).mappings().all()
            return [_rows.row_to_message(self.models, r) for r in rows]
