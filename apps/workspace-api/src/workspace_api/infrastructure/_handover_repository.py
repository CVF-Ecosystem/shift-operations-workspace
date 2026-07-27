"""In-memory handover storage mixin (P2A-HANDOVER-VERTICAL).

Split out of ``repository.py`` (SPEC R13 / ADR section 3.8) to keep that host
module a thin wiring surface, matching ``_incident_repository.py``'s pattern.
``_HandoverRepositoryMixin`` expects ``self._lock``, ``self.handovers``,
``self.shifts``, ``self.tasks``, ``self.customer_requests`` and
``self.incidents`` to already exist (set up by ``InMemoryLedger.__init__``);
it owns no state of its own.

``open_work_snapshot`` is the InMemory half of the server-derived open-work
set (SPEC R3): filters the exact mandatory predicate per record type directly
off the ledger's own dicts, never off caller input. ``model_copy(deep=True)``
is required (not the shallow ``model_copy()`` other mixins use) because a
``Handover`` nests a mutable ``items`` list of ``HandoverItem`` objects - a
shallow copy would still let a caller mutate a stored item through the
returned reference.

HOV-REV-F7 (SPEC R21/R22, WO Amendment 2 section 4): ``add_handover`` and
``put_handover`` prevalidate the SAME controlled ``ValueError`` categories
SqlLedger enforces, entirely before any dict mutation, so a rejection here
is always a complete no-op - not a partial write - by construction (there is
no partial-commit concept to guard against once validation runs first).

HOV-REV-F9: the immutability comparator previously covered only
``(record_type, record_id, digest)`` per item, so ``summary``, ``evidence``
and the aggregate's own ``created_at`` could be silently mutated through
``put_handover``. ``_full_item_key``/``_items_key`` now cover every
``HandoverItem`` field (including ``item_id``, ``handover_id``, ``owner_id``,
``due_at``, ``risk_class`` and all evidence fields), and
``_assert_put_is_lifecycle_only`` also rejects a changed ``created_at``.

HOV-REV-F11: ``_items_key``/``_evidence_key`` returned a plain ``set``/
``frozenset``, which collapses an identical duplicate element - an incoming
snapshot with a real item (or evidence entry) doubled compared to the stored
one hashed to the SAME set as the original, so the "immutable" check silently
accepted the mutation. ``_multiset_key`` fixes this: it is still
order-independent (built from ``frozenset``) but multiplicity-sensitive
(each distinct element carries its own count via ``collections.Counter`),
so ``[x]`` and ``[x, x]`` now hash differently.
"""

from __future__ import annotations

from collections import Counter
from uuid import UUID

from operations_domain.models import (
    CustomerRequestStatus,
    Handover,
    IncidentStatus,
    TaskStatus,
)

_TASK_OPEN_EXCLUDED = {TaskStatus.DONE, TaskStatus.CANCELLED}


def _item_key(item) -> tuple[str, str]:
    return (item.source_record_type, str(item.source_record_id))


def _dt_key(value):
    return value.isoformat() if value else None


def _multiset_key(elements) -> frozenset:
    """Order-independent AND multiplicity-sensitive (HOV-REV-F11): a
    ``Counter`` groups equal hashable elements with their count, and
    ``frozenset(counter.items())`` makes that count-preserving grouping
    itself hashable and order-independent - unlike a bare ``set``/
    ``frozenset`` of the elements, which discards how many times each one
    appeared."""
    return frozenset(Counter(elements).items())


def _evidence_key(evidence) -> frozenset:
    return _multiset_key((str(e.evidence_id), e.source_type, e.source_id, e.sha256) for e in evidence)


def _full_item_key(item) -> tuple:
    """HOV-REV-F9: every HandoverItem field, not just (type, id, digest)."""
    return (
        str(item.item_id), str(item.handover_id), item.source_record_type,
        str(item.source_record_id), item.source_digest, item.summary,
        item.owner_id, _dt_key(item.due_at), str(item.risk_class),
        _evidence_key(item.evidence),
    )


