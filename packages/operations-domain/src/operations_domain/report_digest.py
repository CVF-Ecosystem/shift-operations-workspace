"""Canonical P2-R aggregate digest, shared with presentation validation."""

import hashlib
import json
from uuid import UUID

from .report_models import ReportContent


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def aggregate_digest(shift_id: UUID, report_type: str, content: ReportContent) -> str:
    payload = {
        "schema_version": content.schema_version,
        "shift_id": str(shift_id),
        "report_type": str(report_type),
        "sections": [s.model_dump(mode="json") for s in content.sections],
        "source_manifest": [m.model_dump(mode="json") for m in content.source_manifest],
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()
