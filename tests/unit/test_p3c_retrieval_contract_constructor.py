import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from operations_domain.models import (
    Correction, CustomerRequest, Handover, HandoverItem, HandoverStatus, Incident,
    IncidentStatus, Message, OperationalEvent, Report, ReportStatus, Shift, Task,
)
from refinery_bridge.canonical import source_fingerprint
from refinery_bridge.enums import Sensitivity, SourceType
from refinery_bridge.input_models import RefineryEnvelopeV1
from refinery_bridge.output_models import RefineryResultV1
from refinery_bridge.pipeline import refine

from retrieval_contracts import (
    DataScopeEvidenceV1, RetrievalContractInputV1, RetentionAssertionV1,
    ScopeInputV1, construct_retrieval_contract,
)
from retrieval_contracts.enums import NonAdmissionReason, RetentionDisposition
from retrieval_contracts.source_models import ProjectKnowledgeSourceV1
from _refinery_fixtures import controls, empty_context, route
from test_report_snapshot import _content

NOW = datetime(2026, 8, 7, 8, 0, tzinfo=timezone.utc)


def golden_json_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def make_input(source=None, *, tenant_required=False, source_type=None,
               field_selector=None, raw_text=None):
    is_knowledge = isinstance(source, ProjectKnowledgeSourceV1)
    if isinstance(source, Handover):
        shift_ids = tuple(sorted((source.from_shift_id, source.to_shift_id), key=str))
    elif is_knowledge:
        shift_ids = ()
    else:
        shift_ids = (getattr(source, "shift_id", None) or uuid4(),)
    shifts = tuple(Shift(
        shift_id=value, name=f"Shift-{index}", starts_at=NOW - timedelta(hours=8),
        ends_at=NOW + timedelta(hours=4), version=3,
    ) for index, value in enumerate(shift_ids))
    source = source or Message(
        message_id=uuid4(), shift_id=shifts[0].shift_id, sender_id="operator-1",
        text="Crane inspection complete", created_at=NOW,
    )
    id_names = ("message_id", "event_id", "task_id", "request_id", "incident_id",
                "handover_id", "report_id", "source_id")
    source_id = str(next(getattr(source, name) for name in id_names if hasattr(source, name)))
    if isinstance(source, Message):
        source_version, text, selector = "UNVERSIONED", source.text, "text"
    elif isinstance(source, ProjectKnowledgeSourceV1):
        source_version, text, selector = source.source_pin, raw_text or "Reviewed runbook", "document"
    elif isinstance(source, (OperationalEvent, Task)):
        source_version, text, selector = str(source.version), source.title, "title"
    elif isinstance(source, (CustomerRequest, Incident)):
        source_version, text, selector = str(source.version), source.summary, "summary"
    elif isinstance(source, Handover):
        selected = source.items[0]
        source_version, text = str(source.version), selected.summary
        selector = f"items/{selected.item_id}/summary"
    else:
        source_version = str(source.version)
        text = golden_json_bytes(source.content.model_dump(mode="json")).decode("utf-8")
        selector = "content"
    source_type = source_type or (
        SourceType.PROJECT_KNOWLEDGE if is_knowledge else
        SourceType.INTERNAL_MESSAGE if isinstance(source, Message) else
        SourceType.CANONICAL_OPERATIONAL_RECORD
    )
    owner = source.source_owner_id if is_knowledge else "operations-owner"
    payload = {
        "schema_version": "1.0", "source_id": source_id,
        "source_version": source_version, "source_link": f"record:{source_id}",
        "source_type": source_type, "raw_text": text, "received_at": NOW,
        "declared_sensitivity": Sensitivity.INTERNAL,
        "source_owner_id": owner,
        "source_fingerprint": source_fingerprint(text).model_dump(),
    }
    envelope = RefineryEnvelopeV1.model_validate(payload)
    result = refine(
        payload, controls(), dedupe_context=empty_context(), quarantine_route=route()
    )
    assert isinstance(result, RefineryResultV1) and result.context_candidate is not None
    return RetrievalContractInputV1(
        envelope=envelope, refinery_result=result, candidate=result.context_candidate,
        candidate_fingerprint=result.candidate_fingerprint, source=source,
        field_selector=field_selector or selector,
        source_cutoff_utc=NOW, observed_at_utc=NOW, correction=None,
        scope=ScopeInputV1(
            shift_ids=tuple(str(value) for value in shift_ids), parent_shifts=shifts,
            effective_from_utc=None, effective_to_utc=None,
        ),
        retention=RetentionAssertionV1(
            disposition=RetentionDisposition.OWNER_ASSERTED_ACTIVE,
            owner_id="records-owner", policy_version="retention-v1",
            checked_at_utc=NOW, expires_at_utc=NOW + timedelta(days=1),
            source_evidence_id="retention-check-1",
        ),
        data_scope_evidence=DataScopeEvidenceV1(), tenant_required=tenant_required,
    )


