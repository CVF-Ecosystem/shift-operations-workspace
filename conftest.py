"""Session-wide pytest bootstrap.

P2-B (2026-07-22): ``workspace_api.config.Settings`` now requires
``JWT_SECRET_KEY`` with no default (fail-closed, see config.py). This runs
before pytest imports any test module - including modules that transitively
import ``workspace_api.config`` at collection time - so the test suite never
depends on a developer's local ``.env`` existing. Not a real secret: test-only,
never used outside this process.
"""

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")
