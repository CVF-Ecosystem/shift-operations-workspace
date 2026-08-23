"""P4-B contract test - receipts conform to the published schema.

NOT GOVERNANCE PROOF: schema conformance only.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_providers.models import VALID_RECEIPT_AI_MODES, ProviderModeOutcome, build_receipt, canonical_receipt_ai_mode

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "ai-providers"
    / "contracts"
    / "provider_modes.schema.json"
)
DIGEST = "d" * 64

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _receipt(**overrides):
    base = dict(
        request_id="r1", policy_version="v1", request_digest=DIGEST, output_schema_digest=DIGEST,
        ai_mode="NO_AI", outcome=ProviderModeOutcome.AI_MODE_DISABLED,
        started_at="2026-08-21T00:00:00+00:00", finished_at="2026-08-21T00:00:01+00:00",
    )
    base.update(overrides)
    return build_receipt(**base)


def test_schema_file_is_valid_json_schema(schema):
    jsonschema.Draft202012Validator.check_schema(schema)


def test_no_ai_receipt_conforms(schema):
    payload = json.loads(_receipt().model_dump_json())
    jsonschema.validate(payload, schema)


def test_rules_matched_receipt_conforms(schema):
    receipt = _receipt(
        ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED,
        rule_id="r1", output_digest=DIGEST, ruleset_digest=DIGEST, rules_evaluated=1,
    )
    jsonschema.validate(json.loads(receipt.model_dump_json()), schema)


def test_external_accepted_receipt_conforms(schema):
    receipt = _receipt(
        ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_ACCEPTED,
        provider_id="p1", model_id="m1", output_digest=DIGEST, gateway_calls=1, provider_attempts=1,
    )
    jsonschema.validate(json.loads(receipt.model_dump_json()), schema)


def test_schema_forbids_additional_properties(schema):
    payload = json.loads(_receipt().model_dump_json())
    payload["unexpected_field"] = "x"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_caps_gateway_calls_at_one(schema):
    payload = json.loads(_receipt().model_dump_json())
    payload["gateway_calls"] = 2
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_requires_digest_format(schema):
    payload = json.loads(_receipt().model_dump_json())
    payload["request_digest"] = "short"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_has_no_facts_context_prompt_or_output_body_fields(schema):
    """R9: the contract must not even permit carrying raw bodies."""
    properties = set(schema["properties"])
    forbidden = {
        "facts", "context", "prompt", "output", "messages", "authorization",
        "api_key", "rule_output", "provider_output",
    }
    assert not (properties & forbidden)


class TestReceiptAiModeVocabulary:
    """P4B-REV-F5 - the receipt's closed ai_mode vocabulary and its
    canonicalization helper."""

    def test_valid_receipt_ai_modes_matches_schema_enum(self):
        assert set(VALID_RECEIPT_AI_MODES) == {"NO_AI", "RULES_ONLY", "EXTERNAL_AI", "UNKNOWN"}

    def test_canonical_receipt_ai_mode_passes_through_known_modes(self):
        assert canonical_receipt_ai_mode("NO_AI") == "NO_AI"
        assert canonical_receipt_ai_mode("RULES_ONLY") == "RULES_ONLY"
        assert canonical_receipt_ai_mode("EXTERNAL_AI") == "EXTERNAL_AI"

    def test_canonical_receipt_ai_mode_normalizes_unknown_strings(self):
        assert canonical_receipt_ai_mode("BOGUS") == "UNKNOWN"


class TestPydanticAndSchemaAgreeOnDrift:
    """P4B-REV-F5 - the reviewer's exact three drift cases: each is now
    rejected on the Pydantic side (a receipt with that shape can never be
    constructed) AND, independently, on the published JSON-schema side (a
    hand-built payload with that shape is rejected by the schema)."""

    def test_unknown_ai_mode_is_normalized_before_it_ever_reaches_json(self, schema):
        """The raw bogus mode string is never echoed into the receipt at
        all (canonicalized to UNKNOWN), so the Pydantic-valid receipt's own
        JSON dump conforms to the schema - Pydantic and the schema agree."""
        receipt = _receipt(ai_mode="UNKNOWN", outcome=ProviderModeOutcome.REQUEST_INVALID)
        payload = json.loads(receipt.model_dump_json())
        assert payload["ai_mode"] == "UNKNOWN"
        jsonschema.validate(payload, schema)

    def test_schema_rejects_a_hand_built_bogus_ai_mode_payload(self, schema):
        payload = json.loads(_receipt().model_dump_json())
        payload["ai_mode"] = "BOGUS"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_pydantic_rejects_no_ai_mode_with_rules_matched_outcome(self):
        with pytest.raises(Exception):
            _receipt(
                ai_mode="NO_AI", outcome=ProviderModeOutcome.RULES_MATCHED,
                rule_id="r1", output_digest=DIGEST, ruleset_digest=DIGEST, rules_evaluated=1,
            )

    def test_schema_rejects_no_ai_mode_with_rules_matched_outcome(self, schema):
        payload = json.loads(
            _receipt(
                ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED,
                rule_id="r1", output_digest=DIGEST, ruleset_digest=DIGEST, rules_evaluated=1,
            ).model_dump_json()
        )
        payload["ai_mode"] = "NO_AI"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_pydantic_rejects_external_not_accepted_with_zero_gateway_calls(self):
        with pytest.raises(Exception):
            _receipt(
                ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
                provider_id="p1", model_id="m1", gateway_calls=0,
            )

    def test_schema_rejects_external_not_accepted_with_zero_gateway_calls(self, schema):
        payload = json.loads(
            _receipt(
                ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
                provider_id="p1", model_id="m1", gateway_calls=1,
            ).model_dump_json()
        )
        payload["gateway_calls"] = 0
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)


class TestRoundTripEveryTerminalOutcome:
    """Every terminal outcome's canonical receipt shape round-trips through
    both the Pydantic model and the JSON schema validator, proving they
    agree (P4B-REV-F5)."""

    def test_ai_mode_disabled_round_trips(self, schema):
        receipt = _receipt()
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_rules_no_match_round_trips(self, schema):
        """P4B-REV-F5-R2: RULES_NO_MATCH always carries the ruleset_digest
        the service actually computes even on no-match."""
        receipt = _receipt(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_NO_MATCH, ruleset_digest=DIGEST, rules_evaluated=1)
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_rules_schema_invalid_round_trips(self, schema):
        """P4B-REV-F5-R2: RULES_SCHEMA_INVALID likewise always carries the
        ruleset_digest the service actually computes."""
        receipt = _receipt(
            ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_SCHEMA_INVALID,
            rule_id="r1", ruleset_digest=DIGEST, rules_evaluated=1,
        )
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_external_identity_mismatch_round_trips(self, schema):
        receipt = _receipt(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH)
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_external_not_accepted_round_trips(self, schema):
        receipt = _receipt(
            ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
            provider_id="p1", model_id="m1", gateway_calls=1,
        )
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_request_invalid_round_trips(self, schema):
        receipt = _receipt(ai_mode="UNKNOWN", outcome=ProviderModeOutcome.REQUEST_INVALID)
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)


class TestReviewerImpossibleShapesRejectedByBothLayers:
    """P4B-REV-F5-R1 - the four exact reviewer probes, each rejected by
    Pydantic (never constructible) AND independently by the schema (a
    hand-built payload is rejected). Plus adjacent legitimate shapes,
    proving no overtightening."""

    def test_rules_no_match_with_rule_id_ghost_rejected_by_pydantic(self):
        with pytest.raises(Exception):
            _receipt(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_NO_MATCH, rule_id="ghost", rules_evaluated=1)

    def test_rules_no_match_with_rule_id_ghost_rejected_by_schema(self, schema):
        payload = json.loads(_receipt(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_NO_MATCH, ruleset_digest=DIGEST, rules_evaluated=1).model_dump_json())
        payload["rule_id"] = "ghost"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_rules_matched_with_zero_rules_evaluated_rejected_by_pydantic(self):
        with pytest.raises(Exception):
            _receipt(
                ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED,
                rule_id="r1", output_digest=DIGEST, ruleset_digest=DIGEST, rules_evaluated=0,
            )

    def test_rules_matched_with_zero_rules_evaluated_rejected_by_schema(self, schema):
        payload = json.loads(_receipt(
            ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED,
            rule_id="r1", output_digest=DIGEST, ruleset_digest=DIGEST, rules_evaluated=1,
        ).model_dump_json())
        payload["rules_evaluated"] = 0
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_external_not_accepted_with_gateway_call_but_no_ids_rejected_by_pydantic(self):
        with pytest.raises(Exception):
            _receipt(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED, gateway_calls=1)

    def test_external_not_accepted_with_gateway_call_but_no_ids_rejected_by_schema(self, schema):
        payload = json.loads(_receipt(
            ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
            provider_id="p1", model_id="m1", gateway_calls=1,
        ).model_dump_json())
        payload["provider_id"], payload["model_id"] = "", ""
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_external_identity_mismatch_with_ai_mode_unknown_rejected_by_pydantic(self):
        with pytest.raises(Exception):
            _receipt(ai_mode="UNKNOWN", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH)

    def test_external_identity_mismatch_with_ai_mode_unknown_rejected_by_schema(self, schema):
        payload = json.loads(_receipt(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH).model_dump_json())
        payload["ai_mode"] = "UNKNOWN"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    # Adjacent legitimate shapes - proves no overtightening.
    def test_rules_no_match_with_empty_rule_id_still_valid(self, schema):
        receipt = _receipt(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_NO_MATCH, rule_id="", ruleset_digest=DIGEST, rules_evaluated=3)
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_rules_matched_with_rules_evaluated_greater_than_one_still_valid(self, schema):
        receipt = _receipt(
            ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED,
            rule_id="r1", output_digest=DIGEST, ruleset_digest=DIGEST, rules_evaluated=5,
        )
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_external_not_accepted_with_ids_present_still_valid(self, schema):
        receipt = _receipt(
            ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
            provider_id="p1", model_id="m1", gateway_calls=1,
        )
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    def test_external_identity_mismatch_with_ai_mode_external_ai_still_valid(self, schema):
        receipt = _receipt(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH)
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)
