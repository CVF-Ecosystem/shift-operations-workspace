"""Canonical single-workspace operational assignment boundary (P2-C C3a2)."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from cvf_runtime.identity import Principal
from operations_domain.models import Shift
from operations_ledger import Ledger


class OperationalResourceNotFound(KeyError):
    """Enumeration-safe missing-or-inaccessible operational resource."""


class AssignmentScope:
    """Resolve stored shift ownership and require current ACTIVE membership."""

    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def require_shift(
        self, shift_id: UUID, principal: Principal, *, unit=None
    ) -> Shift:
        try:
            shift = self.ledger.get_shift(shift_id, unit=unit)
            assignment = self.ledger.get_active_assignment(
                shift_id, principal.user_id, unit=unit
            )
        except KeyError as exc:
            raise OperationalResourceNotFound("Operational resource not found") from exc
        if assignment is None:
            raise OperationalResourceNotFound("Operational resource not found")
        return shift

    def require_record(
        self, record, principal: Principal, *, shift_attr: str = "shift_id", unit=None
    ):
        self.require_shift(getattr(record, shift_attr), principal, unit=unit)
        return record

    def assigned_shifts(self, principal: Principal) -> list[Shift]:
        return [
            shift
            for shift in self.ledger.list_shifts()
            if self.ledger.get_active_assignment(shift.shift_id, principal.user_id)
            is not None
        ]


def require_active_assignment(
    ledger: Ledger, shift_id: UUID, principal: Principal, *, unit=None
) -> Shift:
    return AssignmentScope(ledger).require_shift(shift_id, principal, unit=unit)


def assigned_shifts(
    ledger: Ledger, principal: Principal, shifts: Iterable[Shift] | None = None
) -> list[Shift]:
    source = shifts if shifts is not None else ledger.list_shifts()
    return [
        shift
        for shift in source
        if ledger.get_active_assignment(shift.shift_id, principal.user_id) is not None
    ]
