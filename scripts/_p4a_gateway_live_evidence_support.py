"""Support state and helpers for the P4-A live evidence run (SPEC R13).

Separated from the runner so the mechanics are unit-testable without making a
provider call. Nothing here performs I/O at import time.

Secret handling: the API key is read from the environment at dispatch time only.
It is never printed, persisted, hashed, logged, or returned. ``sanitize`` is
applied to every string that reaches an artifact, and ``scan_for_secrets``
double-checks the finished receipt before it is written.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

_REPO_ROOT = Path(__file__).resolve().parents[1]
for _sub in ("ai-gateway", "cvf-runtime"):
    _p = str(_REPO_ROOT / "packages" / _sub / "src")
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ai_gateway.models import (  # noqa: E402
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    GatewayRequest,
    Placement,
    TerminationFacts,
)
from ai_gateway.registry import ProviderRegistry  # noqa: E402
from ai_gateway.service import AIGateway  # noqa: E402
from ai_gateway.usage import UsageLedger  # noqa: E402

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROVIDER_ID = "alibaba_dashscope_evidence_only"

# The canary is deliberately PUBLIC, harmless, and content-free: it asks only
# for a tiny fixed-shape JSON object so schema acceptance is meaningful.
CANARY_TASK_TYPE = "p4a_public_canary"
CANARY_PROMPT = (
    "Return only a compact JSON object with exactly these keys: "
    '"status" set to the string "ok", and "checked" set to the integer 1. '
    "No prose, no code fence, no extra keys."
)
CANARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "checked"],
    "properties": {
        "status": {"type": "string", "enum": ["ok"]},
        "checked": {"type": "integer", "minimum": 1, "maximum": 1},
    },
}

SECRET_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
    re.compile(r"\b(?:sk|ak)-[A-Za-z0-9_-]{8,}", re.I),
    re.compile(r"\b(?:API_KEY|SECRET|PASSWORD|TOKEN)\s*[:=]\s*\S+", re.I),
    re.compile(r"(?:postgres(?:ql)?|https?)://[^\s/@:]+:[^\s/@]+@", re.I),
)

REFUSAL_CASES = (
    "NO_AI",
    "NO_EVIDENCE",
    "P4A1_INTERNAL_WITHOUT_MINIMIZATION",
    "RESTRICTED_EXTERNAL_PLACEMENT",
    "BUDGET_EXCEEDED",
    "KILL_SWITCH_ACTIVE",
)


class LiveEvidenceError(RuntimeError):
    """Raised for any condition that must yield LIVE_EVIDENCE_BLOCKED."""


def key_presence() -> tuple[bool, str | None]:
    """Return ``(present, env_var_name)`` without revealing the value."""
    for name in KEY_ENV_NAMES:
        if os.environ.get(name, "").strip():
            return True, name
    return False, None


def endpoint() -> str:
    """Full chat-completions endpoint. Never included verbatim in artifacts."""
    base_url = next(
        (os.environ[name].strip() for name in BASE_URL_ENV_NAMES if os.environ.get(name, "").strip()),
        DEFAULT_BASE_URL,
    ).rstrip("/")
    return base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"


def safe_origin(url: str) -> str:
    """Scheme + host only: no path, query, credentials, or fragment."""
    parts = urlsplit(url)
    host = parts.hostname or ""
    return urlunsplit((parts.scheme, host, "", "", ""))


def sanitize(text: str, *, limit: int = 200) -> str:
    """Redact secret-shaped substrings and bound the length."""
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    # Defence in depth: if the live key value itself appears, remove it even
    # when it does not match a generic pattern.
    for name in KEY_ENV_NAMES:
        value = os.environ.get(name, "").strip()
        if value and value in redacted:
            redacted = redacted.replace(value, "[REDACTED]")
    return redacted[:limit]


def scan_for_secrets(text: str) -> list[str]:
    """Return the names of any secret patterns still present in ``text``."""
    hits = [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]
    for name in KEY_ENV_NAMES:
        value = os.environ.get(name, "").strip()
        if value and value in text:
            hits.append(f"literal:{name}")
    return hits


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def extract_json_object(content: str) -> dict[str, Any]:
    """Parse a JSON object from model content, tolerating a code fence.

    Raises :class:`LiveEvidenceError` when no object can be parsed; the caller
    treats that as a failed live run rather than retrying.
    """
    text = content.strip()
    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise LiveEvidenceError("provider content contained no JSON object")
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LiveEvidenceError("provider content was not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise LiveEvidenceError("provider content was not a JSON object")
    return parsed


class CallBudget:
    """Hard cap on physical provider calls for this run (exactly one).

    ``reserve`` must be invoked before any I/O; a second reservation raises so
    a coding error cannot silently produce a second billed call.
    """

    def __init__(self, limit: int = 1) -> None:
        self._limit = limit
        self.reserved = 0
        self.physical = 0

    def reserve(self) -> None:
        if self.reserved >= self._limit:
            raise LiveEvidenceError("provider call budget already reserved for this run")
        self.reserved += 1

    def record_physical(self) -> None:
        self.physical += 1
        if self.physical > self._limit:
            raise LiveEvidenceError("more than one physical provider call was made")


CANARY_CONTEXT = {"note": "public canary; contains no operational data"}


def build_context_facts(
    *, classification: Classification = Classification.PUBLIC, redaction: bool = True,
    minimization: bool = False, evidence: int = 1, tokens: int = 40,
) -> ContextFacts:
    return ContextFacts(
        classification=classification,
        redaction_applied=redaction,
        minimization_proven=minimization,
        evidence_count=evidence,
        estimated_input_tokens=tokens,
        context_digest=sha256_hex(canonical(CANARY_CONTEXT)),
    )


def build_budget_facts(**overrides) -> BudgetFacts:
    base = dict(
        per_request_token_limit=4000,
        daily_budget_usd_millis=1000,
        monthly_budget_usd_millis=10000,
        spent_today_usd_millis=0,
        spent_month_usd_millis=0,
        estimated_cost_usd_millis=1,
        on_budget_exceeded="hard_stop",
        kill_switch_enabled=True,
    )
    base.update(overrides)
    return BudgetFacts(**base)


def build_canary_request(model_id: str, **overrides) -> GatewayRequest:
    base = dict(
        task_type=CANARY_TASK_TYPE,
        ai_mode=AIMode.EXTERNAL_AI,
        provider_id=PROVIDER_ID,
        model_id=model_id,
        placement=Placement.EXTERNAL,
        context=CANARY_CONTEXT,
        output_schema=CANARY_SCHEMA,
        context_facts=build_context_facts(),
        budget_facts=build_budget_facts(),
        termination_facts=TerminationFacts(),
        timeout_seconds=60,
        max_output_tokens=200,
    )
    base.update(overrides)
    return GatewayRequest(**base)


def refusal_request(case: str, model_id: str) -> GatewayRequest:
    """Build the exact request shape for one mandated refusal case."""
    if case == "NO_AI":
        return build_canary_request(model_id, ai_mode=AIMode.NO_AI)
    if case == "NO_EVIDENCE":
        return build_canary_request(model_id, context_facts=build_context_facts(evidence=0))
    if case == "P4A1_INTERNAL_WITHOUT_MINIMIZATION":
        # Exactly P4-A1's current handoff truth: minimization NOT_PROVEN.
        return build_canary_request(
            model_id,
            context_facts=build_context_facts(
                classification=Classification.INTERNAL, minimization=False
            ),
        )
    if case == "RESTRICTED_EXTERNAL_PLACEMENT":
        return build_canary_request(
            model_id, context_facts=build_context_facts(classification=Classification.RESTRICTED)
        )
    if case == "BUDGET_EXCEEDED":
        return build_canary_request(
            model_id,
            budget_facts=build_budget_facts(daily_budget_usd_millis=10, spent_today_usd_millis=10),
        )
    if case == "KILL_SWITCH_ACTIVE":
        return build_canary_request(
            model_id,
            termination_facts=TerminationFacts(
                terminate_when=("kill_switch_active",), kill_switch_active=True
            ),
        )
    raise LiveEvidenceError(f"unknown refusal case: {case}")


def run_refusals(model_id: str, budget: CallBudget, provider_factory) -> list[dict]:
    """Every mandated refusal must produce zero physical provider attempts.

    ``provider_factory(budget)`` must return a fresh guard provider (one that
    raises if dispatched); it is injected so this module does not need to
    define provider classes itself.
    """
    results: list[dict] = []
    for case in REFUSAL_CASES:
        provider = provider_factory(budget)
        registry = ProviderRegistry()
        # A1-F3: register truthfully as EXTERNAL - the real placement this
        # evidence-only adapter is deployed at - matching every refusal
        # request's own declared placement built by build_canary_request().
        registry.register(provider, (model_id,), placement=Placement.EXTERNAL)
        gateway = AIGateway(registry, UsageLedger(), endpoint_origin=safe_origin(endpoint()))
        result = asyncio.run(gateway.execute(refusal_request(case, model_id)))
        results.append(
            {
                "case": case,
                "accepted": result.accepted,
                "reason_code": result.receipt.reason_code,
                "final_outcome": result.receipt.final_outcome.value,
                "provider_attempts": result.receipt.provider_attempts,
                "adapter_calls": provider.calls,
                "gateway_attempts": gateway.physical_attempts,
            }
        )
    return results
