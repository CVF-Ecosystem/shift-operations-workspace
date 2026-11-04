"""Authenticated, assigned, read-only source receipt inspection."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from workspace_api.application.proactive_source_access import (
    AccessFailure, SourceAccess, check_access, server_scope,
)
from workspace_api.application.proactive_source_preview import (
    SourcePreview, fresh_release, preview_source,
)
from workspace_api.application.proactive_source_receipt import emit_source_refused
from workspace_api.config import settings
from workspace_api.dependencies import (
    get_ledger, get_proactive_identity, get_proactive_source_clock,
    get_proactive_source_coverage,
)

from .response import (
    ReadyReceipt, RefusedReceipt, error_response, prepare_receipt, receipt_response,
)

router = APIRouter(prefix="/proactive", tags=["proactive"])
KEYS = {"query_start", "query_end", "run_as_of"}
QUERY_DOCUMENTATION = [
    {"name": name, "in": "query", "required": True,
     "schema": {"type": "string", "format": "date-time", "maxLength": 128}}
    for name in ("query_start", "query_end", "run_as_of")
]


def _parse_time(value: str) -> datetime:
    if len(value) > 128 or "T" not in value:
        raise ValueError("invalid timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    return parsed


async def _request_window(request: Request) -> tuple[datetime, datetime, datetime] | None:
    if len(request.scope.get("query_string", b"")) > 2048:
        raise ValueError("query too long")
    items = request.query_params.multi_items()
    if len(items) != 3 or {key for key, _ in items} != KEYS:
        raise ValueError("query keys")
    async for chunk in request.stream():
        if chunk:
            raise ValueError("request body")
    values = dict(items)
    parsed = tuple(_parse_time(values[key]) for key in
                   ("query_start", "query_end", "run_as_of"))
    return parsed


@router.get(
    "/source", response_model=ReadyReceipt | RefusedReceipt,
    openapi_extra={"parameters": QUERY_DOCUMENTATION},
    responses={401: {"description": "Authentication required"},
               403: {"description": "Access denied"},
               422: {"description": "Invalid request"}},
)
async def read_source(
    request: Request,
    identity=Depends(get_proactive_identity),
    ledger=Depends(get_ledger),
    coverage=Depends(get_proactive_source_coverage),
    clock=Depends(get_proactive_source_clock),
):
    principal, expires_at = identity
    access = SourceAccess(principal, expires_at, ledger,
                          settings.proactive_source_instance_id, clock)
    try:
        now = check_access(access)
    except AccessFailure as exc:
        return error_response(exc.status)
    try:
        start, end, as_of = await _request_window(request)
    except (ValueError, UnicodeError):
        return error_response(422)
    if any(value.tzinfo is None or value.utcoffset() is None
           for value in (start, end, as_of)):
        preview = SourcePreview(emit_source_refused("TIME_AMBIGUOUS"), None)
    else:
        start, end, as_of = (value.astimezone(timezone.utc)
                             for value in (start, end, as_of))
        if not start < end <= as_of <= now:
            preview = SourcePreview(emit_source_refused("INVALID_WINDOW"), None)
        else:
            scope = server_scope(access)
            preview = (preview_source(principal, scope, start, end, as_of, ledger, coverage)
                       if scope is not None else
                       SourcePreview(emit_source_refused("SOURCE_UNAVAILABLE"), None))
    receipt, encoded = prepare_receipt(preview.receipt)
    if preview.cohort is not None:
        current = fresh_release(preview, principal, start, end, ledger)
        if current != preview.receipt:
            receipt, encoded = prepare_receipt(current)
    try:
        check_access(access)
    except AccessFailure as exc:
        return error_response(exc.status)
    return receipt_response(encoded)
