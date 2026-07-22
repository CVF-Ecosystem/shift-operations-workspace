"""Schema parity guard, part 3: users.role column-level CHECK (P2-B).

Split into its own module rather than folding into
test_schema_parity_types_and_checks.py's `_COLUMN_LEVEL_STATUS_CHECK_TABLES`
machinery: that helper's regex and value-extraction are hardcoded to a
`status` column with UPPERCASE values (see
_migration_status_check_values/_code_status_check_values in that file).
users.role is a different column name with lowercase values (matching
cvf_runtime.identity.KNOWN_ROLES), so this mirrors the same two-directional
comparison technique with its own small, column-name-correct helpers instead
of overloading the status-specific ones.
"""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint

from operations_ledger.tables import users

from _schema_parity_parsing import migration_text, table_block


def _migration_role_check_values(block: str) -> set[str]:
    m = re.search(r"role\s+text[^,]*CHECK\s*\(role IN \(([^)]+)\)\)", block, re.IGNORECASE)
    assert m, "users: expected a column-level role CHECK (role IN (...)) in migration"
    return {v.strip().strip("'") for v in m.group(1).split(",")}


def _code_role_check_values() -> set[str]:
    code_checks = [c for c in users.constraints if isinstance(c, CheckConstraint)]
    assert code_checks, "users: tables.py has no CheckConstraint"
    code_text = " ".join(str(c.sqltext) for c in code_checks)
    return set(re.findall(r"'([a-z_]+)'", code_text))


def test_users_role_check_matches_two_directionally():
    sql = migration_text()
    block = table_block(sql, "users")

    migration_values = _migration_role_check_values(block)
    code_values = _code_role_check_values()

    missing_from_code = migration_values - code_values
    assert not missing_from_code, (
        f"users: migration role CHECK allows {sorted(missing_from_code)} that "
        f"tables.py's CheckConstraint text does not mention"
    )
    missing_from_migration = code_values - migration_values
    assert not missing_from_migration, (
        f"users: tables.py's CheckConstraint mentions "
        f"{sorted(missing_from_migration)} that the migration's role CHECK "
        f"does not allow"
    )

    # Also matches the role vocabulary permission.py/identity.py already
    # enforce downstream of Principal, so a role accepted at the DB layer
    # cannot be one Principal/require_action would reject.
    from cvf_runtime.identity import KNOWN_ROLES

    assert migration_values == set(KNOWN_ROLES), (
        f"users.role CHECK values {sorted(migration_values)} must match "
        f"cvf_runtime.identity.KNOWN_ROLES {sorted(KNOWN_ROLES)} exactly"
    )
