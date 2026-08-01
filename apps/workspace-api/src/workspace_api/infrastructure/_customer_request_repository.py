"""In-memory customer-request storage mixin (P2C-MUTATION-FULL-UI-C3B2, SPEC
R12).

Split out of ``repository.py`` (same pattern as ``_assignment_repository.py``)
to keep that host module a thin wiring surface. ``_CustomerRequestRepositoryMixin``
expects ``self._lock``, ``self.customer_requests`` and
``self._assert_shift_not_frozen`` to already exist (set up by
``InMemoryLedger.__init__``); it owns no state of its own.

``add_customer_request``/``get_customer_request``/``put_customer_request``
moved here intact from ``repository.py`` (Work Order section 3.1) - no
behavior change, only relocation - alongside the new
``transition_customer_request`` compare-and-swap this tranche adds, mirroring
``_AssignmentRepositoryMixin.revoke_assignment``'s CAS shape: the version
comparison and the write happen under the SAME lock acquisition, so no
concurrent caller can observe or act on a torn intermediate state.
"""

from __future__ import annotations

from uuid import UUID

from operations_domain.models import CustomerRequest


class _CustomerRequestRepositoryMixin:
    def add_customer_request(self, request: CustomerRequest, *, unit=None) -> CustomerRequest:
        # shift_id is nullable on CustomerRequest (unlike Task.shift_id): a
        # request not tied to any shift has no frozen-shift invariant to
        # check, so only guard when a shift_id is actually present.
        if request.shift_id is not None:
            self._assert_shift_not_frozen(
                request.shift_id, "add customer request to a frozen shift"
            )
        # Store and return COPIES, not the caller's live object — see
        # InMemoryLedger.get_shift() for why.
        stored = request.model_copy()
        self.customer_requests[request.request_id] = stored
        return stored.model_copy()

    def get_customer_request(self, request_id: UUID, *, unit=None) -> CustomerRequest:
        # Copy, not the live reference — see InMemoryLedger.get_shift().
        return self.customer_requests[request_id].model_copy()

    def put_customer_request(self, request: CustomerRequest, *, unit=None) -> CustomerRequest:
        if request.shift_id is not None:
            self._assert_shift_not_frozen(
                request.shift_id, "modify customer request in a frozen shift"
            )
        stored = request.model_copy()
        self.customer_requests[request.request_id] = stored
        return stored.model_copy()

    def transition_customer_request(
        self, request_id: UUID, *, expected_version: int, target_status, unit=None
    ) -> CustomerRequest:
        """P2C-MUTATION-FULL-UI-C3B2 (SPEC R12/R14): atomic compare-and-swap
        under ``self._lock`` - a stale ``expected_version`` raises a
        controlled ``ValueError`` with zero write, mirroring
        ``_AssignmentRepositoryMixin.revoke_assignment``."""
        with self._lock:
            if request_id not in self.customer_requests:
                raise KeyError(request_id)
            current = self.customer_requests[request_id]
            if current.shift_id is not None:
                self._assert_shift_not_frozen(
                    current.shift_id, "modify customer request in a frozen shift"
                )
            if current.version != expected_version:
                raise ValueError(
                    f"stale customer_request version: expected {expected_version}, "
                    f"found {current.version}"
                )
            updated = current.model_copy()
            updated.status = target_status
            updated.version = current.version + 1
            self.customer_requests[request_id] = updated
            return updated.model_copy()
