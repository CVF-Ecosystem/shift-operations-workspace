"""Ownership-binding enforcement (SPEC R11) for the invariant-family guard.
Read-only, no provider/network/dynamic-import. Every schema-allowed strategy
(DIRECT_IDENTITY, JSON_REFERENCE, CANONICAL_DIGEST, ADAPTER_ASSERTION)
requires proof metadata AND a production verification step. Full path
authorization record: see the round-2 worker return (exact-30, Amendment 2).
"""
from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import Any
from invariant_family_contract import (
    DuplicateKey, Diagnostic, canonical_digest, is_safe_regular_file,
    load_json_no_dup, safe_repo_path,
)
from invariant_family_mutation_oracle import required_mutation_ids
_SYMBOL_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def _diag(code: str, path: str, family_id: str, message: str) -> Diagnostic:
    return Diagnostic(code=code, path=path, familyId=family_id, message=message)

def extract_module_symbol(resolved: Path, symbol: str) -> str | None:
    # Static text-pattern extraction only, never import/exec.
    if not _SYMBOL_NAME_RE.fullmatch(symbol):
        return None
    pattern = re.compile(rf'(?m)^{re.escape(symbol)}\s*(?::\s*\w[\w\[\], ]*)?\s*=\s*([\'"])([0-9a-f]{{64}})\1\s*$')
    match = pattern.search(resolved.read_text(encoding="utf-8"))
    return match.group(2) if match else None


def _resolve_json_pointer(document: Any, pointer: str) -> tuple[bool, Any]:
    if pointer in ("", "/"):
        return True, document
    if not pointer.startswith("/"):
        return False, None
    node = document
    for raw_segment in pointer.split("/")[1:]:
        segment = raw_segment.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and segment in node:
            node = node[segment]
        elif isinstance(node, list) and segment.isdigit() and int(segment) < len(node):
            node = node[int(segment)]
        else:
            return False, None
    return True, node


def _verify_direct_identity(owner_resolved: Path, binding: dict[str, Any], consumer: dict[str, Any]) -> str | None:
    owner_symbol = binding.get("ownerIdentitySymbol", "")
    consumer_symbol = consumer.get("identitySymbol", "")
    owner_value = extract_module_symbol(owner_resolved, owner_symbol) if owner_resolved.suffix == ".py" else None
    if owner_value is None:
        return "IFC_MISSING_OWNER_IDENTITY_SYMBOL"
    c_resolved = safe_repo_path(consumer.get("consumerPath", ""))
    consumer_value = extract_module_symbol(c_resolved, consumer_symbol) if c_resolved and c_resolved.suffix == ".py" else None
    if consumer_value is None:
        return "IFC_MISSING_CONSUMER_IDENTITY_SYMBOL"
    if owner_value != consumer_value:
        return "IFC_STALE_IDENTITY_BINDING"
    return None


def _verify_json_reference(owner_resolved: Path, consumer_resolved: Path, pointer: str) -> str | None:
    try:
        owner_doc = load_json_no_dup(owner_resolved)
        consumer_doc = load_json_no_dup(consumer_resolved)
    except (DuplicateKey, ValueError, OSError):
        return "IFC_UNRESOLVABLE_JSON_REFERENCE"
    owner_ok, owner_val = _resolve_json_pointer(owner_doc, pointer)
    consumer_ok, consumer_val = _resolve_json_pointer(consumer_doc, pointer)
    if not owner_ok or not consumer_ok:
        return "IFC_UNRESOLVABLE_JSON_REFERENCE"
    if owner_val != consumer_val:
        return "IFC_STALE_JSON_REFERENCE"
    return None


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    return matches[0] if len(matches) == 1 else None


