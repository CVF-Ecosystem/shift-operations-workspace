"""Exact route surface and guard behavior using a labeled in-process ledger."""

from workspace_api.demo.read_routes import TOP_LEVEL_GETS
from workspace_api.demo.read_routes_shift import SELECTED_GETS


def test_closed_read_allowlist_matches_contract():
    assert TOP_LEVEL_GETS == {
        "/health", "/shifts", "/staffing/shifts", "/staffing/users",
    }
    assert SELECTED_GETS == {
        "/events", "/shifts/{shift_id}/open-work", "/incidents", "/handovers",
        "/messages", "/tasks", "/customer-requests",
        "/shifts/{shift_id}/capabilities", "/reports",
    }
