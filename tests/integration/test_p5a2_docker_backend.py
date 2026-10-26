"""Opt-in migrated PostgreSQL proof for the PUBLIC P5-A2 fixture only."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from operations_domain.models import Report, Shift
from operations_domain.report_digest import aggregate_digest, canonical_bytes
from operations_ledger.sql_ledger import SqlLedger, make_engine
from reporting_engine.proactive_analysis import analyze
from reporting_engine.proactive_history import select_history
from reporting_engine.proactive_models import HistoryInput
from workspace_api.domain import models

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "unit"))
from proactive_helpers import START, history, report  # noqa: E402

ORACLE_PATH = ROOT / "tests" / "fixtures" / "p5a2_docker_backend_oracle.json"
ORACLE_SHA256 = "12ad36cbd335a8def5e7ac9a6ade6f0bf542cb45af4cec1760a7291a8f6973c0"
URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


def _oracle() -> dict:
    raw = ORACLE_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ORACLE_SHA256
    return json.loads(raw)


@pytest.fixture(scope="module")
def sql_fixture() -> tuple[list[Report], dict]:
    url = os.environ.get(URL_ENV)
    if not url:
        pytest.skip(f"{URL_ENV} absent: no PostgreSQL or network action")
    oracle = _oracle()
    supplied = history([4] * 36)
    writer_engine = make_engine(url)
    try:
        writer = SqlLedger(url, models=models, engine=writer_engine)
        for index, item in enumerate(supplied.candidates):
            cutoff = START + timedelta(hours=index)
            start = cutoff - timedelta(hours=1)
            writer.create_shift(Shift(shift_id=item.shift_id, name=f"PUBLIC-{index}",
                                      starts_at=start, ends_at=cutoff,
                                      created_at=start - timedelta(hours=1)))
            writer.add_report(item)
        successor = report(0, 9, version=2, created_offset=timedelta(hours=37))
        writer.create_report_successor(supplied.candidates[0].report_id, successor)
    finally:
        writer_engine.dispose()

    reader_engine = make_engine(url)
    try:
        reader = SqlLedger(url, models=models, engine=reader_engine)
        recovered = []
        for shift_id in supplied.eligible_shift_ids:
            recovered.extend(reader.list_reports_for_shift(shift_id, "END_SHIFT"))
        yield recovered, oracle
    finally:
        reader_engine.dispose()


def _candidate_metadata(item: Report) -> dict:
    assert item.generated_from_cutoff.tzinfo is not None
    assert item.generated_from_cutoff.utcoffset() is not None
    assert item.created_at.tzinfo is not None
    assert item.created_at.utcoffset() is not None
    content_bytes = canonical_bytes(item.content.model_dump(mode="json"))
    assert aggregate_digest(item.shift_id, item.report_type, item.content) == item.content.snapshot_digest
    return {
        "created_at": item.created_at.isoformat().replace("+00:00", "Z"),
        "cutoff": item.generated_from_cutoff.isoformat().replace("+00:00", "Z"),
        "immutable_content_sha256": hashlib.sha256(content_bytes).hexdigest(),
        "report_id": str(item.report_id), "shift_id": str(item.shift_id),
        "snapshot_digest": item.content.snapshot_digest, "version": item.version,
    }


def test_postgres_36_shift_version_roundtrip_matches_frozen_oracle(sql_fixture):
    reports, oracle = sql_fixture
    assert oracle["prepared_before_new_sql_loader_build"] is True
    assert oracle["fixture_id"] == "P5A2-PUBLIC-PG36-V1"
    assert oracle["shift_count"] == 36 and oracle["persisted_report_count"] == 37
    assert len(reports) == 37
    actual = sorted((_candidate_metadata(item) for item in reports),
                    key=lambda row: (row["shift_id"], row["version"]))
    expected = sorted(oracle["candidate_immutable_metadata"],
                      key=lambda row: (row["shift_id"], row["version"]))
    assert actual == expected
    prior = next(item for item in reports if item.shift_id == report(0, 4).shift_id and item.version == 1)
    later = next(item for item in reports if item.shift_id == prior.shift_id and item.version == 2)
    assert prior.is_current is False and later.is_current is True

    ids = tuple(sorted((report(i, 4).shift_id for i in range(36)), key=str))
    assert [str(i) for i in ids] == oracle["eligible_shift_ids"]
    results = []
    for case in oracle["cases"]:
        as_of = START + timedelta(hours=36 if case["case"] == "initial_asof36" else 38)
        source = HistoryInput("PUBLIC_SCOPE", "PUBLIC_ACTOR", START,
                              START + timedelta(hours=36), as_of, ids,
                              tuple(reports), True, True)
        selected = select_history(source, as_of, require_complete=True)
        assert [item.lineage_item() for item in selected] == case["selected_reports"]
        result = analyze(source)
        projection = {k: v for k, v in result.items() if k != "history_context"}
        assert projection == case["analysis"]
        assert result["outcome"] == "READY" and result["observation_count"] == 36
        assert result["forecast_count"] == 4
        assert (result["interval_low"], result["interval_high"]) == (4, 4)
        results.append(result)
    assert results[0]["lineage_digest"] != results[1]["lineage_digest"]
    assert results[0]["evaluation_digest"] != results[1]["evaluation_digest"]
