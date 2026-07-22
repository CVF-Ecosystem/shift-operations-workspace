"""Repair tests for defects an independent review reproduced in the
customer_request vertical (P2-A) after commit d59d24d.

Split out of test_customer_request_vertical.py purely to respect the
file-size guard (GC-023 style, hard limit 400 lines for *.py) - not a
behavior change. Shares fixtures/helpers with that module by importing them
directly (same pattern as test_schema_parity_types_and_checks.py importing
MAPPED from test_schema_parity).

Findings repaired here:
* Finding 1 (HIGH): InMemoryLedger returned/stored a caller-owned mutable
  alias for customer_request - a caller could mutate the returned object and
  silently rewrite persisted state with no governance involved at all.
* Finding 2 (MEDIUM): source_message_id was checked inconsistently across
  backends (InMemory accepted anything; SqlLedger/SQLite raised an uncaught
  IntegrityError from the FK, which could surface as an HTTP 500).
* Finding 3 (MEDIUM): CustomerRequestInput.promised_at was typed `str | None`,
  so a malformed value only failed at CustomerRequest(...) construction inside
  the route body, escaping as an HTTP 500 instead of a controlled 422.
* Finding 5 (LOW): the vertical's domain_lock claim had no negative-profile
  test proving a profile that excludes customer_request is actually refused.
"""

from uuid import uuid4

import pytest
from sqlalchemy import insert

from cvf_runtime.errors import CvfDenied
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger.sql_ledger import SqlLedger
from operations_ledger.tables import messages

from workspace_api.application.customer_request_service import CustomerRequestService
from operations_domain import models as domain_models
from operations_domain.models import CustomerRequestStatus
from workspace_api.infrastructure.repository import InMemoryLedger

from test_customer_request_vertical import (
    _backends,
    _client_for,
    _clear_overrides,
    _new_shift,
    _operator,
    _request,
    _sql_ledger,
)

from _auth_test_helpers import auth_headers


# --- Finding 1: InMemory must not return a caller-owned mutable alias --------


def test_inmemory_customer_request_returned_object_is_not_a_live_alias():
    """Independent review, 2026-07-22: InMemoryLedger.add_customer_request
    stored and returned the SAME mutable Pydantic object, so a caller could
    do `created.status = CLOSED` and silently rewrite persisted state with
    no permission check, lifecycle validation, transaction, or audit at all.
    """
    ledger = InMemoryLedger()
    created = CustomerRequestService(ledger).create_customer_request(_request(), _operator())
    assert created.status == CustomerRequestStatus.NEW

    audit_before = ledger.audit_entries_for(str(created.request_id))
    assert len(audit_before) == 1

    # Mutate the object the caller was handed back.
    created.status = CustomerRequestStatus.CLOSED

    # Stored state must be unaffected by that mutation.
    stored = ledger.get_customer_request(created.request_id)
    assert stored.status == CustomerRequestStatus.NEW, (
        "mutating the object returned by create_customer_request must not "
        "change persisted state"
    )

    audit_after = ledger.audit_entries_for(str(created.request_id))
    assert len(audit_after) == 1, "no audit entry should appear from an out-of-band mutation"

    # A legitimate service-mediated transition must still work normally.
    moved = CustomerRequestService(ledger).transition(
        created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED
    )
    assert moved.status == CustomerRequestStatus.ACKNOWLEDGED
    stored_after_transition = ledger.get_customer_request(created.request_id)
    assert stored_after_transition.status == CustomerRequestStatus.ACKNOWLEDGED


def _insert_sql_message(ledger: SqlLedger, shift):
    """Insert a row directly into the messages table for test setup only.

    SqlLedger.add_message still raises NotImplementedError (message
    persistence is a separate, unimplemented vertical - see tables.py's
    module docstring) - this is the smallest way to get a real, valid
    message_id row for the source_message_id existence check without
    implementing that vertical.
    """
    message_id = uuid4()
    with ledger.engine.begin() as conn:
        conn.execute(
            insert(messages).values(
                message_id=message_id,
                shift_id=shift.shift_id,
                source="INTERNAL",
                sender_id="tester",
                text_content="hello",
                state="RAW",
            )
        )
    return message_id


