"""Unit tests for each CVF gate against the real application profile.

These prove the gates actually enforce the YAML policy, not that files exist.
"""

import pytest

from cvf_runtime.approval import Approval, assert_approval_satisfied
from cvf_runtime.errors import CvfDenied
from cvf_runtime.evidence import assert_evidence_sufficient
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority, require_action
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


# --- approval -------------------------------------------------------------

def _confirmer():
    return Principal(user_id="sup1", role="shift_supervisor")


def test_r1_needs_no_quorum(profile):
    assert_approval_satisfied(
        profile=profile, risk_class="R1", confirmer=_confirmer(), approvals=[]
    )


def test_r3_dual_requires_two_distinct_roles(profile):
    # Only one seat filled -> denied.
    with pytest.raises(CvfDenied) as exc:
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            approvals=[Approval(approver_id="a1", role="shift_supervisor")],
        )
    assert exc.value.control == "approval"


def test_r3_same_person_cannot_fill_two_seats(profile):
    # One principal with high authority cannot satisfy a two-seat quorum alone.
    with pytest.raises(CvfDenied):
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            approvals=[
                Approval(approver_id="a1", role="responsible_manager"),
                Approval(approver_id="a1", role="responsible_manager"),
            ],
        )


def test_r3_two_distinct_authorized_approvers_pass(profile):
    # sup2/mgr1 must be registered in known-principals.yaml for this to pass -
    # this is the P-FIX-3 known-principal check, not just quorum shape.
    assert_approval_satisfied(
        profile=profile,
        risk_class="R3",
        confirmer=_confirmer(),
        approvals=[
            Approval(approver_id="sup2", role="shift_supervisor"),
            Approval(approver_id="mgr1", role="responsible_manager"),
        ],
    )


def test_r4_escalation_board_roles(profile):
    # R4 requires responsible_manager + authorized_executive.
    with pytest.raises(CvfDenied):
        assert_approval_satisfied(
            profile=profile,
            risk_class="R4",
            confirmer=_confirmer(),
            approvals=[Approval(approver_id="mgr1", role="responsible_manager")],
        )
    assert_approval_satisfied(
        profile=profile,
        risk_class="R4",
        confirmer=_confirmer(),
        approvals=[
            Approval(approver_id="mgr1", role="responsible_manager"),
            Approval(approver_id="exec1", role="authorized_executive"),
        ],
    )
