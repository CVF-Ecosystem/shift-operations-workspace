"""XR1-S-C2b reciprocal workspace-link contract tests (R-16 through R-23)."""

from __future__ import annotations

import copy
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DESCRIPTOR_PATH = REPO_ROOT / ".cvf" / "workspace-link.json"
OPERATIONS_ROOT = REPO_ROOT.parent / "CVF-Operations-Workspace"
OPERATIONS_AUTHORIZATION_COMMIT = "f99b3bf916985572e633275311a11aef4bd3aabf"
OPERATIONS_ADR = "docs/decisions/ADR_2026-07-24_XR1_TWO_REPOSITORY_LINK_AND_REFRESH.md"

TOP_LEVEL_FIELDS = {
    "schemaVersion",
    "workspaceId",
    "thisRepo",
    "peerRepo",
    "relationshipDirection",
}
REPO_FIELDS = {"repoId", "role", "remote"}
ROLE_COMPLEMENTS = {
    "PROFILE_SOURCE": "PRIMARY_PLATFORM",
    "PRIMARY_PLATFORM": "PROFILE_SOURCE",
}
EXPECTED = {
    "schemaVersion": "1.0",
    "workspaceId": "cvf-operations-workspace",
    "thisRepo": {
        "repoId": "shift-operations-workspace",
        "role": "PROFILE_SOURCE",
        "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git",
    },
    "peerRepo": {
        "repoId": "cvf-operations-workspace",
        "role": "PRIMARY_PLATFORM",
        "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git",
    },
    "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
}


def _load_descriptor() -> dict:
    return json.loads(DESCRIPTOR_PATH.read_text(encoding="utf-8"))


def _all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _validate_descriptor(data: object) -> None:
    if not isinstance(data, dict):
        raise ValueError("descriptor must be an object")
    if set(data) != TOP_LEVEL_FIELDS:
        raise ValueError("descriptor has missing or unknown fields")
    if data["schemaVersion"] != "1.0":
        raise ValueError("wrong schemaVersion")
    if data["workspaceId"] != EXPECTED["workspaceId"]:
        raise ValueError("wrong workspaceId")
    if data["relationshipDirection"] != EXPECTED["relationshipDirection"]:
        raise ValueError("wrong relationshipDirection")

    for side in ("thisRepo", "peerRepo"):
        repo = data[side]
        if not isinstance(repo, dict) or set(repo) != REPO_FIELDS:
            raise ValueError(f"{side} must have the exact repository fields")
        if repo != EXPECTED[side]:
            raise ValueError(f"wrong {side} value")

    this_role = data["thisRepo"]["role"]
    peer_role = data["peerRepo"]["role"]
    if ROLE_COMPLEMENTS.get(this_role) != peer_role:
        raise ValueError("repository roles are not complementary")

    forbidden_acceptance_fields = {
        "sourcePin",
        "pinUpdatePolicy",
        "acceptedCommit",
        "acceptedSourceCommit",
        "consumerAcceptance",
    }
    if forbidden_acceptance_fields.intersection(data):
        raise ValueError("consumer acceptance state is forbidden")

    local_patterns = (
        re.compile(r"^[A-Za-z]:[\\/]"),
        re.compile(r"^\\\\"),
        re.compile(r"^/(?:home|Users|tmp|var|opt)/"),
        re.compile(r"^file://", re.IGNORECASE),
        re.compile(r"(?:^|[/.])localhost(?:$|[/:])", re.IGNORECASE),
        re.compile(r"(?:^|[/.])127\.0\.0\.1(?:$|[/:])"),
        re.compile(r"<[^>]*(?:path|host|user)[^>]*>", re.IGNORECASE),
    )
    for value in _all_strings(data):
        if any(pattern.search(value) for pattern in local_patterns):
            raise ValueError("machine-local path, host, username, or placeholder")


def _run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout


def _operations_contract_at_authorized_commit() -> dict:
    adr = _run_git(
        OPERATIONS_ROOT,
        "show",
        f"{OPERATIONS_AUTHORIZATION_COMMIT}:{OPERATIONS_ADR}",
    )
    marker = '"schemaVersion": "1.0"'
    marker_index = adr.index(marker)
    block_start = adr.rfind("{", 0, marker_index)
    block_end = adr.index("\n  }\n  ```", marker_index) + len("\n  }")
    return json.loads(adr[block_start:block_end])


