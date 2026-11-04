"""Complete independently frozen positive and refusal HTTP receipts."""

from __future__ import annotations

from pathlib import Path
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "unit"))
from p5a2_source_api_helpers import (  # noqa: E402
    api_oracle, assert_private_headers, frozen_refusal, headers, params, source_client,
)

PATH = "/proactive/source"


@pytest.mark.parametrize("case", api_oracle()["cases"], ids=lambda row: row["case"])
def test_complete_frozen_receipt_over_real_http(case):
    with source_client(case=case, coverage=True) as (client, ledger):
        before = len(ledger.reports)
        response = client.get(PATH, params=params(case), headers=headers())
        assert response.status_code == 200
        assert response.json() == case["expected_receipt"]
        expected_wire = json.dumps(case["expected_receipt"], ensure_ascii=False,
                                   separators=(",", ":")).encode("utf-8")
        assert response.content == expected_wire
        assert response.json()["coverage_mode"] == "SYNTHETIC_FIXTURE"
        assert len(ledger.reports) == before
        assert_private_headers(response)


def test_normal_default_coverage_is_exact_frozen_refusal():
    case = api_oracle()["cases"][0]
    with source_client(case=case) as (client, _):
        response = client.get(PATH, params=params(case), headers=headers())
        assert response.status_code == 200
        assert response.json() == frozen_refusal("COVERAGE_UNKNOWN")
        assert response.content == json.dumps(frozen_refusal("COVERAGE_UNKNOWN"),
                                              separators=(",", ":")).encode("utf-8")
        assert_private_headers(response)


def test_blank_server_instance_refuses_before_coverage():
    case = api_oracle()["cases"][0]
    with source_client(case=case, coverage=True, instance="") as (client, _):
        response = client.get(PATH, params=params(case), headers=headers())
        assert response.json() == frozen_refusal("SOURCE_UNAVAILABLE")
        assert_private_headers(response)


def test_empty_assignment_precedes_coverage_and_has_no_body_read():
    case = api_oracle()["cases"][0]
    with source_client(case=case, coverage=True) as (client, ledger):
        ledger.assignments.clear()
        ledger.reports.clear()
        response = client.get(PATH, params=params(case), headers=headers())
        assert response.json() == frozen_refusal("ACCESS_DENIED")
        assert_private_headers(response)


def test_501_preflight_refuses_before_report_body_or_coverage():
    case = api_oracle()["cases"][0]
    with source_client(case=case, coverage=True) as (client, ledger):
        from datetime import timedelta
        from uuid import NAMESPACE_DNS, uuid5
        from operations_domain.models import Shift
        from operations_domain.assignment_models import ShiftAssignment
        from datetime import datetime

        end = datetime.fromisoformat(case["coverage_seed"]["query_end"].replace("Z", "+00:00"))
        for index in range(36, 501):
            shift_id = uuid5(NAMESPACE_DNS, f"p5a2-api-cap-{index}")
            ledger.shifts[shift_id] = Shift(
                shift_id=shift_id, name=f"CAP-{index}", starts_at=end-timedelta(hours=2),
                ends_at=end-timedelta(hours=1), created_at=end-timedelta(hours=3),
            )
            assignment_id = uuid5(NAMESPACE_DNS, f"p5a2-api-cap-assignment-{index}")
            ledger.assignments[assignment_id] = ShiftAssignment(
                assignment_id=assignment_id, shift_id=shift_id,
                user_id="PUBLIC_ACTOR", assigned_by="PUBLIC_ACTOR",
                assigned_at=end-timedelta(hours=3),
            )
        response = client.get(PATH, params=params(case), headers=headers())
        assert response.json() == frozen_refusal("SCOPE_INCOMPLETE")
        assert_private_headers(response)
