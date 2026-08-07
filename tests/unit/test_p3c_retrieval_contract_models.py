from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from operations_domain.models import Correction, OperationalEvent
from pydantic import ValidationError

from retrieval_contracts.contract_models import (
    DataScopeEvidenceV1, LifecycleObservationV1, RetentionAssertionV1,
    VersionBindingV1,
)
from retrieval_contracts.enums import (
    DataScopeStatus, NonAdmissionReason, RecordType, RetentionDisposition,
    ResultKind, TenantScopeStatus, TruthClass, VersionKind,
)
from retrieval_contracts.source_models import ProjectKnowledgeSourceV1
from retrieval_contracts.canonical import source_facts
from retrieval_contracts.constructor import _lineage, construct_retrieval_contract
from test_p3c_retrieval_contract_constructor import make_input

NOW = datetime(2026, 8, 7, tzinfo=timezone.utc)


def test_closed_enums_are_exact() -> None:
    assert [item.value for item in TruthClass] == [
        "CANONICAL_OPERATIONAL_RECORD", "ADVISORY_SOURCE_EVIDENCE"
    ]
    assert [item.value for item in RecordType] == [
        "OperationalEvent", "Task", "CustomerRequest", "Incident",
        "Handover", "Report", "Message", "PROJECT_KNOWLEDGE",
    ]
    assert [item.value for item in VersionKind] == [
        "INTEGER_VERSION", "SOURCE_VERSION_STRING", "UNVERSIONED"
    ]
    assert [item.value for item in RetentionDisposition] == [
        "OWNER_ASSERTED_ACTIVE", "OWNER_ASSERTED_EXPIRED",
        "OWNER_ASSERTED_ERASED", "OWNER_NOT_FOUND",
    ]
    assert [item.value for item in TenantScopeStatus] == ["NOT_MODELED"]
    assert [item.value for item in DataScopeStatus] == ["NOT_EVALUATED"]
    assert [item.value for item in ResultKind] == ["RETRIEVAL_READY", "NOT_ADMITTED"]
    assert len(NonAdmissionReason) == 18


@pytest.mark.parametrize(
    ("kind", "integer", "string"),
    [
        (VersionKind.INTEGER_VERSION, 1, None),
        (VersionKind.SOURCE_VERSION_STRING, None, "pin-v1"),
        (VersionKind.UNVERSIONED, None, None),
    ],
)
def test_version_binding_three_valid_branches(kind, integer, string) -> None:
    value = VersionBindingV1(
        kind=kind, integer_version=integer, source_version_string=string
    )
    assert value.kind == kind


@pytest.mark.parametrize(
    ("kind", "integer", "string"),
    [
        (VersionKind.INTEGER_VERSION, None, None),
        (VersionKind.INTEGER_VERSION, 1, "x"),
        (VersionKind.SOURCE_VERSION_STRING, 1, "x"),
        (VersionKind.SOURCE_VERSION_STRING, None, None),
        (VersionKind.UNVERSIONED, 1, None),
        (VersionKind.UNVERSIONED, None, "x"),
    ],
)
def test_version_binding_rejects_every_contradiction(kind, integer, string) -> None:
    with pytest.raises(ValidationError):
        VersionBindingV1(kind=kind, integer_version=integer, source_version_string=string)


def test_strict_models_reject_bool_unknown_and_non_nfc() -> None:
    with pytest.raises(ValidationError):
        VersionBindingV1(kind=VersionKind.INTEGER_VERSION, integer_version=True)
    with pytest.raises(ValidationError):
        DataScopeEvidenceV1(extra="forbidden")
    with pytest.raises(ValidationError):
        VersionBindingV1(
            kind=VersionKind.SOURCE_VERSION_STRING,
            source_version_string="e\u0301",
        )


def test_retention_model_is_exact_and_utc() -> None:
    value = RetentionAssertionV1(
        disposition=RetentionDisposition.OWNER_ASSERTED_ACTIVE,
        owner_id="records-owner", policy_version="retention-v1",
        checked_at_utc=NOW, source_evidence_id="ret-1",
    )
    assert set(value.model_dump()) == {
        "disposition", "owner_id", "policy_version", "checked_at_utc",
        "expires_at_utc", "erased_at_utc", "source_evidence_id",
    }
    with pytest.raises(ValidationError):
        RetentionAssertionV1(
            disposition=RetentionDisposition.OWNER_ASSERTED_ACTIVE,
            owner_id="owner", policy_version="v1",
            checked_at_utc=datetime(2026, 8, 7), source_evidence_id="ret-1",
        )


@pytest.mark.parametrize("field", [
    "source_id", "source_pin", "current_source_pin", "source_owner_id",
])
@pytest.mark.parametrize("unsafe", [" pin", "pin ", "pin\x00value", "pin\nvalue"])
def test_every_project_knowledge_identifier_rejects_whitespace_and_control(
    field, unsafe,
) -> None:
    values = {
        "source_id": "runbook-1",
        "source_pin": "pin-1",
        "current_source_pin": "pin-1",
        "source_owner_id": "knowledge-owner",
    }
    values[field] = unsafe
    with pytest.raises(ValidationError):
        ProjectKnowledgeSourceV1(**values)


