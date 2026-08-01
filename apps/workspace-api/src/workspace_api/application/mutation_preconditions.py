"""Shared mutation-precondition comparator (P2C-MUTATION-FULL-UI-C3B2, SPEC
R13/R14, ADR section 6/D4).

One canonical place every governed service compares a caller-supplied
``expected_version``/``expected_status`` against current stored truth, so the
missing-precondition-is-422 / stale-precondition-is-409 shape and its
wording cannot silently drift between shift/event/task/customer_request/
incident/handover/report call sites. Callers invoke this INSIDE the same
mutation transaction as the eventual write, after permission and assignment
admission but before any lifecycle/quorum check or mutation itself (Work
Order section 3.3) - it never touches the ledger or the database itself, it
only compares values the caller already read inside that transaction.

``assert_version_precondition``/``assert_status_precondition`` accept
``None`` for a missing request field (the router layer forwards whatever the
client sent) and raise the SAME ``CvfDenied`` shape both HTTP and direct
service callers get: a missing field is controlled 422, a mismatched value is
controlled 409. Neither ever mutates or has a side effect - the caller
remains solely responsible for the actual write.

REVIEW-F4: the HTTP boundary's Pydantic schema already rejects a non-integer
``expected_version`` or a non-enum ``expected_status`` before either function
below ever runs. These functions are the SAME boundary at the direct-service
call site, where no Pydantic validation runs first - a caller there could
pass ``True`` (a ``bool`` is a Python ``int`` subclass and would otherwise
satisfy ``isinstance(x, int)``), ``1.0``, ``"1"``, ``0`` or ``-1`` and reach
the mutation. Every one of those is now a controlled 422, identical in shape
to a missing field - never silently coerced, never admitted as a "valid"
stale comparison.
"""

from __future__ import annotations

from cvf_runtime.errors import CvfDenied


def assert_version_precondition(
    *, control: str, expected_version: int | None, current_version: int
) -> None:
    """R13/R14: missing ``expected_version`` is 422; a non-integer, boolean,
    or out-of-range (``< 1``) value is also 422; only a valid positive
    integer that mismatches ``current_version`` is a stale 409."""
    if expected_version is None:
        raise CvfDenied(
            control=control,
            reason="expected_version is required for this mutation",
            http_status=422,
        )
    if isinstance(expected_version, bool) or not isinstance(expected_version, int) or expected_version < 1:
        raise CvfDenied(
            control=control,
            reason=(
                f"expected_version must be an integer >= 1, got {expected_version!r} "
                f"({type(expected_version).__name__})"
            ),
            http_status=422,
        )
    if expected_version != current_version:
        raise CvfDenied(
            control=control,
            reason=(
                f"stale expected_version: expected {current_version}, "
                f"caller supplied {expected_version}"
            ),
            http_status=409,
        )


def assert_status_precondition(
    *, control: str, expected_status, current_status
) -> None:
    """R13/R14: missing ``expected_status`` is 422; a value that is not a
    genuine INSTANCE of ``current_status``'s exact enum type is also 422 -
    never constructed/coerced from a raw value (REVIEW-REREV-F1: a StrEnum's
    constructor happily accepts a plain string like ``"DRAFT"`` and returns a
    real member, so ``status_type(expected_status)`` used to admit a raw
    string that was never actually a member the caller held; ``isinstance``
    has no such coercion). Only a genuine member that mismatches the current
    stored status is a stale 409.

    Used only by the Report status-only transitions (submit-review, approve),
    whose immutable content version does not increment on a status change -
    see Report.version vs. Report status in ``report_service.py``."""
    if expected_status is None:
        raise CvfDenied(
            control=control,
            reason="expected_status is required for this mutation",
            http_status=422,
        )
    status_type = type(current_status)
    if not isinstance(expected_status, status_type):
        raise CvfDenied(
            control=control,
            reason=(
                f"expected_status must be a genuine {status_type.__name__} member, "
                f"got {expected_status!r} ({type(expected_status).__name__})"
            ),
            http_status=422,
        )
    if expected_status != current_status:
        raise CvfDenied(
            control=control,
            reason=(
                f"stale expected_status: expected {current_status}, "
                f"caller supplied {expected_status}"
            ),
            http_status=409,
        )
