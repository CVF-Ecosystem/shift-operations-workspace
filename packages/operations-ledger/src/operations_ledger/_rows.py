"""Row <-> domain-model mappers for SqlLedger.

Split out of sql_ledger.py to keep that file under the file-size guard and to
give each domain a single obvious place for its column mapping. ``models`` is
the injected domain-model module (never imported here at module load, keeping
the one-way dependency app -> ledger).
"""

from __future__ import annotations


def shift_row(shift) -> dict:
    return {
        "shift_id": shift.shift_id,
        "name": shift.name,
        "starts_at": shift.starts_at,
        "ends_at": shift.ends_at,
        "status": str(shift.status),
        "version": shift.version,
        "created_at": shift.created_at,
    }


def event_row(event) -> dict:
    return {
        "event_id": event.event_id,
        "shift_id": event.shift_id,
        "event_type": event.event_type,
        "title": event.title,
        "description": event.description,
        "risk": str(event.risk_class),
        "state": str(event.state),
        "starts_at": event.starts_at,
        "ends_at": event.ends_at,
        "owner_id": event.owner_id,
        "version": event.version,
    }


def row_to_event(models, row, *, evidence=None):
    return models.OperationalEvent(
        event_id=row["event_id"],
        shift_id=row["shift_id"],
        event_type=row["event_type"],
        title=row["title"],
        description=row["description"],
        risk_class=row["risk"],
        state=row["state"],
        starts_at=row["starts_at"],
        ends_at=row["ends_at"],
        owner_id=row["owner_id"],
        version=row["version"],
        evidence=evidence or [],
    )


def task_row(task) -> dict:
    return {
        "task_id": task.task_id,
        "shift_id": task.shift_id,
        "title": task.title,
        "description": task.description,
        "status": str(task.status),
        "owner_id": task.owner_id,
        "due_at": task.due_at,
        "risk": str(task.risk_class),
        "state": str(task.state),
        "version": task.version,
    }


def row_to_task(models, row, *, evidence=None):
    return models.Task(
        task_id=row["task_id"],
        shift_id=row["shift_id"],
        title=row["title"],
        description=row["description"],
        status=row["status"],
        owner_id=row["owner_id"],
        due_at=row["due_at"],
        risk_class=row["risk"],
        state=row["state"],
        version=row["version"],
        evidence=evidence or [],
    )


def row_to_customer_request(models, row):
    """Read-only row mapper, kept here (rather than moved wholesale into
    ``_customer_request_store.py``) because ``_report_store.py``'s
    ``list_customer_requests_for_shift`` is an out-of-ceiling existing call
    site for this tranche (P2C-MUTATION-FULL-UI-C3B2) and still imports it
    from this module. ``customer_request_row`` (the write-side mapper) moved
    to ``_customer_request_store.py`` since every write call site is inside
    this tranche's authorized changed set."""
    return models.CustomerRequest(
        request_id=row["request_id"],
        customer_id=row["customer_id"],
        shift_id=row["shift_id"],
        summary=row["summary"],
        details=row["details"],
        status=row["status"],
        source_message_id=row["source_message_id"],
        received_at=row["received_at"],
        promised_at=row["promised_at"],
        owner_id=row["owner_id"],
        version=row["version"],
    )


def message_row(message) -> dict:
    # MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30 (SPEC R10): exact field
    # mapping. created_at is supplied explicitly (like shift_row) so a
    # read-back always matches the value the caller was returned, rather than
    # drifting to whatever the server_default clock produced. Internal writes
    # always set raw_payload = NULL — this vertical never persists a raw
    # external envelope.
    return {
        "message_id": message.message_id,
        "shift_id": message.shift_id,
        "source": message.source,
        "sender_id": message.sender_id,
        "text_content": message.text,
        "state": str(message.state),
        "raw_payload": None,
        "created_at": message.created_at,
    }


def row_to_message(models, row):
    return models.Message(
        message_id=row["message_id"],
        shift_id=row["shift_id"],
        source=row["source"],
        sender_id=row["sender_id"],
        text=row["text_content"],
        state=row["state"],
        created_at=row["created_at"],
        evidence=[],
    )


def user_row(user) -> dict:
    return {
        "user_id": user.user_id,
        "username": user.username,
        "password_hash": user.password_hash,
        "role": user.role,
        "is_active": user.is_active,
    }


def row_to_user(models, row):
    return models.User(
        user_id=row["user_id"],
        username=row["username"],
        password_hash=row["password_hash"],
        role=row["role"],
        is_active=row["is_active"],
        created_at=row["created_at"],
    )


def evidence_link_row(evidence_ref, *, record_type: str, record_id) -> dict:
    return {
        "evidence_link_id": evidence_ref.evidence_id,
        "record_type": record_type,
        "record_id": record_id,
        "source_type": evidence_ref.source_type,
        "source_id": evidence_ref.source_id,
        "sha256": evidence_ref.sha256,
    }


def row_to_evidence_ref(models, row):
    return models.EvidenceRef(
        evidence_id=row["evidence_link_id"],
        source_type=row["source_type"],
        source_id=row["source_id"],
        sha256=row["sha256"],
    )


def correction_row(correction) -> dict:
    return {
        "correction_id": correction.correction_id,
        "record_type": correction.record_type,
        "record_id": correction.record_id,
        "previous_version": correction.previous_version,
        "new_version": correction.new_version,
        "reason": correction.reason,
        "requested_by": correction.requested_by,
        "before_data": {"version": correction.previous_version},
        "after_data": {"version": correction.new_version},
    }


def approval_receipt_row(receipt) -> dict:
    return {
        "receipt_id": receipt.receipt_id,
        "record_type": receipt.record_type,
        "record_id": receipt.record_id,
        "action": receipt.action,
        "target_version": receipt.target_version,
        "risk_class": str(receipt.risk_class),
        "payload_digest": receipt.payload_digest,
        "approver_id": receipt.approver_id,
        "approver_role": receipt.approver_role,
    }


def row_to_approval_receipt(models, row):
    return models.ApprovalReceipt(
        receipt_id=row["receipt_id"],
        record_type=row["record_type"],
        record_id=row["record_id"],
        action=row["action"],
        target_version=row["target_version"],
        risk_class=row["risk_class"],
        payload_digest=row["payload_digest"],
        approver_id=row["approver_id"],
        approver_role=row["approver_role"],
        created_at=row["created_at"],
    )


def task_creation_intent_row(intent) -> dict:
    return {
        "intent_id": intent.intent_id,
        "shift_id": intent.shift_id,
        "risk_class": str(intent.risk_class),
        "payload_snapshot": intent.payload_snapshot,
        "payload_digest": intent.payload_digest,
        "created_by": intent.created_by,
    }


def row_to_task_creation_intent(models, row):
    return models.TaskCreationIntent(
        intent_id=row["intent_id"],
        shift_id=row["shift_id"],
        risk_class=row["risk_class"],
        payload_snapshot=row["payload_snapshot"],
        payload_digest=row["payload_digest"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def row_to_correction(models, row):
    return models.Correction(
        correction_id=row["correction_id"],
        record_type=row["record_type"],
        record_id=row["record_id"],
        reason=row["reason"],
        requested_by=row["requested_by"],
        previous_version=row["previous_version"],
        new_version=row["new_version"],
        created_at=row["created_at"],
    )
