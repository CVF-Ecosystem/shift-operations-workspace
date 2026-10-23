"""Structural A7 contract fixtures only; no provider result or live proof."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _p5a_live_contract import (
    MODEL,
    PROMPT_TEMPLATE,
    canonical_bytes,
    request_body,
    sanitized_response,
    sha256,
    strict_json,
    terminal_receipt,
    validate_response,
)
from invariant_family_contract import generate_mutations, load_json_no_dup, matches_shape_exactly

DIGEST = "a" * 64
SHA = "b" * 64


def _response(*, digest=DIGEST, prompt=100, completion=25, model=MODEL,
              content=None, reasoning=None) -> bytes:
    return canonical_bytes({
        "model": model, "choices": [{"index": 0, "finish_reason": "stop",
                                    "message": {"role": "assistant", "reasoning_content": reasoning,
                                                "content": content if content is not None else
                                                json.dumps({"gate_observation_digest": digest,
                                                            "result": "echoed"})}}],
        "usage": {"prompt_tokens": prompt, "completion_tokens": completion,
                  "total_tokens": prompt + completion},
    })


def _counts(*, marker=1, key=1, post=1, response=1, accepted=1):
    return {"marker_reservations": marker, "key_read_attempts": key,
            "transport_attempts": post, "responses": response,
            "accepted_responses": accepted, "retry_count": 0,
            "redirect_count": 0, "fallback_count": 0}


def sample_terminal_receipts() -> dict[str, dict]:
    """Independent structural corpus for every frozen matrix shape."""
    zero = _counts(marker=0, key=0, post=0, response=0, accepted=0)
    no_post = _counts(key=1, post=0, response=0, accepted=0)
    no_response = _counts(response=0, accepted=0)
    rejected = _counts(accepted=0)
    return {
        "P5A_LIVE_PRECALL_BLOCKED_ZERO_CALL": terminal_receipt(
            "PRECALL_BLOCKED_ZERO_CALL", "PREFLIGHT", "WORKTREE_DIRTY", DIGEST, zero),
        "P5A_LIVE_RESERVED_NO_TRANSPORT": terminal_receipt(
            "RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "KEY_LOOKUP", "KEY_MISSING", DIGEST, no_post),
        "P5A_LIVE_RESERVED_TRANSPORT_NO_RESPONSE": terminal_receipt(
            "RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "TRANSPORT", "NETWORK_TIMEOUT", DIGEST,
            no_response, sanitized_request_sha256=SHA),
        "P5A_LIVE_RESERVED_RESPONSE_REJECTED_VALID_USAGE": terminal_receipt(
            "RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "RESPONSE_VALIDATION", "DIGEST_ECHO_MISMATCH",
            DIGEST, rejected, sanitized_request_sha256=SHA, sanitized_response_sha256=SHA,
            http_status=200, usage_state="VALID", prompt_tokens=100, completion_tokens=25,
            total_tokens=125, estimated_cost_nano_usd=15_000),
        "P5A_LIVE_RESERVED_RESPONSE_REJECTED_UNAVAILABLE_USAGE": terminal_receipt(
            "RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "RESPONSE_VALIDATION", "USAGE_ABSENT", DIGEST,
            rejected, sanitized_request_sha256=SHA, sanitized_response_sha256=SHA,
            http_status=200, usage_state="ABSENT"),
        "P5A_LIVE_ACCEPTED_SINGLE_RESPONSE": terminal_receipt(
            "ACCEPTED_SINGLE_RESPONSE", "ACCEPTED", "NONE", DIGEST, _counts(),
            sanitized_request_sha256=SHA, sanitized_response_sha256=SHA, http_status=200,
            model=MODEL, choice_count=1, finish_reason="stop", gate_digest_echo=DIGEST,
            usage_state="VALID", prompt_tokens=100, completion_tokens=25, total_tokens=125,
            estimated_cost_nano_usd=15_000),
    }


@pytest.mark.parametrize("shape_id", [
    "P5A_LIVE_PRECALL_BLOCKED_ZERO_CALL", "P5A_LIVE_RESERVED_NO_TRANSPORT",
    "P5A_LIVE_RESERVED_TRANSPORT_NO_RESPONSE",
    "P5A_LIVE_RESERVED_RESPONSE_REJECTED_VALID_USAGE",
    "P5A_LIVE_RESERVED_RESPONSE_REJECTED_UNAVAILABLE_USAGE",
    "P5A_LIVE_ACCEPTED_SINGLE_RESPONSE",
])
def test_full_generated_mutation_corpus_rejects_every_shape_violation(shape_id):
    matrix = load_json_no_dup(ROOT / "docs/cvf/invariants/p5a-live-canary-outcomes.json")
    shape = next(shape for outcome in matrix["outcomes"] for shape in outcome["shapes"]
                 if shape["shapeId"] == shape_id)
    sample = sample_terminal_receipts()[shape_id]
    assert matches_shape_exactly(shape, sample, matrix)
    mutations = generate_mutations(matrix, shape_id, sample)
    assert mutations
    for mutation in mutations:
        assert not matches_shape_exactly(shape, mutation.payload, matrix), mutation.mutationId


def test_request_is_exact_public_digest_echo_without_header_or_report_data():
    body = strict_json(request_body(DIGEST))
    assert set(body) == {"model", "messages", "max_tokens", "n", "stream", "enable_thinking"}
    assert body["model"] == MODEL and body["max_tokens"] == 64
    assert body["n"] == 1 and body["stream"] is False and body["enable_thinking"] is False
    assert body["messages"] == [{"role": "user", "content": PROMPT_TEMPLATE.replace("<DIGEST>", DIGEST)}]
    assert len(body["messages"][0]["content"]) <= 256
    assert "Authorization" not in request_body(DIGEST).decode()
    with pytest.raises(ValueError):
        request_body("not-a-digest")


def test_strict_nested_json_and_secret_sanitizer():
    with pytest.raises(ValueError):
        strict_json('{"outer":{"a":1,"a":2}}')
    with pytest.raises(ValueError):
        strict_json('{"n":NaN}')
    key = "EXACT_SECRET_CANARY_123"
    raw = canonical_bytes({key: key, "Authorization": "Bearer " + key,
                           "url": "https://u:p@example.com/path?token=" + key})
    safe, digest = sanitized_response(raw, key)
    assert key not in safe and "Bearer " + key not in safe
    assert "token=" not in safe and "u:p@" not in safe
    assert digest == sha256(safe.encode())


def test_accepted_response_fixture_and_matrix_mutations():
    reason, fields = validate_response(200, _response(), DIGEST)
    assert reason == "NONE"
    assert fields["estimated_cost_nano_usd"] == 15_000
    receipt = terminal_receipt("ACCEPTED_SINGLE_RESPONSE", "ACCEPTED", reason,
                               DIGEST, _counts(), sanitized_request_sha256=SHA,
                               sanitized_response_sha256=SHA, **fields)
    matrix = load_json_no_dup(ROOT / "docs/cvf/invariants/p5a-live-canary-outcomes.json")
    shape = next(s for outcome in matrix["outcomes"] if outcome["outcomeId"] == "ACCEPTED_SINGLE_RESPONSE"
                 for s in outcome["shapes"])
    assert matches_shape_exactly(shape, receipt, matrix)
    for field, changed in (("retry_count", 1), ("transport_attempts", 0),
                           ("gate_digest_echo", "c" * 64), ("usage_state", "ABSENT")):
        mutation = {**receipt, field: changed}
        assert not matches_shape_exactly(shape, mutation, matrix), field


@pytest.mark.parametrize("payload,reason", [
    (_response(digest="c" * 64), "DIGEST_ECHO_MISMATCH"),
    (_response(model="other-model"), "MODEL_MISMATCH"),
    (_response(prompt=257), "INPUT_CAP_EXCEEDED"),
    (_response(completion=65), "OUTPUT_CAP_EXCEEDED"),
    (_response(reasoning="hidden"), "REASONING_PRESENT"),
    (b'{"model":"qwen-flash","model":"qwen-flash"}', "RESPONSE_JSON_INVALID"),
    (b'{"model":NaN}', "RESPONSE_JSON_INVALID"),
])
def test_rejected_structural_response_variants(payload, reason):
    actual, fields = validate_response(200, payload, DIGEST)
    assert actual == reason
    assert fields["usage_state"] in {"VALID", "NOT_PARSED"}


def test_response_valid_usage_preserved_on_non_200_and_invalid_echo():
    for status, expected in ((429, "NON_200"), (302, "REDIRECT_RESPONSE"), (200, "DIGEST_ECHO_MISMATCH")):
        body = _response(digest="c" * 64)
        reason, fields = validate_response(status, body, DIGEST)
        assert reason == expected and fields["usage_state"] == "VALID"
        assert fields["prompt_tokens"] == 100 and fields["estimated_cost_nano_usd"] == 15_000


def test_all_three_terminal_shapes_accept_only_expected_counts():
    pre = terminal_receipt("PRECALL_BLOCKED_ZERO_CALL", "PREFLIGHT",
                           "WORKTREE_DIRTY", DIGEST, _counts(marker=0, key=0, post=0,
                                                               response=0, accepted=0))
    reserved = terminal_receipt("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "KEY_LOOKUP",
                                "KEY_MISSING", DIGEST, _counts(key=1, post=0,
                                                                 response=0, accepted=0))
    transport = terminal_receipt("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "TRANSPORT",
                                 "NETWORK_TIMEOUT", DIGEST, _counts(response=0, accepted=0),
                                 sanitized_request_sha256=SHA)
    assert pre["marker_reservations"] == 0
    assert reserved["marker_reservations"] == 1 and reserved["transport_attempts"] == 0
    assert transport["transport_attempts"] == 1 and transport["responses"] == 0
    with pytest.raises(ValueError):
        terminal_receipt("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "TRANSPORT", "NETWORK_TIMEOUT",
                         DIGEST, _counts(response=0, accepted=0),
                         sanitized_request_sha256=SHA, secret_material_persisted=True)
