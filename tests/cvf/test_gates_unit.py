"""Unit tests for each CVF gate against the real application profile.

These prove the gates actually enforce the YAML policy, not that files exist.
"""

from dataclasses import dataclass
from itertools import permutations

import pytest

from cvf_runtime.approval import assert_approval_satisfied
from cvf_runtime.errors import CvfDenied
from cvf_runtime.evidence import assert_evidence_sufficient
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority, may_perform, require_action
from cvf_runtime.policy_loader import load_profile
from cvf_runtime.risk import requirement_for


@pytest.fixture
def profile():
    return load_profile()


# --- identity -------------------------------------------------------------

def test_identity_rejects_unknown_role():
    with pytest.raises(ValueError):
        Principal(user_id="u1", role="wizard")


def test_identity_rejects_empty_user():
    with pytest.raises(ValueError):
        Principal(user_id="   ", role="operator")


# --- permission -----------------------------------------------------------

def test_permission_operator_cannot_confirm():
    operator = Principal(user_id="u1", role="operator")
    with pytest.raises(CvfDenied) as exc:
        require_action(operator, "event.confirm")
    assert exc.value.control == "permission"


def test_permission_supervisor_can_confirm():
    sup = Principal(user_id="u2", role="shift_supervisor")
    require_action(sup, "event.confirm")  # does not raise


def test_authority_ordering():
    assert has_authority("responsible_manager", "shift_supervisor")
    assert not has_authority("operator", "shift_supervisor")


def test_permission_map_has_exactly_shift_assignment_manage_supervisor_added():
    """P2C-MUTATION-FULL-UI-C3A1 (SPEC R5): shift.assignment.manage requires
    at least shift_supervisor."""
    require_action(Principal(user_id="sup1", role="shift_supervisor"), "shift.assignment.manage")
    with pytest.raises(CvfDenied) as exc:
        require_action(Principal(user_id="op1", role="operator"), "shift.assignment.manage")
    assert exc.value.control == "permission"


def test_may_perform_is_the_non_raising_boolean_form():
    assert may_perform("shift_supervisor", "shift.assignment.manage") is True
    assert may_perform("operator", "shift.assignment.manage") is False
    assert may_perform("operator", "not-a-real-action") is False


# --- risk -> requirement --------------------------------------------------

def test_requirement_reads_profile(profile):
    r3 = requirement_for(profile, "R3")
    assert r3.required_roles == ["shift_supervisor", "responsible_manager"]
    assert r3.min_evidence == 1
    r4 = requirement_for(profile, "R4")
    assert r4.min_evidence == 2


# --- evidence -------------------------------------------------------------

def test_evidence_blocks_when_insufficient(profile):
    with pytest.raises(CvfDenied) as exc:
        assert_evidence_sufficient(profile=profile, risk_class="R4", evidence_count=1)
    assert exc.value.control == "evidence"


def test_evidence_passes_when_sufficient(profile):
    assert_evidence_sufficient(profile=profile, risk_class="R4", evidence_count=2)


def test_evidence_r0_needs_none(profile):
    assert_evidence_sufficient(profile=profile, risk_class="R0", evidence_count=0)


# --- approval ---------------------------------------------------------------
# P2B-APPROVER-IDENTITY-RECONCILIATION: assert_approval_satisfied no longer
# takes a caller-supplied ``approvals`` list - it takes server-collected
# ``receipts`` (structural minimum: ``approver_id``) and a fresh
# ``authority_for`` resolver. These unit tests build minimal receipt-like
# objects and a plain dict-backed authority map directly, without touching
# any ledger/HTTP machinery - see test_approver_identity_reconciliation.py
# for the full authenticated-receipt vertical (service + HTTP, both
# backends).


@dataclass
class _Receipt:
    approver_id: str


def _confirmer():
    return Principal(user_id="sup1", role="shift_supervisor")


def _authority_map(roles: dict[str, str]):
    return roles.get


def test_r1_needs_no_quorum(profile):
    assert_approval_satisfied(
        profile=profile,
        risk_class="R1",
        confirmer=_confirmer(),
        receipts=[],
        authority_for=_authority_map({}),
    )


def test_r3_dual_requires_two_distinct_roles(profile):
    # Only one seat filled -> denied.
    with pytest.raises(CvfDenied) as exc:
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            receipts=[_Receipt("a1")],
            authority_for=_authority_map({"a1": "shift_supervisor"}),
        )
    assert exc.value.control == "approval"


def test_r3_same_person_cannot_fill_two_seats(profile):
    # One principal with high authority cannot satisfy a two-seat quorum
    # alone - a receipt is keyed by approver_id, so "two receipts from the
    # same approver" collapses to one candidate in the matching.
    with pytest.raises(CvfDenied):
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            receipts=[_Receipt("a1"), _Receipt("a1")],
            authority_for=_authority_map({"a1": "responsible_manager"}),
        )