def test_descriptor_has_exact_authorized_shape_and_literals():
    data = _load_descriptor()
    _validate_descriptor(data)
    assert set(data) == TOP_LEVEL_FIELDS
    assert data == EXPECTED


def test_roles_are_recognized_complements():
    data = _load_descriptor()
    assert ROLE_COMPLEMENTS[data["thisRepo"]["role"]] == data["peerRepo"]["role"]
    assert ROLE_COMPLEMENTS[data["peerRepo"]["role"]] == data["thisRepo"]["role"]


def test_descriptor_has_no_consumer_acceptance_state():
    data = _load_descriptor()
    assert "sourcePin" not in data
    assert "pinUpdatePolicy" not in data
    assert not any("accept" in field.lower() for field in data)


def test_descriptor_contains_no_machine_local_value():
    data = _load_descriptor()
    _validate_descriptor(data)
    assert all("<" not in value and ">" not in value for value in _all_strings(data))


def test_peer_is_discoverable_from_peer_repo_alone():
    peer = _load_descriptor()["peerRepo"]
    assert peer == {
        "repoId": "cvf-operations-workspace",
        "role": "PRIMARY_PLATFORM",
        "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git",
    }


def test_fresh_clone_simulation_preserves_identical_bytes(tmp_path: Path):
    original = DESCRIPTOR_PATH.read_bytes()
    clone_path = tmp_path / "fresh-clone" / ".cvf" / "workspace-link.json"
    clone_path.parent.mkdir(parents=True)
    clone_path.write_bytes(original)
    assert clone_path.read_bytes() == original
    assert json.loads(clone_path.read_text(encoding="utf-8")) == EXPECTED


def test_operations_authorized_contract_is_reciprocal_when_sibling_present():
    if not (OPERATIONS_ROOT / ".git").exists():
        pytest.skip("CVF-Operations-Workspace sibling clone is not present")

    commit_type = _run_git(
        OPERATIONS_ROOT,
        "cat-file",
        "-t",
        OPERATIONS_AUTHORIZATION_COMMIT,
    ).strip()
    assert commit_type == "commit"
    operations = _operations_contract_at_authorized_commit()
    shift = _load_descriptor()

    assert operations["workspaceId"] == shift["workspaceId"]
    assert operations["relationshipDirection"] == shift["relationshipDirection"]
    assert operations["thisRepo"] == shift["peerRepo"]
    assert operations["peerRepo"] == shift["thisRepo"]
    assert ROLE_COMPLEMENTS[operations["thisRepo"]["role"]] == shift["thisRepo"]["role"]


def _mutate(case: str) -> object:
    data = copy.deepcopy(EXPECTED)
    if case == "malformed-field-type":
        data["thisRepo"] = []
    elif case == "extra-field":
        data["unexpected"] = True
    elif case == "wrong-role":
        data["peerRepo"]["role"] = "PROFILE_SOURCE"
    elif case == "wrong-direction":
        data["relationshipDirection"] = "OPERATIONS_TO_SHIFT"
    elif case == "wrong-remote":
        data["peerRepo"]["remote"] = "https://example.invalid/peer.git"
    elif case == "wrong-workspace":
        data["workspaceId"] = "another-workspace"
    elif case == "absolute-local-path":
        data["peerRepo"]["remote"] = r"C:\local\CVF-Operations-Workspace"
    else:  # pragma: no cover - guards the test table itself
        raise AssertionError(f"unknown mutation case: {case}")
    return data


@pytest.mark.parametrize(
    "case",
    [
        "malformed-field-type",
        "extra-field",
        "wrong-role",
        "wrong-direction",
        "wrong-remote",
        "wrong-workspace",
        "absolute-local-path",
    ],
)
def test_negative_descriptor_cases_fail_closed(case: str):
    with pytest.raises(ValueError):
        _validate_descriptor(_mutate(case))
