"""In-memory incident storage mixin (fifth vertical, P2-A).

Split out of ``repository.py`` (SPEC R11 / ADR section 2.4) to keep that host
module a thin wiring surface, matching ``_approval_store.py``'s pattern.
``_IncidentRepositoryMixin`` expects ``self._lock``, ``self.incidents`` and
``self._assert_shift_not_frozen`` to already exist (set up by
``InMemoryLedger.__init__``); it owns no state of its own.

INC-REV-F2: ``add_incident`` previously silently overwrote an existing id
(no duplicate check at all); it now raises the SAME controlled ``ValueError``
shape ``operations_ledger.sql_ledger`` raises for a duplicate primary key, so
the application layer maps both backends identically. ``put_incident`` now
raises ``KeyError`` for a missing id, matching ``SqlLedger``. List ordering
adds an ``incident_id`` tie-break after ``created_at`` so equal timestamps
stay deterministic.
"""

from __future__ import annotations

from uuid import UUID

from operations_domain.models import Incident


class _IncidentRepositoryMixin:
    def add_incident(self, incident: Incident, *, unit=None) -> Incident:
        self._assert_shift_not_frozen(incident.shift_id, "add incident to a frozen shift")
        with self._lock:
            if incident.incident_id in self.incidents:
                raise ValueError(f"duplicate incident_id: {incident.incident_id}")
            stored = incident.model_copy()
            self.incidents[incident.incident_id] = stored
            return stored.model_copy()

    def get_incident(self, incident_id: UUID, *, unit=None) -> Incident:
        with self._lock:
            return self.incidents[incident_id].model_copy()

    def list_incidents_for_shift(self, shift_id: UUID, *, unit=None) -> list[Incident]:
        with self._lock:
            return sorted(
                (i.model_copy() for i in self.incidents.values() if i.shift_id == shift_id),
                key=lambda i: (i.created_at, i.incident_id),
            )

    def put_incident(self, incident: Incident, *, unit=None) -> Incident:
        self._assert_shift_not_frozen(incident.shift_id, "modify incident in a frozen shift")
        with self._lock:
            if incident.incident_id not in self.incidents:
                raise KeyError(incident.incident_id)
            stored = incident.model_copy()
            self.incidents[incident.incident_id] = stored
            return stored.model_copy()
