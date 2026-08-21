"""Context admission and caller-facts adapters (SPEC R5/R10/R11).

Decides whether declared context facts may be sent to a given placement, *before*
``assert_placement_allowed`` runs. Admission is deliberately stricter than the
placement gate alone:

- PUBLIC to an external placement still requires explicit redaction evidence;
- INTERNAL to an external placement requires positive, caller-declared
  minimization proof. P4-A1's current handoff reports
  ``minimization_evidence_status=NOT_PROVEN``, so an honest caller passing those
  facts through is refused here. Nothing in this module mutates, relabels, or
  reinterprets that handoff;
- CONFIDENTIAL and RESTRICTED are refused for external placement outright and
  are therefore never eligible for the public canary endpoint.

Local and enterprise placements do not require redaction/minimization evidence
here; the placement gate remains authoritative for what those placements allow.

This module also adapts gateway facts to ``cvf_runtime``'s policy-dict/dataclass
shapes (``cost_policy_of``/``termination_policy_of``/``task_state_of``), and binds
receipts to the facts actually dispatched (``assert_context_digest_matches``,
``assert_provider_identity_matches``, ``canonicalize_endpoint_origin``) rather
than trusting caller-declared values, per P4A-REV-F3.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

from cvf_runtime.termination import TaskState

from .errors import (
    ContextDigestMismatchError,
    ContextInadmissibleError,
    EndpointOriginError,
    NoEvidenceError,
    ProviderIdentityMismatchError,
)
from .models import Classification, ContextFacts, GatewayRequest, Placement, digest_of

EXTERNAL_REQUIRES_REDACTION = (Classification.PUBLIC, Classification.INTERNAL)
EXTERNAL_FORBIDDEN = (Classification.CONFIDENTIAL, Classification.RESTRICTED)
_ALLOWED_SCHEMES = ("https", "http")
_MAX_ENDPOINT_ORIGIN_LENGTH = 200

# Fixed data-scope rule set (cvf_runtime.data_scope.classification_rule).
_EXTERNAL_AI_RULES = {
    "PUBLIC": "allow",
    "INTERNAL": "allow_after_minimization",
    "CONFIDENTIAL": "local_or_enterprise_only",
    "RESTRICTED": "local_only",
}


class CvfProfileView:
    """Minimal ``CvfProfile`` view: lets the gateway call the real placement
    gate without loading a YAML profile file."""

    data = {"external_ai": _EXTERNAL_AI_RULES}


def assert_context_digest_matches(context: dict[str, Any], facts: ContextFacts) -> None:
    """P4A-REV-F3: recompute the actual digest and bind it to ``facts``.

    The prior version trusted ``facts.context_digest`` as a caller-supplied
    fact with no check that it corresponds to the ``context`` actually being
    sent. A caller could declare a small, clean digest while dispatching
    arbitrary real content. Recomputing here makes the receipt's
    ``context_digest`` provably the digest of what was actually dispatched.
    """
    actual = digest_of(context)
    if actual != facts.context_digest:
        raise ContextDigestMismatchError(
            "declared context_digest does not match the actual dispatched context"
        )


def assert_provider_identity_matches(
    result_provider_id: str, result_model_id: str, request: GatewayRequest
) -> None:
    """P4A-REV-F3: a provider's response must claim to be the provider/model
    that was actually registered and dispatched, or the receipt could record
    false provenance (SPEC R10/R11)."""
    if result_provider_id != request.provider_id or result_model_id != request.model_id:
        raise ProviderIdentityMismatchError(
            "provider result identity does not match the registered/dispatched request"
        )


def canonicalize_endpoint_origin(raw: str) -> str:
    """P4A-REV-F3: reduce ``raw`` to a bare ``scheme://host[:port]`` string.

    Strips userinfo, path, query, and fragment unconditionally rather than
    trusting a caller-supplied already-safe value, so a secret-bearing or
    otherwise unsafe origin can never reach a persisted receipt. An empty
    input is allowed through as empty (no endpoint contacted yet, e.g. for a
    pre-dispatch refusal receipt).
    """
    if not raw:
        return ""
    parts = urlsplit(raw)
    if parts.scheme not in _ALLOWED_SCHEMES or not parts.hostname:
        raise EndpointOriginError(f"endpoint_origin must be a bare http(s) origin: {parts.scheme!r}")
    if parts.username or parts.password:
        raise EndpointOriginError("endpoint_origin must not carry userinfo/credentials")
    netloc = parts.hostname if parts.port is None else f"{parts.hostname}:{parts.port}"
    origin = urlunsplit((parts.scheme, netloc, "", "", ""))
    if len(origin) > _MAX_ENDPOINT_ORIGIN_LENGTH:
        raise EndpointOriginError("endpoint_origin exceeds the safe length bound")
    return origin


def cost_policy_of(request: GatewayRequest) -> dict[str, Any]:
    """Adapt ``BudgetFacts`` to the ``cvf_runtime.budget`` policy-dict shape.

    P4A-REV-F2: ``cvf_runtime.budget`` reads USD floats
    (``BudgetState.spent_today_usd``/``spent_month_usd`` and
    ``default_daily_budget_usd``/``default_monthly_budget_usd``), while
    ``BudgetFacts`` carries integer USD-millis. The conversion happens only
    here, at the adapter boundary into the real gate; gateway-side arithmetic
    (the usage ledger) stays integer millis throughout.
    """
    facts = request.budget_facts
    return {
        "per_request_token_limit": facts.per_request_token_limit,
        "default_daily_budget_usd": millis_to_usd(facts.daily_budget_usd_millis),
        "default_monthly_budget_usd": millis_to_usd(facts.monthly_budget_usd_millis),
        "on_budget_exceeded": facts.on_budget_exceeded,
        "kill_switch_enabled": facts.kill_switch_enabled,
    }


def millis_to_usd(value_millis: int) -> float:
    """Convert integer USD-millis to a USD float for the ``cvf_runtime`` boundary."""
    return value_millis / 1000.0


def termination_policy_of(request: GatewayRequest) -> dict[str, Any]:
    """Adapt ``TerminationFacts`` to the ``cvf_runtime.termination`` policy shape."""
    return {"terminate_when": list(request.termination_facts.terminate_when)}


def task_state_of(request: GatewayRequest) -> TaskState:
    """Adapt ``TerminationFacts`` to the real ``cvf_runtime.termination.TaskState``."""
    facts = request.termination_facts
    return TaskState(
        elapsed_s=facts.elapsed_s,
        timeout_s=facts.timeout_s,
        used_tokens=facts.used_tokens,
        token_limit=facts.token_limit,
        consecutive_failures=facts.consecutive_failures,
        schema_failures=facts.schema_failures,
        kill_switch_active=facts.kill_switch_active,
    )


def assert_context_admissible(facts: ContextFacts, placement: Placement) -> None:
    """Raise when ``facts`` may not be sent to ``placement``.

    Raises :class:`NoEvidenceError` when there is nothing to ground a call, and
    :class:`ContextInadmissibleError` for a classification/placement refusal.
    """
    if facts.evidence_count <= 0:
        raise NoEvidenceError("no admitted evidence for this request")

    if placement is not Placement.EXTERNAL:
        return

    if facts.classification in EXTERNAL_FORBIDDEN:
        raise ContextInadmissibleError(
            f"{facts.classification.value} context may not reach an external provider"
        )
    if facts.classification in EXTERNAL_REQUIRES_REDACTION and not facts.redaction_applied:
        raise ContextInadmissibleError(
            f"{facts.classification.value} external context requires applied redaction"
        )
    if facts.classification is Classification.INTERNAL and not facts.minimization_proven:
        raise ContextInadmissibleError(
            "INTERNAL external context requires proven minimization evidence"
        )
