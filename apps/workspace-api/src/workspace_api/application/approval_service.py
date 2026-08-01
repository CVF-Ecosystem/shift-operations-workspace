"""Approval receipt / task-creation-intent application service.

P2B-APPROVER-IDENTITY-RECONCILIATION (closing High Finding #4). Owns
everything genuinely new in this tranche: authenticated receipt creation, the
digest-bound task-creation-intent two-phase flow (ADR section 4.4), and the
server-owned authority resolver every governed service (EventService/
CorrectionService/TaskService) uses to evaluate a quorum. This keeps
``cvf_runtime.approval`` a pure gate function (Protocol-typed, no ledger/
domain import - see that module's docstring) while the actual persistence and
authority-lookup glue lives here, in the application layer, exactly like
every other governed action in this codebase.

CVF-FILE-SPLIT-GUARD-HARDENING split the implementation across
``approval_receipts.py`` (receipt creation + authority resolution) and
``task_creation_intents.py`` (digest + creation-intent lifecycle) to stay
under the hard line limit. This module is the unchanged compatibility facade:
every name below is the same object the split-out modules define, re-exported
so existing ``from workspace_api.application import approval_service`` /
``approval_service.<name>`` call sites keep working without modification.
"""

from __future__ import annotations

from workspace_api.application.approval_receipts import (
    authority_for_factory,
    collect_receipts_for,
    create_approval_receipt,
    has_authority_for_any_required_seat as _has_authority_for_any_required_seat,
)
from workspace_api.application.approval_readiness import evaluate_readiness
from workspace_api.application.task_creation_intents import (
    compute_payload_digest,
    create_task_creation_intent,
    get_task_creation_intent,
)

__all__ = [
    "authority_for_factory",
    "collect_receipts_for",
    "create_approval_receipt",
    "compute_payload_digest",
    "create_task_creation_intent",
    "get_task_creation_intent",
    "evaluate_readiness",
]
