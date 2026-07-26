"""SQL incident storage mixin (fifth vertical, P2-A).

Split out of ``sql_ledger.py`` (SPEC R11 / ADR section 2.4) to keep that host
module a thin wiring surface under the hard 300-line file-size guard.
``_IncidentStoreMixin`` expects ``self._open``, ``self._fetch_one``,
``self._fetch_all``, ``self.models`` and ``self._assert_shift_not_frozen`` to
already exist (provided by ``SqlLedger``); it owns no state of its own.
Row<->model mapping lives here rather than in ``_rows.py`` (the shared helper
module is outside this tranche's authorized changed set) - self-contained,
same as every other method on this mixin.

INC-REV-F2/F3: ``add_incident`` raises the SAME controlled ``ValueError``
shape ``add_task`` already uses on a duplicate primary key (never a raw,
backend-specific ``IntegrityError`` reaching the application layer);
``put_incident`` raises ``KeyError`` when no row matched, matching
``InMemoryLedger``; and ``list_incidents_for_shift`` reconstructs each
incident's evidence inside the SAME connection/unit as the select (previously
it silently returned incidents with zero evidence - a real read-path bug, not
just a missing test), ordered by ``(created_at, incident_id)`` so a tied
timestamp is still deterministic.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from operations_ledger import _evidence
from operations_ledger.tables import incidents

_INCIDENT_RECORD_TYPE = "Incident"


def _incident_row(incident) -> dict:
    return {
        "incident_id": incident.incident_id,
        "shift_id": incident.shift_id,
        "risk": str(incident.risk_class),
        "summary": incident.summary,
        "description": incident.description,
        "status": str(incident.status),
        "owner_id": incident.owner_id,
        "version": incident.version,
    }


def _row_to_incident(models, row, *, evidence=None):
    return models.Incident(
        incident_id=row["incident_id"],
        shift_id=row["shift_id"],
        risk_class=row["risk"],
        summary=row["summary"],
        description=row["description"],
        status=row["status"],
        owner_id=row["owner_id"],
        version=row["version"],
        created_at=row["created_at"],
        evidence=evidence or [],
    )


class _IncidentStoreMixin:
    def add_incident(self, incident, *, unit=None):
        with self._open(unit) as c:
            self._assert_shift_not_frozen(c, incident.shift_id, "add incident to a frozen shift")
            try:
                c.execute(insert(incidents).values(**_incident_row(incident)))
            except IntegrityError as exc:
                # Same controlled shape add_task uses (operations_ledger.sql_ledger.add_task)
                # so the application layer maps both backends identically.
                raise ValueError(f"duplicate incident_id: {incident.incident_id}") from exc
            _evidence.insert_evidence(
                c, incident.evidence, record_type=_INCIDENT_RECORD_TYPE, record_id=incident.incident_id
            )
        return incident

    def get_incident(self, incident_id: UUID, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(incidents).where(incidents.c.incident_id == incident_id)
            ).mappings().first()
            if row is None:
                raise KeyError(incident_id)
            evidence = _evidence.evidence_for(
                c, self.models, record_type=_INCIDENT_RECORD_TYPE, record_id=incident_id
            )
        return _row_to_incident(self.models, row, evidence=evidence)

    def list_incidents_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        with self._open(unit) as c:
            rows = c.execute(
                select(incidents)
                .where(incidents.c.shift_id == shift_id)
                .order_by(incidents.c.created_at, incidents.c.incident_id)
            ).mappings().all()
            return [
                _row_to_incident(
                    self.models, r,
                    evidence=_evidence.evidence_for(
                        c, self.models, record_type=_INCIDENT_RECORD_TYPE, record_id=r["incident_id"]
                    ),
                )
                for r in rows
            ]

    def put_incident(self, incident, *, unit=None):
        with self._open(unit) as c:
            self._assert_shift_not_frozen(c, incident.shift_id, "modify incident in a frozen shift")
            result = c.execute(
                update(incidents)
                .where(incidents.c.incident_id == incident.incident_id)
                .values(**_incident_row(incident))
            )
            if result.rowcount == 0:
                raise KeyError(incident.incident_id)
        return incident
