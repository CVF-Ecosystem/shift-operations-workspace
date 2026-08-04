from __future__ import annotations

import re
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from .enums import Sensitivity, Stage
from .input_models import SafeId, StrictModel, validate_safe_string


class RedactionRuleV1(StrictModel):
    rule_id: SafeId
    kind: SafeId
    pattern: Annotated[str, Field(min_length=1, max_length=512)]

    @field_validator("rule_id", "kind")
    @classmethod
    def safe_ids(cls, value: str) -> str:
        return validate_safe_string(value)

    @field_validator("pattern")
    @classmethod
    def valid_pattern(cls, value: str) -> str:
        re.compile(value)
        return value


class ControlBundleV1(StrictModel):
    envelope_schema_version: SafeId
    normalization_rules_version: SafeId
    terminology_rules_version: SafeId
    classification_rules_version: SafeId
    conflict_rules_version: SafeId
    redaction_rules_version: SafeId
    dedupe_rules_version: SafeId
    quality_rules_version: SafeId
    candidate_admission_rules_version: SafeId
    terminology_map: dict[str, str] = Field(default_factory=dict)
    sensitivity_terms: dict[Sensitivity, tuple[str, ...]] = Field(default_factory=dict)
    topic_terms: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    redaction_rules: tuple[RedactionRuleV1, ...] = ()
    current_quarantine_policy_version: SafeId = "quarantine-v1"

    @field_validator(
        "envelope_schema_version",
        "normalization_rules_version",
        "terminology_rules_version",
        "classification_rules_version",
        "conflict_rules_version",
        "redaction_rules_version",
        "dedupe_rules_version",
        "quality_rules_version",
        "candidate_admission_rules_version",
        "current_quarantine_policy_version",
    )
    @classmethod
    def safe_versions(cls, value: str) -> str:
        return validate_safe_string(value)

    @model_validator(mode="after")
    def deterministic_maps(self) -> "ControlBundleV1":
        versions = (
            self.envelope_schema_version,
            self.normalization_rules_version,
            self.terminology_rules_version,
            self.classification_rules_version,
            self.conflict_rules_version,
            self.redaction_rules_version,
            self.dedupe_rules_version,
            self.quality_rules_version,
            self.candidate_admission_rules_version,
        )
        if len(set(versions)) != len(versions):
            raise ValueError("stage control versions must be distinct")
        folded: set[str] = set()
        targets = {value.casefold() for value in self.terminology_map.values()}
        for key, value in self.terminology_map.items():
            if not key or not value or len(key) > 128 or len(value) > 128:
                raise ValueError("invalid terminology entry")
            validate_safe_string(key)
            validate_safe_string(value)
            canonical = key.casefold()
            if canonical in folded or canonical in targets:
                raise ValueError("overlapping or cyclic terminology")
            folded.add(canonical)
        if len(self.topic_terms) > 64:
            raise ValueError("too many topics")
        for topic, terms in self.topic_terms.items():
            validate_safe_string(topic)
            self._validate_terms(terms)
        for terms in self.sensitivity_terms.values():
            self._validate_terms(terms)
        return self

    @staticmethod
    def _validate_terms(terms: tuple[str, ...]) -> None:
        if len(set(terms)) != len(terms):
            raise ValueError("duplicate control term")
        for term in terms:
            if not term or len(term) > 128:
                raise ValueError("invalid control term")
            validate_safe_string(term)

    def version_for(self, stage: Stage) -> str:
        mapping = {
            Stage.ENVELOPE: self.envelope_schema_version,
            Stage.NORMALIZATION: self.normalization_rules_version,
            Stage.TERMINOLOGY: self.terminology_rules_version,
            Stage.CLASSIFICATION: self.classification_rules_version,
            Stage.CONFLICT: self.conflict_rules_version,
            Stage.REDACTION: self.redaction_rules_version,
            Stage.DEDUPE: self.dedupe_rules_version,
            Stage.QUALITY: self.quality_rules_version,
            Stage.CANDIDATE_ADMISSION: self.candidate_admission_rules_version,
        }
        return mapping[stage]
