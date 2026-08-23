"""``NO_AI`` mode (SPEC R3): the zero-call refusal.

``evaluate_no_ai`` never resolves a provider and never evaluates a rule, even
when a rule set or gateway were supplied to the caller elsewhere - it does
not accept either as a parameter at all, so there is structurally nothing to
call. It exists as its own module (rather than an inline branch in
``service.py``) so a dependency-boundary test can assert this exact function
is the one and only NO_AI call site.
"""

from __future__ import annotations

from .models import ProviderModeOutcome


def evaluate_no_ai() -> tuple[ProviderModeOutcome, str]:
    """Return the fixed ``(AI_MODE_DISABLED, "")`` outcome/reason pair.

    Takes no arguments on purpose: a caller cannot pass rules or a gateway
    into this function even by mistake, so NO_AI can never be made to
    evaluate anything.
    """
    return ProviderModeOutcome.AI_MODE_DISABLED, ""


__all__ = ["evaluate_no_ai"]
