"""Deterministic, read-only validation for the local project knowledge pack."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote
ROOT = Path(__file__).resolve().parents[1]
DOCS = {"PROJECT_CONTEXT.md", "OPERATIONS_GLOSSARY.md", "GOVERNANCE_BOUNDARIES.md"}
MARKDOWN = DOCS | {"README.md"}
TOP_FIELDS = {"schemaVersion", "packId", "classification", "reviewedAt", "entries"}
ENTRY_FIELDS = {"id", "path", "owner", "classification", "disposition", "dispositionReason", "purpose", "allowedConsumers", "sourcePins", "reviewedAt", "refreshTriggers", "retentionPolicy", "correctionPolicy", "eligibleForLocalIndex"}
PIN_FIELDS = {"path", "sha256"}
OWNERS = {"ORCHESTRATOR", "SPEC_AUTHOR", "SESSION_SYNC_STEWARD"}
CONSUMERS = {"LOCAL_GOVERNED_AGENT", "HUMAN_OPERATOR"}
TRIGGERS = {"SOURCE_SHA256_CHANGE", "OWNER_WITHDRAWAL", "SECURITY_RECLASSIFICATION", "CONTINUITY_OR_BOOTSTRAP_CHANGE", "REVIEW_FINDING"}
DISPOSITION_CODES = {"OWNER_WITHDRAWN": "KPK_OWNER_WITHDRAWN", "SECURITY_RECLASSIFIED": "KPK_SECURITY_RECLASSIFIED", "REVIEW_BLOCKED": "KPK_REVIEW_BLOCKED"}
EXPECTED = {
    "PROJECT_CONTEXT.md": ("project-context", "ORCHESTRATOR", {"IMPLEMENTATION_STATUS.json", "docs/catalog/MODULE_REGISTRY.json", "docs/implementation/EXECUTION_ROADMAP.md"}),
    "OPERATIONS_GLOSSARY.md": ("operations-glossary", "SPEC_AUTHOR", {"packages/operations-domain/README.md", "packages/operations-domain/src/operations_domain/models.py", "packages/operations-domain/src/operations_domain/lifecycle.py", "packages/operations-domain/src/operations_domain/assignment_models.py", "packages/operations-domain/src/operations_domain/report_models.py", "packages/workspace-contracts/README.md"}),
    "GOVERNANCE_BOUNDARIES.md": ("governance-boundaries", "SESSION_SYNC_STEWARD", {"AGENTS.md", ".cvf/manifest.json", ".cvf/policy.json", "docs/cvf/CONTEXT_CONTROL.md", "docs/cvf/EVIDENCE_AND_TRUTH.md", "docs/cvf/PROVIDER_GOVERNANCE.md", "docs/cvf/RISK_AND_APPROVAL.md"}),
}
FORBIDDEN = {"automatically retrieve", "automatically inject", "enforcement will reject", "retrieval is implemented", "rag is implemented", "production ready"}
PEM_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
ASSIGN_RE = re.compile(r"^[ \t]*([A-Z][A-Z0-9_]*)[ \t]*[:=](.*)$", re.I | re.M)
VALUE_RE = re.compile(
    r"^[ \t]*(?:\"([^\"\r\n]*)\"|'([^'\r\n]*)'|([^\s\"'#]+))[ \t]*(?:#.*)?$"
)
URL_RE = re.compile(r"\b(?:https?|postgres(?:ql)?)://([^/\s:@]+):([^@\s/]+)@", re.I)
JWT_RE = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?![A-Za-z0-9_-])")
AWS_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
CITE_RE = re.compile(r"^Sources: (`[^`\r\n]+`)(; `[^`\r\n]+`)*$")
SENSITIVE_SUFFIXES = ("API_KEY", "ACCESS_KEY", "SECRET", "TOKEN", "PASSWORD")
PLACEHOLDERS = {"<redacted>", "<placeholder>", "example", "dummy"}
ENV_RE = re.compile(r"^\$\{[A-Z][A-Z0-9_]*\}$")
class DuplicateKey(ValueError): pass
@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    eligible: tuple[str, ...]
    @property
    def ok(self) -> bool:
        return not self.errors
def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result
def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def _read_utf8(path: Path) -> str | None:
    try: return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError): return None
def _valid_date(value: Any, today: date) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed <= today else None
def _placeholder(value: str) -> bool:
    return value.casefold() in PLACEHOLDERS or bool(ENV_RE.fullmatch(value))
def _exact_list(value: Any, expected: set[str]) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value) and len(value) == len(expected) and set(value) == expected
def secret_codes(text: str) -> set[str]:
    codes: set[str] = set()
    if PEM_RE.search(text):
        codes.add("KPK_SECRET_PEM")
    for match in ASSIGN_RE.finditer(text):
        if not match.group(1).upper().endswith(SENSITIVE_SUFFIXES):
            continue
        parsed = VALUE_RE.fullmatch(match.group(2))
        if parsed is None:
            codes.add("KPK_SECRET_ASSIGNMENT")
            continue
        values = [value for value in parsed.groups() if value is not None]
        if len(values) != 1 or not values[0] or not _placeholder(values[0]):
            codes.add("KPK_SECRET_ASSIGNMENT")
    for match in URL_RE.finditer(text):
        if not (_placeholder(unquote(match.group(1))) and _placeholder(unquote(match.group(2)))):
            codes.add("KPK_SECRET_URL")
    if JWT_RE.search(text):
        codes.add("KPK_SECRET_JWT")
    if AWS_RE.search(text):
        codes.add("KPK_SECRET_AWS")
    return codes
def _citations(text: str) -> tuple[set[str], bool]:
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    cited: set[str] = set()
    if not starts:
        return cited, False
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        body = [line for line in lines[start + 1:end] if line.strip()]
        if not body or not CITE_RE.fullmatch(body[-1]):
            return cited, False
        cited.update(re.findall(r"`([^`]+)`", body[-1]))
    return cited, True
def _safe_project_file(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or "\\" in relative or not relative:
        return None
    pure = Path(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    target = root.joinpath(*pure.parts)
    try:
        target.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError, OSError):
        return None
    if target.is_symlink() or not target.is_file():
        return None
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative],
        capture_output=True, text=True, check=False,
    )
    return target if tracked.returncode == 0 else None
def _continuity_errors(root: Path) -> list[str]:
    errors: list[str] = []
    check = subprocess.run(
        [sys.executable, str(root / "scripts/check_session_state.py")],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if check.returncode:
        errors.append("KPK_CONTINUITY_CHANGED:session")
    try:
        manifest = _load_json(root / ".cvf/manifest.json")
        policy = _load_json(root / ".cvf/policy.json")
        for field in ("liveGovernanceEvidenceRequired", "mockAllowedOnlyForUi"):
            if manifest.get(field) != policy.get(field):
                errors.append(f"KPK_CONTINUITY_CHANGED:{field}")
        if manifest.get("phaseModel") != [
            "INTAKE", "DESIGN", "SPEC", "WORK_ORDER", "BUILD", "REVIEW", "FREEZE"
        ]:
            errors.append("KPK_CONTINUITY_CHANGED:phaseModel")
    except (OSError, ValueError, json.JSONDecodeError, DuplicateKey):
        errors.append("KPK_CONTINUITY_CHANGED:policy")
    return errors
def validate_pack(
    project_root: Path = ROOT,
    knowledge_root: Path | None = None,
    today: date | None = None,
    check_continuity: bool = True,
) -> ValidationResult:
    root = project_root.resolve()
    knowledge = (knowledge_root or root / "knowledge").resolve()
    clock = today or datetime.now(timezone.utc).date()
    errors: list[str] = []
    eligible: list[str] = []
    found_md = {path.relative_to(knowledge).as_posix() for path in knowledge.rglob("*.md") if path.is_file()}
    if found_md != MARKDOWN:
        errors.append("KPK_MARKDOWN_SET:knowledge")
    if any(root.rglob("_index.json")) or (knowledge != root / "knowledge" and any(knowledge.rglob("_index.json"))):
        errors.append("KPK_INDEX_RESIDUE:repository")
    try:
        data = _load_json(knowledge / "manifest.json")
    except (OSError, ValueError, json.JSONDecodeError, DuplicateKey):
        return ValidationResult(("KPK_MANIFEST_JSON:manifest.json",), ())
    if not isinstance(data, dict) or set(data) != TOP_FIELDS:
        errors.append("KPK_MANIFEST_SCHEMA:manifest.json")
        return ValidationResult(tuple(sorted(set(errors))), ())
    if data.get("schemaVersion") != "1.0" or data.get("packId") != "shift-operations-project-knowledge" or data.get("classification") != "INTERNAL":
        errors.append("KPK_MANIFEST_METADATA:manifest.json")
    manifest_date = _valid_date(data.get("reviewedAt"), clock)
    if manifest_date is None:
        errors.append("KPK_DATE:manifest.json")
    entries = data.get("entries")
    if not isinstance(entries, list) or len(entries) != 3:
        errors.append("KPK_ENTRY_COUNT:manifest.json")
        return ValidationResult(tuple(sorted(set(errors))), ())
    seen_ids: set[str] = set(); seen_paths: set[str] = set()
    texts: dict[str, str] = {}
    for entry in entries:
        local: list[str] = []
        label = entry.get("path", "entry") if isinstance(entry, dict) else "entry"
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            errors.append(f"KPK_ENTRY_SCHEMA:{label}")
            continue
        path = entry["path"]
        expected = EXPECTED.get(path) if isinstance(path, str) else None
        entry_id = entry["id"]; id_key = entry_id if isinstance(entry_id, str) else repr(entry_id)
        path_key = path if isinstance(path, str) else repr(path)
        if expected is None or Path(path).name != path or "/" in path or "\\" in path:
            local.append(f"KPK_ENTRY_PATH:{label}")
        if not isinstance(entry_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry_id):
            local.append(f"KPK_ENTRY_ID:{label}")
        if id_key in seen_ids or path_key in seen_paths:
            local.append(f"KPK_ENTRY_DUPLICATE:{label}")
        seen_ids.add(id_key); seen_paths.add(path_key)
        if expected and (entry["id"] != expected[0] or entry["owner"] != expected[1]):
            local.append(f"KPK_ENTRY_AUTHORITY:{label}")
        if not isinstance(entry["owner"], str) or entry["owner"] not in OWNERS or entry["classification"] != "INTERNAL":
            local.append(f"KPK_ENTRY_CLASSIFICATION:{label}")
        disposition = entry["disposition"]
        reason = entry["dispositionReason"]
        if disposition == "ACTIVE":
            if reason is not None:
                local.append(f"KPK_DISPOSITION_REASON:{label}")
        elif isinstance(disposition, str) and disposition in DISPOSITION_CODES:
            local.append(f"{DISPOSITION_CODES[disposition]}:{label}")
            if not isinstance(reason, str) or not reason.strip():
                local.append(f"KPK_DISPOSITION_REASON:{label}")
        else:
            local.append(f"KPK_DISPOSITION:{label}")
        consumers = entry["allowedConsumers"]
        if not _exact_list(consumers, CONSUMERS):
            local.append(f"KPK_CONSUMERS:{label}")
        triggers = entry["refreshTriggers"]
        if not _exact_list(triggers, TRIGGERS):
            local.append(f"KPK_REFRESH_TRIGGERS:{label}")
        if entry["retentionPolicy"] != "RETAIN_WHILE_SOURCES_ARE_CURRENT_AND_OWNER_MAINTAINS_ENTRY" or entry["correctionPolicy"] != "REVIEWED_COMMIT_OR_AUTHORIZED_R2_WITHDRAWAL":
            local.append(f"KPK_POLICY:{label}")
        entry_date = _valid_date(entry["reviewedAt"], clock)
        if entry_date is None or manifest_date is None or entry_date > manifest_date:
            local.append(f"KPK_DATE:{label}")
        if not isinstance(entry["eligibleForLocalIndex"], bool):
            local.append(f"KPK_ELIGIBILITY_TYPE:{label}")
        purpose = entry["purpose"]
        if not isinstance(purpose, str) or not purpose.strip():
            local.append(f"KPK_PURPOSE:{label}")
        for code in secret_codes("\n".join(value for value in (purpose, reason) if isinstance(value, str))):
            local.append(f"{code}:{label}")
        pins = entry["sourcePins"]
        pin_paths: set[str] = set()
        if not isinstance(pins, list) or not pins:
            local.append(f"KPK_SOURCE_PINS:{label}")
            pins = []
        for pin in pins:
            if not isinstance(pin, dict) or set(pin) != PIN_FIELDS:
                local.append(f"KPK_SOURCE_PIN_SCHEMA:{label}")
                continue
            source = pin["path"]; source_key = source if isinstance(source, str) else repr(source)
            if source_key in pin_paths:
                local.append(f"KPK_SOURCE_PIN_DUPLICATE:{label}")
            pin_paths.add(source_key)
            target = _safe_project_file(root, source)
            if target is None:
                local.append(f"KPK_SOURCE_PATH:{label}")
            elif not isinstance(pin["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", pin["sha256"]) or _hash(target) != pin["sha256"]:
                local.append(f"{'KPK_CONTINUITY_CHANGED' if path == 'GOVERNANCE_BOUNDARIES.md' else 'KPK_SOURCE_PIN_DRIFT'}:{label}")
        if expected and pin_paths != expected[2]:
            local.append(f"KPK_SOURCE_SET:{label}")
        doc = knowledge / path if isinstance(path, str) else knowledge / "missing"
        if not doc.is_file() or doc.is_symlink():
            local.append(f"KPK_DOCUMENT_PATH:{label}")
        else:
            text = _read_utf8(doc)
            if text is None:
                local.append(f"KPK_DOCUMENT_UTF8:{label}")
            else:
                texts[path] = text
                if not 200 <= len(text.encode("utf-8")) <= 12_000:
                    local.append(f"KPK_DOCUMENT_SIZE:{label}")
                cited, grammar_ok = _citations(text)
                if not grammar_ok or cited != pin_paths:
                    local.append(f"KPK_CITATIONS:{label}")
                lowered = text.casefold()
                if any(phrase in lowered for phrase in FORBIDDEN):
                    local.append(f"KPK_FORBIDDEN_CLAIM:{label}")
                for code in secret_codes(text):
                    local.append(f"{code}:{label}")
        derived = not local and disposition == "ACTIVE"
        if entry["eligibleForLocalIndex"] is not derived:
            local.append(f"KPK_ELIGIBILITY_MISMATCH:{label}")
        if not local and derived:
            eligible.append(path)
        errors.extend(local)
    name = "README.md"; text = _read_utf8(knowledge / name)
    if text is None:
        errors.append(f"KPK_DOCUMENT_UTF8:{name}")
    else:
            lowered = text.casefold()
            if any(phrase in lowered for phrase in FORBIDDEN):
                errors.append(f"KPK_FORBIDDEN_CLAIM:{name}")
            errors.extend(f"{code}:{name}" for code in secret_codes(text))
    if check_continuity:
        errors.extend(_continuity_errors(root))
    unique = tuple(sorted(set(errors)))
    return ValidationResult(unique, tuple(sorted(eligible)) if not unique else ())
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--knowledge-root", type=Path)
    args = parser.parse_args()
    result = validate_pack(args.project_root, args.knowledge_root)
    if result.ok:
        print("PROJECT KNOWLEDGE: PASS")
        return 0
    print("PROJECT KNOWLEDGE: FAIL")
    for error in result.errors:
        print(f"  - {error}")
    return 1
if __name__ == "__main__":
    raise SystemExit(main())
