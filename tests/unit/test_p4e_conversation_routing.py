"""P4-E ConversationRoutingService unit tests (SPEC R14-R16, AC-08, AC-09):
WORKSPACE/SHIFT/INCIDENT positive placement, fallback/refusal/unsupported
cases, and conversation-key determinism/mutation sensitivity - against fake
ports, no SQL backend."""

from __future__ import annotations

from datetime import datetime, timezone

from conversation_routing.models import RouteBindingV1, conversation_key
from conversation_routing.service import ConversationRoutingService
from identity_mapping.models import IdentityMappingV1

_DIGEST64 = "a" * 64
_NOW = datetime.now(timezone.utc)


class _FakeIdentityPort:
    def __init__(self, mapping=None, raise_multiple=False):
        self._mapping = mapping
        self._raise_multiple = raise_multiple

    def get_current_mapping(self, external_key_digest, *, unit=None):
        if self._raise_multiple:
            raise ValueError("multiple")
        return self._mapping


class _FakeBindingPort:
    def __init__(self, binding=None, raise_multiple=False):
        self._binding = binding
        self._raise_multiple = raise_multiple

    def get_current_binding(self, mapping_id, *, unit=None):
        if self._raise_multiple:
            raise ValueError("multiple")
        return self._binding


class _FakeEligibility:
    def __init__(self, *, workspace_digest=_DIGEST64, shift_ok=True, incident_ok=True,
                 parent_shift_id="shift1", assignment_ok=True):
        self._workspace_digest = workspace_digest
        self._shift_ok = shift_ok
        self._incident_ok = incident_ok
        self._parent_shift_id = parent_shift_id
        self._assignment_ok = assignment_ok

    def workspace_digest(self):
        return self._workspace_digest

    def shift_eligible(self, shift_id):
        return self._shift_ok, 1

    def incident_eligible(self, incident_id):
        return self._incident_ok, 1, self._parent_shift_id

    def user_assignment_eligible(self, user_id, shift_id):
        return self._assignment_ok


def _confirmed_mapping(**overrides):
    fields = dict(
        mapping_id="m1", external_key_digest=_DIGEST64, target_user_id="u1",
        proposal_evidence_digest=_DIGEST64, proposer_id="u2", status="CONFIRMED",
        version=1, created_at=_NOW, updated_at=_NOW,
    )
    fields.update(overrides)
    return IdentityMappingV1(**fields)


def _binding(**overrides):
    fields = dict(
        binding_id="b1", mapping_id="m1", mapping_version=1, target_kind="WORKSPACE",
        target_id=_DIGEST64, target_version=1, creator_id="u2", status="ACTIVE",
        version=1, created_at=_NOW,
    )
    fields.update(overrides)
    return RouteBindingV1(**fields)


def test_fallback_when_no_sender_evidence():
    service = ConversationRoutingService(_FakeIdentityPort(), _FakeBindingPort(), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=None)
    assert result.outcome == "FALLBACK"
    assert result.reason == "NO_SENDER_EVIDENCE"
    assert result.conversation_key is None


def test_fallback_legacy_sender_evidence_flag():
    service = ConversationRoutingService(
        _FakeIdentityPort(), _FakeBindingPort(), _FakeEligibility(), legacy_sender_evidence=True,
    )
    result = service.place(proposal_id="p1", external_key_digest=None)
    assert result.reason == "LEGACY_SENDER_EVIDENCE"


