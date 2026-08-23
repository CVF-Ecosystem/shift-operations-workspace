"""``ProviderAdapterRegistry`` (SPEC R8): immutable provider metadata.

Owns provider kind/placement/model metadata explicitly and deterministically.
Duplicate or relabeling registration fails closed: once a ``provider_id`` is
registered, re-registering it with different metadata is refused rather than
silently overwritten. A ``MOCK`` kind is denied by default and requires
explicit ``allow_test_only=True``. ``production_projection`` and
``evidence_projection`` both structurally exclude every ``MOCK`` entry
regardless of any caller-supplied label - the exclusion is a kind check on
the registry's own stored metadata, not something a caller can talk around.
"""

from __future__ import annotations

from pydantic import ValidationError

from .errors import DuplicateProviderRegistrationError, ProviderNotRegisteredError
from .models import ProviderKind, ProviderMetadataV1


class ProviderAdapterRegistry:
    """In-memory registry of provider metadata. No network, no I/O."""

    def __init__(self) -> None:
        self._entries: dict[str, ProviderMetadataV1] = {}

    def register(self, metadata: object, *, allow_test_only: bool = False) -> None:
        """Register ``metadata`` under its ``provider_id``.

        Refuses (fails closed) when: the kind is ``MOCK`` and
        ``allow_test_only`` was not explicitly ``True``; or the
        ``provider_id`` is already registered with different metadata (an
        identical re-registration is idempotent and allowed, but a relabel
        attempt - same id, different kind/placement/models - is rejected);
        or ``metadata`` does not genuinely revalidate as a real
        ``ProviderMetadataV1`` (P4B-REV-F4-R1/F4-R2).

        ``metadata`` is declared ``object`` on purpose: this is a public
        boundary and the untrusted caller value might already be a valid
        ``ProviderMetadataV1``, a ``model_construct``-bypassed instance of
        it, a primitive mapping (plain ``dict``), or an arbitrary unrelated
        object - never assumed to already have a ``.model_dump`` method.

        P4B-REV-F4-R1: never trust an attached ``ProviderMetadataV1``
        instance as already-valid merely because ``isinstance`` says so - a
        ``model_construct``-bypassed instance (e.g. ``kind="BOGUS"``,
        ``placement="mars"``) skips the model's own validators entirely, and
        Pydantic's ``model_validate`` does not re-run them for an
        already-same-type instance either. Dumping to a primitive first (via
        ``.model_dump(mode="python")``) forces genuine field-level
        revalidation through ``model_validate`` (the same discipline already
        applied to ``MockAuthorizationV1`` in ``mock_provider.py``).

        P4B-REV-F4-R2: a primitive dump is obtained ONLY when ``metadata``
        actually is a ``ProviderMetadataV1`` instance (checked via
        ``isinstance`` first) - a raw mapping/dict or an arbitrary unrelated
        object (e.g. ``object()``) has no ``.model_dump`` at all, so calling
        it unconditionally raised an undocumented, un-typed
        ``AttributeError``. Any other shape is passed to
        ``ProviderMetadataV1.model_validate`` as-is - it natively accepts
        both a plain dict and a model instance - and only its own
        documented, expected ``ValidationError`` is normalized to the typed
        registration error; no other exception is caught or expected to
        occur here. The registry is left completely unchanged on every
        rejected call - no partial mutation.
        """
        raw = metadata.model_dump(mode="python") if isinstance(metadata, ProviderMetadataV1) else metadata
        try:
            revalidated = ProviderMetadataV1.model_validate(raw)
        except ValidationError as exc:
            raise DuplicateProviderRegistrationError(
                "metadata failed real field-level revalidation from its primitive dump"
            ) from exc
        if revalidated.kind is ProviderKind.MOCK and not allow_test_only:
            raise DuplicateProviderRegistrationError(
                "MOCK provider registration requires allow_test_only=True"
            )
        existing = self._entries.get(revalidated.provider_id)
        if existing is not None and existing != revalidated:
            raise DuplicateProviderRegistrationError(
                f"provider_id already registered with different metadata: {revalidated.provider_id}"
            )
        self._entries[revalidated.provider_id] = revalidated

    def resolve(self, provider_id: str, model_id: str) -> ProviderMetadataV1:
        """Return the registered metadata for an explicitly registered
        (provider, model) pair, or fail closed."""
        metadata = self._entries.get(provider_id)
        if metadata is None:
            raise ProviderNotRegisteredError(f"provider not registered: {provider_id}")
        if model_id not in metadata.model_ids:
            raise ProviderNotRegisteredError(
                f"model not registered for provider {provider_id}: {model_id}"
            )
        return metadata

    def registered_metadata(self, provider_id: str) -> ProviderMetadataV1 | None:
        """Return the provider's registered metadata, or ``None`` when the
        provider id is not registered at all."""
        return self._entries.get(provider_id)

    def production_projection(self) -> tuple[ProviderMetadataV1, ...]:
        """All registered entries except ``MOCK`` (SPEC R8), sorted by
        ``provider_id`` for determinism."""
        return tuple(
            sorted(
                (m for m in self._entries.values() if m.kind is not ProviderKind.MOCK),
                key=lambda m: m.provider_id,
            )
        )

    def evidence_projection(self) -> tuple[ProviderMetadataV1, ...]:
        """All registered entries eligible as governance evidence: never
        ``MOCK``, and only entries whose own ``evidence_eligible`` is
        ``True`` (SPEC R8) - never trusts a caller-supplied label outside
        this registry's own stored metadata."""
        return tuple(
            sorted(
                (
                    m
                    for m in self._entries.values()
                    if m.kind is not ProviderKind.MOCK and m.evidence_eligible
                ),
                key=lambda m: m.provider_id,
            )
        )


__all__ = ["ProviderAdapterRegistry"]
