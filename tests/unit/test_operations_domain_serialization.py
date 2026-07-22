"""Behavioural-parity tests for the moved models (tranche P1-B).

Covers SPEC AC-06, AC-07, AC-08 and the OpenAPI half of AC-09.

Golden values were captured at the pre-BUILD commit, BEFORE any source edit,
with the same `canonical()` helper used here. They are stored as SHA-256
digests of the canonical bytes rather than as inline literals: the canonical
OpenAPI document is 18,567 bytes and the seven model schemas total ~7 KB, which
would blow past the 400-line `.py` file-size guard and would have required a
fixture file outside the authorized 43-path changed set. Comparing SHA-256 of
canonical bytes is byte-equality proof; on failure the actual canonical bytes
are dumped for diffing.

Round trips use the matching API in each direction (SPEC section 4.4):
`model_validate(model_dump())` for Python objects and
`model_validate_json(model_dump_json())` for JSON.
`model_validate(<json string>)` is forbidden - it is the wrong entry point and
would exercise a path unrelated to what AC-06 claims to verify.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from uuid import UUID

import pytest

from operations_domain import lifecycle as lc
from operations_domain import models as m

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")


def canonical(value) -> bytes:
    """SPEC section 4.4: the one definition of 'byte-identical'."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


U = [UUID(f"00000000-0000-4000-8000-0000000000{i:02d}") for i in range(10)]
T0 = datetime(2026, 7, 23, 6, 0, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 7, 23, 18, 0, 0, tzinfo=timezone.utc)
_EV = dict(evidence_id=U[0], source_type="doc", source_id="s1", sha256="ab" * 32)


def _instances() -> dict[str, object]:
    """Fixed UUIDs and timestamps - no uuid4()/now() at assertion time."""
    return {
        "EvidenceRef": m.EvidenceRef(**_EV),
        "Shift": m.Shift(shift_id=U[1], name="Shift A", starts_at=T0, ends_at=T1, created_at=T0),
        "Message": m.Message(
            message_id=U[2], shift_id=U[1], sender_id="op1", text="hello", created_at=T0,
            evidence=[m.EvidenceRef(**_EV)],
        ),
        "OperationalEvent": m.OperationalEvent(
            event_id=U[3], shift_id=U[1], event_type="DELAY", title="t", description="d",
            starts_at=T0, ends_at=T1, owner_id="op1", evidence=[m.EvidenceRef(**_EV)],
        ),
        "Correction": m.Correction(
            correction_id=U[4], record_type="OperationalEvent", record_id=U[3], reason="r",
            requested_by="op1", previous_version=1, new_version=2, created_at=T0,
        ),
        "Task": m.Task(
            task_id=U[5], shift_id=U[1], title="t", description="d", owner_id="op1",
            due_at=T1, created_at=T0, evidence=[m.EvidenceRef(**_EV)],
        ),
        "CustomerRequest": m.CustomerRequest(
            request_id=U[6], customer_id="c1", shift_id=U[1], summary="s", details="d",
            source_message_id=U[2], received_at=T0, promised_at=T1, owner_id="op1",
        ),
    }


MODEL_NAMES = sorted(_instances())

