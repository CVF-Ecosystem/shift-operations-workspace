"""Shared strict-model base for the governed-retrieval pure package (P4-A1).

CVF control: ``governed-retrieval.model_base``. Every V1 model in this package
rejects unknown fields and forbids float values so canonical hashing (R9) is
byte-deterministic. This module performs no I/O, clock/id creation, or any
access beyond the standard library and Pydantic.
"""

from __future__ import annotations

import unicodedata

from pydantic import BaseModel, ConfigDict, model_validator


def require_nfc(value: str) -> str:
    if unicodedata.normalize("NFC", value) != value:
        raise ValueError("NFC string required")
    return value


class StrictModel(BaseModel):
    """Closed-schema base: unknown fields rejected, immutable, non-float."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def _reject_non_nfc_strings(cls, value):
        def walk(item):
            if isinstance(item, str):
                require_nfc(item)
            elif isinstance(item, dict):
                for key, nested in item.items():
                    require_nfc(key)
                    walk(nested)
            elif isinstance(item, (list, tuple)):
                for nested in item:
                    walk(nested)

        if isinstance(value, dict):
            walk(value)
        return value

    @model_validator(mode="before")
    @classmethod
    def _reject_floats(cls, value):
        def walk(item):
            if isinstance(item, float):
                raise ValueError("float forbidden in governed-retrieval models")
            if isinstance(item, dict):
                for nested in item.values():
                    walk(nested)
            elif isinstance(item, (list, tuple)):
                for nested in item:
                    walk(nested)

        if isinstance(value, dict):
            walk(value)
        return value
