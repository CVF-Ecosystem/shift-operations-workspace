"""Chronological fold reconstruction; no current-state leakage."""
from __future__ import annotations

from datetime import timedelta
from fractions import Fraction

from .proactive_history import lineage_payload, select_history
from .proactive_metrics import baseline
from .proactive_models import HistoryInput, Observation, ProactiveRefusal, digest, stamp, POLICY_VERSION


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def evaluate(source: HistoryInput, selected: list[Observation], outer_lineage: str) -> dict:
    if len(selected) < 18:
        floor = 12 if len(selected) < 12 else 18
        raise ProactiveRefusal("INSUFFICIENT_HISTORY" if floor == 12 else "CALIBRATION_UNAVAILABLE",
                               available_observations=len(selected), required_observations=floor)
    folds = []
    training_payloads = []
    for target in selected[-12:]:
        try:
            origin = target.cutoff - timedelta(microseconds=1)
        except OverflowError as exc:
            raise ProactiveRefusal("TIME_AMBIGUOUS") from exc
        training = select_history(source, origin, require_complete=False,
                                  before=target.order, exclude_shift=target.shift_id)
        if len(training) < 6:
            raise ProactiveRefusal("CALIBRATION_UNAVAILABLE", available_training=len(training),
                                   required_training=6, available_folds=len(folds), required_folds=12)
        prediction = baseline([o.count for o in training])
        comparator = Fraction(training[-1].count)
        error = abs(Fraction(target.count) - prediction)
        training_payload = lineage_payload(source, training, as_of=origin, training=True)
        training_payloads.append(training_payload)
        folds.append({
            "origin_cutoff": stamp(origin), "target_shift_id": str(target.shift_id),
            "target_report_id": str(target.report_id), "target_version": target.version,
            "target_digest": target.snapshot_digest, "target_availability": stamp(target.created_at),
            "training_lineage_digest": digest(training_payload),
            "prediction_numerator": prediction.numerator, "prediction_denominator": prediction.denominator,
            "comparator": rational(comparator), "target_count": target.count,
            "absolute_residual": rational(error),
        })
    assessment = folds[:6]
    calibration = folds[6:]
    assessment_mae = sum((Fraction(f["absolute_residual"]) for f in assessment), Fraction()) / 6
    persistence_mae = sum((abs(Fraction(f["target_count"]) - Fraction(f["comparator"])) for f in assessment), Fraction()) / 6
    calibration_errors = [Fraction(f["absolute_residual"]) for f in calibration]
    calibration_mae = sum(calibration_errors, Fraction()) / 6
    evaluation_payload = {"lineage_digest": outer_lineage, "policy_version": POLICY_VERSION, "folds": folds}
    evaluation_digest = digest(evaluation_payload)
    return {"folds": folds, "assessment_mae": assessment_mae,
            "persistence_mae": persistence_mae, "calibration_mae": calibration_mae,
            "calibration_residuals": calibration_errors, "evaluation_digest": evaluation_digest,
            "evaluation_payload": evaluation_payload, "training_lineage_payloads": training_payloads,
            "drifted": calibration_mae > max(Fraction(2), Fraction(3, 2) * assessment_mae)}
