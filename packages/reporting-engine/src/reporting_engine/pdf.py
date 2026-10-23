"""Unicode PDF presentation with explicit page and byte limits."""

import io
import unicodedata

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from .limits import MAX_BYTES, validate_text
from .model import ExportFailure

MAX_PAGES = 512
FONT = "P5A-DejaVu"


def _lines(text: str, width: float, size: float):
    line = ""
    for char in text:
        if char == "\n":
            yield line
            line = ""
        elif pdfmetrics.stringWidth(line + char, FONT, size) > width and line:
            yield line
            line = char
        else:
            line += char
    yield line


def render_pdf(metadata: list[tuple[str, str]], rows: list[tuple[str, str]]) -> bytes:
    for key, value in metadata + rows:
        validate_text(key, pdf=True)
        validate_text(value, pdf=True)
    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4, pageCompression=1)
    width, height = A4
    page = 1
    y = height - 42
    current_section = None
    current_record = None

    def header() -> None:
        nonlocal y
        pdf.setFont(FONT, 10)
        pdf.drawString(40, height - 30, "End-shift report — " + dict(metadata)["view"])
        pdf.drawRightString(width - 40, height - 30, f"Page {page}")
        pdf.line(40, height - 34, width - 40, height - 34)
        y = height - 48

    header()
    for key, value in metadata + [("Content", "Persisted snapshot view")] + rows:
        if key == "Section":
            current_section, current_record = value, None
        elif key == "Record":
            current_record = value
        elif key == "Source":
            current_section, current_record = "source_manifest", None
        if key in {"Section", "Record", "Content"}:
            y -= 5
        display = unicodedata.normalize("NFC", f"{key}: {value}")
        display = display.replace("\t", "\\t").replace("\r", "\\r")
        font_size = 10 if key in {"Section", "Record", "Content"} else 9
        for line in _lines(display, width - 80, font_size):
            if y < 40:
                if page >= MAX_PAGES:
                    raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
                pdf.showPage()
                page += 1
                header()
                if current_section:
                    pdf.setFont(FONT, 9)
                    pdf.drawString(40, y, f"Continued section: {current_section}")
                    y -= 12
                if current_record:
                    pdf.setFont(FONT, 9)
                    pdf.drawString(40, y, f"Continued record: {current_record}")
                    y -= 15
            pdf.setFont(FONT, font_size)
            pdf.drawString(40, y, line)
            y -= 14 if key in {"Section", "Record", "Content"} else 12
    pdf.save()
    data = output.getvalue()
    if len(data) > MAX_BYTES:
        raise ExportFailure("EXPORT_LIMIT_EXCEEDED")
    return data
