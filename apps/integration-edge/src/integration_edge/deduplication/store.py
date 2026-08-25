"""Compatibility wrapper over the atomic edge reservation store."""

class DedupeStore:
    def __init__(self, edge_store=None): self.edge_store=edge_store; self._seen=set()
    def first_seen(self,key:str)->bool:
        if key in self._seen:return False
        self._seen.add(key);return True

store=DedupeStore()
