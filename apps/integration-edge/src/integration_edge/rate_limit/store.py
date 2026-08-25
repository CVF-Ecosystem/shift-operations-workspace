from __future__ import annotations


class DualBudgetLimiter:
    def __init__(self, store, *, preauth_limit: int, postauth_limit: int) -> None:
        self.store, self.preauth_limit, self.postauth_limit = store, preauth_limit, postauth_limit

    def consume_preauth(self, peer_key: str) -> bool:
        return self.store.consume_rate("PREAUTH", peer_key, self.preauth_limit)[0]

    def consume_postauth(self, identity_key: str) -> bool:
        return self.store.consume_rate("POSTAUTH", identity_key, self.postauth_limit)[0]
