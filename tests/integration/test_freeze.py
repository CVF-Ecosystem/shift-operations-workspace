from datetime import datetime, timedelta, timezone
from workspace_api.domain.models import Shift, Message
from workspace_api.infrastructure.repository import InMemoryLedger

def test_frozen_shift_rejects_new_messages():
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = ledger.create_shift(Shift(name="Night", starts_at=now, ends_at=now+timedelta(hours=12)))
    ledger.freeze_shift(shift.shift_id)
    try:
        ledger.add_message(Message(shift_id=shift.shift_id, sender_id="u1", text="late update"))
    except ValueError:
        return
    raise AssertionError("Frozen shift accepted a new message")
