"""``LedgerTargetEligibility`` (SPEC R14/R18): implements
``conversation_routing.ports.TargetEligibilityPort`` against live Workspace
API state - conversation-routing never queries shift/incident/assignment
tables directly. Split out of ``p4e_placement.py`` for the file-size guard
(completion-rereview R2 grew that file past the 300-line hard limit)."""

from __future__ import annotations

from operations_ledger import Ledger


class LedgerTargetEligibility:
    def __init__(self, ledger: Ledger, workspace_digest: str, *, unit=None) -> None:
        self._ledger = ledger
        self._workspace_digest = workspace_digest
        self._unit = unit

    def workspace_digest(self) -> str:
        return self._workspace_digest

    def shift_eligible(self, shift_id: str):
        try:
            shift = self._ledger.get_shift(shift_id, unit=self._unit)
        except (KeyError, ValueError):
            return False, 0
        eligible = str(shift.status) not in ("CLOSED", "FROZEN")
        return eligible, shift.version

    def incident_eligible(self, incident_id: str):
        try:
            incident = self._ledger.get_incident(incident_id, unit=self._unit)
        except (KeyError, ValueError):
            return False, 0, None
        eligible = str(incident.status) != "CLOSED"
        return eligible, incident.version, str(incident.shift_id)

    def user_assignment_eligible(self, user_id: str, shift_id: str) -> bool:
        try:
            assignment = self._ledger.get_active_assignment(shift_id, user_id, unit=self._unit)
        except (KeyError, ValueError):
            return False
        return assignment is not None and str(assignment.status) == "ACTIVE"
