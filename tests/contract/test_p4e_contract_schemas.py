"""P4-E JSON Schema representation-parity tests (SPEC R20, AC-10): the
closed schemas mirror the pinned invariant matrices field-for-field, and
every real emitted receipt/result validates against its schema."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from identity_mapping.invariants import (
    emit_identity_resolution_result,
    emit_mapping_action_receipt,
)
from conversation_routing.invariants import emit_placement_decision

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "contracts"

IDENTITY_SCHEMA = json.loads((CONTRACTS_DIR / "identity" / "external-identity-mapping.schema.json").read_text())
PLACEMENT_SCHEMA = json.loads((CONTRACTS_DIR / "conversation" / "conversation-placement.schema.json").read_text())


def _validate(instance: dict, schema: dict) -> None:
    jsonschema.validate(instance=instance, schema=schema)


def test_mapping_applied_receipt_validates():
    receipt = emit_mapping_action_receipt(
        "APPLIED", action="PROPOSE", aggregate_id="m1", aggregate_version=1,
        audit_id="a1", command_application_count=1, audit_count=1, replayed=False,
    )
    _validate(receipt.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_mapping_replay_receipt_validates():
    receipt = emit_mapping_action_receipt(
        "IDEMPOTENT_REPLAY", action="CONFIRM", aggregate_id="m1", aggregate_version=2,
        audit_id="a1", command_application_count=0, audit_count=0, replayed=True,
    )
    _validate(receipt.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_mapping_refused_receipt_validates():
    receipt = emit_mapping_action_receipt(
        "REFUSED", action="CONFIRM", reason="SEPARATION_OF_DUTY",
        command_application_count=0, audit_count=0, replayed=False,
    )
    _validate(receipt.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_mapping_conflict_receipt_validates():
    receipt = emit_mapping_action_receipt(
        "CONFLICT", action="REVOKE", reason="VERSION_CONFLICT",
        command_application_count=0, audit_count=0, replayed=False,
    )
    _validate(receipt.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_identity_resolved_validates():
    result = emit_identity_resolution_result(
        "RESOLVED", mapping_id="m1", mapping_version=1, target_user_id="u1",
        external_key_digest="a" * 64, resolution_count=1,
    )
    _validate(result.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_identity_fallback_validates():
    result = emit_identity_resolution_result("FALLBACK", reason="NO_MAPPING", resolution_count=0)
    _validate(result.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_identity_refused_validates():
    result = emit_identity_resolution_result("REFUSED", reason="CORRUPT_STATE", resolution_count=0)
    _validate(result.model_dump(exclude_none=True), IDENTITY_SCHEMA)


def test_placement_placed_validates():
    decision = emit_placement_decision(
        "PLACED", decision_id="d1", proposal_id="p1", mapping_id="m1", binding_id="b1",
        target_kind="WORKSPACE", target_id="a" * 64, conversation_key="b" * 64,
        decision_count=1, work_complete=True,
    )
    _validate(decision.model_dump(exclude_none=True), PLACEMENT_SCHEMA)


def test_placement_fallback_validates():
    decision = emit_placement_decision(
        "FALLBACK", reason="NO_MAPPING", decision_id="d1", proposal_id="p1",
        decision_count=1, work_complete=True,
    )
    _validate(decision.model_dump(exclude_none=True), PLACEMENT_SCHEMA)


def test_placement_refused_validates():
    decision = emit_placement_decision(
        "REFUSED", reason="RETRY_EXHAUSTED", decision_id="d1", proposal_id="p1",
        decision_count=1, work_complete=True,
    )
    _validate(decision.model_dump(exclude_none=True), PLACEMENT_SCHEMA)


def test_placement_retry_pending_validates():
    decision = emit_placement_decision(
        "RETRY_PENDING", reason="CLAIM_RECOVERABLE", proposal_id="p1",
        decision_count=0, work_complete=False,
    )
    _validate(decision.model_dump(exclude_none=True), PLACEMENT_SCHEMA)


def test_placement_placed_with_extra_field_fails_schema():
    """SPEC R20: unknown fields fail closed."""
    with pytest.raises(jsonschema.ValidationError):
        _validate({
            "outcome": "PLACED", "decision_id": "d1", "proposal_id": "p1", "mapping_id": "m1",
            "binding_id": "b1", "target_kind": "WORKSPACE", "target_id": "a" * 64,
            "conversation_key": "b" * 64, "decision_count": 1, "work_complete": True,
            "unexpected_field": "x",
        }, PLACEMENT_SCHEMA)


def test_two_schemas_have_no_overlapping_definitions_by_accident():
    identity_defs = set(IDENTITY_SCHEMA["$defs"])
    placement_defs = set(PLACEMENT_SCHEMA["$defs"])
    assert identity_defs.isdisjoint(placement_defs - {"digest"})
