"""Termination gate.

CVF control: ``termination``. Enforces termination-policy.yaml: an AI task must
be terminated when any stop condition is met (timeout, token limit, repeated
failures, kill switch), and evidence must be preserved on termination.

Runs and is tested now; load-bearing when an AI mode beyond NO_AI is enabled.
"""

from __future__ import annotations

from dataclasses import dataclass

from cvf_runtime.errors import CvfDenied


@dataclass(frozen=True)
class TaskState:
    """Observed state of a running AI task, supplied by the caller."""

    elapsed_s: float = 0.0
    timeout_s: float = 0.0
    used_tokens: int = 0
    token_limit: int = 0
    consecutive_failures: int = 0
    schema_failures: int = 0
    kill_switch_active: bool = False


def should_terminate(cost_or_termination_policy: dict, state: TaskState) -> str | None:
    """Return the stop-condition name if the task must terminate, else None."""
    conditions = set(cost_or_termination_policy.get("terminate_when", []))
    if "timeout_exceeded" in conditions and state.timeout_s and state.elapsed_s >= state.timeout_s:
        return "timeout_exceeded"
    if "token_limit_exceeded" in conditions and state.token_limit and state.used_tokens >= state.token_limit:
        return "token_limit_exceeded"
    if "three_consecutive_failures" in conditions and state.consecutive_failures >= 3:
        return "three_consecutive_failures"
    if "schema_validation_repeatedly_fails" in conditions and state.schema_failures >= 3:
        return "schema_validation_repeatedly_fails"
    if "kill_switch_active" in conditions and state.kill_switch_active:
        return "kill_switch_active"
    return None


def assert_not_terminated(policy: dict, state: TaskState) -> None:
    """Raise :class:`CvfDenied` (preserving evidence intent) if a task must stop."""
    reason = should_terminate(policy, state)
    if reason is not None:
        raise CvfDenied(
            control="termination",
            reason=f"task terminated: {reason} (evidence preserved)",
            http_status=409,
        )
