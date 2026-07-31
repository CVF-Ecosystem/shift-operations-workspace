"""In-memory shift-assignment storage mixin (P2C-MUTATION-FULL-UI-C3A1).

Split out of ``repository.py`` (same pattern as ``_incident_repository.py``)
to keep that host module a thin wiring surface. ``_AssignmentRepositoryMixin``
expects ``self._lock``, ``self.assignments``, ``self.shifts`` and
``self.users`` to already exist (set up by ``InMemoryLedger.__init__``); it
owns no state of its own.

P2C-C3A1-BUILD-REV-F1 repair: this mixin previously accepted a missing
shift/target-user/assigned_by/revoked_by reference unconditionally - the
in-memory backend has no real foreign key, so nothing rejected it, unlike
SqlLedger which (before this same repair) would have hit a real FK
IntegrityError. Both backends now pre-validate every reference explicitly
(mirrors ``_report_store.py``'s ``_assert_new_report_valid`` pattern: SELECT/
lookup checks before the write, not a catch-all exception remap) and raise
the SAME controlled ``ValueError`` shape for a missing reference, kept
distinct from the genuine duplicate-active-assignment ``ValueError``.

P2C-C3A1-BUILD-REV-F1 amendment: reference prevalidation does NOT make
duplicate-active the only way an insert can fail - a caller can still
present an ``assignment_id`` that collides with an existing row (e.g. a
previously revoked assignment's id reused, whether by a buggy caller or a
replay). This dict is keyed by ``assignment_id``, so ``add_assignment``
previously overwrote that row in place unconditionally, silently destroying
history that SqlLedger's real primary key would have refused. A duplicate
``assignment_id`` is now checked and rejected BEFORE the duplicate-active
check, with a distinct message, and the dict is never written to for a
rejected assignment.

P2C-C3A1-BUILD-REV-F4 repair: pydantic does not re-validate a model's own
fields on plain attribute assignment, so a caller could hand this dict a
``ShiftAssignment`` whose ``status``/``version`` were mutated after
construction into an invalid shape (e.g. ``status = "NOT_A_REAL_STATUS"``)
- this backend has no real CHECK constraint, so nothing rejected it and the
invalid row was accepted and stored verbatim. ``add_assignment`` now calls
the SAME ``assert_assignment_lifecycle_valid`` SqlLedger's INSERT path
calls, before any reference check or dict write, so both backends reject an
invalid lifecycle shape identically.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from operations_domain.assignment_models import assert_assignment_lifecycle_valid


class _AssignmentRepositoryMixin:
    def list_active_users(self) -> list:
        with self._lock:
            return [
                {"user_id": u.user_id, "username": u.username, "role": u.role}
                for u in sorted(self.users.values(), key=lambda u: u.user_id)
                if u.is_active
            ]

    def _assert_assignment_references_exist(self, shift_id, user_id, assigned_by) -> None:
        if shift_id not in self.shifts:
            raise ValueError(f"unknown shift: {shift_id}")
        if user_id not in self.users:
            raise ValueError(f"unknown target user: {user_id!r}")
        if assigned_by not in self.users:
            raise ValueError(f"unknown assigned_by actor: {assigned_by!r}")

    def add_assignment(self, assignment, *, unit=None):
        with self._lock:
            assert_assignment_lifecycle_valid(assignment)
            self._assert_assignment_references_exist(
                assignment.shift_id, assignment.user_id, assignment.assigned_by
            )
            if assignment.assignment_id in self.assignments:
                raise ValueError(f"duplicate assignment_id: {assignment.assignment_id}")
            duplicate = any(
                a.shift_id == assignment.shift_id
                and a.user_id == assignment.user_id
                and a.status.value == "ACTIVE"
                for a in self.assignments.values()
            )
            if duplicate:
                raise ValueError(
                    f"duplicate active assignment for shift {assignment.shift_id} "
                    f"user {assignment.user_id}"
                )
            stored = assignment.model_copy()
            self.assignments[assignment.assignment_id] = stored
            return stored.model_copy()

    def get_assignment(self, assignment_id: UUID, *, unit=None):
        with self._lock:
            if assignment_id not in self.assignments:
                raise KeyError(assignment_id)
            return self.assignments[assignment_id].model_copy()

    def list_assignments_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        with self._lock:
            return sorted(
                (a.model_copy() for a in self.assignments.values() if a.shift_id == shift_id),
                key=lambda a: (a.assigned_at, a.assignment_id),
            )

    def get_active_assignment(self, shift_id: UUID, user_id: str, *, unit=None):
        with self._lock:
            for a in self.assignments.values():
                if a.shift_id == shift_id and a.user_id == user_id and a.status.value == "ACTIVE":
                    return a.model_copy()
            return None

    def revoke_assignment(self, assignment_id: UUID, *, revoked_by: str, expected_version: int, unit=None):
        with self._lock:
            if assignment_id not in self.assignments:
                raise KeyError(assignment_id)
            if revoked_by not in self.users:
                raise ValueError(f"unknown revoked_by actor: {revoked_by!r}")
            current = self.assignments[assignment_id]
            if current.status.value == "REVOKED" and current.version == expected_version:
                return current.model_copy()
            if current.version != expected_version:
                raise ValueError(
                    f"stale assignment version: expected {expected_version}, found {current.version}"
                )
            updated = current.model_copy()
            updated.status = type(current.status)("REVOKED")
            updated.revoked_by = revoked_by
            updated.revoked_at = datetime.now(timezone.utc)
            updated.version = current.version + 1
            self.assignments[assignment_id] = updated
            return updated.model_copy()
