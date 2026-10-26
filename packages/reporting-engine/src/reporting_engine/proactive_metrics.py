"""Exact rational numerical defaults for the P5-A2 first method."""
from __future__ import annotations

from fractions import Fraction
from math import ceil, floor
from statistics import median

from .proactive_models import ProactiveRefusal


def count_value(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 500:
        raise ProactiveRefusal("INPUT_INVALID")
    return value


def baseline(counts: list[int]) -> Fraction:
    if len(counts) < 6:
        raise ProactiveRefusal("INSUFFICIENT_HISTORY")
    return Fraction(median([count_value(x) for x in counts[-6:]]))


def display(value: Fraction) -> int:
    return max(0, round(value))  # Fraction.__round__: nearest, ties to even.


def band(raw_forecast: Fraction, residuals: list[Fraction]) -> tuple[int, int]:
    if len(residuals) != 6:
        raise ProactiveRefusal("CALIBRATION_UNAVAILABLE")
    radius = max(residuals)
    return max(0, floor(raw_forecast - radius)), ceil(raw_forecast + radius)


def signals(counts: list[int]) -> dict:
    if len(counts) < 12:
        raise ProactiveRefusal("INSUFFICIENT_HISTORY")
    recent = [count_value(v) for v in counts[-6:]]
    previous = [count_value(v) for v in counts[-12:-6]]
    change = Fraction(median(recent)) - Fraction(median(previous))
    base = Fraction(median(previous))
    trend = "NO_TREND"
    if abs(change) >= 3 and abs(change) * 2 >= max(Fraction(1), base):
        trend = "UP" if change > 0 else "DOWN"
    prior = [count_value(v) for v in counts[-7:-1]]
    center = Fraction(median(prior))
    mad = Fraction(median([abs(Fraction(v) - center) for v in prior]))
    anomalous = abs(Fraction(counts[-1]) - center) >= max(Fraction(3), 2 * mad)
    return {"trend": trend, "trend_delta": str(change), "anomaly": anomalous,
            "anomaly_direction": ("UP" if counts[-1] > center else "DOWN") if anomalous else None}
