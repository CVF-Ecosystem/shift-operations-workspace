"""Opt-in live PostgreSQL P4-E Transaction B claim-owner CAS suite
(completion-rereview R3/R4: proves the claim-owner CAS predicates - not
just SQLite/InMemory - reject a wrong token/version/lineage/state and
leave no partial decision/work update on REAL PostgreSQL). Same opt-in
contract as ``test_p4e_postgres_live.py``: requires
``LIVE_POSTGRES_DATABASE_URL``, skips otherwise.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import update

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import p4e_placement_work

_DIGEST64 = "a" * 64
LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R10)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    from workspace_api.domain import models as domain_models

    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _proposal(**overrides):
    fields = dict(
        proposal_id=str(uuid4()), envelope_id=f"pg-env-{uuid4().hex[:8]}", channel="ch1",
        external_id="msg1", candidate={"text": "hi"}, provenance_digest=_DIGEST64,
        sender_evidence=None, idempotency_key=f"pg-idem-{uuid4().hex[:8]}",
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


def test_live_correct_owner_completes_and_wrong_owner_is_rejected(sql_ledger):
    stored, _ = sql_ledger.add_p4e_proposal(_proposal())
    work = sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert work["state"] == "CLAIMED"

    with pytest.raises(ValueError):
        sql_ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token="wrong-token",
            expected_lineage_digest=work["lineage_digest"],
        )
    with pytest.raises(ValueError):
        sql_ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"] + 99, claim_token=work["claim_token"],
            expected_lineage_digest=work["lineage_digest"],
        )
    with pytest.raises(ValueError):
        sql_ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"], claim_token=work["claim_token"],
            expected_lineage_digest="wrong-lineage",
        )

    sql_ledger.complete_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    assert sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    ) is None


def test_live_wrong_state_completion_is_rejected_after_rollback(sql_ledger):
    stored, _ = sql_ledger.add_p4e_proposal(_proposal())
    work = sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    sql_ledger.rollback_placement_work(
        stored["proposal_id"], expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    with pytest.raises(ValueError):
        sql_ledger.complete_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=work["version"] + 1, claim_token=work["claim_token"],
            expected_lineage_digest=work["lineage_digest"],
        )


def test_live_rollback_by_non_owner_is_rejected_and_leaves_no_partial_update(sql_ledger, live_database_url):
    stored, _ = sql_ledger.add_p4e_proposal(_proposal())
    work = sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        sql_ledger.rollback_placement_work(
            stored["proposal_id"], expected_version=work["version"], claim_token="not-the-owner",
            expected_lineage_digest=work["lineage_digest"],
        )
    sql_ledger.engine.dispose()

    from workspace_api.domain import models as domain_models

    fresh = SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))
    still = fresh.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert still is None  # still CLAIMED by the real owner - the rejected rollback wrote nothing


def test_live_claim_and_stale_recovery_reject_wrong_lineage(sql_ledger):
    stored, _ = sql_ledger.add_p4e_proposal(_proposal())
    with pytest.raises(ValueError):
        sql_ledger.claim_placement_work(
            stored["proposal_id"], expected_lineage_digest="b" * 64,
        )
    first = sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    stale_time = datetime.now(timezone.utc) - timedelta(minutes=6)
    with sql_ledger.transaction() as unit:
        unit.execute(
            update(p4e_placement_work)
            .where(p4e_placement_work.c.proposal_id == stored["proposal_id"])
            .values(claimed_at=stale_time)
        )
    with pytest.raises(ValueError):
        sql_ledger.claim_placement_work(
            stored["proposal_id"], expected_lineage_digest="b" * 64,
        )
    recovered = sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert recovered["attempt_count"] == 2
    assert recovered["claim_token"] != first["claim_token"]


def test_live_rollback_and_unclaimed_completion_reject_wrong_lineage(sql_ledger):
    stored, _ = sql_ledger.add_p4e_proposal(_proposal())
    for attempt in range(3):
        work = sql_ledger.claim_placement_work(
            stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
        )
        wrong_lineage = "b" * 64
        with pytest.raises(ValueError):
            sql_ledger.rollback_placement_work(
                stored["proposal_id"], expected_version=work["version"],
                claim_token=work["claim_token"], expected_lineage_digest=wrong_lineage,
            )
        sql_ledger.rollback_placement_work(
            stored["proposal_id"], expected_version=work["version"],
            claim_token=work["claim_token"], expected_lineage_digest=work["lineage_digest"],
        )
    exhausted = sql_ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    with pytest.raises(ValueError):
        sql_ledger.complete_unclaimed_placement_work(
            stored["proposal_id"], _decision(stored["proposal_id"]),
            expected_version=exhausted["version"], expected_lineage_digest="b" * 64,
        )
    sql_ledger.complete_unclaimed_placement_work(
        stored["proposal_id"], _decision(stored["proposal_id"]),
        expected_version=exhausted["version"],
        expected_lineage_digest=exhausted["lineage_digest"],
    )
