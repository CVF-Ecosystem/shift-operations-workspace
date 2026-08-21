"""Support state and helpers for the P4-A3 application-memory evidence run
(SPEC R6/R7/R12).

Separated from the runner so mechanics are unit-testable without any provider
or network call; nothing here performs I/O at import time. The memory layer is
provider-neutral, so every refusal case proves ZERO store mutation and ZERO
provider attempts (there is no provider dispatch in this package). Secret
handling reuses the P4-A module's sanitizers: values are never printed,
persisted, hashed, logged or returned.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parents[1]
_SIBLING_PATHS = (
    "packages/application-memory/src", "packages/retrieval-contracts/src",
    "packages/refinery-bridge/src", "packages/operations-domain/src",
)
for _p in (str(REPO_ROOT / s) for s in _SIBLING_PATHS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p4a_gateway_live_evidence_support import (  # noqa: E402
    LiveEvidenceError,
    sanitize,
    scan_for_secrets,
    sha256_hex,
)
from application_memory.hashing import content_digest, provenance_digest  # noqa: E402
from application_memory.models import (  # noqa: E402
    AdmissionRequestV1,
    MemoryClassification,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryPurpose,
    SourceRefV1,
    SourceRevalidationOutcome,
    SourceRevalidationV1,
    SourceType,
)
from application_memory.service import ApplicationMemory  # noqa: E402
from application_memory.store import InMemoryApplicationMemoryStore  # noqa: E402

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)

# The mandated negative-write refusal cases: each must produce a negative
# receipt with zero store mutations and zero provider attempts (SPEC R6/R12).
REFUSAL_CASES = (
    "REQUEST_INVALID_TTL",
    "SOURCE_REVALIDATION_FAILED",
    "AUTHORIZATION_SCOPE_MISMATCH",
    "ENTRY_NOT_FOUND",
    "ENTRY_NOT_ACTIVE",
    "ENTRY_EXPIRED",
    "BUDGET_BREACH",
)

_OWNER_ID = "operator-1"
_SHIFT_ID = UUID("00000000-0000-0000-0000-000000000001")
_SCOPE_DIGEST = "a" * 64


class _GuardProvider:
    """NOT PROOF - raises if ever dispatched. The memory layer must never
    reach any provider, so every refusal case keeps ``calls == 0``."""

    provider_id = "application_memory_provider_neutral"

    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured_output(self, request):  # pragma: no cover - never reached
        self.calls += 1
        raise LiveEvidenceError("a refusal case reached a provider")


def _advancing_utc_now(*, start: datetime = NOW):
    calls = [0]

    def clock() -> datetime:
        calls[0] += 1
        return start + timedelta(microseconds=calls[0])

    return clock


def source_ref(*, source_id: str = "src-1", source_version: str = "1", text: str = "synthetic source text") -> SourceRefV1:
    """A deterministic, valid source reference whose digests are recomputed
    from the same explicit preimage helpers the service uses."""
    return SourceRefV1(
        source_type=SourceType.PROJECT_KNOWLEDGE,
        source_id=source_id,
        source_version=source_version,
        source_content_digest_sha256=content_digest(text),
        provenance_digest_sha256=provenance_digest(
            source_type=SourceType.PROJECT_KNOWLEDGE.value, source_id=source_id,
            source_version=source_version, owner_scope="",
        ),
    )


def admission_request(
    *, content: str = "advisory working note", ttl_seconds: int = 3600,
    source: SourceRefV1 | None = None,
) -> AdmissionRequestV1:
    return AdmissionRequestV1(
        layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
        classification=MemoryClassification.INTERNAL, content=content,
        source=source or source_ref(), requested_ttl_seconds=ttl_seconds,
    )


def fake_revalidator(*, outcome: SourceRevalidationOutcome, source: SourceRefV1 | None = None):
    """A fixed-outcome revalidator used only to force a specific refusal path."""

    def revalidate(declared: SourceRefV1) -> SourceRevalidationV1:
        bound = source if source is not None else declared
        return SourceRevalidationV1(source=bound, outcome=outcome, checked_at_utc=NOW)

    return revalidate


def fresh_service(*, clock, revalidator):
    """A fresh store + service for one refusal case (zero pre-existing state)."""
    store = InMemoryApplicationMemoryStore()
    service = ApplicationMemory(store, clock=clock, revalidator=revalidator)
    return service, store


def _admit_ok(service) -> "object":
    """Admit one valid entry and return it, so the mutation-refusal cases
    (scope/expiry/tombstone) have a real active predecessor to refuse against."""
    valid_source = source_ref()
    outcome = service.admit(
        request=admission_request(source=valid_source), owner_id=_OWNER_ID,
        shift_id=_SHIFT_ID, authorization_scope_digest=_SCOPE_DIGEST,
    )
    if outcome.receipt.final_outcome is not MemoryFinalOutcome.ADMITTED:
        raise LiveEvidenceError(f"fixture admission failed: {outcome.receipt.reason_code}")
    return outcome.entries[0]


def _run_case(case: str, clock, provider: _GuardProvider) -> dict:
    if case == "REQUEST_INVALID_TTL":
        service, store = fresh_service(clock=clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        before = store.snapshot()
        outcome = service.admit(
            request=admission_request(ttl_seconds=24 * 3600),  # exceeds SESSION ceiling
            owner_id=_OWNER_ID, shift_id=_SHIFT_ID, authorization_scope_digest=_SCOPE_DIGEST,
        )
    elif case == "SOURCE_REVALIDATION_FAILED":
        service, store = fresh_service(clock=clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.STALE))
        before = store.snapshot()
        outcome = service.admit(
            request=admission_request(), owner_id=_OWNER_ID, shift_id=_SHIFT_ID,
            authorization_scope_digest=_SCOPE_DIGEST,
        )
    elif case == "BUDGET_BREACH":
        service, store = fresh_service(clock=clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        before = store.snapshot()
        # 3000 emoji -> 3000 codepoints but 12000 UTF-8 bytes, exceeding the
        # 8192-byte bound while staying within the 4096-codepoint bound.
        oversized = "\U0001f600" * 3000
        outcome = service.admit(
            request=admission_request(content=oversized), owner_id=_OWNER_ID,
            shift_id=_SHIFT_ID, authorization_scope_digest=_SCOPE_DIGEST,
        )
    elif case == "AUTHORIZATION_SCOPE_MISMATCH":
        service, store = fresh_service(clock=clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        entry = _admit_ok(service)
        before = store.snapshot()
        outcome = service.delete(
            entry_id=entry.entry_id, owner_id=_OWNER_ID, shift_id=_SHIFT_ID,
            authorization_scope_digest="b" * 64,
        )
    elif case == "ENTRY_NOT_FOUND":
        service, store = fresh_service(clock=clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        before = store.snapshot()
        outcome = service.delete(
            entry_id=UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"), owner_id=_OWNER_ID,
            shift_id=_SHIFT_ID, authorization_scope_digest=_SCOPE_DIGEST,
        )
    elif case == "ENTRY_NOT_ACTIVE":
        service, store = fresh_service(clock=clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        entry = _admit_ok(service)
        service.delete(entry_id=entry.entry_id, owner_id=_OWNER_ID, shift_id=_SHIFT_ID, authorization_scope_digest=_SCOPE_DIGEST)
        before = store.snapshot()
        outcome = service.delete(entry_id=entry.entry_id, owner_id=_OWNER_ID, shift_id=_SHIFT_ID, authorization_scope_digest=_SCOPE_DIGEST)
    elif case == "ENTRY_EXPIRED":
        fast_clock = _advancing_utc_now()
        service, store = fresh_service(clock=fast_clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        entry = _admit_ok(service)
        late_clock = _advancing_utc_now(start=NOW + timedelta(hours=9))
        before = store.snapshot()
        expired_service = ApplicationMemory(store, clock=late_clock, revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID))
        outcome = expired_service.delete(
            entry_id=entry.entry_id, owner_id=_OWNER_ID, shift_id=_SHIFT_ID,
            authorization_scope_digest=_SCOPE_DIGEST,
        )
    else:
        raise LiveEvidenceError(f"unknown refusal case: {case}")

    after = store.snapshot()
    mutations = 0 if (before == after) else 1
    return {
        "case": case,
        "final_outcome": outcome.receipt.final_outcome.value,
        "reason_code": outcome.receipt.reason_code or "",
        "appended_entries": outcome.receipt.appended_entries,
        "appended_tombstones": outcome.receipt.appended_tombstones,
        "mutations": mutations,
        "provider_attempts": provider.calls,
    }


def run_refusals(provider: _GuardProvider | None = None) -> list[dict]:
    """Every mandated refusal case must produce zero store mutations and zero
    provider attempts. ``provider`` is optional; when supplied, any dispatch
    would raise inside the guard and fail the run."""
    provider = provider or _GuardProvider()
    results: list[dict] = []
    for case in REFUSAL_CASES:
        results.append(_run_case(case, _advancing_utc_now(), provider))
    return results


def scan_receipt_dump(dump: str) -> list[str]:
    return scan_for_secrets(dump)


def sha256_hex_of(text: str) -> str:
    return sha256_hex(text)


__all__ = [
    "REFUSAL_CASES",
    "NOW",
    "_GuardProvider",
    "source_ref",
    "admission_request",
    "fake_revalidator",
    "fresh_service",
    "run_refusals",
    "scan_receipt_dump",
    "sha256_hex_of",
    "sanitize",
    "scan_for_secrets",
]
