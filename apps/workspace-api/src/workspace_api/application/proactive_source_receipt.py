"""Closed internal scoped-source receipt emitter and consumer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any
from uuid import UUID

from operations_domain.report_models import ReportSourceRef

from reporting_engine.proactive_models import HistoryInput

P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST = "6fec188950fe752ac438e2952ec3d4e2ffd3b4156efa0b9a2e06e1048c568754"
RECEIPT_VERSION = "P5A2-SOURCE-RECEIPT-1"
COHORT_VERSION = "P5A2-COHORT-ENDS-1"
NUMERIC_VERSION = "P5A2-INITIAL-1"
REASONS = frozenset({
    "ACCESS_DENIED", "INVALID_WINDOW", "TIME_AMBIGUOUS", "COVERAGE_UNKNOWN",
    "SCOPE_INCOMPLETE", "SNAPSHOT_UNAVAILABLE", "INVALID_LINEAGE",
    "INCOMPATIBLE_POLICY", "SOURCE_UNAVAILABLE",
})
READY_FIELDS = frozenset({
    "outcome", "receipt_version", "cohort_policy_version", "numeric_policy_version",
    "scope_id", "actor_id", "query_start", "query_end", "run_as_of", "coverage_mode",
    "eligible_count", "selected_count", "candidate_version_count",
    "max_snapshot_incident_refs", "canonical_manifest", "source_digest",
})
REFUSED_FIELDS = frozenset({"outcome", "receipt_version", "cohort_policy_version",
                             "numeric_policy_version", "reason"})
MANIFEST_FIELDS = frozenset({
    "scope_id", "actor_id", "query_start", "query_end", "run_as_of",
    "cohort_policy_version", "numeric_policy_version", "coverage_fixture_id",
    "coverage_manifest_digest", "eligible_shifts", "candidate_reports", "selected_reports",
})
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?Z\Z")
ELIGIBLE_FIELDS = frozenset({"shift_id", "ends_at", "assignment_id", "assignment_version"})
CANDIDATE_FIELDS = frozenset({"shift_id", "report_id", "version", "generated_from_cutoff",
                              "created_at", "snapshot_digest"})
SELECTED_FIELDS = CANDIDATE_FIELDS | {"source_manifest"}


@dataclass(frozen=True)
class SourceQueryResult:
    receipt: dict[str, Any]
    payload: HistoryInput | None


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=False)


def _time(value: Any) -> datetime:
    if type(value) is not str or not STAMP.fullmatch(value):
        raise ValueError("invalid source timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid source calendar timestamp") from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise ValueError("noncanonical UTC source timestamp")
    return parsed


def _uuid(value: Any) -> None:
    try:
        if type(value) is not str or str(UUID(value)) != value:
            raise ValueError("noncanonical UUID")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid source UUID") from exc


def validate_source_receipt(receipt: dict[str, Any]) -> None:
    """Native closed consumer; reject matrix field/relationship and parsed-manifest drift."""
    if not isinstance(receipt, dict) or type(receipt.get("outcome")) is not str:
        raise ValueError("invalid source receipt")
    if (receipt.get("receipt_version"), receipt.get("cohort_policy_version"),
            receipt.get("numeric_policy_version")) != (RECEIPT_VERSION, COHORT_VERSION, NUMERIC_VERSION):
        raise ValueError("source receipt version mismatch")
    if receipt["outcome"] == "SOURCE_REFUSED":
        if set(receipt) != REFUSED_FIELDS or receipt.get("reason") not in REASONS:
            raise ValueError("invalid refusal receipt")
        return
    if receipt["outcome"] != "SOURCE_READY" or set(receipt) != READY_FIELDS:
        raise ValueError("invalid ready receipt shape")
    if receipt["coverage_mode"] != "SYNTHETIC_FIXTURE":
        raise ValueError("untrusted coverage mode")
    for key in ("scope_id", "actor_id", "query_start", "query_end", "run_as_of"):
        if type(receipt[key]) is not str or not receipt[key]:
            raise ValueError("invalid source receipt header")
    for key, low in (("eligible_count", 1), ("selected_count", 1),
                     ("candidate_version_count", 1), ("max_snapshot_incident_refs", 0)):
        if type(receipt[key]) is not int or not low <= receipt[key] <= 500:
            raise ValueError("invalid source receipt count")
    if receipt["selected_count"] != receipt["eligible_count"] or receipt["candidate_version_count"] < receipt["selected_count"]:
        raise ValueError("source receipt count mismatch")
    raw = receipt["canonical_manifest"]
    if type(raw) is not str or not raw:
        raise ValueError("invalid source manifest")
    try:
        manifest = json.loads(raw)
        if canonical_json(manifest) != raw or set(manifest) != MANIFEST_FIELDS:
            raise ValueError("noncanonical source manifest")
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid source manifest JSON") from exc
    if sha256(raw.encode("utf-8")).hexdigest() != receipt["source_digest"]:
        raise ValueError("source digest mismatch")
    for key in ("scope_id", "actor_id", "query_start", "query_end", "run_as_of",
                "cohort_policy_version", "numeric_policy_version"):
        if manifest[key] != receipt[key]:
            raise ValueError("source manifest header mismatch")
    eligible, candidates, selected = (manifest[key] for key in
                                      ("eligible_shifts", "candidate_reports", "selected_reports"))
    if not all(isinstance(x, list) for x in (eligible, candidates, selected)):
        raise ValueError("source manifest lists invalid")
    if (len(eligible), len(candidates), len(selected)) != (
        receipt["eligible_count"], receipt["candidate_version_count"], receipt["selected_count"]
    ):
        raise ValueError("source manifest count mismatch")
    if (type(manifest["coverage_fixture_id"]) is not str or not manifest["coverage_fixture_id"]
            or type(manifest["coverage_manifest_digest"]) is not str
            or not HEX64.fullmatch(manifest["coverage_manifest_digest"])):
        raise ValueError("invalid coverage manifest identity")
    start, end, as_of = (_time(manifest[k]) for k in ("query_start", "query_end", "run_as_of"))
    if not start < end <= as_of:
        raise ValueError("invalid source window")
    for rows, fields in ((eligible, ELIGIBLE_FIELDS), (candidates, CANDIDATE_FIELDS),
                         (selected, SELECTED_FIELDS)):
        if any(type(item) is not dict or set(item) != fields for item in rows):
            raise ValueError("invalid source manifest item shape")
    for item in eligible:
        _uuid(item["shift_id"])
        _uuid(item["assignment_id"])
        if type(item["assignment_version"]) is not int or item["assignment_version"] < 1:
            raise ValueError("invalid assignment version")
        if not start <= _time(item["ends_at"]) < end:
            raise ValueError("invalid eligible shift time")
    for item in candidates + selected:
        _uuid(item["shift_id"])
        _uuid(item["report_id"])
        if type(item["version"]) is not int or item["version"] < 1:
            raise ValueError("invalid report version")
        if type(item["snapshot_digest"]) is not str or not HEX64.fullmatch(item["snapshot_digest"]):
            raise ValueError("invalid report digest")
        if not _time(item["generated_from_cutoff"]) <= _time(item["created_at"]) <= as_of:
            raise ValueError("invalid report causal time")
    for item in selected:
        if not start <= _time(item["generated_from_cutoff"]) < end:
            raise ValueError("selected report outside source window")
        if type(item["source_manifest"]) is not list:
            raise ValueError("invalid selected lineage")
        for ref in item["source_manifest"]:
            try:
                if type(ref) is not dict or ("source_version" in ref and
                                               ref["source_version"] is not None and
                                               type(ref["source_version"]) is not int):
                    raise ValueError("non-integer lineage source version")
                parsed = ReportSourceRef.model_validate(ref)
            except Exception as exc:
                raise ValueError("invalid selected lineage ref") from exc
            if canonical_json(parsed.model_dump(mode="json")) != canonical_json(ref):
                raise ValueError("noncanonical selected lineage ref")
    ids = [x["shift_id"] for x in eligible]
    if ids != sorted(set(ids)) or any(x["shift_id"] not in ids for x in candidates):
        raise ValueError("source manifest cohort mismatch")
    ordered = [(x["shift_id"], x["version"], x["report_id"]) for x in candidates]
    if ordered != sorted(ordered) or len(set(ordered)) != len(ordered):
        raise ValueError("candidate ordering mismatch")
    selected_order = [(x["generated_from_cutoff"], x["shift_id"]) for x in selected]
    if selected_order != sorted(selected_order) or {x["shift_id"] for x in selected} != set(ids):
        raise ValueError("selected ordering or coverage mismatch")
    candidate_keys = {tuple(x[k] for k in sorted(CANDIDATE_FIELDS)) for x in candidates}
    if any(tuple(x[k] for k in sorted(CANDIDATE_FIELDS)) not in candidate_keys for x in selected):
        raise ValueError("selected report not in candidate manifest")


def emit_source_ready(manifest: dict, eligible_count: int, candidate_count: int,
                      max_refs: int) -> dict[str, Any]:
    raw = canonical_json(manifest)
    receipt = {
        "receipt_version": RECEIPT_VERSION, "cohort_policy_version": COHORT_VERSION,
        "numeric_policy_version": NUMERIC_VERSION, "outcome": "SOURCE_READY",
        "scope_id": manifest["scope_id"], "actor_id": manifest["actor_id"],
        "query_start": manifest["query_start"], "query_end": manifest["query_end"],
        "run_as_of": manifest["run_as_of"], "coverage_mode": "SYNTHETIC_FIXTURE",
        "eligible_count": eligible_count, "selected_count": len(manifest["selected_reports"]),
        "candidate_version_count": candidate_count, "max_snapshot_incident_refs": max_refs,
        "canonical_manifest": raw, "source_digest": sha256(raw.encode("utf-8")).hexdigest(),
    }
    validate_source_receipt(receipt)
    return receipt


def emit_source_refused(reason: str) -> dict[str, Any]:
    receipt = {
        "receipt_version": RECEIPT_VERSION, "cohort_policy_version": COHORT_VERSION,
        "numeric_policy_version": NUMERIC_VERSION, "outcome": "SOURCE_REFUSED",
        "reason": reason,
    }
    validate_source_receipt(receipt)
    return receipt
