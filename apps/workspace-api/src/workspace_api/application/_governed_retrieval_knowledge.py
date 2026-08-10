"""P4-A1 governed retrieval - Project Knowledge positive path (SPEC R4/R5/R7).

The ONLY corpus in this tranche that may produce positive evidence. Every
input is explicit, caller-injected execution metadata; absence fails closed.
Validates ``knowledge/manifest.json`` against the deliberately NARROWER
retrieval-runtime subset of the Project Knowledge owner contract (Amendment 3
5.2) before constructing a P3-C ``RetrievalReadyV1``: exact shapes, owner/
consumer allowlists, no-symlink-anywhere containment, current pins,
``eligibleForLocalIndex``, active-retention literal. Whole-manifest
fail-closed (Amendment 4 5.1): one invalid entry raises
``KnowledgeCorpusUnavailable``, never a silent filter. Never PUBLIC/
provider-eligible. Also builds the R8/R9 citation/projection.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from refinery_bridge.canonical import source_fingerprint
from refinery_bridge.controls import ControlBundleV1
from refinery_bridge.enums import Sensitivity, SourceType
from refinery_bridge.input_models import DedupeContextV1, QuarantineRouteV1, RefineryEnvelopeV1
from refinery_bridge.output_models import RefineryResultV1
from refinery_bridge.pipeline import refine
from retrieval_contracts import (
    DataScopeEvidenceV1,
    RetrievalContractInputV1,
    RetentionAssertionV1,
    ScopeInputV1,
    construct_retrieval_contract,
)
from retrieval_contracts.contract_models import RetrievalReadyV1
from retrieval_contracts.enums import RetentionDisposition
from retrieval_contracts.source_models import ProjectKnowledgeSourceV1
from operations_domain.models import Shift

# RR2-F2/Amendment 3 5.2 - retrieval-runtime subset of the checker's field
# sets (reimplemented, never imported from the checker script).
_TOP_FIELDS = {"schemaVersion", "packId", "classification", "reviewedAt", "entries"}
_ENTRY_FIELDS = {
    "id", "path", "owner", "classification", "disposition", "dispositionReason", "purpose",
    "allowedConsumers", "sourcePins", "reviewedAt", "refreshTriggers", "retentionPolicy",
    "correctionPolicy", "eligibleForLocalIndex",
}
_PIN_FIELDS = {"path", "sha256"}
_OWNERS = {"ORCHESTRATOR", "SPEC_AUTHOR", "SESSION_SYNC_STEWARD"}
_CONSUMERS = {"LOCAL_GOVERNED_AGENT", "HUMAN_OPERATOR"}
_REQUIRED_CONSUMER = "LOCAL_GOVERNED_AGENT"
_SCHEMA_VERSION = "1.0"
_PACK_ID = "shift-operations-project-knowledge"
_REQUIRED_CLASSIFICATION = "INTERNAL"
_ACTIVE_DISPOSITION = "ACTIVE"
_MAX_MANIFEST_ENTRIES = 100
_ACTIVE_RETENTION_POLICY = "RETAIN_WHILE_SOURCES_ARE_CURRENT_AND_OWNER_MAINTAINS_ENTRY"
_SHA256_RE = re.compile(r"[0-9a-f]{64}")

class KnowledgeCorpusUnavailable(Exception):
    """Raised when the manifest, an entry, or its pins fail admission."""

class ManifestEntryLimitExceeded(Exception):
    """R6/F10/RR1-F4 - over 100 entries; applies to read AND reread."""

@dataclass(frozen=True)
class ProjectKnowledgeExecutionContext:
    """Explicit, caller-injected execution metadata; no production default."""

    repository_root: Path
    control_bundle: ControlBundleV1
    now: datetime
    dedupe_context: DedupeContextV1
    quarantine_route: QuarantineRouteV1
    anchor_shift: Shift
    anchor_principal_user_id: str

def _digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _load_manifest(repository_root: Path) -> dict[str, Any]:
    manifest_path = repository_root / "knowledge" / "manifest.json"
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgeCorpusUnavailable("manifest unreadable") from exc
    if not isinstance(raw, dict) or set(raw) != _TOP_FIELDS:  # RR2-F2 - exact shape, not just "is a mapping"
        raise KnowledgeCorpusUnavailable("manifest is not the exact top-level shape")
    if raw.get("schemaVersion") != _SCHEMA_VERSION or raw.get("packId") != _PACK_ID:
        raise KnowledgeCorpusUnavailable("manifest schemaVersion/packId mismatch")
    if raw.get("classification") != _REQUIRED_CLASSIFICATION or not isinstance(raw.get("entries"), list):
        raise KnowledgeCorpusUnavailable("manifest classification/entries shape invalid")
    return raw

def _load_manifest_within_ceiling(repository_root: Path) -> dict[str, Any]:
    """RR1-F4 - shared: SAME 100-entry ceiling for read and reread."""
    manifest = _load_manifest(repository_root)
    entries = manifest["entries"]
    if len(entries) > _MAX_MANIFEST_ENTRIES:
        raise ManifestEntryLimitExceeded(len(entries))
    return manifest

def _has_active_owner_and_retention(entry: dict[str, Any]) -> bool:
    """R5/F4/RR1-F3/RR2-F2 - owner allowlisted AND EXACT retention literal."""
    return entry.get("owner") in _OWNERS and entry.get("retentionPolicy") == _ACTIVE_RETENTION_POLICY

def _safe_relative_path(value: Any) -> str | None:
    """RR1-F3 - shape only: non-empty relative, no ``..``; see :func:`_resolve_contained`."""
    if not isinstance(value, str) or not value:
        return None
    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return value

def _resolve_contained(base: Path, relative: str) -> Path | None:
    """RR1-F3/RR2-F2/RR3-F3 - resolve under ``base``, proving the RESOLVED
    path stays inside ``base`` AND that neither ``base`` itself, any of its
    ancestors, nor any component down to the target is a symlink."""
    walked = base
    while True:
        if walked.is_symlink():
            return None
        parent = walked.parent
        if parent == walked:
            break
        walked = parent
    try:
        resolved_base = base.resolve(strict=False)
        resolved = (base / relative).resolve(strict=False)
    except (OSError, ValueError):
        return None
    if resolved != resolved_base and resolved_base not in resolved.parents:
        return None
    parts = PurePosixPath(relative.replace("\\", "/")).parts
    walked = base
    for part in parts:
        walked = walked / part
        if walked.is_symlink():
            return None
    return resolved

def _pin_current(pin: Any, repository_root: Path) -> bool:
    """RR1-F3/RR2-F2 - exact shape, hex sha256, containment, current bytes."""
    if not isinstance(pin, dict) or set(pin) != _PIN_FIELDS:
        return False
    pin_path = _safe_relative_path(pin.get("path"))
    resolved = _resolve_contained(repository_root, pin_path) if pin_path else None
    pin_sha = pin.get("sha256")
    if resolved is None or not isinstance(pin_sha, str) or not _SHA256_RE.fullmatch(pin_sha):
        return False
    try:
        return _digest_file(resolved) == pin_sha
    except (OSError, UnicodeError):
        return False

def _consumers_admissible(consumers: Any) -> bool:
    """RR2-F2 - known-shape strings, duplicate-free, allowlisted, has the required consumer."""
    if not isinstance(consumers, list) or not all(isinstance(c, str) for c in consumers):
        return False
    if len(set(consumers)) != len(consumers) or not set(consumers).issubset(_CONSUMERS):
        return False
    return _REQUIRED_CONSUMER in consumers

def _entry_admissible(entry: dict[str, Any], repository_root: Path) -> bool:
    # RR2-F2 - exact entry field shape before any single-field access.
    if not isinstance(entry, dict) or set(entry) != _ENTRY_FIELDS:
        return False
    if entry.get("classification") != _REQUIRED_CLASSIFICATION or entry.get("disposition") != _ACTIVE_DISPOSITION:
        return False
    if entry.get("eligibleForLocalIndex") is not True or _safe_relative_path(entry.get("id")) is None:
        return False
    if not _has_active_owner_and_retention(entry) or not _consumers_admissible(entry.get("allowedConsumers")):
        return False
    source_pins = entry.get("sourcePins")
    entry_path = _safe_relative_path(entry.get("path"))
    if not isinstance(source_pins, list) or not source_pins or entry_path is None:
        return False
    pin_paths = [p.get("path") for p in source_pins if isinstance(p, dict)]
    if len(pin_paths) != len(source_pins) or len({str(p) for p in pin_paths}) != len(pin_paths):
        return False
    if _resolve_contained(repository_root / "knowledge", entry_path) is None:  # RR1-F3 - containment
        return False
    return all(_pin_current(pin, repository_root) for pin in source_pins)

def _unique_safe(entries: list, key: str) -> bool:
    values = [v for v in (_safe_relative_path(e.get(key)) for e in entries if isinstance(e, dict)) if v is not None]
    return len(set(values)) == len(values)

def _admissible_entries(manifest: dict[str, Any], repository_root: Path) -> list[dict[str, Any]]:
    """RR3-F1 - whole-manifest fail-closed: one invalid entry raises
    :class:`KnowledgeCorpusUnavailable` for the entire corpus, never a
    silent filter; a valid empty entries list is a valid empty corpus."""
    if manifest.get("classification") != _REQUIRED_CLASSIFICATION:
        raise KnowledgeCorpusUnavailable("manifest classification invalid")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise KnowledgeCorpusUnavailable("manifest entries not a list")
    # RR2-F2 - unique safe entry ids AND unique safe entry paths.
    if not _unique_safe(entries, "id") or not _unique_safe(entries, "path"):
        raise KnowledgeCorpusUnavailable("manifest entry id/path not unique-safe")
    admissible = []
    for e in entries:
        if not _entry_admissible(e, repository_root):
            raise KnowledgeCorpusUnavailable("manifest entry failed admission")
        admissible.append(e)
    return admissible

def list_admissible_knowledge_entries(repository_root: Path) -> tuple[dict[str, Any], ...]:
    """R4/R7 - eligible entries for local advisory retrieval; no Ledger/
    network/provider access. Raises :class:`ManifestEntryLimitExceeded`
    above the R6 100-entry maximum, or :class:`KnowledgeCorpusUnavailable`
    (RR3-F1) if any entry is invalid."""
    manifest = _load_manifest_within_ceiling(repository_root)
    return tuple(_admissible_entries(manifest, repository_root))

_MAX_DOCUMENT_CODEPOINTS = 65536

class DocumentLimitExceeded(Exception):
    """R6/F10 - document exceeds 65,536 code points; typed limit, never a silent slice."""

def build_ready_contract(
    entry: dict[str, Any], context: ProjectKnowledgeExecutionContext
) -> tuple[RetrievalReadyV1, str] | None:
    """Construct the P3-C ``RetrievalReadyV1`` for one admissible manifest
    entry plus its P3-A candidate sensitivity, or ``None`` if P3-C admission
    fails (fail-closed). Raises :class:`DocumentLimitExceeded` above 65,536
    code points - never silently truncated."""
    # RR1-F3 - defense in depth: re-prove containment here too.
    safe_path = _safe_relative_path(entry.get("path"))
    doc_path = _resolve_contained(context.repository_root / "knowledge", safe_path) if safe_path else None
    if doc_path is None:
        return None
    try:
        text = doc_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    if not text:
        return None
    if len(text) > _MAX_DOCUMENT_CODEPOINTS:
        raise DocumentLimitExceeded(entry.get("id"))
    owner_id, retention_policy = str(entry["owner"]), str(entry["retentionPolicy"])
    pin_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    source = ProjectKnowledgeSourceV1(
        source_id=entry["id"], source_pin=pin_digest, current_source_pin=pin_digest, source_owner_id=owner_id,
    )
    payload = {
        "schema_version": "1.0", "source_id": source.source_id, "source_version": source.source_pin,
        "source_link": f"knowledge:{entry['path']}", "source_type": SourceType.PROJECT_KNOWLEDGE,
        "raw_text": text, "received_at": context.now, "declared_sensitivity": Sensitivity.INTERNAL,
        "source_owner_id": source.source_owner_id, "source_fingerprint": source_fingerprint(text).model_dump(),
    }
    try:
        envelope = RefineryEnvelopeV1.model_validate(payload)
    except Exception:
        return None
    result = refine(
        payload, context.control_bundle, dedupe_context=context.dedupe_context,
        quarantine_route=context.quarantine_route,
    )
    if not isinstance(result, RefineryResultV1) or result.context_candidate is None:
        return None
    item = RetrievalContractInputV1(
        envelope=envelope, refinery_result=result, candidate=result.context_candidate,
        candidate_fingerprint=result.candidate_fingerprint, source=source, field_selector="document",
        source_cutoff_utc=context.now, observed_at_utc=context.now, correction=None,
        scope=ScopeInputV1(shift_ids=(), parent_shifts=(), effective_from_utc=None, effective_to_utc=None),
        retention=RetentionAssertionV1(
            disposition=RetentionDisposition.OWNER_ASSERTED_ACTIVE, owner_id=owner_id,
            policy_version=retention_policy, checked_at_utc=context.now, expires_at_utc=None,
            source_evidence_id=f"knowledge:{entry['id']}",
        ),
        data_scope_evidence=DataScopeEvidenceV1(), tenant_required=False,
    )
    candidate = construct_retrieval_contract(item)
    if not isinstance(candidate, RetrievalReadyV1):
        return None
    return candidate, result.context_candidate.sensitivity.value


def revalidate_entry(
    entry_id: str, repository_root: Path, context: ProjectKnowledgeExecutionContext
) -> tuple[dict[str, Any], RetrievalReadyV1, str] | None:
    """R7/RR1-F4 - at use time, reread the manifest and *rebuild* the
    admitted P3-C contract from current bytes; ``None``/raises if the
    entry no longer admits - never a stale reuse."""
    manifest = _load_manifest_within_ceiling(repository_root)
    for entry in _admissible_entries(manifest, repository_root):
        if entry.get("id") != entry_id:
            continue
        built = build_ready_contract(entry, context)
        if built is None:
            return None
        ready, sensitivity = built
        return entry, ready, sensitivity
    return None
