"""P4-A SPEC R6 - atomic process-local usage ledger.

NOT GOVERNANCE PROOF: mechanical tests of in-process accounting. The ledger is
explicitly non-durable; these tests prove transition safety, not persistence.
"""

from __future__ import annotations

import threading

import pytest

from ai_gateway.errors import BudgetUnavailableError, UsageLedgerError
from ai_gateway.models import BudgetFacts
from ai_gateway.usage import UsageLedger


def _facts(**overrides) -> BudgetFacts:
    base = dict(
        per_request_token_limit=1000,
        daily_budget_usd_millis=100,
        monthly_budget_usd_millis=1000,
        spent_today_usd_millis=0,
        spent_month_usd_millis=0,
        estimated_cost_usd_millis=10,
    )
    base.update(overrides)
    return BudgetFacts(**base)


class TestReservation:
    def test_reserve_then_commit_records_actual_usage(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(_facts(), estimated_tokens=100)
        ledger.commit(reservation.reservation_id, actual_tokens=80, actual_cost_usd_millis=8)
        assert ledger.committed_tokens == 80
        assert ledger.committed_cost_usd_millis == 8
        assert ledger.outstanding_reservations == 0

    def test_release_records_no_usage(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(_facts(), estimated_tokens=100)
        ledger.release(reservation.reservation_id)
        assert ledger.committed_tokens == 0
        assert ledger.outstanding_reservations == 0

    def test_per_request_token_limit_refuses(self):
        ledger = UsageLedger()
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(_facts(per_request_token_limit=50), estimated_tokens=51)

    def test_daily_cap_refuses(self):
        ledger = UsageLedger()
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(
                _facts(daily_budget_usd_millis=100, spent_today_usd_millis=95), estimated_tokens=1
            )

    def test_monthly_cap_refuses(self):
        ledger = UsageLedger()
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(
                _facts(monthly_budget_usd_millis=100, spent_month_usd_millis=95),
                estimated_tokens=1,
            )

    def test_zero_cap_means_no_cap_declared(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(
            _facts(daily_budget_usd_millis=0, monthly_budget_usd_millis=0), estimated_tokens=1
        )
        assert reservation.estimated_tokens == 1

    def test_negative_estimate_rejected(self):
        ledger = UsageLedger()
        with pytest.raises(UsageLedgerError):
            ledger.reserve(_facts(), estimated_tokens=-1)


class TestCumulativeAccounting:
    """P4A-REV-F2: committed cost must count toward later projections."""

    def test_sequential_commits_are_counted_against_the_cap(self):
        """Reviewer probe: 5-millis cap, three sequential 3-millis requests.

        Only the first may be admitted (projected 3 <= 5); the second (would
        project 3+3=6 > 5) and third must be refused. Before the repair all
        three were admitted (committed total 9), because the ledger's own
        committed cost was never added into the projection.
        """
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=5, estimated_cost_usd_millis=3)

        first = ledger.reserve(facts, estimated_tokens=1)
        ledger.commit(first.reservation_id, actual_tokens=1, actual_cost_usd_millis=3)
        assert ledger.committed_cost_usd_millis == 3

        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(facts, estimated_tokens=1)

        assert ledger.committed_cost_usd_millis == 3, "no further commit must occur"

    def test_outstanding_reservation_counts_before_commit(self):
        """An open (uncommitted) reservation must also count toward the cap."""
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=5, estimated_cost_usd_millis=3)
        ledger.reserve(facts, estimated_tokens=1)  # open, not yet committed
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(facts, estimated_tokens=1)

    def test_exact_boundary_at_cap_is_admitted(self):
        """Ledger refuses only when the projection would EXCEED the cap; a
        request landing exactly on the cap is admitted (SPEC: 'daily budget
        would be exceeded', strict >, not >=). cvf_runtime.budget's own
        post-reservation state check separately uses >=; the two checks run
        at different stages and are independently correct."""
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=10, estimated_cost_usd_millis=10)
        reservation = ledger.reserve(facts, estimated_tokens=1)
        assert reservation.estimated_cost_usd_millis == 10

    def test_one_millis_over_boundary_is_refused(self):
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=10, estimated_cost_usd_millis=11)
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(facts, estimated_tokens=1)

    def test_release_frees_capacity_for_a_later_request(self):
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=5, estimated_cost_usd_millis=3)
        first = ledger.reserve(facts, estimated_tokens=1)
        ledger.release(first.reservation_id)
        second = ledger.reserve(facts, estimated_tokens=1)
        assert second.estimated_cost_usd_millis == 3

    def test_prior_caller_supplied_spend_and_ledger_spend_both_count(self):
        """spent_today_usd_millis (external accounting) adds to ledger spend."""
        ledger = UsageLedger()
        facts = _facts(
            daily_budget_usd_millis=10, spent_today_usd_millis=8, estimated_cost_usd_millis=3
        )
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(facts, estimated_tokens=1)

    def test_monthly_cap_also_counts_committed_cost(self):
        ledger = UsageLedger()
        facts = _facts(monthly_budget_usd_millis=5, estimated_cost_usd_millis=3)
        first = ledger.reserve(facts, estimated_tokens=1)
        ledger.commit(first.reservation_id, actual_tokens=1, actual_cost_usd_millis=3)
        with pytest.raises(BudgetUnavailableError):
            ledger.reserve(facts, estimated_tokens=1)


