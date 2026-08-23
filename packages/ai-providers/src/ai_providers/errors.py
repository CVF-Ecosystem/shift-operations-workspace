"""Typed P4-B provider-mode errors and their stable reason codes (SPEC R2/R9).

Every error carries a fixed ``reason_code`` so receipts and tests can assert
an outcome without parsing prose. No error message may ever embed facts,
context, rule output, a prompt, provider output, a credential, or raw
exception text - callers build messages from safe identifiers only.

Also hosts the bounded-JSON validation helpers (SPEC R4) other ``ai_providers``
modules import: this is a leaf module with zero internal project imports, so
it is the one dependency-cycle-free home for a helper every model/rule/mock
module needs (``models.py``, ``rules_only.py``, ``mock_provider.py``).
"""

from __future__ import annotations

import math
from typing import Any

MAX_JSON_DEPTH = 8
MAX_CONTAINER_ITEMS = 100
MAX_JSON_BYTES = 16 * 1024

_PRIMITIVE_TYPES = (str, int, float, bool, type(None))


def _canonical_json(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _depth_of(value: Any) -> int:
    if isinstance(value, dict):
        return 1 + max((_depth_of(v) for v in value.values()), default=0)
    if isinstance(value, list):
        return 1 + max((_depth_of(v) for v in value), default=0)
    return 0


def assert_bounded_json(value: Any, *, label: str) -> None:
    """Fail closed unless ``value`` is a bounded JSON-only structure (R4).

    Every nested container must be a plain ``dict``/``list`` (never a tuple,
    set, or class instance masquerading as one); every leaf must be a plain
    JSON primitive, and any float must be finite (P4B-REV-F4.3 - JSON has no
    NaN/Infinity/-Infinity representation). Depth, per-container item count,
    and total canonical-JSON byte size are all bounded so a caller cannot
    smuggle unbounded content into a rule fact or a rule/output body.
    """
    _assert_json_only(value, label=label)
    if _depth_of(value) > MAX_JSON_DEPTH:
        raise ValueError(f"{label}: exceeds maximum JSON depth {MAX_JSON_DEPTH}")
    _assert_container_bounds(value, label=label)
    size = len(_canonical_json(value).encode("utf-8"))
    if size > MAX_JSON_BYTES:
        raise ValueError(f"{label}: canonical JSON exceeds {MAX_JSON_BYTES} bytes")


def _assert_json_only(value: Any, *, label: str) -> None:
    if isinstance(value, dict):
        if type(value) is not dict:
            raise ValueError(f"{label}: mapping must be a plain dict")
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(f"{label}: mapping keys must be plain str")
            _assert_json_only(item, label=label)
        return
    if isinstance(value, list):
        if type(value) is not list:
            raise ValueError(f"{label}: sequence must be a plain list")
        for item in value:
            _assert_json_only(item, label=label)
        return
    if type(value) not in _PRIMITIVE_TYPES:
        raise ValueError(f"{label}: value must be a JSON primitive or container")
    if type(value) is float and not math.isfinite(value):
        raise ValueError(f"{label}: non-finite float (NaN/Infinity) is not a JSON primitive")


def _assert_container_bounds(value: Any, *, label: str) -> None:
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError(f"{label}: object exceeds {MAX_CONTAINER_ITEMS} keys")
        for item in value.values():
            _assert_container_bounds(item, label=label)
    elif isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError(f"{label}: array exceeds {MAX_CONTAINER_ITEMS} items")
        for item in value:
            _assert_container_bounds(item, label=label)


def assert_receipt_grammar(
    *,
    outcome_value: str,
    ai_mode: str,
    provider_id: str,
    model_id: str,
    rule_id: str,
    output_digest: str,
    ruleset_digest: str,
    rules_evaluated: int,
    gateway_calls: int,
    provider_attempts: int,
) -> None:
    """P4B-REV-F5/F5-R1/F5-R2 exact cross-field receipt grammar (SPEC R9).
    Lives here (leaf module, no internal imports) so ``ProviderModeReceiptV1``
    stays under the file-size guard; takes the outcome's plain ``.value``
    string to avoid an import cycle back into ``models.py``.

    P4B-REV-F5-R2: one complete GENERAL grammar derived from the real
    outcome taxonomy (``models.py::ProviderModeOutcome``) and the real
    emission sites in ``service.py`` - not a growing list of probe-specific
    shape rejections. Every branch is keyed off an outcome-FAMILY predicate
    (``is_external``/``is_rules``/etc.), so a new outcome in the same family
    automatically inherits its rules instead of silently passing unchecked:

    - Every ``EXTERNAL_*`` outcome carries ZERO rule facts/counters - rules
      and external are mutually exclusive paths (``_finish_rules_only`` vs.
      ``_finish_external_ai``) and must never mix.
    - A non-accepted external outcome never carries ``output_digest`` - only
      an accepted call could have produced output.
    - Every ``RULES_*`` outcome REQUIRES the ``ruleset_digest``
      ``_finish_rules_only`` always computes, and forbids provider/model
      ids and gateway/provider calls.
    - ``RULES_MATCHED``/``RULES_SCHEMA_INVALID`` require ``rule_id`` +
      ``rules_evaluated >= 1``; ``RULES_NO_MATCH`` forbids ``rule_id``. Only
      a match carries ``output_digest``.
    - ``EXTERNAL_IDENTITY_MISMATCH``'s provider/model ids are both-present-
      or-both-absent as a pair, and it is zero-call.
    - A genuine gateway attempt (accepted/not-accepted) requires exactly
      one call and both ids recorded; an accepted one also has output.
    - Zero-work refusals require zero counters and no facts at all.
    """

    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise ValueError(message)

    o = outcome_value
    is_external = o.startswith("EXTERNAL_")
    is_rules = o.startswith("RULES_")
    rule_matched = o in ("RULES_MATCHED", "RULES_SCHEMA_INVALID")
    accepted_external = o == "EXTERNAL_ACCEPTED"
    gateway_attempted = o in ("EXTERNAL_ACCEPTED", "EXTERNAL_NOT_ACCEPTED")
    no_facts = not (rule_id or output_digest or ruleset_digest or provider_id or model_id)

    expected_ai_mode = {"AI_MODE_DISABLED": "NO_AI", "REQUEST_INVALID": "UNKNOWN"}.get(o) or (
        "RULES_ONLY" if is_rules else "EXTERNAL_AI" if is_external else None
    )
    if expected_ai_mode is not None:
        _require(ai_mode == expected_ai_mode, f"{o} requires ai_mode={expected_ai_mode}")

    # Rule 1: EXTERNAL_* and RULES_* are mutually exclusive fact families -
    # an EXTERNAL_* outcome never carries a rule fact/counter (P4B-REV-F5-R2:
    # closes rule_id/ruleset_digest/rules_evaluated leaking onto
    # EXTERNAL_IDENTITY_MISMATCH and EXTERNAL_ACCEPTED).
    if is_external:
        _require(rules_evaluated == 0, f"{o} must carry zero rules_evaluated")
        _require(not rule_id, f"{o} must carry no rule_id")
        _require(not ruleset_digest, f"{o} must carry no ruleset_digest")

    # Rule 2: a non-accepted external outcome never carries output (closes
    # output_digest leaking onto EXTERNAL_IDENTITY_MISMATCH/NOT_ACCEPTED).
    if is_external and not accepted_external:
        _require(not output_digest, f"{o} must carry no output_digest")

    # Rule 3: every RULES_* outcome requires the always-computed ruleset
    # digest (closes RULES_NO_MATCH/RULES_SCHEMA_INVALID omitting it) and
    # forbids gateway/provider facts.
    if is_rules:
        _require(bool(ruleset_digest), f"{o} requires a non-null ruleset_digest")
        _require((gateway_calls, provider_attempts) == (0, 0), f"{o} requires zero gateway/provider calls")
        _require(not (provider_id or model_id), f"{o} must carry no provider/model id")

    # Rule 4: matched/schema-invalid require the rule_id + positive count;
    # no-match forbids rule_id; only a match ever carries output.
    if rule_matched:
        _require(bool(rule_id), f"{o} requires the matched/offending rule_id")
        _require(rules_evaluated >= 1, f"{o} requires rules_evaluated >= 1")
    if o == "RULES_NO_MATCH":
        _require(not rule_id, "RULES_NO_MATCH must carry no rule_id")
    if o in ("RULES_NO_MATCH", "RULES_SCHEMA_INVALID"):
        _require(not output_digest, f"{o} must carry no output_digest")
    if o == "RULES_MATCHED":
        _require(bool(output_digest), "RULES_MATCHED requires an output_digest")

    # Rule 5: identity-mismatch provider/model facts are both-present-or-
    # both-absent as a pair, and zero-call.
    if o == "EXTERNAL_IDENTITY_MISMATCH":
        _require(bool(provider_id) == bool(model_id), f"{o} requires provider_id and model_id both present or both absent")
        _require((gateway_calls, provider_attempts) == (0, 0), f"{o} requires zero gateway/provider calls")

    # Rule 6: a genuine gateway attempt requires exactly one call and both
    # identity facts recorded; an accepted one additionally has output and,
    # since acceptance is only reachable after a real physical dispatch
    # (P4B-REV-F5-R3), requires exactly one provider attempt too.
    # EXTERNAL_NOT_ACCEPTED stays untightened here - it may be refused
    # before or after the physical attempt, so provider_attempts may be
    # either 0 or 1 for that outcome.
    if gateway_attempted:
        _require(gateway_calls == 1, f"{o} requires exactly one gateway call")
        _require(bool(provider_id and model_id), f"{o} requires provider_id and model_id")
    if accepted_external:
        _require(bool(output_digest), "EXTERNAL_ACCEPTED requires an output_digest")
        _require(provider_attempts == 1, "EXTERNAL_ACCEPTED requires exactly one provider attempt")

    # Rule 7: zero-work refusals carry zero counters and no facts at all.
    if o in ("AI_MODE_DISABLED", "REQUEST_INVALID"):
        _require((rules_evaluated, gateway_calls, provider_attempts) == (0, 0, 0), f"{o} requires zero rules/gateway/provider counters")
        _require(no_facts, f"{o} must carry no rule/output/provider/model facts")


class ProviderModeError(RuntimeError):
    """Base class. ``reason_code`` is the stable, assertable outcome name."""

    reason_code = "PROVIDER_MODE_ERROR"

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail or self.reason_code)
        self.detail = detail


