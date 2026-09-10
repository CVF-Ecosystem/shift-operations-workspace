"""Provider-neutral read/write ports for identity-mapping persistence.

``conversation-routing`` consumes only :class:`IdentityMappingReadPort` (SPEC
R18: it "consumes an identity read port, and never mutates mappings").
Workspace API composes the write side via
:class:`IdentityMappingRepositoryPort`; identity-mapping itself never imports
a concrete Ledger backend.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import ExternalIdentityKeyV1, IdentityMappingV1, SenderObservationV1


@runtime_checkable
class IdentityMappingReadPort(Protocol):
    def get_current_mapping(
        self, external_key_digest: str, *, unit: object = None
    ) -> IdentityMappingV1 | None:
        """Return the single current confirmed mapping for a complete
        external identity key, or ``None`` if absent. Raises ``ValueError``
        if more than one current confirmed mapping exists (corruption)."""
        ...


@runtime_checkable
class IdentityMappingRepositoryPort(Protocol):
    def add_observation(
        self, observation: SenderObservationV1, *, unit: object = None
    ) -> SenderObservationV1: ...

    def get_observation(self, observation_id: str, *, unit: object = None) -> SenderObservationV1: ...

    def get_current_mapping(
        self, external_key_digest: str, *, unit: object = None
    ) -> IdentityMappingV1 | None: ...

    def get_mapping(self, mapping_id: str, *, unit: object = None) -> IdentityMappingV1: ...

    def propose_mapping(self, mapping: IdentityMappingV1, *, unit: object = None) -> IdentityMappingV1: ...

    def confirm_mapping(
        self, mapping_id: str, *, expected_version: int, confirmer_id: str,
        predecessor_mapping_id: str | None = None, unit: object = None,
    ) -> IdentityMappingV1:
        """When ``predecessor_mapping_id`` is set (a correction successor),
        atomically revokes that predecessor in the same write as confirming
        this mapping (SPEC section 4)."""
        ...

    def reject_mapping(
        self, mapping_id: str, *, expected_version: int, rejector_id: str, unit: object = None
    ) -> IdentityMappingV1: ...

    def revoke_mapping(
        self, mapping_id: str, *, expected_version: int, revoker_id: str, unit: object = None
    ) -> IdentityMappingV1: ...

    def privacy_delete_mapping(
        self, mapping_id: str, *, expected_version: int, unit: object = None
    ) -> IdentityMappingV1: ...


class SenderTokenKeyPort(Protocol):
    """SPEC R2/R19: resolves the currently active token key, and (during the
    24-hour dual-read window) the immediately previous version. Missing,
    inactive, ambiguous, or unavailable key authority must yield no
    observation and no mapping attempt - callers must not try arbitrary
    keys."""

    def active_key(self) -> tuple[str, str, bytes]:
        """Returns (key_id, key_version, secret) for the current active key."""
        ...

    def resolve_key(self, key_id: str, key_version: str) -> bytes | None:
        """Returns the secret for exactly this key id/version if it is the
        current or immediately-previous version within the dual-read
        window, else ``None``."""
        ...


__all__ = [
    "ExternalIdentityKeyV1",
    "IdentityMappingReadPort",
    "IdentityMappingRepositoryPort",
    "SenderTokenKeyPort",
]
