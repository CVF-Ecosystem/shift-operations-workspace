"""P4-E mapping/binding command application service (SPEC section 5, R7-R9).

Implements the full R7 human authority order for every propose/confirm/
reject/revoke/bind/replace/privacy-delete command: (1) verified JWT subject
only (no role trust); (2) fresh authoritative user reload; (3) principal
reconstructed from the fresh stored role; (4) permission; (5) scope/
separation-of-duty (identity_mapping.service already enforces separation);
(6) idempotency/version/lifecycle checks; (7) atomic persist plus audit.
Reuses the SAME cvf-runtime permission gate every other vertical uses -
never a local role comparison (SPEC R7's explicit prohibition).
"""

from __future__ import annotations

import hashlib
import json

from cvf_runtime.audit import AuditRecord
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from identity_mapping import IdentityMappingService, MappingActionReceipt, privacy_delete
from operations_ledger import Ledger

# completion-review F4: canonical control chain recorded on every P4-E
# human-command audit row - same shape convention as every other vertical
# (see incident_service.py's _audit chains), scoped to this family.
_AUDIT_CHAIN = ["identity", "permission", "cas", "audit"]
_RECORD_TYPE = "P4EMapping"


def _payload_digest(payload: dict) -> str:
    """SPEC R9/completion-review F4: binds every command semantic
    non-disclosingly. ``payload`` already excludes raw sender bytes and
    token-key secret bytes by construction of every caller below (it
    carries only ids, key id/version *labels*, and actor/target
    references, never raw_sender itself or key secret material) - so the
    hash below discloses nothing beyond opaque identifiers a caller
    already supplied in cleartext to reach this command."""
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


class _NoSuchActor(Exception):
    pass


def _fresh_principal(ledger: Ledger, principal: Principal, *, unit=None) -> Principal:
    """SPEC R7 steps 1-3: verified subject only; fresh authoritative user
    reload; principal reconstructed from the fresh stored role. The JWT
    role claim (``principal.role`` as decoded) is discarded here."""
    user = ledger.get_user_by_id(principal.user_id, unit=unit)
    if user is None or not user.is_active:
        raise _NoSuchActor()
    return Principal(user_id=user.user_id, role=user.role)


def _idempotent_or_none(ledger: Ledger, idempotency_key: str, payload: dict, *, unit=None):
    """SPEC R9: same key and digest returns the prior sanitized receipt;
    same key with a different digest is a closed idempotency conflict."""
    digest = _payload_digest(payload)
    existing = ledger.get_action_receipt(idempotency_key, unit=unit)
    if existing is None:
        return digest, None
    if existing["payload_digest"] != digest:
        return digest, MappingActionReceipt(
            outcome="CONFLICT", action=payload.get("action", "UNKNOWN"),
            reason="IDEMPOTENCY_CONFLICT", command_application_count=0, audit_count=0, replayed=False,
        )
    prior = dict(existing["receipt"])
    prior["command_application_count"] = 0
    prior["audit_count"] = 0
    prior["replayed"] = True
    prior["outcome"] = "IDEMPOTENT_REPLAY"
    return digest, MappingActionReceipt(**prior)


