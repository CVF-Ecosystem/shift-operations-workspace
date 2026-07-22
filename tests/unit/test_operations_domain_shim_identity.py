"""Shim identity tests (tranche P1-B). Covers SPEC AC-04a and AC-04b.

`workspace_api.domain.models` and `workspace_api.domain.lifecycle` re-export the
canonical objects from `operations_domain`. Because `from X import Y` binds the
SAME object, the relationship is identity, not equivalence - and that is what is
asserted here, per module pair.

The negative assertions matter as much as the positive ones: if a future change
re-declares (or subclasses) one of these names in a shim, the repo would carry
TWO `Shift` classes that fail each other's isinstance checks and diverge in
Pydantic schema output. That is the exact failure mode this file exists to
block.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from operations_domain import lifecycle as domain_lifecycle
from operations_domain import models as domain_models
from workspace_api.domain import lifecycle as shim_lifecycle
from workspace_api.domain import models as shim_models

REPO_ROOT = Path(__file__).resolve().parents[2]
SHIM_MODELS_PATH = (
    REPO_ROOT / "apps" / "workspace-api" / "src" / "workspace_api" / "domain" / "models.py"
)
SHIM_LIFECYCLE_PATH = (
    REPO_ROOT / "apps" / "workspace-api" / "src" / "workspace_api" / "domain" / "lifecycle.py"
)

MOVED_TYPES = [
    "Correction",
    "CustomerRequest",
    "CustomerRequestStatus",
    "DataState",
    "EvidenceRef",
    "Message",
    "OperationalEvent",
    "RiskClass",
    "Shift",
    "ShiftStatus",
    "Task",
    "TaskStatus",
]
MOVED_FUNCTIONS = [
    "assert_customer_request_transition",
    "assert_task_transition",
    "assert_transition",
]


@pytest.mark.parametrize("name", MOVED_TYPES)
def test_ac04a_model_identity_between_models_modules(name):
    """AC-04a: identity holds between the two *models* modules."""
    assert getattr(shim_models, name) is getattr(domain_models, name)


def test_ac04a_named_example_from_the_spec():
    """The SPEC names this one explicitly; assert it verbatim."""
    assert shim_models.Shift is domain_models.Shift


@pytest.mark.parametrize("name", MOVED_FUNCTIONS)
def test_ac04b_lifecycle_identity_between_lifecycle_modules(name):
    """AC-04b: identity holds between the two *lifecycle* modules."""
    assert getattr(shim_lifecycle, name) is getattr(domain_lifecycle, name)


def test_lifecycle_guards_are_not_re_exported_from_the_models_module():
    """Cross-module assertion is not a valid substitute (SPEC section 4.1)."""
    for name in MOVED_FUNCTIONS:
        assert not hasattr(domain_models, name)
        assert not hasattr(shim_models, name)


def _top_level_definitions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_shims_declare_no_moved_name():
    """R4.3: neither shim may declare a class/def for a moved name."""
    moved = set(MOVED_TYPES) | set(MOVED_FUNCTIONS)

    models_defs = _top_level_definitions(SHIM_MODELS_PATH)
    assert models_defs & moved == set(), f"shim redeclares moved names: {models_defs & moved}"
    # User is the one class this module is still allowed to define (R4.4).
    assert models_defs == {"User"}, models_defs

    lifecycle_defs = _top_level_definitions(SHIM_LIFECYCLE_PATH)
    assert lifecycle_defs == set(), f"lifecycle shim must declare nothing: {lifecycle_defs}"


def test_user_did_not_move_and_stays_canonical_in_the_application_package():
    """R4.4: User is a reasoned exception, not an oversight."""
    assert shim_models.User.__module__ == "workspace_api.domain.models"
    assert not hasattr(domain_models, "User")


def test_injected_namespace_exposes_everything_the_ledger_needs():
    """ADR section 2.5: the SqlLedger `models=` namespace contract is intact.

    operations_ledger._rows / sql_ledger reach for these names on the injected
    namespace. If the shim ever stopped exposing one - in particular `User`,
    which does not live in operations_domain - add_user/get_user_by_username
    would break at runtime in a path no current test constructs.
    """
    for name in (
        "Shift",
        "ShiftStatus",
        "OperationalEvent",
        "Task",
        "CustomerRequest",
        "EvidenceRef",
        "Correction",
        "User",
    ):
        assert hasattr(shim_models, name), f"injected namespace lost {name}"
