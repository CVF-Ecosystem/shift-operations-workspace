"""Pure P5-A A7 request, receipt, and response-contract helpers.

This module never reads a credential or opens a connection. Structural tests
exercise these functions with inert bytes, not provider emulation evidence.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from invariant_family_contract import load_json_no_dup, matches_shape_exactly

ADMISSION_ID = "P5A-A7-ONE-CANARY-20261023"
ENDPOINT = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen-flash"
MATRIX_PATH = Path(__file__).resolve().parents[1] / "docs/cvf/invariants/p5a-live-canary-outcomes.json"
PROMPT_TEMPLATE = (
    'Return only the JSON object below and no other text:\n'
    '{"gate_observation_digest":"<DIGEST>","result":"echoed"}'
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
BEARER = re.compile(r"(?i)Bearer\s+\S+")
JWT = re.compile(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
URL_SECRET = re.compile(r"https?://[^\s\"']+", re.IGNORECASE)
SENSITIVE_FIELD = re.compile(r"(?i)(authorization|api.?key|access.?token|secret|password)")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def reject_duplicate(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def strict_json(data: str | bytes) -> object:
    def bad_constant(_value: str) -> None:
        raise ValueError("non-standard JSON constant")

    return json.loads(data, object_pairs_hook=reject_duplicate, parse_constant=bad_constant)


def request_body(gate_digest: str) -> bytes:
    if not HEX64.fullmatch(gate_digest):
        raise ValueError("invalid gate digest")
    prompt = PROMPT_TEMPLATE.replace("<DIGEST>", gate_digest)
    if not prompt.isascii() or len(prompt) > 256:
        raise ValueError("PUBLIC prompt bound exceeded")
    return canonical_bytes({
        "model": MODEL, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 64, "n": 1, "stream": False, "enable_thinking": False,
    })


def _safe_url(match: re.Match) -> str:
    from urllib.parse import urlsplit

    try:
        parts = urlsplit(match.group(0))
        return f"{parts.scheme}://{parts.hostname or '<redacted-host>'}{parts.path}"
    except ValueError:
        return "<redacted-url>"


def sanitize_text(value: str, key: str | None = None) -> str:
    if key:
        value = value.replace(key, "<redacted-key>")
    value = BEARER.sub("Bearer <redacted>", value)
    value = JWT.sub("<redacted-jwt>", value)
    return URL_SECRET.sub(_safe_url, value)


def _sanitize_value(value: object, key: str | None) -> object:
    if isinstance(value, dict):
        return {"<redacted-field>" if SENSITIVE_FIELD.search(name)
                else sanitize_text(name, key): "<redacted>" if SENSITIVE_FIELD.search(name)
                else _sanitize_value(item, key) for name, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(item, key) for item in value]
    if isinstance(value, str):
        return sanitize_text(value, key)
    return value


def sanitized_response(raw: bytes, key: str | None = None) -> tuple[str, str]:
    decoded = raw.decode("utf-8", errors="replace")
    try:
        value = strict_json(decoded)
    except (ValueError, UnicodeError):
        safe = sanitize_text(decoded, key)
    else:
        safe = canonical_bytes(_sanitize_value(value, key)).decode("utf-8")
    if key:
        safe = safe.replace(key, "<redacted-key>")
    return safe, sha256(safe.encode("utf-8"))


def validate_response(status: int, raw: bytes, gate_digest: str) -> tuple[str, dict]:
    """Return a fixed reason and matrix-compatible validated fields.

    Usage is evaluated independently, so a response rejected for model/content
    still retains valid provider usage and the conservative cost estimate.
    """
    fields: dict = {"http_status": status, "usage_state": "NOT_PARSED"}
    try:
        payload = strict_json(raw)
    except (ValueError, UnicodeError):
        return "RESPONSE_JSON_INVALID", fields
    if not isinstance(payload, dict):
        return "RESPONSE_JSON_INVALID", fields

    usage = payload.get("usage")
    if usage is None:
        fields["usage_state"] = "ABSENT"
    elif not isinstance(usage, dict):
        fields["usage_state"] = "INVALID"
    else:
        keys = ("prompt_tokens", "completion_tokens", "total_tokens")
        values = [usage.get(name) for name in keys]
        if any(type(value) is not int or value < 0 for value in values):
            fields["usage_state"] = "INVALID"
        else:
            prompt, completion, _total = values
            fields.update(zip(keys, values))
            fields["estimated_cost_nano_usd"] = prompt * 50 + completion * 400
            fields["usage_state"] = "VALID"

    if status in range(300, 400):
        return "REDIRECT_RESPONSE", fields
    if status != 200:
        return "NON_200", fields
    if payload.get("model") != MODEL:
        return "MODEL_MISMATCH", fields
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return "CHOICE_INVALID", fields
    choice = choices[0]
    if type(choice.get("index")) is not int or choice["index"] != 0:
        return "CHOICE_INVALID", fields
    if choice.get("finish_reason") != "stop":
        return "FINISH_REASON_INVALID", fields
    message = choice.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        return "CHOICE_INVALID", fields
    if message.get("tool_calls") or message.get("refusal"):
        return "CHOICE_INVALID", fields
    if message.get("reasoning_content"):
        return "REASONING_PRESENT", fields
    content = message.get("content")
    if not isinstance(content, str):
        return "CONTENT_NOT_JSON", fields
    try:
        echo = strict_json(content)
    except ValueError:
        return "CONTENT_NOT_JSON", fields
    if not isinstance(echo, dict) or set(echo) != {"gate_observation_digest", "result"}:
        return "CONTENT_SCHEMA_INVALID", fields
    if echo["gate_observation_digest"] != gate_digest or echo["result"] != "echoed":
        return "DIGEST_ECHO_MISMATCH", fields
    if fields["usage_state"] != "VALID":
        return "USAGE_ABSENT" if fields["usage_state"] == "ABSENT" else "USAGE_INVALID", fields
    if fields["total_tokens"] != fields["prompt_tokens"] + fields["completion_tokens"]:
        return "TOTAL_TOKENS_INVALID", fields
    if fields["prompt_tokens"] > 256:
        return "INPUT_CAP_EXCEEDED", fields
    if fields["completion_tokens"] > 64:
        return "OUTPUT_CAP_EXCEEDED", fields
    if fields["estimated_cost_nano_usd"] > 10_000_000:
        return "COST_CAP_EXCEEDED", fields
    fields.update(model=MODEL, choice_count=1, finish_reason="stop", gate_digest_echo=gate_digest)
    return "NONE", fields


def terminal_receipt(outcome: str, stage: str, reason: str, digest: str,
                     counts: dict, **fields: object) -> dict:
    receipt = {
        "outcome": outcome, "admission_id": ADMISSION_ID, "terminal_stage": stage,
        "terminal_reason": reason, "gate_observation_sha256": digest,
        "secret_material_persisted": False, "authorization_header_recorded": False,
        **counts, **fields,
    }
    matrix = load_json_no_dup(MATRIX_PATH)
    shapes = [shape for item in matrix["outcomes"] if item["outcomeId"] == outcome
              for shape in item["shapes"]]
    if not any(matches_shape_exactly(shape, receipt, matrix) for shape in shapes):
        raise ValueError("terminal receipt violates frozen invariant family")
    return receipt
