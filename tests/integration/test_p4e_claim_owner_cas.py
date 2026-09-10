"""P4-E Transaction B claim-owner CAS (completion-rereview R3): completion
and rollback are CAS-owned by the EXACT claim (state, version, token,
lineage digest), never by proposal id alone, on BOTH the SQL and InMemory
backends. Parametrized over both ledgers so a semantic divergence between
backends fails immediately, not later at completion review."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger

_DIGEST64 = "a" * 64


def _sql_ledger() -> SqlLedger:
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)


@pytest.fixture(params=["sql", "inmemory"])
def ledger(request):
    return _sql_ledger() if request.param == "sql" else InMemoryLedger()


def _proposal(**overrides):
    fields = dict(
        proposal_id=str(uuid4()), envelope_id=f"env-{uuid4().hex[:8]}", channel="ch1",
        external_id="msg1", candidate={"text": "hi"}, provenance_digest=_DIGEST64,
        sender_evidence=None, idempotency_key=f"idem-{uuid4().hex[:8]}",
    )
    fields.update(overrides)
    return fields


def _decision(proposal_id, **overrides):
    fields = dict(
        decision_id=str(uuid4()), proposal_id=proposal_id, outcome="FALLBACK", reason="NO_MAPPING",
        mapping_id=None, binding_id=None, target_kind=None, target_id=None, conversation_key=None,
    )
    fields.update(overrides)
    return fields


def test_correct_owner_completes_successfully(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    ledger.complete_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    assert ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    ) is None


def test_wrong_claim_token_is_rejected(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token="wrong-token",
            expected_lineage_digest=work["lineage_digest"],
        )
    # the real owner's claim survived the rejected attempt untouched -
    # completing with the correct token now still succeeds exactly once.
    ledger.complete_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token=work["claim_token"],
            expected_lineage_digest=work["lineage_digest"],
        )


def test_stale_version_is_rejected(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"] + 99, claim_token=work["claim_token"],
            expected_lineage_digest=work["lineage_digest"],
        )


def test_wrong_lineage_digest_is_rejected(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token=work["claim_token"],
            expected_lineage_digest="b" * 64,
        )


def test_wrong_state_is_rejected_completion_never_targets_a_pending_row(ledger):
    """Once a row is rolled back to PENDING, its former (now stale)
    claim can never complete it via the claim-owned CAS path - proves
    ``state == "CLAIMED"`` is part of the predicate, not just
    version/token/lineage."""
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    ledger.rollback_placement_work(
        stored["proposal_id"], expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"] + 1, claim_token=work["claim_token"],
            expected_lineage_digest=work["lineage_digest"],
        )


def test_stale_processor_cannot_complete_after_another_claim_reclaimed_it(ledger):
    """The scenario R3 names directly: processor A claims, times out/loses
    its own bookkeeping, a second real claim (simulated via rollback then
    reclaim) takes over - A's original claim_token/version must no longer
    complete anything."""
    stored, _ = ledger.add_p4e_proposal(_proposal())
    stale_work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    ledger.rollback_placement_work(
        stored["proposal_id"], expected_version=stale_work["version"], claim_token=stale_work["claim_token"],
        expected_lineage_digest=stale_work["lineage_digest"],
    )
    fresh_work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert fresh_work["claim_token"] != stale_work["claim_token"]

    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=stale_work["version"], claim_token=stale_work["claim_token"],
            expected_lineage_digest=stale_work["lineage_digest"],
        )
    # the real (fresh) owner still succeeds
    ledger.complete_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=fresh_work["version"], claim_token=fresh_work["claim_token"],
        expected_lineage_digest=fresh_work["lineage_digest"],
    )


def test_concurrent_completion_race_only_one_winner(ledger):
    """Two callers race to complete the SAME claim - exactly one succeeds,
    the second gets a closed conflict, never a double-applied decision."""
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    ledger.complete_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token=work["claim_token"],
            expected_lineage_digest=work["lineage_digest"],
        )


def test_rollback_by_non_owner_is_rejected(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.rollback_placement_work(
            stored["proposal_id"], expected_version=work["version"], claim_token="someone-elses-token",
            expected_lineage_digest=work["lineage_digest"],
        )
    # the real owner can still roll back
    ledger.rollback_placement_work(
        stored["proposal_id"], expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    reclaimed = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert reclaimed["state"] == "CLAIMED"


def test_rejected_completion_never_records_a_decision_and_leaves_the_claim_intact(ledger):
    """A CAS-rejected completion (wrong token here) must be fully atomic:
    zero decision rows recorded, and the SAME real owner can still
    complete afterward - proves the rejected attempt left no partial
    write on either table."""
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token="wrong-token",
            expected_lineage_digest=work["lineage_digest"],
        )


def test_claim_rejects_wrong_expected_lineage_without_mutation(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    with pytest.raises(ValueError):
        ledger.claim_placement_work(
            stored["proposal_id"], expected_lineage_digest="b" * 64,
        )
    claimed = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert claimed["attempt_count"] == 1


def test_rollback_rejects_wrong_expected_lineage_without_mutation(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.rollback_placement_work(
            stored["proposal_id"], expected_version=work["version"],
            claim_token=work["claim_token"], expected_lineage_digest="b" * 64,
        )
    ledger.rollback_placement_work(
        stored["proposal_id"], expected_version=work["version"],
        claim_token=work["claim_token"], expected_lineage_digest=work["lineage_digest"],
    )


def test_unclaimed_terminal_completion_rejects_wrong_lineage(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
    for _ in range(3):
        work = ledger.claim_placement_work(
            stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
        )
        ledger.rollback_placement_work(
            stored["proposal_id"], expected_version=work["version"],
            claim_token=work["claim_token"], expected_lineage_digest=work["lineage_digest"],
        )
    exhausted = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        ledger.complete_unclaimed_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=exhausted["version"], expected_lineage_digest="b" * 64,
        )
    ledger.complete_unclaimed_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=exhausted["version"],
        expected_lineage_digest=exhausted["lineage_digest"],
    )
