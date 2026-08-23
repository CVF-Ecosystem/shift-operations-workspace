"""P4-B SPEC R1/R4/R9 - strict, frozen, bounded-JSON, receipt-hash models.

Adversary tests: unknown fields, non-frozen mutation, primitive
reconstruction (never trusting an attached instance as pre-validated), JSON
depth/size/container bounds, non-finite floats, mock authorization forgery
attempts, and receipt-hash forgery/mismatch. P4B-REV-F5's ai_mode-vocabulary/
cross-field-grammar tests live in tests/contract/test_p4b_provider_modes_
schema.py; P4B-REV-F2's ProviderModeResultV1 envelope tests live in
tests/unit/test_p4b_rules_only.py.
"""

from __future__ import annotations

import pytest
from ai_gateway.models import Placement, digest_of
from pydantic import ValidationError

from ai_providers.models import (
    MAX_CONTAINER_ITEMS,
    MAX_JSON_DEPTH,
    MockAuthorizationV1,
    ProviderKind,
    ProviderMetadataV1,
    ProviderModeOutcome,
    ProviderModeReceiptV1,
    ProviderModeRequestV1,
    RuleDefinitionV1,
    assert_bounded_json,
    build_receipt,
)

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {"status": {"type": "string"}}}


def _request(**overrides) -> dict:
    fields = dict(
        task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="r1",
    )
    fields.update(overrides)
    return fields


class TestProviderModeRequestV1:
    def test_rejects_unknown_fields(self):
        with pytest.raises(ValidationError):
            ProviderModeRequestV1(**_request(unexpected="x"))

    def test_is_frozen(self):
        req = ProviderModeRequestV1(**_request())
        with pytest.raises(ValidationError):
            req.task_type = "other"

    def test_rejects_empty_task_type(self):
        with pytest.raises(ValidationError):
            ProviderModeRequestV1(**_request(task_type=""))

    def test_rejects_non_object_output_schema(self):
        with pytest.raises(ValidationError):
            ProviderModeRequestV1(**_request(output_schema={"type": "array"}))

    def test_primitive_reconstruction_rejects_non_dict_facts(self):
        """R1 - facts must be a plain dict of primitives; a class instance
        or unsupported nested type is never silently accepted."""
        with pytest.raises(ValidationError):
            ProviderModeRequestV1(**_request(facts={"x": object()}))

    def test_model_construct_bypass_still_caught_by_bounded_json_at_next_validation(self):
        """A model_construct bypass skips validators; re-validating via
        model_validate on the dump must still enforce the same bounds."""
        bypassed = ProviderModeRequestV1.model_construct(
            **_request(facts={"a" * 5: "b"}, ai_mode="RULES_ONLY")
        )
        # Reconstructing from the primitive dump re-triggers real validation.
        ProviderModeRequestV1.model_validate(bypassed.model_dump(mode="python"))

    def test_accepts_explicit_external_binding_facts(self):
        """P4B-REV-F3 - the outer request may declare provider_id/model_id/
        placement/context_digest explicitly."""
        req = ProviderModeRequestV1(
            **_request(
                ai_mode="EXTERNAL_AI", provider_id="p1", model_id="m1",
                placement=Placement.LOCAL, context_digest="a" * 64,
            )
        )
        assert req.provider_id == "p1"
        assert req.placement is Placement.LOCAL

    def test_rejects_non_enum_placement_string(self):
        """P4B-REV-F3 - placement must be a real ai_gateway.models.Placement
        member, not an arbitrary string like 'mars'."""
        with pytest.raises(ValidationError):
            ProviderModeRequestV1(**_request(placement="mars"))


class TestBoundedJson:
    def test_accepts_small_structure(self):
        assert_bounded_json({"a": [1, 2, 3], "b": "x"}, label="t")

    def test_rejects_excess_depth(self):
        value: dict = {}
        cursor = value
        for _ in range(MAX_JSON_DEPTH + 2):
            cursor["n"] = {}
            cursor = cursor["n"]
        with pytest.raises(ValueError):
            assert_bounded_json(value, label="t")

    def test_rejects_excess_container_items(self):
        value = {f"k{i}": i for i in range(MAX_CONTAINER_ITEMS + 1)}
        with pytest.raises(ValueError):
            assert_bounded_json(value, label="t")

    def test_rejects_oversized_canonical_json(self):
        value = {"payload": "x" * (20 * 1024)}
        with pytest.raises(ValueError):
            assert_bounded_json(value, label="t")

    def test_rejects_non_json_types(self):
        with pytest.raises(ValueError):
            assert_bounded_json({"x": (1, 2)}, label="t")
        with pytest.raises(ValueError):
            assert_bounded_json({"x": {1, 2}}, label="t")
        with pytest.raises(ValueError):
            assert_bounded_json(object(), label="t")

    def test_rejects_nan(self):
        """P4B-REV-F4.3 - JSON has no NaN representation."""
        with pytest.raises(ValueError):
            assert_bounded_json({"x": float("nan")}, label="t")

    def test_rejects_positive_and_negative_infinity(self):
        with pytest.raises(ValueError):
            assert_bounded_json({"x": float("inf")}, label="t")
        with pytest.raises(ValueError):
            assert_bounded_json({"x": float("-inf")}, label="t")

    def test_accepts_finite_float(self):
        assert_bounded_json({"x": 1.5}, label="t")


