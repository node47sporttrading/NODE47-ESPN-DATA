"""Transparent tennis Elo baseline with surface-specific adjustment."""
from __future__ import annotations

from typing import Any

SURFACES = {"hard", "clay", "grass", "carpet", "unknown"}


def predict_tennis(
    player_a: dict[str, Any],
    player_b: dict[str, Any],
    *,
    surface: str = "unknown",
    best_of: int = 3,
) -> dict[str, Any]:
    """Estimate match-winner probability from pre-match Elo snapshots.

    Each player requires overall_elo and matches_played. Optional surface_elo
    is used only when both players supply it. No match/set/game markets are
    inferred from this single-match-winner model.
    """
    surface = surface.strip().lower()
    if surface not in SURFACES:
        raise ValueError(f"surface must be one of {sorted(SURFACES)}")
    if best_of not in (3, 5):
        raise ValueError("best_of must be 3 or 5")
    for label, player in (("player_a", player_a), ("player_b", player_b)):
        for key in ("name", "overall_elo", "matches_played"):
            if key not in player:
                raise ValueError(f"{label}.{key} is required")
        if not str(player["name"]).strip():
            raise ValueError(f"{label}.name must not be empty")
        for key in ("overall_elo", "matches_played"):
            value = player[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{label}.{key} must be a non-negative number")
        if "surface_elo" in player and player["surface_elo"] is not None:
            value = player["surface_elo"]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{label}.surface_elo must be a non-negative number")

    use_surface = (
        surface != "unknown"
        and player_a.get("surface_elo") is not None
        and player_b.get("surface_elo") is not None
    )
    rating_a = float(player_a["surface_elo"] if use_surface else player_a["overall_elo"])
    rating_b = float(player_b["surface_elo"] if use_surface else player_b["overall_elo"])
    difference = rating_a - rating_b
    if difference >= 0:
        p_a = 1.0 / (1.0 + 10.0 ** (-difference / 400.0))
    else:
        relative = 10.0 ** (difference / 400.0)
        p_a = relative / (1.0 + relative)
    adequate = int(player_a["matches_played"]) >= 10 and int(player_b["matches_played"]) >= 10
    return {
        "model": "tennis_elo_logistic_baseline",
        "model_version": "tennis-elo-baseline-0.1",
        "status": "baseline_uncalibrated",
        "validation_status": "not_validated",
        "betting_eligible": False,
        "player_a": str(player_a["name"]),
        "player_b": str(player_b["name"]),
        "surface": surface,
        "rating_basis": "surface_elo" if use_surface else "overall_elo",
        "best_of": best_of,
        "rating_difference_a_minus_b": round(difference, 2),
        "probabilities": {
            "player_a_win": round(p_a, 6),
            "player_b_win": round(1.0 - p_a, 6),
        },
        "sample_adequacy": "minimum_met" if adequate else "insufficient",
        "matches_played": {
            "player_a": int(player_a["matches_played"]),
            "player_b": int(player_b["matches_played"]),
            "minimum_required": 10,
        },
        "assumptions": [
            "Elo logistic transform with fixed scale 400",
            "Surface adjustment used only when both surface-specific ratings are supplied",
            "No serve/return, fatigue, injury, travel, head-to-head or tournament-level features",
            "Best-of format is metadata only; no set/game score distribution is inferred",
            "No probability calibration or independent out-of-sample validation has been established",
        ],
    }


