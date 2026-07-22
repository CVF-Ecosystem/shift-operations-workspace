"""P-FIX-3: approval must reject fabricated approver identities.

A 2026-07-22 independent review (High Finding #4.1) proved the approval gate
checked only quorum SHAPE: a probe using self-asserted supervisor headers and
two entirely fabricated approver identities/roles confirmed an R3 event with
HTTP 200. These tests reproduce that scenario and assert the opposite outcome:
an approver_id not present in known-principals.yaml can no longer fill a
quorum seat, even if the declared role would otherwise satisfy it.
"""

import pytest

from cvf_runtime.approval import Approval, assert_approval_satisfied
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.policy_loader import load_profile


@pytest.fixture
def profile():
    return load_profile()


def _confirmer():
    return Principal(user_id="sup1", role="shift_supervisor")


def test_fabricated_approver_id_rejected(profile):
    """The exact Codex probe shape: two invented approver identities."""
    with pytest.raises(CvfDenied) as exc:
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            approvals=[
                Approval(approver_id="totally-made-up-1", role="shift_supervisor"),
                Approval(approver_id="totally-made-up-2", role="responsible_manager"),
            ],
        )
    assert exc.value.control == "approval"


def test_known_id_with_inflated_role_rejected(profile):
    """op1 is registered as 'operator' in known-principals.yaml - claiming a
    higher role for a real-but-under-authorized id must still fail."""
    with pytest.raises(CvfDenied):
        assert_approval_satisfied(
            profile=profile,
            risk_class="R3",
            confirmer=_confirmer(),
            approvals=[
                Approval(approver_id="op1", role="responsible_manager"),  # inflated
                Approval(approver_id="mgr2", role="responsible_manager"),
            ],
        )


def test_known_principals_with_correct_roles_pass(profile):
    assert_approval_satisfied(
        profile=profile,
        risk_class="R3",
        confirmer=_confirmer(),
        approvals=[
            Approval(approver_id="sup2", role="shift_supervisor"),
            Approval(approver_id="mgr1", role="responsible_manager"),
        ],
    )


def test_known_role_for_returns_none_for_unknown_id(profile):
    assert profile.known_role_for("nobody") is None
    assert profile.known_role_for("sup1") == "shift_supervisor"
