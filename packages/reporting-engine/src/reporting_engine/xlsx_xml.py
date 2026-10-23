"""Preserve XML carriage returns in literal XLSX inline text cells."""

import io
import re
from zipfile import ZipFile

_INLINE_TEXT = re.compile(rb"(<t(?:\s[^>]*)?>)(.*?)(</t>)", re.DOTALL)


def preserve_carriage_returns(data: bytes) -> bytes:
    """XML normalizes raw CR to LF; character references retain exact text."""
    output = io.BytesIO()
    with ZipFile(io.BytesIO(data)) as source, ZipFile(output, "w") as target:
        for info in source.infolist():
            payload = source.read(info.filename)
            if info.filename.startswith("xl/worksheets/") and info.filename.endswith(".xml"):
                payload = _INLINE_TEXT.sub(
                    lambda match: match[1] + match[2].replace(b"\r", b"&#13;") + match[3],
                    payload,
                )
            target.writestr(info, payload)
    return output.getvalue()
