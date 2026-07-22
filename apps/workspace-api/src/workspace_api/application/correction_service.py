"""Correction application service — the second CVF golden vertical.

Post-freeze the architecture forbids silent overwrite: any change to a confirmed
or frozen record must produce a Correction record with before/after, reason,
actor, version and approval (freeze-policy.yaml: post_freeze_mutation =
correction_record_only, silent_overwrite = prohibited).

This service reuses the SAME cvf-runtime gates as EventService — it does not
re-implement permission, approval, or audit. That reuse is the point of the
golden vertical: a new domain wires the existing chain, it does not fork it.

Chain: identity -> permission -> correctable-state -> approval -> record -> audit
"""

from uuid import UUID

from cvf_runtime.approval import Approval, assert_approval_satisfied
from cvf_runtime.audit import AuditLog, AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from workspace_api.domain.models import Correction, DataState, OperationalEvent

_CONTROL_CHAIN = ["identity", "permission", "freeze", "approval", "audit"]

# A record may only be corrected once it is an official fact.
_CORRECTABLE_STATES = {DataState.CONFIRMED, DataState.CORRECTED, DataState.FROZEN}


class CorrectionService:
    def __init__(
        self,
        ledger: Ledger,
        audit: AuditLog,
        profile: CvfProfile | None = None,
    ):
        self.ledger = ledger
        self.audit = audit
        self.profile = profile or load_profile()

    def correct_event(
        self,
        event_id: UUID,
        principal: Principal,
        reason: str,
        approvals: list[Approval],
    ) -> Correction:
        event: OperationalEvent = self.ledger.get_event(event_id)
        risk_class = str(event.risk_class)

        # permission: may this principal issue corrections?
        require_action(principal, "event.correct")

        # freeze/state: only an official fact can be corrected; a proposal must
        # go through normal confirmation, not a correction record.
        if event.state not in _CORRECTABLE_STATES:
            raise CvfDenied(
                control="freeze",
                reason=(
                    f"cannot correct an event in state {event.state}; "
                    f"only {sorted(s.value for s in _CORRECTABLE_STATES)} are correctable"
                ),
                http_status=409,
            )

        # evidence-of-intent: a correction must state why (audit requirement).
        if not reason or not reason.strip():
            raise CvfDenied(
                control="audit",
                reason="correction requires a non-empty reason",
                http_status=422,
            )

        # approval: a correction carries the same quorum as the record's risk.
        assert_approval_satisfied(
            profile=self.profile,
            risk_class=risk_class,
            confirmer=principal,
            approvals=approvals,
        )

        previous_version = event.version
        new_version = previous_version + 1

        # Record the correction (before/after preserved as versions). The frozen
        # record is not silently overwritten: state stays FROZEN if it was
        # frozen; a CONFIRMED record moves to CORRECTED.
        before_state = str(event.state)
        if event.state == DataState.CONFIRMED:
            event.state = DataState.CORRECTED
        event.version = new_version

        correction = Correction(
            record_type="OperationalEvent",
            record_id=event_id,
            reason=reason.strip(),
            requested_by=principal.user_id,
            previous_version=previous_version,
            new_version=new_version,
        )

        # Unit-of-work: event update + correction insert + audit append
        # commit or roll back together (P-FIX-2 / High Finding #5).
        with self.ledger.transaction() as unit:
            # allow_when_frozen=True: a correction record is the one permitted
            # post-freeze mutation path (freeze-policy.yaml:
            # post_freeze_mutation = correction_record_only). Every other write
            # path defaults to blocking a frozen shift.
            self.ledger.put_event(event, allow_when_frozen=True, unit=unit)
            self.ledger.add_correction(correction, unit=unit)
            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="event.correct",
                    record_type="OperationalEvent",
                    record_id=str(event_id),
                    control_chain=_CONTROL_CHAIN,
                    before_state=before_state,
                    after_state=str(event.state),
                ),
                unit=unit,
            )
        return correction
