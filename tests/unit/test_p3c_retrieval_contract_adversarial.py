from collections.abc import Mapping
from datetime import datetime

import pytest
from operations_domain.models import Correction

from retrieval_contracts.canonical import canonical_json_bytes
from retrieval_contracts.constructor import construct_retrieval_contract
from retrieval_contracts.enums import NonAdmissionReason
from test_p3c_retrieval_contract_constructor import make_input


class RaisingPayload:
    @property
    def contract_version(self):
        raise RuntimeError("must not inspect arbitrary object properties")


class RaisingMapping(Mapping):
    def __getitem__(self, key):
        raise RuntimeError("hostile mapping")

    def __iter__(self):
        raise RuntimeError("hostile mapping")

    def __len__(self):
        raise RuntimeError("hostile mapping")


@pytest.mark.parametrize(
    "payload",
    [None, True, 1, 1.5, "secret source text", [], (), object(), {"contract_version": "1.0"}],
)
def test_constructor_is_total_and_disclosure_safe(payload) -> None:
    result = construct_retrieval_contract(payload)
    assert result.kind == "NOT_ADMITTED"
    serialized = result.model_dump_json()
    assert "secret source text" not in serialized
    assert "traceback" not in serialized.lower()
    assert "exception" not in serialized.lower()


@pytest.mark.parametrize("payload", [RaisingPayload(), RaisingMapping()])
def test_hostile_objects_and_properties_never_escape(payload) -> None:
    result = construct_retrieval_contract(payload)
    assert result.reason == NonAdmissionReason.INVARIANT_VIOLATION
    assert result.safe_source_id is None
    assert result.safe_record_id is None


@pytest.mark.parametrize("unsafe_id", [
    "x" * 129,
    "credential-secret-value",
    " raw secret text ",
    "record\x00identifier",
])
def test_invalid_mapping_identifiers_are_never_disclosed(unsafe_id) -> None:
    result = construct_retrieval_contract({
        "contract_version": "2.0",
        "source": {"event_id": unsafe_id},
    })
    assert result.reason == NonAdmissionReason.CONTRACT_VERSION_UNSUPPORTED
    assert result.safe_source_id is None
    assert result.safe_record_id is None
    assert unsafe_id not in result.model_dump_json()


def test_unknown_contract_version_has_fixed_precedence() -> None:
    result = construct_retrieval_contract({"contract_version": "2.0", "unknown": object()})
    assert result.reason == NonAdmissionReason.CONTRACT_VERSION_UNSUPPORTED


def test_fixed_precedence_p3a_before_unknown_source_and_structure_before_p3a() -> None:
    payload = make_input().model_dump()
    payload["source"] = {"mystery": "x"}
    assert construct_retrieval_contract(payload).reason == NonAdmissionReason.UNKNOWN_SOURCE_TYPE

    payload["candidate_fingerprint"]["sha256"] = "0" * 64
    assert construct_retrieval_contract(payload).reason == (
        NonAdmissionReason.CANDIDATE_BINDING_MISMATCH
    )

    payload["refinery_result"]["disposition"] = "QUARANTINED"
    assert construct_retrieval_contract(payload).reason == NonAdmissionReason.REFINERY_RESULT_NOT_READY

    payload["unknown"] = "structural-defect"
    assert construct_retrieval_contract(payload).reason == NonAdmissionReason.INVARIANT_VIOLATION


def test_candidate_binding_precedes_ineligible_typed_source() -> None:
    item = make_input()
    correction = Correction(
        record_type="Message", record_id=item.source.message_id, reason="fix",
        requested_by="operator-1", previous_version=1, new_version=2,
    )
    bad = item.model_copy(update={
        "source": correction,
        "candidate_fingerprint": item.candidate_fingerprint.model_copy(
            update={"sha256": "0" * 64}
        ),
    })
    assert construct_retrieval_contract(bad).reason == (
        NonAdmissionReason.CANDIDATE_BINDING_MISMATCH
    )


def test_unknown_source_precedes_later_data_scope_defect() -> None:
    payload = make_input().model_dump()
    payload["source"] = {"mystery": "x"}
    payload["data_scope_evidence"]["status"] = "ALLOWED"
    assert construct_retrieval_contract(payload).reason == NonAdmissionReason.UNKNOWN_SOURCE_TYPE


