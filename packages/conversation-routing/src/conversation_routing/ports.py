"""Provider-neutral ports consumed/owned by conversation-routing (SPEC R18).

``conversation-routing`` consumes an identity-mapping read port and never
mutates mappings. It also defines its own binding-repository and target-
eligibility ports; Workspace API composes concrete implementations for both.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import RouteBindingV1


@runtime_checkable
class RouteBindingRepositoryPort(Protocol):
    def get_current_binding(
        self, mapping_id: str, *, unit: object = None
    ) -> RouteBindingV1 | None:
        """Returns the single current binding for a mapping id, or ``None``.
        Raises ``ValueError`` if more than one current binding exists
        (corruption - never priority-sorted into success, SPEC R13)."""
        ...

    def create_binding(self, binding: RouteBindingV1, *, unit: object = None) -> RouteBindingV1: ...

    def replace_binding(
        self, old_binding_id: str, successor: RouteBindingV1, *,
        expected_binding_version: int, unit: object = None
    ) -> RouteBindingV1:
        """CAS-revokes the expected old binding version and creates its
        successor atomically (SPEC R8/R9/R13)."""
        ...


class TargetEligibilityPort(Protocol):
    """SPEC R14: target and assignment eligibility revalidation. Workspace
    API implements this against live shift/incident/assignment/user state;
    conversation-routing never queries those tables directly."""

    def workspace_digest(self) -> str: ...

    def shift_eligible(self, shift_id: str) -> tuple[bool, int]:
        """Returns (eligible, target_version). Eligible iff the shift
        exists and is neither closed nor frozen."""
        ...

    def incident_eligible(self, incident_id: str) -> tuple[bool, int, str | None]:
        """Returns (eligible, target_version, parent_shift_id). Eligible
        iff the incident exists, is non-closed, and its parent shift is
        itself eligible."""
        ...

    def user_assignment_eligible(self, user_id: str, shift_id: str) -> bool:
        """True iff ``user_id`` is active and has a current active
        assignment to ``shift_id`` (SPEC R14: required of both the mapped
        user and the binding actor, at bind time and at route time)."""
        ...


class PlacementWorkPort(Protocol):
    """SPEC R11/R12: the durable work-item claim/retry surface. Owned by
    Operations Ledger; consumed here only through this port."""

    def claim(self, work_item_id: str, *, unit: object = None): ...

    def complete(self, work_item_id: str, decision, *, unit: object = None) -> None: ...

    def mark_pending(self, work_item_id: str, *, unit: object = None) -> None: ...


__all__ = [
    "PlacementWorkPort",
    "RouteBindingRepositoryPort",
    "TargetEligibilityPort",
]
