"""Pure full-row comparison for the one retained synthetic demo profile."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

from workspace_api.auth.passwords import verify_password

TARGET = {"users": 1, "shifts": 36, "shift_assignments": 36, "reports": 37}
PUBLIC_ACTOR = "PUBLIC_ACTOR"


def _json_value(value):
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise RuntimeError("unsupported raw column type")


def _canonical(value) -> str:
    return json.dumps(_json_value(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def _timestamp(value) -> str:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(
        str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise RuntimeError("timestamp timezone invalid")
    return parsed.astimezone(timezone.utc).isoformat()


def _expected_model_rows(bundle: dict):
    from operations_domain.models import Shift, Report
    from operations_domain.assignment_models import ShiftAssignment

    return {
        "shifts": {str(item.shift_id): item for item in
                   (Shift(**row) for row in bundle["shifts"])},
        "shift_assignments": {str(item.assignment_id): item for item in
                              (ShiftAssignment(**row) for row in bundle["assignments"])},
        "reports": {str(item.report_id): item for item in
                    (Report(**row) for row in bundle["reports"])},
    }


def compare_rows(rows: dict[str, list[dict]], bundle: dict, password: str,
                 user_type: type) -> dict:
    """Reject every partial/foreign/raw-column difference before selecting a write.

    The returned digest binds *all* raw rows, including the stored password
    hash, while neither that value nor any row body leaves this process.
    """
    from operations_ledger.tables import shifts, users
    from operations_ledger._assignment_store import shift_assignments
    from operations_ledger._report_store import reports
    from operations_domain.models import Shift, Report
    from operations_domain.assignment_models import ShiftAssignment
    from workspace_api.infrastructure import repository

    # The retained user must use the same canonical auth model that the
    # existing repository and SqlLedger injection seam expose.
    if user_type is not repository.User:
        raise RuntimeError("USER_TYPE_INVALID")

    known_columns = {table.name: set(table.columns.keys())
                     for table in (users, shifts, shift_assignments, reports)}
    if len(rows) != 31 or not set(TARGET).issubset(rows):
        raise RuntimeError("ROW_SET_INVALID")
    counts = {name: len(value) for name, value in rows.items()}
    if all(n == 0 for n in counts.values()):
        state = "EMPTY_COMPATIBLE"
        old_timestamp = None
    else:
        if any(counts.get(name) != value for name, value in TARGET.items()):
            raise RuntimeError("ROW_COUNTS_INVALID")
        if any(value for name, value in counts.items() if name not in TARGET):
            raise RuntimeError("FOREIGN_ROW_INVALID")
        for name in TARGET:
            if any(set(row) != known_columns[name] for row in rows[name]):
                raise RuntimeError("RAW_COLUMNS_INVALID")
        actual_user = rows["users"][0]
        try:
            password_valid = verify_password(password, actual_user["password_hash"])
        except (TypeError, ValueError):
            password_valid = False
        if actual_user["user_id"] != PUBLIC_ACTOR or not password_valid:
            raise RuntimeError("USER_SECURITY_INVALID")
        expected_user = user_type(**bundle["user"],
                                  password_hash=actual_user["password_hash"])
        observed_user = user_type(**actual_user)
        old_timestamp = actual_user["created_at"]
        if observed_user == expected_user:
            state = "EXACT_SEEDED"
        elif observed_user.model_copy(update={"created_at": expected_user.created_at}) == expected_user:
            state = "SOLE_CREATED_AT_MISMATCH"
        else:
            raise RuntimeError("USER_ROW_INVALID")
        expected_user_raw = expected_user.model_dump(mode="python")
        if state == "SOLE_CREATED_AT_MISMATCH":
            expected_user_raw["created_at"] = actual_user["created_at"]
        if _canonical(actual_user) != _canonical(expected_user_raw):
            raise RuntimeError("USER_RAW_ROW_INVALID")
        expected = _expected_model_rows(bundle)
        spec = (("shifts", "shift_id", Shift),
                ("shift_assignments", "assignment_id", ShiftAssignment),
                ("reports", "report_id", Report))
        for name, key, model in spec:
            observed = {str(row[key]): model(**row) for row in rows[name]}
            if len(observed) != TARGET[name] or observed != expected[name]:
                raise RuntimeError("SYNTHETIC_ROW_INVALID")
            if any(_canonical(row) != _canonical(
                    expected[name][str(row[key])].model_dump(mode="python"))
                   for row in rows[name]):
                raise RuntimeError("SYNTHETIC_RAW_ROW_INVALID")
    raw = {name: sorted(_canonical(row) for row in value)
           for name, value in sorted(rows.items())}
    digest = hashlib.sha256(_canonical(raw).encode("utf-8")).hexdigest()
    return {"classification": state, "state_digest": digest,
            "observed_created_at": (_timestamp(old_timestamp)
                                    if old_timestamp else None),
            "counts": counts}
