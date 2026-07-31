"""SQL report storage mixin (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).

Split out of ``sql_ledger.py`` (SPEC R25) to keep that host module a thin
wiring surface under the hard 300-line file-size guard. ``_ReportStoreMixin``
expects ``self._open``, ``self.models`` to already exist (provided by
``SqlLedger``); it owns no state of its own. Mirrors the prevalidate-before-
any-write and lifecycle-only-put patterns established by
``_handover_store.py``/``_incident_store.py``.

``content`` (a Pydantic ``ReportContent``) is persisted as one JSON(B) value
via ``model_dump(mode="json")`` and reconstructed with
``self.models.ReportContent(**row["content"])`` - lossless round-trip,
timezone-aware where applicable, matching SPEC R2's public-content shape.

``create_report_successor`` is the one compound, atomic method on this
mixin: it marks the previous current row non-current and inserts the new
current DRAFT row in the SAME connection, so a caller never observes a state
with zero or two current rows for one (shift_id, report_type) pair.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, select, update

from operations_ledger import _evidence, _rows
from operations_ledger.tables import customer_requests, reports, shifts, tasks

_REPORT_RECORD_TYPE = "Report"
_TASK_RECORD_TYPE = "Task"


def _report_row(report) -> dict:
    return {
        "report_id": report.report_id,
        "shift_id": report.shift_id,
        "report_type": str(report.report_type),
        "version": report.version,
        "status": str(report.status),
        "content": report.content.model_dump(mode="json"),
        "generated_from_cutoff": report.generated_from_cutoff,
        "created_at": report.created_at,
        "is_current": report.is_current,
    }


def _row_to_report(models, row):
    return models.Report(
        report_id=row["report_id"],
        shift_id=row["shift_id"],
        report_type=row["report_type"],
        version=row["version"],
        status=row["status"],
        content=models.ReportContent(**row["content"]),
        generated_from_cutoff=row["generated_from_cutoff"],
        created_at=row["created_at"],
        is_current=row["is_current"],
    )


class _ReportStoreMixin:
    def list_tasks_for_shift(self, shift_id, *, unit=None) -> list:
        """P2R (SPEC R6): every shift-bound Task INCLUDING terminal statuses -
        unlike open_work_snapshot's deliberately-open-only filter, a Report
        is a historical record, not an open-work worklist.

        Builds the Task directly from the row rather than delegating to
        ``_rows.row_to_task`` (outside this tranche's changed-set ceiling):
        that mapper never round-trips the persisted ``created_at`` column, so
        every read would otherwise reconstruct a fresh
        ``Task.created_at`` (its Pydantic default_factory) instead of the
        real, stable, database-owned value R7's deterministic ordering and
        digest input require."""
        with self._open(unit) as c:
            rows = c.execute(
                select(tasks).where(tasks.c.shift_id == shift_id)
                .order_by(tasks.c.created_at, tasks.c.task_id)
            ).mappings().all()
            return [
                self.models.Task(
                    task_id=r["task_id"], shift_id=r["shift_id"], title=r["title"],
                    description=r["description"], status=r["status"], owner_id=r["owner_id"],
                    due_at=r["due_at"], risk_class=r["risk"], state=r["state"], version=r["version"],
                    created_at=r["created_at"],
                    evidence=_evidence.evidence_for(
                        c, self.models, record_type=_TASK_RECORD_TYPE, record_id=r["task_id"]
                    ),
                )
                for r in rows
            ]

    def list_customer_requests_for_shift(self, shift_id, *, unit=None) -> list:
        """P2R (SPEC R6): every CustomerRequest whose non-null shift_id
        matches, including terminal CLOSED status."""
        with self._open(unit) as c:
            rows = c.execute(
                select(customer_requests).where(customer_requests.c.shift_id == shift_id)
                .order_by(customer_requests.c.received_at, customer_requests.c.request_id)
            ).mappings().all()
            return [_rows.row_to_customer_request(self.models, r) for r in rows]

    def _assert_new_report_valid(self, c, report, *, exclude_report_id=None) -> None:
        # F4 repair: an unknown or FROZEN parent shift is a distinct,
        # correctly-categorized conflict - checked explicitly (mirroring
        # _handover_store._assert_new_handover_valid) rather than left to
        # surface as a raw FK IntegrityError that a blanket `except` would
        # otherwise mislabel as "duplicate report_id".
        parent = c.execute(
            select(shifts.c.status).where(shifts.c.shift_id == report.shift_id)
        ).mappings().first()
        if parent is None:
            raise ValueError(f"unknown parent shift: {report.shift_id}")
        if parent["status"] == self.models.ShiftStatus.FROZEN.value:
            raise ValueError(f"cannot add report to a frozen shift: {report.shift_id}")

        existing_shift = c.execute(
            select(reports.c.report_id).where(reports.c.report_id == report.report_id)
        ).first()
        if existing_shift is not None:
            raise ValueError(f"duplicate report_id: {report.report_id}")

        dup_version = c.execute(
            select(reports.c.report_id).where(
                reports.c.shift_id == report.shift_id,
                reports.c.report_type == str(report.report_type),
                reports.c.version == report.version,
            )
        ).first()
        if dup_version is not None:
            raise ValueError(
                f"duplicate (shift_id, report_type, version): "
                f"({report.shift_id}, {report.report_type}, {report.version})"
            )

        if report.is_current:
            stmt = select(reports.c.report_id).where(
                reports.c.shift_id == report.shift_id,
                reports.c.report_type == str(report.report_type),
                reports.c.is_current.is_(True),
            )
            if exclude_report_id is not None:
                stmt = stmt.where(reports.c.report_id != exclude_report_id)
            current = c.execute(stmt).first()
            if current is not None:
                raise ValueError(
                    f"a current report already exists for "
                    f"(shift_id={report.shift_id}, report_type={report.report_type}); "
                    "use successor generation instead"
                )

    def add_report(self, report, *, unit=None):
        with self._open(unit) as c:
            self._assert_new_report_valid(c, report)
            # Parent existence/frozen-state and every duplicate/current
            # conflict are pre-validated above (F4) before this insert is
            # ever attempted, so no IntegrityError is expected here; letting
            # one propagate uncaught avoids re-introducing a mislabeling
            # catch-all that would blur a genuine unexpected DB conflict
            # with "duplicate report_id".
            c.execute(insert(reports).values(**_report_row(report)))
        return report

    def get_report(self, report_id: UUID, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(reports).where(reports.c.report_id == report_id)
            ).mappings().first()
            if row is None:
                raise KeyError(report_id)
        return _row_to_report(self.models, row)

    def get_current_report(self, shift_id: UUID, report_type: str, *, unit=None):
        with self._open(unit) as c:
            rows = c.execute(
                select(reports).where(
                    reports.c.shift_id == shift_id,
                    reports.c.report_type == str(report_type),
                    reports.c.is_current.is_(True),
                )
            ).mappings().all()
        if len(rows) == 0:
            return None
        if len(rows) > 1:
            raise ValueError(
                f"ambiguous current report for (shift_id={shift_id}, report_type={report_type}): "
                f"{len(rows)} current rows found"
            )
        return _row_to_report(self.models, rows[0])

    def list_reports_for_shift(self, shift_id: UUID, report_type: str | None = None, *, unit=None) -> list:
        with self._open(unit) as c:
            stmt = select(reports).where(reports.c.shift_id == shift_id)
            if report_type is not None:
                stmt = stmt.where(reports.c.report_type == str(report_type))
            stmt = stmt.order_by(reports.c.version.desc(), reports.c.report_id)
            rows = c.execute(stmt).mappings().all()
        return [_row_to_report(self.models, r) for r in rows]

    def _assert_report_put_is_lifecycle_only(self, current, incoming) -> None:
        # F2 repair: put_report may change ONLY `status`. every other field -
        # including is_current, created_at and every ReportContent sub-field
        # individually (not just the aggregate digest, so a tampered content
        # that happens to preserve the old digest is still caught) - must be
        # byte-identical to the persisted row.
        if incoming.report_id != current.report_id:
            raise ValueError(f"report snapshot is immutable: report_id changed for {incoming.report_id}")
        if incoming.shift_id != current.shift_id or incoming.report_type != current.report_type:
            raise ValueError(f"report snapshot is immutable: shift/type changed for {incoming.report_id}")
        if incoming.version != current.version:
            raise ValueError(f"report snapshot is immutable: version changed for {incoming.report_id}")
        if incoming.generated_from_cutoff != current.generated_from_cutoff:
            raise ValueError(f"report snapshot is immutable: cutoff changed for {incoming.report_id}")
        if incoming.created_at != current.created_at:
            raise ValueError(f"report snapshot is immutable: created_at changed for {incoming.report_id}")
        if incoming.is_current != current.is_current:
            raise ValueError(
                f"report is_current is lifecycle-owned and cannot be changed via put_report for {incoming.report_id}"
            )
        if incoming.content.schema_version != current.content.schema_version:
            raise ValueError(f"report snapshot is immutable: schema_version changed for {incoming.report_id}")
        if incoming.content.sections != current.content.sections:
            raise ValueError(f"report snapshot is immutable: sections changed for {incoming.report_id}")
        if incoming.content.source_manifest != current.content.source_manifest:
            raise ValueError(f"report snapshot is immutable: source_manifest changed for {incoming.report_id}")
        if incoming.content.snapshot_digest != current.content.snapshot_digest:
            raise ValueError(f"report snapshot is immutable: content changed for {incoming.report_id}")

    def put_report(self, report, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(reports).where(reports.c.report_id == report.report_id)
            ).mappings().first()
            if row is None:
                raise KeyError(report.report_id)
            current = _row_to_report(self.models, row)
            self._assert_report_put_is_lifecycle_only(current, report)

            result = c.execute(
                update(reports).where(reports.c.report_id == report.report_id)
                .values(status=str(report.status))
            )
            if result.rowcount == 0:
                raise KeyError(report.report_id)
        return report

    def create_report_successor(self, previous_report_id: UUID, successor, *, unit=None):
        """Atomically marks ``previous_report_id`` non-current and inserts
        ``successor`` as the new current row - SPEC R12: all steps commit or
        roll back together, never producing a state with zero or two current
        rows for one (shift_id, report_type)."""
        with self._open(unit) as c:
            row = c.execute(
                select(reports).where(reports.c.report_id == previous_report_id)
            ).mappings().first()
            if row is None:
                raise KeyError(previous_report_id)
            previous = _row_to_report(self.models, row)
            if not previous.is_current:
                raise ValueError(f"report is not current: {previous_report_id}")
            if previous.shift_id != successor.shift_id or previous.report_type != successor.report_type:
                raise ValueError("successor shift_id/report_type must match predecessor")
            if successor.version != previous.version + 1:
                raise ValueError(
                    f"successor version must be exactly {previous.version + 1}, got {successor.version}"
                )
            # F3 repair: a successor must be a fresh current DRAFT - any other
            # status/current combination would either leave zero current
            # reports (is_current=False) or insert an already-decided
            # snapshot that never went through generate/review/approve.
            if not successor.is_current:
                raise ValueError("successor must be inserted as the current report (is_current=True)")
            if str(successor.status) != "DRAFT":
                raise ValueError(f"successor must be a fresh DRAFT report, got status={successor.status}")
            self._assert_new_report_valid(c, successor, exclude_report_id=previous_report_id)

            result = c.execute(
                update(reports).where(reports.c.report_id == previous_report_id)
                .values(is_current=False)
            )
            if result.rowcount == 0:
                raise KeyError(previous_report_id)
            c.execute(insert(reports).values(**_report_row(successor)))
        return successor
