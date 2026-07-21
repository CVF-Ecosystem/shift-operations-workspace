from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
_SKIP_PARTS = {".venv", "node_modules", ".pytest_cache", "__pycache__", ".git", "dist", "build"}
errors = []

for item in root.rglob("*"):
    if any(part in _SKIP_PARTS for part in item.relative_to(root).parts):
        continue
    if item.is_file() and item.stat().st_size == 0 and item.name != "__init__.py":
        errors.append(f"empty: {item.relative_to(root)}")

for item in (root / "packages" / "workspace-contracts").rglob("*.json"):
    try:
        json.loads(item.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"json: {item.relative_to(root)}: {exc}")

required = [
    "README.md",
    "TREEVIEW.md",
    "CONTRIBUTING.md",
    "docs/implementation/IMPLEMENTATION_PHASES.md",
    "packages/cvf-application-profile/profile.yaml",
    "docs/catalog/MODULE_REGISTRY.json",
    "docs/catalog/MODULE_CATALOG.md",
    "scripts/generate_catalog.py",
    "SESSION/ACTIVE_SESSION_STATE.json",
    "SESSION/SESSION_MEMORY.md",
    "scripts/check_session_state.py",
    "scripts/check_file_size.py",
    "docs/reference/FILE_SIZE_GUARD.md",
]
for rel in required:
    if not (root / rel).exists():
        errors.append(f"missing: {rel}")

# Module catalog must stay consistent (paths exist, statuses/controls valid).
# This is the automated gate that forces the catalog to be updated whenever a
# module is added or its status changes.
catalog_check = subprocess.run(
    [sys.executable, str(root / "scripts" / "generate_catalog.py"), "--check"],
    capture_output=True,
    text=True,
)
if catalog_check.returncode != 0:
    errors.append("catalog: MODULE_REGISTRY.json failed --check")
    errors.append(catalog_check.stdout.strip())
    errors.append(catalog_check.stderr.strip())

# Session state must stay consistent (active handoff exists, required reads
# exist, next move + guardrails recorded). Forces handoffs to be updated.
session_check = subprocess.run(
    [sys.executable, str(root / "scripts" / "check_session_state.py")],
    capture_output=True,
    text=True,
)
if session_check.returncode != 0:
    errors.append("session: ACTIVE_SESSION_STATE.json failed check")
    errors.append(session_check.stdout.strip())
    errors.append(session_check.stderr.strip())

# File size guard: keep files from silently growing into technical debt.
size_check = subprocess.run(
    [sys.executable, str(root / "scripts" / "check_file_size.py")],
    capture_output=True,
    text=True,
)
if size_check.returncode != 0:
    errors.append("file-size: guard failed")
    errors.append(size_check.stdout.strip())
    errors.append(size_check.stderr.strip())

if errors:
    raise SystemExit("\n".join(e for e in errors if e))
print("repository validation passed (catalog + session state + file-size checks)")
