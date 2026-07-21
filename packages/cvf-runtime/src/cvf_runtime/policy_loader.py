"""Loads the CVF application profile from YAML and caches it.

This is the bridge the EA review found missing: the ``cvf-application-profile``
YAML files existed but no code read them. Every gate in this package resolves
its rules through :func:`load_profile`, so policy lives in one governed place
instead of being hard-coded per handler.

Fail-closed: if a required policy file is missing or unreadable, loading raises
:class:`CvfDenied` rather than silently defaulting to permissive behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from cvf_runtime.errors import CvfDenied

# Files that make up the profile. Keys are the logical names gates ask for.
_PROFILE_FILES: dict[str, str] = {
    "profile": "profile.yaml",
    "risk_classes": "risk-classes.yaml",
    "approval": "approval-policy.yaml",
    "evidence": "evidence-policy.yaml",
    "domain_lock": "domain-lock.yaml",
    "data": "data-policy.yaml",
    "cost": "cost-policy.yaml",
    "termination": "termination-policy.yaml",
}


def _default_profile_dir() -> Path:
    """Resolve ``packages/cvf-application-profile`` relative to this file.

    packages/cvf-runtime/src/cvf_runtime/policy_loader.py -> up 4 -> packages/
    """
    return Path(__file__).resolve().parents[3] / "cvf-application-profile"


@dataclass(frozen=True)
class CvfProfile:
    """Parsed, in-memory view of the CVF application profile."""

    profile: dict[str, Any]
    risk_classes: dict[str, Any]
    approval: dict[str, Any]
    evidence: dict[str, Any]
    domain_lock: dict[str, Any]
    data: dict[str, Any]
    cost: dict[str, Any]
    termination: dict[str, Any]

    @property
    def required_controls(self) -> list[str]:
        return list(self.profile.get("required_controls", []))


def _read_yaml(path: Path, logical_name: str) -> dict[str, Any]:
    if not path.is_file():
        raise CvfDenied(
            control="policy",
            reason=f"CVF profile file missing: {logical_name} ({path.name})",
            http_status=500,
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise CvfDenied(
            control="policy",
            reason=f"CVF profile file unreadable: {logical_name}: {exc}",
            http_status=500,
        ) from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise CvfDenied(
            control="policy",
            reason=f"CVF profile file must be a mapping: {logical_name}",
            http_status=500,
        )
    return data


@lru_cache(maxsize=4)
def load_profile(profile_dir: str | None = None) -> CvfProfile:
    """Load and cache the CVF application profile.

    ``profile_dir`` is accepted mainly so tests can point at a fixture profile.
    Results are cached per directory; call :func:`reset_cache` if the underlying
    files change within a process.
    """
    base = Path(profile_dir) if profile_dir else _default_profile_dir()
    loaded = {key: _read_yaml(base / fname, key) for key, fname in _PROFILE_FILES.items()}
    return CvfProfile(**loaded)


def reset_cache() -> None:
    """Clear the profile cache (used by tests that swap the profile dir)."""
    load_profile.cache_clear()
