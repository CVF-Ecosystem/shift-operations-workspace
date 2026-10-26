"""Detailed module catalog Markdown renderer."""

def render_markdown(registry: dict) -> str:
    totals = registry["metrics"]["totals"]
    gen = registry["metrics"]["generated_at"]
    lines: list[str] = []
    lines.append("# Module Catalog")
    lines.append("")
    lines.append(
        "> GENERATED FILE — do not edit by hand. Source of truth is "
        "[`MODULE_REGISTRY_DETAIL.json`](MODULE_REGISTRY_DETAIL.json). "
        "Run `python scripts/generate_catalog.py --write` to regenerate."
    )
    lines.append("")
    lines.append(f"_Last generated: {gen}_")
    lines.append("")
    lines.append("## How to use this catalog")
    lines.append("")
    lines.append(
        "- **Before working:** find the module you will touch and read its "
        "`purpose`, `status`, `cvf_controls`, and `enforcement`."
    )
    lines.append(
        "- **After completing a piece:** update that module's entry in "
        "`MODULE_REGISTRY_DETAIL.json` (status, enforcement, next_step, tests), then "
        "run the generator to refresh this file and the metrics."
    )
    lines.append(
        "- **Size metrics are computed**, not written — they cannot lie about "
        "how much code exists."
    )
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append(f"- Modules: **{totals['modules']}**")
    lines.append(f"- Code LOC (py/ts/tsx): **{totals['code_loc']}**")
    lines.append(f"- Code files: **{totals['code_files']}**")
    by_status = ", ".join(f"{k}={v}" for k, v in totals["by_status"].items())
    lines.append(f"- By status: {by_status}")
    lines.append("")
    lines.append("## Status legend")
    lines.append("")
    for k, v in registry["status_legend"].items():
        lines.append(f"- **{k}** — {v}")
    lines.append("")
    lines.append("## Modules")
    lines.append("")
    lines.append("| Module | Path | Status | LOC | CVF controls | Purpose |")
    lines.append("|---|---|---|---:|---|---|")
    for mod in sorted(registry["modules"], key=_status_sort_key):
        ctrls = ", ".join(mod["cvf_controls"]) or "—"
        loc = mod["metrics"]["loc"]
        purpose = mod["purpose"].replace("|", "\\|")
        lines.append(
            f"| `{mod['id']}` | {mod['path']} | {mod['status']} | {loc} | "
            f"{ctrls} | {purpose} |"
        )
    lines.append("")
    lines.append("## Per-module detail")
    lines.append("")
    for mod in sorted(registry["modules"], key=_status_sort_key):
        lines.append(f"### `{mod['id']}` — {mod['status']}")
        lines.append("")
        lines.append(f"- **Path:** `{mod['path']}` ({mod['kind']})")
        lines.append(f"- **Purpose:** {mod['purpose']}")
        lines.append(f"- **CVF controls:** {', '.join(mod['cvf_controls']) or '—'}")
        lines.append(f"- **Enforcement:** {mod['enforcement']}")
        lines.append(f"- **Contract:** {mod.get('contract', '—')}")
        deps = ", ".join(f"`{d}`" for d in mod.get("depends_on", [])) or "—"
        lines.append(f"- **Depends on:** {deps}")
        tests = ", ".join(f"`{t}`" for t in mod.get("tests", [])) or "—"
        lines.append(f"- **Tests:** {tests}")
        lines.append(
            f"- **Metrics:** {mod['metrics']['loc']} LOC across "
            f"{mod['metrics']['code_files']} code file(s)"
        )
        lines.append(f"- **Next step:** {mod.get('next_step', '—')}")
        lines.append("")
    lines.append("## Related")
    lines.append("")
    lines.append(
        "- CVF control enforcement points: "
        "[`docs/cvf/CVF_CONTROL_MAPPING.md`](../cvf/CVF_CONTROL_MAPPING.md)"
    )
    lines.append("- Release/validation status: `IMPLEMENTATION_STATUS.json` (repo root)")
    lines.append("")
    return "\n".join(lines)


_STATUS_ORDER = {"enforced": 0, "partial": 1, "contract-only": 2, "stub": 3, "empty": 4}


def _status_sort_key(mod: dict):
    return (_STATUS_ORDER.get(mod["status"], 9), mod["id"])
