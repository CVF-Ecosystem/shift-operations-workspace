"""P4-B AI provider mode foundation.

Zero-call ``NO_AI``, deterministic local ``RULES_ONLY``, a default-denied
test-only mock, registry-owned provider metadata, and an ``EXTERNAL_AI`` mode
that delegates at most once to an injected P4-A ``AIGateway``. Depends only
on the standard library, Pydantic, and ``ai_gateway`` (for the canonical
types this package reuses rather than duplicates). No provider SDK, network
client, environment, filesystem, database, or hidden CVF Core import
anywhere in this package (SPEC R10).
"""

from __future__ import annotations

from .errors import ProviderModeError
from .mock_provider import MockProviderAdapter
from .models import (
    MockAuthorizationV1,
    ProviderKind,
    ProviderMetadataV1,
    ProviderModeOutcome,
    ProviderModeReceiptV1,
    ProviderModeRequestV1,
    RuleDefinitionV1,
)
from .registry import ProviderAdapterRegistry
from .rules_only import RuleSetV1
from .service import ProviderModeService

__all__ = [
    "ProviderModeError",
    "MockProviderAdapter",
    "MockAuthorizationV1",
    "ProviderKind",
    "ProviderMetadataV1",
    "ProviderModeOutcome",
    "ProviderModeReceiptV1",
    "ProviderModeRequestV1",
    "RuleDefinitionV1",
    "ProviderAdapterRegistry",
    "RuleSetV1",
    "ProviderModeService",
]
