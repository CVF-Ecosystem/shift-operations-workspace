"""Compatibility shim for the operational models, PLUS the canonical home of `User`.

This module has two deliberate jobs (tranche P1B-OPERATIONS-DOMAIN-EXTRACTION).
Do not "clean it up" into one without reading both.

1. **Compatibility shim.** The twelve operational types below are re-exported
   from `operations_domain.models`, which owns their single canonical
   definition. `from X import Y` binds the SAME object, so this is class
   identity, not equivalence:
   `workspace_api.domain.models.Shift is operations_domain.models.Shift`.
   Never re-declare or subclass one of them here to "re-export" it - that would
   create two classes that fail each other's isinstance checks and diverge in
   Pydantic schema output. `tests/unit/test_operations_domain_shim_identity.py`
   fails the build if anyone tries.

   New code should import from `operations_domain.models` directly. This shim
   exists for backward compatibility and for the ledger `models=` injection
   seam described below.

2. **Canonical home of `User`.** `User` did NOT move to operations-domain, and
   that is a decision, not an oversight. It mirrors
   `database/migrations/003_users.sql` (P2-B authentication), its `role` values
   are constrained by `cvf_runtime.identity.KNOWN_ROLES`, and no operations
   vertical references it - it belongs to the authentication boundary. Where it
   finally lives is owned by the `known-principals.yaml` <-> `users`
   reconciliation tranche (High Finding #4), not by a mechanical move here.

Because this module exposes both the operational types and `User`, it is also
the namespace object passed as `SqlLedger(models=...)`: `operations_ledger`
needs `models.User` for `build_user`, so the injected namespace must expose it.
That seam is deliberately NOT refactored by this tranche - see
`infrastructure/ledger_factory.py` and ADR section 2.5.
"""

from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from operations_domain.models import (  # noqa: F401  (re-exported for compatibility)
    Correction,
    CustomerRequest,
    CustomerRequestStatus,
    DataState,
    EvidenceRef,
    Message,
    OperationalEvent,
    RiskClass,
    Shift,
    ShiftStatus,
    Task,
    TaskStatus,
)

__all__ = [
    "Correction",
    "CustomerRequest",
    "CustomerRequestStatus",
    "DataState",
    "EvidenceRef",
    "Message",
    "OperationalEvent",
    "RiskClass",
    "Shift",
    "ShiftStatus",
    "Task",
    "TaskStatus",
    "User",
]


class User(BaseModel):
    # Mirrors database/migrations/003_users.sql (P2-B: real authentication).
    # user_id is free-form text (not a UUID) to reuse the same ids already
    # used in known-principals.yaml, e.g. "op1"/"sup1" - that registry and
    # this table are independent stores, sharing ids only for legibility.
    user_id: str
    username: str
    password_hash: str
    role: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
