"""Sanitized approval-readiness reads (P2C-MUTATION-FULL-UI-C3B1, SPEC
R11/R35/R37).

Readiness answers "is the current stored binding's approval quorum matched
right now", for exactly the four canonical pairs the ADR addendum/SPEC R35
authorize: ``OperationalEvent/event.confirm``, ``Task/task.create`` (whose
``record_id`` is the stored ``TaskCreationIntent`` id),
``Incident/incident.acknowledge`` and ``Report/report.approve``. It is a read,
never an authorization: every later mutation still re-runs identity,
permission, assignment, lifecycle and quorum from scratch
(``approval_receipts.create_approval_receipt``). Readiness is deliberately
requester-independent and never applies the later confirmer/self-approval
rule.

Admission order (R37): validate the canonical pair, apply ``require_action``
for the requested action, resolve the stored target (same lookups
``create_approval_receipt`` uses), then require current ACTIVE assignment.
Missing/inaccessible targets share the common sanitized 404 boundary; an
exact non-current Report returns sanitized 409 only after permission and
assignment succeed (a current binding is used regardless of lifecycle,
because readiness is not lifecycle admission).

Matching is deterministic maximum bipartite matching over required seats
(role names, order and multiplicity preserved) against currently active
approvers holding a receipt for the resolved target — one distinct approver
fills at most one seat. The response never exposes payload digest, receipt
id, approver identity or raw policy internals.
"""

from __future__ import annotations

from dataclasses import dataclass

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority, require_action
from cvf_runtime.policy_loader import load_profile
from cvf_runtime.risk import requirement_for
from operations_ledger import Ledger

from workspace_api.application.approval_receipts import _VALID_RECORD_ACTION_PAIRS
from workspace_api.application.assignment_scope import require_active_assignment

_TARGET_NOT_FOUND = "target not found"


@dataclass(frozen=True)
class ReadinessResult:
    record_type: str
    record_id: object
    action: str
    target_version: int
    risk_class: str
    ready: bool
    required_roles: list[str]
    satisfied_roles: list[str]


def _resolve_target(ledger: Ledger, record_type: str, action: str, record_id):
    """Mirrors ``create_approval_receipt``'s per-type target resolution
    (SPEC R35/R37): same lookups, same not-found mapping, but read-only —
    no receipt, audit or mutation is written here."""
    if record_type == "OperationalEvent":
        try:
            record = ledger.get_event(record_id)
        except KeyError as exc:
            raise CvfDenied(control="approval", reason=_TARGET_NOT_FOUND, http_status=404) from exc
        return record.shift_id, str(record.risk_class), record.version, True
    if record_type == "Incident":
        try:
            record = ledger.get_incident(record_id)
        except KeyError as exc:
            raise CvfDenied(control="approval", reason=_TARGET_NOT_FOUND, http_status=404) from exc
        return record.shift_id, str(record.risk_class), record.version, True
    if record_type == "Report":
        try:
            record = ledger.get_report(record_id)
        except KeyError as exc:
            raise CvfDenied(control="approval", reason=_TARGET_NOT_FOUND, http_status=404) from exc
        # R35/C3B1-WO-REREV-F1: readiness derives the current binding
        # regardless of lifecycle; "is this the current report" is checked by
        # the caller (require_current_report) after assignment, per R37.
        return record.shift_id, "R2", record.version, record.is_current
    # ("Task", "task.create"): record_id is the stored TaskCreationIntent id.
    try:
        intent = ledger.get_task_creation_intent(record_id)
    except KeyError as exc:
        raise CvfDenied(control="approval", reason=_TARGET_NOT_FOUND, http_status=404) from exc
    return intent.shift_id, str(intent.risk_class), 1, True


def _authority_for(ledger: Ledger):
    cache: dict[str, str | None] = {}

    def _lookup(user_id: str) -> str | None:
        if user_id not in cache:
            user = ledger.get_user_by_id(user_id)
            cache[user_id] = user.role if user is not None and user.is_active else None
        return cache[user_id]

    return _lookup