@pytest.mark.parametrize("component", [
    "envelope", "refinery_result", "candidate", "candidate_fingerprint",
])
def test_malformed_p3a_component_is_structural_before_binding(component) -> None:
    payload = make_input().model_dump()
    malformed = {"source_id": "secret"}
    if component == "refinery_result":
        malformed = {"disposition": payload[component]["disposition"]}
    payload[component] = malformed
    assert construct_retrieval_contract(payload).reason == (
        NonAdmissionReason.INVARIANT_VIOLATION
    )


@pytest.mark.parametrize("component", ["envelope", "candidate", "candidate_fingerprint"])
def test_parsed_but_unequal_p3a_component_is_binding_mismatch(component) -> None:
    payload = make_input().model_dump()
    if component == "candidate_fingerprint":
        payload[component]["sha256"] = "0" * 64
    else:
        payload[component]["source_id"] = "other-source"
    assert construct_retrieval_contract(payload).reason == (
        NonAdmissionReason.CANDIDATE_BINDING_MISMATCH
    )


def test_unknown_field_and_bool_are_invariant_failures() -> None:
    item = make_input()
    payload = item.model_dump()
    payload["unknown"] = "forbidden"
    assert construct_retrieval_contract(payload).reason == NonAdmissionReason.INVARIANT_VIOLATION
    payload = item.model_dump()
    payload["tenant_required"] = 1
    assert construct_retrieval_contract(payload).reason == NonAdmissionReason.INVARIANT_VIOLATION


def test_canonical_json_exact_bytes_and_rejections() -> None:
    assert canonical_json_bytes({"b": 2, "a": "x"}) == b'{"a":"x","b":2}'
    for value in ({"x": 1.0}, {1: "x"}, {"x": "e\u0301"}, {"x": datetime(2026, 1, 1)}):
        with pytest.raises(ValueError):
            canonical_json_bytes(value)


def test_output_never_contains_envelope_raw_text() -> None:
    item = make_input()
    result = construct_retrieval_contract(item)
    dumped = result.model_dump(mode="json")
    assert "raw_text" not in str(dumped)
    assert dumped["redacted_normalized_text"] == item.candidate.redacted_normalized_text


def test_equivalent_mapping_order_is_deterministic() -> None:
    item = make_input()
    first = construct_retrieval_contract(item)
    payload = item.model_dump()
    reversed_payload = dict(reversed(tuple(payload.items())))
    second = construct_retrieval_contract(reversed_payload)
    assert first.model_dump_json() == second.model_dump_json()


def test_malformed_data_scope_has_its_closed_reason() -> None:
    payload = make_input().model_dump()
    payload["data_scope_evidence"]["status"] = "ALLOWED"
    result = construct_retrieval_contract(payload)
    assert result.reason == NonAdmissionReason.DATA_SCOPE_EVIDENCE_INVALID


@pytest.mark.parametrize("mutation", [
    {"source": {}},
    {"source": {"event_id": []}},
    {"field_selector": " selector"},
    {"field_selector": "selector\n"},
    {"scope": {"shift_ids": ["x"]}},
    {"retention": []},
    {"candidate": {"source_id": "secret"}},
])
def test_broad_invalid_payloads_are_deterministic_and_closed(mutation) -> None:
    payload = make_input().model_dump()
    payload.update(mutation)
    first = construct_retrieval_contract(payload)
    second = construct_retrieval_contract(payload)
    assert first.kind == "NOT_ADMITTED"
    assert first.model_dump_json() == second.model_dump_json()
    assert first.safe_source_id is None
    assert first.safe_record_id is None


def test_candidate_and_provenance_binding_mismatch_classes() -> None:
    item = make_input()
    bad_receipts = tuple([
        item.refinery_result.stage_receipts[0].model_copy(update={"outcome": "FAIL"}),
        *item.refinery_result.stage_receipts[1:],
    ])
    mutations = (
        {"candidate_fingerprint": item.candidate_fingerprint.model_copy(
            update={"sha256": "0" * 64}
        )},
        {"envelope": item.envelope.model_copy(update={"source_id": "other-source"})},
        {"envelope": item.envelope.model_copy(update={"source_version": "other-version"})},
        {"envelope": item.envelope.model_copy(update={"source_owner_id": "other-owner"})},
        {"envelope": item.envelope.model_copy(update={"source_link": "record:other"})},
        {"refinery_result": item.refinery_result.model_copy(
            update={"stage_receipts": bad_receipts}
        )},
    )
    for update in mutations:
        result = construct_retrieval_contract(item.model_copy(update=update))
        assert result.reason == NonAdmissionReason.CANDIDATE_BINDING_MISMATCH