def test_message_constructs_deterministic_ready_contract() -> None:
    item = make_input()
    first = construct_retrieval_contract(item)
    second = construct_retrieval_contract(item)
    assert first.kind == "RETRIEVAL_READY"
    assert first.model_dump_json() == second.model_dump_json()
    assert first.source_reference.record_type.value == "Message"
    assert first.source_reference.version.kind.value == "UNVERSIONED"
    assert first.scope.shift_ids == item.scope.shift_ids
    assert first.lifecycle.requires_use_time_revalidation is True
    assert len(first.chunk_id) == len(first.lifecycle.revalidation_token) == 64


def test_canonical_record_fails_closed_without_digest_owner() -> None:
    event = OperationalEvent(
        event_id=uuid4(), shift_id=uuid4(),
        event_type="inspection", title="Crane inspection complete", state="CONFIRMED",
        version=2,
    )
    item = make_input(source=event, source_type=SourceType.CANONICAL_OPERATIONAL_RECORD)
    result = construct_retrieval_contract(item)
    assert result.reason == NonAdmissionReason.SOURCE_DIGEST_OWNER_MISSING


def test_tenant_requirement_fails_closed() -> None:
    result = construct_retrieval_contract(make_input(tenant_required=True))
    assert result.reason == NonAdmissionReason.TENANT_SCOPE_NOT_MODELED


def test_scope_and_retention_failures_are_distinct() -> None:
    item = make_input()
    bad_scope = item.model_copy(update={
        "scope": item.scope.model_copy(update={"shift_ids": ()})
    })
    assert construct_retrieval_contract(bad_scope).reason == NonAdmissionReason.SCOPE_INVALID
    bad_retention = item.model_copy(update={
        "retention": item.retention.model_copy(update={
            "disposition": RetentionDisposition.OWNER_NOT_FOUND,
            "owner_id": None, "source_evidence_id": None,
        })
    })
    assert construct_retrieval_contract(bad_retention).reason == NonAdmissionReason.RETENTION_OWNER_NOT_FOUND


def test_candidate_binding_and_projection_are_distinct() -> None:
    item = make_input()
    mismatched = item.model_copy(update={"candidate_fingerprint": item.candidate_fingerprint.model_copy(update={"sha256": "0" * 64})})
    assert construct_retrieval_contract(mismatched).reason == NonAdmissionReason.CANDIDATE_BINDING_MISMATCH
    wrong_projection = item.model_copy(update={"field_selector": "title"})
    assert construct_retrieval_contract(wrong_projection).reason == NonAdmissionReason.SOURCE_PROJECTION_MISMATCH


def _canonical_sources():
    shift_a, shift_b = uuid4(), uuid4()
    handover_id = uuid4()
    item = HandoverItem(
        item_id=uuid4(), handover_id=handover_id, source_record_type="Task",
        source_record_id=uuid4(), source_digest="1" * 64, summary="Carry inspection",
    )
    return (
        OperationalEvent(shift_id=shift_a, event_type="ops", title="Event title", state="CONFIRMED"),
        Task(shift_id=shift_a, title="Task title", state="CONFIRMED"),
        CustomerRequest(customer_id="customer-1", shift_id=shift_a, summary="Request summary"),
        Incident(shift_id=shift_a, summary="Incident summary", status=IncidentStatus.ACKNOWLEDGED),
        Handover(handover_id=handover_id, from_shift_id=shift_a, to_shift_id=shift_b,
                 status=HandoverStatus.REVIEWED, items=[item], created_by="operator-1"),
        Report(shift_id=shift_a, status=ReportStatus.APPROVED, is_current=True,
               generated_from_cutoff=NOW, content=_content()),
    )


def test_every_canonical_type_fails_closed_without_public_digest_owner() -> None:
    observed = []
    for source in _canonical_sources():
        result = construct_retrieval_contract(make_input(source=source))
        observed.append(result.reason)
    assert observed == [NonAdmissionReason.SOURCE_DIGEST_OWNER_MISSING] * 6


