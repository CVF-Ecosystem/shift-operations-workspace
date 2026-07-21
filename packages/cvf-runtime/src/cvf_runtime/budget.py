"""Cost / budget gate.

CVF control: ``cost``. Enforces cost-policy.yaml: per-request token limit and
daily/monthly spend caps, with ``on_budget_exceeded`` behaviour. Every AI task
must pass this gate before a provider call.

Runs and is tested now; it becomes load-bearing when an AI mode beyond NO_AI is
enabled (there is no provider call in NO_AI mode).
"""

from __future__ import annotations

from dataclasses import dataclass

from cvf_runtime.errors import CvfDenied


@dataclass(frozen=True)
class BudgetState:
    """Current spend, supplied by the caller (e.g. from a usage ledger)."""

    spent_today_usd: float = 0.0
    spent_month_usd: float = 0.0


def assert_within_budget(
    *,
    cost_policy: dict,
    state: BudgetState,
    requested_tokens: int,
) -> str:
    """Enforce token + spend caps.

    Returns the ``on_budget_exceeded`` action ("fallback_to_rules") instead of
    raising when a soft cap is hit, so the caller can degrade gracefully; a hard
    token overflow raises :class:`CvfDenied`.
    """
    token_limit = int(cost_policy.get("per_request_token_limit", 8000))
    if requested_tokens > token_limit:
        raise CvfDenied(
            control="cost",
            reason=f"request wants {requested_tokens} tokens; limit is {token_limit}",
            http_status=429,
        )

    daily_cap = float(cost_policy.get("default_daily_budget_usd", 0))
    monthly_cap = float(cost_policy.get("default_monthly_budget_usd", 0))
    over_daily = daily_cap and state.spent_today_usd >= daily_cap
    over_monthly = monthly_cap and state.spent_month_usd >= monthly_cap
    if over_daily or over_monthly:
        action = str(cost_policy.get("on_budget_exceeded", "fallback_to_rules"))
        if cost_policy.get("kill_switch_enabled") and action == "hard_stop":
            raise CvfDenied(
                control="cost", reason="budget exceeded; kill switch", http_status=429
            )
        return action  # e.g. "fallback_to_rules"
    return "ok"
