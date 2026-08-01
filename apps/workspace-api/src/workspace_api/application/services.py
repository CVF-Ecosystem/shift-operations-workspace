"""Event application service — the golden vertical for CVF enforcement.

``confirm`` runs the full CVF control chain in order before any state changes:

    identity -> permission -> risk -> evidence -> approval -> transition -> audit

Every refusal is a :class:`CvfDenied` naming the control that refused, so the
API layer maps it to the right HTTP status and the audit log records intent.

2026-07-26 (P2B-APPROVER-IDENTITY-RECONCILIATION): the caller-supplied
``approvals`` list is retired (it was High Finding #4 - approver identity
asserted by the confirmer, not the approver). The server now auto-collects
persisted, authenticated approval receipts matching the event's current scope
(SPEC R5.1) and evaluates them through a fresh, server-owned authority
resolver (SPEC R3.1). The whole read-decide-write path runs inside one
``transaction()`` so the resolver's reads are evaluated against the same
consistent state the mutation commits against.
"""

from uuid import UUID

from cvf_runtime.approval import assert_approval_satisfied
from cvf_runtime.audit import AuditLog, AuditRecord
from cvf_runtime.evidence import assert_evidence_sufficient
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_transition
from operations_domain.models import DataState, OperationalEvent
from workspace_api.application import approval_service
from workspace_api.application.assignment_scope import AssignmentScope

_CONTROL_CHAIN = ["identity", "permission", "risk", "evidence", "approval", "audit"]
_RECORD_TYPE = "OperationalEvent"
_ACTION = "event.confirm"


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

    def confirm(self, event_id: UUID, principal: Principal) -> OperationalEvent:
        require_action(principal, "event.confirm")
        with self.ledger.transaction() as unit:
            event = self.ledger.get_event(event_id, unit=unit)
            AssignmentScope(self.ledger).require_record(event, principal, unit=unit)
            risk_class = str(event.risk_class)

            # state: is CONFIRMED even reachable from event's own data-state?
            # NOTE: this only checks the event's own state, NOT the parent
            # shift. The parent-shift-frozen check happens at put_event()
            # below (both ledger backends reject a mutation whose shift is
            # FROZEN).
            assert_transition(event.state, DataState.CONFIRMED)

            # evidence: enough evidence links for this risk class?
            assert_evidence_sufficient(
                profile=self.profile,
                risk_class=risk_class,
                evidence_count=len(event.evidence),
            )

            # approval: server-collected receipts matching the event's
            # CURRENT scope, evaluated by a fresh authority resolver -
            # never a caller-supplied approval list (High Finding #4).
            receipts = approval_service.collect_receipts_for(
                self.ledger,
                record_type=_RECORD_TYPE,
                record_id=event_id,
                action=_ACTION,
                target_version=event.version,
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

            before = str(event.state)
            event.state = DataState.CONFIRMED
            event.version += 1

            # Unit-of-work: state change + audit append commit or roll back
            # together.
            self.ledger.put_event(event, unit=unit)
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
                ),
                unit=unit,
            )
        return event