def test_project_knowledge_current_pin_is_ready_and_stale_pin_fails() -> None:
    current = ProjectKnowledgeSourceV1(
        source_id="runbook-1", source_pin="abc123", current_source_pin="abc123",
        source_owner_id="knowledge-owner",
    )
    ready = construct_retrieval_contract(make_input(source=current))
    assert ready.kind == "RETRIEVAL_READY"
    assert ready.scope.shift_ids == ()
    stale = current.model_copy(update={"current_source_pin": "def456"})
    result = construct_retrieval_contract(make_input(source=stale))
    assert result.reason == NonAdmissionReason.STALE_SOURCE


def test_retention_expired_erased_and_stale_active_are_not_admitted() -> None:
    item = make_input()
    cases = (
        item.retention.model_copy(update={"disposition": RetentionDisposition.OWNER_ASSERTED_EXPIRED}),
        item.retention.model_copy(update={"disposition": RetentionDisposition.OWNER_ASSERTED_ERASED,
                                          "erased_at_utc": NOW}),
        item.retention.model_copy(update={"expires_at_utc": NOW}),
    )
    for retention in cases:
        result = construct_retrieval_contract(item.model_copy(update={"retention": retention}))
        assert result.reason == NonAdmissionReason.RETENTION_NOT_ACTIVE


def test_correction_on_unversioned_source_is_lifecycle_invalid() -> None:
    item = make_input()
    correction = Correction(
        record_type="Message", record_id=item.source.message_id, reason="fix",
        requested_by="operator-1", previous_version=1, new_version=2,
    )
    result = construct_retrieval_contract(item.model_copy(update={"correction": correction}))
    assert result.reason == NonAdmissionReason.LIFECYCLE_INVALID


def test_each_source_type_has_one_ineligible_lifecycle_fixture() -> None:
    sources = _canonical_sources()
    ineligible = (
        sources[0].model_copy(update={"state": "DRAFT"}),
        sources[1].model_copy(update={"state": "DRAFT"}),
        sources[2].model_copy(update={"shift_id": None}),
        sources[3].model_copy(update={"status": "REPORTED"}),
        sources[4].model_copy(update={"status": "DRAFT"}),
        sources[5].model_copy(update={"is_current": False}),
        make_input().source.model_copy(update={"source": "EXTERNAL"}),
    )
    for source in ineligible:
        result = construct_retrieval_contract(make_input(source=source))
        assert result.reason == NonAdmissionReason.SOURCE_NOT_ELIGIBLE


def test_report_stored_snapshot_digest_does_not_replace_public_digest_owner() -> None:
    report = _canonical_sources()[-1]
    assert len(report.content.snapshot_digest) == 64
    result = construct_retrieval_contract(make_input(source=report))
    assert result.reason == NonAdmissionReason.SOURCE_DIGEST_OWNER_MISSING


def test_all_selector_shapes_and_missing_handover_item() -> None:
    for source in _canonical_sources():
        result = construct_retrieval_contract(make_input(source=source))
        assert result.reason == NonAdmissionReason.SOURCE_DIGEST_OWNER_MISSING
    handover = _canonical_sources()[4]
    missing = make_input(
        source=handover,
        field_selector=f"items/{uuid4()}/summary",
    )
    assert construct_retrieval_contract(missing).reason == (
        NonAdmissionReason.SOURCE_PROJECTION_MISMATCH
    )


def test_zero_one_two_and_invalid_scope_matrix() -> None:
    knowledge = ProjectKnowledgeSourceV1(
        source_id="runbook-1", source_pin="pin-1", current_source_pin="pin-1",
        source_owner_id="knowledge-owner",
    )
    assert construct_retrieval_contract(make_input(source=knowledge)).scope.shift_ids == ()
    message = make_input()
    assert len(construct_retrieval_contract(message).scope.shift_ids) == 1
    handover = make_input(source=_canonical_sources()[4])
    assert len(handover.scope.shift_ids) == 2

    wrong = message.model_copy(update={
        "scope": message.scope.model_copy(update={"shift_ids": ()}),
    })
    assert construct_retrieval_contract(wrong).reason == NonAdmissionReason.SCOPE_INVALID
    too_many = message.model_copy(update={
        "scope": message.scope.model_copy(update={
            "shift_ids": ("a", "b", "c"), "parent_shifts": (),
        }),
    })
    assert construct_retrieval_contract(too_many).reason == NonAdmissionReason.SCOPE_INVALID
    inverted = message.model_copy(update={
        "scope": message.scope.model_copy(update={
            "effective_from_utc": NOW + timedelta(seconds=1),
            "effective_to_utc": NOW,
        }),
    })
    assert construct_retrieval_contract(inverted).reason == NonAdmissionReason.SCOPE_INVALID