def test_fallback_no_mapping():
    service = ConversationRoutingService(_FakeIdentityPort(mapping=None), _FakeBindingPort(), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome == "FALLBACK"
    assert result.reason == "NO_MAPPING"


def test_refused_multiple_current_mappings():
    service = ConversationRoutingService(
        _FakeIdentityPort(raise_multiple=True), _FakeBindingPort(), _FakeEligibility(),
    )
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome == "REFUSED"
    assert result.reason == "MULTIPLE_CURRENT_MAPPINGS"


def test_fallback_rejected_mapping():
    mapping = _confirmed_mapping(status="REJECTED")
    service = ConversationRoutingService(_FakeIdentityPort(mapping), _FakeBindingPort(), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.reason == "MAPPING_REJECTED"


def test_fallback_revoked_mapping():
    mapping = _confirmed_mapping(status="REVOKED")
    service = ConversationRoutingService(_FakeIdentityPort(mapping), _FakeBindingPort(), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.reason == "MAPPING_REVOKED"


def test_fallback_no_binding():
    mapping = _confirmed_mapping()
    service = ConversationRoutingService(_FakeIdentityPort(mapping), _FakeBindingPort(binding=None), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.reason == "NO_BINDING"


def test_placed_workspace_target():
    mapping = _confirmed_mapping()
    binding = _binding(target_kind="WORKSPACE", target_id=_DIGEST64)
    service = ConversationRoutingService(
        _FakeIdentityPort(mapping), _FakeBindingPort(binding), _FakeEligibility(workspace_digest=_DIGEST64),
    )
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome == "PLACED"
    assert result.target_kind == "WORKSPACE"
    assert result.conversation_key is not None
    assert len(result.conversation_key) == 64


def test_placed_shift_target():
    mapping = _confirmed_mapping()
    binding = _binding(target_kind="SHIFT", target_id="shift1")
    service = ConversationRoutingService(_FakeIdentityPort(mapping), _FakeBindingPort(binding), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome == "PLACED"
    assert result.target_kind == "SHIFT"


def test_placed_incident_target():
    mapping = _confirmed_mapping()
    binding = _binding(target_kind="INCIDENT", target_id="incident1")
    service = ConversationRoutingService(_FakeIdentityPort(mapping), _FakeBindingPort(binding), _FakeEligibility())
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome == "PLACED"
    assert result.target_kind == "INCIDENT"


def test_fallback_unsupported_target_kind_never_reaches_placed():
    """SPEC section 1: CUSTOMER/VESSEL are unsupported and must reach a
    closed unsupported-target outcome, never PLACED."""
    mapping = _confirmed_mapping()

    class _CustomBinding:
        binding_id, mapping_id, mapping_version = "b1", "m1", 1
        target_kind, target_id, target_version = "CUSTOMER", "cust1", 1
        creator_id, status, version, created_at, successor_binding_id = "u2", "ACTIVE", 1, _NOW, None

    class _FakeBindingWithCustom:
        def get_current_binding(self, mapping_id, *, unit=None):
            return _CustomBinding()

    service = ConversationRoutingService(
        _FakeIdentityPort(mapping), _FakeBindingWithCustom(), _FakeEligibility(),
    )
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome != "PLACED"
    assert result.target_kind is None


def test_shift_ineligible_when_shift_not_open():
    mapping = _confirmed_mapping()
    binding = _binding(target_kind="SHIFT", target_id="shift1")
    service = ConversationRoutingService(
        _FakeIdentityPort(mapping), _FakeBindingPort(binding), _FakeEligibility(shift_ok=False),
    )
    result = service.place(proposal_id="p1", external_key_digest=_DIGEST64)
    assert result.outcome != "PLACED"


def test_conversation_key_deterministic_for_same_tuple():
    key_a = conversation_key(
        mapping_id="m1", mapping_version=1, binding_id="b1", binding_version=1,
        target_kind="WORKSPACE", target_id=_DIGEST64, target_version=1, workspace_digest=_DIGEST64,
    )
    key_b = conversation_key(
        mapping_id="m1", mapping_version=1, binding_id="b1", binding_version=1,
        target_kind="WORKSPACE", target_id=_DIGEST64, target_version=1, workspace_digest=_DIGEST64,
    )
    assert key_a == key_b


def test_conversation_key_changes_on_remap_rebind_revoke_version_change():
    baseline = dict(
        mapping_id="m1", mapping_version=1, binding_id="b1", binding_version=1,
        target_kind="WORKSPACE", target_id=_DIGEST64, target_version=1, workspace_digest=_DIGEST64,
    )
    base_key = conversation_key(**baseline)
    for field, new_value in [
        ("mapping_id", "m2"), ("mapping_version", 2), ("binding_id", "b2"),
        ("binding_version", 2), ("target_id", "b" * 64), ("target_version", 2),
    ]:
        mutated = dict(baseline)
        mutated[field] = new_value
        assert conversation_key(**mutated) != base_key, field
