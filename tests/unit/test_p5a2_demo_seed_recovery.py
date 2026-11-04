"""Inert AM2 full-row and registered outcome adapter evidence."""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from invariant_family_contract import (generate_mutations, load_json_no_dup,
                                       matches_shape_exactly)
from p5a2_source_demo_recovery_inventory import expected_tables
from p5a2_source_demo_bootstrap import isolated_child_env
import p5a2_source_demo_recover as recovery
from workspace_api.auth.passwords import hash_password
from workspace_api.demo.bundle import load_bundle
from workspace_api.demo.seed_recovery import (family_record, proven_refusal_record,
                                             seed_transaction)
from workspace_api.demo.seed_recovery_compare import _json_value, compare_rows
from workspace_api.domain.models import User
from operations_domain.models import Report, Shift
from operations_domain.assignment_models import ShiftAssignment

MATRIX = load_json_no_dup(ROOT / "docs/cvf/invariants/p5a2-demo-seed-recovery.json")
FINGERPRINT = "a" * 64
PASSWORD = "inert-test-password-long"


def test_parent_inventory_user_seam_is_canonical_and_config_free(tmp_path):
    code = """
import builtins
import pathlib
import sys
real_open = builtins.open
real_path_open = pathlib.Path.open
def checked_open(path, *args, **kwargs):
    if str(path).endswith('.env'):
        raise AssertionError('dotenv read attempted')
    return real_open(path, *args, **kwargs)
def checked_path_open(path, *args, **kwargs):
    if str(path).endswith('.env'):
        raise AssertionError('dotenv read attempted')
    return real_path_open(path, *args, **kwargs)
builtins.open = checked_open
pathlib.Path.open = checked_path_open
from workspace_api.infrastructure import repository
from workspace_api.domain import models
assert repository.User is models.User
assert 'workspace_api.config' not in sys.modules
assert 'workspace_api.infrastructure.ledger_factory' not in sys.modules
"""
    proc = subprocess.run([sys.executable, "-P", "-c", code], cwd=tmp_path,
                          env=isolated_child_env(), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


@pytest.fixture(scope="module")
def raw_rows():
    bundle = load_bundle()
    rows = {name: [] for name in expected_tables()}
    rows["users"] = [User(**bundle["user"],
                          password_hash=hash_password(PASSWORD)).model_dump(mode="python")]
    rows["shifts"] = [Shift(**row).model_dump(mode="python") for row in bundle["shifts"]]
    rows["shift_assignments"] = [ShiftAssignment(**row).model_dump(mode="python")
                                 for row in bundle["assignments"]]
    rows["reports"] = [Report(**row).model_dump(mode="python")
                       for row in bundle["reports"]]
    return rows


def test_full_rows_exact_empty_and_sole_timestamp(raw_rows):
    bundle = load_bundle()
    exact = compare_rows(raw_rows, bundle, PASSWORD, User)
    assert exact["classification"] == "EXACT_SEEDED"
    assert exact["counts"] == {name: {"users": 1, "shifts": 36,
                                      "shift_assignments": 36,
                                      "reports": 37}.get(name, 0)
                               for name in expected_tables()}
    empty = compare_rows({name: [] for name in expected_tables()}, bundle,
                         PASSWORD, User)
    assert empty["classification"] == "EMPTY_COMPATIBLE"
    changed = copy.deepcopy(raw_rows)
    changed["users"][0]["created_at"] = changed["users"][0]["created_at"].replace(year=2026)
    sole = compare_rows(changed, bundle, PASSWORD, User)
    assert sole["classification"] == "SOLE_CREATED_AT_MISMATCH"
    assert sole["state_digest"] != exact["state_digest"]
    assert sole["observed_created_at"] != exact["observed_created_at"]


def test_noncanonical_user_type_refuses_even_for_empty_snapshot():
    class WrongUser(User):
        pass

    with pytest.raises(RuntimeError, match="USER_TYPE_INVALID"):
        compare_rows({name: [] for name in expected_tables()}, load_bundle(),
                     PASSWORD, WrongUser)


@pytest.mark.parametrize("mutation", ["extra_column", "role", "password", "report_body",
                                      "partial", "foreign"])
def test_other_rows_or_security_fail_before_write(raw_rows, mutation):
    rows = copy.deepcopy(raw_rows)
    if mutation == "extra_column":
        rows["users"][0]["undeclared"] = "x"
    elif mutation == "role":
        rows["users"][0]["role"] = "operator"
    elif mutation == "password":
        rows["users"][0]["password_hash"] = hash_password("wrong-inert-password")
    elif mutation == "report_body":
        rows["reports"][0]["content"]["summary"] = "altered"
    elif mutation == "partial":
        rows["reports"].pop()
    else:
        rows["tasks"] = [{"task_id": "foreign"}]
    with pytest.raises((RuntimeError, ValueError)):
        compare_rows(rows, load_bundle(), PASSWORD, User)


def test_unknown_raw_type_and_forged_31_table_set_refuse():
    with pytest.raises(RuntimeError, match="unsupported raw column type"):
        _json_value(object())
    names = sorted(expected_tables())
    names[0] = "zz_forged"
    snapshot = {"classification": "EMPTY_COMPATIBLE", "state_digest": "b" * 64,
                "db_fingerprint": FINGERPRINT, "schema_digest": "c" * 64,
                "observed_created_at": None, "table_names": names}
    class NoEngine:
        def begin(self):
            pytest.fail("transaction opened for forged table set")
    class Ledger:
        engine = NoEngine()
    with pytest.raises(RuntimeError, match="table set invalid"):
        seed_transaction(Ledger(), load_bundle(), {"data_bundle_sha256": "pinned"},
                         PASSWORD, snapshot)


def test_seed_recovery_invariant_family():
    """Four actual emitter positives and every generated invalid mutation."""
    records = [
        proven_refusal_record(FINGERPRINT, "PREWRITE_MISMATCH"),
        family_record("SEEDED", FINGERPRINT),
        family_record("VERIFY", FINGERPRINT),
        family_record("CREATED_AT_REPAIRED", FINGERPRINT,
                      "2026-10-27T00:00:00+00:00", "2025-12-31T20:00:00Z"),
    ]
    assert [r["outcome"] for r in records] == [
        "REFUSED_ZERO_WRITE", "SEEDED_ATOMIC", "EXACT_VERIFIED",
        "CREATED_AT_REPAIRED"]
    mutations = 0
    for outcome, record in zip(MATRIX["outcomes"], records):
        shape = outcome["shapes"][0]
        assert matches_shape_exactly(shape, record, MATRIX)
        generated = generate_mutations(MATRIX, shape["shapeId"], record)
        assert generated
        for mutation in generated:
            assert not matches_shape_exactly(shape, mutation.payload, MATRIX)
            mutations += 1
    assert mutations >= 20


@pytest.mark.parametrize("classification,result", [
    ("EMPTY_COMPATIBLE", "SEEDED"),
    ("EXACT_SEEDED", "VERIFY"),
    ("SOLE_CREATED_AT_MISMATCH", "CREATED_AT_REPAIRED"),
])
def test_native_child_receipt_is_bounded_and_matrix_checked(monkeypatch,
                                                             classification, result):
    before = {"classification": classification, "state_digest": "b" * 64,
              "db_fingerprint": FINGERPRINT,
              "schema_digest": "d" * 64,
              "table_names": sorted(expected_tables()),
              "observed_created_at": "2026-10-27T00:00:00+00:00"
              if classification == "SOLE_CREATED_AT_MISMATCH" else None}
    record = family_record(result, FINGERPRINT, before["observed_created_at"],
                           "2025-12-31T20:00:00Z")
    output = {"result": result, "state_digest": "c" * 64,
              "db_fingerprint": FINGERPRINT, "family_record": record}
    monkeypatch.setattr(recovery, "run", lambda *a, **kw: __import__("json").dumps(output))
    assert recovery._native_seed("unused", {}, "inert", before) == output
    bad = copy.deepcopy(output)
    bad["family_record"]["durable_application_writes"] = 99
    monkeypatch.setattr(recovery, "run", lambda *a, **kw: __import__("json").dumps(bad))
    with pytest.raises(RuntimeError, match="NATIVE_SEED_FAMILY_INVALID"):
        recovery._native_seed("unused", {}, "inert", before)
    extra = {**output, "unreviewed": True}
    monkeypatch.setattr(recovery, "run", lambda *a, **kw: __import__("json").dumps(extra))
    with pytest.raises(RuntimeError, match="NATIVE_SEED_STATE_INVALID"):
        recovery._native_seed("unused", {}, "inert", before)
