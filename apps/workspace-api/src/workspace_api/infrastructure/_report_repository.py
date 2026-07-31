"""In-memory report storage mixin (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).

Split out of ``repository.py`` (SPEC R25) to keep that host module a thin
wiring surface, matching ``_incident_repository.py``/``_handover_repository.py``'s
pattern. ``_ReportRepositoryMixin`` expects ``self._lock`` and
``self.reports`` to already exist (set up by ``InMemoryLedger.__init__``);
it owns no state of its own.

``model_copy(deep=True)`` is required (not the shallow ``model_copy()`` other
mixins use for flat models) because ``Report.content`` nests a
``ReportContent`` with further nested ``ReportSection``/``ReportSourceRef``
lists - a shallow copy would still let a caller mutate a stored section
through the returned reference, mirroring ``_handover_repository.py``'s
reasoning for ``Handover.items``.

Prevalidation mirrors ``_report_store.py``'s SQL mixin exactly: every
``ValueError`` category (duplicate id, duplicate version, ambiguous current)
is raised before any dict mutation, so a rejection here is always a complete
no-op.
"""

from __future__ import annotations

from uuid import UUID

from operations_domain.models import Report


class _ReportRepositoryMixin:
    def list_tasks_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        """P2R (SPEC R6): every shift-bound Task INCLUDING terminal statuses -
        unlike open_work_snapshot's deliberately-open-only filter."""
        with self._lock:
            return sorted(
                (t.model_copy() for t in self.tasks.values() if t.shift_id == shift_id),
                key=lambda t: (t.created_at, t.task_id),
            )

    def list_customer_requests_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        """P2R (SPEC R6): every CustomerRequest whose non-null shift_id
        matches, including terminal CLOSED status."""
        with self._lock:
            return sorted(
                (r.model_copy() for r in self.customer_requests.values() if r.shift_id == shift_id),
                key=lambda r: (r.received_at, r.request_id),
            )

    def _assert_new_report_valid(self, report: Report, *, exclude_report_id: UUID | None = None) -> None:
        # F4 repair: an unknown or FROZEN parent shift is a distinct,
        # correctly-categorized ValueError - checked explicitly here so
        # InMemoryLedger/SqlLedger/PostgreSQL agree on both the refusal and
        # its category (never a raw KeyError from self.shifts[...] leaking
        # through, and never conflated with "duplicate report_id").
        parent = self.shifts.get(report.shift_id)
        if parent is None:
            raise ValueError(f"unknown parent shift: {report.shift_id}")
        if str(parent.status) == "FROZEN":
            raise ValueError(f"cannot add report to a frozen shift: {report.shift_id}")

        if report.report_id in self.reports:
            raise ValueError(f"duplicate report_id: {report.report_id}")

        for existing in self.reports.values():
            if (
                existing.shift_id == report.shift_id
                and existing.report_type == report.report_type
                and existing.version == report.version
            ):
                raise ValueError(
                    f"duplicate (shift_id, report_type, version): "
                    f"({report.shift_id}, {report.report_type}, {report.version})"
                )

        if report.is_current:
            for existing in self.reports.values():
                if existing.report_id == exclude_report_id:
                    continue
                if (
                    existing.shift_id == report.shift_id
                    and existing.report_type == report.report_type
                    and existing.is_current
                ):
                    raise ValueError(
                        f"a current report already exists for "
                        f"(shift_id={report.shift_id}, report_type={report.report_type}); "
                        "use successor generation instead"
                    )

    def add_report(self, report: Report, *, unit=None) -> Report:
        with self._lock:
            self._assert_new_report_valid(report)
            stored = report.model_copy(deep=True)
            self.reports[report.report_id] = stored
            return stored.model_copy(deep=True)

    def get_report(self, report_id: UUID, *, unit=None) -> Report:
        with self._lock:
            return self.reports[report_id].model_copy(deep=True)

    def get_current_report(self, shift_id: UUID, report_type: str, *, unit=None) -> Report | None:
        with self._lock:
            matches = [
                r for r in self.reports.values()
                if r.shift_id == shift_id and str(r.report_type) == str(report_type) and r.is_current
            ]
        if len(matches) == 0:
            return None
        if len(matches) > 1:
            raise ValueError(
                f"ambiguous current report for (shift_id={shift_id}, report_type={report_type}): "
                f"{len(matches)} current rows found"
            )
        return matches[0].model_copy(deep=True)

    def list_reports_for_shift(self, shift_id: UUID, report_type: str | None = None, *, unit=None) -> list[Report]:
        with self._lock:
            matches = [
                r for r in self.reports.values()
                if r.shift_id == shift_id and (report_type is None or str(r.report_type) == str(report_type))
            ]
            return sorted(
                (r.model_copy(deep=True) for r in matches),
                key=lambda r: (-r.version, str(r.report_id)),
            )

    def _assert_report_put_is_lifecycle_only(self, current: Report, incoming: Report) -> None:
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

    def put_report(self, report: Report, *, unit=None) -> Report:
        with self._lock:
            current = self.reports.get(report.report_id)
            if current is None:
                raise KeyError(report.report_id)
            self._assert_report_put_is_lifecycle_only(current, report)
            updated = current.model_copy(deep=True)
            updated.status = report.status
            self.reports[report.report_id] = updated
            return updated.model_copy(deep=True)

    def create_report_successor(self, previous_report_id: UUID, successor: Report, *, unit=None) -> Report:
        with self._lock:
            previous = self.reports.get(previous_report_id)
            if previous is None:
                raise KeyError(previous_report_id)
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
            self._assert_new_report_valid(successor, exclude_report_id=previous_report_id)

            updated_previous = previous.model_copy(deep=True)
            updated_previous.is_current = False
            self.reports[previous_report_id] = updated_previous

            stored_successor = successor.model_copy(deep=True)
            self.reports[successor.report_id] = stored_successor
            return stored_successor.model_copy(deep=True)
