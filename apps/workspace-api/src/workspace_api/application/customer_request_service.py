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
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_customer_request_transition
from operations_domain.models import CustomerRequest, CustomerRequestStatus
from workspace_api.application.assignment_scope import AssignmentScope, require_active_assignment
from workspace_api.application.mutation_preconditions import assert_version_precondition

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
        if request.shift_id is not None:
            require_active_assignment(self.ledger, request.shift_id, principal)

        # Independent review, 2026-07-22 (Finding 2): source_message_id has a
        # real FK to messages in the migration. Message persistence is now
        # implemented on both backends (MESSAGE-ADMISSION-TRUST-REPAIR-
        # 2026-07-30), but a caller can still reference a message_id that was
        # never created, so InMemoryLedger and SqlLedger/SQLite would
        # otherwise diverge (no check vs. an uncaught IntegrityError from the
        # FK, surfacing as an HTTP 500). Validate existence up front, before
        # either backend ever attempts the insert, so both raise the SAME
        # controlled error.
        if request.source_message_id is not None and not self.ledger.message_exists(
            request.source_message_id
        ):
            raise CvfDenied(
                control="reference",
                reason=f"source_message_id {request.source_message_id} does not reference an existing message",
                http_status=404,
            )

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
        *,
        expected_version: int | None = None,
    ) -> CustomerRequest:
        require_action(principal, "customer_request.transition")
        # C3B2-WO-REV-F2: stored-target read, assignment admission,
        # precondition compare, lifecycle check and the atomic CAS mutation
        # all now share ONE transaction.
        with self.ledger.transaction() as unit:
            request = self.ledger.get_customer_request(request_id, unit=unit)
            if request.shift_id is not None:
                AssignmentScope(self.ledger).require_record(request, principal, unit=unit)

            # SPEC R12/R13/R14: a missing expected_version is 422 here (never
            # reaches the CAS write below); a present-but-stale value is
            # instead left to the atomic CAS write's own rowcount check so
            # the compare happens against the freshest possible row.
            assert_version_precondition(
                control="lifecycle", expected_version=expected_version, current_version=request.version
            )

            # Customer-request-status lifecycle guard (raises ValueError on
            # an illegal move) - checked against current status before the
            # atomic compare-and-swap write.
            assert_customer_request_transition(request.status, target_status)

            before = str(request.status)
            updated = self.ledger.transition_customer_request(
                request_id, expected_version=expected_version, target_status=target_status, unit=unit
            )
            self._audit(
                principal, "customer_request.transition", request_id, _TRANSITION_CHAIN,
                before, str(updated.status), unit=unit,
            )
        return updated

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
