"""P4-E deterministic placement service (SPEC section 6, R13-R16).

``ConversationRoutingService`` performs the ordered evaluation from SPEC
R15: immutable proposal lineage; exactly one current mapping; current
mapped user; zero/one/multiple bindings; target and assignment eligibility;
decision idempotency. It consumes only ``IdentityMappingReadPort`` (never
mutates a mapping) plus its own binding/eligibility ports.
"""

from __future__ import annotations

from uuid import uuid4

from identity_mapping.ports import IdentityMappingReadPort

from .invariants import emit_placement_decision
from .models import PlacementDecisionReceipt, conversation_key
from .ports import RouteBindingRepositoryPort, TargetEligibilityPort


def _fallback(proposal_id: str, reason: str) -> PlacementDecisionReceipt:
    return emit_placement_decision(
        "FALLBACK", reason=reason, decision_id=str(uuid4()), proposal_id=proposal_id,
        decision_count=1, work_complete=True,
    )


def _refused(proposal_id: str, reason: str) -> PlacementDecisionReceipt:
    return emit_placement_decision(
        "REFUSED", reason=reason, decision_id=str(uuid4()), proposal_id=proposal_id,
        decision_count=1, work_complete=True,
    )


def _retry_pending(proposal_id: str, reason: str) -> PlacementDecisionReceipt:
    return emit_placement_decision(
        "RETRY_PENDING", reason=reason, proposal_id=proposal_id,
        decision_count=0, work_complete=False,
    )


class ConversationRoutingService:
    def __init__(
        self,
        identity_read_port: IdentityMappingReadPort,
        binding_repository: RouteBindingRepositoryPort,
        target_eligibility: TargetEligibilityPort,
        *,
        legacy_sender_evidence: bool = False,
    ) -> None:
        self._identity = identity_read_port
        self._bindings = binding_repository
        self._targets = target_eligibility
        self._legacy_sender_evidence = legacy_sender_evidence

    def place(
        self, *, proposal_id: str, external_key_digest: str | None, unit: object = None
    ) -> PlacementDecisionReceipt:
        """SPEC R15 ordered evaluation. ``external_key_digest`` is ``None``
        when the admitted proposal carries no sender evidence at all
        (legacy ingress or a missing assertion) - both reach fallback
        without a mapping lookup (SPEC AC-02)."""
        if external_key_digest is None:
            reason = "LEGACY_SENDER_EVIDENCE" if self._legacy_sender_evidence else "NO_SENDER_EVIDENCE"
            return _fallback(proposal_id, reason)

        try:
            mapping = self._identity.get_current_mapping(external_key_digest, unit=unit)
        except ValueError:
            return _refused(proposal_id, "MULTIPLE_CURRENT_MAPPINGS")
        if mapping is None:
            return _fallback(proposal_id, "NO_MAPPING")
        if mapping.status == "REJECTED":
            return _fallback(proposal_id, "MAPPING_REJECTED")
        if mapping.status == "REVOKED":
            return _fallback(proposal_id, "MAPPING_REVOKED")
        if mapping.status != "CONFIRMED":
            return _refused(proposal_id, "CORRUPT_STATE")

        try:
            binding = self._bindings.get_current_binding(mapping.mapping_id, unit=unit)
        except ValueError:
            return _refused(proposal_id, "MULTIPLE_CURRENT_BINDINGS")
        if binding is None:
            return _fallback(proposal_id, "NO_BINDING")
        if binding.status != "ACTIVE":
            return _refused(proposal_id, "STALE_BINDING_VERSION")

        eligible, target_version, assignment_shift_id, extra = self._check_target(binding)
        if eligible is None:
            return _refused(proposal_id, "TARGET_STATE_AMBIGUOUS")
        if not eligible:
            if extra == "UNSUPPORTED_TARGET":
                return _fallback(proposal_id, "UNSUPPORTED_TARGET")
            return _refused(proposal_id, "ASSIGNMENT_INELIGIBLE")
        if target_version != binding.target_version:
            return _refused(proposal_id, "STALE_BINDING_VERSION")
        # SPEC R14/completion-review F5: reread BOTH the mapped user and the
        # binding actor at route time, checked against the target shift -
        # for INCIDENT that is the resolved PARENT shift id
        # (``assignment_shift_id``), never the incident id itself.
        if binding.target_kind != "WORKSPACE":
            if not self._targets.user_assignment_eligible(mapping.target_user_id, assignment_shift_id):
                return _fallback(proposal_id, "TARGET_USER_INACTIVE")
            if not self._targets.user_assignment_eligible(binding.creator_id, assignment_shift_id):
                return _refused(proposal_id, "ASSIGNMENT_INELIGIBLE")

        key = conversation_key(
            mapping_id=mapping.mapping_id, mapping_version=mapping.version,
            binding_id=binding.binding_id, binding_version=binding.version,
            target_kind=binding.target_kind, target_id=binding.target_id,
            target_version=binding.target_version,
            workspace_digest=self._targets.workspace_digest(),
        )
        return emit_placement_decision(
            "PLACED", decision_id=str(uuid4()), proposal_id=proposal_id,
            mapping_id=mapping.mapping_id, binding_id=binding.binding_id,
            target_kind=binding.target_kind, target_id=binding.target_id,
            conversation_key=key, decision_count=1, work_complete=True,
        )

    def _check_target(self, binding) -> tuple[bool | None, int, str | None, str | None]:
        """SPEC R14: WORKSPACE requires exact equality with the injected
        workspace digest; SHIFT requires a non-closed, non-frozen shift;
        INCIDENT requires a non-closed incident with an eligible parent
        shift. Returns (eligible, target_version, assignment_shift_id,
        extra) - ``assignment_shift_id`` is the shift both actors' active
        assignments must be checked against: the shift itself for SHIFT,
        the resolved PARENT shift (never the incident id) for INCIDENT,
        and ``None`` for WORKSPACE (no per-shift assignment requirement)."""
        if binding.target_kind == "WORKSPACE":
            eligible = binding.target_id == self._targets.workspace_digest()
            return eligible, binding.target_version, None, None
        if binding.target_kind == "SHIFT":
            eligible, version = self._targets.shift_eligible(binding.target_id)
            return eligible, version, binding.target_id, None
        if binding.target_kind == "INCIDENT":
            eligible, version, parent_shift_id = self._targets.incident_eligible(binding.target_id)
            if eligible and parent_shift_id is not None:
                parent_eligible, _parent_version = self._targets.shift_eligible(parent_shift_id)
                eligible = eligible and parent_eligible
            return eligible, version, parent_shift_id, None
        return False, 0, None, "UNSUPPORTED_TARGET"
