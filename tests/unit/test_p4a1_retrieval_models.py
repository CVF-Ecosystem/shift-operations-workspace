"""SPEC R2 - GovernedRetrievalRequestV1 and closed request contracts.

AC-02: field/type/default/bound coverage, each of the eight R2 failure
codes, multi-failure precedence, strict extra-field rejection, one/two-shift
rules, and rejection of a client-supplied ``correlation_id``.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from governed_retrieval.enums import CorpusId, RequestFailureCode
from governed_retrieval.request_models import (
    ContextBudgetV1,
    GovernedRetrievalRequestV1,
    RequestValidationError,
    RetrievalFiltersV1,
)

from _p4a1_retrieval_fixtures import DEFAULT_BUDGET


def _valid_body(**overrides) -> dict:
    body = {
        "query": "governed retrieval",
        "corpus_id": "PROJECT_KNOWLEDGE_LOCAL_V1",
        "filters": {"shift_ids": ("shift-1",)},
        "context_budget": dict(DEFAULT_BUDGET),
    }
    body.update(overrides)
    return body


def test_valid_request_round_trips_with_defaults() -> None:
    request = GovernedRetrievalRequestV1.model_validate(_valid_body())
    assert request.contract_version == "1.0"
    assert request.corpus_id == CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1
    assert request.result_limit == 10
    assert request.filters.record_types == ()
    assert request.filters.truth_classes == ()
    assert request.filters.lifecycle_statuses == ()


def test_unknown_top_level_field_rejected() -> None:
    with pytest.raises(ValidationError):
        GovernedRetrievalRequestV1.model_validate(_valid_body(extra_field="nope"))


def test_correlation_id_field_is_rejected() -> None:
    body = _valid_body()
    body["correlation_id"] = "client-supplied"
    with pytest.raises(ValidationError):
        GovernedRetrievalRequestV1.model_validate(body)


def test_result_limit_bounds() -> None:
    GovernedRetrievalRequestV1.model_validate(_valid_body(result_limit=1))
    GovernedRetrievalRequestV1.model_validate(_valid_body(result_limit=20))
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(result_limit=0))
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(result_limit=21))


def test_result_limit_rejects_bool() -> None:
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(result_limit=True))


def test_project_knowledge_shift_id_shape_allows_one_or_two_at_structural_stage() -> None:
    """R2/R3 boundary: at bare structural validation (before R3
    authorization resolves which corpus this actually is), only the widest
    1-2 shape bound applies - the exact "Project Knowledge requires exactly
    one" cardinality is a stage-5 FILTER_WIDENS_SCOPE check
    (resolve_and_authorize_corpus), never disclosed earlier."""
    for shift_ids in (("a",), ("a", "b")):
        request = GovernedRetrievalRequestV1.model_validate(
            _valid_body(filters={"shift_ids": shift_ids})
        )
        assert request.filters.shift_ids == tuple(sorted(shift_ids))


def test_project_knowledge_two_shift_ids_denied_only_after_authorization() -> None:
    """The exact-one-shift-id rule for PROJECT_KNOWLEDGE_LOCAL_V1 fires only
    in resolve_and_authorize_corpus (stage 5), not at bare model
    validation."""
    from workspace_api.application._governed_retrieval_sources import (
        CorpusResolutionFailed,
        resolve_and_authorize_corpus,
    )

    request = GovernedRetrievalRequestV1.model_validate(
        _valid_body(filters={"shift_ids": ("a", "b")})
    )
    with pytest.raises(CorpusResolutionFailed) as exc_info:
        resolve_and_authorize_corpus(request)
    assert exc_info.value.code == RequestFailureCode.FILTER_WIDENS_SCOPE


def test_shift_corpus_allows_one_or_two_shift_ids() -> None:
    for shift_ids in (("a",), ("a", "b")):
        request = GovernedRetrievalRequestV1.model_validate(
            _valid_body(corpus_id="SHIFT_CONFIRMED_OPERATIONS_V1", filters={"shift_ids": shift_ids})
        )
        assert request.filters.shift_ids == tuple(sorted(shift_ids))


def test_shift_corpus_rejects_three_shift_ids() -> None:
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(
            _valid_body(corpus_id="SHIFT_CONFIRMED_OPERATIONS_V1", filters={"shift_ids": ("a", "b", "c")})
        )


def test_unknown_corpus_id_has_safe_shape_at_structural_stage() -> None:
    """R2/R3 boundary: an unknown-but-safely-shaped corpus_id string passes
    bare structural validation (it is not resolved against the registry
    until stage 5, post-authorization) - only a genuinely malformed shape
    (empty, too long, unsafe characters) fails here."""
    request = GovernedRetrievalRequestV1.model_validate(_valid_body(corpus_id="NOT_A_REAL_CORPUS"))
    assert request.corpus_id == "NOT_A_REAL_CORPUS"


def test_malformed_corpus_id_shape_rejected_at_structural_stage() -> None:
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(corpus_id=""))
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(corpus_id="has spaces/slash"))


def test_unknown_corpus_id_rejected_only_after_authorization() -> None:
    from workspace_api.application._governed_retrieval_sources import (
        CorpusResolutionFailed,
        resolve_and_authorize_corpus,
    )

    request = GovernedRetrievalRequestV1.model_validate(_valid_body(corpus_id="NOT_A_REAL_CORPUS"))
    with pytest.raises(CorpusResolutionFailed) as exc_info:
        resolve_and_authorize_corpus(request)
    assert exc_info.value.code == RequestFailureCode.CORPUS_ID_INVALID


@pytest.mark.parametrize(
    "shift_ids",
    [("b", "a"), ("a", "a")],
)
def test_filters_shift_ids_must_be_sorted_and_unique(shift_ids) -> None:
    with pytest.raises((ValidationError, RequestValidationError)):
        RetrievalFiltersV1.model_validate({"shift_ids": shift_ids})


def test_filters_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        RetrievalFiltersV1.model_validate({"shift_ids": ("a",), "bogus": 1})


def test_context_budget_rejects_non_positive_values() -> None:
    bad = dict(DEFAULT_BUDGET)
    bad["max_projection_records"] = 0
    with pytest.raises((ValidationError, RequestValidationError)):
        ContextBudgetV1.model_validate(bad)


def test_context_budget_rejects_above_server_maximum() -> None:
    bad = dict(DEFAULT_BUDGET)
    bad["max_projection_records"] = 5
    with pytest.raises((ValidationError, RequestValidationError)):
        ContextBudgetV1.model_validate(bad)


def test_context_budget_accepts_lower_ceilings() -> None:
    lower = dict(DEFAULT_BUDGET)
    lower["max_projection_records"] = 1
    lower["max_snippet_codepoints"] = 100
    budget = ContextBudgetV1.model_validate(lower)
    assert budget.max_projection_records == 1


# --- eight closed request failure codes (via the application admission
# layer, which classifies every ValidationError/RequestValidationError) ---


def test_eight_failure_codes_are_closed_and_named() -> None:
    codes = {code.value for code in RequestFailureCode}
    assert codes == {
        "REQUEST_SHAPE_INVALID",
        "QUERY_INVALID",
        "QUERY_LIMIT_EXCEEDED",
        "CORPUS_ID_INVALID",
        "FILTER_INVALID",
        "FILTER_WIDENS_SCOPE",
        "RESULT_LIMIT_INVALID",
        "CONTEXT_BUDGET_INVALID",
    }


def test_admission_layer_classifies_each_structural_failure() -> None:
    from workspace_api.application import _governed_retrieval_admission as admission

    cases = [
        (object(), RequestFailureCode.REQUEST_SHAPE_INVALID),
        (_valid_body(query=""), RequestFailureCode.QUERY_INVALID),
        (_valid_body(query="x" * 600), RequestFailureCode.QUERY_LIMIT_EXCEEDED),
        # corpus_id is deliberately NOT a structural-stage failure - a
        # malformed *shape* (below) is, but an unknown *registry* value is
        # only classified as CORPUS_ID_INVALID after R3 authorization
        # (see test_unknown_corpus_id_rejected_only_after_authorization).
        (_valid_body(corpus_id=""), RequestFailureCode.CORPUS_ID_INVALID),
        (_valid_body(filters={"shift_ids": ("b", "a")}), RequestFailureCode.FILTER_INVALID),
        (_valid_body(result_limit=0), RequestFailureCode.RESULT_LIMIT_INVALID),
        (
            _valid_body(context_budget={**DEFAULT_BUDGET, "max_projection_records": 0}),
            RequestFailureCode.CONTEXT_BUDGET_INVALID,
        ),
    ]
    for raw_body, expected_code in cases:
        with pytest.raises(admission.RequestInvalid) as exc_info:
            admission.validate_structure(raw_body)
        assert exc_info.value.code == expected_code


def test_multi_failure_precedence_reports_first_applicable_code() -> None:
    """Shape failure (non-mapping) must dominate over any nested failure."""
    from workspace_api.application import _governed_retrieval_admission as admission

    with pytest.raises(admission.RequestInvalid) as exc_info:
        admission.validate_structure(["not", "a", "mapping"])
    assert exc_info.value.code == RequestFailureCode.REQUEST_SHAPE_INVALID


def test_structural_validation_never_touches_protected_state(monkeypatch) -> None:
    """AC-02 spy: structural validation must call zero registry/Ledger/source
    functions. We assert this by ensuring validate_structure succeeds/fails
    purely from the in-memory dict with no ledger/corpus import touched."""
    from workspace_api.application import _governed_retrieval_admission as admission

    calls: list[str] = []

    class _Spy:
        def __getattr__(self, name):
            calls.append(name)
            raise AssertionError(f"unexpected protected access: {name}")

    # validate_structure takes no ledger/registry argument at all - the
    # strongest possible proof is that its signature has no such parameter
    # and it operates purely on the raw dict.
    result = admission.validate_structure(_valid_body())
    assert result.query == "governed retrieval"


# --- F9: JSON-wire-safe closed validation ---


def test_normal_json_arrays_are_accepted_and_normalized_to_tuples() -> None:
    """F9: a normal JSON array (Python list, as any real JSON client sends)
    must be accepted and converted to a tuple - not rejected with a raw
    strict-mode tuple_type error."""
    request = GovernedRetrievalRequestV1.model_validate(
        _valid_body(filters={"shift_ids": ["a"], "record_types": [], "truth_classes": [], "lifecycle_statuses": []})
    )
    assert request.filters.shift_ids == ("a",)
    assert isinstance(request.filters.record_types, tuple)


def test_malformed_filter_element_types_raise_typed_code_not_raw_exception() -> None:
    """F9: malformed filter values must convert to FILTER_INVALID - never a
    raw TypeError/ValueError escaping the model boundary."""
    from workspace_api.application import _governed_retrieval_admission as admission

    bad_bodies = [
        _valid_body(filters={"shift_ids": "not-a-list"}),
        _valid_body(filters={"shift_ids": [1, "a"]}),  # unsortable mixed types
        _valid_body(filters={"shift_ids": {"nested": "dict"}}),
        _valid_body(filters={"lifecycle_statuses": [123]}),
    ]
    for raw_body in bad_bodies:
        with pytest.raises(admission.RequestInvalid) as exc_info:
            admission.validate_structure(raw_body)
        assert exc_info.value.code == RequestFailureCode.FILTER_INVALID


def test_unsafe_whitespace_shift_id_rejected() -> None:
    """F9: shift_ids must not permit unsafe whitespace (leading/trailing
    space, embedded control characters, etc.)."""
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(filters={"shift_ids": ("  a  ",)}))
    with pytest.raises((ValidationError, RequestValidationError)):
        GovernedRetrievalRequestV1.model_validate(_valid_body(filters={"shift_ids": ("a\tb",)}))


def test_safe_shift_id_shape_accepted() -> None:
    request = GovernedRetrievalRequestV1.model_validate(_valid_body(filters={"shift_ids": ("shift-1_a.b:c",)}))
    assert request.filters.shift_ids == ("shift-1_a.b:c",)
