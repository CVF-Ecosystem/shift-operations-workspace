"""SQL handover storage mixin (P2A-HANDOVER-VERTICAL).

Split out of ``sql_ledger.py`` (SPEC R13 / ADR section 3.8) to keep that host
module a thin wiring surface under the hard 300-line file-size guard.
``_HandoverStoreMixin`` expects ``self._open``, ``self.models`` to already
exist (provided by ``SqlLedger``); it owns no state of its own. Row<->model
mapping and the open-work snapshot query for Task/CustomerRequest/Incident
live here rather than in ``_rows.py`` (outside this tranche's authorized
changed set) - self-contained, matching ``_incident_store.py``'s pattern.
Reuses ``_incident_store._row_to_incident`` rather than duplicating incident
row-mapping a second time.

HOV-REV-F7 (SPEC R21/R22, WO Amendment 2 section 4): ``add_handover``
prevalidates shift existence, duplicate aggregate id, duplicate item source
and item/aggregate mismatch - using the SAME connection/unit the mutation
uses - entirely before any INSERT, so a raised ``ValueError`` never leaves a
partial write (the surrounding transaction, owned or caller-supplied, rolls
back atomically either way). No raw ``IntegrityError`` can reach a caller.
``put_handover`` loads the current row/items first and rejects any change
outside the lifecycle-owned columns with the same controlled shape on both
backends.

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
(each distinct element carries its own count via ``collections.Counter``),
so ``[x]`` and ``[x, x]`` now hash differently.
"""

from __future__ import annotations

from collections import Counter
from uuid import UUID

from sqlalchemy import insert, select, update

from operations_ledger import _evidence, _rows
from operations_ledger._incident_store import _row_to_incident
from operations_ledger.tables import (
    customer_requests,
    handover_items,
    handovers,
    incidents,
    shifts,
    tasks,
)

_HANDOVER_ITEM_RECORD_TYPE = "HandoverItem"
_TASK_OPEN_EXCLUDED = ("DONE", "CANCELLED")


def _handover_row(handover) -> dict:
    return {
        "handover_id": handover.handover_id,
        "from_shift_id": handover.from_shift_id,
        "to_shift_id": handover.to_shift_id,
        "status": str(handover.status),
        "created_by": handover.created_by,
        "reviewed_by": handover.reviewed_by,
        "reviewed_at": handover.reviewed_at,
        "received_by": handover.received_by,
        "acknowledged_at": handover.acknowledged_at,
        "version": handover.version,
    }


def _item_row(item) -> dict:
    return {
        "item_id": item.item_id,
        "handover_id": item.handover_id,
        "source_record_type": item.source_record_type,
        "source_record_id": item.source_record_id,
        "source_digest": item.source_digest,
        "summary": item.summary,
        "owner_id": item.owner_id,
        "due_at": item.due_at,
        "risk": str(item.risk_class),
    }


def _item_key(item) -> tuple[str, str]:
    return (item.source_record_type, str(item.source_record_id))


def _dt_key(value):
    return value.isoformat() if value else None


def _multiset_key(elements) -> frozenset:
    """Order-independent AND multiplicity-sensitive (HOV-REV-F11): see the
    matching helper/docstring in ``_handover_repository.py``."""
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


