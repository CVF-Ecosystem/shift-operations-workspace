"""Unit tests for the canonical ShiftAssignment/AssignmentStatus model
(P2C-MUTATION-FULL-UI-C3A1, SPEC R1, AC-01).

Package-owned in operations_domain.assignment_models; workspace_api.domain.
models re-exports the SAME objects (identity, not equivalence), matching the
pattern test_operations_domain_shim_identity.py already asserts for every
other moved type.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from operations_domain.assignment_models import AssignmentStatus, ShiftAssignment
from workspace_api.domain import models as shim_models


def test_shim_reexports_the_same_object_identity():
    assert shim_models.ShiftAssignment is ShiftAssignment
    assert shim_models.AssignmentStatus is AssignmentStatus


def test_assignment_status_is_active_or_revoked_only():
    assert {s.value for s in AssignmentStatus} == {"ACTIVE", "REVOKED"}


def test_default_construction_is_active_version_one_with_no_revoke_fields():
    a = ShiftAssignment(shift_id=uuid4(), user_id="op1", assigned_by="sup1")
    assert a.status == AssignmentStatus.ACTIVE
    assert a.version == 1
    assert a.revoked_by is None
    assert a.revoked_at is None
    assert a.assigned_at is not None


def test_version_must_be_at_least_one():
    with pytest.raises(ValidationError):
        ShiftAssignment(shift_id=uuid4(), user_id="op1", assigned_by="sup1", version=0)


def test_revoked_construction_carries_revoke_fields():
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    a = ShiftAssignment(
        shift_id=uuid4(), user_id="op1", assigned_by="sup1",
        status=AssignmentStatus.REVOKED, revoked_by="sup1", revoked_at=now, version=2,
    )
    assert a.status == AssignmentStatus.REVOKED
    assert a.revoked_by == "sup1"
    assert a.revoked_at == now
    assert a.version == 2


def test_model_has_no_tenant_or_provider_data_scope_field():
    """ADR section 3/4.1: per-shift resource scope, not tenant isolation, and
    not a repurposing of cvf_runtime's provider-placement data_scope."""
    fields = ShiftAssignment.model_fields.keys()
    assert "tenant_id" not in fields
    assert "data_scope" not in fields
