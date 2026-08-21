"""Canonical application-memory digests (SPEC R2/R9).

All hashes reuse ``retrieval_contracts.canonical.canonical_json_bytes`` -
enums become values, UUIDs lowercase, UTC datetimes use ``Z``, NFC strings and
tuple order are preserved, map keys sort, and floats are forbidden - so every
digest here is byte-deterministic and independently recomputable by tests from
the same explicit preimage helpers the service uses. This module performs no
clock/id creation and no I/O; every input is supplied by the caller.
"""

from __future__ import annotations

from typing import Any

from retrieval_contracts.canonical import canonical_json_bytes, sha256_bytes


def content_digest(text: str) -> str:
    """SPEC R2 - digest of the normalized advisory content text (never the raw
    text itself, which receipts must not carry)."""
    return sha256_bytes(text.encode("utf-8", errors="strict"))


def entry_digest(entry_dump_without_digest: dict[str, Any]) -> str:
    """SPEC R2 - digest of one immutable entry over every field except its own
    ``entry_digest_sha256`` (caller must have already omitted it)."""
    return sha256_bytes(canonical_json_bytes({"entry": entry_dump_without_digest}))


def provenance_digest(
    *, source_type: str, source_id: str | None, source_version: str, owner_scope: str
) -> str:
    """SPEC R5 - digest binding the source's origin: its closed type, id,
    version and the caller-supplied canonical ownership scope. Recomputed by
    the revalidator rather than trusted from the admission path alone."""
    preimage = {
        "source_type": source_type,
        "source_id": source_id,
        "source_version": source_version,
        "owner_scope": owner_scope,
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def receipt_hash(receipt_dump_without_hash: dict[str, Any]) -> str:
    """SPEC R9 - receipt hash covers the entire receipt dump with only
    ``receipt_hash_sha256`` omitted (caller must have already omitted it)."""
    return sha256_bytes(canonical_json_bytes(receipt_dump_without_hash))
