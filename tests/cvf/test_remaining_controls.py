"""Tests for the four controls that were profile-only until now:
domain_lock, data_scope, cost, termination — each enforced against the real
application profile YAML.
"""

import pytest

from cvf_runtime.budget import BudgetState, assert_within_budget
from cvf_runtime.data_scope import (
    EXTERNAL,
    ENTERPRISE,
    LOCAL,
    assert_placement_allowed,
    requires_minimization,
)
from cvf_runtime.domain_lock import assert_domain_allowed, assert_event_type_in_scope
from cvf_runtime.errors import CvfDenied
from cvf_runtime.policy_loader import load_profile
from cvf_runtime.termination import TaskState, assert_not_terminated, should_terminate


@pytest.fixture
def profile():
    return load_profile()


# --- domain_lock ----------------------------------------------------------

def test_domain_lock_allows_in_scope(profile):
    assert_domain_allowed(profile, "equipment_incident")  # no raise


def test_domain_lock_refuses_out_of_scope(profile):
    with pytest.raises(CvfDenied) as exc:
        assert_domain_allowed(profile, "payroll")
    assert exc.value.control == "domain_lock"


def test_domain_lock_maps_event_type(profile):
    assert_event_type_in_scope(profile, "equipment_downtime")  # maps -> equipment_incident
    with pytest.raises(CvfDenied):
        assert_event_type_in_scope(profile, "unknown_event_type")


# --- data_scope -----------------------------------------------------------

def test_public_allowed_everywhere(profile):
    for placement in (EXTERNAL, ENTERPRISE, LOCAL):
        assert_placement_allowed(profile=profile, classification="PUBLIC", placement=placement)


def test_restricted_local_only(profile):
    assert_placement_allowed(profile=profile, classification="RESTRICTED", placement=LOCAL)
    with pytest.raises(CvfDenied) as exc:
        assert_placement_allowed(profile=profile, classification="RESTRICTED", placement=EXTERNAL)
    assert exc.value.control == "data_scope"


def test_confidential_blocks_external(profile):
    with pytest.raises(CvfDenied):
        assert_placement_allowed(profile=profile, classification="CONFIDENTIAL", placement=EXTERNAL)
    assert_placement_allowed(profile=profile, classification="CONFIDENTIAL", placement=ENTERPRISE)


def test_internal_requires_minimization(profile):
    assert requires_minimization(profile, "INTERNAL") is True
    assert requires_minimization(profile, "PUBLIC") is False


# --- cost / budget --------------------------------------------------------

def test_token_overflow_denied(profile):
    with pytest.raises(CvfDenied) as exc:
        assert_within_budget(
            cost_policy=profile.cost,
            state=BudgetState(),
            requested_tokens=999_999,
        )
    assert exc.value.control == "cost"


def test_within_budget_ok(profile):
    action = assert_within_budget(
        cost_policy=profile.cost,
        state=BudgetState(spent_today_usd=0, spent_month_usd=0),
        requested_tokens=100,
    )
    assert action == "ok"


def test_daily_cap_falls_back_to_rules(profile):
    action = assert_within_budget(
        cost_policy=profile.cost,
        state=BudgetState(spent_today_usd=999),
        requested_tokens=100,
    )
    assert action == "fallback_to_rules"


# --- termination ----------------------------------------------------------

def test_timeout_terminates(profile):
    assert should_terminate(profile.termination, TaskState(elapsed_s=10, timeout_s=5)) == "timeout_exceeded"


def test_kill_switch_terminates(profile):
    with pytest.raises(CvfDenied) as exc:
        assert_not_terminated(profile.termination, TaskState(kill_switch_active=True))
    assert exc.value.control == "termination"


def test_healthy_task_not_terminated(profile):
    assert should_terminate(profile.termination, TaskState(elapsed_s=1, timeout_s=30)) is None
