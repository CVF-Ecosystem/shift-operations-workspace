from __future__ import annotations

import hashlib
import json

from channel_sdk import AdapterDeliveryRequestV1, AdapterDeliveryResultV1
from pydantic import ValidationError
from integration_edge.invariants import emit_outbound_terminal_receipt
from integration_edge.models import OutboundCommand

from .scope import AdapterScopeBindingV1, has_exact_scope


class OutboundService:
    """Provider-neutral state machine. Adapter is an injected internal port."""

    def __init__(
        self,
        store,
        adapter,
        assertion_verifier,
        *,
        scope_bindings: tuple[AdapterScopeBindingV1, ...] = (),
        rate_limit: int = 100,
    ) -> None:
        self.store = store
        self.adapter = adapter
        self.assertion_verifier = assertion_verifier
        try:
            self.scope_bindings = tuple(
                AdapterScopeBindingV1.model_validate(item) for item in scope_bindings
            )
        except (TypeError, ValidationError):
            self.scope_bindings = ()
        self.rate_limit = rate_limit

    def deliver(self, command: dict, assertion: str, *, prerequisites_valid: bool = True):
        validated = OutboundCommand.model_validate(command)
        command_id = validated.command_id
        existing=getattr(self.store,"outbound",{}).get(command_id)
        if existing:
            safe={key:value for key,value in existing.items() if key!="prerequisite_digest"}
            return emit_outbound_terminal_receipt(safe.pop("outcome"),**safe)
        body = json.dumps(
            validated.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ).encode()
        try:
            self.assertion_verifier(assertion, audience="integration-edge", operation="outbound.deliver", body=body)
        except (ValueError, PermissionError):
            return emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="AUTH_REFUSED", command_id=command_id, delivery_attempts=0)
        if not prerequisites_valid:
            return emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="PREREQUISITE_REFUSED", command_id=command_id, delivery_attempts=0)
        allowed, _ = self.store.consume_rate(
            "OUTBOUND", validated.channel_digest, self.rate_limit
        )
        if not allowed:
            return emit_outbound_terminal_receipt("RATE_LIMITED", reason="RATE_LIMITED", command_id=command_id, delivery_attempts=0)
        try:
            request = AdapterDeliveryRequestV1.model_validate(validated.model_dump(mode="python"))
        except ValidationError:
            return emit_outbound_terminal_receipt(
                "NOT_ATTEMPTED",
                reason="ADAPTER_UNAVAILABLE",
                command_id=command_id,
                delivery_attempts=0,
            )
        if (
            self.adapter is None
            or getattr(self.adapter, "adapter_mode", None) != "DEPLOYABLE"
            or not has_exact_scope(request, self.scope_bindings)
        ):
            return emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="ADAPTER_UNAVAILABLE", command_id=command_id, delivery_attempts=0)
        try:
            raw = self.adapter.deliver(
                request=request, idempotency_key=request.idempotency_key
            )
            result = AdapterDeliveryResultV1.model_validate(raw)
            status = result.status
            if status == "SENT_ACCEPTED":
                receipt = emit_outbound_terminal_receipt(status, command_id=command_id, delivery_id=result.delivery_id, delivery_attempts=1)
            elif status == "PROVIDER_REFUSED":
                receipt = emit_outbound_terminal_receipt(status, reason="PROVIDER_REFUSED", command_id=command_id, delivery_attempts=1)
            elif status == "TERMINAL_FAILED":
                receipt = emit_outbound_terminal_receipt(status, reason=result.reason, command_id=command_id, delivery_attempts=1)
            elif status == "NOT_ATTEMPTED":
                receipt = emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="ADAPTER_UNAVAILABLE", command_id=command_id, delivery_attempts=0)
            else:
                receipt = emit_outbound_terminal_receipt("OUTCOME_UNKNOWN", reason="AMBIGUOUS_TRANSPORT", command_id=command_id, delivery_attempts=1)
        except Exception:
            receipt = emit_outbound_terminal_receipt("OUTCOME_UNKNOWN", reason="AMBIGUOUS_TRANSPORT", command_id=command_id, delivery_attempts=1)
        dumped = receipt.model_dump(exclude_none=True)
        self.store.save_outbound(dumped, hashlib.sha256(body).hexdigest())
        return receipt
