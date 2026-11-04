"""Trusted source roots for isolated standalone P5-A2 demo children."""
from __future__ import annotations

import os
from pathlib import Path

from p5a2_source_demo_common import ROOT, child_env, fail

# Explicit local source roots. Pytest's separate pythonpath setting is not a
# standalone launch contract; no path is inherited from the caller.
SOURCE_ROOTS = (
    "apps/workspace-api/src",
    "apps/workspace-worker/src",
    "apps/integration-edge/src",
    "packages/identity-mapping/src",
    "packages/conversation-routing/src",
    "packages/channel-sdk/src",
    "packages/channel-adapters/src",
    "packages/application-memory/src",
    "packages/cvf-runtime/src",
    "packages/operations-ledger/src",
    "packages/operations-domain/src",
    "packages/refinery-bridge/src",
    "packages/retrieval-contracts/src",
    "packages/governed-retrieval/src",
    "packages/ai-gateway/src",
    "packages/governed-rag/src",
    "packages/ai-providers/src",
    "packages/reporting-engine/src",
)


def source_path(root: Path = ROOT) -> str:
    resolved = root.resolve()
    paths = []
    for relative in SOURCE_ROOTS:
        path = (resolved / relative).resolve()
        if not path.is_dir() or not path.is_relative_to(resolved):
            raise fail("SOURCE_ROOT_INVALID")
        paths.append(str(path))
    return os.pathsep.join(paths)


def isolated_child_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    if extra and any(key in extra for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE")):
        raise fail("SOURCE_PATH_OVERRIDE")
    env = child_env(extra)
    env.update({"PYTHONPATH": source_path(), "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1"})
    return env
