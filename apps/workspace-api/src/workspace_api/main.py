from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from workspace_api.auth.router import router as auth_router
from workspace_api.api.health.router import router as health_router
from workspace_api.api.shifts.router import router as shifts_router
from workspace_api.api.messages.router import router as messages_router
from workspace_api.api.events.router import router as events_router
from workspace_api.api.corrections.router import router as corrections_router
from workspace_api.api.tasks.router import router as tasks_router
from workspace_api.api.customer_requests.router import router as customer_requests_router
from workspace_api.api.approvals.router import router as approvals_router
from workspace_api.api.incidents.router import router as incidents_router
from workspace_api.api.handovers.router import router as handovers_router
from workspace_api.api.reports.router import router as reports_router
from workspace_api.api.staffing.router import router as staffing_router
from workspace_api.api.external_identities.router import router as external_identities_router
from workspace_api.api.conversation_routes.router import router as conversation_routes_router
from workspace_api.external_ingress.router import router as external_ingress_router
from workspace_api.config import settings
from workspace_api.middleware.request_id import RequestIdMiddleware

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(shifts_router)
app.include_router(messages_router)
app.include_router(events_router)
app.include_router(corrections_router)
app.include_router(tasks_router)
app.include_router(customer_requests_router)
app.include_router(approvals_router)
app.include_router(incidents_router)
app.include_router(handovers_router)
app.include_router(reports_router)
app.include_router(staffing_router)
app.include_router(external_identities_router)
app.include_router(conversation_routes_router)
app.include_router(external_ingress_router)


def _compose_external_ingress_service():
    """P4-E SPEC R10/AC-16/completion-review F7: durable Ledger-backed
    composition, or FAIL CLOSED - never a process-local fallback wired
    into the mounted app. Returns ``None`` when no durable Ledger is
    configured; the router already refuses with 503 when
    ``app.state.external_ingress_service`` is ``None`` (see
    ``external_ingress/router.py``), so this is a real fail-closed
    default, not a silent degrade. ``InMemoryExternalIngressRepository``
    remains importable for explicitly test-only construction (see
    ``tests/integration/test_p4e_workspace_composition.py``), but
    ``main.py`` itself never instantiates it.

    Pre-existing, unrelated to P4-E: without ``DATABASE_URL``,
    ``get_ledger()`` returns ``InMemoryLedger`` (``ledger_factory.py``'s own
    documented "tests, offline/degraded mode"). Repairing that pre-existing
    in-memory default for every OTHER vertical is out of this tranche's
    scope (DESIGN section 9); P4-E's own boundary is simply to refuse
    rather than pretend durability it cannot provide.

    The service-assertion key registry here is a disposable, deterministic
    local key (SPEC R21: BUILD makes zero provider/network calls; no real
    credential). Cross-service key provisioning between Integration Edge
    and Workspace API is pre-existing, unconfigured infrastructure debt
    outside this tranche (DESIGN section 9 forbids repairing unrelated
    P4-C/P4-D implementation debt); this uses the SAME real
    ``verify_service_assertion`` path Integration Edge's own
    ``verification/service_assertion.py`` defines, never a bypass."""
    from datetime import datetime, timezone

    from channel_sdk import ServiceAssertionV1
    from integration_edge.verification.service_assertion import (
        InMemoryNonceStore, ServiceAssertionKey, ServiceKeyRegistry, verify_service_assertion,
    )

    from workspace_api.dependencies import _P4E_WORKSPACE_DIGEST, _p4e_key_authority, get_ledger
    from workspace_api.external_ingress.repository import LedgerExternalIngressRepository
    from workspace_api.external_ingress.service import ExternalIngressService
    from workspace_api.application.p4e_placement import P4ePlacementProcessor

    ledger = get_ledger()
    if not hasattr(ledger, "add_p4e_proposal"):
        return None
    repository = LedgerExternalIngressRepository(ledger)
    processor = P4ePlacementProcessor(ledger, _P4E_WORKSPACE_DIGEST, _p4e_key_authority())

    key_registry = ServiceKeyRegistry({
        "p4e-dev-service-key-1": ServiceAssertionKey(
            secret=b"0" * 32,
            not_before=datetime(2020, 1, 1, tzinfo=timezone.utc),
            not_after=datetime(2999, 1, 1, tzinfo=timezone.utc),
            issuer="integration-edge", subject="workspace-api",
        )
    })
    nonce_store = InMemoryNonceStore()

    def _verifier(assertion: str, *, audience: str, operation: str, body: bytes):
        parsed = ServiceAssertionV1.model_validate_json(assertion)
        return verify_service_assertion(
            parsed, key_registry=key_registry, nonce_store=nonce_store,
            expected_audience=audience, expected_operation=operation,
            expected_method="POST", expected_path="/external-ingress/proposals",
            body=body,
        )

    return ExternalIngressService(repository, _verifier, placement_processor=processor)


app.state.external_ingress_service = _compose_external_ingress_service()
