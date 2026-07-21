from threading import RLock
class DedupeStore:
    def __init__(self):
        self._seen: set[str] = set()
        self._lock = RLock()
    def first_seen(self, key: str) -> bool:
        with self._lock:
            if key in self._seen: return False
            self._seen.add(key); return True
store = DedupeStore()
