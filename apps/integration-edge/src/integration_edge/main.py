from datetime import datetime, timezone

from channel_adapters import GenericWebhookAdapter, GenericWebhookConfig, StdlibResolvedHttpsTransport
from fastapi import FastAPI

from integration_edge.health import EdgeReadiness
from integration_edge.webhook.router import router

def create_app(
    *,
    adapter_id=None,
    webhook_config=None,
    resolver=None,
    transport=None,
    secret_resolver=None,
    clock=None,
    store=None,
    assertion_verifier=None,
    scope_bindings=(),
):
    application = FastAPI(title="Shift Operations Integration Edge", version="0.1.0")
    application.include_router(router)
    adapter = None
    if adapter_id == "generic-webhook" and isinstance(webhook_config, GenericWebhookConfig):
        if resolver is not None and secret_resolver is not None:
            adapter = GenericWebhookAdapter(
                config=webhook_config,
                resolver=resolver,
                transport=transport or StdlibResolvedHttpsTransport(),
                secret_resolver=secret_resolver,
                clock=clock or (lambda: datetime.now(timezone.utc)),
            )
    if store is not None and assertion_verifier is not None:
        from integration_edge.outbound import OutboundService

        application.state.outbound_service = OutboundService(
            store, adapter, assertion_verifier, scope_bindings=tuple(scope_bindings)
        )

    @application.get("/health")
    def health():
        readiness = getattr(
            application.state,
            "readiness",
            EdgeReadiness(False, False, False, False, False, False),
        )
        return {"service": "integration-edge", **readiness.public()}

    return application


app = create_app()