@pytest.mark.parametrize("unsafe", [" CONFIRMED", "CONFIRMED ", "BAD\x7fSTATUS"])
def test_lifecycle_source_status_is_a_safe_identifier(unsafe) -> None:
    with pytest.raises(ValidationError):
        LifecycleObservationV1(
            source_status=unsafe,
            source_version=VersionBindingV1(kind=VersionKind.UNVERSIONED),
            parent_shift_id=None,
            parent_shift_version=None,
            parent_shift_status=None,
            report_status=None,
            report_snapshot_digest=None,
            correction_lineage=None,
            revalidation_token="0" * 64,
        )


def _retention(disposition, *, expires=None, erased=None):
    return RetentionAssertionV1(
        disposition=disposition,
        owner_id="records-owner",
        policy_version="retention-v1",
        checked_at_utc=NOW,
        expires_at_utc=expires,
        erased_at_utc=erased,
        source_evidence_id="ret-1",
    )


def test_retention_disposition_time_matrix_and_boundaries() -> None:
    assert _retention(
        RetentionDisposition.OWNER_ASSERTED_ACTIVE,
        expires=NOW + timedelta(microseconds=1),
    ).expires_at_utc > NOW
    assert _retention(
        RetentionDisposition.OWNER_ASSERTED_EXPIRED, expires=NOW
    ).expires_at_utc == NOW
    assert _retention(
        RetentionDisposition.OWNER_ASSERTED_ERASED, erased=NOW
    ).erased_at_utc == NOW
    invalid = (
        (RetentionDisposition.OWNER_ASSERTED_ACTIVE, None, NOW),
        (RetentionDisposition.OWNER_ASSERTED_ACTIVE, NOW, None),
        (RetentionDisposition.OWNER_ASSERTED_EXPIRED, None, None),
        (RetentionDisposition.OWNER_ASSERTED_EXPIRED, NOW + timedelta(seconds=1), None),
        (RetentionDisposition.OWNER_ASSERTED_EXPIRED, NOW, NOW),
        (RetentionDisposition.OWNER_ASSERTED_ERASED, None, None),
        (RetentionDisposition.OWNER_ASSERTED_ERASED, None, NOW + timedelta(seconds=1)),
        (RetentionDisposition.OWNER_ASSERTED_ERASED, NOW, NOW),
        (RetentionDisposition.OWNER_NOT_FOUND, NOW, None),
    )
    for disposition, expires, erased in invalid:
        with pytest.raises(ValidationError):
            _retention(disposition, expires=expires, erased=erased)


def test_retention_public_nonadmission_covers_all_dispositions_and_bad_times() -> None:
    item = make_input()
    cases = (
        item.retention.model_copy(update={
            "disposition": RetentionDisposition.OWNER_ASSERTED_EXPIRED,
            "expires_at_utc": NOW,
        }),
        item.retention.model_copy(update={
            "disposition": RetentionDisposition.OWNER_ASSERTED_ERASED,
            "expires_at_utc": None, "erased_at_utc": NOW,
        }),
        item.retention.model_copy(update={
            "disposition": RetentionDisposition.OWNER_NOT_FOUND,
            "owner_id": None, "expires_at_utc": None,
        }),
        item.retention.model_copy(update={"expires_at_utc": NOW}),
        item.retention.model_copy(update={"erased_at_utc": NOW}),
    )
    expected = (
        NonAdmissionReason.RETENTION_NOT_ACTIVE,
        NonAdmissionReason.RETENTION_NOT_ACTIVE,
        NonAdmissionReason.RETENTION_OWNER_NOT_FOUND,
        NonAdmissionReason.RETENTION_NOT_ACTIVE,
        NonAdmissionReason.RETENTION_NOT_ACTIVE,
    )
    for retention, reason in zip(cases, expected, strict=True):
        payload = item.model_dump()
        payload["retention"] = retention.model_dump()
        assert construct_retrieval_contract(payload).reason == reason


def test_correction_lineage_valid_wrong_record_and_wrong_version() -> None:
    event = OperationalEvent(
        event_id=uuid4(), shift_id=uuid4(), event_type="inspection",
        title="Crane inspection complete", state="CONFIRMED", version=2,
    )
    item = make_input(source=event)
    correction = Correction(
        record_type="OperationalEvent", record_id=event.event_id, reason="fix",
        requested_by="operator-1", previous_version=1, new_version=2,
    )
    facts = source_facts(event, "title")
    lineage = _lineage(item.model_copy(update={"correction": correction}), facts)
    assert lineage.record_id == str(event.event_id)
    assert lineage.previous_version == 1 and lineage.new_version == 2
    invalid = (
        correction.model_copy(update={"record_id": uuid4()}),
        correction.model_copy(update={"new_version": 3}),
    )
    for value in invalid:
        with pytest.raises(ValueError):
            _lineage(item.model_copy(update={"correction": value}), facts)
