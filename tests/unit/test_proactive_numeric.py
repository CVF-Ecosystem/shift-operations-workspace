from __future__ import annotations

from fractions import Fraction
from dataclasses import replace
from datetime import timedelta

import pytest

from proactive_helpers import history
from reporting_engine.proactive_analysis import analyze
from reporting_engine.proactive_metrics import band, baseline, count_value, display, signals
from reporting_engine.proactive_models import ProactiveRefusal


@pytest.mark.parametrize("counts,outcome,forecast,bounds,reason", [
    ([0] * 18, "READY", 0, (0, 0), None),
    ([0] * 12 + [3] * 6, "READY", 3, (0, 6), None),
    ([0] * 17 + [9], "READY", 0, (0, 9), None),
    ([0] * 12 + [6] * 6, "ABSTAINED", None, None, "DRIFTED"),
    (list(range(18)), "ABSTAINED", None, None, "MODEL_UNSUPPORTED"),
    ([8] * 12 + [11] * 6, "READY", 11, (8, 14), None),
    ([1, 2] * 9, "READY", 2, (1, 2), None),
])
def test_prebuild_numeric_vectors(counts, outcome, forecast, bounds, reason):
    result = analyze(history(counts))
    assert result["outcome"] == outcome
    if outcome == "READY":
        assert result["forecast_count"] == forecast
        assert (result["interval_low"], result["interval_high"]) == bounds
    else:
        assert result["reason"] == reason
        assert "forecast_count" not in result and "signals" not in result


def test_exact_numeric_edges_and_signal_thresholds():
    assert baseline([1, 2] * 3) == Fraction(3, 2)
    assert display(Fraction(3, 2)) == 2
    assert display(Fraction(5, 2)) == 2
    assert band(Fraction(3, 2), [Fraction(1, 2)] * 6) == (1, 2)
    assert signals([0] * 12 + [3] * 6)["trend"] == "UP"
    assert signals([8] * 12 + [11] * 6)["trend"] == "NO_TREND"
    assert signals([0] * 17 + [9])["anomaly"] is True
    assert signals([0] * 17 + [2])["anomaly"] is False
    assert count_value(0) == 0 and count_value(500) == 500
    with pytest.raises(ProactiveRefusal, match="INPUT_INVALID"):
        count_value(501)


def test_history_floors_and_zero_filled_missing_forbidden():
    for size, reason, required in [(11, "INSUFFICIENT_HISTORY", 12),
                                   (12, "CALIBRATION_UNAVAILABLE", 18),
                                   (17, "CALIBRATION_UNAVAILABLE", 18)]:
        result = analyze(history([0] * size))
        assert result["outcome"] == "ABSTAINED" and result["reason"] == reason
        assert "forecast_count" not in result
        assert result["diagnostics"] == {"available_observations": size, "required_observations": required}


def test_assessment_calibration_and_raw_band_values():
    step = analyze(history([0] * 12 + [3] * 6))
    assert step["assessment_mae"] == "0/1"
    assert step["calibration_mae"] == "7/4"
    assert step["signals"]["trend"] == "UP"
    alternate = analyze(history([1, 2] * 9))
    assert alternate["raw_forecast"] == "3/2"
    assert alternate["assessment_mae"] == "1/2"
    assert alternate["persistence_mae"] == "1/1"
    assert alternate["band_label"] == "in-sample empirical residual envelope, n=6"


def test_exact_freshness_and_drift_equality_boundaries():
    source = history([0] * 18)
    latest = source.candidates[-1].created_at
    at_24h = replace(source, run_as_of=latest + timedelta(hours=24))
    assert analyze(at_24h)["outcome"] == "READY"
    after_24h = replace(source, run_as_of=latest + timedelta(hours=24, microseconds=1))
    answer = analyze(after_24h)
    assert answer["reason"] == "STALE" and "forecast_count" not in answer
    at_drift = analyze(history([0] * 17 + [12]))
    assert at_drift["outcome"] == "READY" and at_drift["calibration_mae"] == "2/1"
    above_drift = analyze(history([0] * 17 + [13]))
    assert above_drift["outcome"] == "ABSTAINED" and above_drift["reason"] == "DRIFTED"