def _items_key(items) -> frozenset:
    return _multiset_key(_full_item_key(i) for i in items)


class _HandoverRepositoryMixin:
    def open_work_snapshot(self, shift_id: UUID, *, unit=None) -> dict[str, list]:
        with self._lock:
            tasks = sorted(
                (
                    t.model_copy()
                    for t in self.tasks.values()
                    if t.shift_id == shift_id and t.status not in _TASK_OPEN_EXCLUDED
                ),
                key=lambda r: r.task_id,
            )
            requests = sorted(
                (
                    r.model_copy()
                    for r in self.customer_requests.values()
                    if r.shift_id == shift_id and r.status != CustomerRequestStatus.CLOSED
                ),
                key=lambda r: r.request_id,
            )
            incidents = sorted(
                (
                    i.model_copy()
                    for i in self.incidents.values()
                    if i.shift_id == shift_id and i.status != IncidentStatus.CLOSED
                ),
                key=lambda r: r.incident_id,
            )
        return {"Task": tasks, "CustomerRequest": requests, "Incident": incidents}

    def _assert_new_handover_valid(self, handover: Handover) -> None:
        if handover.from_shift_id not in self.shifts:
            raise ValueError(f"source shift not found: {handover.from_shift_id}")
        if handover.to_shift_id not in self.shifts:
            raise ValueError(f"destination shift not found: {handover.to_shift_id}")
        if handover.handover_id in self.handovers:
            raise ValueError(f"duplicate handover_id: {handover.handover_id}")
        seen: set[tuple[str, str]] = set()
        for item in handover.items:
            if item.handover_id != handover.handover_id:
                raise ValueError(
                    f"handover item aggregate mismatch: item {item.item_id} "
                    f"belongs to {item.handover_id}, not {handover.handover_id}"
                )
            key = _item_key(item)
            if key in seen:
                raise ValueError(f"duplicate handover item source: {key}")
            seen.add(key)

    def add_handover(self, handover: Handover, *, unit=None) -> Handover:
        with self._lock:
            self._assert_new_handover_valid(handover)
            stored = handover.model_copy(deep=True)
            self.handovers[handover.handover_id] = stored
            return stored.model_copy(deep=True)

    def get_handover(self, handover_id: UUID, *, unit=None) -> Handover:
        with self._lock:
            return self.handovers[handover_id].model_copy(deep=True)

    def list_handovers_for_shift(self, shift_id: UUID, *, unit=None) -> list[Handover]:
        with self._lock:
            return sorted(
                (h.model_copy(deep=True) for h in self.handovers.values() if h.from_shift_id == shift_id),
                key=lambda h: (h.created_at, h.handover_id),
            )

    def _assert_put_is_lifecycle_only(self, current: Handover, incoming: Handover) -> None:
        if incoming.from_shift_id != current.from_shift_id or incoming.to_shift_id != current.to_shift_id:
            raise ValueError(f"handover snapshot is immutable: shift pair changed for {incoming.handover_id}")
        if incoming.created_by != current.created_by:
            raise ValueError(f"handover snapshot is immutable: created_by changed for {incoming.handover_id}")
        if _dt_key(incoming.created_at) != _dt_key(current.created_at):
            raise ValueError(f"handover snapshot is immutable: created_at changed for {incoming.handover_id}")
        if _items_key(incoming.items) != _items_key(current.items):
            raise ValueError(f"handover snapshot is immutable: items changed for {incoming.handover_id}")

    def put_handover(self, handover: Handover, *, unit=None) -> Handover:
        with self._lock:
            current = self.handovers.get(handover.handover_id)
            if current is None:
                raise KeyError(handover.handover_id)
            self._assert_put_is_lifecycle_only(current, handover)
            updated = current.model_copy(deep=True)
            updated.status = handover.status
            updated.reviewed_by = handover.reviewed_by
            updated.reviewed_at = handover.reviewed_at
            updated.received_by = handover.received_by
            updated.acknowledged_at = handover.acknowledged_at
            updated.version = handover.version
            self.handovers[handover.handover_id] = updated
            return updated.model_copy(deep=True)
