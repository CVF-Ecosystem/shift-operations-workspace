"""Pure P5-A2 input and result types; no ledger or scheduler binding."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any
from uuid import UUID

from operations_domain.report_digest import canonical_bytes

POLICY_VERSION = "P5A2-INITIAL-1"


class ProactiveRefusal(ValueError):
    def __init__(self, reason: str, **diagnostics: int):
        super().__init__(reason)
        self.reason = reason
        self.diagnostics = diagnostics


def aware_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProactiveRefusal("TIME_AMBIGUOUS")
    return value.astimezone(timezone.utc)


def stamp(value: datetime) -> str:
    return aware_utc(value).isoformat().replace("+00:00", "Z")


def digest(payload: object) -> str:
    # Reject nonfinite JSON and use the domain snapshot's canonical encoding.
    try:
        json.dumps(payload, allow_nan=False)
        return sha256(canonical_bytes(payload)).hexdigest()
    except (TypeError, ValueError) as exc:
        raise ProactiveRefusal("INPUT_INVALID") from exc


@dataclass(frozen=True)
class Observation:
    shift_id: UUID
    report_id: UUID
    version: int
    cutoff: datetime
    created_at: datetime
    snapshot_digest: str
    source_manifest: tuple[dict[str, Any], ...]
    count: int

    @property
    def order(self) -> tuple[datetime, str]:
        return self.cutoff, str(self.shift_id)

    def lineage_item(self) -> dict[str, Any]:
        return {
            "shift_id": str(self.shift_id), "report_id": str(self.report_id),
            "version": self.version, "generated_from_cutoff": stamp(self.cutoff),
            "created_at": stamp(self.created_at), "snapshot_digest": self.snapshot_digest,
            "source_manifest": list(self.source_manifest),
        }


@dataclass(frozen=True)
class HistoryInput:
    scope_id: str
    actor_id: str
    query_start: datetime
    query_end: datetime
    run_as_of: datetime
    eligible_shift_ids: tuple[UUID, ...]
    candidates: tuple[Any, ...]  # Canonical operations_domain.Report objects.
    complete: bool
    retention_complete: bool


def result_abstained(reason: str, *, lineage_digest: str | None = None,
                     observations: int = 0, diagnostics: dict[str, int] | None = None,
                     history_context: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {"outcome": "ABSTAINED", "reason": reason,
              "source_selected": lineage_digest is not None,
              "observation_count": observations, "policy_version": POLICY_VERSION}
    if lineage_digest is not None:
        result["lineage_digest"] = lineage_digest
    if diagnostics:
        result["diagnostics"] = diagnostics
    if history_context is not None:
        result["history_context"] = history_context
    return result
