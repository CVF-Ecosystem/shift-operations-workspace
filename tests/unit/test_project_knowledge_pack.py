from __future__ import annotations
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
import pytest
import scripts.check_project_knowledge as checker

from scripts.check_project_knowledge import (
    DOCS,
    ROOT,
    _safe_project_file,
    secret_codes,
    validate_pack,
)


@pytest.fixture
def pack(tmp_path: Path) -> Path:
    target = tmp_path / "knowledge"
    shutil.copytree(ROOT / "knowledge", target)
    return target


def load_manifest(pack: Path) -> dict:
    return json.loads((pack / "manifest.json").read_text(encoding="utf-8"))


def write_manifest(pack: Path, data: dict) -> None:
    (pack / "manifest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def codes(pack: Path, *, today: date = date(2026, 8, 3)) -> set[str]:
    return set(validate_pack(ROOT, pack, today=today).errors)


def has(result: set[str], prefix: str) -> bool:
    return any(item.startswith(prefix) for item in result)


def test_repository_pack_passes_with_exact_eligible_set() -> None:
    result = validate_pack(ROOT)
    assert result.ok
    assert set(result.eligible) == DOCS


def test_duplicate_json_key_fails(pack: Path) -> None:
    path = pack / "manifest.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"schemaVersion": "1.0",', '"schemaVersion": "1.0",\n  "schemaVersion": "1.0",', 1), encoding="utf-8")
    assert codes(pack) == {"KPK_MANIFEST_JSON:manifest.json"}


@pytest.mark.parametrize("mutation", ["unknown", "missing"])
def test_top_level_schema_fails(pack: Path, mutation: str) -> None:
    data = load_manifest(pack)
    if mutation == "unknown":
        data["extra"] = True
    else:
        del data["packId"]
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_MANIFEST_SCHEMA")


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("eligibleForLocalIndex", 1, "KPK_ELIGIBILITY_TYPE"),
        ("owner", "UNKNOWN", "KPK_ENTRY_AUTHORITY"),
        ("classification", "RESTRICTED", "KPK_ENTRY_CLASSIFICATION"),
        ("allowedConsumers", ["UNKNOWN"], "KPK_CONSUMERS"),
    ],
)
def test_strict_types_and_allowlists(pack: Path, field: str, value: object, expected: str) -> None:
    data = load_manifest(pack)
    data["entries"][0][field] = value
    write_manifest(pack, data)
    assert has(codes(pack), expected)


@pytest.mark.parametrize("field", ["id", "path"])
def test_duplicate_entry_identity_fails(pack: Path, field: str) -> None:
    data = load_manifest(pack)
    data["entries"][1][field] = data["entries"][0][field]
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_ENTRY_DUPLICATE")


def test_duplicate_source_pin_fails(pack: Path) -> None:
    data = load_manifest(pack)
    data["entries"][0]["sourcePins"].append(data["entries"][0]["sourcePins"][0])
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_SOURCE_PIN_DUPLICATE")


@pytest.mark.parametrize(
    "bad_path",
    ["../PROJECT_CONTEXT.md", "C:/PROJECT_CONTEXT.md", "nested/PROJECT_CONTEXT.md", "nested\\PROJECT_CONTEXT.md"],
)
def test_entry_path_attacks_fail(pack: Path, bad_path: str) -> None:
    data = load_manifest(pack)
    data["entries"][0]["path"] = bad_path
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_ENTRY_PATH")


@pytest.mark.parametrize("bad_source", ["../outside", "C:/outside", "docs\\outside", []])
def test_source_path_traversal_and_absence_fail(pack: Path, bad_source: object) -> None:
    data = load_manifest(pack)
    data["entries"][0]["sourcePins"][0]["path"] = bad_source
    write_manifest(pack, data)
    result = codes(pack)
    assert has(result, "KPK_SOURCE_PATH")
    assert has(result, "KPK_SOURCE_SET")


