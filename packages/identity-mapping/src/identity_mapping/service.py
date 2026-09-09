"""P4-E mapping lifecycle service (SPEC section 4, R6-R9).

``IdentityMappingService`` is the provider-neutral orchestrator for propose/
confirm/reject/revoke. It never performs JWT verification, permission, or
HTTP concerns (those are Workspace API's - SPEC R7 steps 1-4 run in
``workspace_api.application`` before this service is invoked); this service
owns the identity-semantic key recomputation, transient re-entry match,
two-human separation, and repository dispatch (R7 steps 5-7 are the
repository's CAS/version responsibility, enforced by raising ``ValueError``
back into ``CONFLICT``).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .crypto import (
    derive_sender_token,
    normalize_sender_bytes,
    proposal_evidence_digest,
)
from .invariants import emit_identity_resolution_result, emit_mapping_action_receipt
from .models import ExternalIdentityKeyV1, IdentityMappingV1, MappingActionReceipt, SenderObservationV1
from .ports import IdentityMappingRepositoryPort, SenderTokenKeyPort


class MappingActionRefused(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def _refused(action: str, reason: str) -> MappingActionReceipt:
    return emit_mapping_action_receipt(
        "REFUSED", action=action, reason=reason,
        command_application_count=0, audit_count=0, replayed=False,
    )


def _conflict(action: str, reason: str) -> MappingActionReceipt:
    return emit_mapping_action_receipt(
        "CONFLICT", action=action, reason=reason,
        command_application_count=0, audit_count=0, replayed=False,
    )


def _applied(action: str, mapping: IdentityMappingV1) -> MappingActionReceipt:
    return emit_mapping_action_receipt(
        "APPLIED", action=action, aggregate_id=mapping.mapping_id,
        aggregate_version=mapping.version, audit_id=str(uuid4()),
        command_application_count=1, audit_count=1, replayed=False,
    )


def _recompute_key(
    *,
    observation: SenderObservationV1,
    raw_sender: str,
    key_secret_resolver: SenderTokenKeyPort,
    key_id: str,
    key_version: str,
) -> ExternalIdentityKeyV1:
    """SPEC R8: recompute the complete R4 key from the transient raw value
    and discard the raw value before returning."""
    secret = key_secret_resolver.resolve_key(key_id, key_version)
    if secret is None:
        raise MappingActionRefused("SENDER_MISMATCH")
    normalized = normalize_sender_bytes(raw_sender)
    token = derive_sender_token(
        key_id=key_id, key_secret=secret,
        workspace_digest=observation.workspace_digest, endpoint_id=observation.endpoint_id,
        channel_id=observation.channel_id, provider_account_digest=observation.provider_account_digest,
        subject_kind=observation.subject_kind, extraction_policy_id=observation.extraction_policy_id,
        extraction_policy_version=observation.extraction_policy_version,
        verification_scheme="observation", verification_version="1",
        normalized_sender_bytes=normalized,
    )
    return ExternalIdentityKeyV1(
        workspace_digest=observation.workspace_digest, endpoint_id=observation.endpoint_id,
        channel_id=observation.channel_id, provider_account_digest=observation.provider_account_digest,
        subject_kind=observation.subject_kind, extraction_policy_id=observation.extraction_policy_id,
        extraction_policy_version=observation.extraction_policy_version,
        verification_scheme="observation", verification_version="1",
        sender_token=token, token_key_id=key_id, token_key_version=key_version,
    )


class IdentityMappingService:
    def __init__(
        self,
        repository: IdentityMappingRepositoryPort,
        key_port: SenderTokenKeyPort,
        *,
        clock=lambda: datetime.now(timezone.utc),
    ) -> None:
        self._repository = repository
        self._key_port = key_port
        self._clock = clock

    def _reencode_key_or_refuse(self, action, observation_id, raw_sender, key_id, key_version, unit):
        """Shared re-entry path for propose/confirm: returns
        (observation, key) on success or a refusal receipt on failure."""
        try:
            observation = self._repository.get_observation(observation_id, unit=unit)
        except KeyError:
            return None, _refused(action, "IDENTITY_REQUIRED")
        try:
            key = _recompute_key(
                observation=observation, raw_sender=raw_sender,
                key_secret_resolver=self._key_port, key_id=key_id, key_version=key_version,
            )
        except MappingActionRefused as exc:
            return None, _refused(action, exc.reason)
        return (observation, key), None

    def propose(
        self, *, observation_id: str, expected_version: int, target_user_id: str, proposer_id: str,
        raw_sender: str, key_id: str, key_version: str, idempotency_key: str, unit: object = None,
        predecessor_mapping_id: str | None = None, action: str = "PROPOSE",
    ) -> MappingActionReceipt:
        """SPEC R8/completion-rereview2 F3: propose requires observation
        id, target user id, expected version, idempotency key, and
        transient raw sender re-entry. ``expected_version`` is a real,
        enforced CAS input, not decorative: a fresh propose always
        creates the aggregate's version 1, so any other value is a closed
        conflict. ``predecessor_mapping_id``/``action="CORRECT"`` is the
        correction path (SPEC section 4): creates a successor proposal
        referencing the prior mapping without yet revoking it - revocation
        happens atomically only when the successor is confirmed (see
        ``confirm``)."""
        if expected_version != 1:
            return _conflict(action, "VERSION_CONFLICT")
        found, refusal = self._reencode_key_or_refuse(
            action, observation_id, raw_sender, key_id, key_version, unit
        )
        if refusal is not None:
            return refusal
        observation, key = found
        external_key_digest = key.digest()
        if external_key_digest != observation.external_key_digest:
            return _refused(action, "SENDER_MISMATCH")
        now = self._clock()
        mapping = IdentityMappingV1(
            mapping_id=str(uuid4()), external_key_digest=external_key_digest,
            target_user_id=target_user_id,
            proposal_evidence_digest=proposal_evidence_digest(
                observation_id=observation_id, external_key_digest=external_key_digest
            ),
            proposer_id=proposer_id, status="PROPOSED", version=1, created_at=now, updated_at=now,
            predecessor_mapping_id=predecessor_mapping_id,
        )
        try:
            created = self._repository.propose_mapping(mapping, unit=unit)
        except ValueError as exc:
            return _conflict(action, str(exc) or "CURRENT_MAPPING_CONFLICT")
        return _applied(action, created)

    def correct(
        self, *, predecessor_mapping_id: str, expected_predecessor_version: int, target_user_id: str,
        proposer_id: str, raw_sender: str, key_id: str, key_version: str, observation_id: str,
        idempotency_key: str, unit: object = None,
    ) -> MappingActionReceipt:
        """SPEC R8/R9/completion-rereview R2: correction repeats the
        two-human propose/confirm flow with an explicit predecessor
        reference AND its expected version - a stale caller whose read of
        the predecessor is no longer current (e.g. it was revoked or
        corrected by someone else since) must get a closed conflict, not
        silently propose a successor against a premise that has moved. The
        predecessor itself is not mutated until the successor is confirmed."""
        try:
            predecessor = self._repository.get_mapping(predecessor_mapping_id, unit=unit)
        except KeyError:
            return _refused("CORRECT", "IDENTITY_REQUIRED")
        if predecessor.version != expected_predecessor_version:
            return _conflict("CORRECT", "VERSION_CONFLICT")
        if predecessor.status != "CONFIRMED":
            return _refused("CORRECT", "INVALID_LIFECYCLE")
        return self.propose(
            observation_id=observation_id, expected_version=1, target_user_id=target_user_id,
            proposer_id=proposer_id, raw_sender=raw_sender, key_id=key_id, key_version=key_version,
            idempotency_key=idempotency_key, unit=unit,
            predecessor_mapping_id=predecessor_mapping_id, action="CORRECT",
        )

    def confirm(
        self, *, mapping_id: str, expected_version: int, confirmer_id: str, target_user_active: bool,
        observation_id: str, raw_sender: str, key_id: str, key_version: str, unit: object = None,
    ) -> MappingActionReceipt:
        """SPEC R8/section 5: confirm requires a fresh transient re-entry by
        a different human who is neither proposer nor target user."""
        try:
            mapping = self._repository.get_mapping(mapping_id, unit=unit)
        except KeyError:
            return _refused("CONFIRM", "IDENTITY_REQUIRED")
        if mapping.proposer_id == confirmer_id or mapping.target_user_id == confirmer_id:
            return _refused("CONFIRM", "SEPARATION_OF_DUTY")
        if not target_user_active:
            return _refused("CONFIRM", "ACTOR_INACTIVE")
        found, refusal = self._reencode_key_or_refuse(
            "CONFIRM", observation_id, raw_sender, key_id, key_version, unit
        )
        if refusal is not None:
            return refusal
        _observation, key = found
        if key.digest() != mapping.external_key_digest:
            return _refused("CONFIRM", "SENDER_MISMATCH")
        if mapping.status != "PROPOSED":
            return _refused("CONFIRM", "INVALID_LIFECYCLE")
        try:
            updated = self._repository.confirm_mapping(
                mapping_id, expected_version=expected_version, confirmer_id=confirmer_id, unit=unit,
                predecessor_mapping_id=mapping.predecessor_mapping_id,
            )
        except ValueError as exc:
            return _conflict("CONFIRM", str(exc) or "VERSION_CONFLICT")
        action = "CORRECT" if mapping.predecessor_mapping_id else "CONFIRM"
        return _applied(action, updated)

    def reject(
        self, *, mapping_id: str, expected_version: int, rejector_id: str, unit: object = None
    ) -> MappingActionReceipt:
        try:
            mapping = self._repository.get_mapping(mapping_id, unit=unit)
        except KeyError:
            return _refused("REJECT", "IDENTITY_REQUIRED")
        if mapping.status != "PROPOSED":
            return _refused("REJECT", "INVALID_LIFECYCLE")
        try:
            updated = self._repository.reject_mapping(
                mapping_id, expected_version=expected_version, rejector_id=rejector_id, unit=unit
            )
        except ValueError as exc:
            return _conflict("REJECT", str(exc) or "VERSION_CONFLICT")
        return _applied("REJECT", updated)

    def revoke(
        self, *, mapping_id: str, expected_version: int, revoker_id: str, unit: object = None
    ) -> MappingActionReceipt:
        try:
            mapping = self._repository.get_mapping(mapping_id, unit=unit)
        except KeyError:
            return _refused("REVOKE", "IDENTITY_REQUIRED")
        if mapping.status != "CONFIRMED":
            return _refused("REVOKE", "INVALID_LIFECYCLE")
        try:
            updated = self._repository.revoke_mapping(
                mapping_id, expected_version=expected_version, revoker_id=revoker_id, unit=unit
            )
        except ValueError as exc:
            return _conflict("REVOKE", str(exc) or "VERSION_CONFLICT")
        return _applied("REVOKE", updated)

    def resolve(self, external_key_digest: str, *, unit: object = None):
        """SPEC section 4/R15 (identity layer only - placement layer owns
        binding/target eligibility)."""
        try:
            mapping = self._repository.get_current_mapping(external_key_digest, unit=unit)
        except ValueError:
            return emit_identity_resolution_result(
                "REFUSED", reason="MULTIPLE_CURRENT_MAPPINGS", resolution_count=0
            )
        if mapping is None:
            return emit_identity_resolution_result("FALLBACK", reason="NO_MAPPING", resolution_count=0)
        if mapping.status == "REJECTED":
            return emit_identity_resolution_result("FALLBACK", reason="MAPPING_REJECTED", resolution_count=0)
        if mapping.status == "REVOKED":
            return emit_identity_resolution_result("FALLBACK", reason="MAPPING_REVOKED", resolution_count=0)
        if mapping.status != "CONFIRMED":
            return emit_identity_resolution_result("REFUSED", reason="CORRUPT_STATE", resolution_count=0)
        return emit_identity_resolution_result(
            "RESOLVED", mapping_id=mapping.mapping_id, mapping_version=mapping.version,
            target_user_id=mapping.target_user_id, external_key_digest=mapping.external_key_digest,
            resolution_count=1,
        )