def _local_assignments(func: ast.FunctionDef) -> dict[str, ast.expr]:
    assigns: dict[str, ast.expr] = {}
    for node in func.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            assigns[node.targets[0].id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assigns[node.target.id] = node.value
    return assigns


_ALLOWED_READERS = frozenset({"load_json_no_dup", "canonical_digest", "raw_digest"})
_PATH_RESOLVER = "safe_repo_path"


def _ifc_binding_is_closed(tree: ast.Module) -> bool:
    trusted = {
        id(node) for node in tree.body if isinstance(node, ast.Import) and len(node.names) == 1
        and node.names[0].name == "invariant_family_contract" and node.names[0].asname == "ifc"
    }
    if len(trusted) != 1:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if id(node) not in trusted and any((a.asname or a.name.split(".")[0]) == "ifc" for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and any(a.name == "*" or (a.asname or a.name) == "ifc" for a in node.names):
            return False
        elif isinstance(node, ast.Name) and node.id == "ifc" and isinstance(node.ctx, (ast.Store, ast.Del)):
            return False
        elif isinstance(node, ast.arg) and node.arg == "ifc":
            return False
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == "ifc":
            return False
        elif isinstance(node, ast.ExceptHandler) and node.name == "ifc":
            return False
        elif isinstance(node, (ast.Global, ast.Nonlocal)) and "ifc" in node.names:
            return False
        elif isinstance(node, ast.MatchAs) and node.name == "ifc":
            return False
        elif isinstance(node, ast.MatchStar) and node.name == "ifc" or isinstance(node, ast.MatchMapping) and node.rest == "ifc":
            return False
    return True


def _ifc_symbol(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "ifc":
        return func.attr
    return None


def _reads_path(node: ast.AST, declared_path: str) -> bool:
    if isinstance(node, (ast.Subscript, ast.Attribute)):
        return _reads_path(node.value, declared_path)
    if not isinstance(node, ast.Call) or _ifc_symbol(node) not in _ALLOWED_READERS:
        return False
    if len(node.args) != 1 or node.keywords:
        return False
    resolver = node.args[0]
    if not isinstance(resolver, ast.Call) or _ifc_symbol(resolver) != _PATH_RESOLVER:
        return False
    if len(resolver.args) != 1 or resolver.keywords:
        return False
    arg = resolver.args[0]
    return isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value == declared_path


def _verify_adapter_assertion(consumer: dict[str, Any], owner_path: str, consumer_path: str) -> str | None:
    # F3: equality-only compare of owner-path read vs consumer-path read.
    test_resolved = safe_repo_path(consumer.get("adapterTestPath", ""))
    if test_resolved is None or not is_safe_regular_file(test_resolved):
        return "IFC_UNSAFE_ADAPTER_TEST_PATH"
    function_name = consumer.get("assertionFunction", "")
    if not _SYMBOL_NAME_RE.fullmatch(function_name):
        return "IFC_MISSING_ASSERTION_FUNCTION"
    try:
        tree = ast.parse(test_resolved.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return "IFC_UNPARSEABLE_ADAPTER_TEST"
    func = _find_function(tree, function_name)
    if func is None:
        return "IFC_MISSING_ASSERTION_FUNCTION"
    if not any(isinstance(n, ast.Assert) for n in ast.walk(func)):
        return "IFC_ASSERTION_FUNCTION_HAS_NO_ASSERTION"
    local = _local_assignments(func)
    if not _ifc_binding_is_closed(tree):
        return "IFC_ASSERTION_NOT_BOUND_TO_OWNER"
    for n in ast.walk(func):
        if not isinstance(n, ast.Assert):
            continue
        test = n.test
        if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
            continue
        if not isinstance(test.ops[0], ast.Eq):
            continue
        left, right = test.left, test.comparators[0]
        if not isinstance(left, ast.Name) or not isinstance(right, ast.Name):
            continue
        lv, rv = local.get(left.id), local.get(right.id)
        if lv is None or rv is None:
            continue
        l_owner = _reads_path(lv, owner_path)
        r_owner = _reads_path(rv, owner_path)
        if l_owner == r_owner:
            continue
        consumer_side = rv if l_owner else lv
        if _reads_path(consumer_side, consumer_path):
            return None
    return "IFC_ASSERTION_NOT_BOUND_TO_OWNER"


def check_ownership_bindings(matrix: dict[str, Any], matrix_rel: str, family_id: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    seen_binding_ids: set[str] = set()
    for binding in matrix.get("ownershipBindings", []):
        bid = binding.get("bindingId")
        if bid in seen_binding_ids:
            diags.append(_diag("IFC_DUPLICATE_OWNERSHIP_BINDING_ID", matrix_rel, family_id, bid))
        seen_binding_ids.add(bid)
        owner_path = binding.get("ownerPath", "")
        owner_resolved = safe_repo_path(owner_path)
        if owner_resolved is None or not is_safe_regular_file(owner_resolved):
            diags.append(_diag("IFC_UNSAFE_OWNER_PATH", matrix_rel, family_id, owner_path))
            continue
        consumer_paths: set[str] = set()
        for consumer in binding.get("consumers", []):
            cpath = consumer.get("consumerPath", "")
            strategy = consumer.get("strategy")
            if cpath in consumer_paths:
                diags.append(_diag("IFC_DUPLICATE_CONSUMER_PATH", matrix_rel, family_id, cpath))
            consumer_paths.add(cpath)
            if cpath == owner_path:
                diags.append(_diag("IFC_OWNER_AS_CONSUMER", matrix_rel, family_id, cpath))
            c_resolved = safe_repo_path(cpath)
            if c_resolved is None or not is_safe_regular_file(c_resolved):
                diags.append(_diag("IFC_UNSAFE_CONSUMER_PATH", matrix_rel, family_id, cpath))
                continue
            code: str | None = None
            if strategy == "CANONICAL_DIGEST":
                symbol = consumer.get("digestSymbol", "")
                declared = extract_module_symbol(c_resolved, symbol)
                if declared is None:
                    code = "IFC_MISSING_DIGEST_SYMBOL"
                elif declared != canonical_digest(owner_resolved):
                    code = "IFC_STALE_OWNERSHIP_DIGEST"
            elif strategy == "JSON_REFERENCE":
                pointer = consumer.get("jsonPointer", "")
                if not pointer:
                    code = "IFC_MISSING_JSON_POINTER"
                else:
                    code = _verify_json_reference(owner_resolved, c_resolved, pointer)
            elif strategy == "DIRECT_IDENTITY":
                code = _verify_direct_identity(owner_resolved, binding, consumer)
            elif strategy == "ADAPTER_ASSERTION":
                code = _verify_adapter_assertion(consumer, owner_path, cpath)
            else:
                code = "IFC_UNSUPPORTED_OWNERSHIP_STRATEGY"
            if code:
                diags.append(_diag(code, matrix_rel, family_id, cpath))
    return diags


__all__ = ["check_ownership_bindings", "extract_module_symbol", "required_mutation_ids"]