class TestUnitConversionHelper:
    def test_millis_to_usd_converts_exactly(self):
        from ai_gateway.context import millis_to_usd

        assert millis_to_usd(1000) == 1.0
        assert millis_to_usd(1) == 0.001
        assert millis_to_usd(0) == 0.0

    def test_millis_to_usd_matches_cvf_runtime_scale(self):
        """cvf_runtime.budget compares USD floats; 1000 millis is exactly $1."""
        from ai_gateway.context import millis_to_usd

        assert millis_to_usd(2500) == 2.5


class TestIllegalTransitions:
    def test_double_commit_refused(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(_facts(), estimated_tokens=10)
        ledger.commit(reservation.reservation_id, actual_tokens=1, actual_cost_usd_millis=1)
        with pytest.raises(UsageLedgerError):
            ledger.commit(reservation.reservation_id, actual_tokens=1, actual_cost_usd_millis=1)

    def test_double_release_refused(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(_facts(), estimated_tokens=10)
        ledger.release(reservation.reservation_id)
        with pytest.raises(UsageLedgerError):
            ledger.release(reservation.reservation_id)

    def test_commit_after_release_refused(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(_facts(), estimated_tokens=10)
        ledger.release(reservation.reservation_id)
        with pytest.raises(UsageLedgerError):
            ledger.commit(reservation.reservation_id, actual_tokens=1, actual_cost_usd_millis=1)

    def test_unknown_reservation_refused(self):
        ledger = UsageLedger()
        with pytest.raises(UsageLedgerError):
            ledger.release("res-does-not-exist")

    def test_negative_actual_usage_refused(self):
        ledger = UsageLedger()
        reservation = ledger.reserve(_facts(), estimated_tokens=10)
        with pytest.raises(UsageLedgerError):
            ledger.commit(reservation.reservation_id, actual_tokens=-1, actual_cost_usd_millis=0)


class TestConcurrency:
    def test_concurrent_reservations_cannot_over_reserve(self):
        """R6: outstanding reservations count toward the cap under a lock.

        Cap is 100 millis and each reservation estimates 10, so at most 10 of
        the 40 competing threads may succeed.
        """
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=100, estimated_cost_usd_millis=10)
        granted: list[object] = []
        refused: list[object] = []
        lock = threading.Lock()

        def attempt() -> None:
            try:
                reservation = ledger.reserve(facts, estimated_tokens=1)
            except BudgetUnavailableError:
                with lock:
                    refused.append(True)
            else:
                with lock:
                    granted.append(reservation)

        threads = [threading.Thread(target=attempt) for _ in range(40)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(granted) == 10
        assert len(refused) == 30
        assert ledger.outstanding_reservations == 10

    def test_reservation_ids_are_unique_under_concurrency(self):
        ledger = UsageLedger()
        facts = _facts(daily_budget_usd_millis=0, monthly_budget_usd_millis=0)
        ids: list[str] = []
        lock = threading.Lock()

        def attempt() -> None:
            reservation = ledger.reserve(facts, estimated_tokens=1)
            with lock:
                ids.append(reservation.reservation_id)

        threads = [threading.Thread(target=attempt) for _ in range(25)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(ids) == 25 and len(set(ids)) == 25
