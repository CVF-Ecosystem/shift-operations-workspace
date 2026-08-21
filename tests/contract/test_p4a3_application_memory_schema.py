"""P4-A3 contract test - receipts and entries conform to the JSON schema.

NOT GOVERNANCE PROOF: schema conformance only. The receipt produced by a real
run is validated against this same schema by the evidence runner.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from application_memory.models import (
    MemoryClassification,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryOperation,
    MemoryPurpose,
    TombstoneReason,
)
from application_memory.receipts import MemoryReceiptV1, build_receipt

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "application-memory"
    / "contracts"
    / "application_memory.schema.json"
)
NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
DIGEST = "d" * 64

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _entry_facts() -> dict:
    return dict(
        layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
        classification=MemoryClassification.INTERNAL,
        source_content_digest_sha256=DIGEST, provenance_digest_sha256=DIGEST,
        expires_at_utc=NOW + timedelta(hours=1),
    )


def _admitted_receipt(**overrides):
    fields = dict(
        operation=MemoryOperation.ADMIT, final_outcome=MemoryFinalOutcome.ADMITTED, reason_code="",
        owner_id="op1", shift_id=uuid4(), authorization_scope_digest_sha256=DIGEST,
        entry_id=uuid4(), entry_digest_sha256=DIGEST, appended_entries=1, appended_tombstones=0,
        created_at_utc=NOW, **_entry_facts(),
    )
    fields.update(overrides)
    return build_receipt(**fields)


def _negative_receipt(**overrides):
    fields = dict(
        operation=MemoryOperation.ADMIT, final_outcome=MemoryFinalOutcome.REQUEST_INVALID,
        reason_code="REQUEST_INVALID", owner_id="op1", shift_id=uuid4(),
        authorization_scope_digest_sha256=DIGEST, appended_entries=0, appended_tombstones=0,
        created_at_utc=NOW,
    )
    fields.update(overrides)
    return build_receipt(**fields)


def test_schema_file_is_valid_json_schema(schema):
    jsonschema.Draft202012Validator.check_schema(schema)


def test_admitted_receipt_conforms(schema):
    payload = json.loads(_admitted_receipt().model_dump_json())
    jsonschema.validate(payload, schema)


def test_negative_receipt_conforms(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    jsonschema.validate(payload, schema)


def test_deleted_receipt_conforms(schema):
    payload = json.loads(
        build_receipt(
            operation=MemoryOperation.DELETE, final_outcome=MemoryFinalOutcome.DELETED, reason_code="",
            owner_id="op1", shift_id=uuid4(), authorization_scope_digest_sha256=DIGEST,
            tombstoned_entry_id=uuid4(), tombstone_reason=TombstoneReason.DELETED,
            appended_entries=0, appended_tombstones=1, created_at_utc=NOW,
        ).model_dump_json()
    )
    jsonschema.validate(payload, schema)


def test_schema_forbids_additional_properties(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    payload["unexpected_field"] = "x"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_requires_digest_format(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    payload["authorization_scope_digest_sha256"] = "short"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_receipt_schema_has_no_content_query_prompt_or_secret_fields(schema):
    properties = set(schema["properties"])
    forbidden = {"content", "query", "prompt", "context", "output", "evidence", "authorization", "api_key", "token"}
    assert not (properties & forbidden)


def test_entry_schema_forbids_additional_properties(schema):
    entry_def = schema["$defs"]["MemoryEntryV1"]
    assert entry_def["additionalProperties"] is False


def test_admitted_missing_required_field_rejected_by_schema(schema):
    """P4A3-REV-F4a - the JSON contract rejects an ADMITTED receipt missing a
    required field (model_construct bypasses Pydantic so the schema itself is
    the enforcement under test)."""
    payload = json.loads(
        MemoryReceiptV1.model_construct(
            operation=MemoryOperation.ADMIT, final_outcome=MemoryFinalOutcome.ADMITTED, reason_code="",
            owner_id="op1", shift_id=uuid4(), authorization_scope_digest_sha256=DIGEST,
            entry_id=uuid4(), entry_digest_sha256=DIGEST, appended_entries=1, appended_tombstones=0,
            created_at_utc=NOW, layer=None, receipt_hash_sha256=DIGEST,
        ).model_dump_json()
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_read_complete_surplus_field_rejected_by_schema(schema):
    """P4A3-REV-F4a - the JSON contract rejects a READ_COMPLETE receipt carrying
    a surplus positive field (model_construct bypasses Pydantic)."""
    payload = json.loads(
        MemoryReceiptV1.model_construct(
            operation=MemoryOperation.READ, final_outcome=MemoryFinalOutcome.READ_COMPLETE, reason_code="",
            owner_id="op1", shift_id=uuid4(), authorization_scope_digest_sha256=DIGEST,
            layer=MemoryLayer.SESSION, appended_entries=0, appended_tombstones=0,
            created_at_utc=NOW, receipt_hash_sha256=DIGEST,
        ).model_dump_json()
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
