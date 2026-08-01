"""Task application service — third CVF vertical, replicating the chain.

Reuses the SAME cvf-runtime gates as EventService/CorrectionService: it does not
re-implement identity, permission, domain_lock, risk, approval, evidence or
audit. That reuse is the whole point of the golden vertical — a new operational
domain wires the existing chain rather than forking it.

Governed actions:
* create_creation_intent — R2+ only: identity -> permission -> persist the
  durable, digest-bound target `task.create` receipts bind to (ADR section
  4.4). No Task row exists yet.
* create_task    — identity -> permission -> domain_lock -> (for R2+: load the
                   creation intent, verify proposer/digest, then risk+evidence
                   +approval) -> persist -> audit.
* transition     — identity -> permission -> task-status lifecycle -> persist
                   -> audit.

2026-07-26 (P2B-APPROVER-IDENTITY-RECONCILIATION): the caller-supplied
``approvals`` list is retired. For R0/R1 (no required roles), ``create_task``
persists directly, exactly as before. For R2+, ``create_task`` now requires a
prior, digest-matching ``TaskCreationIntent`` (SPEC R9) instead of accepting
approvals inline - there is no pre-existing Task row an approver could
otherwise inspect before the record is created.
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
from cvf_runtime.risk import requirement_for
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_task_transition
from operations_domain.models import Task, TaskCreationIntent, TaskStatus
from workspace_api.application import approval_service
from workspace_api.application.assignment_scope import AssignmentScope, require_active_assignment
from workspace_api.application.mutation_preconditions import assert_version_precondition

_CREATE_CHAIN = ["identity", "permission", "domain_lock", "risk", "evidence", "approval", "audit"]
_TRANSITION_CHAIN = ["identity", "permission", "freeze", "audit"]

# Tasks belong to the shift-operation domain (domain-lock.yaml).
_TASK_DOMAIN = "shift_operation"


class TaskService:
    def __init__(self, ledger: Ledger, profile: CvfProfile | None = None):
        self.ledger = ledger
        self.profile = profile or load_profile()

    def create_creation_intent(self, task: Task, principal: Principal) -> TaskCreationIntent:
        """R9.1: durable, approver-visible target for a future `task.create`
        approval quorum. Only valid when the risk class actually requires
        approval (R0/R1 tasks use the direct ``create_task`` path)."""
        return approval_service.create_task_creation_intent(
            self.ledger, principal, task=task, profile=self.profile
        )

    def get_creation_intent(self, intent_id: UUID, principal: Principal) -> TaskCreationIntent:
        return approval_service.get_task_creation_intent(
            self.ledger, principal, intent_id, profile=self.profile
        )

    def create_task(
        self,
        task: Task,
        principal: Principal,
        *,
        intent_id: UUID | None = None,
    ) -> Task:
        risk_class = str(task.risk_class)

        require_action(principal, "task.create")
        assert_domain_allowed(self.profile, _TASK_DOMAIN)
        require_active_assignment(self.ledger, task.shift_id, principal)

        requirement = requirement_for(self.profile, risk_class)

        if requirement.required_roles:
            return self._create_task_from_intent(task, principal, intent_id=intent_id)

        # R0/R1: no approval quorum required; a dangling intent_id would be a
        # dead, confusing parameter (R9.3).
        if intent_id is not None:
            raise CvfDenied(
                control="approval",
                reason=f"{risk_class} requires no approval; intent_id must be omitted",
                http_status=422,
            )
        assert_evidence_sufficient(
            profile=self.profile, risk_class=risk_class, evidence_count=len(task.evidence)
        )
        with self.ledger.transaction() as unit:
            stored = self.ledger.add_task(task, unit=unit)
            self._audit(
                principal, "task.create", stored.task_id, _CREATE_CHAIN,
                None, str(stored.status), unit=unit,
            )
        return stored

    def _create_task_from_intent(
        self, task: Task, principal: Principal, *, intent_id: UUID | None
    ) -> Task:
        # A higher-risk task (R2+) is an operational commitment: it must be
        # consuming a durable, digest-matching creation intent the approvers
        # actually reviewed (R9.3/R9.4), not a bare inline approvals list.
        if intent_id is None:
            raise CvfDenied(
                control="approval",
                reason=(
                    f"{task.risk_class} requires approval; POST /tasks/creation-intents "
                    f"first, then submit intent_id"
                ),
                http_status=422,
            )

        with self.ledger.transaction() as unit:
            try:
                intent = self.ledger.get_task_creation_intent(intent_id, unit=unit)
            except KeyError as exc:
                raise CvfDenied(
                    control="approval", reason="creation intent not found", http_status=404
                ) from exc

            # Only the proposer may consume their own intent (closes an
            # actor-coherence gap: someone else "spending" an approved intent
            # under a different actor identity).
            if intent.created_by != principal.user_id:
                raise CvfDenied(
                    control="approval",
                    reason="only the creation intent's proposer may consume it",
                    http_status=409,
                )

            # Recompute the digest from the request body ACTUALLY submitted
            # right now and require it to equal the intent's stored digest -
            # the TOCTOU/payload-substitution defence (R9.4).
            digest = approval_service.compute_payload_digest(task)
            if digest != intent.payload_digest:
                raise CvfDenied(
                    control="approval",
                    reason="submitted payload no longer matches the approved creation intent",
                    http_status=409,
                )

            risk_class = str(intent.risk_class)
            assert_evidence_sufficient(
                profile=self.profile, risk_class=risk_class, evidence_count=len(task.evidence)
            )

            receipts = approval_service.collect_receipts_for(
                self.ledger,
                record_type="Task",
                record_id=intent_id,
                action="task.create",
                target_version=1,
                risk_class=risk_class,
                payload_digest=intent.payload_digest,
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

            # task_id := intent_id (R9.4 point 3/R9.5): the receipt's
            # record_id and the eventual Task.task_id are the same value
            # throughout.
            task.task_id = intent_id
            try:
                stored = self.ledger.add_task(task, unit=unit)
            except ValueError as exc:
                # R9.6: a second POST /tasks against the same intent collides
                # on the task_id primary key, independent of receipt state -
                # both backends raise this same ValueError shape.
                if "duplicate task_id" not in str(exc):
                    raise
                raise CvfDenied(
                    control="approval",
                    reason=f"creation intent {intent_id} was already consumed",
                    http_status=409,
                ) from exc

            self._audit(
                principal, "task.create", stored.task_id, _CREATE_CHAIN,
                None, str(stored.status), unit=unit,
            )
        return stored

    def transition(
        self,
        task_id: UUID,
        principal: Principal,
        target_status: TaskStatus,
        *,
        expected_version: int | None = None,
    ) -> Task:
        require_action(principal, "task.transition")
        # C3B2-WO-REV-F2: the stored-target read, assignment admission,
        # precondition compare, lifecycle check and mutation all now share
        # ONE transaction - previously the read/decision happened outside
        # transaction(), so a concurrent writer could interleave between the
        # read and the eventual put_task().
        with self.ledger.transaction() as unit:
            task = self.ledger.get_task(task_id, unit=unit)
            AssignmentScope(self.ledger).require_record(task, principal, unit=unit)

            # SPEC R13/R14: compared after assignment admission, before the
            # lifecycle check or any mutation.
            assert_version_precondition(
                control="lifecycle", expected_version=expected_version, current_version=task.version
            )

            # Task-status lifecycle guard (raises ValueError on an illegal move).
            assert_task_transition(task.status, target_status)

            before = str(task.status)
            task.status = target_status
            task.version += 1

            self.ledger.put_task(task, unit=unit)
            self._audit(
                principal, "task.transition", task_id, _TRANSITION_CHAIN,
                before, str(task.status), unit=unit,
            )
        return task

    def _audit(self, principal, action, record_id, chain, before, after, *, unit=None) -> None:
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action=action,
                record_type="Task",
                record_id=str(record_id),
                control_chain=chain,
                before_state=before,
                after_state=after,
            ),
            unit=unit,
        )
