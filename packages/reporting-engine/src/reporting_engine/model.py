"""Validate persisted truth before passing it to a renderer."""

from operations_domain.models import Report
from operations_domain.report_digest import aggregate_digest, canonical_bytes

VIEWS = {
    "shift-summary": None,
    "customer-report": "customer_requests",
    "incident-report": "incidents",
    "handover-report": "handovers",
}
TEMPLATE_VERSION = "p5a-1"


class ExportFailure(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def prepare_report(report: Report, view: str) -> Report:
    if view not in VIEWS:
        raise ExportFailure("EXPORT_INVALID_PARAMETER")
    try:
        clean = Report.model_validate(report.model_dump(mode="json"))
        if len(canonical_bytes(clean.content.model_dump(mode="json"))) > 2_097_152:
            raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
        if any(len(section.records) > 500 for section in clean.content.sections):
            raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
        actual = aggregate_digest(clean.shift_id, clean.report_type, clean.content)
        if actual != clean.content.snapshot_digest:
            raise ExportFailure("EXPORT_INVALID_SNAPSHOT")
        return clean
    except ExportFailure:
        raise
    except (TypeError, ValueError) as exc:
        raise ExportFailure("EXPORT_INVALID_SNAPSHOT") from exc
