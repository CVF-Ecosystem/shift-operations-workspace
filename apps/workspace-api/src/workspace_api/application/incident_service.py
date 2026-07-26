"""Incident application service — fifth CVF vertical (P2-A).

Reuses the SAME cvf-runtime gates as Event/Task/CustomerRequest services: it
does not re-implement identity, permission, domain_lock, risk, evidence,
approval or audit.

Three governed actions:
* report       — identity -> permission -> domain_lock -> persist (evidence +
                 incident atomically) -> audit. Reporting an incident is
                 immediate; it is NOT the protected acceptance decision
                 (ADR section 2.2).
* acknowledge  — identity -> permission -> risk -> evidence -> approval ->
                 lifecycle -> persist -> audit. The protected R2+ decision
                 that accepts the incident into the governed workflow, reusing
                 the same durable receipt architecture as event.confirm/
                 task.create (SPEC R8): receipts bind to the already-persisted
                 Incident's (record_id, version), never a caller-supplied
                 approver identity.
* transition   — identity -> permission -> lifecycle -> frozen-parent -> persist
                 -> audit. Post-acknowledgement progress only: REPORTED ->
                 ACKNOWLEDGED is refused here even though the lifecycle guard's
                 full graph allows it (SPEC R2/R9) - only ``acknowledge`` may
                 perform that specific move.
"""

from uuid import UUID

from cvf_runtime.approval import assert_approval_satisfied
from cvf_runtime.audit import AuditRecord
from cvf_runtime.domain_lock import assert_domain_allowed
from cvf_runtime.errors import CvfDenied
from cvf_runtime.evidence import assert_evidence_sufficient
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_incident_transition
from operations_domain.models import Incident, IncidentStatus
from workspace_api.application import approval_service

_REPORT_CHAIN = ["identity", "permission", "domain_lock", "audit"]
_ACKNOWLEDGE_CHAIN = ["identity", "permission", "risk", "evidence", "approval", "audit"]
_TRANSITION_CHAIN = ["identity", "permission", "freeze", "audit"]

_INCIDENT_DOMAIN = "equipment_incident"
_RECORD_TYPE = "Incident"
_ACKNOWLEDGE_ACTION = "incident.acknowledge"


class IncidentService:
    def __init__(self, ledger: Ledger, profile: CvfProfile | None = None):
        self.ledger = ledger
        self.profile = profile or load_profile()

    def report(self, incident: Incident, principal: Principal) -> Incident:
        require_action(principal, "incident.report")
        assert_domain_allowed(self.profile, _INCIDENT_DOMAIN)

        with self.ledger.transaction() as unit:
            stored = self.ledger.add_incident(incident, unit=unit)
            self._audit(
                principal, "incident.report", stored.incident_id, _REPORT_CHAIN,
                None, str(stored.status), unit=unit,
            )
        return stored

    def acknowledge(self, incident_id: UUID, principal: Principal) -> Incident:
        with self.ledger.transaction() as unit:
            incident = self.ledger.get_incident(incident_id, unit=unit)
            risk_class = str(incident.risk_class)

            require_action(principal, "incident.acknowledge")
            assert_incident_transition(incident.status, IncidentStatus.ACKNOWLEDGED)
            assert_evidence_sufficient(
                profile=self.profile, risk_class=risk_class, evidence_count=len(incident.evidence),
            )

            receipts = approval_service.collect_receipts_for(
                self.ledger,
                record_type=_RECORD_TYPE,
                record_id=incident_id,
                action=_ACKNOWLEDGE_ACTION,
                target_version=incident.version,
                risk_class=risk_class,
                payload_digest=None,
                unit=unit,
            )
            authority_for = approval_service.authority_for_factory(self.ledger, unit=unit)
            assert_approval_satisfied(
                profile=self.profile,
                risk_class=risk_class,
                confirmer=principal,
                receipts=receipts,
                authority_for=authority_for,
            )

            before = str(incident.status)
            incident.status = IncidentStatus.ACKNOWLEDGED
            incident.version += 1

            self.ledger.put_incident(incident, unit=unit)
            self._audit(
                principal, _ACKNOWLEDGE_ACTION, incident_id, _ACKNOWLEDGE_CHAIN,
                before, str(incident.status), unit=unit,
            )
        return incident

    def transition(
        self,
        incident_id: UUID,
        principal: Principal,
        target_status: IncidentStatus,
    ) -> Incident:
        incident = self.ledger.get_incident(incident_id)

        require_action(principal, "incident.transition")
        if incident.status == IncidentStatus.REPORTED:
            raise CvfDenied(
                control="lifecycle",
                reason=(
                    "REPORTED incidents must be accepted via POST "
                    "/incidents/{incident_id}/acknowledge, not the generic transition action"
                ),
                http_status=409,
            )
        assert_incident_transition(incident.status, target_status)

        before = str(incident.status)
        incident.status = target_status
        incident.version += 1

        with self.ledger.transaction() as unit:
            self.ledger.put_incident(incident, unit=unit)
            self._audit(
                principal, "incident.transition", incident_id, _TRANSITION_CHAIN,
                before, str(incident.status), unit=unit,
            )
        return incident

    def _audit(self, principal, action, record_id, chain, before, after, *, unit=None) -> None:
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action=action,
                record_type=_RECORD_TYPE,
                record_id=str(record_id),
                control_chain=chain,
                before_state=before,
                after_state=after,
            ),
            unit=unit,
        )
