from __future__ import annotations

import hashlib
import json

from integration_edge.invariants import emit_outbound_terminal_receipt


class OutboundService:
    """Provider-neutral state machine. Adapter is an injected internal port."""

    def __init__(self, store, adapter, assertion_verifier, *, rate_limit: int = 100) -> None:
        self.store, self.adapter, self.assertion_verifier, self.rate_limit = store, adapter, assertion_verifier, rate_limit

    def deliver(self, command: dict, assertion: str, *, prerequisites_valid: bool = True):
        command_id = str(command["command_id"])
        existing=getattr(self.store,"outbound",{}).get(command_id)
        if existing:
            safe={key:value for key,value in existing.items() if key!="prerequisite_digest"}
            return emit_outbound_terminal_receipt(safe.pop("outcome"),**safe)
        body = json.dumps(command, sort_keys=True, separators=(",", ":")).encode()
        try:
            self.assertion_verifier(assertion, audience="integration-edge", operation="outbound.deliver", body=body)
        except (ValueError, PermissionError):
            return emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="AUTH_REFUSED", command_id=command_id, delivery_attempts=0)
        if not prerequisites_valid:
            return emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="PREREQUISITE_REFUSED", command_id=command_id, delivery_attempts=0)
        allowed, _ = self.store.consume_rate("OUTBOUND", command.get("channel", "default"), self.rate_limit)
        if not allowed:
            return emit_outbound_terminal_receipt("RATE_LIMITED", reason="RATE_LIMITED", command_id=command_id, delivery_attempts=0)
        if self.adapter is None or getattr(self.adapter,"evidence_eligible",True) is not False:
            return emit_outbound_terminal_receipt("NOT_ATTEMPTED", reason="ADAPTER_UNAVAILABLE", command_id=command_id, delivery_attempts=0)
        try:
            result = self.adapter.deliver(command=command,idempotency_key=command_id)
            status = result.get("status")
            if status in {"SENT_ACCEPTED", "DELIVERED"}:
                receipt = emit_outbound_terminal_receipt(status, command_id=command_id, delivery_id=result["delivery_id"], delivery_attempts=1)
            elif status == "PROVIDER_REFUSED":
                receipt = emit_outbound_terminal_receipt(status, reason="PROVIDER_REFUSED", command_id=command_id, delivery_attempts=1)
            elif status == "TERMINAL_FAILED":
                receipt = emit_outbound_terminal_receipt(status, reason=result.get("reason", "NONRETRYABLE_ERROR"), command_id=command_id, delivery_attempts=1)
            else:
                receipt = emit_outbound_terminal_receipt("OUTCOME_UNKNOWN", reason="AMBIGUOUS_TRANSPORT", command_id=command_id, delivery_attempts=1)
        except Exception:
            receipt = emit_outbound_terminal_receipt("OUTCOME_UNKNOWN", reason="AMBIGUOUS_TRANSPORT", command_id=command_id, delivery_attempts=1)
        dumped = receipt.model_dump(exclude_none=True)
        self.store.save_outbound(dumped, hashlib.sha256(body).hexdigest())
        return receipt
