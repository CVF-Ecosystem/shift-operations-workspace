"""Immutable server corpus registry (SPEC R4). Pure package module.

The registry is process configuration, never derived from a client value. A
client-supplied ``corpus_id`` is matched against this closed mapping only; it
can never become a path, URL, table/column name, query fragment, filesystem
glob, adapter import, or source location.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from retrieval_contracts.enums import RecordType, TruthClass

from .enums import CorpusId, CorpusState


@dataclass(frozen=True)
class CorpusDescriptor:
    corpus_id: CorpusId
    truth_class: TruthClass
    allowed_record_types: tuple[RecordType, ...]
    state: CorpusState
    max_shift_ids: int
    local_human_operator_allowed: bool
    # RR1-F2 - the closed set of lifecycle status literals this corpus
    # allows a client to narrow by; a non-empty client filter outside this
    # set (or supplied against a corpus that allows none) always widens
    # scope. An empty tuple means the corpus supports zero lifecycle values
    # - any non-empty client filter for it is therefore always widening.
    allowed_lifecycle_statuses: tuple[str, ...] = ()


_SHIFT_CONFIRMED_OPERATIONS_V1 = CorpusDescriptor(
    corpus_id=CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1,
    truth_class=TruthClass.CANONICAL_OPERATIONAL_RECORD,
    allowed_record_types=(
        RecordType.OPERATIONAL_EVENT,
        RecordType.TASK,
        RecordType.CUSTOMER_REQUEST,
        RecordType.INCIDENT,
        RecordType.HANDOVER,
        RecordType.REPORT,
    ),
    state=CorpusState.DEPENDENCY_BLOCKED,
    max_shift_ids=2,
    local_human_operator_allowed=False,
    # R5 - the union of per-record-type eligible lifecycle states for this
    # corpus's six allowed record types (OperationalEvent/Task: CONFIRMED,
    # CORRECTED, FROZEN; Incident: ACKNOWLEDGED, MITIGATING, RESOLVED,
    # CLOSED; Handover: REVIEWED, ACKNOWLEDGED). CustomerRequest/Report have
    # no named lifecycle status filter, so they are excluded from this set.
    allowed_lifecycle_statuses=(
        "ACKNOWLEDGED", "CLOSED", "CONFIRMED", "CORRECTED", "FROZEN", "MITIGATING", "RESOLVED", "REVIEWED",
    ),
)

_SHIFT_ADVISORY_MESSAGES_V1 = CorpusDescriptor(
    corpus_id=CorpusId.SHIFT_ADVISORY_MESSAGES_V1,
    truth_class=TruthClass.ADVISORY_SOURCE_EVIDENCE,
    allowed_record_types=(RecordType.MESSAGE,),
    state=CorpusState.DEPENDENCY_BLOCKED,
    max_shift_ids=2,
    local_human_operator_allowed=False,
    # R5 - Message carries no named lifecycle status in the eligibility
    # matrix (only "INTERNAL persisted, bound to an admitted P3-A
    # candidate"), so this corpus allows zero lifecycle values.
    allowed_lifecycle_statuses=(),
)

_PROJECT_KNOWLEDGE_LOCAL_V1 = CorpusDescriptor(
    corpus_id=CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1,
    truth_class=TruthClass.ADVISORY_SOURCE_EVIDENCE,
    allowed_record_types=(RecordType.PROJECT_KNOWLEDGE,),
    state=CorpusState.LOCAL_ONLY,
    max_shift_ids=1,
    local_human_operator_allowed=True,
    # RR1-F2 - Project Knowledge admission uses disposition/owner/retention
    # (never a lifecycle status literal); it allows zero lifecycle values,
    # so ANY non-empty client lifecycle filter (e.g. "CURRENT") always
    # widens scope, never silently passing through to EVIDENCE_AVAILABLE.
    allowed_lifecycle_statuses=(),
)

CORPUS_REGISTRY: MappingProxyType[CorpusId, CorpusDescriptor] = MappingProxyType(
    {
        CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1: _SHIFT_CONFIRMED_OPERATIONS_V1,
        CorpusId.SHIFT_ADVISORY_MESSAGES_V1: _SHIFT_ADVISORY_MESSAGES_V1,
        CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1: _PROJECT_KNOWLEDGE_LOCAL_V1,
    }
)
"""R4 - immutable process configuration. ``MappingProxyType`` rejects item
assignment/deletion at runtime (``TypeError``); the registry can only be
replaced by rebuilding this module, never mutated by a caller."""


def resolve_corpus(corpus_id: CorpusId) -> CorpusDescriptor:
    """Return the immutable descriptor for ``corpus_id``.

    Raises :class:`KeyError` for any id outside the closed registry - callers
    must have already validated ``corpus_id`` is a member of
    :class:`CorpusId` via R2 structural validation before calling this.
    """
    return CORPUS_REGISTRY[corpus_id]


def is_available(descriptor: CorpusDescriptor) -> bool:
    """True only for a corpus whose state permits a protected read attempt.

    Both operational corpora are ``DEPENDENCY_BLOCKED`` and MUST NOT become
    readable in this tranche; only ``LOCAL_ONLY`` (Project Knowledge) is
    available.
    """
    return descriptor.state == CorpusState.LOCAL_ONLY


def filters_within_descriptor(
    descriptor: CorpusDescriptor,
    record_types: tuple[RecordType, ...],
    truth_classes: tuple[TruthClass, ...],
    lifecycle_statuses: tuple[str, ...] = (),
) -> bool:
    """R4/RR1-F2 - a non-empty filter value must be a subset of what the
    corpus descriptor allows; an empty filter requests the full allowlist.
    ``lifecycle_statuses`` is enforced identically to the other two
    dimensions - a non-empty client value outside
    ``descriptor.allowed_lifecycle_statuses`` (including any value at all
    for a corpus that allows none) always widens scope."""
    if record_types and not set(record_types).issubset(set(descriptor.allowed_record_types)):
        return False
    if truth_classes and not set(truth_classes).issubset({descriptor.truth_class}):
        return False
    if lifecycle_statuses and not set(lifecycle_statuses).issubset(set(descriptor.allowed_lifecycle_statuses)):
        return False
    return True