def test_r3_two_distinct_authorized_approvers_pass(profile):
    assert_approval_satisfied(
        profile=profile,
        risk_class="R3",
        confirmer=_confirmer(),
        receipts=[_Receipt("sup2"), _Receipt("mgr1")],
        authority_for=_authority_map(
            {"sup2": "shift_supervisor", "mgr1": "responsible_manager"}
        ),
    )


def test_r4_escalation_board_roles(profile):
    # R4 requires responsible_manager + authorized_executive.
    with pytest.raises(CvfDenied):
        assert_approval_satisfied(
            profile=profile,
            risk_class="R4",
            confirmer=_confirmer(),
            receipts=[_Receipt("mgr1")],
            authority_for=_authority_map({"mgr1": "responsible_manager"}),
        )
    assert_approval_satisfied(
        profile=profile,
        risk_class="R4",
        confirmer=_confirmer(),
        receipts=[_Receipt("mgr1"), _Receipt("exec1")],
        authority_for=_authority_map(
            {"mgr1": "responsible_manager", "exec1": "authorized_executive"}
        ),
    )


def test_inactive_or_removed_approver_does_not_count(profile):
    """authority_for returning None (missing/inactive user) must not count -
    even though a receipt for that approver_id exists."""
    with pytest.raises(CvfDenied) as exc:
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            receipts=[_Receipt("sup2"), _Receipt("mgr1")],
            authority_for=_authority_map({"sup2": "shift_supervisor"}),  # mgr1 missing
        )
    assert exc.value.control == "approval"


def test_self_approval_alone_denied_for_single_seat_risk(profile):
    """R2 needs one seat (shift_supervisor); the confirmer filling it alone
    must still be denied."""
    with pytest.raises(CvfDenied) as exc:
        assert_approval_satisfied(
            profile=profile,
            risk_class="R2",
            confirmer=_confirmer(),
            receipts=[_Receipt("sup1")],
            authority_for=_authority_map({"sup1": "shift_supervisor"}),
        )
    assert exc.value.control == "approval"


def test_self_approval_with_distinct_valid_r2_approver_passes(profile):
    """F15: R2 needs one seat; if confirmer is in receipts but another valid
    R2 approver is also present, it must succeed."""
    assert_approval_satisfied(
        profile=profile,
        risk_class="R2",
        confirmer=_confirmer(),  # sup1
        receipts=[_Receipt("sup1"), _Receipt("sup2")],
        authority_for=_authority_map(
            {"sup1": "shift_supervisor", "sup2": "shift_supervisor"}
        ),
    )


# --- order-invariant quorum matching (F9 fix, AC-23) -----------------------
# ADR section 4.7 / SPEC R3.6: a probe found the ORIGINAL greedy matcher
# order-dependent on this exact R3 quorum - [shift_supervisor,
# responsible_manager] receipt order PASSed, [responsible_manager,
# shift_supervisor] DENIED, even though both name the same two genuinely
# qualifying, distinct approvers. Every permutation below must PASS.


def _r3_authority_map():
    return _authority_map({"sup2": "shift_supervisor", "mgr1": "responsible_manager"})


@pytest.mark.parametrize("order", list(permutations(["sup2", "mgr1"])))
def test_r3_quorum_passes_regardless_of_receipt_order(profile, order):
    assert_approval_satisfied(
        profile=profile,
        risk_class="R3",
        confirmer=_confirmer(),
        receipts=[_Receipt(approver_id) for approver_id in order],
        authority_for=_r3_authority_map(),
    )


@pytest.mark.parametrize("order", list(permutations(["mgr1", "exec1"])))
def test_r4_quorum_passes_regardless_of_receipt_order(profile, order):
    assert_approval_satisfied(
        profile=profile,
        risk_class="R4",
        confirmer=_confirmer(),
        receipts=[_Receipt(approver_id) for approver_id in order],
        authority_for=_authority_map(
            {"mgr1": "responsible_manager", "exec1": "authorized_executive"}
        ),
    )


def test_higher_authority_before_lower_does_not_starve_a_seat(profile):
    """The exact probe shape: a responsible_manager receipt (who also
    qualifies for the shift_supervisor seat) appears FIRST. A greedy
    left-to-right matcher would have claimed the shift_supervisor seat with
    the manager, then found no one left for the responsible_manager seat.
    The order-invariant matcher must still find the valid assignment
    (supervisor -> shift_supervisor seat, manager -> responsible_manager
    seat) and PASS."""
    assert_approval_satisfied(
        profile=profile,
        risk_class="R3",
        confirmer=_confirmer(),
        receipts=[_Receipt("mgr1"), _Receipt("sup2")],
        authority_for=_r3_authority_map(),
    )


def test_order_invariance_does_not_weaken_insufficient_quorum(profile):
    """A genuinely insufficient quorum must still fail regardless of order -
    order-invariance must not turn into an accept-anything gate."""
    for order in permutations(["sup2"]):
        with pytest.raises(CvfDenied) as exc:
            assert_approval_satisfied(
                profile=profile,
                risk_class="R3",
                confirmer=_confirmer(),
                receipts=[_Receipt(a) for a in order],
                authority_for=_r3_authority_map(),
            )
        assert exc.value.control == "approval"
