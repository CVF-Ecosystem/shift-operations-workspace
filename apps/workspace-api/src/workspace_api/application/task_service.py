"""Task application service — third CVF vertical, replicating the chain.

Reuses the SAME cvf-runtime gates as EventService/CorrectionService: it does not
re-implement identity, permission, domain_lock, risk, approval, evidence or
audit. That reuse is the whole point of the golden vertical — a new operational
domain wires the existing chain rather than forking it.

Two governed actions:
* create_task  — identity -> permission -> domain_lock -> (risk+evidence+approval
                 when the task is R2+) -> persist -> audit
* transition   — identity -> permission -> task-status lifecycle -> persist -> audit
"""

from uuid import UUID

from cvf_runtime.approval import Approval, assert_approval_satisfied
from cvf_runtime.audit import AuditRecord
from cvf_runtime.domain_lock import assert_domain_allowed
from cvf_runtime.evidence import assert_evidence_sufficient
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from workspace_api.domain.lifecycle import assert_task_transition
from workspace_api.domain.models import Task, TaskStatus

_CREATE_CHAIN = ["identity", "permission", "domain_lock", "risk", "evidence", "approval", "audit"]
_TRANSITION_CHAIN = ["identity", "permission", "freeze", "audit"]

# Tasks belong to the shift-operation domain (domain-lock.yaml).
_TASK_DOMAIN = "shift_operation"


class TaskService:
    def __init__(self, ledger: Ledger, profile: CvfProfile | None = None):
        self.ledger = ledger
        self.profile = profile or load_profile()

    def create_task(
        self,
        task: Task,
        principal: Principal,
        approvals: list[Approval],
    ) -> Task:
        risk_class = str(task.risk_class)

        require_action(principal, "task.create")
        assert_domain_allowed(self.profile, _TASK_DOMAIN)

        # A higher-risk task (R2+) is an operational commitment: it must carry
        # evidence and the approval quorum for its risk class, exactly like an
        # event confirmation.
        assert_evidence_sufficient(
            profile=self.profile,
            risk_class=risk_class,
            evidence_count=len(task.evidence),
        )
        assert_approval_satisfied(
            profile=self.profile,
            risk_class=risk_class,
            confirmer=principal,
            approvals=approvals,
        )

        stored = self.ledger.add_task(task)
        self._audit(principal, "task.create", stored.task_id, _CREATE_CHAIN, None, str(stored.status))
        return stored

    def transition(
        self,
        task_id: UUID,
        principal: Principal,
        target_status: TaskStatus,
    ) -> Task:
        task = self.ledger.get_task(task_id)

        require_action(principal, "task.transition")
        # Task-status lifecycle guard (raises ValueError on an illegal move).
        assert_task_transition(task.status, target_status)

        before = str(task.status)
        task.status = target_status
        task.version += 1
        self.ledger.put_task(task)

        self._audit(principal, "task.transition", task_id, _TRANSITION_CHAIN, before, str(task.status))
        return task

    def _audit(self, principal, action, record_id, chain, before, after) -> None:
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
            )
        )
