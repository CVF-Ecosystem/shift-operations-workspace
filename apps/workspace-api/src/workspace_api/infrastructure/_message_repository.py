"""In-memory message storage mixin (P2C-MUTATION-FULL-UI-C3B1).

Split out of ``repository.py`` (SPEC R11/R36) to keep that host module a
thin wiring surface under the hard 300-line guard, matching
``_incident_repository.py``/``_report_repository.py``'s pattern.
``_MessageRepositoryMixin`` expects ``self._lock``, ``self.messages`` and
``self._assert_shift_not_frozen`` to already exist (set up by
``InMemoryLedger.__init__``); it owns no state of its own.

``add_message``/``get_message``/``message_exists`` moved here intact from
``repository.py`` (unchanged behavior) so the new ``list_messages_for_shift``
(SPEC R11/R36: ``(created_at, message_id)`` ascending) has room under the
file-size guard without altering any existing method's semantics.
"""

from __future__ import annotations

from uuid import UUID

from operations_domain.models import Message


class _MessageRepositoryMixin:
    def add_message(self, message: Message, *, unit=None) -> Message:
        # SPEC R9: shift/freeze check, duplicate/evidence refusal, then
        # deep-copy in and out so caller mutation never touches stored truth.
        self._assert_shift_not_frozen(message.shift_id, "add message to a frozen shift")
        if message.message_id in self.messages:
            raise ValueError(f"duplicate message_id: {message.message_id}")
        if message.evidence:
            raise ValueError("message evidence is not supported by the persisted schema")
        stored = message.model_copy(deep=True)
        self.messages[message.message_id] = stored
        return stored.model_copy(deep=True)

    def get_message(self, message_id: UUID, *, unit=None) -> Message:
        # Deep copy, not the live reference — see get_shift() for why.
        return self.messages[message_id].model_copy(deep=True)

    def message_exists(self, message_id: UUID, *, unit=None) -> bool:
        return message_id in self.messages

    def list_messages_for_shift(self, shift_id: UUID, *, unit=None) -> list[Message]:
        """SPEC R11/R36: every Message bound to ``shift_id``, ascending
        ``(created_at, message_id)`` — deterministic and cross-backend
        equivalent, including terminal states (Message has no lifecycle to
        exclude)."""
        with self._lock:
            return sorted(
                (m.model_copy(deep=True) for m in self.messages.values() if m.shift_id == shift_id),
                key=lambda m: (m.created_at, str(m.message_id)),
            )
