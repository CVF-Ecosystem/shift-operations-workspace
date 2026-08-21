"""P4-A3 application memory - no-route application composition (SPEC R5/R10).

The sole application-boundary owner: verifies the existing authenticated
principal/assignment boundary, computes the exact authorization-scope digest,
and injects the process-local store, clock and a real ledger/project-knowledge
source-revalidation callback into the pure ``application_memory`` package.
Opens no HTTP route, persists nothing, and never recalls memory implicitly
into P4-A2 - a later explicit caller may request already-revalidated entries
only.

``User``/``InMemoryLedger`` are deliberately NOT imported here:
``tests/unit/test_operations_domain_boundary.py`` enforces a closed allowlist
of production files permitted to import ``User`` directly, and the composition
receives the ledger/principal/shift/assignment-scope from its caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from application_memory.hashing import content_digest, provenance_digest
from application_memory.models import (
    AdmissionRequestV1,
    SourceRefV1,
    SourceRevalidationOutcome,
    SourceRevalidationV1,
    SourceType,
)
from application_memory.service import ApplicationMemory, MemoryOutcome
from application_memory.store import InMemoryApplicationMemoryStore
from governed_retrieval.hashing import authorization_scope_digest

from workspace_api.application.assignment_scope import AssignmentScope

WORKSPACE_ID = "shift-operations-workspace"

# The versioned, shift-bound record types this bounded, advisory revalidator
# supports. HANDOVER/REPORT/MESSAGE sources are deliberately out of scope for
# this tranche's revalidator (advisory limitation, not a silent success).
_RECORD_GETTERS: dict[SourceType, tuple[str, str]] = {
    SourceType.OPERATIONAL_EVENT: ("get_event", "title"),
    SourceType.TASK: ("get_task", "title"),
    SourceType.CUSTOMER_REQUEST: ("get_customer_request", "summary"),
    SourceType.INCIDENT: ("get_incident", "summary"),
}


def _default_clock() -> datetime:
    return datetime.now(timezone.utc)


def scope_digest_for(principal, shift_id: UUID, *, workspace_id: str = WORKSPACE_ID) -> str:
    """The exact single-shift authorization-scope digest, reusing the P4-A1
    canonical ``authorization_scope_digest`` preimage (workspace, owner, sorted
    shift ids)."""
    return authorization_scope_digest(workspace_id, principal.user_id, (str(shift_id),))


@dataclass(frozen=True)
class BoundApplicationMemory:
    """The verified-scope handle: bundles the pure service with the exact
    owner/shift/scope facts so a caller cannot silently substitute another
    principal or shift between build and use."""

    memory: ApplicationMemory
    owner_id: str
    shift_id: UUID
    authorization_scope_digest: str

    def admit(self, *, request: AdmissionRequestV1) -> MemoryOutcome:
        return self.memory.admit(
            request=request, owner_id=self.owner_id, shift_id=self.shift_id,
            authorization_scope_digest=self.authorization_scope_digest,
        )

    def correct(self, *, entry_id: UUID, request: AdmissionRequestV1) -> MemoryOutcome:
        return self.memory.correct(
            entry_id=entry_id, request=request, owner_id=self.owner_id, shift_id=self.shift_id,
            authorization_scope_digest=self.authorization_scope_digest,
        )

    def delete(self, *, entry_id: UUID) -> MemoryOutcome:
        return self.memory.delete(
            entry_id=entry_id, owner_id=self.owner_id, shift_id=self.shift_id,
            authorization_scope_digest=self.authorization_scope_digest,
        )

    def read(self, *, limit: int) -> MemoryOutcome:
        return self.memory.read(
            owner_id=self.owner_id, shift_id=self.shift_id,
            authorization_scope_digest=self.authorization_scope_digest, limit=limit,
        )


def _record_source_facts(
    ledger, source_type: SourceType, source_id: str | None, bound_shift_id: UUID
) -> tuple[str, str, str] | None:
    getter = _RECORD_GETTERS.get(source_type)
    if getter is None or source_id is None:
        return None
    try:
        rid = UUID(source_id)
    except (ValueError, TypeError):
        return None
    method_name, text_attr = getter
    try:
        record = getattr(ledger, method_name)(rid)
    except (KeyError, AttributeError):
        return None
    version = str(getattr(record, "version"))
    text = getattr(record, text_attr)
    shift = getattr(record, "shift_id", None)
    # P4A3-REV-F1 - a shift-owned operational source must belong to the bound
    # shift; a record from another shift (or an unbound record) fails closed.
    if str(shift) != str(bound_shift_id):
        return None
    return version, text, (str(shift) if shift is not None else "")


def _build_revalidator(ledger, *, project_knowledge: dict | None, clock, bound_shift_id: UUID):
    project_knowledge = project_knowledge or {}

    def revalidate(source: SourceRefV1) -> SourceRevalidationV1:
        now = clock()
        if source.source_type is SourceType.PROJECT_KNOWLEDGE:
            facts = project_knowledge.get(source.source_id)
            if facts is None:
                return SourceRevalidationV1(source=source, outcome=SourceRevalidationOutcome.NOT_FOUND, checked_at_utc=now)
            version, text, owner_scope = facts
        else:
            facts = _record_source_facts(ledger, source.source_type, source.source_id, bound_shift_id)
            if facts is None:
                return SourceRevalidationV1(source=source, outcome=SourceRevalidationOutcome.NOT_FOUND, checked_at_utc=now)
            version, text, owner_scope = facts

        current_content = content_digest(text)
        current_provenance = provenance_digest(
            source_type=source.source_type.value, source_id=source.source_id,
            source_version=version, owner_scope=owner_scope,
        )
        if (
            version != source.source_version
            or current_content != source.source_content_digest_sha256
            or current_provenance != source.provenance_digest_sha256
        ):
            return SourceRevalidationV1(source=source, outcome=SourceRevalidationOutcome.STALE, checked_at_utc=now)
        return SourceRevalidationV1(source=source, outcome=SourceRevalidationOutcome.VALID, checked_at_utc=now)

    return revalidate


def build_application_memory(
    *,
    ledger,
    principal,
    shift,
    assignment_scope: AssignmentScope,
    clock=None,
    project_knowledge: dict | None = None,
    workspace_id: str = WORKSPACE_ID,
) -> BoundApplicationMemory:
    """SPEC R5/R10 - verify assignment, compute the exact scope digest, and
    inject store/clock/revalidator. Opens no route and persists nothing."""
    assignment_scope.require_shift(shift.shift_id, principal)
    scope_digest = authorization_scope_digest(workspace_id, principal.user_id, (str(shift.shift_id),))
    clock = clock or _default_clock
    store = InMemoryApplicationMemoryStore()
    revalidator = _build_revalidator(
        ledger, project_knowledge=project_knowledge, clock=clock, bound_shift_id=shift.shift_id
    )
    memory = ApplicationMemory(store, clock=clock, revalidator=revalidator)
    return BoundApplicationMemory(
        memory=memory, owner_id=principal.user_id, shift_id=shift.shift_id,
        authorization_scope_digest=scope_digest,
    )


__all__ = [
    "WORKSPACE_ID",
    "BoundApplicationMemory",
    "build_application_memory",
    "scope_digest_for",
]
