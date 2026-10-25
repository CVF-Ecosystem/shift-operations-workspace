"""Pure supplied-history analytical entrypoint; never emits a scheduled run."""
from __future__ import annotations

from datetime import timedelta
from fractions import Fraction

from .proactive_evaluation import evaluate, rational
from .proactive_history import lineage_payload, select_history, validate_input
from .proactive_metrics import band, baseline, display, signals
from .proactive_models import HistoryInput, ProactiveRefusal, digest, result_abstained, POLICY_VERSION


def analyze(source: HistoryInput) -> dict:
    """Return READY or a reasoned ABSTAINED result from supplied canonical reports.

    ``complete`` and actor/scope values are supplied assertions, not proofs of
    current authorization or actual database completeness.
    """
    lineage: str | None = None
    history_context: dict | None = None
    selected_count = 0
    try:
        _, _, as_of = validate_input(source)
        selected = select_history(source, as_of, require_complete=True)
        selected_count = len(selected)
        outer_payload = lineage_payload(source, selected, as_of=as_of)
        lineage = digest(outer_payload)
        history_context = {"actor_assertion": source.actor_id,
                           "complete_assertion": source.complete,
                           "retention_complete_assertion": source.retention_complete,
                           "outer_lineage_payload": outer_payload}
        if selected_count < 12:
            raise ProactiveRefusal("INSUFFICIENT_HISTORY", available_observations=selected_count,
                                   required_observations=12)
        if selected_count < 18:
            raise ProactiveRefusal("CALIBRATION_UNAVAILABLE", available_observations=selected_count,
                                   required_observations=18)
        evaluation = evaluate(source, selected, lineage)
        history_context["training_lineage_payloads"] = evaluation["training_lineage_payloads"]
        history_context["evaluation_payload"] = evaluation["evaluation_payload"]
        if evaluation["assessment_mae"] > evaluation["persistence_mae"]:
            raise ProactiveRefusal("MODEL_UNSUPPORTED")
        if as_of - selected[-1].created_at > timedelta(hours=24):
            raise ProactiveRefusal("STALE")
        if evaluation["drifted"]:
            raise ProactiveRefusal("DRIFTED")
        counts = [o.count for o in selected]
        raw = baseline(counts)
        low, high = band(raw, evaluation["calibration_residuals"])
        return {
            "outcome": "READY", "policy_version": POLICY_VERSION,
            "metric": "snapshot_incident_count", "horizon": "NEXT_ELIGIBLE_SHIFT",
            "observation_count": selected_count, "lineage_digest": lineage,
            "history_context": history_context,
            "evaluation_digest": evaluation["evaluation_digest"],
            "forecast_count": display(raw), "raw_forecast": rational(raw),
            "interval_low": low, "interval_high": high,
            "band_label": "in-sample empirical residual envelope, n=6",
            "assessment_mae": rational(evaluation["assessment_mae"]),
            "persistence_mae": rational(evaluation["persistence_mae"]),
            "calibration_mae": rational(evaluation["calibration_mae"]),
            "in_sample_inclusion": "6/6; not validation",
            "signals": signals(counts),
        }
    except ProactiveRefusal as exc:
        return result_abstained(exc.reason, lineage_digest=lineage, observations=selected_count,
                                diagnostics=exc.diagnostics, history_context=history_context)
