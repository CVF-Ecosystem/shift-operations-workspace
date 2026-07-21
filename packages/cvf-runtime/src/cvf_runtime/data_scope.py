"""Data scope / classification gate.

CVF control: ``data_scope``. Governs where classified data may go, per
data-policy.yaml. The key rule is external_ai: what classifications may be sent
to an external (cloud) model, and under what condition.

    PUBLIC        -> allow
    INTERNAL      -> allow_after_minimization
    CONFIDENTIAL  -> local_or_enterprise_only
    RESTRICTED    -> local_only

This gate answers "may this classified content be sent to a provider of this
placement?" and is the guard the AI context builder must call before any
outbound model call. It runs and is tested now; it becomes load-bearing when an
AI mode beyond NO_AI is enabled.
"""

from __future__ import annotations

from cvf_runtime.errors import CvfDenied
from cvf_runtime.policy_loader import CvfProfile

# Provider placement categories.
EXTERNAL = "external"      # cloud LLM / third-party API
ENTERPRISE = "enterprise"  # enterprise gateway under contract
LOCAL = "local"            # on-prem / local model

# Which placements satisfy each external_ai rule.
_RULE_ALLOWS: dict[str, set[str]] = {
    "allow": {EXTERNAL, ENTERPRISE, LOCAL},
    "allow_after_minimization": {EXTERNAL, ENTERPRISE, LOCAL},
    "local_or_enterprise_only": {ENTERPRISE, LOCAL},
    "local_only": {LOCAL},
}


def classification_rule(profile: CvfProfile, classification: str) -> str:
    rules = profile.data.get("external_ai", {})
    if classification not in rules:
        raise CvfDenied(
            control="data_scope",
            reason=f"unknown data classification: {classification}",
            http_status=422,
        )
    return rules[classification]


def requires_minimization(profile: CvfProfile, classification: str) -> bool:
    return classification_rule(profile, classification) == "allow_after_minimization"


def assert_placement_allowed(
    *, profile: CvfProfile, classification: str, placement: str
) -> None:
    """Raise :class:`CvfDenied` if ``classification`` may not go to ``placement``."""
    rule = classification_rule(profile, classification)
    allowed = _RULE_ALLOWS.get(rule, set())
    if placement not in allowed:
        raise CvfDenied(
            control="data_scope",
            reason=(
                f"{classification} data may not be sent to a {placement!r} provider "
                f"(policy: {rule})"
            ),
            http_status=403,
        )
