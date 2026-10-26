"""Export text and output limits."""

import io
from importlib import resources

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .model import ExportFailure

MAX_BYTES = 8 * 1024 * 1024
FONT_PATH = resources.files("reporting_engine").joinpath("assets", "DejaVuSans.ttf")


def validate_text(value: str, *, pdf: bool) -> None:
    if any((ord(ch) < 32 and ch not in "\n\t\r") or
           0xD800 <= ord(ch) <= 0xDFFF or ord(ch) in {0xFFFE, 0xFFFF}
           for ch in value):
        raise ExportFailure("EXPORT_UNSUPPORTED_TEXT")
    if not pdf and len(value.encode("utf-16-le")) // 2 > 32_767:
        raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
    if pdf:
        if not FONT_PATH.is_file():
            raise ExportFailure("EXPORT_UNSUPPORTED_TEXT")
        if "P5A-DejaVu" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("P5A-DejaVu", io.BytesIO(FONT_PATH.read_bytes())))
        face = pdfmetrics.getFont("P5A-DejaVu").face
        if any(ord(ch) not in face.charToGlyph for ch in value if ch not in "\n\t\r"):
            raise ExportFailure("EXPORT_UNSUPPORTED_TEXT")
