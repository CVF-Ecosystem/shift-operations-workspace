"""P4-A3 SPEC R1/R2/R11 - strict model contracts and reconstruction.

Covers extra-forbid/frozen, closed enums, UTC enforcement, content
codepoint/UTF-8-byte bounds, content/entry digest self-validation,
``model_construct``/hash-recompute adversaries, and reconstruction of
untrusted nested models from primitive dumps.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from application_memory.hashing import content_digest, entry_digest
from application_memory.models import (
    AdmissionRequestV1,
    MemoryClassification,
    MemoryEntryV1,
    MemoryLayer,
    MemoryPurpose,
    SourceRefV1,
    SourceType,
)

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _source() -> SourceRefV1:
    return SourceRefV1(
        source_type=SourceType.PROJECT_KNOWLEDGE,
        source_id="src-1",
        source_version="1",
        source_content_digest_sha256=content_digest("source text"),
        provenance_digest_sha256="b" * 64,
    )


def _entry_fields(**overrides):
    fields = dict(
        entry_id=uuid4(), layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
        owner_id="op1", shift_id=uuid4(), authorization_scope_digest_sha256="a" * 64,
        classification=MemoryClassification.INTERNAL, source=_source(), content="hello world",
        content_digest_sha256=content_digest("hello world"), created_at_utc=NOW,
        expires_at_utc=NOW + timedelta(hours=1), policy_version="1.0", predecessor_id=None,
    )
    fields.update(overrides)
    dump = MemoryEntryV1.model_construct(**fields, entry_digest_sha256="0" * 64).model_dump(mode="python")
    dump.pop("entry_digest_sha256")
    fields["entry_digest_sha256"] = entry_digest(dump)
    return fields


def _entry(**overrides) -> MemoryEntryV1:
    return MemoryEntryV1(**_entry_fields(**overrides))


class TestStrictAndFrozen:
    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            MemoryEntryV1(**_entry_fields(), unexpected="x")

    def test_model_is_frozen(self):
        entry = _entry()
        with pytest.raises(ValidationError):
            entry.content = "mutated"  # type: ignore[misc]

    def test_admission_request_extra_forbidden(self):
        with pytest.raises(ValidationError):
            AdmissionRequestV1(
                layer=MemoryLayer.SESSION, purpose=MemoryPurpose.HANDOVER_CONTEXT,
                classification=MemoryClassification.INTERNAL, content="x", source=_source(),
                requested_ttl_seconds=60, extra=1,
            )


class TestClosedEnums:
    def test_unknown_layer_rejected(self):
        dump = _entry().model_dump(mode="python")
        dump["layer"] = "EPISODIC"
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(dump)

    def test_unknown_purpose_rejected(self):
        dump = _entry().model_dump(mode="python")
        dump["purpose"] = "AUTONOMOUS_ACTION"
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(dump)

    def test_restricted_classification_rejected(self):
        dump = _entry().model_dump(mode="python")
        dump["classification"] = "RESTRICTED"
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(dump)

    def test_unknown_source_type_rejected(self):
        with pytest.raises(ValidationError):
            SourceRefV1(
                source_type="CHAT_HISTORY", source_id="x", source_version="1",
                source_content_digest_sha256="a" * 64, provenance_digest_sha256="b" * 64,
            )


class TestUtcAndContentBounds:
    def test_naive_datetime_rejected(self):
        dump = _entry().model_dump(mode="python")
        dump["created_at_utc"] = datetime(2026, 8, 21, 12, 0)
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(dump)

    def test_empty_content_rejected(self):
        with pytest.raises(ValidationError):
            _entry(content="", content_digest_sha256=content_digest(""))

    def test_content_over_codepoint_bound_rejected(self):
        with pytest.raises(ValidationError):
            _entry(content="a" * 4097, content_digest_sha256=content_digest("a" * 4097))

    def test_content_over_utf8_byte_bound_rejected(self):
        oversized = "\U0001f600" * 3000  # 3000 codepoints, 12000 UTF-8 bytes
        with pytest.raises(ValidationError):
            _entry(content=oversized, content_digest_sha256=content_digest(oversized))

    def test_non_nfc_content_rejected(self):
        dump = _entry().model_dump(mode="python")
        decomposed = "e\u0301"  # "é" in NFD form
        dump["content"] = decomposed
        dump["content_digest_sha256"] = content_digest(decomposed)
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(dump)


class TestDigestAdversaries:
    def test_forged_content_digest_rejected(self):
        with pytest.raises(ValidationError):
            _entry(content_digest_sha256="0" * 64)

    def test_forged_entry_digest_rejected_via_model_copy(self):
        entry = _entry()
        dump = entry.model_dump(mode="python")
        dump["entry_digest_sha256"] = "0" * 64
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(dump)

    def test_model_construct_bypass_still_revalidates_on_validate(self):
        fields = _entry_fields()
        fields["entry_digest_sha256"] = "0" * 64
        raw = MemoryEntryV1.model_construct(**fields)
        with pytest.raises(ValidationError):
            MemoryEntryV1.model_validate(raw.model_dump(mode="python"))


class TestPrimitiveReconstruction:
    def test_entry_reconstructed_from_canonical_dump(self):
        entry = _entry()
        dump = entry.model_dump(mode="python")
        rebuilt = MemoryEntryV1.model_validate(dump)
        assert rebuilt == entry
        assert isinstance(rebuilt.source, SourceRefV1)

    def test_source_reconstructed_from_canonical_dump(self):
        source = _source()
        rebuilt = SourceRefV1.model_validate(source.model_dump(mode="python"))
        assert rebuilt == source


class TestTtlCeiling:
    """P4A3-REV-F3a - the entry invariant enforces strict positive TTL and the
    layer ceiling (SESSION <= 8h, WORKING <= 24h)."""

    def test_zero_ttl_rejected(self):
        with pytest.raises(ValidationError):
            _entry(expires_at_utc=NOW)

    def test_session_exactly_8h_accepted(self):
        entry = _entry(expires_at_utc=NOW + timedelta(hours=8))
        assert entry.layer is MemoryLayer.SESSION

    def test_session_8h_plus_1s_rejected(self):
        with pytest.raises(ValidationError):
            _entry(expires_at_utc=NOW + timedelta(hours=8, seconds=1))

    def test_working_exactly_24h_accepted(self):
        entry = _entry(layer=MemoryLayer.WORKING, expires_at_utc=NOW + timedelta(hours=24))
        assert entry.layer is MemoryLayer.WORKING

    def test_working_24h_plus_1s_rejected(self):
        with pytest.raises(ValidationError):
            _entry(layer=MemoryLayer.WORKING, expires_at_utc=NOW + timedelta(hours=24, seconds=1))