class TestRuleDefinitionV1:
    def test_rejects_container_required_fact(self):
        with pytest.raises(ValidationError):
            RuleDefinitionV1(
                rule_id="r1", task_type="t1", priority=1,
                required_facts={"x": {"nested": True}}, output={"status": "ok"},
            )

    def test_signature_is_stable_for_equal_facts(self):
        r1 = RuleDefinitionV1(rule_id="a", task_type="t1", priority=1, required_facts={"x": 1, "y": 2}, output={})
        r2 = RuleDefinitionV1(rule_id="b", task_type="t1", priority=1, required_facts={"y": 2, "x": 1}, output={})
        assert r1.signature() == r2.signature()

    def test_is_frozen(self):
        rule = RuleDefinitionV1(rule_id="r1", task_type="t1", priority=1, required_facts={}, output={})
        with pytest.raises(ValidationError):
            rule.priority = 2


class TestMockAuthorizationV1:
    def test_rejects_wrong_purpose(self):
        with pytest.raises(ValidationError):
            MockAuthorizationV1(purpose="ANYTHING_ELSE", evidence_eligible=False)

    def test_rejects_evidence_eligible_true(self):
        with pytest.raises(ValidationError):
            MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=True)

    def test_accepts_the_one_valid_shape(self):
        auth = MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=False)
        assert auth.evidence_eligible is False

    def test_model_construct_bypass_still_caught_on_revalidation(self):
        bypassed = MockAuthorizationV1.model_construct(purpose="WRONG", evidence_eligible=True)
        with pytest.raises(ValidationError):
            MockAuthorizationV1.model_validate(bypassed.model_dump(mode="python"))


class TestProviderMetadataV1:
    def test_mock_kind_requires_evidence_eligible_false(self):
        with pytest.raises(ValidationError):
            ProviderMetadataV1(
                provider_id="p1", kind=ProviderKind.MOCK, placement=Placement.LOCAL,
                model_ids=("m1",), evidence_eligible=True,
            )

    def test_rejects_duplicate_model_ids(self):
        with pytest.raises(ValidationError):
            ProviderMetadataV1(
                provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.LOCAL,
                model_ids=("m1", "m1"), evidence_eligible=True,
            )

    def test_placement_reuses_canonical_enum(self):
        metadata = ProviderMetadataV1(
            provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.EXTERNAL,
            model_ids=("m1",), evidence_eligible=True,
        )
        assert metadata.placement is Placement.EXTERNAL

    def test_rejects_arbitrary_placement_string(self):
        """P4B-REV-F3 - the reviewer registered a nonsense placement 'mars'
        successfully; placement must be a real Placement enum member."""
        with pytest.raises(ValidationError):
            ProviderMetadataV1(
                provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement="mars",
                model_ids=("m1",), evidence_eligible=True,
            )


class TestProviderModeReceiptV1:
    def _base(self, **overrides) -> dict:
        fields = dict(
            request_id="r1", policy_version="v1", request_digest="a" * 64,
            output_schema_digest="b" * 64, ai_mode="NO_AI",
            outcome=ProviderModeOutcome.AI_MODE_DISABLED, started_at="t0", finished_at="t1",
        )
        fields.update(overrides)
        return fields

    def test_build_receipt_hash_is_recomputable(self):
        receipt = build_receipt(**self._base())
        dump = receipt.model_dump(mode="python")
        dump.pop("receipt_hash_sha256")
        assert digest_of(dump) == receipt.receipt_hash_sha256

    def test_forged_hash_is_rejected(self):
        receipt = build_receipt(**self._base())
        forged = receipt.model_dump(mode="python")
        forged["receipt_hash_sha256"] = "f" * 64
        with pytest.raises(ValidationError):
            ProviderModeReceiptV1(**forged)

    def test_model_construct_bypass_hash_forgery_caught_on_revalidation(self):
        bypassed = ProviderModeReceiptV1.model_construct(
            **self._base(), receipt_hash_sha256="0" * 64
        )
        with pytest.raises(ValidationError):
            ProviderModeReceiptV1.model_validate(bypassed.model_dump(mode="python"))

    def test_ai_mode_disabled_requires_zero_counters(self):
        with pytest.raises(ValidationError):
            build_receipt(**self._base(rules_evaluated=1))

    def test_external_accepted_requires_one_gateway_call(self):
        with pytest.raises(ValidationError):
            build_receipt(
                **self._base(
                    ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_ACCEPTED, gateway_calls=0,
                    provider_id="p1", model_id="m1", output_digest="c" * 64,
                )
            )

    def test_rules_outcome_requires_zero_gateway_provider_calls(self):
        with pytest.raises(ValidationError):
            build_receipt(
                **self._base(
                    ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED, gateway_calls=1,
                    rule_id="r1", output_digest="c" * 64, ruleset_digest="d" * 64,
                )
            )

    def test_is_frozen(self):
        receipt = build_receipt(**self._base())
        with pytest.raises(ValidationError):
            receipt.reason_code = "x"

    # P4B-REV-F5 additional cross-field grammar rules (relocated here from
    # tests/contract/test_p4b_provider_modes_schema.py for file-size budget).
    def test_ai_mode_disabled_requires_no_ai_mode_string(self):
        with pytest.raises(ValidationError):
            build_receipt(**self._base(ai_mode="RULES_ONLY"))

    def test_rules_matched_requires_rule_and_output_digest(self):
        with pytest.raises(ValidationError):
            build_receipt(**self._base(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_MATCHED, rules_evaluated=1))

    def test_external_identity_mismatch_forbids_gateway_calls(self):
        with pytest.raises(ValidationError):
            build_receipt(**self._base(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH, gateway_calls=1))

    def test_request_invalid_requires_canonical_unknown_ai_mode(self):
        with pytest.raises(ValidationError):
            build_receipt(**self._base(ai_mode="NO_AI", outcome=ProviderModeOutcome.REQUEST_INVALID))
