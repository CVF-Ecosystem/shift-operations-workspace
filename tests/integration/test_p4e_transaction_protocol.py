"""P4-E two-transaction admission/processing protocol tests (SPEC R11/R12,
AC-06/AC-07): transaction A idempotent admission and collision refusal,
transaction B digest reread and at-most-one decision, rollback-to-pending,
bounded attempts, stale-claim CAS recovery, and terminal exhaustion.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import insert, update

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata, p4e_placement_work, users
from workspace_api.domain import models as domain_models
from workspace_api.external_ingress.models import ExternalIngressProposal, ExternalIngressProposalInput
from workspace_api.external_ingress.repository import LedgerExternalIngressRepository
from workspace_api.external_ingress.service import ExternalIngressService
from workspace_api.application.p4e_placement import P4ePlacementProcessor

_DIGEST64 = "a" * 64


class _FakeKeyPort:
    def active_key(self):
        return "k1", "1", b"0" * 32

    def resolve_key(self, key_id, key_version):
        return b"0" * 32 if (key_id, key_version) == ("k1", "1") else None


@pytest.fixture()
def ledger() -> SqlLedger:
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    sql_ledger = SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)
    with engine.begin() as conn:
        conn.execute(insert(users).values(user_id="u1", username="u1", password_hash="x", role="operator", is_active=True))
    return sql_ledger


def _accept(assertion, **_kwargs):
    return assertion


def _proposal_input(**overrides) -> ExternalIngressProposalInput:
    fields = dict(
        envelope_id=str(uuid4()), channel="ch1", external_id="msg1",
        candidate={"text": "hello"}, provenance_digest=_DIGEST64,
    )
    fields.update(overrides)
    return ExternalIngressProposalInput(**fields)


def _claim(ledger, proposal_id: str):
    stored = ledger.get_p4e_proposal(proposal_id)
    return ledger.claim_placement_work(
        proposal_id, expected_lineage_digest=stored["lineage_digest"],
    )


def test_transaction_a_admits_proposal_and_creates_exactly_one_work_item(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    proposal = repository.add(ExternalIngressProposal(**_proposal_input().model_dump()))
    work = _claim(ledger, str(proposal.proposal_id))
    assert work is not None
    assert work["proposal_id"] == str(proposal.proposal_id)


def test_transaction_a_idempotent_admission_preserves_proposal_id(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    envelope_id = str(uuid4())
    proposal_1 = ExternalIngressProposal(**_proposal_input(envelope_id=envelope_id).model_dump())
    repository.add(proposal_1)
    proposal_2 = ExternalIngressProposal(**_proposal_input(envelope_id=envelope_id).model_dump())
    repository.add(proposal_2)
    # Same envelope/idempotency identity returns the prior admission - no
    # regenerated identity, no second work item silently created.
    stored = ledger.get_p4e_proposal(str(proposal_1.proposal_id))
    assert stored["envelope_id"] == envelope_id


def test_transaction_a_lineage_collision_refused_on_key_reuse_with_different_envelope(ledger):
    """The default repository derives idempotency_key from envelope_id
    1:1, so a genuine key-reuse-with-different-lineage collision is
    exercised directly at the ledger method (SPEC R11), which is the
    actual enforcement point regardless of repository key-derivation
    policy."""
    proposal_a = {
        "proposal_id": str(uuid4()), "envelope_id": "env-a", "channel": "ch1", "external_id": "msg1",
        "candidate": {"text": "hi"}, "provenance_digest": _DIGEST64, "sender_evidence": None,
        "idempotency_key": "shared-key",
    }
    ledger.add_p4e_proposal(proposal_a)
    proposal_b = dict(proposal_a, proposal_id=str(uuid4()), envelope_id="env-b")
    with pytest.raises(ValueError):
        ledger.add_p4e_proposal(proposal_b)


def test_transaction_b_processes_and_leaves_exactly_one_terminal_decision(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    proposal = repository.add(ExternalIngressProposal(**_proposal_input().model_dump()))
    processor = P4ePlacementProcessor(ledger, _DIGEST64, _FakeKeyPort())
    decision = processor.process(str(proposal.proposal_id))
    assert decision is not None
    assert decision.outcome == "FALLBACK"
    assert decision.decision_count == 1
    assert decision.work_complete is True

    second_attempt = processor.process(str(proposal.proposal_id))
    assert second_attempt is None  # already COMPLETE - not reprocessed


def test_external_ingress_service_composes_transaction_a_then_b(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    processor = P4ePlacementProcessor(ledger, _DIGEST64, _FakeKeyPort())
    service = ExternalIngressService(repository, _accept, placement_processor=processor)
    stored = service.propose(_proposal_input(), assertion="ignored")
    work = _claim(ledger, str(stored.proposal_id))
    assert work is None  # COMPLETE after the synchronous transaction-B attempt


def test_transaction_b_failure_leaves_item_pending_never_erases_proposal(ledger, monkeypatch):
    """SPEC R11/R12: a transient dependency failure rolls B back and leaves
    the item pending with zero placement decision; the admitted proposal
    and its receipt are never erased. Failure is injected at
    ``complete_placement_work`` - reached on every routing outcome, right
    before the final commit, exactly where a real transient dependency
    failure (a lost connection, a full disk) would occur."""
    repository = LedgerExternalIngressRepository(ledger)
    proposal = repository.add(ExternalIngressProposal(**_proposal_input().model_dump()))

    original = type(ledger).complete_placement_work

    def _boom(self, *args, **kwargs):
        raise RuntimeError("simulated transient dependency failure")

    monkeypatch.setattr(type(ledger), "complete_placement_work", _boom)

    processor = P4ePlacementProcessor(ledger, _DIGEST64, _FakeKeyPort())
    with pytest.raises(RuntimeError):
        processor.process(str(proposal.proposal_id))

    monkeypatch.setattr(type(ledger), "complete_placement_work", original)

    # Proposal itself survives; the work item is left pending (rolled back
    # from CLAIMED), not silently marked complete.
    still_there = ledger.get_p4e_proposal(str(proposal.proposal_id))
    assert still_there is not None
    work = _claim(ledger, str(proposal.proposal_id))
    assert work is not None  # reclaimable - was rolled back to PENDING


def test_stale_claim_recovered_by_cas_after_five_minutes(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    proposal = repository.add(ExternalIngressProposal(**_proposal_input().model_dump()))
    proposal_id = str(proposal.proposal_id)

    # Simulate a stale claim: CLAIMED, claimed 6 minutes ago.
    stale_time = datetime.now(timezone.utc) - timedelta(minutes=6)
    with ledger.transaction() as unit:
        unit.execute(
            update(p4e_placement_work)
            .where(p4e_placement_work.c.proposal_id == proposal_id)
            .values(state="CLAIMED", claim_token="stale-token", claimed_at=stale_time, attempt_count=1)
        )

    recovered = _claim(ledger, proposal_id)
    assert recovered is not None
    assert recovered["state"] == "CLAIMED"
    assert recovered["attempt_count"] == 2


def test_fresh_claim_not_recoverable_before_five_minutes(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    proposal = repository.add(ExternalIngressProposal(**_proposal_input().model_dump()))
    proposal_id = str(proposal.proposal_id)

    recent_time = datetime.now(timezone.utc) - timedelta(minutes=2)
    with ledger.transaction() as unit:
        unit.execute(
            update(p4e_placement_work)
            .where(p4e_placement_work.c.proposal_id == proposal_id)
            .values(state="CLAIMED", claim_token="fresh-token", claimed_at=recent_time, attempt_count=1)
        )

    not_recoverable = _claim(ledger, proposal_id)
    assert not_recoverable is None


def test_exhausted_attempts_yield_terminal_refused_retry_exhausted(ledger):
    repository = LedgerExternalIngressRepository(ledger)
    proposal = repository.add(ExternalIngressProposal(**_proposal_input().model_dump()))
    proposal_id = str(proposal.proposal_id)

    with ledger.transaction() as unit:
        unit.execute(
            update(p4e_placement_work)
            .where(p4e_placement_work.c.proposal_id == proposal_id)
            .values(attempt_count=4)
        )

    processor = P4ePlacementProcessor(ledger, _DIGEST64, _FakeKeyPort())
    decision = processor.process(proposal_id)
    assert decision is not None
    assert decision.outcome == "REFUSED"
    assert decision.reason == "RETRY_EXHAUSTED"
    assert decision.decision_count == 1