# --- golden captures from the pre-BUILD commit -----------------------------
GOLDEN_SCHEMA_SHA = {
    "Correction": "65aab7b864d5b93348642449ba735c0e0cd7695abd951cf6aed9dca7c8db7829",
    "CustomerRequest": "3dd9bc52ae4aad2b3338f6c0067fc825a975534a9979f38a6d70d3483ff8dadf",
    "EvidenceRef": "978e8f78a0ba88137a7558b823e0518c0185b3698c8e6a9aa9914c429527a85a",
    "Message": "6d6f6fa228cb162f54addc51d8e7d43d649db59be65548bf9f05444c70c32835",
    "OperationalEvent": "47272b4c40fb86c2f0c27299f3d1e2b3d777445ce05ce7264bb6f86a7840a933",
    "Shift": "6b00c69f748e5be42f29af962b021cc6f4a291ba24827c7c52bdc494632a2c89",
    "Task": "f15a3836ba25603149df752e093f5c945587f3b84dd96ae67e4cbf7ba8d02570",
}
GOLDEN_DUMP_SHA = {
    "Correction": "d2634a1a5f4e3dd2946d4497353b5ad17605965d251f1c07e78e21a32f664a0f",
    "CustomerRequest": "140ffebe2e7c57989939ed6d7a40ab3c4df509b98fc243384947dd5a4dd93adb",
    "EvidenceRef": "449fff73b872b588f60d8ee661d1d93b39a9f91526f32849118c126a4cad8de0",
    "Message": "7c280bb6d2c6854c3b87fe1df68a0cabb45b14df5be85472d6d67a4ecc2459b1",
    "OperationalEvent": "76d75ba5297061924c28e9aa0716969ec7369ede984e416342d9cd5d359a318b",
    "Shift": "221971ba1df5f1b457a162fb062e92077177ee69961a3a6654e0972a0d54665d",
    "Task": "fa5bb0e8ead5c440b7d05f305bb676437865bcde4a3ae82a243bf137b097e51c",
}
GOLDEN_DUMP_JSON_SHA = {
    "Correction": "bc2a0ad969b8977732a567fe3bdbbf01803c29a67e03b65d01388ca5c6ae751a",
    "CustomerRequest": "f87d25a09e1bf377f1ec15e59f58ade75dad091f01fd12fa425a65d1a7bdd930",
    "EvidenceRef": "a0e2743dad518391fe1373d0a0b14e8ae40e5ec339160e9cb9170e00d51f516a",
    "Message": "4c0853cd8bd1204d922e497fa1ee7c60d2c84d7321385ba020fca4a283580526",
    "OperationalEvent": "ff43cecec1cf62ce2df2332859d6b473dc4e99c517a2ebc8c3f5a0a2c1f31312",
    "Shift": "7fca25e5ec702fa73bbc4bdc9efdd0d9a638ea7add0f04f094dd8edd74fa5bd5",
    "Task": "bc1dec30719b51fec14ccf01c8ef2f6a40cee494e36966f70c23f8677b22f181",
}
GOLDEN_OPENAPI_SHA = "5015828a81e1c4760cff0c8dc1b6412b4ba3cd5a300137cb8cfa1090e813e8e1"

GOLDEN_ENUMS = {
    "CustomerRequestStatus": [
        ("NEW", "NEW"), ("ACKNOWLEDGED", "ACKNOWLEDGED"), ("IN_PROGRESS", "IN_PROGRESS"),
        ("WAITING", "WAITING"), ("RESOLVED", "RESOLVED"), ("CLOSED", "CLOSED"),
    ],
    "DataState": [
        ("RAW", "RAW"), ("NORMALIZED", "NORMALIZED"), ("PROPOSED", "PROPOSED"),
        ("CONFIRMED", "CONFIRMED"), ("REJECTED", "REJECTED"), ("CORRECTED", "CORRECTED"),
        ("FROZEN", "FROZEN"),
    ],
    "RiskClass": [("R0", "R0"), ("R1", "R1"), ("R2", "R2"), ("R3", "R3"), ("R4", "R4")],
    "ShiftStatus": [
        ("OPEN", "OPEN"), ("HANDOVER_PENDING", "HANDOVER_PENDING"), ("CLOSED", "CLOSED"),
        ("FROZEN", "FROZEN"),
    ],
    "TaskStatus": [
        ("OPEN", "OPEN"), ("IN_PROGRESS", "IN_PROGRESS"), ("BLOCKED", "BLOCKED"),
        ("DONE", "DONE"), ("CARRY_OVER", "CARRY_OVER"), ("CANCELLED", "CANCELLED"),
    ],
}


# --- AC-06 -----------------------------------------------------------------
@pytest.mark.parametrize("name", MODEL_NAMES)
def test_python_object_round_trip(name):
    """AC-06: model_validate(model_dump()) - the Python-object direction."""
    inst = _instances()[name]
    assert type(inst).model_validate(inst.model_dump()) == inst


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_json_round_trip(name):
    """AC-06: model_validate_json(model_dump_json()) - the JSON direction."""
    inst = _instances()[name]
    assert type(inst).model_validate_json(inst.model_dump_json()) == inst


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_dump_is_unchanged_from_the_pre_build_capture(name):
    inst = _instances()[name]
    actual = canonical(inst.model_dump(mode="json"))
    assert _sha(actual) == GOLDEN_DUMP_SHA[name], actual.decode("utf-8")


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_dump_json_is_unchanged_from_the_pre_build_capture(name):
    inst = _instances()[name]
    actual = inst.model_dump_json().encode("utf-8")
    assert _sha(actual) == GOLDEN_DUMP_JSON_SHA[name], actual.decode("utf-8")


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_json_schema_is_unchanged_from_the_pre_build_capture(name):
    actual = canonical(getattr(m, name).model_json_schema())
    assert _sha(actual) == GOLDEN_SCHEMA_SHA[name], actual.decode("utf-8")