# --- Finding 2: source_message_id must be validated consistently ------------


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_without_source_message_id_succeeds(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    created = CustomerRequestService(ledger).create_customer_request(_request(), _operator())
    assert created.source_message_id is None


def test_create_customer_request_with_valid_source_message_id_in_memory_succeeds():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = domain_models.Message(shift_id=shift.shift_id, sender_id="tester", text="hi")
    ledger.add_message(message)

    created = CustomerRequestService(ledger).create_customer_request(
        _request(shift, source_message_id=message.message_id), _operator()
    )
    assert created.source_message_id == message.message_id


def test_create_customer_request_with_valid_source_message_id_sql_succeeds(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    message_id = _insert_sql_message(ledger, shift)

    created = CustomerRequestService(ledger).create_customer_request(
        _request(shift, source_message_id=message_id), _operator()
    )
    assert created.source_message_id == message_id


def test_create_customer_request_with_nonexistent_source_message_id_in_memory_is_rejected():
    ledger = InMemoryLedger()
    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger).create_customer_request(
            _request(source_message_id=uuid4()), _operator()
        )
    assert exc.value.control == "reference"
    assert exc.value.http_status == 404
    assert ledger.customer_requests == {}


def test_create_customer_request_with_nonexistent_source_message_id_sql_is_rejected(tmp_path):
    ledger = _sql_ledger(tmp_path)
    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger).create_customer_request(
            _request(source_message_id=uuid4()), _operator()
        )
    assert exc.value.control == "reference"
    assert exc.value.http_status == 404
    # No IntegrityError leaked, and nothing was persisted.
    from operations_ledger.tables import customer_requests as cr_table

    with ledger.engine.connect() as conn:
        rows = conn.execute(cr_table.select()).mappings().all()
    assert rows == []


def test_http_create_with_nonexistent_source_message_id_is_controlled_not_500():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={
                "customer_id": "cust-9",
                "summary": "Late delivery",
                "source_message_id": str(uuid4()),
            },
            headers=auth_headers("op1", "operator"),
        )
        assert resp.status_code == 404, resp.text
        assert resp.status_code != 500
    finally:
        _clear_overrides()


# --- Finding 3: malformed promised_at must be a controlled 422, not 500 -----


def test_http_create_with_valid_promised_at_succeeds():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={
                "customer_id": "cust-9",
                "summary": "Late delivery",
                "promised_at": "2026-08-01T10:00:00Z",
            },
            headers=auth_headers("op1", "operator"),
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["promised_at"] is not None
    finally:
        _clear_overrides()


def test_http_create_with_malformed_promised_at_is_422_not_500():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={
                "customer_id": "cust-9",
                "summary": "Late delivery",
                "promised_at": "not-a-date",
            },
            headers=auth_headers("op1", "operator"),
        )
        assert resp.status_code == 422, resp.text
        assert resp.status_code != 500
        assert ledger.customer_requests == {}
    finally:
        _clear_overrides()


# --- Finding 5: domain_lock negative profile test ---------------------------


def test_customer_request_denied_when_domain_lock_excludes_it():
    real_profile = load_profile()
    restricted_domain_lock = dict(real_profile.domain_lock)
    restricted_domain_lock["allowed_domains"] = [
        d for d in restricted_domain_lock.get("allowed_domains", []) if d != "customer_request"
    ]
    restricted_profile = CvfProfile(
        profile=real_profile.profile,
        risk_classes=real_profile.risk_classes,
        approval=real_profile.approval,
        evidence=real_profile.evidence,
        domain_lock=restricted_domain_lock,
        data=real_profile.data,
        cost=real_profile.cost,
        termination=real_profile.termination,
        known_principals=real_profile.known_principals,
    )

    ledger = InMemoryLedger()
    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger, profile=restricted_profile).create_customer_request(
            _request(), _operator()
        )
    assert exc.value.control == "domain_lock"
    assert ledger.customer_requests == {}
    assert len(ledger._audit.all()) == 0
