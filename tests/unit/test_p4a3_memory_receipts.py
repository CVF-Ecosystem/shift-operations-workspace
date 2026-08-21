"""P4-A3 SPEC R9 - sanitized receipt grammar and hash recomputation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from application_memory.models import (
    MemoryClassification,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryOperation,
    MemoryPurpose,
    TombstoneReason,
)
from application_memory.receipts import MemoryReceiptV1, build_receipt

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
OWNER = "op1"
SCOPE = "a" * 64
SHIFT = uuid4()
DIGEST = "d" * 64


def _entry_facts() -> dict:
    """The full entry/source/lifecycle facts a positive ADMITTED/CORRECTED
    receipt must carry (P4A3-REV-F4a)."""
    return dict(
        layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
        classification=MemoryClassification.INTERNAL,
        source_content_digest_sha256=DIGEST, provenance_digest_sha256=DIGEST,
        expires_at_utc=NOW + timedelta(hours=1),
    )


def _admitted(**overrides) -> MemoryReceiptV1:
    fields = dict(
        operation=MemoryOperation.ADMIT, final_outcome=MemoryFinalOutcome.ADMITTED, reason_code="",
        owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
        entry_id=uuid4(), entry_digest_sha256=DIGEST, appended_entries=1, appended_tombstones=0,
        created_at_utc=NOW, **_entry_facts(),
    )
    fields.update(overrides)
    return build_receipt(**fields)


def _negative(**overrides) -> MemoryReceiptV1:
    fields = dict(
        operation=MemoryOperation.ADMIT, final_outcome=MemoryFinalOutcome.REQUEST_INVALID,
        reason_code="REQUEST_INVALID", owner_id=OWNER, shift_id=SHIFT,
        authorization_scope_digest_sha256=SCOPE, appended_entries=0, appended_tombstones=0,
        created_at_utc=NOW,
    )
    fields.update(overrides)
    return build_receipt(**fields)


class TestHashRecomputation:
    def test_builder_produces_self_consistent_hash(self):
        receipt = _admitted()
        assert receipt.receipt_hash_sha256 != "0" * 64

    def test_tampered_hash_rejected(self):
        receipt = _admitted()
        dump = receipt.model_dump(mode="python")
        dump["receipt_hash_sha256"] = "0" * 64
        with pytest.raises(ValidationError):
            MemoryReceiptV1.model_validate(dump)

    def test_tampered_field_changes_hash(self):
        a = _admitted()
        b = _admitted(entry_id=uuid4())
        assert a.receipt_hash_sha256 != b.receipt_hash_sha256


class TestPositiveGrammar:
    def test_admitted_requires_empty_reason(self):
        with pytest.raises(ValidationError):
            _admitted(reason_code="NONEMPTY")

    def test_admitted_requires_entry_id_and_digest(self):
        with pytest.raises(ValidationError):
            _admitted(entry_id=None)

    def test_deleted_requires_tombstone_reason(self):
        with pytest.raises(ValidationError):
            build_receipt(
                operation=MemoryOperation.DELETE, final_outcome=MemoryFinalOutcome.DELETED, reason_code="",
                owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
                tombstoned_entry_id=uuid4(), appended_entries=0, appended_tombstones=1,
                created_at_utc=NOW,
            )

    def test_deleted_valid(self):
        receipt = build_receipt(
            operation=MemoryOperation.DELETE, final_outcome=MemoryFinalOutcome.DELETED, reason_code="",
            owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
            tombstoned_entry_id=uuid4(), tombstone_reason=TombstoneReason.DELETED,
            appended_entries=0, appended_tombstones=1, created_at_utc=NOW,
        )
        assert receipt.final_outcome is MemoryFinalOutcome.DELETED


class TestNegativeGrammar:
    def test_negative_requires_reason(self):
        with pytest.raises(ValidationError):
            _negative(reason_code="")

    def test_negative_requires_zero_mutations(self):
        with pytest.raises(ValidationError):
            _negative(appended_entries=1)

    def test_negative_valid(self):
        receipt = _negative()
        assert receipt.appended_entries == 0
        assert receipt.appended_tombstones == 0


class TestNoSensitiveFields:
    def test_receipt_model_has_no_content_or_secret_fields(self):
        forbidden = {"content", "query", "prompt", "token", "credential", "api_key", "provider_output", "source_body"}
        assert not (set(MemoryReceiptV1.model_fields) & forbidden)

    def test_receipt_dump_contains_no_content_text(self):
        receipt = _admitted()
        dump = str(receipt.model_dump(mode="python"))
        assert "hello" not in dump


class TestClosedGrammar:
    """P4A3-REV-F4 - every mismatched operation/positive-outcome pair and every
    surplus field must fail closed."""

    MISMATCHED = [
        (MemoryOperation.ADMIT, MemoryFinalOutcome.READ_COMPLETE),
        (MemoryOperation.ADMIT, MemoryFinalOutcome.CORRECTED),
        (MemoryOperation.ADMIT, MemoryFinalOutcome.DELETED),
        (MemoryOperation.READ, MemoryFinalOutcome.ADMITTED),
        (MemoryOperation.READ, MemoryFinalOutcome.CORRECTED),
        (MemoryOperation.READ, MemoryFinalOutcome.DELETED),
        (MemoryOperation.CORRECT, MemoryFinalOutcome.ADMITTED),
        (MemoryOperation.CORRECT, MemoryFinalOutcome.READ_COMPLETE),
        (MemoryOperation.CORRECT, MemoryFinalOutcome.DELETED),
        (MemoryOperation.DELETE, MemoryFinalOutcome.ADMITTED),
        (MemoryOperation.DELETE, MemoryFinalOutcome.READ_COMPLETE),
        (MemoryOperation.DELETE, MemoryFinalOutcome.CORRECTED),
    ]

    @pytest.mark.parametrize("op,outcome", MISMATCHED)
    def test_mismatched_operation_outcome_rejected(self, op, outcome):
        with pytest.raises(ValidationError):
            build_receipt(
                operation=op, final_outcome=outcome, reason_code="",
                owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
                appended_entries=0, appended_tombstones=0, created_at_utc=NOW,
            )

    def test_admitted_surplus_predecessor_rejected(self):
        with pytest.raises(ValidationError):
            _admitted(predecessor_entry_id=uuid4())

    def test_admitted_surplus_tombstone_reason_rejected(self):
        with pytest.raises(ValidationError):
            _admitted(tombstone_reason=TombstoneReason.CORRECTED)

    def test_admitted_surplus_read_payload_rejected(self):
        with pytest.raises(ValidationError):
            _admitted(returned_entry_ids=(uuid4(),), returned_entry_digests=(DIGEST,))

    def test_corrected_predecessor_must_equal_tombstoned(self):
        with pytest.raises(ValidationError):
            build_receipt(
                operation=MemoryOperation.CORRECT, final_outcome=MemoryFinalOutcome.CORRECTED, reason_code="",
                owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
                entry_id=uuid4(), entry_digest_sha256=DIGEST,
                predecessor_entry_id=uuid4(), tombstoned_entry_id=uuid4(),
                tombstone_reason=TombstoneReason.CORRECTED,
                appended_entries=1, appended_tombstones=1, created_at_utc=NOW, **_entry_facts(),
            )

    def test_deleted_surplus_entry_rejected(self):
        with pytest.raises(ValidationError):
            build_receipt(
                operation=MemoryOperation.DELETE, final_outcome=MemoryFinalOutcome.DELETED, reason_code="",
                owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
                tombstoned_entry_id=uuid4(), tombstone_reason=TombstoneReason.DELETED,
                entry_id=uuid4(), appended_entries=0, appended_tombstones=1, created_at_utc=NOW,
            )


class TestFieldGrammar:
    """P4A3-REV-F4a - missing required fields and surplus fields per positive
    outcome must fail closed (hash recomputed independently by build_receipt)."""

    @pytest.mark.parametrize("missing", ["layer", "purpose", "classification", "source_content_digest_sha256", "provenance_digest_sha256", "expires_at_utc", "entry_id", "entry_digest_sha256"])
    def test_admitted_missing_required_field_rejected(self, missing):
        with pytest.raises(ValidationError):
            _admitted(**{missing: None})

    @pytest.mark.parametrize("surplus", ["layer", "purpose", "classification", "source_content_digest_sha256", "provenance_digest_sha256", "expires_at_utc"])
    def test_read_complete_surplus_field_rejected(self, surplus):
        fields = dict(
            operation=MemoryOperation.READ, final_outcome=MemoryFinalOutcome.READ_COMPLETE, reason_code="",
            owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
            appended_entries=0, appended_tombstones=0, created_at_utc=NOW,
        )
        fields[surplus] = _entry_facts()[surplus]
        with pytest.raises(ValidationError):
            build_receipt(**fields)

    def test_deleted_missing_tombstoned_rejected(self):
        with pytest.raises(ValidationError):
            build_receipt(
                operation=MemoryOperation.DELETE, final_outcome=MemoryFinalOutcome.DELETED, reason_code="",
                owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest_sha256=SCOPE,
                tombstone_reason=TombstoneReason.DELETED,
                appended_entries=0, appended_tombstones=1, created_at_utc=NOW,
            )

    def test_admitted_surplus_omitted_count_rejected(self):
        with pytest.raises(ValidationError):
            _admitted(omitted_count=1)