class RequestInvalidError(ProviderModeError):
    """The strict request failed validation, or declared an unknown mode."""

    reason_code = "REQUEST_INVALID"


class DuplicateRuleIdError(ProviderModeError):
    """Two rules in one immutable rule set share the same ``rule_id`` (R5)."""

    reason_code = "DUPLICATE_RULE_ID"


class AmbiguousRuleSignatureError(ProviderModeError):
    """Two rules share the same ``(task_type, priority, required_facts)``
    signature, so winner order could not be made deterministic (SPEC R5)."""

    reason_code = "AMBIGUOUS_RULE_SIGNATURE"


class RulesSchemaInvalidError(ProviderModeError):
    """A winning rule's output failed the real output-schema validator; the
    execution must not fall through to external AI (SPEC R5)."""

    reason_code = "RULES_SCHEMA_INVALID"


class ExternalIdentityMismatchError(ProviderModeError):
    """The nested ``GatewayRequest``'s task/mode/provider/model/placement/
    schema/digests do not match the outer request (SPEC R6). Zero-call."""

    reason_code = "EXTERNAL_IDENTITY_MISMATCH"


class MockAuthorizationInvalidError(ProviderModeError):
    """A mock adapter construction lacked, or supplied an invalid, explicit
    ``TEST_ONLY_COMPONENT_TEST``/``evidence_eligible=False`` authorization
    (SPEC R7)."""

    reason_code = "MOCK_AUTHORIZATION_INVALID"


class ProviderNotRegisteredError(ProviderModeError):
    """The provider/model id is not explicitly registered (SPEC R8)."""

    reason_code = "PROVIDER_NOT_REGISTERED"


class DuplicateProviderRegistrationError(ProviderModeError):
    """A provider id is already registered with different metadata, or a
    mock is registered without explicit ``allow_test_only=True`` (SPEC R8)."""

    reason_code = "DUPLICATE_PROVIDER_REGISTRATION"


__all__ = [
    "ProviderModeError",
    "RequestInvalidError",
    "DuplicateRuleIdError",
    "AmbiguousRuleSignatureError",
    "RulesSchemaInvalidError",
    "ExternalIdentityMismatchError",
    "MockAuthorizationInvalidError",
    "ProviderNotRegisteredError",
    "DuplicateProviderRegistrationError",
    "MAX_JSON_DEPTH",
    "MAX_CONTAINER_ITEMS",
    "MAX_JSON_BYTES",
    "assert_bounded_json",
    "assert_receipt_grammar",
]
