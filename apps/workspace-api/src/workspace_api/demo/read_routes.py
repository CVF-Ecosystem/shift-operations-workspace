"""Explicit top-level read route table for the synthetic viewer app."""

from datetime import datetime, timezone

from fastapi import Depends, HTTPException

from workspace_api.dependencies import get_ledger, get_proactive_identity

TOP_LEVEL_GETS = frozenset({
    "/health", "/shifts", "/staffing/shifts", "/staffing/users",
})
NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


def require_demo_viewer(identity=Depends(get_proactive_identity), ledger=Depends(get_ledger)):
    principal, expires_at = identity
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Authentication required", headers=NO_STORE)
    user = ledger.get_user_by_id(principal.user_id)
    if (user is None or not user.is_active or user.role != principal.role
            or user.user_id != "PUBLIC_ACTOR" or user.role != "viewer"):
        raise HTTPException(status_code=403, detail="Demo viewer required", headers=NO_STORE)
    return principal


def mount_read_route(app, route, guard):
    app.add_api_route(
        route.path, route.endpoint, methods=["GET"], name=route.name,
        response_model=route.response_model, response_class=route.response_class,
        status_code=route.status_code, tags=route.tags,
        dependencies=[Depends(guard)] if guard is not None else None,
    )


def mount_top_level_gets(app, routers):
    found = set()
    for router in routers:
        for route in router.routes:
            if route.path in TOP_LEVEL_GETS and route.methods == {"GET"}:
                mount_read_route(app, route, None if route.path == "/health" else require_demo_viewer)
                found.add(route.path)
    if found != TOP_LEVEL_GETS:
        raise RuntimeError("demo read allowlist incomplete")
