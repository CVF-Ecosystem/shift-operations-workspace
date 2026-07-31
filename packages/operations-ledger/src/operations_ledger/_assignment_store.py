"""SQL shift-assignment storage mixin (P2C-MUTATION-FULL-UI-C3A1).

Split out of ``sql_ledger.py`` (same pattern as ``_incident_store.py``) to
keep that host module under the hard 300-line file-size guard.
``_AssignmentStoreMixin`` expects ``self._open``/``self._fetch_one``/
``self._fetch_all``/``self.models`` to already exist (provided by
``SqlLedger``); it owns no state of its own.

R3/R5: duplicate-active is enforced by the migration's partial unique index
(``shift_assignments_active_unique``). Revoke is exact-version-checked via an
atomic compare-and-swap ``UPDATE ... WHERE id=? AND version=?`` whose rowcount
decides the outcome - never a separate SELECT-then-UPDATE that could let two
concurrent callers both pass a read-only check.

P2C-C3A1-BUILD-REV-F1 repair: ``add_assignment`` previously wrapped the
INSERT in a blanket ``except IntegrityError`` and mislabeled EVERY failure -
missing shift, missing target user, missing assigned_by actor, or a genuine
duplicate-active-assignment - as "duplicate active assignment...". Every
reference is now pre-validated explicitly (SELECT/lookup checks before the
write), mirroring ``_report_store.py``'s ``_assert_new_report_valid``
pattern. ``revoke_assignment`` pre-validates ``revoked_by`` the same way.

P2C-C3A1-BUILD-REV-F1 amendment: reference prevalidation does NOT make
duplicate-active the only constraint the INSERT can still trip - a caller
can present an ``assignment_id`` that collides with an existing row's
PRIMARY KEY (``shift_assignments_pkey``), a wholly separate constraint from
the partial unique index (``shift_assignments_active_unique``) that backs
duplicate-active. The previous blanket ``except IntegrityError`` mapped a PK
collision to the SAME "duplicate active assignment..." message, which is
both wrong and would mislead a caller into thinking the ACTIVE-assignment
invariant (not the id itself) was the problem. ``_classify_assignment_insert_conflict``
below identifies which of the two known constraints actually fired -
via ``diag.constraint_name`` on PostgreSQL (psycopg exposes the server's own
reported constraint identity) and via the exact UNIQUE-violation column list
in the driver's message on SQLite (its ``IntegrityError`` carries no
structured constraint name, only a "UNIQUE constraint failed: <cols>"
string) - and raises the correspondingly distinct, controlled ``ValueError``.
Any OTHER IntegrityError (a check constraint, an FK violation that somehow
reached this point, or anything unrecognized) is re-raised unchanged rather
than being folded into either duplicate message, so a genuinely unexpected
database failure is never mislabeled as either kind of duplicate.

P2C-C3A1-BUILD-REV-F4 repair: an invalid lifecycle shape (e.g. ``status``
mutated after construction to a value outside ``AssignmentStatus``, or
``version < 1``) previously reached the INSERT unvalidated and let the
migration's own CHECK constraints raise a raw ``sqlalchemy.exc.
IntegrityError`` straight through to the caller - never classified,
never controlled, and the InMemory backend had no equivalent constraint at
all so it silently stored the corrupted row (see
``_assignment_repository.py``). ``add_assignment`` now calls the SAME
``assert_assignment_lifecycle_valid`` both backends share, before the
reference prevalidation and before the INSERT is even attempted, so this
class of failure is fully knowable in advance and never needs to touch the
database. The migration's CHECK constraints remain in place as defense in
depth for any caller that bypasses this method entirely (e.g. a raw
``conn.execute``), and ``_classify_assignment_insert_conflict`` is
unaffected - it still only ever sees a genuine PK/partial-unique-index
IntegrityError, since a lifecycle-invalid row can no longer reach the
INSERT at all.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from operations_domain.assignment_models import assert_assignment_lifecycle_valid

from operations_ledger.tables import shift_assignments, shifts, users

_PK_CONSTRAINT = "shift_assignments_pkey"
_ACTIVE_UNIQUE_CONSTRAINT = "shift_assignments_active_unique"


def _classify_assignment_insert_conflict(exc: IntegrityError, assignment) -> ValueError | None:
    """Return the controlled ValueError this IntegrityError maps to, or None
    if it does not match either known assignment-insert constraint (caller
    must then re-raise the original exception unchanged)."""
    orig = exc.orig
    constraint_name = getattr(getattr(orig, "diag", None), "constraint_name", None)
    if constraint_name is not None:
        # PostgreSQL: the server itself reports which constraint fired.
        if constraint_name == _PK_CONSTRAINT:
            return ValueError(f"duplicate assignment_id: {assignment.assignment_id}")
        if constraint_name == _ACTIVE_UNIQUE_CONSTRAINT:
            return ValueError(
                f"duplicate active assignment for shift {assignment.shift_id} "
                f"user {assignment.user_id}"
            )
        return None
    # SQLite: sqlite3.IntegrityError carries no structured constraint name,
    # only a message of the exact form "UNIQUE constraint failed: <cols>".
    message = str(orig)
    if "UNIQUE constraint failed: shift_assignments.assignment_id" in message:
        return ValueError(f"duplicate assignment_id: {assignment.assignment_id}")
    if "UNIQUE constraint failed: shift_assignments.shift_id, shift_assignments.user_id" in message:
        return ValueError(
            f"duplicate active assignment for shift {assignment.shift_id} "
            f"user {assignment.user_id}"
        )
    return None


def _row_to_assignment(models, row):
    return models.ShiftAssignment(
        assignment_id=row["assignment_id"],
        shift_id=row["shift_id"],
        user_id=row["user_id"],
        status=row["status"],
        assigned_by=row["assigned_by"],
        assigned_at=row["assigned_at"],
        revoked_by=row["revoked_by"],
        revoked_at=row["revoked_at"],
        version=row["version"],
    )


class _AssignmentStoreMixin:
    def list_active_users(self) -> list:
        rows = self._fetch_all(
            select(users.c.user_id, users.c.username, users.c.role)
            .where(users.c.is_active.is_(True))
            .order_by(users.c.user_id)
        )
        return [dict(r) for r in rows]

    def _assert_assignment_references_exist(self, c, shift_id, user_id, assigned_by) -> None:
        if c.execute(select(shifts.c.shift_id).where(shifts.c.shift_id == shift_id)).first() is None:
            raise ValueError(f"unknown shift: {shift_id}")
        if c.execute(select(users.c.user_id).where(users.c.user_id == user_id)).first() is None:
            raise ValueError(f"unknown target user: {user_id!r}")
        if c.execute(select(users.c.user_id).where(users.c.user_id == assigned_by)).first() is None:
            raise ValueError(f"unknown assigned_by actor: {assigned_by!r}")

    def add_assignment(self, assignment, *, unit=None):
        assert_assignment_lifecycle_valid(assignment)
        with self._open(unit) as c:
            self._assert_assignment_references_exist(c, assignment.shift_id, assignment.user_id, assignment.assigned_by)
            # References are pre-validated above (F1), but the INSERT can
            # still trip either of two DISTINCT constraints: a primary-key
            # collision on assignment_id, or the partial unique index
            # enforcing at most one ACTIVE assignment per (shift_id,
            # user_id) - the database itself remains the concurrency
            # authority for both. _classify_assignment_insert_conflict tells
            # them apart; anything it doesn't recognize is re-raised as-is.
            try:
                c.execute(
                    insert(shift_assignments).values(
                        assignment_id=assignment.assignment_id,
                        shift_id=assignment.shift_id,
                        user_id=assignment.user_id,
                        status=str(assignment.status),
                        assigned_by=assignment.assigned_by,
                        assigned_at=assignment.assigned_at,
                        revoked_by=assignment.revoked_by,
                        revoked_at=assignment.revoked_at,
                        version=assignment.version,
                    )
                )
            except IntegrityError as exc:
                controlled = _classify_assignment_insert_conflict(exc, assignment)
                if controlled is None:
                    raise
                raise controlled from exc
        return assignment

    def get_assignment(self, assignment_id: UUID, *, unit=None):
        row = self._fetch_one(
            select(shift_assignments).where(shift_assignments.c.assignment_id == assignment_id),
            unit=unit,
        )
        if row is None:
            raise KeyError(assignment_id)
        return _row_to_assignment(self.models, row)

    def list_assignments_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        rows = self._fetch_all(
            select(shift_assignments)
            .where(shift_assignments.c.shift_id == shift_id)
            .order_by(shift_assignments.c.assigned_at, shift_assignments.c.assignment_id),
            unit=unit,
        )
        return [_row_to_assignment(self.models, r) for r in rows]

    def get_active_assignment(self, shift_id: UUID, user_id: str, *, unit=None):
        row = self._fetch_one(
            select(shift_assignments).where(
                shift_assignments.c.shift_id == shift_id,
                shift_assignments.c.user_id == user_id,
                shift_assignments.c.status == "ACTIVE",
            ),
            unit=unit,
        )
        return _row_to_assignment(self.models, row) if row is not None else None

    def revoke_assignment(self, assignment_id: UUID, *, revoked_by: str, expected_version: int, unit=None):
        """Exact revoke semantics (SPEC R5): a matching-version update
        increments once; a repeat with the CURRENT (already-revoked) version
        is idempotent (returns unchanged, no second write); any other
        mismatch - including the version having moved between this method's
        own read and its write - is a controlled stale-version ``ValueError``
        (mapped to 409 by the service layer).

        P2C-C3A1-BUILD-REV-F3 repair: the UPDATE's ``version = :expected``
        predicate is now the ONLY authority for whether this call won -
        checked via rowcount, never inferred from a prior, separate SELECT.
        Under PostgreSQL READ COMMITTED, two concurrent callers can both
        legitimately observe the same pre-revoke version at the initial read;
        only one UPDATE can actually match that WHERE clause once the first
        writer commits, so the loser's rowcount is 0 and it MUST be refused,
        never re-SELECT the winner's row and report it as its own success."""
        with self._open(unit) as c:
            if c.execute(select(users.c.user_id).where(users.c.user_id == revoked_by)).first() is None:
                raise ValueError(f"unknown revoked_by actor: {revoked_by!r}")
            current = c.execute(
                select(shift_assignments).where(shift_assignments.c.assignment_id == assignment_id)
            ).mappings().first()
            if current is None:
                raise KeyError(assignment_id)
            if current["status"] == "REVOKED" and current["version"] == expected_version:
                return _row_to_assignment(self.models, current)
            new_version = expected_version + 1
            revoked_at = datetime.now(timezone.utc)
            result = c.execute(
                update(shift_assignments)
                .where(
                    shift_assignments.c.assignment_id == assignment_id,
                    shift_assignments.c.version == expected_version,
                )
                .values(status="REVOKED", revoked_by=revoked_by, revoked_at=revoked_at, version=new_version)
            )
            if result.rowcount == 0:
                # Either genuinely stale, or lost a concurrent race - the
                # UPDATE's own atomic predicate is the single source of
                # truth for both cases; either way, no partial write, no
                # audit, controlled 409 upstream.
                raise ValueError(
                    f"stale assignment version: expected {expected_version}, "
                    f"assignment {assignment_id} was not at that version"
                )
            row = c.execute(
                select(shift_assignments).where(shift_assignments.c.assignment_id == assignment_id)
            ).mappings().first()
        return _row_to_assignment(self.models, row)
