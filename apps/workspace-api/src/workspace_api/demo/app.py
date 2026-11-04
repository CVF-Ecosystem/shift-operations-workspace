"""Separate exact-route synthetic app. Import only inside the isolated child."""

import os

PROFILE = "P5A2-SOURCE-DEMO-LOCAL-1"
if os.environ.get("P5A2_SOURCE_DEMO_PROFILE") != PROFILE:
    raise RuntimeError("synthetic profile marker required")

from fastapi import Depends, FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from workspace_api.config import settings  # noqa: E402
from workspace_api.demo.bundle import load_bundle  # noqa: E402
from workspace_api.demo.coverage import DemoCoverageVerifier  # noqa: E402
from workspace_api.demo.read_routes import mount_top_level_gets, require_demo_viewer  # noqa: E402
from workspace_api.demo.read_routes_shift import mount_selected_gets  # noqa: E402


def _profile_settings():
    forbidden = {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
                 "GEMINI_API_KEY", "DASHSCOPE_API_KEY", "AZURE_OPENAI_API_KEY",
                 "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"}
    if forbidden & os.environ.keys():
        raise RuntimeError("ambient provider credential in demo child")
    if (settings.ai_mode != "NO_AI" or settings.app_env != "source_demo"
            or settings.proactive_source_instance_id != PROFILE
            or settings.cors_allowed_origins != "http://127.0.0.1:5174"
            or settings.allowed_origins() != ["http://127.0.0.1:5174"]):
        raise RuntimeError("invalid synthetic profile settings")
    from sqlalchemy.engine import make_url

    try:
        url = make_url(settings.database_url)
        if (not url.drivername.startswith("postgresql")
                or url.host not in {"127.0.0.1", "localhost"}
                or url.port != 5433 or url.database != "shiftops_p5a2_source_demo"):
            raise ValueError("database identity")
    except Exception as exc:
        raise RuntimeError("invalid owned demo database") from exc


def create_app(*, nonphysical_test_ledger=None) -> FastAPI:
    """Build an exact read-only app; injected ledger is labeled nonphysical."""
    _profile_settings()
    bundle = load_bundle()
    verifier = DemoCoverageVerifier()

    from workspace_api.auth.router import router as auth_router
    from workspace_api.api.health.router import router as health_router
    from workspace_api.api.proactive.router import router as source_router
    from workspace_api.api.shifts.router import router as shifts_router
    from workspace_api.api.staffing.router import router as staffing_router
    from workspace_api.api.events.router import router as events_router
    from workspace_api.api.incidents.router import router as incidents_router
    from workspace_api.api.handovers.router import router as handovers_router
    from workspace_api.api.messages.router import router as messages_router
    from workspace_api.api.tasks.router import router as tasks_router
    from workspace_api.api.customer_requests.router import router as requests_router
    from workspace_api.api.reports.router import router as reports_router
    from workspace_api.dependencies import get_ledger, get_proactive_source_coverage
    from workspace_api.infrastructure.ledger_factory import build_ledger

    ledger = nonphysical_test_ledger if nonphysical_test_ledger is not None else build_ledger()
    if nonphysical_test_ledger is None and ledger.engine.dialect.name != "postgresql":
        raise RuntimeError("demo requires owned PostgreSQL")
    if nonphysical_test_ledger is None:
        from workspace_api.demo.seed import verify_owned_database
        verify_owned_database(ledger, bundle)
    app = FastAPI(title="Synthetic Shift Source", version="1.0.0")
    app.state.demo_evidence_class = (
        "NONPHYSICAL_IN_PROCESS" if nonphysical_test_ledger is not None else "OWNED_POSTGRESQL"
    )
    app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins(),
                       allow_methods=["GET", "POST", "OPTIONS"],
                       allow_headers=["Authorization", "Content-Type"])
    # Mount individual original handlers, never an entire mutation-bearing router.
    for router, path, method in (
        (auth_router, "/auth/login", "POST"),
        (auth_router, "/auth/me", "GET"),
        (source_router, "/proactive/source", "GET"),
    ):
        matching = [route for route in router.routes
                    if route.path == path and route.methods == {method}]
        if len(matching) != 1:
            raise RuntimeError("demo auth/source route missing")
        route = matching[0]
        app.add_api_route(route.path, route.endpoint, methods=[method], name=route.name,
                          response_model=route.response_model,
                          response_class=route.response_class,
                          status_code=route.status_code, tags=route.tags,
                          dependencies=[Depends(require_demo_viewer)] if path == "/auth/me" else None)
    mount_top_level_gets(app, (health_router, shifts_router, staffing_router))
    mount_selected_gets(app, (shifts_router, staffing_router, events_router,
                              incidents_router, handovers_router, messages_router,
                              tasks_router, requests_router, reports_router))
    app.dependency_overrides[get_ledger] = lambda: ledger
    app.dependency_overrides[get_proactive_source_coverage] = lambda: verifier
    return app