def test_safe_project_file_rejects_symlink(monkeypatch: pytest.MonkeyPatch) -> None:
    original = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self.name == "IMPLEMENTATION_STATUS.json" or original(self),
    )
    assert _safe_project_file(ROOT, "IMPLEMENTATION_STATUS.json") is None


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("id", [], "KPK_ENTRY_ID"),
        ("owner", [], "KPK_ENTRY_CLASSIFICATION"),
        ("path", [], "KPK_ENTRY_PATH"),
        ("allowedConsumers", [{}], "KPK_CONSUMERS"),
        ("refreshTriggers", [{}], "KPK_REFRESH_TRIGGERS"),
        ("disposition", [], "KPK_DISPOSITION"),
    ],
)
def test_unhashable_entry_values_fail_closed(
    pack: Path, field: str, value: object, expected: str
) -> None:
    data = load_manifest(pack)
    data["entries"][0][field] = value
    write_manifest(pack, data)
    assert has(codes(pack), expected)


def test_source_pin_drift_excludes_entry(pack: Path) -> None:
    data = load_manifest(pack)
    data["entries"][0]["sourcePins"][0]["sha256"] = "0" * 64
    write_manifest(pack, data)
    result = validate_pack(ROOT, pack, today=date(2026, 8, 3))
    assert has(set(result.errors), "KPK_SOURCE_PIN_DRIFT")
    assert "PROJECT_CONTEXT.md" not in result.eligible


def test_unmanifested_markdown_and_readme_eligibility_fail(pack: Path) -> None:
    (pack / "EXTRA.md").write_text("extra substantive markdown" * 20, encoding="utf-8")
    data = load_manifest(pack)
    data["entries"][0]["path"] = "README.md"
    write_manifest(pack, data)
    result = codes(pack)
    assert has(result, "KPK_MARKDOWN_SET")
    assert has(result, "KPK_ENTRY_PATH")


def test_nested_unmanifested_markdown_fails(pack: Path) -> None:
    nested = pack / "nested"
    nested.mkdir()
    (nested / "EXTRA.md").write_text("nested substantive markdown" * 20, encoding="utf-8")
    assert has(codes(pack), "KPK_MARKDOWN_SET")


@pytest.mark.parametrize(
    ("disposition", "code"),
    [
        ("OWNER_WITHDRAWN", "KPK_OWNER_WITHDRAWN"),
        ("SECURITY_RECLASSIFIED", "KPK_SECURITY_RECLASSIFIED"),
        ("REVIEW_BLOCKED", "KPK_REVIEW_BLOCKED"),
    ],
)
def test_non_active_disposition_is_ineligible(pack: Path, disposition: str, code: str) -> None:
    data = load_manifest(pack)
    data["entries"][0]["disposition"] = disposition
    data["entries"][0]["dispositionReason"] = "reviewed local fixture"
    data["entries"][0]["eligibleForLocalIndex"] = False
    write_manifest(pack, data)
    result = validate_pack(ROOT, pack, today=date(2026, 8, 3))
    assert has(set(result.errors), code)
    assert "PROJECT_CONTEXT.md" not in result.eligible


def test_all_refresh_triggers_are_required(pack: Path) -> None:
    data = load_manifest(pack)
    data["entries"][0]["refreshTriggers"].pop()
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_REFRESH_TRIGGERS")


@pytest.mark.parametrize(("scope", "value"), [("manifest", "2026-08-04"), ("entry", "2026-08-04"), ("manifest", "2026-02-30")])
def test_invalid_or_future_review_dates_fail(pack: Path, scope: str, value: str) -> None:
    data = load_manifest(pack)
    if scope == "manifest":
        data["reviewedAt"] = value
    else:
        data["entries"][0]["reviewedAt"] = value
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_DATE")


@pytest.mark.parametrize(
    "phrase",
    ["automatically retrieve", "automatically inject", "enforcement will reject", "retrieval is implemented", "rag is implemented", "production ready"],
)
def test_forbidden_claim_phrases_fail(pack: Path, phrase: str) -> None:
    path = pack / "PROJECT_CONTEXT.md"
    path.write_text(path.read_text(encoding="utf-8") + f"\n{phrase}\n", encoding="utf-8")
    assert has(codes(pack), "KPK_FORBIDDEN_CLAIM")


