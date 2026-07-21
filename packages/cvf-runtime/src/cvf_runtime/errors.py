"""Refusal primitives shared by every CVF gate.

CVF control: ``refusal``. A denied request must fail with a machine-readable
reason and a stable control name so audit and the API layer can classify it,
rather than leaking a bare string or a generic 500.
"""

from __future__ import annotations


class CvfDenied(Exception):
    """Raised when a CVF gate refuses an action.

    ``control`` is the CVF control that refused (e.g. ``permission``,
    ``approval``, ``evidence``). ``http_status`` lets the API layer map the
    refusal to the correct response without re-deriving intent.
    """

    def __init__(self, control: str, reason: str, http_status: int = 403) -> None:
        self.control = control
        self.reason = reason
        self.http_status = http_status
        super().__init__(f"[{control}] {reason}")
