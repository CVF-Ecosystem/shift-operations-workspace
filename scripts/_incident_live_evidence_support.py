"""Support module for run_incident_live_governance_evidence.py.

INC-REV-F5 (SPEC R15-A/R15-B, ADR section 6): owns everything that touches
provider HTTP, sanitization, safe endpoint description, provider-call
accounting and receipt rendering, so the runner stays a coherent
orchestration facade. Nothing here ever returns, prints, or writes the exact
configured provider key, a bearer/JWT value, or a URL's userinfo/query/
fragment - every provider-derived string is sanitized before it leaves
:func:`call_provider`.

INC-REV-F6 ENDPOINT_CREDENTIAL_FAILURE_LEAK: a transport exception that
embeds `req.full_url` could previously carry URL-only credential material
(userinfo/query/fragment) past `sanitize_secret_text`, because that function
only ever knew about the API key, not about secrets smuggled in the endpoint
URL itself. The fix is structural, not another regex: :func:`_clean_endpoint`
strips userinfo/query/fragment from the endpoint BEFORE any
``Request``/``urlopen`` call is ever constructed, so `req.full_url` can never
contain them regardless of what an exception (construction or transport)
later embeds - and the stripped fragments are also scrubbed from any error
text as defense-in-depth.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

_BEARER_RE = re.compile(r"Bearer\s+\S+", re.IGNORECASE)
_JWT_RE = re.compile(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")


class ProviderCallCounter:
    """A fresh instance per runner invocation (SPEC R15-B) - never a module
    global, so accounting cannot leak or persist across calls/tests."""

    def __init__(self) -> None:
        self.count = 0

    def record(self) -> None:
        self.count += 1


def sanitize_secret_text(text: str | None, *, api_key: str | None = None) -> str:
    """Strip the exact configured key and any bearer/JWT-shaped material from
    provider-derived text (error bodies, exception messages, response
    excerpts) before it can reach a return value, print, or receipt."""
    if not text:
        return text or ""
    if api_key:
        text = text.replace(api_key, "<redacted-key>")
    text = _BEARER_RE.sub("Bearer <redacted>", text)
    text = _JWT_RE.sub("<redacted-jwt>", text)
    return text


def safe_endpoint_description(endpoint: str) -> str:
    """Scheme + hostname only (SPEC R15-A) - no userinfo, port, path, query
    or fragment. This is the only endpoint form a receipt may ever store."""
    parts = urlsplit(endpoint)
    hostname = parts.hostname or "<unknown-host>"
    return f"{parts.scheme}://{hostname}"


def _clean_endpoint(endpoint: str) -> tuple[str, list[str]]:
    """Split ``endpoint`` into (url-safe-for-request, [secret fragments]).

    The returned URL carries no userinfo, query or fragment - it is the ONLY
    form ever handed to ``Request``/``urlopen`` (INC-REV-F6), so
    ``req.full_url`` can never embed credential material smuggled into the
    endpoint's userinfo/query/fragment, no matter what a later construction
    or transport exception chooses to stringify. The returned fragment list
    (non-empty username/password/query/fragment pieces) is for scrubbing any
    error text as a second, defense-in-depth layer.
    """
    parts = urlsplit(endpoint)
    secrets = [v for v in (parts.username, parts.password, parts.query, parts.fragment) if v]
    netloc = parts.hostname or ""
    if parts.port:
        netloc = f"{netloc}:{parts.port}"
    clean = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    return clean, secrets


def call_provider(
    *, model: str, api_key: str, endpoint: str, prompt: str, expected_token: str,
    counter: ProviderCallCounter,
) -> dict:
    """One real, non-mocked provider call. Every field of the returned dict
    is already sanitized - callers never need to scrub it again. Covers both
    request-construction and transport failures: the endpoint is cleaned
    before ``Request()`` is ever built, and that construction call itself
    lives inside the same try/except as ``urlopen`` (INC-REV-F6)."""
    counter.record()
    clean_endpoint, endpoint_secrets = _clean_endpoint(endpoint)

    def _sanitize(text: str) -> str:
        text = sanitize_secret_text(text, api_key=api_key)
        for secret in endpoint_secrets:
            text = text.replace(secret, "<redacted-endpoint-credential>")
        return text

    body = json.dumps(
        {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 32}
    ).encode("utf-8")
    started = datetime.now(timezone.utc)
    try:
        req = urllib.request.Request(
            clean_endpoint, data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:300]
        return {
            "outcome": "FAIL", "reached_server": True, "http_status": exc.code,
            "error": _sanitize(error_body),
            "started_at": started.isoformat(),
        }
    except Exception as exc:  # noqa: BLE001 - construction or transport failure, sanitized alike
        return {
            "outcome": "FAIL", "reached_server": False, "http_status": None,
            "error": _sanitize(f"{type(exc).__name__}: {exc}"),
            "started_at": started.isoformat(),
        }

    content = _sanitize(payload.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return {
        "outcome": "PASS" if expected_token in content else "FAIL",
        "reached_server": True, "http_status": status,
        "response_excerpt": content.strip()[:200],
        "started_at": started.isoformat(),
    }


def render_receipt(
    path: Path, *, gate_results: list[dict], quorum_detail: str, provider_result: dict,
    model: str, safe_endpoint: str, call_count: int,
) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# P2-A incident vertical - live governance evidence receipt", "",
        f"Overall outcome: {overall}", "",
        "Produced by `scripts/run_incident_live_governance_evidence.py` via "
        "`scripts/_incident_live_evidence_support.py` (P2A-INCIDENT-VERTICAL, "
        "SPEC section 6/R14/R15-A). Sanitized: contains no API key, no "
        "Authorization header, no JWT, no raw secret, no URL userinfo/query/"
        "fragment.", "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}", f"- Endpoint (host only): {safe_endpoint}", "",
        "## 1. Gate-refusal cases (in-process, real code path, observed provider-call delta)", "",
        "| Case | Outcome | Detail | Provider calls |", "|---|---|---|---|",
    ]
    for r in gate_results:
        lines.append(f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |")
    lines += [
        "", "## 2. Genuine acknowledgement construction (real code path)", "",
        f"- {quorum_detail}", "", "## 3. Real provider call", "",
        "Reached only because the acknowledgement above genuinely satisfied the R2 quorum.", "",
        f"- Outcome: **{provider_result['outcome']}**",
        f"- Reached the provider (got any HTTP response): **{provider_result.get('reached_server', False)}**",
        f"- HTTP status: {provider_result.get('http_status')}",
        f"- Started at: {provider_result.get('started_at')}",
    ]
    if "response_excerpt" in provider_result:
        lines.append(f"- Response excerpt: `{provider_result['response_excerpt']}`")
    if "error" in provider_result:
        lines.append(f"- Error: `{provider_result['error']}`")
    lines += [
        "", "## 4. Provider-call count (observed, reset per invocation)", "",
        f"- Total provider calls made by this run: **{call_count}**",
        "- Expected: 0 for every gate-refusal case above, exactly 1 after the genuine acknowledgement.",
        "", "## Claim boundary", "",
        "This receipt evidences that the incident vertical's `approval` control "
        "correctly refuses insufficient-evidence, fabricated, self-approval, "
        "inactive-approver and stale-version acknowledgement attempts before "
        "any provider call, and correctly admits a genuine, distinct-approver "
        "acknowledgement through the real application code path. It does NOT "
        "evidence that any production endpoint calls a provider in production "
        "(none do), and it does not evidence PostgreSQL production readiness.", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
