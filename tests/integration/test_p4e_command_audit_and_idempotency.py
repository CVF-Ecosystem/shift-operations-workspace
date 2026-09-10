"""P4-E human-command application-service coverage (completion-rereview
R2): durable actor-bound audit on bind/replace, audit-failure rollback,
receipt-failure rollback, changed-actor/version/target replay conflicts,
R17 read permission and fresh-authority demotion, and no sensitive-field
disclosure. Exercises the REAL P4ePlacementCommandService/
P4eMappingCommandService application layer against InMemoryLedger, not
only the lower ledger/identity_mapping-package layers generation 1 tested."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from cvf_runtime.identity import Principal
from identity_mapping.models import IdentityMappingV1

from workspace_api.application.p4e_commands import P4eMappingCommandService
from workspace_api.application.p4e_placement import P4ePlacementCommandService
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.domain.models import User

_DIGEST64 = "a" * 64
_NOW = datetime.now(timezone.utc)


def _ledger_with_users(**roles) -> InMemoryLedger:
    ledger = InMemoryLedger()
    for user_id, role in roles.items():
        ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))
    return ledger


def _confirmed_mapping(ledger, *, mapping_id="m1", target_user_id="target1",
                        proposer_id="sup1", confirmer_id="sup2", key_digest=_DIGEST64):
    ledger.propose_mapping(IdentityMappingV1(
        mapping_id=mapping_id, external_key_digest=key_digest, target_user_id=target_user_id,
        proposal_evidence_digest="b" * 64, proposer_id=proposer_id, status="PROPOSED",
        version=1, created_at=_NOW, updated_at=_NOW,
    ))
    return ledger.confirm_mapping(mapping_id, expected_version=1, confirmer_id=confirmer_id)


def _bind_workspace(ledger, *, actor_id, mapping_version, idempotency_key="idem-bind"):
    service = P4ePlacementCommandService(ledger, _DIGEST64)
    return service, service.bind(
        Principal(user_id=actor_id, role="shift_supervisor"), mapping_id="m1",
        expected_mapping_version=mapping_version, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key=idempotency_key,
    )


def test_bind_persists_a_real_durable_audit_row():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    _service, receipt = _bind_workspace(ledger, actor_id="sup2", mapping_version=2)
    assert receipt.outcome == "APPLIED"
    entries = ledger.audit_entries_for(receipt.aggregate_id)
    assert len(entries) == 1
    assert entries[0].actor_id == "sup2"
    assert entries[0].action == "BIND"


def test_replace_binding_persists_a_real_durable_audit_row():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    service, bind_receipt = _bind_workspace(ledger, actor_id="sup2", mapping_version=2)
    replace_receipt = service.replace_binding(
        Principal(user_id="sup2", role="shift_supervisor"), old_binding_id=bind_receipt.aggregate_id,
        expected_binding_version=1, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key="idem-replace",
    )
    assert replace_receipt.outcome == "APPLIED"
    entries = ledger.audit_entries_for(replace_receipt.aggregate_id)
    assert len(entries) == 1
    assert entries[0].action == "REPLACE_BINDING"


def test_bind_audit_failure_rolls_back_the_binding_mutation():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    service = P4ePlacementCommandService(ledger, _DIGEST64)

    def _boom(*args, **kwargs):
        raise RuntimeError("audit sink unavailable")

    ledger.append_audit = _boom
    with pytest.raises(RuntimeError):
        service.bind(
            Principal(user_id="sup2", role="shift_supervisor"), mapping_id="m1",
            expected_mapping_version=2, target_kind="WORKSPACE", target_id=_DIGEST64,
            idempotency_key="idem-fail",
        )
    assert ledger.get_current_binding("m1") is None


def test_bind_receipt_persistence_failure_rolls_back_binding_and_audit():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    service = P4ePlacementCommandService(ledger, _DIGEST64)

    def _boom(*args, **kwargs):
        raise RuntimeError("receipt sink unavailable")

    ledger.put_action_receipt = _boom
    with pytest.raises(RuntimeError):
        service.bind(
            Principal(user_id="sup2", role="shift_supervisor"), mapping_id="m1",
            expected_mapping_version=2, target_kind="WORKSPACE", target_id=_DIGEST64,
            idempotency_key="idem-fail2",
        )
    assert ledger.get_current_binding("m1") is None
    assert ledger.audit_entries_for("m1") == []


def test_changed_actor_under_same_idempotency_key_is_a_closed_conflict_not_a_replay():
    ledger = _ledger_with_users(
        target1="operator", sup1="shift_supervisor", sup2="shift_supervisor", sup3="shift_supervisor",
    )
    _confirmed_mapping(ledger)
    service, first = _bind_workspace(ledger, actor_id="sup2", mapping_version=2, idempotency_key="idem-actor")
    assert first.outcome == "APPLIED"
    second = service.bind(
        Principal(user_id="sup3", role="shift_supervisor"), mapping_id="m1",
        expected_mapping_version=2, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key="idem-actor",
    )
    assert second.outcome == "CONFLICT"


def test_changed_expected_version_under_same_idempotency_key_is_a_closed_conflict():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    service, first = _bind_workspace(ledger, actor_id="sup2", mapping_version=2, idempotency_key="idem-version")
    assert first.outcome == "APPLIED"
    second = service.bind(
        Principal(user_id="sup2", role="shift_supervisor"), mapping_id="m1",
        expected_mapping_version=99, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key="idem-version",
    )
    assert second.outcome == "CONFLICT"


def test_changed_target_under_same_idempotency_key_is_a_closed_conflict():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    service, first = _bind_workspace(ledger, actor_id="sup2", mapping_version=2, idempotency_key="idem-target")
    assert first.outcome == "APPLIED"
    second = service.bind(
        Principal(user_id="sup2", role="shift_supervisor"), mapping_id="m1",
        expected_mapping_version=2, target_kind="WORKSPACE", target_id="b" * 64,
        idempotency_key="idem-target",
    )
    assert second.outcome == "CONFLICT"


def test_exact_replay_same_key_and_dimensions_returns_prior_receipt():
    ledger = _ledger_with_users(target1="operator", sup1="shift_supervisor", sup2="shift_supervisor")
    _confirmed_mapping(ledger)
    service, first = _bind_workspace(ledger, actor_id="sup2", mapping_version=2, idempotency_key="idem-replay")
    assert first.outcome == "APPLIED"
    second = service.bind(
        Principal(user_id="sup2", role="shift_supervisor"), mapping_id="m1",
        expected_mapping_version=2, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key="idem-replay",
    )
    assert second.outcome == "IDEMPOTENT_REPLAY"
    assert second.aggregate_id == first.aggregate_id
    assert len(ledger.audit_entries_for(first.aggregate_id)) == 1


def _real_observation_and_key_port():
    """Real observation + key port at the application layer (mirrors
    ``tests/unit/test_p4e_identity_service.py``'s ``_observation_and_key``)
    - completion-rereview2 F3's propose regressions need an actually
    resolvable key, unlike ``_NullKeyPort``."""
    from identity_mapping.crypto import derive_sender_token, normalize_sender_bytes
    from identity_mapping.models import ExternalIdentityKeyV1
    from identity_mapping import SenderObservationV1

    key_id, key_version, secret = "k1", "1", b"0" * 32
    raw_sender = "+84901234567"
    normalized = normalize_sender_bytes(raw_sender)
    token = derive_sender_token(
        key_id=key_id, key_secret=secret, workspace_digest=_DIGEST64, endpoint_id="ep1",
        channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="observation", verification_version="1", normalized_sender_bytes=normalized,
    )
    key = ExternalIdentityKeyV1(
        workspace_digest=_DIGEST64, endpoint_id="ep1", channel_id="ch1",
        provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="observation", verification_version="1",
        sender_token=token, token_key_id=key_id, token_key_version=key_version,
    )
    observation = SenderObservationV1(
        observation_id="obs1", external_key_digest=key.digest(), workspace_digest=_DIGEST64,
        endpoint_id="ep1", channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        raw_envelope_id="env1", external_message_id="msg1", received_at=_NOW,
    )

    class _RealKeyPort:
        def active_key(self):
            return key_id, key_version, secret

        def resolve_key(self, k_id, k_version):
            return secret if (k_id, k_version) == (key_id, key_version) else None

    return observation, raw_sender, key_id, key_version, _RealKeyPort()


def test_propose_applies_with_expected_version_one_at_the_application_layer():
    ledger = _ledger_with_users(sup1="shift_supervisor", target1="operator")
    observation, raw_sender, key_id, key_version, key_port = _real_observation_and_key_port()
    ledger.add_observation(observation)
    commands = P4eMappingCommandService(ledger, key_port=key_port)

    receipt = commands.propose(
        Principal(user_id="sup1", role="shift_supervisor"), observation_id="obs1",
        expected_version=1, target_user_id="target1", raw_sender=raw_sender,
        key_id=key_id, key_version=key_version, idempotency_key="idem-propose",
    )
    assert receipt.outcome == "APPLIED"


def test_propose_rejects_a_wrong_expected_version_at_the_application_layer():
    ledger = _ledger_with_users(sup1="shift_supervisor", target1="operator")
    observation, raw_sender, key_id, key_version, key_port = _real_observation_and_key_port()
    ledger.add_observation(observation)
    commands = P4eMappingCommandService(ledger, key_port=key_port)

    receipt = commands.propose(
        Principal(user_id="sup1", role="shift_supervisor"), observation_id="obs1",
        expected_version=2, target_user_id="target1", raw_sender=raw_sender,
        key_id=key_id, key_version=key_version, idempotency_key="idem-propose-bad",
    )
    assert receipt.outcome == "CONFLICT"
    assert receipt.reason == "VERSION_CONFLICT"


def test_list_observations_requires_permission_and_returns_no_sensitive_field():
    ledger = _ledger_with_users(op1="operator")
    commands = P4eMappingCommandService(ledger, key_port=_NullKeyPort())
    from operations_ledger.p4e_records import observation_from_sender_evidence
    from identity_mapping import SenderObservationV1

    sender_evidence = {
        "workspace_digest": _DIGEST64, "endpoint_id": "ep1", "channel_id": "ch1",
        "provider_account_digest": _DIGEST64, "subject_kind": "phone",
        "extraction_policy_id": "pol1", "extraction_policy_version": "1",
        "verification_scheme": "hmac", "verification_version": "1",
        "sender_token": _DIGEST64, "token_key_id": "k1", "token_key_version": "1",
        "raw_envelope_id": "env1", "external_message_id": "msg1", "received_at": _NOW.isoformat(),
    }
    row = observation_from_sender_evidence("obs1", sender_evidence)
    ledger.add_observation(SenderObservationV1(**row))

    observations = commands.list_observations(Principal(user_id="op1", role="operator"))
    assert len(observations) == 1
    dumped = observations[0].model_dump(mode="json")
    for forbidden in ("sender_token", "raw_sender"):
        assert forbidden not in dumped


def test_list_observations_denies_a_role_without_the_read_permission():
    """SPEC R17: external_identity_mapping.read is gated by fresh-role
    lookup - a real user whose current stored role lacks the permission
    (never the caller-claimed JWT role) must be denied."""
    from cvf_runtime.errors import CvfDenied

    ledger = _ledger_with_users(bystander="viewer")
    commands = P4eMappingCommandService(ledger, key_port=_NullKeyPort())
    with pytest.raises(CvfDenied):
        commands.list_observations(Principal(user_id="bystander", role="operator"))


def test_list_observations_denies_an_inactive_actor():
    from workspace_api.application.p4e_commands import _NoSuchActor

    ledger = _ledger_with_users(op1="operator")
    user = ledger.get_user_by_id("op1")
    user.is_active = False
    ledger.users["op1"] = user
    commands = P4eMappingCommandService(ledger, key_port=_NullKeyPort())
    with pytest.raises(_NoSuchActor):
        commands.list_observations(Principal(user_id="op1", role="operator"))


class _NullKeyPort:
    def resolve_key(self, key_id, key_version):
        return None

    def active_key(self):
        raise ValueError("no key")