def _eligible_approvers(receipts: list, authority_for) -> list[str]:
    """Distinct currently-active approver ids, deduplicated deterministically
    while preserving first-receipt order (C3B1-BUILD-REV-F1 repair item 4)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for receipt in receipts:
        approver_id = receipt.approver_id
        if approver_id in seen:
            continue
        seen.add(approver_id)
        if authority_for(approver_id) is not None:
            ordered.append(approver_id)
    return ordered


def _try_augment(
    seat_index: int,
    required_roles: list[str],
    approvers: list[str],
    authority_for,
    seat_of_approver: dict[int, int],
    visited: set[int],
) -> bool:
    """One augmenting-path step of Kuhn's algorithm over approver indices for
    ``seat_index``: try every eligible, not-yet-visited-this-attempt approver;
    if one is free, take it; if all are taken, try to displace one whose own
    seat can instead be filled by some other eligible approver."""
    for approver_index, approver_id in enumerate(approvers):
        if approver_index in visited:
            continue
        current_role = authority_for(approver_id)
        if current_role is None or not has_authority(current_role, required_roles[seat_index]):
            continue
        visited.add(approver_index)
        held_seat = seat_of_approver.get(approver_index)
        if held_seat is None or _try_augment(
            held_seat, required_roles, approvers, authority_for, seat_of_approver, visited
        ):
            seat_of_approver[approver_index] = seat_index
            return True
    return False


def _match_seats(required_roles: list[str], receipts: list, authority_for) -> list[str]:
    """Deterministic maximum bipartite matching (SPEC R35): required-seat
    order and multiplicity are preserved; one distinct approver fills at most
    one seat; the result is independent of receipt iteration order
    (C3B1-BUILD-REV-F1). Runs Kuhn's augmenting-path algorithm seat-by-seat in
    declared seat order over the distinct eligible-approver list, so an
    already-matched approver can be displaced onto a different seat it also
    qualifies for when that raises the total number of matched seats — a
    scenario plain greedy left-to-right assignment misses whenever a single
    higher-authority approver could satisfy an earlier seat but is the only
    approver present for a later one."""
    approvers = _eligible_approvers(receipts, authority_for)
    seat_of_approver: dict[int, int] = {}
    for seat_index in range(len(required_roles)):
        _try_augment(seat_index, required_roles, approvers, authority_for, seat_of_approver, set())
    matched_seats = set(seat_of_approver.values())
    return [required_roles[i] for i in range(len(required_roles)) if i in matched_seats]


def evaluate_readiness(
    ledger: Ledger,
    principal: Principal,
    *,
    record_type: str,
    action: str,
    record_id,
) -> ReadinessResult:
    if (record_type, action) not in _VALID_RECORD_ACTION_PAIRS or action not in (
        "event.confirm", "task.create", "incident.acknowledge", "report.approve",
    ):
        raise CvfDenied(
            control="approval",
            reason=f"unknown readiness pair: ({record_type!r}, {action!r})",
            http_status=422,
        )

    require_action(principal, action)
    shift_id, risk_class, target_version, is_current = _resolve_target(
        ledger, record_type, action, record_id
    )
    require_active_assignment(ledger, shift_id, principal)
    if record_type == "Report" and not is_current:
        raise CvfDenied(
            control="approval", reason="report is not the current version", http_status=409,
        )

    profile = load_profile()
    required_roles = requirement_for(profile, risk_class).required_roles
    receipts = ledger.list_approval_receipts_for(
        record_type=record_type,
        record_id=record_id,
        action=action,
        target_version=target_version,
        risk_class=risk_class,
        payload_digest=None if record_type != "Report" else _current_report_digest(ledger, record_id),
    )
    satisfied = _match_seats(list(required_roles), receipts, _authority_for(ledger))
    return ReadinessResult(
        record_type=record_type,
        record_id=record_id,
        action=action,
        target_version=target_version,
        risk_class=risk_class,
        ready=len(satisfied) == len(required_roles),
        required_roles=list(required_roles),
        satisfied_roles=satisfied,
    )


def _current_report_digest(ledger: Ledger, record_id) -> str | None:
    # Report receipts bind payload_digest = the stored current snapshot
    # digest (approval_receipts.create_approval_receipt); readiness must
    # match on the SAME digest to find the SAME receipts, never a
    # caller-supplied value.
    report = ledger.get_report(record_id)
    return report.content.snapshot_digest
