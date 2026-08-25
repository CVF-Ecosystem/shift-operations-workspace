"""Bounded runner contract for already-provisioned disposable PostgreSQL."""
import os
from pathlib import Path
import pytest

def test_runner_requires_explicit_disposable_url_and_migration():
    migration=Path(__file__).resolve().parents[2]/"database/migrations/010_integration_edge.sql"
    assert migration.exists() and "edge_raw_envelopes" in migration.read_text()
    if "P4C_POSTGRES_URL" not in os.environ:pytest.skip("no disposable local PostgreSQL authority configured")
    assert "localhost" in os.environ["P4C_POSTGRES_URL"] or "127.0.0.1" in os.environ["P4C_POSTGRES_URL"]
