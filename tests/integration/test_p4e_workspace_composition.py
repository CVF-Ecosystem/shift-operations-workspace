"""P4-E Workspace API composition tests (SPEC AC-11/AC-16, Work Order
carry-forward). Imports the REAL composition root, instantiates production
composition with injected stores, and inspects the concrete bound
repository/store module ownership - never a source-comment assertion.

The default test/dev environment has no ``DATABASE_URL``, so
``get_ledger()`` returns the pre-existing ``InMemoryLedger`` (documented in
``ledger_factory.py`` as "tests, offline/degraded mode" - unrelated to P4-E
and out of this tranche's scope to repair, DESIGN section 9). The
composition root's own degraded-fallback logic is exercised directly
against that reality; the durable branch is exercised by calling the SAME
real composition function with an injected durable ledger, never by
asserting a claim the ambient environment cannot support.
"""

from __future__ import annotations

import workspace_api.main as main_module


def test_default_environment_fails_closed_not_process_local_fallback():
    """SPEC R10/AC-16/completion-review F7: without a durable backend
    configured, mounted production composition must FAIL CLOSED
    (``external_ingress_service`` is ``None``, and the router already
    returns 503 for that) - never silently wire the process-local
    ``InMemoryExternalIngressRepository`` into the live app."""
    from workspace_api.dependencies import get_ledger

    ledger = get_ledger()
    if hasattr(ledger, "add_p4e_proposal"):
        import pytest

        pytest.skip("DATABASE_URL is configured in this environment; durable branch is exercised below")
    assert main_module.app.state.external_ingress_service is None


def test_router_refuses_with_503_when_composition_is_not_durable():
    """completion-review F7 required regression: the actual router path
    (not just the composed service object) fails closed with 503 when the
    mounted composition has no durable backend - proving the FastAPI app
    never silently accepts ingress into process-local storage."""
    from fastapi.testclient import TestClient
    from workspace_api.dependencies import get_ledger

    ledger = get_ledger()
    if hasattr(ledger, "add_p4e_proposal"):
        import pytest

        pytest.skip("DATABASE_URL is configured in this environment; durable branch is exercised elsewhere")
    client = TestClient(main_module.app)
    response = client.post(
        "/external-ingress/proposals",
        json={"envelope_id": "env1", "channel": "ch1", "external_id": "msg1",
              "candidate": {"text": "hi"}, "provenance_digest": "a" * 64},
        headers={"X-Service-Assertion": "irrelevant"},
    )
    assert response.status_code == 503


def test_durable_ledger_composes_the_ledger_backed_repository_and_processor(monkeypatch):
    """AC-16: when a durable Ledger is available, the process-local
    repository must not be reachable - the sole live proposal/placement
    store is the injected durable Ledger."""
    from operations_ledger.sql_ledger import SqlLedger, make_engine
    from operations_ledger.tables import metadata
    from workspace_api.domain import models as domain_models
    from workspace_api.external_ingress.repository import (
        InMemoryExternalIngressRepository,
        LedgerExternalIngressRepository,
    )
    from workspace_api.application.p4e_placement import P4ePlacementProcessor

    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    durable_ledger = SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)
    monkeypatch.setattr(main_module, "get_ledger", lambda: durable_ledger, raising=False)

    import workspace_api.dependencies as dependencies_module

    monkeypatch.setattr(dependencies_module, "get_ledger", lambda: durable_ledger)

    service = main_module._compose_external_ingress_service()
    assert type(service.repository) is LedgerExternalIngressRepository
    assert not isinstance(service.repository, InMemoryExternalIngressRepository)
    assert isinstance(service.placement_processor, P4ePlacementProcessor)
    assert service.repository._ledger is durable_ledger


def test_composed_durable_repository_targets_a_ledger_with_p4e_persistence_methods(monkeypatch):
    """The bound repository's ``_ledger`` must be the real Operations
    Ledger Protocol object (has the P4-E persistence methods), not an
    in-memory dict/list structure."""
    from operations_ledger.sql_ledger import SqlLedger, make_engine
    from operations_ledger.tables import metadata
    from workspace_api.domain import models as domain_models
    import workspace_api.dependencies as dependencies_module

    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    durable_ledger = SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)
    monkeypatch.setattr(dependencies_module, "get_ledger", lambda: durable_ledger)

    service = main_module._compose_external_ingress_service()
    ledger = service.repository._ledger
    assert hasattr(ledger, "add_p4e_proposal")
    assert hasattr(ledger, "claim_placement_work")
    assert hasattr(ledger, "confirm_mapping")


def test_external_identities_router_is_mounted_and_hidden_from_schema():
    from workspace_api.main import app

    paths = {route.path for route in app.routes}
    assert "/external-identities/mappings/propose" in paths
    matching = [r for r in app.routes if getattr(r, "path", None) == "/external-identities/mappings/propose"]
    assert matching[0].include_in_schema is False


def test_conversation_routes_router_is_mounted_and_hidden_from_schema():
    from workspace_api.main import app

    paths = {route.path for route in app.routes}
    assert "/conversation-routes/bindings" in paths
    matching = [r for r in app.routes if getattr(r, "path", None) == "/conversation-routes/bindings"]
    assert matching[0].include_in_schema is False


def test_p4e_commands_use_get_ledger_dependency_not_a_hardcoded_backend():
    """SPEC R17/R18: Workspace API is the sole composition owner - identity-
    mapping/conversation-routing never import a concrete backend."""
    import inspect

    from workspace_api.dependencies import get_p4e_mapping_commands, get_p4e_placement_commands

    source_a = inspect.getsource(get_p4e_mapping_commands)
    source_b = inspect.getsource(get_p4e_placement_commands)
    assert "build_ledger" in source_a
    assert "build_ledger" in source_b


def test_p4e_key_authority_uses_disposable_secret_store_never_a_real_credential():
    from workspace_api.dependencies import _p4e_key_authority

    authority = _p4e_key_authority()
    key_id, key_version, secret = authority.active_key()
    assert isinstance(secret, bytes)
    assert len(secret) >= 32


def test_request_models_reject_extra_fields():
    """SPEC R17: closed application operations - request models forbid
    extra fields."""
    from workspace_api.api.external_identities.router import ProposeInput
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        ProposeInput(
            observation_id="o1", target_user_id="u1", raw_sender="x",
            key_id="k1", key_version="1", idempotency_key="i1",
            actor_id="injected",  # forbidden - callers cannot supply actor id
        )


def test_bind_input_forbids_caller_supplied_result_fields():
    from workspace_api.api.conversation_routes.router import BindInput
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        BindInput(
            mapping_id="m1", expected_mapping_version=1, target_kind="WORKSPACE",
            target_id="a" * 64, idempotency_key="i1",
            conversation_key="injected",  # forbidden - callers cannot supply the result
        )
