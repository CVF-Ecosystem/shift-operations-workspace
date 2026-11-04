"""Selected-shift GET allowlist with current stored assignment checks."""

from uuid import UUID

from fastapi import Depends, HTTPException, Request

from workspace_api.demo.read_routes import NO_STORE, mount_read_route, require_demo_viewer
from workspace_api.dependencies import get_ledger

SELECTED_GETS = frozenset({
    "/events", "/shifts/{shift_id}/open-work", "/incidents",
    "/handovers", "/messages", "/tasks", "/customer-requests",
    "/shifts/{shift_id}/capabilities", "/reports",
})


def require_selected_shift(request: Request, principal=Depends(require_demo_viewer),
                           ledger=Depends(get_ledger)):
    raw = request.path_params.get("shift_id") or request.query_params.get("shift_id")
    try:
        shift_id = UUID(raw) if raw else None
        if shift_id is None:
            raise ValueError("missing shift")
        ledger.get_shift(shift_id)
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found",
                            headers=NO_STORE) from exc
    if ledger.get_active_assignment(shift_id, principal.user_id) is None:
        raise HTTPException(status_code=403, detail="Active assignment required",
                            headers=NO_STORE)
    return principal


def mount_selected_gets(app, routers):
    found = set()
    for router in routers:
        for route in router.routes:
            if route.path in SELECTED_GETS and route.methods == {"GET"}:
                mount_read_route(app, route, require_selected_shift)
                found.add(route.path)
    if found != SELECTED_GETS:
        raise RuntimeError("demo selected read allowlist incomplete")
