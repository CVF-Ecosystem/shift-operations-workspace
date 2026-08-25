from concurrent.futures import ThreadPoolExecutor

from integration_edge.rate_limit import DualBudgetLimiter
from integration_edge.storage import InMemoryEdgeStore


def test_concurrent_preauth_budget_is_exact():
    store=InMemoryEdgeStore(); limiter=DualBudgetLimiter(store,preauth_limit=10,postauth_limit=2)
    with ThreadPoolExecutor(max_workers=20) as pool: results=list(pool.map(lambda _:limiter.consume_preauth("peer"),range(30)))
    assert sum(results)==10 and store.rates[("PREAUTH","peer")]==10

def test_dual_budgets_are_independent():
    store=InMemoryEdgeStore(); limiter=DualBudgetLimiter(store,preauth_limit=2,postauth_limit=1)
    assert limiter.consume_preauth("p") and limiter.consume_preauth("p") and not limiter.consume_preauth("p")
    assert limiter.consume_postauth("id") and not limiter.consume_postauth("id")
