from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    model_validator,
)

_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def safe_identifier(value: str) -> str:
    if value != value.strip() or _CONTROL.search(value):
        raise ValueError("unsafe identifier")
    return value


SafeId = Annotated[
    str,
    Field(min_length=1, max_length=128),
    AfterValidator(safe_identifier),
]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


def utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError("UTC datetime required")
    return value.astimezone(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def require_nfc(value: str) -> str:
    if unicodedata.normalize("NFC", value) != value:
        raise ValueError("NFC string required")
    return value


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def reject_non_nfc_strings(cls, value):
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

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_utc(self, value):
        if isinstance(value, datetime):
            return utc_text(value)
        return value


class SafeIdentifierModel(StrictModel):
    """Compatibility base; identifier safety is carried by every SafeId field."""
