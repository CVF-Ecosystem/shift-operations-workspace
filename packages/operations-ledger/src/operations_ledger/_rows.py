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


def customer_request_row(request) -> dict:
    return {
        "request_id": request.request_id,
        "customer_id": request.customer_id,
        "shift_id": request.shift_id,
        "summary": request.summary,
        "details": request.details,
        "status": str(request.status),
        "source_message_id": request.source_message_id,
        "received_at": request.received_at,
        "promised_at": request.promised_at,
        "owner_id": request.owner_id,
    }


def row_to_customer_request(models, row):
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
