"""``RULES_ONLY`` mode (SPEC R4/R5): deterministic local rule evaluation.

``RuleSetV1`` is immutable once constructed: duplicate ``rule_id``s and
duplicate ``(task_type, priority, required_facts)`` signatures both fail at
construction time, never at match time, so an ambiguous rule set can never
even exist to be evaluated against. ``evaluate_rules`` never calls a gateway
or provider - it does not accept either as a parameter - and validates a
winning rule's output against the request schema using the real
``ai_gateway.validation.validate_output`` function before releasing it.
"""

from __future__ import annotations

import copy
from typing import Any

from ai_gateway.errors import OutputSchemaError
from ai_gateway.validation import validate_output

from .errors import AmbiguousRuleSignatureError, DuplicateRuleIdError
from .models import ProviderModeOutcome, RuleDefinitionV1


class RuleSetV1:
    """An immutable, deterministically ordered collection of rules (R5).

    Construction is the sole place ambiguity is rejected: every rule's
    ``rule_id`` must be unique, and every rule's ``(task_type, priority,
    required_facts)`` signature must be unique, so two rules can never tie
    for the same match with no way to break the tie.
    """

    def __init__(self, rules: tuple[RuleDefinitionV1, ...]) -> None:
        seen_ids: set[str] = set()
        seen_signatures: set[tuple[str, int, str]] = set()
        for rule in rules:
            if rule.rule_id in seen_ids:
                raise DuplicateRuleIdError(f"duplicate rule_id: {rule.rule_id}")
            seen_ids.add(rule.rule_id)
            signature = rule.signature()
            if signature in seen_signatures:
                raise AmbiguousRuleSignatureError(
                    f"ambiguous (task_type, priority, required_facts) signature: {rule.rule_id}"
                )
            seen_signatures.add(signature)
        self._rules = rules

    @property
    def rules(self) -> tuple[RuleDefinitionV1, ...]:
        return self._rules

    def digest_source(self) -> tuple[dict[str, Any], ...]:
        """A deterministic, order-stable dump usable to compute a ruleset
        digest for receipts - callers own hashing, this method only fixes
        the exact ordering/content contract."""
        ordered = sorted(self._rules, key=lambda r: (r.task_type, -r.priority, r.rule_id))
        return tuple(r.model_dump(mode="python") for r in ordered)


def _facts_match(rule: RuleDefinitionV1, facts: dict[str, Any]) -> bool:
    """Exact scalar equality for every required fact; no partial/prefix
    match, and a missing fact never matches (SPEC R4).

    P4B-REV-F4.4: equality alone is not exact-scalar matching in Python,
    because ``True == 1`` and ``False == 0``. A required fact must also
    match by exact runtime type, so a JSON boolean can never satisfy an
    integer (or vice versa) required fact.
    """
    for key, expected in rule.required_facts.items():
        if key not in facts:
            return False
        actual = facts[key]
        if type(actual) is not type(expected) or actual != expected:
            return False
    return True


def select_winner(
    rule_set: RuleSetV1, *, task_type: str, facts: dict[str, Any]
) -> RuleDefinitionV1 | None:
    """Return the winning rule by ``(-priority, rule_id)`` order, or
    ``None`` when no eligible rule matches (SPEC R4)."""
    eligible = [
        rule
        for rule in rule_set.rules
        if rule.task_type == task_type and _facts_match(rule, facts)
    ]
    if not eligible:
        return None
    eligible.sort(key=lambda r: (-r.priority, r.rule_id))
    return eligible[0]


def evaluate_rules(
    rule_set: RuleSetV1, *, task_type: str, facts: dict[str, Any], output_schema: dict[str, Any]
) -> tuple[ProviderModeOutcome, str, RuleDefinitionV1 | None, dict[str, Any] | None]:
    """Evaluate ``rule_set`` once and return ``(outcome, rule_id, rule,
    output)``. Never calls a gateway or provider (R4). A winning rule's
    output is deep-copy isolated and validated against ``output_schema``
    using the real gateway validator before being released; invalid output
    yields ``RULES_SCHEMA_INVALID`` and never falls through to external AI
    (R5)."""
    winner = select_winner(rule_set, task_type=task_type, facts=facts)
    if winner is None:
        return ProviderModeOutcome.RULES_NO_MATCH, "", None, None

    isolated_output = copy.deepcopy(winner.output)
    try:
        validate_output(isolated_output, output_schema)
    except OutputSchemaError:
        return ProviderModeOutcome.RULES_SCHEMA_INVALID, winner.rule_id, winner, None

    return ProviderModeOutcome.RULES_MATCHED, winner.rule_id, winner, isolated_output


__all__ = ["RuleSetV1", "select_winner", "evaluate_rules"]
