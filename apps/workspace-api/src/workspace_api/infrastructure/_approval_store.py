"""In-memory approval-receipt / task-creation-intent storage mixin.

Split out of ``repository.py`` (CVF-FILE-SPLIT-GUARD-HARDENING) to keep the
module under the hard line limit. ``_ApprovalStoreMixin`` expects
``self._lock``, ``self.approval_receipts`` and ``self.task_creation_intents``
to already exist (set up by ``InMemoryLedger.__init__``); it owns no state of
its own and is not a second, independent implementation of these lookups -
``InMemoryLedger`` inherits it directly so every public method keeps its exact
prior name, signature and behavior.
"""

from __future__ import annotations

from uuid import UUID

from operations_domain.models import ApprovalReceipt, TaskCreationIntent


class _ApprovalStoreMixin:
    def add_approval_receipt(self, receipt: ApprovalReceipt, *, unit=None) -> ApprovalReceipt:
        with self._lock:
            existing = self.get_approval_receipt(
                record_type=receipt.record_type,
                record_id=receipt.record_id,
                action=receipt.action,
                target_version=receipt.target_version,
                approver_id=receipt.approver_id,
                unit=unit,
            )
            if existing is not None:
                return existing.model_copy()
            stored = receipt.model_copy()
            self.approval_receipts[receipt.receipt_id] = stored
            return stored.model_copy()

    def list_approval_receipts_for(
        self,
        *,
        record_type: str,
        record_id,
        action: str,
        target_version: int,
        risk_class: str | None,
        payload_digest: str | None,
        unit=None,
    ) -> list[ApprovalReceipt]:
        with self._lock:
            return [
                r.model_copy()
                for r in self.approval_receipts.values()
                if (
                    r.record_type == record_type
                    and r.record_id == record_id
                    and r.action == action
                    and r.target_version == target_version
                    and r.risk_class == risk_class
                    and r.payload_digest == payload_digest
                )
            ]

    def get_approval_receipt(
        self,
        *,
        record_type: str,
        record_id,
        action: str,
        target_version: int,
        approver_id: str,
        unit=None,
    ) -> ApprovalReceipt | None:
        with self._lock:
            for r in self.approval_receipts.values():
                if (
                    r.record_type == record_type
                    and r.record_id == record_id
                    and r.action == action
                    and r.target_version == target_version
                    and r.approver_id == approver_id
                ):
                    return r.model_copy()
        return None

    def add_task_creation_intent(
        self, intent: TaskCreationIntent, *, unit=None
    ) -> TaskCreationIntent:
        with self._lock:
            stored = intent.model_copy()
            self.task_creation_intents[intent.intent_id] = stored
            return stored.model_copy()

    def get_task_creation_intent(self, intent_id: UUID, *, unit=None) -> TaskCreationIntent:
        with self._lock:
            return self.task_creation_intents[intent_id].model_copy()
