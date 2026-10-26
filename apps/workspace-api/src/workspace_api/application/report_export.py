"""Read-only bounded export composition after route authorization."""

from threading import BoundedSemaphore

from operations_domain.models import Report
from reporting_engine import ExportFailure, render_bounded
from reporting_engine.model import prepare_report

_render_slot = BoundedSemaphore(1)


def export_report(report: Report, view: str, fmt: str) -> bytes:
    prepare_report(report, view)
    if not _render_slot.acquire(blocking=False):
        raise ExportFailure("EXPORT_BUSY")
    try:
        return render_bounded(report, view, fmt)
    finally:
        _render_slot.release()
