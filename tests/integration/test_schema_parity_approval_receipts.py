"""Schema parity: approval_receipts UNIQUE constraint.

Split out of test_schema_parity.py (CVF-FILE-SPLIT-GUARD-HARDENING) purely to
respect the file-size guard - not a behavior change. Shares parsing helpers
from _schema_parity_parsing.py, same as every sibling schema-parity module.
"""

from __future__ import annotations

import re

from sqlalchemy import UniqueConstraint

from operations_ledger.tables import approval_receipts

from _schema_parity_parsing import migration_text, table_block


def test_approval_receipts_unique_constraint_matches_migration():
    """P2B-APPROVER-IDENTITY-RECONCILIATION, AC-13: the receipt idempotency
    key (SPEC R2.4/R8.1) must exist identically on both sides - a migration
    UNIQUE the tables.py UniqueConstraint doesn't mirror would let SQLite
    accept a duplicate receipt row a real PostgreSQL database would reject."""
    sql = migration_text()
    block = table_block(sql, "approval_receipts")
    migration_unique = re.search(
        r"UNIQUE\s*\(([^)]+)\)", block, re.IGNORECASE
    )
    assert migration_unique, "approval_receipts: expected a table-level UNIQUE in the migration"
    migration_cols = {c.strip() for c in migration_unique.group(1).split(",")}

    code_unique_constraints = [
        c for c in approval_receipts.constraints if isinstance(c, UniqueConstraint)
    ]
    assert code_unique_constraints, "approval_receipts: tables.py has no UniqueConstraint"
    code_cols = {col.name for col in code_unique_constraints[0].columns}

    assert migration_cols == code_cols, (
        f"approval_receipts: UNIQUE column set mismatch - migration has "
        f"{sorted(migration_cols)}, tables.py has {sorted(code_cols)}"
    )
    assert migration_cols == {
        "record_type", "record_id", "action", "target_version", "approver_id",
    }
