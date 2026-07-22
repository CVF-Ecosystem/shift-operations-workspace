#!/usr/bin/env python3
"""Seed a fixed set of dev/test users (P2-B: real authentication).

NOT for production: passwords here are fixed, printed to stdout, and
intentionally weak. Production user provisioning is out of scope for this
tranche and remains a follow-up - see the P2-B entry in
docs/implementation/EXECUTION_ROADMAP.md.

Reuses the same ids/roles already used in
packages/cvf-application-profile/known-principals.yaml so dev/test fixtures
stay legible across both registries - they remain independent stores; this
script does not read or write that YAML file.

Requires JWT_SECRET_KEY (and, to persist across process runs, DATABASE_URL)
to already be set in the environment, same as running the API itself.

Usage:
    python scripts/seed_dev_users.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for rel in (
    "apps/workspace-api/src",
    "packages/cvf-runtime/src",
    "packages/operations-ledger/src",
):
    sys.path.insert(0, str(REPO_ROOT / rel))

from workspace_api.auth.passwords import hash_password  # noqa: E402
from workspace_api.domain.models import User  # noqa: E402
from workspace_api.infrastructure.ledger_factory import build_ledger  # noqa: E402

# (user_id, role) pairs. username == user_id for legibility. Dev-only
# password: "<user_id>-devpass" - change immediately if used past a local
# dev/test environment.
_DEV_USERS = [
    ("op1", "operator"),
    ("sup1", "shift_supervisor"),
    ("sup2", "shift_supervisor"),
    ("sup3", "shift_supervisor"),
    ("mgr1", "responsible_manager"),
    ("mgr2", "responsible_manager"),
    ("exec1", "authorized_executive"),
    ("v1", "viewer"),
]


def main() -> None:
    ledger = build_ledger()
    for user_id, role in _DEV_USERS:
        if ledger.get_user_by_username(user_id) is not None:
            print(f"skip {user_id}: already exists")
            continue
        password = f"{user_id}-devpass"
        ledger.add_user(
            User(
                user_id=user_id,
                username=user_id,
                password_hash=hash_password(password),
                role=role,
            )
        )
        print(f"created {user_id} (role={role}, password={password!r} - DEV ONLY)")


if __name__ == "__main__":
    main()
