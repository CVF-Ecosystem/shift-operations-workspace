from __future__ import annotations

from datetime import datetime, timezone

from refinery_bridge.canonical import source_fingerprint
from refinery_bridge.controls import ControlBundleV1, RedactionRuleV1
from refinery_bridge.enums import Sensitivity, SourceType
from refinery_bridge.input_models import DedupeContextV1, QuarantineRouteV1

NOW = datetime(2026, 7, 21, 23, 41, tzinfo=timezone.utc)


def controls() -> ControlBundleV1:
    return ControlBundleV1(
        envelope_schema_version="envelope-v1",
        normalization_rules_version="normalization-v1",
        terminology_rules_version="terminology-v1",
        classification_rules_version="classification-v1",
        conflict_rules_version="conflict-v1",
        redaction_rules_version="redaction-v1",
        dedupe_rules_version="dedupe-v1",
        quality_rules_version="quality-v1",
        candidate_admission_rules_version="admission-v1",
        terminology_map={"qc3": "QC03", "tech": "technical"},
        sensitivity_terms={
            Sensitivity.CONFIDENTIAL: ("confidential",),
            Sensitivity.RESTRICTED: ("restricted",),
        },
        topic_terms={"equipment_downtime": ("stopped", "stop", "dừng")},
        redaction_rules=(
            RedactionRuleV1(
                rule_id="credential-rule",
                kind="credential",
                pattern=r"(?i)password\s*[:=]\s*\S+",
            ),
        ),
        current_quarantine_policy_version="quarantine-v1",
    )


def payload(
    text: str = "QC03 stopped at 2026-07-21T23:40:00Z due to sensor fault.",
    *,
    source_id: str = "msg-001",
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "source_id": source_id,
        "source_version": "v1",
        "source_link": f"fixture:{source_id}",
        "source_type": SourceType.EXTERNAL_UNTRUSTED_FIXTURE,
        "raw_text": text,
        "received_at": NOW,
        "declared_sensitivity": sensitivity,
        "source_owner_id": "fixture-owner",
        "source_fingerprint": source_fingerprint(text).model_dump(),
    }


def empty_context(scope_id: str = "scope-1") -> DedupeContextV1:
    return DedupeContextV1(
        scope_id=scope_id,
        window_start=datetime(2026, 7, 21, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2026, 7, 22, 0, 0, tzinfo=timezone.utc),
        records=(),
    )


def route(*, available: bool = True) -> QuarantineRouteV1:
    return QuarantineRouteV1(
        owner_id="quarantine-owner",
        sink_id="quarantine-sink",
        policy_version="quarantine-v1",
        retention_days=30,
        sink_available=available,
    )


MATRIX_CASES = (
    "non-mapping", "missing-field", "extra-field", "unpaired-surrogate",
    "unsafe-link", "malformed-fingerprint", "fingerprint-mismatch",
    "control-version-substitution", "ready", "nfc-idempotence", "qualified-time",
    "ambiguous-time", "ambiguous-action", "terminology", "terminology-overlap",
    "sensitivity-retention", "sensitivity-escalation", "policy-drift", "redaction",
    "redaction-overlap", "redaction-residue", "conflict", "source-duplicate",
    "content-match", "collision", "invalid-context", "unavailable-route", "invariant",
)
