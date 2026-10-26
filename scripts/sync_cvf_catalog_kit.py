#!/usr/bin/env python3
"""Project-owned projection from the detailed module catalog to CVF kit v1.1.

The detailed registry remains the source for module status, evidence and metrics.
This projection preserves all module IDs and rejects missing source evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DETAIL = ROOT / "docs/catalog/MODULE_REGISTRY_DETAIL.json"
KIT = ROOT / "docs/catalog/MODULE_REGISTRY.json"
STATUS = {
    "enforced": "ENFORCED",
    "partial": "PARTIAL",
    "contract-only": "CONTRACT_ONLY",
    "stub": "STUB",
}


def source_evidence(module: dict) -> str:
    for candidate in module.get("tests", []):
        if (ROOT / candidate).is_file():
            return candidate
    path = ROOT / module["path"]
    if module["status"] == "partial":
        suffixes = {".py", ".ts", ".tsx"}
    elif module["status"] == "contract-only":
        suffixes = {".json", ".yaml", ".yml", ".py", ".ts"}
    else:
        suffixes = {".md", ".py", ".ts", ".json", ".yaml"}
    for candidate in sorted(path.rglob("*")):
        if candidate.is_file() and candidate.suffix in suffixes:
            return candidate.relative_to(ROOT).as_posix()
    raise ValueError(f"{module['id']}: no source evidence for {module['status']}")


def project(detail: dict, updated_at: str) -> dict:
    modules = []
    for module in detail["modules"]:
        status = STATUS[module["status"]]
        evidence = source_evidence(module)
        description = " ".join(module["purpose"].split()).replace("|", "/")
        modules.append({
            "id": module["id"],
            "name": module["id"],
            "path": module["path"],
            "status": status,
            "description": description,
            "evidence": evidence,
            "dependencies": [dep for dep in module.get("depends_on", [])],
        })
    return {
        "schemaVersion": "1.0",
        "projectName": "shift-operations-workspace",
        "updatedAt": updated_at,
        "claimBoundary": "Projection of source-verified legacy module records; detailed registry retains control mapping and size metrics. Status is scoped to each module, not application readiness.",
        "modules": modules,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    detail = json.loads(DETAIL.read_text(encoding="utf-8-sig"))
    prior = json.loads(KIT.read_text(encoding="utf-8-sig")) if KIT.exists() else None
    updated_at = prior["updatedAt"] if prior and "updatedAt" in prior else "2026-09-26"
    expected = project(detail, updated_at)
    if args.write:
        KIT.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"CVF KIT PROJECTION: wrote {len(expected['modules'])} modules")
        return 0
    if prior != expected:
        print("CVF KIT PROJECTION: FAIL (run --write, then catalog manager -Write)")
        return 1
    print(f"CVF KIT PROJECTION: PASS ({len(expected['modules'])} modules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
