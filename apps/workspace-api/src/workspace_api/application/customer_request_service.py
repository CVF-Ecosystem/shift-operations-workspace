"""Customer-request application service — fourth CVF vertical (P2-A), replicating
the chain to a new operational domain.

Reuses the SAME cvf-runtime gates as EventService/CorrectionService/TaskService/
ShiftService: identity, permission, domain_lock, audit are not re-implemented
here. database/migrations/002_tasks_customers_reports.sql's customer_requests
table has no version/risk/state/evidence columns (unlike tasks/
operational_events), so this domain is intentionally NOT risk-classed: no
evidence/approval gate is wired for create, matching the schema exactly.

Two governed actions:
* create_customer_request — identity -> permission -> domain_lock -> persist
                             (frozen-shift check only when shift_id is given,
                             since shift_id is nullable) -> audit
* transition               — identity -> permission -> customer-request-status
                             lifecycle -> persist -> audit
"""

from uuid import UUID

from cvf_runtime.audit import AuditRecord
from cvf_runtime.domain_lock import assert_domain_allowed
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from workspace_api.domain.lifecycle import assert_customer_request_transition
from workspace_api.domain.models import CustomerRequest, CustomerRequestStatus

# No "risk"/"evidence"/"approval" in either chain: customer_requests has no
# risk_class/evidence column in the migration, so those gates do not apply to
# this domain (unlike Task, which is risk-classed).
_CREATE_CHAIN = ["identity", "permission", "domain_lock", "audit"]
_TRANSITION_CHAIN = ["identity", "permission", "audit"]

# Customer requests belong to the customer_request domain (domain-lock.yaml).
_CUSTOMER_REQUEST_DOMAIN = "customer_request"


class CustomerRequestService:
    def __init__(self, ledger: Ledger, profile: CvfProfile | None = None):
        self.ledger = ledger
        self.profile = profile or load_profile()

    def create_customer_request(
        self,
        request: CustomerRequest,
        principal: Principal,
    ) -> CustomerRequest:
        require_action(principal, "customer_request.create")
        assert_domain_allowed(self.profile, _CUSTOMER_REQUEST_DOMAIN)

        # Unit-of-work: customer-request insert + audit append commit or roll
        # back together (P-FIX-2 / High Finding #5 pattern). The frozen-shift
        # check (when shift_id is present) happens inside add_customer_request
        # itself, same as add_task/add_event.
        with self.ledger.transaction() as unit:
            stored = self.ledger.add_customer_request(request, unit=unit)
            self._audit(
                principal, "customer_request.create", stored.request_id, _CREATE_CHAIN,
                None, str(stored.status), unit=unit,
            )
        return stored

    def transition(
        self,
        request_id: UUID,
        principal: Principal,
        target_status: CustomerRequestStatus,
    ) -> CustomerRequest:
        request = self.ledger.get_customer_request(request_id)

        require_action(principal, "customer_request.transition")
        # Customer-request-status lifecycle guard (raises ValueError on an
        # illegal move).
        assert_customer_request_transition(request.status, target_status)

        before = str(request.status)
        request.status = target_status

        with self.ledger.transaction() as unit:
            self.ledger.put_customer_request(request, unit=unit)
            self._audit(
                principal, "customer_request.transition", request_id, _TRANSITION_CHAIN,
                before, str(request.status), unit=unit,
            )
        return request

    def _audit(self, principal, action, record_id, chain, before, after, *, unit=None) -> None:
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action=action,
                record_type="CustomerRequest",
                record_id=str(record_id),
                control_chain=chain,
                before_state=before,
                after_state=after,
            ),
            unit=unit,
        )
