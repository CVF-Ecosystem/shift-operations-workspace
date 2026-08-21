"""Published provider contract for P4-A (SPEC R2/R11).

This file is the stable, importable contract surface. It re-exports the strict
models and protocol from the ``ai_gateway`` package so there is exactly one
canonical definition of each type rather than a second, drifting copy.

Historical note: this file previously declared its own loose models with a
mutable default (``usage: dict = {}``) and no ``extra="forbid"``. SPEC R2
forbids both, so the definitions now live in ``ai_gateway.models`` and this
module is a thin re-export.
"""

from __future__ import annotations

from ai_gateway.models import ProviderRequest, ProviderResult
from ai_gateway.provider import AIProvider

__all__ = ["AIProvider", "ProviderRequest", "ProviderResult"]
