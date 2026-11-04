"""Frozen input independence and deployable raw-byte binding."""

from hashlib import sha256
from pathlib import Path

import pytest

from workspace_api.demo.bundle import P5A2_DEMO_BUNDLE_SHA256, load_bundle
from workspace_api.demo.coverage import P5A2_DEMO_AUTHORITY_SHA256, load_authority

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "apps/workspace-api/src/workspace_api/demo"


def test_deployable_files_match_independently_frozen_bytes():
    for source, copy, digest in (
        (ROOT / "fixtures/p5a2_source_demo_v1.json", DEMO / "source_bundle_v1.json",
         P5A2_DEMO_BUNDLE_SHA256),
        (ROOT / "fixtures/p5a2_source_demo_authority_v1.json", DEMO / "authority_v1.json",
         P5A2_DEMO_AUTHORITY_SHA256),
    ):
        assert source.read_bytes() == copy.read_bytes()
        assert sha256(copy.read_bytes()).hexdigest() == digest
    bundle, authority = load_bundle(), load_authority()
    assert [len(bundle[key]) for key in ("shifts", "assignments", "reports")] == [36, 36, 37]
    assert authority["data_bundle_sha256"] == P5A2_DEMO_BUNDLE_SHA256


def test_loader_refuses_byte_mutation(monkeypatch, tmp_path):
    original = Path(__file__).resolve()
    from workspace_api.demo import bundle as module

    forged = tmp_path / "source_bundle_v1.json"
    forged.write_bytes((DEMO / "source_bundle_v1.json").read_bytes() + b" ")
    monkeypatch.setattr(module, "__file__", str(tmp_path / original.name))
    with pytest.raises(ValueError, match="integrity"):
        module.load_bundle()


def test_seed_uses_canonical_record_classes_and_existing_user_injection():
    from operations_domain.models import Shift, Report
    from operations_domain.assignment_models import ShiftAssignment
    from workspace_api.demo.seed import _models
    from workspace_api.infrastructure.ledger_factory import domain_models

    user, shifts, assignments, reports = _models(
        load_bundle(), "nonphysical-test-password", domain_models.User)
    assert type(user) is domain_models.User
    assert len(shifts) == 36 and all(type(row) is Shift for row in shifts)
    assert len(assignments) == 36 and all(type(row) is ShiftAssignment for row in assignments)
    assert len(reports) == 37 and all(type(row) is Report for row in reports)


def test_seed_refuses_configured_dsn_mismatch_before_factory(monkeypatch):
    from workspace_api.config import settings
    from workspace_api.demo.seed import _owned_ledger
    from workspace_api.infrastructure import ledger_factory

    monkeypatch.setattr(settings, "database_url", "")
    monkeypatch.setattr(ledger_factory, "build_ledger",
                        lambda: pytest.fail("factory called after mismatched DSN"))
    with pytest.raises(RuntimeError, match="configured demo database differs"):
        _owned_ledger("postgresql+psycopg://demo:local@127.0.0.1:5433/shiftops_p5a2_source_demo")


def test_seed_refuses_factory_memory_fallback(monkeypatch):
    from workspace_api.config import settings
    from workspace_api.demo.seed import _owned_ledger
    from workspace_api.infrastructure import ledger_factory

    dsn = "postgresql+psycopg://demo:local@127.0.0.1:5433/shiftops_p5a2_source_demo"
    monkeypatch.setattr(settings, "database_url", dsn)
    monkeypatch.setattr(ledger_factory, "build_ledger", lambda: object())
    with pytest.raises(RuntimeError, match="owned PostgreSQL ledger required"):
        _owned_ledger(dsn)


def test_seed_entry_refuses_missing_marker_before_settings(monkeypatch):
    from workspace_api.demo.seed import main

    monkeypatch.delenv("P5A2_SOURCE_DEMO_PROFILE", raising=False)
    with pytest.raises(RuntimeError, match="profile marker"):
        main()