# --- AC-07 -----------------------------------------------------------------
@pytest.mark.parametrize("name", sorted(GOLDEN_ENUMS))
def test_enum_members_and_values_unchanged(name):
    """AC-07: names, values AND order."""
    actual = [(e.name, e.value) for e in getattr(m, name)]
    assert actual == GOLDEN_ENUMS[name]


# --- AC-08 -----------------------------------------------------------------
def _matrix(enum_cls, guard):
    allowed, denied = set(), set()
    for cur in enum_cls:
        for tgt in enum_cls:
            try:
                guard(cur, tgt)
            except ValueError:
                denied.add((cur.name, tgt.name))
            else:
                allowed.add((cur.name, tgt.name))
    return allowed, denied


def test_data_state_transition_matrix_unchanged():
    allowed, denied = _matrix(m.DataState, lc.assert_transition)
    assert allowed == {
        ("RAW", "NORMALIZED"), ("RAW", "REJECTED"),
        ("NORMALIZED", "PROPOSED"), ("NORMALIZED", "REJECTED"),
        ("PROPOSED", "CONFIRMED"), ("PROPOSED", "REJECTED"),
        ("CONFIRMED", "CORRECTED"), ("CONFIRMED", "FROZEN"),
        ("CORRECTED", "FROZEN"),
    }
    assert len(allowed) + len(denied) == len(m.DataState) ** 2


def test_task_status_transition_matrix_unchanged():
    allowed, denied = _matrix(m.TaskStatus, lc.assert_task_transition)
    assert allowed == {
        ("OPEN", "IN_PROGRESS"), ("OPEN", "BLOCKED"), ("OPEN", "CANCELLED"), ("OPEN", "CARRY_OVER"),
        ("IN_PROGRESS", "BLOCKED"), ("IN_PROGRESS", "DONE"), ("IN_PROGRESS", "CANCELLED"),
        ("IN_PROGRESS", "CARRY_OVER"),
        ("BLOCKED", "IN_PROGRESS"), ("BLOCKED", "CANCELLED"), ("BLOCKED", "CARRY_OVER"),
        ("CARRY_OVER", "OPEN"), ("CARRY_OVER", "IN_PROGRESS"), ("CARRY_OVER", "CANCELLED"),
    }
    assert len(allowed) + len(denied) == len(m.TaskStatus) ** 2


def test_customer_request_transition_matrix_unchanged():
    allowed, denied = _matrix(m.CustomerRequestStatus, lc.assert_customer_request_transition)
    assert allowed == {
        ("NEW", "ACKNOWLEDGED"),
        ("ACKNOWLEDGED", "IN_PROGRESS"),
        ("IN_PROGRESS", "WAITING"), ("IN_PROGRESS", "RESOLVED"),
        ("WAITING", "IN_PROGRESS"),
        ("RESOLVED", "CLOSED"),
    }
    # The design choice WAITING must not skip straight to CLOSED.
    assert ("WAITING", "CLOSED") in denied
    assert len(allowed) + len(denied) == len(m.CustomerRequestStatus) ** 2


def test_transition_error_messages_unchanged():
    with pytest.raises(ValueError, match=r"^Invalid data-state transition: RAW -> CONFIRMED$"):
        lc.assert_transition(m.DataState.RAW, m.DataState.CONFIRMED)
    with pytest.raises(ValueError, match=r"^Invalid task-status transition: DONE -> OPEN$"):
        lc.assert_task_transition(m.TaskStatus.DONE, m.TaskStatus.OPEN)
    with pytest.raises(
        ValueError, match=r"^Invalid customer-request-status transition: WAITING -> CLOSED$"
    ):
        lc.assert_customer_request_transition(
            m.CustomerRequestStatus.WAITING, m.CustomerRequestStatus.CLOSED
        )


# --- AC-09 (OpenAPI half) --------------------------------------------------
def test_openapi_document_is_unchanged_from_the_pre_build_capture():
    """AC-09: the generated contract did not move."""
    from workspace_api.main import app

    actual = canonical(app.openapi())
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:4000]
