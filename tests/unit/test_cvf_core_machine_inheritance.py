from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPT))
import _cvf_core_binding as binding  # noqa: E402

SPEC = importlib.util.spec_from_file_location("check_cvf_core_machine_inheritance", SCRIPT / "check_cvf_core_machine_inheritance.py")
guard = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(guard)


def test_current_installed_core_binding() -> None:
    assert binding.verify_binding(guard.PROJECT_ROOT).is_file()


def test_native_cli_preserves_flags_and_exit(monkeypatch) -> None:
    checker = Path("C:/pinned/core/checker.py")
    monkeypatch.setattr(guard, "verify_binding", lambda _root: checker)
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(guard.subprocess, "run", run)
    monkeypatch.setattr(sys, "argv", ["guard", "--base", "abc", "--head", "def", "--enforce"])
    assert guard.main() == 7
    command, kwargs = calls[0]
    assert command == [sys.executable, "-I", str(checker), "--repo-root", str(guard.PROJECT_ROOT), "--base", "abc", "--head", "def", "--enforce"]
    assert kwargs["cwd"] == guard.PROJECT_ROOT


def test_invalid_binding_fails_even_without_enforce(monkeypatch) -> None:
    def invalid(_root):
        raise ValueError("bad pin")

    monkeypatch.setattr(guard, "verify_binding", invalid)
    monkeypatch.setattr(sys, "argv", ["guard"])
    assert guard.main() == 2


def test_native_core_cli_rejects_invalid_active_packet(tmp_path: Path) -> None:
    project = tmp_path / "project"
    packet = project / "docs" / "work_orders" / "INVALID.md"
    packet.parent.mkdir(parents=True)
    packet.write_text("Status: APPROVED_FOR_EXECUTION\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(["git", "-C", str(project), "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture", "commit", "-q", "--allow-empty", "-m", "baseline"], check=True)
    checker = binding.verify_binding(guard.PROJECT_ROOT)
    result = subprocess.run(
        [sys.executable, "-I", str(checker), "--repo-root", str(project), "--enforce"],
        cwd=guard.PROJECT_ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert "contract_missing" in result.stdout


def test_native_core_cli_rejects_invalid_self_declared_return(tmp_path: Path) -> None:
    project = tmp_path / "project"
    packet = project / "docs" / "reviews" / "INVALID.md"
    packet.parent.mkdir(parents=True)
    packet.write_text(
        "Status: COMPLETE_PENDING_REVIEW\nSelf-declared worker-return artifact: yes\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(["git", "-C", str(project), "-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture", "commit", "-q", "--allow-empty", "-m", "baseline"], check=True)
    checker = binding.verify_binding(guard.PROJECT_ROOT)
    result = subprocess.run(
        [sys.executable, "-I", str(checker), "--repo-root", str(project), "--enforce"],
        cwd=guard.PROJECT_ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert "return_recheck_missing" in result.stdout


def test_own_return_has_anchored_native_applicability_and_valid_recheck() -> None:
    source = guard.PROJECT_ROOT / "docs" / "decisions" / "P5A2_CORE_ONLY_BINDING_WORKER_RETURN_2026-10-26.md"
    content = source.read_text(encoding="utf-8")
    assert re.search(r"(?mi)^Self-declared worker-return artifact:\s*yes\s*$", content)
    checker = binding.verify_binding(guard.PROJECT_ROOT)
    spec = importlib.util.spec_from_file_location("pinned_core_closeability", checker)
    assert spec and spec.loader
    native = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = native
    spec.loader.exec_module(native)
    assert native.check_recheck("docs/decisions/P5A2_CORE_ONLY_BINDING_WORKER_RETURN_2026-10-26.md", content) == []