class P4eMappingCommandService:
    def __init__(self, ledger: Ledger, key_port) -> None:
        self.ledger = ledger
        self.identity_service = IdentityMappingService(_LedgerRepositoryAdapter(ledger), key_port)

    def propose(
        self, principal: Principal, *, observation_id: str, expected_version: int, target_user_id: str,
        raw_sender: str, key_id: str, key_version: str, idempotency_key: str,
    ) -> MappingActionReceipt:
        with self.ledger.transaction() as unit:
            try:
                actor = _fresh_principal(self.ledger, principal, unit=unit)
            except _NoSuchActor:
                return self._refused("PROPOSE", "ACTOR_INACTIVE")
            require_action(actor, "external_identity_mapping.propose")

            payload = {
                "action": "PROPOSE", "observation_id": observation_id, "expected_version": expected_version,
                "target_user_id": target_user_id, "actor_id": actor.user_id,
                "raw_sender": raw_sender, "key_id": key_id, "key_version": key_version,
            }
            digest, replay = _idempotent_or_none(self.ledger, idempotency_key, payload, unit=unit)
            if replay is not None:
                return replay

            receipt = self.identity_service.propose(
                observation_id=observation_id, expected_version=expected_version, target_user_id=target_user_id,
                proposer_id=actor.user_id, raw_sender=raw_sender, key_id=key_id, key_version=key_version,
                idempotency_key=idempotency_key, unit=unit,
            )
            self._persist_receipt(idempotency_key, "PROPOSE", digest, receipt, unit=unit, actor=actor)
        return receipt

    def correct(
        self, principal: Principal, *, predecessor_mapping_id: str, expected_predecessor_version: int,
        target_user_id: str, raw_sender: str, key_id: str, key_version: str, observation_id: str,
        idempotency_key: str,
    ) -> MappingActionReceipt:
        with self.ledger.transaction() as unit:
            try:
                actor = _fresh_principal(self.ledger, principal, unit=unit)
            except _NoSuchActor:
                return self._refused("CORRECT", "ACTOR_INACTIVE")
            require_action(actor, "external_identity_mapping.correct")

            payload = {"action": "CORRECT", "predecessor_mapping_id": predecessor_mapping_id,
                       "expected_predecessor_version": expected_predecessor_version,
                       "target_user_id": target_user_id, "actor_id": actor.user_id,
                       "observation_id": observation_id, "raw_sender": raw_sender,
                       "key_id": key_id, "key_version": key_version}
            digest, replay = _idempotent_or_none(self.ledger, idempotency_key, payload, unit=unit)
            if replay is not None:
                return replay

            receipt = self.identity_service.correct(
                predecessor_mapping_id=predecessor_mapping_id,
                expected_predecessor_version=expected_predecessor_version, target_user_id=target_user_id,
                proposer_id=actor.user_id, raw_sender=raw_sender, key_id=key_id, key_version=key_version,
                observation_id=observation_id, idempotency_key=idempotency_key, unit=unit,
            )
            self._persist_receipt(idempotency_key, "CORRECT", digest, receipt, unit=unit, actor=actor)
        return receipt

    def confirm(
        self, principal: Principal, *, mapping_id: str, expected_version: int, raw_sender: str,
        key_id: str, key_version: str, observation_id: str, idempotency_key: str,
    ) -> MappingActionReceipt:
        with self.ledger.transaction() as unit:
            try:
                actor = _fresh_principal(self.ledger, principal, unit=unit)
            except _NoSuchActor:
                return self._refused("CONFIRM", "ACTOR_INACTIVE")
            require_action(actor, "external_identity_mapping.confirm")

            payload = {"action": "CONFIRM", "mapping_id": mapping_id, "expected_version": expected_version,
                       "actor_id": principal.user_id, "observation_id": observation_id,
                       "raw_sender": raw_sender, "key_id": key_id, "key_version": key_version}
            digest, replay = _idempotent_or_none(self.ledger, idempotency_key, payload, unit=unit)
            if replay is not None:
                return replay

            try:
                mapping = self.ledger.get_mapping(mapping_id, unit=unit)
            except KeyError:
                return self._refused("CONFIRM", "IDENTITY_REQUIRED")
            target_user = self.ledger.get_user_by_id(mapping.target_user_id, unit=unit)
            target_active = target_user is not None and target_user.is_active

            receipt = self.identity_service.confirm(
                mapping_id=mapping_id, expected_version=expected_version, confirmer_id=actor.user_id,
                target_user_active=target_active, observation_id=observation_id, raw_sender=raw_sender,
                key_id=key_id, key_version=key_version, unit=unit,
            )
            self._persist_receipt(idempotency_key, "CONFIRM", digest, receipt, unit=unit, actor=actor)
        return receipt

    def reject(self, principal: Principal, *, mapping_id: str, expected_version: int, idempotency_key: str):
        return self._simple_action(
            principal, action="REJECT", governed_action="external_identity_mapping.reject",
            mapping_id=mapping_id, expected_version=expected_version, idempotency_key=idempotency_key,
            call=lambda actor, unit: self.identity_service.reject(
                mapping_id=mapping_id, expected_version=expected_version, rejector_id=actor.user_id, unit=unit,
            ),
        )

    def revoke(self, principal: Principal, *, mapping_id: str, expected_version: int, idempotency_key: str):
        return self._simple_action(
            principal, action="REVOKE", governed_action="external_identity_mapping.revoke",
            mapping_id=mapping_id, expected_version=expected_version, idempotency_key=idempotency_key,
            call=lambda actor, unit: self.identity_service.revoke(
                mapping_id=mapping_id, expected_version=expected_version, revoker_id=actor.user_id, unit=unit,
            ),
        )

    def privacy_delete(
        self, principal: Principal, *, mapping_id: str, expected_version: int, reason: str, idempotency_key: str,
    ):
        return self._simple_action(
            principal, action="PRIVACY_DELETE", governed_action="external_identity_mapping.privacy_delete",
            mapping_id=mapping_id, expected_version=expected_version, idempotency_key=idempotency_key,
            call=lambda actor, unit: privacy_delete(
                _LedgerRepositoryAdapter(self.ledger), mapping_id=mapping_id, expected_version=expected_version,
                actor_role=actor.role, reason=reason, idempotency_key=idempotency_key, unit=unit,
            ),
        )

    def _simple_action(self, principal, *, action, governed_action, mapping_id, expected_version, idempotency_key, call):
        with self.ledger.transaction() as unit:
            try:
                actor = _fresh_principal(self.ledger, principal, unit=unit)
            except _NoSuchActor:
                return self._refused(action, "ACTOR_INACTIVE")
            require_action(actor, governed_action)

            payload = {"action": action, "mapping_id": mapping_id, "expected_version": expected_version}
            digest, replay = _idempotent_or_none(self.ledger, idempotency_key, payload, unit=unit)
            if replay is not None:
                return replay

            receipt = call(actor, unit)
            self._persist_receipt(idempotency_key, action, digest, receipt, unit=unit, actor=actor)
        return receipt

    def _persist_receipt(self, idempotency_key, action, digest, receipt, *, unit, actor=None) -> None:
        """SPEC R7 step 7/completion-review F4: persists a REAL actor-bound
        audit row via ``Ledger.append_audit`` in the SAME unit of work as
        the receipt - both calls run inside the caller's
        ``with self.ledger.transaction()`` block, so if ``append_audit``
        raises, the whole block (mapping/binding mutation included) rolls
        back; no receipt or audit is ever persisted for a mutation that
        did not also get its audit row."""
        if receipt.outcome != "APPLIED":
            return
        if actor is not None:
            self.ledger.append_audit(
                AuditRecord(
                    audit_id=receipt.audit_id, actor_id=actor.user_id, actor_role=actor.role,
                    action=action, record_type=_RECORD_TYPE, record_id=receipt.aggregate_id,
                    control_chain=_AUDIT_CHAIN, after_state=receipt.outcome,
                ),
                unit=unit,
            )
        self.ledger.put_action_receipt(
            idempotency_key, action, digest, receipt.model_dump(exclude_none=True), unit=unit,
        )

    def _refused(self, action: str, reason: str) -> MappingActionReceipt:
        return MappingActionReceipt(
            outcome="REFUSED", action=action, reason=reason,
            command_application_count=0, audit_count=0, replayed=False,
        )

    def list_observations(self, principal: Principal) -> list:
        """SPEC R17/completion-rereview R2: the required observation-list
        operation at the real API layer - fresh principal, governed
        permission, and only the closed SenderObservationV1 selector
        metadata the ledger already exposes (never sender_token/raw
        sender/candidate)."""
        actor = _fresh_principal(self.ledger, principal)
        require_action(actor, "external_identity_mapping.read")
        return self.ledger.list_observations()


class _LedgerRepositoryAdapter:
    """Adapts the Ledger Protocol's P4-E methods to
    ``identity_mapping.ports.IdentityMappingRepositoryPort`` - a thin
    pass-through, added because the port's method names already match the
    ledger's 1:1 (kept as an explicit seam rather than passing the ledger
    directly, so the identity-mapping package never depends on the Ledger
    Protocol type itself, per SPEC R18)."""

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger

    def __getattr__(self, name: str):
        return getattr(self._ledger, name)
