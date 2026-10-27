"""AM3 exact read-only retained state gate; no seed or write connection."""
from __future__ import annotations

from collections.abc import Callable

from p5a2_source_demo_common import ROOT, fail
from p5a2_source_demo_recovery_inventory import expected_tables

FINGERPRINT = "afeb7f5ca42aec45a1bdc9f8a6d10c7401a401c080ce4b6097279badb3cadca9"
SCHEMA_DIGEST = "d1b13a0a45bad4c3607e5fbdb6439082df6f4b1ff3cd2f90398d4d0c228716db"
STATE_DIGEST = "d9418536c37fadc684a73ecfb2d2c67199bae29dfe5f43db5f12239b4ad8518b"
DATABASE = "shiftops_p5a2_source_demo"
POSTGRESQL_VERSION = ("PostgreSQL 16.15 on x86_64-pc-linux-musl, compiled by "
                      "gcc (Alpine 15.2.0) 15.2.0, 64-bit")
FROZEN_CREATED_AT = "2025-12-31T20:00:00+00:00"
TARGET = {"users": 1, "shifts": 36, "shift_assignments": 36, "reports": 37}
BEFORE_KEYS = {"database", "postgresql_major", "postgresql_version",
               "transaction_isolation", "transaction_read_only",
               "db_fingerprint", "schema_table_count", "schema_digest",
               "table_names", "counts", "classification", "state_digest",
               "observed_created_at"}
AFTER_KEYS = {"database", "postgresql_major", "postgresql_version",
              "transaction_isolation", "transaction_read_only",
              "db_fingerprint", "schema_digest", "counts", "state_digest",
              "record_classification"}


def _exact_counts(value: object, names: frozenset[str]) -> bool:
    return (type(value) is dict and set(value) == names
            and all(type(count) is int and count == TARGET.get(name, 0)
                    for name, count in value.items()))


def _shared(value: dict, names: frozenset[str]) -> bool:
    return (value.get("database") == DATABASE
            and type(value.get("postgresql_major")) is int
            and value["postgresql_major"] == 16
            and value.get("postgresql_version") == POSTGRESQL_VERSION
            and value.get("transaction_isolation") == "repeatable read"
            and value.get("transaction_read_only") == "on"
            and value.get("db_fingerprint") == FINGERPRINT
            and value.get("schema_digest") == SCHEMA_DIGEST
            and value.get("state_digest") == STATE_DIGEST
            and _exact_counts(value.get("counts"), names))


def verify_only(before: dict, post_summary: Callable[[], dict]) -> tuple[dict, dict]:
    """Call post-summary only after the first full exact RR/RO snapshot passes."""
    names = expected_tables()
    if (type(before) is not dict or set(before) != BEFORE_KEYS
            or not _shared(before, names)
            or before.get("classification") != "EXACT_SEEDED"
            or type(before.get("schema_table_count")) is not int
            or before["schema_table_count"] != 31
            or type(before.get("table_names")) is not list
            or before["table_names"] != sorted(names)
            or before.get("observed_created_at") != FROZEN_CREATED_AT):
        raise fail("VERIFY_PRESTATE_INVALID")
    after = post_summary()
    if (type(after) is not dict or set(after) != AFTER_KEYS
            or not _shared(after, names)
            or after.get("record_classification") != "EXACT_SEEDED"):
        raise fail("VERIFY_POSTSTATE_INVALID")

    # Reuse the already registered seed-recovery outcome adapter. Importing
    # its pure emitter never invokes the native seed transaction.
    from workspace_api.demo.seed_recovery import family_record
    from invariant_family_contract import load_json_no_dup, matches_shape_exactly

    record = family_record("VERIFY", FINGERPRINT)
    matrix = load_json_no_dup(ROOT / "docs/cvf/invariants/p5a2-demo-seed-recovery.json")
    shapes = [shape for outcome in matrix["outcomes"]
              if outcome["outcomeId"] == "EXACT_VERIFIED"
              for shape in outcome["shapes"]]
    if len(shapes) != 1 or not matches_shape_exactly(shapes[0], record, matrix):
        raise fail("VERIFY_FAMILY_INVALID")
    receipt = {"result": "VERIFY", "state_digest": STATE_DIGEST,
               "db_fingerprint": FINGERPRINT, "family_record": record}
    return receipt, after
