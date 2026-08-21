"""P4-A3 CVF governance boundary tests (SPEC R1/R5/R10/R12).

No-network, no-persistence, no-route and claim-boundary checks proving the
memory layer and its application composition are structural safe by
construction. Not governance proof by itself - these prove the STRUCTURAL
boundaries that make any future live-provider checkpoint meaningful.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _package_files():
    import application_memory

    root = Path(application_memory.__file__).resolve().parent
    return sorted(root.glob("*.py"))


class TestNoNetworkBoundary:
    def test_package_has_no_network_capable_import(self):
        for path in _package_files():
            text = path.read_text(encoding="utf-8")
            assert "socket" not in text
            assert "urllib.request" not in text
            assert "http.client" not in text

    def test_composition_module_has_no_network_capable_import(self):
        import workspace_api.application.application_memory as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "urllib.request" not in text
        assert "http.client" not in text
        assert "socket" not in text


class TestNoPersistenceBoundary:
    def test_package_has_no_database_import(self):
        for path in _package_files():
            text = path.read_text(encoding="utf-8")
            assert "sqlite3" not in text
            assert "sqlalchemy" not in text

    def test_composition_never_calls_audit_or_ledger_append(self):
        import workspace_api.application.application_memory as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "append_audit" not in text
        assert "AuditLog.record" not in text
        assert "INSERT INTO" not in text

    def test_composition_opens_no_route(self):
        import workspace_api.application.application_memory as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "APIRouter" not in text
        assert "@router" not in text


class TestProviderNeutralBoundary:
    def test_package_imports_no_provider_sdk(self):
        for path in _package_files():
            text = path.read_text(encoding="utf-8")
            for sdk in ("openai", "dashscope", "anthropic"):
                assert sdk not in text

    def test_no_provider_dispatch_call_site_exists(self):
        for path in _package_files():
            text = path.read_text(encoding="utf-8")
            assert ".execute(" not in text
            assert "generate_structured_output" not in text


class TestClaimBoundary:
    def test_readme_declares_the_claim_boundary(self):
        readme = (_REPO_ROOT / "packages" / "application-memory" / "README.md").read_text(encoding="utf-8")
        assert "claim boundary" in readme.lower()
        assert "does not prove" in readme.lower()

    def test_spec_declares_exclusions(self):
        spec = (_REPO_ROOT / "docs" / "specs" / "P4A3_APPLICATION_MEMORY_SPEC.md").read_text(encoding="utf-8")
        assert "No episodic/semantic memory" in spec

    def test_application_composition_docstring_declares_no_implicit_recall(self):
        import workspace_api.application.application_memory as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "never recalls memory implicitly" in text


class TestReceiptSanitizationBoundary:
    def test_receipt_contains_no_content_or_secret_fields(self):
        from application_memory.receipts import MemoryReceiptV1

        forbidden = {"content", "query", "prompt", "token", "credential", "api_key", "provider_output"}
        assert not (set(MemoryReceiptV1.model_fields) & forbidden)
