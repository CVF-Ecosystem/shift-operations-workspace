# connection-health

Accessible connectivity truth for the Operations Console. The runtime reports
authenticated foreground `polling sync`, last successful refresh, offline,
stale/error, pending, blocked, outcome-unknown and known-applied/stale queue
states. It does not claim WebSocket/SSE push, exactly-once delivery or a fully
offline data replica. Backend identity, assignment, permission and CAS remain
authoritative on every replay.
