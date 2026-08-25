from __future__ import annotations

ALLOWED_REASONS = frozenset({"MALFORMED_SCHEMA","UNSUPPORTED_TYPE","AMBIGUOUS_CONTENT","UNSAFE_ATTACHMENT","SCAN_UNAVAILABLE","POLICY_DRIFT","ROUTE_POLICY_REFUSED","KEY_COLLISION"})


class QuarantineService:
    def __init__(self, store, *, release_recheck=None) -> None:
        self.store, self.release_recheck = store, release_recheck

    def quarantine(self, envelope_id: str, reason: str, *, original_envelope_id: str | None = None):
        if reason not in ALLOWED_REASONS:
            raise ValueError("closed quarantine reason required")
        return self.store.quarantine(envelope_id, reason, original_envelope_id=original_envelope_id)

    def release(self, quarantine_id: str) -> None:
        if self.release_recheck is None or not self.release_recheck(quarantine_id):
            raise PermissionError("quarantine release recheck refused")
