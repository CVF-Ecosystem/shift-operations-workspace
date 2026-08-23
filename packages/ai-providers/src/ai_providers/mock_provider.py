"""``MockProviderAdapter`` (SPEC R7): a test-only, evidence-ineligible
structural implementation of ``ai_gateway.provider.AIProvider``.

Construction requires an explicit, immutable ``MockAuthorizationV1`` whose
``purpose`` equals exactly ``TEST_ONLY_COMPONENT_TEST`` and whose
``evidence_eligible`` is exactly ``False``. P4B-REV-F4.1: this is enforced by
reconstructing the authorization from its own primitive dump via
``MockAuthorizationV1.model_validate`` - never by trusting ``isinstance`` -
so an ``authorization`` built via ``MockAuthorizationV1.model_construct``
(which skips the model's own validators entirely) is still forced through
real field-level revalidation here and rejected if it does not genuinely
satisfy the purpose/eligibility grammar. Responses are fixed, bounded,
deep-copy isolated primitives; calls/cancels are tracked deterministically.
No network of any kind is performed here.
"""

from __future__ import annotations

import copy
from typing import Any

from ai_gateway.models import ProviderRequest, ProviderResult
from pydantic import ValidationError

from .models import MockAuthorizationV1, assert_bounded_json


class MockProviderAdapter:
    """Structurally matches ``ai_gateway.provider.AIProvider``. Never used
    as governance evidence: construction fails closed without a validated
    :class:`~ai_providers.models.MockAuthorizationV1`."""

    def __init__(
        self,
        *,
        provider_id: str,
        authorization: MockAuthorizationV1,
        fixed_output: dict[str, Any],
    ) -> None:
        if not isinstance(authorization, MockAuthorizationV1):
            # MockAuthorizationV1's own validators already reject an invalid
            # purpose/evidence_eligible; this only guards against a caller
            # passing something else entirely (e.g. a plain dict).
            raise TypeError("authorization must be a validated MockAuthorizationV1")
        # P4B-REV-F4.1: never trust isinstance alone - an
        # authorization built via model_construct() is an instance of the
        # class but never ran the class's own validators. Reconstruct from
        # the primitive dump so the purpose/eligibility grammar is always
        # genuinely re-checked, independent of how the instance was built.
        try:
            revalidated = MockAuthorizationV1.model_validate(
                authorization.model_dump(mode="python")
            )
        except ValidationError as exc:
            raise ValueError(
                "authorization failed real field-level revalidation from its primitive dump"
            ) from exc
        assert_bounded_json(fixed_output, label="fixed_output")
        self.provider_id = provider_id
        self._authorization = revalidated
        self._fixed_output = copy.deepcopy(fixed_output)
        self.calls = 0
        self.cancels = 0
        self._cancelled_request_ids: list[str] = []

    @property
    def authorization(self) -> MockAuthorizationV1:
        return self._authorization

    @property
    def evidence_eligible(self) -> bool:
        """Always ``False`` for a mock adapter (R7) - exposed so a caller or
        registry can check without reaching into private state."""
        return self._authorization.evidence_eligible

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        self.calls += 1
        return ProviderResult(
            output=copy.deepcopy(self._fixed_output),
            provider_id=self.provider_id,
            model_id=request.model_id,
            usage={"total_tokens": 0, "cost_usd_millis": 0},
        )

    async def health_check(self) -> dict[str, Any]:
        return {"status": "mock", "evidence_eligible": False}

    async def cancel_request(self, request_id: str) -> None:
        self.cancels += 1
        self._cancelled_request_ids.append(request_id)

    @property
    def cancelled_request_ids(self) -> tuple[str, ...]:
        return tuple(self._cancelled_request_ids)


__all__ = ["MockProviderAdapter"]
