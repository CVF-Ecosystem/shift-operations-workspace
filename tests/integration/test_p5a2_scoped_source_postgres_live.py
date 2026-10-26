"""One opt-in, owned-context physical PostgreSQL scoped-source experiment."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

import pytest

from operations_domain.report_digest import aggregate_digest, canonical_bytes
from operations_ledger.sql_ledger import SqlLedger, make_engine
from reporting_engine.proactive_analysis import analyze
from reporting_engine.proactive_history import select_history
from workspace_api.application.proactive_source import query_source
from workspace_api.domain import models

from p5a2_scoped_source_pg_fixture import (
    BODY_ORACLE, BODY_SHA, PG_ORACLE, PG_SHA, ROOT, SOURCE_ORACLE, SOURCE_SHA,
    baseline_expectations, context, oracle, seed_aux, seed_baseline,
    validate_all_auxiliary_fixtures,
)
from p5a2_scoped_source_pg_probes import (
    assert_closed_refusal, counted_query, race_query, repeatable_read_probe, traced_ready_query,
)

ADMISSION = ROOT / "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ADMISSION_2026-10-26.json"
ATTEMPT = ROOT / "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ATTEMPT_2026-10-26.json"
OWNED_ENV = "P5A2_PG_OWNED_CONTEXT"
URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


def _verified_port_binding(name: str, port: int) -> None:
    binding = subprocess.run(["docker", "inspect", name, "--format",
                              "{{json .HostConfig.PortBindings}}"], capture_output=True, text=True, check=False)
    assert binding.returncode == 0 and json.loads(binding.stdout) == {
        "5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(port)}]}


def _owned_context():
    raw = os.environ.get(OWNED_ENV)
    if raw is None:
        pytest.skip("no runner-owned context; ambient LIVE URL cannot activate physical proof")
    owned = json.loads(raw)
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    if admission["status"] != "SOURCE_REVIEWED" or not admission["harnessPins"]:
        raise AssertionError("sealed physical admission absent")
    assert sha256(ADMISSION.read_bytes()).hexdigest() == owned["admission_sha256"]
    for key in ("nonce", "container_name", "image_id", "host_port"):
        assert owned[key] == marker[key]
    assert marker["admission_sha256"] == owned["admission_sha256"]
    assert owned["image_id"] == admission["imageId"]
    assert owned["container_name"].startswith("cvf-pg-live-")
    for relative, digest in {**admission["sourcePins"], **admission["harnessPins"]}.items():
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT.resolve()) and sha256(path.read_bytes()).hexdigest() == digest
    for field, value in (("{{.Id}}", owned["container_id"]), ("{{.Image}}", owned["image_id"])):
        inspected = subprocess.run(["docker", "inspect", owned["container_name"], "--format", field],
                                   capture_output=True, text=True, check=False)
        assert inspected.returncode == 0 and inspected.stdout.strip() == value
    _verified_port_binding(owned["container_name"], owned["host_port"])
    url = os.environ[URL_ENV]
    parsed = urlsplit(url)
    assert (parsed.scheme, parsed.hostname, parsed.port, parsed.username, parsed.path) == (
        "postgresql+psycopg", "127.0.0.1", owned["host_port"], "cvf_live", "/cvf_live_roundtrip")
    assert parsed.password and parsed.query == "" and parsed.fragment == ""
    return owned, admission, url


def _claim_target(admission, owned):
    path = (ROOT / admission["observationPath"]).resolve()
    assert path.is_relative_to(ROOT.resolve())
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w",
                   encoding="utf-8") as stream:
        json.dump({"target_claim": "SPENT_ONCE", "nonce": owned["nonce"]}, stream)
        stream.write("\n")
    return path


def _metadata(item) -> dict:
    content = item.content.model_dump(mode="json")
    assert aggregate_digest(item.shift_id, item.report_type, item.content) == item.content.snapshot_digest
    assert item.created_at.tzinfo is not None and item.generated_from_cutoff.tzinfo is not None
    return {"created_at": item.created_at.isoformat().replace("+00:00", "Z"),
            "cutoff": item.generated_from_cutoff.isoformat().replace("+00:00", "Z"),
            "immutable_content_sha256": sha256(canonical_bytes(content)).hexdigest(),
            "report_id": str(item.report_id), "shift_id": str(item.shift_id),
            "snapshot_digest": item.content.snapshot_digest, "version": item.version}


def _baseline(reader, fixture, source_oracle, body_oracle, pg_oracle, foreign_id, monkeypatch):
    recorded = []
    for context_row, golden in zip(pg_oracle["baselineContexts"], source_oracle["cases"]):
        assert context_row["case"] == golden["case"]
        result, trace = traced_ready_query(reader, context_row, fixture[context_row["case"]],
                                           foreign_id, monkeypatch)
        assert result.receipt == golden["expected_receipt"] and result.payload is not None
        selected = select_history(result.payload, context(context_row)[-1], require_complete=True)
        assert [item.lineage_item() for item in selected] == golden["expected_selected_reports"]
        analysis = analyze(result.payload)
        assert {k: v for k, v in analysis.items() if k != "history_context"} == golden["expected_analysis"]
        if context_row["case"] == "later_asof38":
            actual = sorted((_metadata(item) for item in result.payload.candidates),
                            key=lambda value: (value["shift_id"], value["version"]))
            expected = sorted(body_oracle["candidate_immutable_metadata"],
                              key=lambda value: (value["shift_id"], value["version"]))
            assert actual == expected and len(actual) == 37
        recorded.append({"case": context_row["case"], "source_digest": result.receipt["source_digest"],
                         "eligible_count": result.receipt["eligible_count"],
                         "candidate_version_count": result.receipt["candidate_version_count"],
                         "lineage_digest": analysis["lineage_digest"], "transaction_trace": trace})
    assert recorded[0]["source_digest"] != recorded[1]["source_digest"]
    return recorded


def test_owned_postgres_scoped_source_full_experiment(monkeypatch):
    owned, admission, url = _owned_context()
    path = _claim_target(admission, owned)
    validate_all_auxiliary_fixtures()  # Pure construction, before any DB write.
    pg = oracle(PG_ORACLE, PG_SHA)
    source = oracle(SOURCE_ORACLE, SOURCE_SHA)
    body = oracle(BODY_ORACLE, BODY_SHA)
    engine = make_engine(url)
    writer_engine = make_engine(url)
    observations = {"experiment_id": pg["id"], "container_id": owned["container_id"],
                    "image_id": owned["image_id"], "oracle_sha256": PG_SHA,
                    "cases": [], "caps": [], "races": []}
    try:
        writer = SqlLedger(url, models=models, engine=writer_engine)
        reader = SqlLedger(url, models=models, engine=engine)
        baseline = seed_baseline(writer)
        cap_fixtures = [(row, seed_aux(writer, row)) for row in pg["capCases"]]
        negative_fixtures = [(row, seed_aux(writer, row)) for row in pg["negativeCases"]]
        race_fixtures = [(row, seed_aux(writer, row)) for row in pg["raceCases"]]
        snapshot = seed_aux(writer, pg["snapshotCase"])
        foreign_row, foreign = next((row, fixture) for row, fixture in negative_fixtures
                                    if row["id"] == "foreign")
        observations["cases"] = _baseline(reader, baseline, source, body, pg,
                                           foreign.reports[0].report_id, monkeypatch)
        for row, fixture in cap_fixtures:
            result, counts = counted_query(reader, row, fixture, monkeypatch)
            assert result.receipt["outcome"] == row["outcome"]
            assert counts["body_load_calls"] == row["bodyLoadCalls"]
            if row["size"] == 501:
                assert_closed_refusal(result, row["reason"])
                assert counts["body_rows"] == counts["body_select_calls"] == 0
            else:
                assert result.payload is not None and counts["body_select_calls"] == 1
                assert counts["body_rows"] == row["shiftCount"] * row["reportVersions"]
                assert result.receipt[{"eligible": "eligible_count", "candidates": "candidate_version_count",
                                       "refs": "max_snapshot_incident_refs"}[row["dimension"]]] == 500
            observations["caps"].append({"case": row["id"], "outcome": result.receipt["outcome"],
                                          "reason": result.receipt.get("reason"), **counts})
        for row, fixture in negative_fixtures:
            if row["id"] == "foreign":
                continue  # Already challenged inside the exact baseline oracle query.
            result, counts = counted_query(reader, row,
                None if row["id"] == "no_coverage" else fixture, monkeypatch)
            assert_closed_refusal(result, row["reason"])
            if row["id"] == "reportless":
                principal, _scope, start, end, as_of = context(row)
                with reader.scoped_source_read(principal.user_id, start, end, as_of) as unit:
                    cohort = unit.cohort()
                    candidates = unit.candidates(tuple(item.shift_id for item in cohort))
                assert len(cohort) == row["enrolledCohortCountBeforeRefusal"] == 1
                assert len(candidates) == 0
                assert counts["body_load_calls"] == row["bodyLoadCalls"] == 0
            observations["cases"].append({"case": row["id"], "reason": row["reason"], **counts})
        observations["snapshot"] = repeatable_read_probe(reader, writer, pg["snapshotCase"], snapshot)
        for row, fixture in race_fixtures:
            result, identity = race_query(reader, writer, row, fixture, monkeypatch)
            assert_closed_refusal(result, row["reason"])
            observations["races"].append({"case": row["id"], "reason": row["reason"], **identity})
        observations["completed"] = True
        with path.open("w", encoding="utf-8") as stream:
            json.dump(observations, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
    finally:
        engine.dispose()
        writer_engine.dispose()
