"""P4-A3 SPEC R2/R9 - canonical digest determinism and distinctness."""

from __future__ import annotations

from application_memory.hashing import (
    content_digest,
    entry_digest,
    provenance_digest,
    receipt_hash,
)

DIGEST_RE = r"^[0-9a-f]{64}$"


class TestContentDigest:
    def test_is_lowercase_sha256_hex(self):
        assert content_digest("hello") != content_digest("hello").upper()
        assert len(content_digest("hello")) == 64
        assert int(content_digest("hello"), 16) >= 0

    def test_distinct_inputs_distinct_digests(self):
        assert content_digest("a") != content_digest("b")


class TestEntryDigest:
    def test_deterministic_and_recomputable(self):
        dump = {"entry_id": "x", "content": "hello", "n": 1}
        assert entry_digest(dump) == entry_digest(dict(dump))

    def test_changes_with_any_field(self):
        base = {"a": 1}
        assert entry_digest(base) != entry_digest({"a": 2})


class TestProvenanceDigest:
    def test_binds_all_four_facts(self):
        args = dict(source_type="TASK", source_id="t1", source_version="3", owner_scope="shift-1")
        assert provenance_digest(**args) != provenance_digest(**{**args, "owner_scope": "shift-2"})
        assert provenance_digest(**args) != provenance_digest(**{**args, "source_version": "4"})

    def test_none_source_id_is_distinct_from_empty_string(self):
        assert provenance_digest(source_type="T", source_id=None, source_version="1", owner_scope="") != (
            provenance_digest(source_type="T", source_id="", source_version="1", owner_scope="")
        )


class TestReceiptHash:
    def test_recomputable_and_field_sensitive(self):
        base = {"operation": "ADMIT", "final_outcome": "ADMITTED", "appended_entries": 1}
        assert receipt_hash(base) == receipt_hash(dict(base))
        assert receipt_hash(base) != receipt_hash({**base, "appended_entries": 2})
