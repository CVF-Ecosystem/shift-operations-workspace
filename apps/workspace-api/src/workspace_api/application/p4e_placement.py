"""P4-E route binding commands (SPEC R7/R13/R14) plus the automatic
placement two-transaction protocol (SPEC R10-R12/R15/R16).

``LedgerTargetEligibility`` implements ``conversation_routing.ports.
TargetEligibilityPort`` against live Workspace API state - conversation-
routing never queries shift/incident/assignment tables directly (SPEC R18).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from cvf_runtime.audit import AuditRecord
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from conversation_routing import RouteBindingV1
from identity_mapping import MappingActionReceipt
from operations_ledger import Ledger

from workspace_api.application.p4e_commands import _fresh_principal, _idempotent_or_none, _NoSuchActor
from workspace_api.application._p4e_target_eligibility import LedgerTargetEligibility
from workspace_api.application.p4e_placement_processor import P4ePlacementProcessor  # noqa: F401 - re-exported

# completion-rereview R2: same audit-chain/record-type convention
# p4e_commands.py uses for mapping actions, scoped to bindings.
_AUDIT_CHAIN = ["identity", "permission", "cas", "audit"]
_RECORD_TYPE = "P4EBinding"


class P4ePlacementCommandService:
    """SPEC R7/R13: human-authorized bind/replace-binding commands."""

    def __init__(self, ledger: Ledger, workspace_digest: str) -> None:
        self.ledger = ledger
        self.workspace_digest = workspace_digest

    def bind(
        self, principal: Principal, *, mapping_id: str, expected_mapping_version: int,
        target_kind: str, target_id: str, idempotency_key: str,
    ) -> MappingActionReceipt:
        with self.ledger.transaction() as unit:
            try:
                actor = _fresh_principal(self.ledger, principal, unit=unit)
            except _NoSuchActor:
                return self._refused("BIND", "ACTOR_INACTIVE")
            require_action(actor, "conversation_route.bind")

            payload = {
                "action": "BIND", "mapping_id": mapping_id, "expected_mapping_version": expected_mapping_version,
                "target_kind": target_kind, "target_id": target_id, "actor_id": actor.user_id,
            }
            digest, replay = _idempotent_or_none(self.ledger, idempotency_key, payload, unit=unit)
            if replay is not None:
                return replay

            try:
                mapping = self.ledger.get_mapping(mapping_id, unit=unit)
            except KeyError:
                return self._refused("BIND", "IDENTITY_REQUIRED")
            if mapping.status != "CONFIRMED" or mapping.version != expected_mapping_version:
                return self._refused("BIND", "TARGET_INELIGIBLE")

            eligibility = LedgerTargetEligibility(self.ledger, self.workspace_digest, unit=unit)
            eligible, target_version, assignment_shift_id = self._check_target(eligibility, target_kind, target_id)
            if not eligible:
                return self._refused("BIND", "UNSUPPORTED_TARGET")
            if not self._both_actors_eligible(
                eligibility, assignment_shift_id, actor_id=actor.user_id,
                mapped_user_id=mapping.target_user_id, target_kind=target_kind,
            ):
                return self._refused("BIND", "TARGET_INELIGIBLE")

            binding = RouteBindingV1(
                binding_id=str(uuid4()), mapping_id=mapping_id, mapping_version=mapping.version,
                target_kind=target_kind, target_id=target_id, target_version=target_version,
                creator_id=actor.user_id, status="ACTIVE", version=1,
                created_at=datetime.now(timezone.utc),
            )
            try:
                self.ledger.create_binding(binding, unit=unit)
            except ValueError as exc:
                receipt = MappingActionReceipt(
                    outcome="CONFLICT", action="BIND", reason="CURRENT_BINDING_CONFLICT",
                    command_application_count=0, audit_count=0, replayed=False,
                )
                return receipt
            audit_id = str(uuid4())
            self.ledger.append_audit(
                AuditRecord(
                    audit_id=audit_id, actor_id=actor.user_id, actor_role=actor.role,
                    action="BIND", record_type=_RECORD_TYPE, record_id=binding.binding_id,
                    control_chain=_AUDIT_CHAIN, after_state="APPLIED",
                ),
                unit=unit,
            )
            receipt = MappingActionReceipt(
                outcome="APPLIED", action="BIND", aggregate_id=binding.binding_id, aggregate_version=1,
                audit_id=audit_id, command_application_count=1, audit_count=1, replayed=False,
            )
            self.ledger.put_action_receipt(idempotency_key, "BIND", digest, receipt.model_dump(exclude_none=True), unit=unit)
        return receipt

    def replace_binding(
        self, principal: Principal, *, old_binding_id: str, expected_binding_version: int,
        target_kind: str, target_id: str, idempotency_key: str,
    ) -> MappingActionReceipt:
        with self.ledger.transaction() as unit:
            try:
                actor = _fresh_principal(self.ledger, principal, unit=unit)
            except _NoSuchActor:
                return self._refused("REPLACE_BINDING", "ACTOR_INACTIVE")
            require_action(actor, "conversation_route.replace")

            payload = {
                "action": "REPLACE_BINDING", "old_binding_id": old_binding_id,
                "expected_binding_version": expected_binding_version, "target_kind": target_kind,
                "target_id": target_id, "actor_id": actor.user_id,
            }
            digest, replay = _idempotent_or_none(self.ledger, idempotency_key, payload, unit=unit)
            if replay is not None:
                return replay

            try:
                old = self.ledger.get_binding(old_binding_id, unit=unit)
            except KeyError:
                return self._refused("REPLACE_BINDING", "TARGET_INELIGIBLE")
            # SPEC R8/R9/completion-review F4: CAS on the old binding's
            # expected version before any mutation - a stale caller must
            # not silently replace a binding that already moved.
            if old.version != expected_binding_version or old.status != "ACTIVE":
                return self._refused("REPLACE_BINDING", "TARGET_INELIGIBLE")
            try:
                old_mapping = self.ledger.get_mapping(old.mapping_id, unit=unit)
            except KeyError:
                return self._refused("REPLACE_BINDING", "IDENTITY_REQUIRED")

            eligibility = LedgerTargetEligibility(self.ledger, self.workspace_digest, unit=unit)
            eligible, target_version, assignment_shift_id = self._check_target(eligibility, target_kind, target_id)
            if not eligible:
                return self._refused("REPLACE_BINDING", "UNSUPPORTED_TARGET")
            if not self._both_actors_eligible(
                eligibility, assignment_shift_id, actor_id=actor.user_id,
                mapped_user_id=old_mapping.target_user_id, target_kind=target_kind,
            ):
                return self._refused("REPLACE_BINDING", "TARGET_INELIGIBLE")

            successor = RouteBindingV1(
                binding_id=str(uuid4()), mapping_id=old.mapping_id, mapping_version=old.mapping_version,
                target_kind=target_kind, target_id=target_id, target_version=target_version,
                creator_id=actor.user_id, status="ACTIVE", version=1,
                created_at=datetime.now(timezone.utc),
            )
            try:
                self.ledger.replace_binding(
                    old_binding_id, successor,
                    expected_binding_version=expected_binding_version, unit=unit,
                )
            except ValueError as exc:
                return MappingActionReceipt(
                    outcome="CONFLICT" if "conflict" in str(exc) else "REFUSED",
                    action="REPLACE_BINDING", reason="CURRENT_BINDING_CONFLICT",
                    command_application_count=0, audit_count=0, replayed=False,
                )
            audit_id = str(uuid4())
            self.ledger.append_audit(
                AuditRecord(
                    audit_id=audit_id, actor_id=actor.user_id, actor_role=actor.role,
                    action="REPLACE_BINDING", record_type=_RECORD_TYPE, record_id=successor.binding_id,
                    control_chain=_AUDIT_CHAIN, after_state="APPLIED",
                ),
                unit=unit,
            )
            receipt = MappingActionReceipt(
                outcome="APPLIED", action="REPLACE_BINDING", aggregate_id=successor.binding_id,
                aggregate_version=1, audit_id=audit_id, command_application_count=1, audit_count=1, replayed=False,
            )
            self.ledger.put_action_receipt(
                idempotency_key, "REPLACE_BINDING", digest, receipt.model_dump(exclude_none=True), unit=unit,
            )
        return receipt

    def _check_target(self, eligibility, target_kind, target_id):
        """Returns (eligible, target_version, assignment_shift_id) - the
        SAME parent-shift resolution ``conversation_routing.service`` uses
        at route time (SPEC R14/completion-review F5): the shift itself for
        SHIFT, the resolved PARENT shift (never the incident id) for
        INCIDENT, ``None`` for WORKSPACE."""
        if target_kind == "WORKSPACE":
            return target_id == eligibility.workspace_digest(), 1, None
        if target_kind == "SHIFT":
            eligible, version = eligibility.shift_eligible(target_id)
            return eligible, version, target_id
        if target_kind == "INCIDENT":
            eligible, version, parent_shift_id = eligibility.incident_eligible(target_id)
            return eligible, version, parent_shift_id
        return False, 0, None

    def _both_actors_eligible(self, eligibility, assignment_shift_id, *, actor_id, mapped_user_id, target_kind):
        """SPEC R14/completion-review F5: at bind/replace time, reread BOTH
        the binding actor and the mapped user, checked against the target
        shift (or incident's parent shift). WORKSPACE has no per-shift
        assignment requirement."""
        if target_kind == "WORKSPACE":
            return True
        return (
            eligibility.user_assignment_eligible(actor_id, assignment_shift_id)
            and eligibility.user_assignment_eligible(mapped_user_id, assignment_shift_id)
        )

    def _refused(self, action: str, reason: str) -> MappingActionReceipt:
        return MappingActionReceipt(
            outcome="REFUSED", action=action, reason=reason,
            command_application_count=0, audit_count=0, replayed=False,
        )
