"""Canonical receipt/citation/evidence hashing (SPEC R9 and the receipt
contract appendix). Pure package module.

All hashes reuse ``retrieval_contracts.canonical.canonical_json_bytes`` -
enums become values, UUIDs lowercase, UTC datetimes use ``Z``, NFC strings
and tuple order are preserved, map keys sort, and floats are forbidden. This
module performs no clock/id creation; every timestamp/id is supplied by the
caller.
"""

from __future__ import annotations

from typing import Any

from retrieval_contracts.canonical import canonical_json_bytes, sha256_bytes


def citation_id(citation_dump: dict[str, Any]) -> str:
    """``citation_id`` is SHA-256 of canonical JSON bytes for
    ``{"citation": <CitationV1 model_dump(mode="python")>}``."""
    return sha256_bytes(canonical_json_bytes({"citation": citation_dump}))


def authorization_scope_digest(
    workspace_id: str, principal_user_id: str, admitted_shift_ids: tuple[str, ...]
) -> str:
    """The authorization preimage is exactly
    ``{"workspace_id": ..., "principal_user_id": ..., "admitted_shift_ids": sorted ids}``."""
    preimage = {
        "workspace_id": workspace_id,
        "principal_user_id": principal_user_id,
        "admitted_shift_ids": list(sorted(admitted_shift_ids)),
    }
    return sha256_bytes(canonical_json_bytes(preimage))


def evidence_set_hash(
    citation_dumps: list[dict[str, Any]], projection_dumps: list[dict[str, Any]]
) -> str:
    """Evidence hash covers exactly
    ``{"citations": ordered citation dumps, "projections": ordered projection dumps}``."""
    preimage = {"citations": citation_dumps, "projections": projection_dumps}
    return sha256_bytes(canonical_json_bytes(preimage))


def receipt_hash(receipt_dump_without_hash: dict[str, Any]) -> str:
    """Receipt hash covers the entire receipt dump with only
    ``receipt_hash_sha256`` omitted (caller must have already omitted it)."""
    return sha256_bytes(canonical_json_bytes(receipt_dump_without_hash))
