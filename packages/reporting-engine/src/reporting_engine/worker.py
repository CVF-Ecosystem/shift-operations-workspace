"""Killable renderer process with a fixed-size shared output buffer."""

import multiprocessing as mp
import time

from operations_domain.models import Report

from .limits import MAX_BYTES
from .model import ExportFailure, prepare_report

DEADLINE_SECONDS = 10
_ERROR_CODES = {
    1: "EXPORT_INVALID_SNAPSHOT",
    2: "EXPORT_UNSUPPORTED_TEXT",
    3: "EXPORT_LIMIT_EXCEEDED",
    4: "EXPORT_INVALID_PARAMETER",
}


def _render_child(shared, size, status, primitive: dict, view: str, fmt: str) -> None:
    try:
        from .pdf import render_pdf
        from .views import selected_rows
        from .xlsx import render_xlsx

        report = prepare_report(Report.model_validate(primitive), view)
        metadata, rows = selected_rows(report, view)
        data = render_pdf(metadata, rows) if fmt == "pdf" else render_xlsx(metadata, rows)
        if len(data) > MAX_BYTES:
            raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
        shared[:len(data)] = data
        size.value = len(data)
        status.value = 1
    except ExportFailure as exc:
        status.value = next((key + 1 for key, code in _ERROR_CODES.items()
                             if code == exc.code), 0)


def _run_isolated(target, args: tuple, deadline: float) -> bytes:
    """Return bytes only after full child exit; discard any partially written buffer."""
    ctx = mp.get_context("spawn")
    shared = ctx.RawArray("B", MAX_BYTES)
    size = ctx.RawValue("i", 0)
    status = ctx.RawValue("i", 0)
    child = ctx.Process(target=target, args=(shared, size, status, *args))
    start = time.monotonic()
    try:
        child.start()
        child.join(timeout=max(0, deadline - (time.monotonic() - start)))
        if child.is_alive():
            child.terminate()
            child.join(timeout=1)
            if child.is_alive():
                child.kill()
                child.join(timeout=1)
            raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
        if child.exitcode != 0:
            raise ExportFailure("EXPORT_FAILED")
        if status.value != 1:
            raise ExportFailure(_ERROR_CODES.get(status.value - 1, "EXPORT_FAILED"))
        if not 0 < size.value <= MAX_BYTES:
            raise ExportFailure("EXPORT_FAILED")
        return bytes(shared[:size.value])
    finally:
        if child.is_alive():
            child.kill()
            child.join(timeout=1)
        child.close()


def render_bounded(report: Report, view: str, fmt: str) -> bytes:
    if fmt not in {"pdf", "xlsx"} or view not in {
        "shift-summary", "customer-report", "incident-report", "handover-report"
    }:
        raise ExportFailure("EXPORT_INVALID_PARAMETER")
    clean = prepare_report(report, view)
    return _run_isolated(_render_child, (clean.model_dump(mode="json"), view, fmt), DEADLINE_SECONDS)
