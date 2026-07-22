"""Compatibility shim for the lifecycle guards.

The canonical definitions live in `operations_domain.lifecycle`, which owns the
three transition tables (tranche P1B-OPERATIONS-DOMAIN-EXTRACTION). These names
are re-exported here so existing callers keep working; `from X import Y` binds
the SAME function object, so
`workspace_api.domain.lifecycle.assert_transition is
operations_domain.lifecycle.assert_transition`.

Do not re-declare these functions here, and do not copy a transition table back
into this module. New code should import from `operations_domain.lifecycle`
directly.
"""

from operations_domain.lifecycle import (  # noqa: F401  (re-exported for compatibility)
    assert_customer_request_transition,
    assert_task_transition,
    assert_transition,
)

__all__ = [
    "assert_customer_request_transition",
    "assert_task_transition",
    "assert_transition",
]
