"""Canonical shift-assignment domain types (P2C-MUTATION-FULL-UI-C3A1).

Owns `ShiftAssignment`/`AssignmentStatus` only - the package-owned model SPEC
R1 requires, mirroring database/migrations/008_shift_assignments.sql exactly.
No tenant field or provider `data_scope` field is added (ADR section 3/4.1):
this is per-shift resource scope inside one workspace, not tenant isolation.

Split into its own module (not appended to `models.py`) purely for the
100-line-under-limit split-module wiring pattern this tranche's ADR/WO
requires for every new-package-owned surface, matching `report_models.py`'s
precedent of a second domain module living alongside `models.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError


class AssignmentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class ShiftAssignment(BaseModel):
    """One shift-to-user staffing grant. Retained as history when revoked -
    a revoke never deletes or overwrites this row's identity, only its
    status/revoked_by/revoked_at/version (ADR section 4.1)."""

    assignment_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    user_id: str
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    assigned_by: str
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revoked_by: str | None = None
    revoked_at: datetime | None = None
    version: int = Field(default=1, ge=1)


def assert_assignment_lifecycle_valid(assignment: ShiftAssignment) -> None:
    """P2C-C3A1-BUILD-REV-F4: pydantic does NOT re-validate a model's own
    fields on plain attribute assignment (``assignment.status = "X"``)
    unless ``model_config = ConfigDict(validate_assignment=True)`` is set -
    it isn't here, matching every other domain model in this codebase. A
    caller can therefore hand either backend a ``ShiftAssignment`` whose
    ``status``/``version`` were mutated after construction into a shape the
    constructor itself would have refused. Both ``add_assignment``
    implementations call this SAME check before any write, so an invalid
    lifecycle shape is rejected identically on both backends, before a row
    ever reaches InMemory's dict or the SQL INSERT - never a raw, backend-
    specific `IntegrityError` for a failure that was fully knowable in
    advance without touching the database."""
    if not isinstance(assignment, ShiftAssignment):
        raise ValueError("invalid assignment record type")
    if not isinstance(assignment.status, AssignmentStatus) or assignment.status not in (
        AssignmentStatus.ACTIVE, AssignmentStatus.REVOKED,
    ):
        raise ValueError(f"invalid assignment status: {assignment.status!r}")
    if not isinstance(assignment.version, int) or isinstance(assignment.version, bool) or assignment.version < 1:
        raise ValueError(f"invalid assignment version: {assignment.version!r}")
    # ``add_assignment`` is the creation boundary, not a history-import
    # primitive. Every new row starts ACTIVE at version 1 with no revoke
    # metadata; only ``revoke_assignment`` may create the REVOKED/version-2
    # shape and derive its actor/timestamp. Checking these fields together
    # prevents individually well-typed values from forming an impossible
    # lifecycle state.
    if assignment.status is not AssignmentStatus.ACTIVE:
        raise ValueError("invalid initial assignment status: must be ACTIVE")
    if assignment.version != 1:
        raise ValueError("invalid initial assignment version: must be 1")
    if assignment.revoked_by is not None:
        raise ValueError("invalid initial assignment: revoked_by must be absent")
    if assignment.revoked_at is not None:
        raise ValueError("invalid initial assignment: revoked_at must be absent")
    # Revalidate the complete mutable model strictly at the persistence
    # boundary. Pydantic validated construction does not protect fields that
    # callers later overwrite (for example assignment_id/assigned_at=None).
    # Both backends must reject that malformed record before either a dict
    # mutation or a SQL NOT NULL/type constraint can diverge their behavior.
    try:
        ShiftAssignment.model_validate(dict(assignment.__dict__), strict=True)
    except ValidationError as exc:
        fields = ", ".join(".".join(map(str, error["loc"])) for error in exc.errors())
        raise ValueError(f"invalid assignment record fields: {fields}") from exc
