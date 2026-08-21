"""P4-A2 SPEC R13 - strict answer schema and post-dispatch citation-
membership validation against the exact post-omission granted set."""

from __future__ import annotations

import pytest

from governed_rag.errors import OutputValidationFailedError
from governed_rag.validation import ANSWER_JSON_SCHEMA, parse_answer, validate_citation_membership

C1 = "1" * 64
C2 = "2" * 64
C3 = "3" * 64


def test_parses_valid_answer_output():
    output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C1]}], "abstention_reason": ""}
    answer = parse_answer(output)
    assert answer.status.value == "ANSWER"


def test_parses_valid_abstain_output():
    output = {"status": "ABSTAIN", "claims": [], "abstention_reason": "insufficient evidence"}
    answer = parse_answer(output)
    assert answer.status.value == "ABSTAIN"


def test_rejects_unknown_top_level_field():
    output = {
        "status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C1]}],
        "abstention_reason": "", "extra": "nope",
    }
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_answer_with_no_claims():
    output = {"status": "ANSWER", "claims": [], "abstention_reason": ""}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_uncited_claim():
    output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": []}], "abstention_reason": ""}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_duplicate_citations_within_a_claim():
    output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C1, C1]}], "abstention_reason": ""}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_abstain_with_claims():
    output = {"status": "ABSTAIN", "claims": [{"text": "x", "citation_ids": [C1]}], "abstention_reason": "why"}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_abstain_with_empty_reason():
    output = {"status": "ABSTAIN", "claims": [], "abstention_reason": ""}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_unknown_status_literal():
    output = {"status": "MAYBE", "claims": [], "abstention_reason": "x"}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


def test_rejects_more_than_eight_claims():
    claims = [{"text": f"claim {i}", "citation_ids": [C1]} for i in range(9)]
    output = {"status": "ANSWER", "claims": claims, "abstention_reason": ""}
    with pytest.raises(OutputValidationFailedError):
        parse_answer(output)


class TestCitationMembership:
    def test_accepts_when_every_citation_is_granted(self):
        output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C1]}], "abstention_reason": ""}
        answer = parse_answer(output)
        validate_citation_membership(answer, (C1, C2))  # should not raise

    def test_rejects_citation_outside_granted_set(self):
        output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C3]}], "abstention_reason": ""}
        answer = parse_answer(output)
        with pytest.raises(OutputValidationFailedError):
            validate_citation_membership(answer, (C1, C2))

    def test_rejects_when_one_of_multiple_citations_is_unknown(self):
        output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C1, C3]}], "abstention_reason": ""}
        answer = parse_answer(output)
        with pytest.raises(OutputValidationFailedError):
            validate_citation_membership(answer, (C1, C2))

    def test_membership_checked_against_exact_post_omission_set_not_pre_omission(self):
        """A citation that was in the pre-injection/pre-minimization set but
        got omitted must NOT be accepted, even though it was once granted by
        P4-A1 - membership is checked against the precise post-omission set
        only."""
        output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [C2]}], "abstention_reason": ""}
        answer = parse_answer(output)
        pre_omission_set = (C1, C2)  # C2 was omitted by injection/minimization
        post_omission_set = (C1,)
        with pytest.raises(OutputValidationFailedError):
            validate_citation_membership(answer, post_omission_set)
        # sanity: it WOULD have passed against the wider pre-omission set,
        # proving the test actually distinguishes the two sets.
        validate_citation_membership(answer, pre_omission_set)


def test_schema_declares_object_type_and_closed_additional_properties():
    assert ANSWER_JSON_SCHEMA["type"] == "object"
    assert ANSWER_JSON_SCHEMA["additionalProperties"] is False


def test_schema_has_no_prompt_or_free_form_body_fields():
    properties = set(ANSWER_JSON_SCHEMA["properties"])
    forbidden = {"prompt", "context", "raw_output", "messages", "system"}
    assert not (properties & forbidden)
