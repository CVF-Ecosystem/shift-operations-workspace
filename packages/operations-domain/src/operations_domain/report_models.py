"""Report domain models (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).

Split out of ``models.py`` (SPEC R1) under the hard 300-line file-size
guard. One governed report type: `END_SHIFT`. Every Report row is an
immutable snapshot version (ADR Decision 2): only ``status``/``is_current``
are lifecycle-owned. Duplicates (never imports) hash helpers/enum value
sets from ``report_snapshot.py``/``models.py`` (sink package; ``models.py``
imports FROM this module). Every record's exact value/type/format shape,
manifest cross-checks, R7 section order and R7 evidence order are enforced
structurally, matching each field's OWN owning domain/DB contract (e.g.
plain strings may be empty where the domain model allows it)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_UUID_STR = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?Z$")

_VERSIONED_RECORD_TYPES = {"OperationalEvent", "Task", "Incident", "Handover"}
_UNVERSIONED_RECORD_TYPES = {"Correction", "CustomerRequest"}
_RECORD_TYPES = _VERSIONED_RECORD_TYPES | _UNVERSIONED_RECORD_TYPES

_SECTION_ORDER = (
    "operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers",
)
_SECTION_TYPE_TO_RECORD_TYPE = {
    "operational_events": "OperationalEvent", "corrections": "Correction", "tasks": "Task",
    "customer_requests": "CustomerRequest", "incidents": "Incident", "handovers": "Handover",
}

_RISK_CLASSES = {"R0", "R1", "R2", "R3", "R4"}
_EVENT_STATES = {"RAW", "NORMALIZED", "PROPOSED", "CONFIRMED", "REJECTED", "CORRECTED", "FROZEN"}
_TASK_STATUSES = {"OPEN", "IN_PROGRESS", "BLOCKED", "DONE", "CARRY_OVER", "CANCELLED"}
_CUSTOMER_REQUEST_STATUSES = {"NEW", "ACKNOWLEDGED", "IN_PROGRESS", "WAITING", "RESOLVED", "CLOSED"}
_INCIDENT_STATUSES = {"REPORTED", "ACKNOWLEDGED", "MITIGATING", "RESOLVED", "CLOSED"}
_HANDOVER_STATUSES = {"DRAFT", "REVIEWED", "ACKNOWLEDGED"}

_EVIDENCE_T, _ITEMS_T = "evidence", "handover_items"

_is_str = lambda v: isinstance(v, str)
_is_uuid = lambda v: isinstance(v, str) and bool(_UUID_STR.match(v))
_is_dt = lambda v: isinstance(v, str) and bool(_ISO_UTC.match(v))
_is_hex64 = lambda v: isinstance(v, str) and bool(_HEX64.match(v))
_opt = lambda pred: (lambda v: v is None or pred(v))
_enum = lambda values: (lambda v: isinstance(v, str) and v in values)

_STR, _OPT_STR = _is_str, _opt(_is_str)
_UUID_T, _OPT_UUID = _is_uuid, _opt(_is_uuid)
_DT, _OPT_DT = _is_dt, _opt(_is_dt)
_INT = lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 1  # versioned source records
_CORRECTION_VERSION = lambda v: isinstance(v, int) and not isinstance(v, bool)  # DB CHECK: new_version > previous_version only
_OPT_HEX64 = _opt(_is_hex64)


_RECORD_SCHEMAS: dict[str, dict[str, object]] = {  # field -> predicate; record_type/record_id checked separately
    "OperationalEvent": {
        "shift_id": _UUID_T, "event_type": _STR, "title": _STR, "description": _OPT_STR,
        "risk_class": _enum(_RISK_CLASSES), "state": _enum(_EVENT_STATES),
        "starts_at": _OPT_DT, "ends_at": _OPT_DT, "owner_id": _OPT_STR,
        "version": _INT, "evidence": _EVIDENCE_T,
    },
    "Correction": {
        "target_record_type": _STR, "target_record_id": _UUID_T, "reason": _STR,
        "requested_by": _STR, "previous_version": _CORRECTION_VERSION,
        "new_version": _CORRECTION_VERSION, "created_at": _DT,
    },
    "Task": {
        "shift_id": _UUID_T, "title": _STR, "description": _OPT_STR, "status": _enum(_TASK_STATUSES),
        "owner_id": _OPT_STR, "due_at": _OPT_DT, "risk_class": _enum(_RISK_CLASSES),
        "state": _enum(_EVENT_STATES), "version": _INT, "created_at": _DT, "evidence": _EVIDENCE_T,
    },
    "CustomerRequest": {
        "customer_id": _STR, "shift_id": _OPT_UUID, "summary": _STR, "details": _OPT_STR,
        "status": _enum(_CUSTOMER_REQUEST_STATUSES), "source_message_id": _OPT_UUID,
        "received_at": _DT, "promised_at": _OPT_DT, "owner_id": _OPT_STR,
    },
    "Incident": {
        "shift_id": _UUID_T, "risk_class": _enum(_RISK_CLASSES), "summary": _STR, "description": _OPT_STR,
        "status": _enum(_INCIDENT_STATUSES), "owner_id": _OPT_STR, "version": _INT,
        "created_at": _DT, "evidence": _EVIDENCE_T,
    },
    "Handover": {
        "from_shift_id": _UUID_T, "to_shift_id": _UUID_T, "status": _enum(_HANDOVER_STATUSES),
        "created_by": _STR, "reviewed_by": _OPT_STR, "reviewed_at": _OPT_DT,
        "received_by": _OPT_STR, "acknowledged_at": _OPT_DT, "version": _INT,
        "created_at": _DT, "items": _ITEMS_T,
    },
}
_HANDOVER_ITEM_SCHEMA: dict[str, object] = {
    "item_id": _UUID_T, "source_record_type": _STR, "source_record_id": _UUID_T,
    "source_digest": _is_hex64, "summary": _STR, "owner_id": _OPT_STR, "due_at": _OPT_DT,
    "risk_class": _enum(_RISK_CLASSES), "evidence": _EVIDENCE_T,
}
_EVIDENCE_SCHEMA: dict[str, object] = {
    "evidence_id": _UUID_T, "source_type": _STR, "source_id": _STR, "sha256": _OPT_HEX64,
}
_RECORD_FIELD_SETS = {rt: frozenset({"record_type", "record_id", *fields}) for rt, fields in _RECORD_SCHEMAS.items()}
_HANDOVER_ITEM_KEYS = frozenset(_HANDOVER_ITEM_SCHEMA)
_EVIDENCE_KEYS = frozenset(_EVIDENCE_SCHEMA)


def _check_value(field: str, predicate, value, ctx: str) -> None:
    if not predicate(value):
        raise ValueError(f"{ctx}.{field} has an invalid canonical value/type/format: {value!r}")


def _evidence_sort_key(item: dict) -> tuple:
    return (item["evidence_id"], item["source_type"], item["source_id"], item["sha256"] or "")


def _check_list(schema: dict, keys: frozenset, items: object, ctx: str) -> None:
    if not isinstance(items, list):
        raise ValueError(f"{ctx} must be a list")
    for item in items:
        _check_dict_shape(schema, keys, item, ctx)
    if schema is _EVIDENCE_SCHEMA:
        keys_in_order = [_evidence_sort_key(item) for item in items]
        if keys_in_order != sorted(keys_in_order):
            raise ValueError(f"{ctx} is not in SPEC R7 canonical evidence order")


def _check_dict_shape(schema: dict, keys: frozenset, obj: object, ctx: str) -> None:
    if not isinstance(obj, dict) or set(obj.keys()) != keys:
        raise ValueError(f"{ctx} has wrong field set: {sorted(obj.keys()) if isinstance(obj, dict) else obj!r}")
    for field, tag in schema.items():
        if tag == _EVIDENCE_T:
            _check_list(_EVIDENCE_SCHEMA, _EVIDENCE_KEYS, obj["evidence"], f"{ctx}.evidence[]")
        elif tag == _ITEMS_T:
            _check_list(_HANDOVER_ITEM_SCHEMA, _HANDOVER_ITEM_KEYS, obj["items"], "Handover item")
        else:
            _check_value(field, tag, obj[field], ctx)
    if schema is _RECORD_SCHEMAS["Correction"] and obj["new_version"] <= obj["previous_version"]:
        raise ValueError(f"{ctx}.new_version ({obj['new_version']!r}) must be greater than previous_version ({obj['previous_version']!r})")


def _assert_record_shape(record_type: str, record: dict) -> None:
    _check_dict_shape(_RECORD_SCHEMAS[record_type], _RECORD_FIELD_SETS[record_type], record, record_type)


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _recompute_record_digest(record: dict) -> str:
    """SHA-256 over the exact record dict, byte-identical to report_snapshot._sha256(payload)."""
    return hashlib.sha256(_canonical_bytes(record)).hexdigest()


class ReportStatus(StrEnum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    FROZEN = "FROZEN"


class ReportType(StrEnum):
    END_SHIFT = "END_SHIFT"


class ReportSourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_type: str
    record_id: UUID
    source_version: int | None = None
    source_digest: str

    @field_validator("record_type")
    @classmethod
    def _record_type_known(cls, value: str) -> str:
        if value not in _RECORD_TYPES:
            raise ValueError(f"unknown record_type: {value!r}")
        return value

    @field_validator("source_digest")
    @classmethod
    def _source_digest_shape(cls, value: str) -> str:
        if not _HEX64.match(value):
            raise ValueError("source_digest must be a lowercase 64-character hex SHA-256 digest")
        return value

    @model_validator(mode="after")
    def _source_version_matches_record_type(self) -> "ReportSourceRef":
        versioned = self.record_type in _VERSIONED_RECORD_TYPES
        if versioned and (self.source_version is None or self.source_version < 1):
            raise ValueError(f"{self.record_type} source_version must be an integer >= 1")
        if not versioned and self.source_version is not None:
            raise ValueError(f"{self.record_type} source_version must be null")
        return self


class ReportSection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    section_type: str
    records: list[dict]

    @model_validator(mode="after")
    def _records_match_section_record_type_and_shape(self) -> "ReportSection":
        if self.section_type not in _SECTION_TYPE_TO_RECORD_TYPE:
            raise ValueError(f"unknown section_type: {self.section_type!r}")
        expected_record_type = _SECTION_TYPE_TO_RECORD_TYPE[self.section_type]
        for record in self.records:
            if record.get("record_type") != expected_record_type:
                raise ValueError(f"section {self.section_type!r} contains record_type={record.get('record_type')!r}, expected {expected_record_type!r}")
            record_id = record.get("record_id")
            if not isinstance(record_id, str) or not _UUID_STR.match(record_id):
                raise ValueError(f"{expected_record_type} record has an invalid record_id: {record_id!r}")
            _assert_record_shape(expected_record_type, record)
        return self

    @model_validator(mode="after")
    def _records_are_in_r7_canonical_order(self) -> "ReportSection":
        keys = [_r7_sort_key(self.section_type, r) for r in self.records]
        if keys != sorted(keys):
            raise ValueError(f"section {self.section_type!r} records are not in SPEC R7 canonical order")
        return self


_R7_SORT_FIELD = {
    "operational_events": "starts_at", "corrections": "created_at", "tasks": "created_at",
    "customer_requests": "received_at", "incidents": "created_at", "handovers": "created_at",
}


def _r7_sort_key(section_type: str, record: dict) -> tuple:
    value = record[_R7_SORT_FIELD[section_type]]
    rid = record["record_id"]
    return (value is None, value or "", rid) if section_type == "operational_events" else (value, rid)


class ReportContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "1.0"
    sections: list[ReportSection]
    source_manifest: list[ReportSourceRef]
    snapshot_digest: str

    @model_validator(mode="after")
    def _own_field_shapes_and_section_order(self) -> "ReportContent":
        if self.schema_version != "1.0":
            raise ValueError('schema_version must be exactly "1.0"')
        if not _HEX64.match(self.snapshot_digest):
            raise ValueError("snapshot_digest must be a lowercase 64-character hex SHA-256 digest")
        actual = tuple(s.section_type for s in self.sections)
        if actual != _SECTION_ORDER:
            raise ValueError(f"sections must be exactly {list(_SECTION_ORDER)} in that order, got {list(actual)}")
        return self

    @model_validator(mode="after")
    def _manifest_matches_records_exactly(self) -> "ReportContent":
        seen: set[tuple[str, str]] = set()
        for ref in self.source_manifest:
            key = (ref.record_type, str(ref.record_id))
            if key in seen:
                raise ValueError(f"duplicate source manifest entry: {key}")
            seen.add(key)

        records_by_key: dict[tuple[str, str], dict] = {}
        record_keys: list[tuple[str, str]] = []
        for section in self.sections:
            for record in section.records:
                key = (record.get("record_type"), record.get("record_id"))
                record_keys.append(key)
                records_by_key[key] = record
        manifest_keys = [(ref.record_type, str(ref.record_id)) for ref in self.source_manifest]

        if manifest_keys != record_keys:
            missing, extra = set(record_keys) - set(manifest_keys), set(manifest_keys) - set(record_keys)
            if missing or extra:
                raise ValueError(f"source_manifest mismatch: no-manifest-entry={sorted(missing)}, no-record={sorted(extra)}")
            raise ValueError("source_manifest order does not match the per-section record order")

        for ref in self.source_manifest:
            record = records_by_key[(ref.record_type, str(ref.record_id))]
            if ref.record_type in _VERSIONED_RECORD_TYPES and ref.source_version != record.get("version"):
                raise ValueError(f"{ref.record_type} {ref.record_id} source_version does not equal the record's own persisted version")
            if ref.source_digest != _recompute_record_digest(record):
                raise ValueError(f"{ref.record_type} {ref.record_id} source_digest does not equal SHA-256 of its own canonical record JSON")
        return self


class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    report_type: ReportType = ReportType.END_SHIFT
    version: int = Field(default=1, ge=1)
    status: ReportStatus = ReportStatus.DRAFT
    is_current: bool = True
    content: ReportContent
    generated_from_cutoff: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
