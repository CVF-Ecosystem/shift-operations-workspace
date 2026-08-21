"""P4-A SPEC R1/R3 - dependency direction and real gate invocation.

These tests are structural, not governance proof: they prove the gateway is a
pure package that *calls the real cvf-runtime gates* rather than reimplementing
them, and that it does not depend on apps, ledgers, provider SDKs, network
clients, or the hidden CVF Core. R13's live run remains the governance proof.
"""

from __future__ import annotations

import asyncio
import ast
from pathlib import Path

import pytest

import ai_gateway
from ai_gateway.models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    GatewayRequest,
    Placement,
    ProviderRequest,
    ProviderResult,
    TerminationFacts,
    digest_of,
)
from ai_gateway.registry import ProviderRegistry
from ai_gateway.service import AIGateway
from ai_gateway.usage import UsageLedger

PACKAGE_ROOT = Path(ai_gateway.__file__).resolve().parent
DIGEST = "c" * 64
SCHEMA = {"type": "object", "required": ["ok"], "properties": {"ok": {"type": "boolean"}}}

FORBIDDEN_IMPORT_ROOTS = {
    "workspace_api",
    "operations_ledger",
    "operations_domain",
    "refinery_bridge",
    "governed_retrieval",
    "retrieval_contracts",
    "fastapi",
    "starlette",
    "sqlalchemy",
    "httpx",
    "requests",
    "urllib3",
    "openai",
    "dashscope",
    "anthropic",
}


def _module_files() -> list[Path]:
    return sorted(PACKAGE_ROOT.glob("*.py"))


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _imported_qualified_names(path: Path) -> set[str]:
    """Full dotted import targets, e.g. {'urllib.parse'} not just {'urllib'}."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                names.add(node.module)
    return names


class TestDependencyDirection:
    def test_package_has_modules(self):
        assert _module_files(), "expected ai_gateway modules to exist"

    @pytest.mark.parametrize("path", _module_files(), ids=lambda p: p.name)
    def test_no_forbidden_imports(self, path: Path):
        offending = _imported_roots(path) & FORBIDDEN_IMPORT_ROOTS
        assert not offending, f"{path.name} imports forbidden module(s): {sorted(offending)}"

    def test_no_network_client_import_anywhere(self):
        """R1: the pure package performs no network I/O of its own.

        ``urllib.parse`` is pure URL structure parsing with no I/O and is used
        by context.py to canonicalize endpoint_origin (P4A-REV-F3); only the
        network-capable urllib submodules (request/error) are forbidden.
        """
        for path in _module_files():
            roots = _imported_roots(path)
            assert "socket" not in roots, f"{path.name} imports socket"
            qualified = _imported_qualified_names(path)
            network_urllib = {n for n in qualified if n.startswith("urllib.") and n != "urllib.parse"}
            assert not network_urllib, f"{path.name} imports network-capable {network_urllib}"

    def test_only_cvf_runtime_is_the_external_project_dependency(self):
        """The gateway may depend on cvf_runtime; that is the call-site point."""
        service_roots = _imported_roots(PACKAGE_ROOT / "service.py")
        assert "cvf_runtime" in service_roots

    def test_package_does_not_import_hidden_core(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "Controlled-Vibe-Framework" not in text
            assert ".cvf" not in text


class TestRealGateInvocation:
    """R3: prove the three gates are really called, in order, before dispatch."""

    def _request(self) -> GatewayRequest:
        return GatewayRequest(
            task_type="canary",
            ai_mode=AIMode.EXTERNAL_AI,
            provider_id="fake",
            model_id="model-a",
            placement=Placement.EXTERNAL,
            context={},
            output_schema=SCHEMA,
            context_facts=ContextFacts(
                classification=Classification.PUBLIC,
                redaction_applied=True,
                minimization_proven=False,
                evidence_count=1,
                estimated_input_tokens=5,
                context_digest=digest_of({}),
            ),
            budget_facts=BudgetFacts(
                per_request_token_limit=1000,
                daily_budget_usd_millis=1000,
                monthly_budget_usd_millis=10000,
                spent_today_usd_millis=0,
                spent_month_usd_millis=0,
                estimated_cost_usd_millis=1,
            ),
            termination_facts=TerminationFacts(),
        )

    def test_gateway_invokes_the_real_cvf_runtime_functions(self, monkeypatch):
        """Patching cvf_runtime's own callables must be observed by the gateway.

        If the gateway had reimplemented these checks locally, patching the
        real module functions would have no effect and this test would fail.
        """
        import ai_gateway.service as service

        order: list[str] = []
        real_placement = service.assert_placement_allowed
        real_budget = service.assert_within_budget
        real_termination = service.assert_not_terminated

        def spy_placement(**kwargs):
            order.append("placement")
            return real_placement(**kwargs)

        def spy_budget(**kwargs):
            order.append("budget")
            return real_budget(**kwargs)

        def spy_termination(policy, state):
            order.append("termination")
            return real_termination(policy, state)

        monkeypatch.setattr(service, "assert_placement_allowed", spy_placement)
        monkeypatch.setattr(service, "assert_within_budget", spy_budget)
        monkeypatch.setattr(service, "assert_not_terminated", spy_termination)

        class _Provider:
            provider_id = "fake"

            def __init__(self) -> None:
                self.calls = 0

            async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
                order.append("dispatch")
                self.calls += 1
                return ProviderResult(
                    output={"ok": True},
                    provider_id="fake",
                    model_id=request.model_id,
                    usage={"total_tokens": 1, "cost_usd_millis": 1},
                )

            async def health_check(self) -> dict:
                return {}

            async def cancel_request(self, request_id: str) -> None:
                return None

        provider = _Provider()
        registry = ProviderRegistry()
        registry.register(provider, ("model-a",))
        gateway = AIGateway(registry, UsageLedger())

        result = asyncio.run(gateway.execute(self._request()))

        assert result.accepted is True
        assert order == ["placement", "budget", "termination", "dispatch"]
        assert provider.calls == 1

    def test_gate_functions_are_the_cvf_runtime_originals(self):
        """The imported names must be identical objects to cvf_runtime's."""
        import cvf_runtime.budget as budget_module
        import cvf_runtime.data_scope as data_scope_module
        import cvf_runtime.termination as termination_module
        import ai_gateway.service as service

        assert service.assert_placement_allowed is data_scope_module.assert_placement_allowed
        assert service.assert_within_budget is budget_module.assert_within_budget
        assert service.assert_not_terminated is termination_module.assert_not_terminated


class TestPurity:
    def test_gateway_declares_no_application_import(self):
        """No gateway module may declare an application-package import.

        Asserted statically over the source rather than via ``sys.modules``,
        which is unreliable here because earlier tests in the same session may
        legitimately have imported application packages for other reasons.
        """
        for path in _module_files():
            assert "workspace_api" not in _imported_roots(path)
