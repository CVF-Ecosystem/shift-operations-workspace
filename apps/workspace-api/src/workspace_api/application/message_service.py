"""Message application service — internal-user command only
(MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30).

`POST /messages` previously accepted an anonymous request, trusted a
caller-supplied `sender_id`/`source` as authority, and called
`ledger.add_message(...)` directly from the router — no identity, no
permission, no audit (INTAKE probe: anonymous request -> 200, forged
`sender_id="forged-executive"`/`source="INTERNAL"` accepted unchanged, zero
audit records). This service is the single governed entry point now,
following the same identity -> permission -> transaction(mutate + audit)
shape as ShiftService/CustomerRequestService/IncidentService.

Legacy `sender_id`/`source` request fields are optional COMPATIBILITY
ASSERTIONS only (SPEC R2/R4) — never authority. They are verified before
`message.create` permission is even checked, so a mismatched assertion never
reaches the ledger. Server-derived `sender_id`/`source` are the only values
ever persisted.

External channel/provider payloads must never reach this service — that is a
separate, later Integration Edge tranche (ADR Decision 1/5).
"""

from __future__ import annotations

from uuid import UUID

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from operations_ledger import Ledger

from operations_domain.models import Message

_CREATE_CHAIN = ["identity", "permission", "create", "audit"]
_INTERNAL_SOURCE = "INTERNAL"


class MessageService:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def create(
        self,
        shift_id: UUID,
        text: str,
        principal: Principal,
        sender_assertion: str | None = None,
        source_assertion: str | None = None,
    ) -> Message:
        # R4 step 1: verify optional legacy assertions BEFORE any permission
        # check or ledger access — a refused assertion never reaches the
        # ledger at all (mirrors ShiftService.create's admission-before-
        # mutation ordering).
        if sender_assertion is not None and sender_assertion != principal.user_id:
            raise CvfDenied(
                control="sender_assertion",
                reason=(
                    f"sender_id assertion {sender_assertion!r} does not match "
                    "the authenticated principal"
                ),
                http_status=403,
            )
        if source_assertion is not None and source_assertion != _INTERNAL_SOURCE:
            raise CvfDenied(
                control="source_assertion",
                reason=f"source assertion {source_assertion!r} is not valid for this endpoint",
                http_status=422,
            )

        # R4 step 2: message.create permission, minimum role operator.
        require_action(principal, "message.create")

        # R5: canonical internal Message — every persisted field is
        # server/domain-derived from only the admitted shift_id, text and
        # principal. Message text remains RAW input; it does not become a
        # confirmed event, instruction, approval or operational fact.
        message = Message(
            shift_id=shift_id,
            sender_id=principal.user_id,
            source=_INTERNAL_SOURCE,
            text=text,
        )

        # R6: one transaction, message persistence and its exact actor-bound
        # audit commit or roll back together. Audit failure rolls back the
        # message; message failure (unknown/frozen shift, duplicate id,
        # unsupported evidence) leaves no audit.
        with self.ledger.transaction() as unit:
            stored = self.ledger.add_message(message, unit=unit)
            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="message.create",
                    record_type="Message",
                    record_id=str(stored.message_id),
                    control_chain=_CREATE_CHAIN,
                    before_state=None,
                    after_state=str(stored.state),
                ),
                unit=unit,
            )
        return stored
