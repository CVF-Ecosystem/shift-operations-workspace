"""Support module for run_message_admission_live_governance_evidence.py.

MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30 (SPEC R16-R18): owns everything
that touches provider HTTP, sanitization, safe endpoint description,
provider-call accounting and receipt rendering, mirroring the shift-create
vertical's proven design (_shift_create_live_evidence_support.py) but
deliberately self-contained rather than cross-imported, per this repo's
established convention. Nothing here ever returns, prints, or writes the
exact configured provider key, a bearer/JWT value, or a URL's userinfo/query/
fragment - every provider-derived string is sanitized before it leaves
:func:`call_provider`.
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
    """A fresh instance per runner invocation (SPEC R16 parity) - never a
    module global, so accounting cannot leak or persist across calls/tests."""

    def __init__(self) -> None:
        self.count = 0

    def record(self) -> None:
        self.count += 1


def sanitize_secret_text(text: str | None, *, api_key: str | None = None) -> str:
    if not text:
        return text or ""
    if api_key:
        text = text.replace(api_key, "<redacted-key>")
    text = _BEARER_RE.sub("Bearer <redacted>", text)
    text = _JWT_RE.sub("<redacted-jwt>", text)
    return text


def safe_endpoint_description(endpoint: str) -> str:
    """Scheme + hostname only - no userinfo, port, path, query or fragment.

    MAR-BUILD-REV-F2 (third branch): this used to call urlsplit/`.hostname`
    with no failure boundary of its own, and `main()` called it BEFORE
    `call_provider` - so a malformed IPv6 (or any other urlsplit/hostname
    ValueError) raised here propagated raw out of `main()` entirely, never
    reaching call_provider's sanitized boundary at all. Must fail closed:
    never raise, never return anything derived from the unparsed endpoint."""
    try:
        parts = urlsplit(endpoint)
        hostname = parts.hostname or "<unknown-host>"
        return f"{parts.scheme}://{hostname}"
    except ValueError:
        return "<unparseable-endpoint>"


class _EndpointParseError(Exception):
    """Raised only with an already-sanitized message - never wraps the
    original urlsplit/port ValueError, whose text embeds the raw offending
    fragment (e.g. a non-numeric port smuggling a secret, MAR-BUILD-REV-F2)."""


def _clean_endpoint(endpoint: str) -> tuple[str, list[str]]:
    """Split ``endpoint`` into (url-safe-for-request, [secret fragments]) -
    the ONLY form ever handed to Request/urlopen, so a later construction or
    transport exception can never embed credential material smuggled into
    the endpoint's userinfo/query/fragment (mirrors INC-REV-F6).

    MAR-BUILD-REV-F2: ``parts.port`` itself raises ``ValueError`` for a
    non-numeric port (e.g. ``:PORT_SECRET_xxx``), and that exception's
    message embeds the raw offending text verbatim - a secret smuggled into
    the port position would otherwise leak through the generic exception
    handler in :func:`call_provider`, which has no ``endpoint_secrets`` yet
    to redact with. The raw netloc (which may itself contain the secret) is
    captured as a secret fragment BEFORE the port is ever accessed, and any
    port-access failure is re-raised as a sanitized, secret-free error."""
    parts = urlsplit(endpoint)
    secrets = [v for v in (parts.username, parts.password, parts.query, parts.fragment) if v]
    if parts.netloc:
        secrets.append(parts.netloc)
    try:
        port = parts.port
    except ValueError as exc:
        raise _EndpointParseError("endpoint port could not be parsed") from exc
    netloc = parts.hostname or ""
    if port:
        netloc = f"{netloc}:{port}"
    clean = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    return clean, secrets


def call_provider(
    *, model: str, api_key: str, endpoint: str, prompt: str, expected_token: str,
    counter: ProviderCallCounter,
) -> dict:
    """One real, non-mocked provider call. Every field of the returned dict
    is already sanitized - callers never need to scrub it again.

    MAR-BUILD-REV-F2 repair (SPEC R22): endpoint parsing/cleaning, request
    construction and transport now share ONE sanitized failure boundary.
    Previously `_clean_endpoint(endpoint)` ran BEFORE this try/except, so an
    invalid port, malformed IPv6, or other urlsplit-time ValueError
    propagated raw out of this function - bypassing every sanitizer below
    and any caller's own error handling. A generic `_sanitize` (only the
    literal api_key, no endpoint-secret substitutions - the endpoint itself
    may not have parsed yet) now also covers that construction phase."""
    counter.record()
    started = datetime.now(timezone.utc)

    def _sanitize(text: str, *, endpoint_secrets: list[str] | None = None) -> str:
        text = sanitize_secret_text(text, api_key=api_key)
        for secret in endpoint_secrets or ():
            text = text.replace(secret, "<redacted-endpoint-credential>")
        return text

    try:
        clean_endpoint, endpoint_secrets = _clean_endpoint(endpoint)

        def _sanitize_with_endpoint(text: str) -> str:
            return _sanitize(text, endpoint_secrets=endpoint_secrets)

        body = json.dumps(
            {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 32}
        ).encode("utf-8")
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
            "error": _sanitize_with_endpoint(error_body),
            "started_at": started.isoformat(),
        }
    except Exception as exc:  # noqa: BLE001 - endpoint parsing, construction, or transport
        # failure, sanitized alike. endpoint_secrets may not exist yet (a
        # parsing failure in _clean_endpoint itself), so only the literal
        # api_key/bearer/JWT patterns are guaranteed removable here.
        return {
            "outcome": "FAIL", "reached_server": False, "http_status": None,
            "error": _sanitize(f"{type(exc).__name__}: {exc}"),
            "started_at": started.isoformat(),
        }

    content = _sanitize_with_endpoint(payload.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return {
        "outcome": "PASS" if expected_token in content else "FAIL",
        "reached_server": True, "http_status": status,
        "response_excerpt": content.strip()[:200],
        "started_at": started.isoformat(),
    }


def render_receipt(
    path: Path, *, gate_results: list[dict], admitted_detail: str, provider_result: dict,
    model: str, safe_endpoint: str, call_count: int,
) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# Message admission trust repair - live governance evidence receipt", "",
        f"Overall outcome: {overall}", "",
        "Produced by `scripts/run_message_admission_live_governance_evidence.py` "
        "via `scripts/_message_admission_live_evidence_support.py` "
        "(MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC R16-R18). Sanitized: "
        "contains no API key, no Authorization header, no JWT, no raw secret, "
        "no URL userinfo/query/fragment.", "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}", f"- Endpoint (host only): {safe_endpoint}", "",
        "## 1. Refusal cases (real HTTP route chain, observed provider-call delta)", "",
        "| Case | Outcome | Detail | Provider calls |", "|---|---|---|---|",
    ]
    for r in gate_results:
        lines.append(f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |")
    lines += [
        "", "## 2. Genuine admitted create (real HTTP route chain)", "",
        f"- {admitted_detail}", "", "## 3. Real provider call", "",
        "Reached only because the create above genuinely admitted a valid "
        "operator JWT and persisted the message plus its actor-bound audit.", "",
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
        "- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted create.",
        "", "## Claim boundary", "",
        "This receipt evidences that internal POST /messages's real "
        "identity/permission/provenance gate correctly refuses anonymous, "
        "malformed-token, insufficient-role, sender-mismatch, "
        "non-internal-source, unknown-shift and frozen-shift create attempts "
        "before any provider call, and correctly admits a genuine "
        "valid-operator-JWT create through the real HTTP route chain, "
        "persisting exactly one message and one actor-bound audit record. "
        "It does NOT evidence external/channel message ingestion, the "
        "Canonical Message Contract, or PostgreSQL production readiness.", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
