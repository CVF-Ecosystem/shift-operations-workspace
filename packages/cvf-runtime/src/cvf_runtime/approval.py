"""Approval gate.

CVF control: ``approval``. This decides whether a risk class's required
approval quorum is satisfied.

2026-07-22 (P-FIX-3): the original gate accepted ANY caller-supplied
``approver_id``/``role`` pair in the confirmer's own request body as
fabricated authorization - only the quorum *shape* was checked, not the
approver's actual identity/authority. An interim ``known-principals.yaml``
registry check was added (High Finding #4.1).

2026-07-26 (P2B-APPROVER-IDENTITY-RECONCILIATION, closing High Finding #4):
the interim registry check is retired. Approver identity is no longer
asserted by the confirmer - it is proved by the approver's own authenticated
request, persisted as a durable, scope-bound receipt
(``application/approval_service.py``). This gate now decides quorum
satisfaction purely over ``receipts`` (structural minimum: ``approver_id``)
and a server-owned ``authority_for`` resolver that re-derives each approver's
CURRENT role fresh, every time - never trusting a receipt's own stored
``approver_role``.

2026-07-26 revision 2 (F9 fix): quorum satisfaction is now decided by a
deterministic, order-invariant bipartite-matching search (ADR section 4.7 /
SPEC R3.6) rather than a greedy left-to-right scan. A greedy scan let a
higher-authority principal's receipt (processed first) claim a seat that only
a lower-authority principal was left to fill, starving a later seat and
producing a false deny that depended solely on receipt/role-declaration
order - proven by an independent-review probe on an R3 quorum. The matching
decision here depends only on the SET of required seats and the SET of
qualifying receipts, never on the order either is supplied in.
"""

from __future__ import annotations

from typing import Callable, Protocol, Sequence, runtime_checkable

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority
from cvf_runtime.policy_loader import CvfProfile
from cvf_runtime.risk import requirement_for


@runtime_checkable
class ApprovalReceiptLike(Protocol):
    """Structural minimum a receipt must expose for quorum evaluation.

    cvf-runtime is a dependency sink (never imports operations_domain,
    operations_ledger, or workspace_api - see policy_loader.py's module
    docstring), so this is a Protocol rather than the real
    ``operations_domain.models.ApprovalReceipt``. Only ``approver_id`` is
    read here; a receipt's persisted ``approver_role`` is evidence only, not
    current authority (see ``authority_for`` below).
    """

    approver_id: str


def assert_approval_satisfied(
    *,
    profile: CvfProfile,
    risk_class: str,
    confirmer: Principal,
    receipts: Sequence[ApprovalReceiptLike],
    authority_for: Callable[[str], str | None],
) -> None:
    """Raise :class:`CvfDenied` unless the approval quorum is met.

    Rules enforced:
    * Every role the risk class requires must be filled by a receipt whose
      approver's CURRENT authority (``authority_for``, resolved fresh - never
      the receipt's stored ``approver_role``) meets that seat's bar.
    * Distinct required seats must be filled by distinct approvers - no
      single approver fills two seats.
    * A required quorum is never satisfied by the confirmer alone (F15,
      SPEC R3.4/R3.7): the confirmer is sorted to the END of the candidate
      list so Kuhn's augmenting-path search prefers non-confirmer candidates
      first. If the only full matching assigns every seat to the confirmer,
      the quorum is denied without a second search pass.
    * The result is a function of the SET of required roles and the SET of
      qualifying receipts only - never of receipt or required-role order
      (F9 fix, SPEC R3.6).
    """
    requirement = requirement_for(profile, risk_class)
    required_roles = requirement.required_roles
    if not required_roles:
        return  # R0/R1: no approval quorum required.

    # Sort confirmer to end so the augmenting-path search prefers non-confirmer
    # candidates for every seat. Non-confirmer ids are sorted lexicographically
    # first for deterministic traces; confirmer follows them.
    distinct_ids = {receipt.approver_id for receipt in receipts}
    candidate_ids = sorted(
        distinct_ids - {confirmer.user_id}
    ) + ([confirmer.user_id] if confirmer.user_id in distinct_ids else [])
    current_role_by_id = {
        approver_id: authority_for(approver_id) for approver_id in candidate_ids
    }

    assignment = _max_bipartite_matching(
        required_roles=required_roles,
        candidate_ids=candidate_ids,
        current_role_by_id=current_role_by_id,
    )

    if assignment is None or len(assignment) < len(required_roles):
        raise CvfDenied(
            control="approval",
            reason=(
                f"{risk_class} requires approval by roles {required_roles!r} "
                f"from distinct, currently-authorized approvers; quorum not met"
            ),
            http_status=409,
        )

    # F15 (SPEC R3.4/R3.7): confirmer sorted last means if any non-confirmer
    # candidate could have filled a seat, they were preferred. If the result
    # still uses only the confirmer, no non-confirmer can satisfy the quorum.
    if set(assignment.values()) == {confirmer.user_id}:
        raise CvfDenied(
            control="approval",
            reason=f"{risk_class} requires an approver other than the confirmer",
            http_status=409,
        )


def _max_bipartite_matching(
    *,
    required_roles: list[str],
    candidate_ids: list[str],
    current_role_by_id: dict[str, str | None],
) -> dict[int, str] | None:
    """Deterministic maximum bipartite matching (Kuhn's augmenting-path search).

    Seats are the LEFT side, addressed by their INDEX into ``required_roles``
    (not by role name - a future risk class could require the same role for
    two distinct seats). Candidates are the RIGHT side. An edge exists when a
    candidate's fresh current role has authority for a seat's required role.

    This asks only: does a matching exist that fills every seat with a
    distinct candidate? - never "claim the first candidate that fits, in
    scan order", which is the greedy behaviour that produced order-dependent
    false denials (F9). Kuhn's algorithm is guaranteed to find a MAXIMUM
    matching regardless of the order either side is iterated in, so whether a
    full (size == len(required_roles)) matching exists is a property of the
    two SETS involved, not of iteration order.

    Returns a mapping ``{seat_index: approver_id}`` covering every seat, or
    ``None``/a partial mapping if no full matching exists.
    """

    def qualifies(seat_index: int, approver_id: str) -> bool:
        current_role = current_role_by_id.get(approver_id)
        if current_role is None:
            return False
        return has_authority(current_role, required_roles[seat_index])

    # approver_id -> seat_index it is currently assigned to fill.
    seat_for_candidate: dict[str, int] = {}

    def try_assign(seat_index: int, seen: set[str]) -> bool:
        for approver_id in candidate_ids:
            if approver_id in seen or not qualifies(seat_index, approver_id):
                continue
            seen.add(approver_id)
            current_seat = seat_for_candidate.get(approver_id)
            if current_seat is None or try_assign(current_seat, seen):
                seat_for_candidate[approver_id] = seat_index
                return True
        return False

    for seat_index in range(len(required_roles)):
        try_assign(seat_index, set())

    if len(seat_for_candidate) < len(required_roles):
        return None
    return {seat_index: approver_id for approver_id, seat_index in seat_for_candidate.items()}
