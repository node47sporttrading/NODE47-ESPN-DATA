"""Evaluation metrics for chronological basketball backtests."""
from __future__ import annotations

from math import log, sqrt
from typing import Any, Iterable


def chronological_split(rows: Iterable[dict[str, Any]], *, timestamp_key: str = "prediction_time", test_fraction: float = 0.2):
    """Sort observations by prediction time and split without random shuffling."""
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be between 0 and 1")
    ordered = sorted(rows, key=lambda row: row[timestamp_key])
    if len(ordered) < 2:
        raise ValueError("at least two observations are required")
    cut = int(len(ordered) * (1.0 - test_fraction))
    cut = min(max(cut, 1), len(ordered) - 1)
    return ordered[:cut], ordered[cut:]


def evaluate_predictions(rows: Iterable[dict[str, Any]], *, probability_key: str = "home_win_probability",
                         outcome_key: str = "home_win", predicted_home_score_key: str = "predicted_home_score",
                         predicted_away_score_key: str = "predicted_away_score",
                         actual_home_score_key: str = "actual_home_score",
                         actual_away_score_key: str = "actual_away_score",
                         calibration_bins: int = 10) -> dict[str, Any]:
    """Evaluate already-generated, out-of-sample predictions.

    Each row must contain a probability in [0,1] and a binary outcome.
    Score errors are calculated only when all four score fields are present.
    """
    data = list(rows)
    if not data:
        raise ValueError("at least one prediction is required")
    if calibration_bins < 1:
        raise ValueError("calibration_bins must be at least one")

    probs, outcomes = [], []
    score_errors = []
    for row in data:
        p = float(row[probability_key])
        y = row[outcome_key]
        if not 0.0 <= p <= 1.0:
            raise ValueError("probabilities must be between zero and one")
        if y not in (0, 1, False, True):
            raise ValueError("outcomes must be binary (0 or 1)")
        probs.append(p)
        outcomes.append(int(y))
        score_keys = (predicted_home_score_key, predicted_away_score_key,
                      actual_home_score_key, actual_away_score_key)
        if all(key in row and row[key] is not None for key in score_keys):
            score_errors.extend([
                float(row[predicted_home_score_key]) - float(row[actual_home_score_key]),
                float(row[predicted_away_score_key]) - float(row[actual_away_score_key]),
            ])

    n = len(data)
    eps = 1e-15
    brier = sum((p - y) ** 2 for p, y in zip(probs, outcomes)) / n
    log_loss = -sum(y * log(max(p, eps)) + (1 - y) * log(max(1 - p, eps))
                    for p, y in zip(probs, outcomes)) / n
    accuracy = sum((p >= 0.5) == bool(y) for p, y in zip(probs, outcomes)) / n

    bins = []
    for index in range(calibration_bins):
        lower = index / calibration_bins
        upper = (index + 1) / calibration_bins
        members = [(p, y) for p, y in zip(probs, outcomes)
                   if lower <= p < upper or (index == calibration_bins - 1 and p == 1.0)]
        if members:
            bins.append({
                "lower": round(lower, 4),
                "upper": round(upper, 4),
                "count": len(members),
                "mean_predicted_probability": round(sum(p for p, _ in members) / len(members), 6),
                "observed_frequency": round(sum(y for _, y in members) / len(members), 6),
            })

    result: dict[str, Any] = {
        "sample_size": n,
        "brier_score": round(brier, 6),
        "log_loss": round(log_loss, 6),
        "accuracy": round(accuracy, 6),
        "calibration_bins": bins,
    }
    if score_errors:
        result["score_mae"] = round(sum(abs(error) for error in score_errors) / len(score_errors), 6)
        result["score_rmse"] = round(sqrt(sum(error ** 2 for error in score_errors) / len(score_errors)), 6)
    return result
