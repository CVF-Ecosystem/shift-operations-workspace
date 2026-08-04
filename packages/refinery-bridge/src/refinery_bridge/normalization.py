from __future__ import annotations

import re
import unicodedata


HORIZONTAL_SPACE = re.compile(r"[^\S\r\n]+")
TRAILING_SPACE = re.compile(r"[ \t]+(?=\n|$)")


def normalize_syntax(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = HORIZONTAL_SPACE.sub(" ", normalized)
    normalized = TRAILING_SPACE.sub("", normalized)
    return normalized.strip()
