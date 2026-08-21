"""Deterministic rules fallback (SPEC R4).

When cost policy says ``fallback_to_rules`` instead of hard-stopping, the caller
still needs a typed answer that never involved a provider. The fallback is pure
and deterministic: it derives nothing from provider output and performs no I/O,
so a fallback result can never be mistaken for model output.
"""

from __future__ import annotations

from typing import Any

FALLBACK_MARKER = "rules_fallback"


def build_rules_fallback(task_type: str, reason_code: str) -> dict[str, Any]:
    """Return a deterministic, provider-free result body.

    The marker field makes it unambiguous downstream that no model produced
    this content.
    """
    return {
        FALLBACK_MARKER: True,
        "task_type": task_type,
        "reason_code": reason_code,
    }