class _HandoverStoreMixin:
    def open_work_snapshot(self, shift_id: UUID, *, unit=None) -> dict[str, list]:
        with self._open(unit) as c:
            task_rows = c.execute(
                select(tasks).where(
                    tasks.c.shift_id == shift_id, tasks.c.status.notin_(_TASK_OPEN_EXCLUDED)
                )
            ).mappings().all()
            task_list = [
                _rows.row_to_task(
                    self.models, r,
                    evidence=_evidence.evidence_for(c, self.models, record_type="Task", record_id=r["task_id"]),
                )
                for r in task_rows
            ]

            request_rows = c.execute(
                select(customer_requests).where(
                    customer_requests.c.shift_id == shift_id,
                    customer_requests.c.status != "CLOSED",
                )
            ).mappings().all()
            request_list = [_rows.row_to_customer_request(self.models, r) for r in request_rows]

            incident_rows = c.execute(
                select(incidents).where(
                    incidents.c.shift_id == shift_id, incidents.c.status != "CLOSED"
                )
            ).mappings().all()
            incident_list = [
                _row_to_incident(
                    self.models, r,
                    evidence=_evidence.evidence_for(c, self.models, record_type="Incident", record_id=r["incident_id"]),
                )
                for r in incident_rows
            ]
        return {
            "Task": sorted(task_list, key=lambda t: t.task_id),
            "CustomerRequest": sorted(request_list, key=lambda r: r.request_id),
            "Incident": sorted(incident_list, key=lambda i: i.incident_id),
        }

    def _load_items(self, c, handover_id) -> list:
        rows = c.execute(
            select(handover_items).where(handover_items.c.handover_id == handover_id)
        ).mappings().all()
        return [
            self.models.HandoverItem(
                item_id=r["item_id"], handover_id=r["handover_id"],
                source_record_type=r["source_record_type"], source_record_id=r["source_record_id"],
                source_digest=r["source_digest"], summary=r["summary"], owner_id=r["owner_id"],
                due_at=r["due_at"], risk_class=r["risk"],
                evidence=_evidence.evidence_for(
                    c, self.models, record_type=_HANDOVER_ITEM_RECORD_TYPE, record_id=r["item_id"]
                ),
            )
            for r in rows
        ]

    def _row_to_handover(self, row, items) -> object:
        return self.models.Handover(
            handover_id=row["handover_id"], from_shift_id=row["from_shift_id"],
            to_shift_id=row["to_shift_id"], status=row["status"], items=items,
            created_by=row["created_by"], reviewed_by=row["reviewed_by"],
            reviewed_at=row["reviewed_at"], received_by=row["received_by"],
            acknowledged_at=row["acknowledged_at"], version=row["version"],
            created_at=row["created_at"],
        )

    def _assert_new_handover_valid(self, c, handover) -> None:
        existing_shift_ids = {
            r["shift_id"] for r in c.execute(
                select(shifts.c.shift_id).where(
                    shifts.c.shift_id.in_([handover.from_shift_id, handover.to_shift_id])
                )
            ).mappings().all()
        }
        if handover.from_shift_id not in existing_shift_ids:
            raise ValueError(f"source shift not found: {handover.from_shift_id}")
        if handover.to_shift_id not in existing_shift_ids:
            raise ValueError(f"destination shift not found: {handover.to_shift_id}")

        existing = c.execute(
            select(handovers.c.handover_id).where(handovers.c.handover_id == handover.handover_id)
        ).first()
        if existing is not None:
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

    def add_handover(self, handover, *, unit=None):
        with self._open(unit) as c:
            self._assert_new_handover_valid(c, handover)
            c.execute(insert(handovers).values(**_handover_row(handover)))
            for item in handover.items:
                c.execute(insert(handover_items).values(**_item_row(item)))
                _evidence.insert_evidence(
                    c, item.evidence, record_type=_HANDOVER_ITEM_RECORD_TYPE, record_id=item.item_id
                )
        return handover

    def get_handover(self, handover_id: UUID, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(handovers).where(handovers.c.handover_id == handover_id)
            ).mappings().first()
            if row is None:
                raise KeyError(handover_id)
            items = self._load_items(c, handover_id)
        return self._row_to_handover(row, items)

    def list_handovers_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        with self._open(unit) as c:
            rows = c.execute(
                select(handovers)
                .where(handovers.c.from_shift_id == shift_id)
                .order_by(handovers.c.created_at, handovers.c.handover_id)
            ).mappings().all()
            return [self._row_to_handover(row, self._load_items(c, row["handover_id"])) for row in rows]

    def _assert_put_is_lifecycle_only(self, current, incoming) -> None:
        if incoming.from_shift_id != current.from_shift_id or incoming.to_shift_id != current.to_shift_id:
            raise ValueError(f"handover snapshot is immutable: shift pair changed for {incoming.handover_id}")
        if incoming.created_by != current.created_by:
            raise ValueError(f"handover snapshot is immutable: created_by changed for {incoming.handover_id}")
        if _dt_key(incoming.created_at) != _dt_key(current.created_at):
            raise ValueError(f"handover snapshot is immutable: created_at changed for {incoming.handover_id}")
        if _items_key(incoming.items) != _items_key(current.items):
            raise ValueError(f"handover snapshot is immutable: items changed for {incoming.handover_id}")

    def put_handover(self, handover, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(handovers).where(handovers.c.handover_id == handover.handover_id)
            ).mappings().first()
            if row is None:
                raise KeyError(handover.handover_id)
            current = self._row_to_handover(row, self._load_items(c, handover.handover_id))
            self._assert_put_is_lifecycle_only(current, handover)

            result = c.execute(
                update(handovers).where(handovers.c.handover_id == handover.handover_id)
                .values(
                    status=str(handover.status), reviewed_by=handover.reviewed_by,
                    reviewed_at=handover.reviewed_at, received_by=handover.received_by,
                    acknowledged_at=handover.acknowledged_at, version=handover.version,
                )
            )
            if result.rowcount == 0:
                raise KeyError(handover.handover_id)
        return handover
