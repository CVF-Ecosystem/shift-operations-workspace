"""Actual native read followed by current membership and identity release checks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "unit"))
from p5a2_source_api_helpers import (  # noqa: E402
    ApiFixtureCoverage, api_oracle, assert_private_headers, frozen_refusal,
    headers, params, source_client,
)
from workspace_api.dependencies import get_proactive_source_coverage

CASE = api_oracle()["cases"][0]
PATH = "/proactive/source"


class AfterNativeCoverage(ApiFixtureCoverage):
    def __init__(self, case, mutate):
        super().__init__(case)
        self.mutate = mutate

    def verify(self, *args):
        identity = super().verify(*args)
        self.mutate()
        return identity


@pytest.mark.parametrize("change,reason", [
    ("revoke", "ACCESS_DENIED"),
    ("version", "SCOPE_INCOMPLETE"),
    ("boundary", "SCOPE_INCOMPLETE"),
    ("disable_user", "TRANSPORT_403"),
    ("change_role", "TRANSPORT_403"),
])
def test_change_after_native_seal_discards_ready_receipt(change, reason):
    with source_client(case=CASE, coverage=True) as (client, ledger):
        def mutate():
            if change in {"revoke", "version"}:
                assignment = next(iter(ledger.assignments.values()))
                if change == "revoke":
                    assignment.status = "REVOKED"
                else:
                    assignment.version += 1
            elif change == "boundary":
                shift = next(iter(ledger.shifts.values()))
                shift.ends_at = datetime(2026, 1, 10, tzinfo=timezone.utc)
            elif change == "disable_user":
                ledger.users["PUBLIC_ACTOR"].is_active = False
            else:
                ledger.users["PUBLIC_ACTOR"].role = "operator"
        client.app.dependency_overrides[get_proactive_source_coverage] = (
            lambda: AfterNativeCoverage(CASE, mutate)
        )
        response = client.get(PATH, params=params(CASE), headers=headers())
        if reason == "TRANSPORT_403":
            assert response.status_code == 403
            assert response.json() == {"detail": "Access denied"}
        else:
            assert response.status_code == 200
            assert response.json() == frozen_refusal(reason)
        assert "canonical_manifest" not in response.json()
        assert_private_headers(response)


def test_token_expiry_between_buffer_and_final_release():
    calls = 0
    def moving_clock():
        nonlocal calls
        calls += 1
        return datetime.now(timezone.utc) + timedelta(hours=2 if calls > 1 else 0)
    with source_client(case=CASE, coverage=True, clock=moving_clock) as (client, _):
        response = client.get(PATH, params=params(CASE), headers=headers())
        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication required"}
        assert "canonical_manifest" not in response.json()
        assert_private_headers(response)


@pytest.mark.parametrize("failure", ["probe", "fresh"])
def test_unavailable_native_capability_closes_without_exception_text(failure):
    with source_client(case=CASE, coverage=True) as (client, ledger):
        def unavailable(*_args):
            raise RuntimeError("private DSN and driver details")
        if failure == "probe":
            ledger.scoped_source_read = unavailable
        else:
            ledger.fresh_scoped_cohort = unavailable
        response = client.get(PATH, params=params(CASE), headers=headers())
        assert response.status_code == 200
        assert response.json() == frozen_refusal("SOURCE_UNAVAILABLE")
        assert b"private DSN" not in response.content
        assert_private_headers(response)


def test_refusal_after_successful_probe_still_rechecks_membership():
    with source_client(case=CASE) as (client, ledger):
        original = ledger.fresh_scoped_cohort
        def revoked(*args):
            ledger.assignments.clear()
            return original(*args)
        ledger.fresh_scoped_cohort = revoked
        response = client.get(PATH, params=params(CASE), headers=headers())
        assert response.json() == frozen_refusal("ACCESS_DENIED")
        assert_private_headers(response)


def test_added_assignment_after_native_seal_refuses_complete_cohort():
    from uuid import NAMESPACE_DNS, uuid5
    from operations_domain.models import Shift
    from operations_domain.assignment_models import ShiftAssignment
    with source_client(case=CASE, coverage=True) as (client, ledger):
        def add_member():
            start = datetime(2026, 1, 2, 10, tzinfo=timezone.utc)
            shift_id = uuid5(NAMESPACE_DNS, "api-after-seal-shift")
            ledger.shifts[shift_id] = Shift(
                shift_id=shift_id, name="after-seal", starts_at=start,
                ends_at=start + timedelta(hours=1), created_at=start,
            )
            assignment_id = uuid5(NAMESPACE_DNS, "api-after-seal-assignment")
            ledger.assignments[assignment_id] = ShiftAssignment(
                assignment_id=assignment_id, shift_id=shift_id,
                user_id="PUBLIC_ACTOR", assigned_by="PUBLIC_ACTOR", assigned_at=start,
            )
        client.app.dependency_overrides[get_proactive_source_coverage] = (
            lambda: AfterNativeCoverage(CASE, add_member)
        )
        response = client.get(PATH, params=params(CASE), headers=headers())
        assert response.json() == frozen_refusal("SCOPE_INCOMPLETE")
        assert "canonical_manifest" not in response.json()
        assert_private_headers(response)


def test_http_overflow_releases_only_closed_refusal(monkeypatch):
    from workspace_api.api.proactive import response as transport
    ready = CASE["expected_receipt"]
    size = len(transport.bounded_json(ready))
    monkeypatch.setattr(transport, "MAX_RESPONSE_BYTES", size - 1)
    with source_client(case=CASE, coverage=True) as (client, _):
        response = client.get(PATH, params=params(CASE), headers=headers())
        assert response.json() == frozen_refusal("SCOPE_INCOMPLETE")
        assert b"canonical_manifest" not in response.content
        assert_private_headers(response)
