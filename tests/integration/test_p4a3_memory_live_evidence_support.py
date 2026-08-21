"""P4-A3 live-evidence support mechanics (SPEC R6/R12).

Mechanical test of the support script only - NO provider, network, install or
database call. Proves every mandated refusal case reports zero store mutations
and zero provider attempts, and that the secret scanner still catches secrets.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = str(_REPO_ROOT / "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import _p4a3_application_memory_live_evidence_support as support  # noqa: E402

POSITIVE_OUTCOMES = {"ADMITTED", "READ_COMPLETE", "CORRECTED", "DELETED"}


def test_refusal_cases_are_the_expected_set():
    assert set(support.REFUSAL_CASES) == {
        "REQUEST_INVALID_TTL",
        "SOURCE_REVALIDATION_FAILED",
        "AUTHORIZATION_SCOPE_MISMATCH",
        "ENTRY_NOT_FOUND",
        "ENTRY_NOT_ACTIVE",
        "ENTRY_EXPIRED",
        "BUDGET_BREACH",
    }


def test_every_refusal_case_is_zero_mutation_and_zero_provider():
    results = support.run_refusals()
    assert len(results) == len(support.REFUSAL_CASES)
    for row in results:
        assert row["final_outcome"] not in POSITIVE_OUTCOMES, row
        assert row["appended_entries"] == 0, row
        assert row["appended_tombstones"] == 0, row
        assert row["mutations"] == 0, row
        assert row["provider_attempts"] == 0, row


def test_refusals_do_not_dispatch_a_provider():
    provider = support._GuardProvider()
    support.run_refusals(provider)
    assert provider.calls == 0


def test_source_ref_has_valid_digest_shape():
    source = support.source_ref()
    assert len(source.source_content_digest_sha256) == 64
    assert len(source.provenance_digest_sha256) == 64
