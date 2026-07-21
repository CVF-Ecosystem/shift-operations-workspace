"""Event application service — the golden vertical for CVF enforcement.

``confirm`` runs the full CVF control chain in order before any state changes:

    identity -> permission -> risk -> evidence -> approval -> transition -> audit

Every refusal is a :class:`CvfDenied` naming the control that refused, so the
API layer maps it to the right HTTP status and the audit log records intent.
This replaces the previous symbolic guard (a bare non-empty ``approver_id``
string) called out in the EA independent review.
"""

from uuid import UUID

from cvf_runtime.approval import Approval, assert_approval_satisfied
from cvf_runtime.audit import AuditLog, AuditRecord
from cvf_runtime.evidence import assert_evidence_sufficient
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from workspace_api.domain.lifecycle import assert_transition
from workspace_api.domain.models import DataState, OperationalEvent

_CONTROL_CHAIN = ["identity", "permission", "risk", "evidence", "approval", "audit"]


class EventService:
    def __init__(
        self,
        ledger: Ledger,
        audit: AuditLog,
        profile: CvfProfile | None = None,
    ):
        self.ledger = ledger
        self.audit = audit
        self.profile = profile or load_profile()

    def confirm(
        self,
        event_id: UUID,
        principal: Principal,
        approvals: list[Approval],
    ) -> OperationalEvent:
        event = self.ledger.get_event(event_id)
        risk_class = str(event.risk_class)

        # permission: may this principal confirm events at all?
        require_action(principal, "event.confirm")

        # state: is CONFIRMED even reachable from here? (also blocks frozen)
        assert_transition(event.state, DataState.CONFIRMED)

        # evidence: enough evidence links for this risk class?
        assert_evidence_sufficient(
            profile=self.profile,
            risk_class=risk_class,
            evidence_count=len(event.evidence),
        )

        # approval: is the required quorum met by distinct, authorized principals?
        assert_approval_satisfied(
            profile=self.profile,
            risk_class=risk_class,
            confirmer=principal,
            approvals=approvals,
        )

        before = str(event.state)
        event.state = DataState.CONFIRMED
        event.version += 1
        self.ledger.put_event(event)

        # audit: append-only record of the confirmed mutation, written durably
        # through the ledger (survives restart when a SqlLedger backs it).
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action="event.confirm",
                record_type="OperationalEvent",
                record_id=str(event_id),
                control_chain=_CONTROL_CHAIN,
                before_state=before,
                after_state=str(event.state),
            )
        )
        return event