@pytest.mark.parametrize("suffix", ["API_KEY", "ACCESS_KEY", "SECRET", "TOKEN", "PASSWORD"])
@pytest.mark.parametrize("prefix", ["", "APP_"])
def test_bare_and_prefixed_secret_assignments_fail(suffix: str, prefix: str) -> None:
    assert "KPK_SECRET_ASSIGNMENT" in secret_codes(f"{prefix}{suffix}=real-value")


@pytest.mark.parametrize(
    "text",
    [
        'TOKEN="dummy real-value"', "TOKEN='dummy real-value'", 'TOKEN="unterminated',
        "-----BEGIN PRIVATE KEY-----", "https://user:real-value@example.test",
        "abcdefgh.ijklmnop.qrstuvwx", "AKIAABCDEFGHIJKLMNOP",
    ],
)
def test_exact_secret_sentinels_fail(text: str) -> None:
    assert secret_codes(text)


@pytest.mark.parametrize(
    "text",
    [
        'TOKEN="dummy"', "TOKEN='<redacted>'", "TOKEN=${ENV_VAR}",
        "mention TOKEN without assignment", "PUBLIC_NAME=real-value",
        "BEGIN PRIVATE KEY", "https://example.test/path", "header.payload",
        "AKIASHORT", "https://example:dummy@example.test",
    ],
)
def test_secret_safe_controls_pass(text: str) -> None:
    assert not secret_codes(text)


@pytest.mark.parametrize("field", ["purpose", "dispositionReason"])
def test_manifest_controlled_secret_text_fails(pack: Path, field: str) -> None:
    data = load_manifest(pack)
    if field == "dispositionReason":
        data["entries"][0]["disposition"] = "REVIEW_BLOCKED"
        data["entries"][0]["eligibleForLocalIndex"] = False
    data["entries"][0][field] = 'TOKEN="dummy real-value"'
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_SECRET_ASSIGNMENT")


def test_index_residue_fails(pack: Path) -> None:
    (pack / "_index.json").write_text("{}", encoding="utf-8")
    assert has(codes(pack), "KPK_INDEX_RESIDUE")

def test_invalid_utf8_returns_stable_diagnostic(pack: Path) -> None:
    (pack / "PROJECT_CONTEXT.md").write_bytes(b"\xff\xfe")
    assert has(codes(pack), "KPK_DOCUMENT_UTF8")

def test_governance_pin_change_is_continuity_event(pack: Path) -> None:
    data = load_manifest(pack)
    data["entries"][2]["sourcePins"][0]["sha256"] = "0" * 64
    write_manifest(pack, data)
    assert has(codes(pack), "KPK_CONTINUITY_CHANGED")

def test_repository_root_index_residue_fails(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "knowledge", tmp_path / "knowledge")
    (tmp_path / "_index.json").write_text("{}", encoding="utf-8")
    assert has(set(validate_pack(tmp_path, check_continuity=False).errors), "KPK_INDEX_RESIDUE")

def test_default_clock_uses_utc(pack: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class BoundaryClock:
        @classmethod
        def now(cls, zone: timezone) -> datetime:
            assert zone is timezone.utc
            return datetime(2026, 8, 2, 23, 30, tzinfo=zone)
    monkeypatch.setattr(checker, "datetime", BoundaryClock)
    assert has(set(checker.validate_pack(ROOT, pack).errors), "KPK_DATE")

def test_diagnostics_are_sorted_and_do_not_echo_value(pack: Path) -> None:
    marker = "unique-sensitive-marker"
    data = load_manifest(pack)
    data["entries"][0]["purpose"] = f"TOKEN={marker}"
    data["entries"][0]["owner"] = "UNKNOWN"
    write_manifest(pack, data)
    result = validate_pack(ROOT, pack, today=date(2026, 8, 3))
    assert list(result.errors) == sorted(result.errors)
    assert marker not in "\n".join(result.errors)
