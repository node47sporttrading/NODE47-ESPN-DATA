"""Transparent baseline basketball model (not a trained or calibrated model).

The model combines team offensive efficiency with opponent defensive efficiency,
projects possessions from both teams' pace, and converts the expected margin
to a win probability using an explicit, configurable normal approximation.
All inputs must be known as of the prediction timestamp.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import erf, sqrt
from typing import Any


@dataclass(frozen=True)
class TeamForm:
    name: str
    points_for_per_game: float
    points_against_per_game: float
    pace: float  # possessions per 48 minutes

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("team name is required")
        for key, value in asdict(self).items():
            if key == "name":
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"{key} must be numeric")
            if value <= 0:
                raise ValueError(f"{key} must be greater than zero")


@dataclass(frozen=True)
class ModelConfig:
    home_court_points: float = 2.0
    margin_standard_deviation: float = 12.0
    total_standard_deviation: float = 18.0
    version: str = "nba-baseline-0.1"
    calibrated: bool = False

    def validate(self) -> None:
        if self.margin_standard_deviation <= 0 or self.total_standard_deviation <= 0:
            raise ValueError("standard deviations must be greater than zero")


def _normal_cdf(value: float, mean: float, sd: float) -> float:
    return 0.5 * (1.0 + erf((value - mean) / (sd * sqrt(2.0))))


def _expected_points(team: TeamForm, opponent: TeamForm, possessions: float) -> float:
    offensive_rating = 100.0 * team.points_for_per_game / team.pace
    opponent_defensive_rating = 100.0 * opponent.points_against_per_game / opponent.pace
    expected_rating = (offensive_rating + opponent_defensive_rating) / 2.0
    return expected_rating * possessions / 100.0


def predict_matchup(
    home: TeamForm,
    away: TeamForm,
    *,
    config: ModelConfig | None = None,
    market_total: float | None = None,
    market_home_handicap: float | None = None,
) -> dict[str, Any]:
    """Return a reproducible baseline projection and optional market probabilities.

    market_home_handicap follows the sportsbook convention: a home handicap
    of -5.5 means the home team must win by more than 5.5 to cover.
    """
    home.validate()
    away.validate()
    cfg = config or ModelConfig()
    cfg.validate()
    if market_total is not None and market_total <= 0:
        raise ValueError("market_total must be greater than zero")
    if market_home_handicap is not None and not isinstance(market_home_handicap, (int, float)):
        raise ValueError("market_home_handicap must be numeric")

    possessions = (home.pace + away.pace) / 2.0
    home_points = _expected_points(home, away, possessions) + cfg.home_court_points / 2.0
    away_points = _expected_points(away, home, possessions) - cfg.home_court_points / 2.0
    margin = home_points - away_points
    total = home_points + away_points

    result: dict[str, Any] = {
        "model_version": cfg.version,
        "calibrated": cfg.calibrated,
        "status": "baseline_uncalibrated" if not cfg.calibrated else "calibrated",
        "home_team": home.name,
        "away_team": away.name,
        "projected_possessions": round(possessions, 2),
        "projected_home_points": round(home_points, 2),
        "projected_away_points": round(away_points, 2),
        "projected_margin_home": round(margin, 2),
        "projected_total": round(total, 2),
        "home_win_probability": round(_normal_cdf(margin, 0.0, cfg.margin_standard_deviation), 6),
        "away_win_probability": round(1.0 - _normal_cdf(margin, 0.0, cfg.margin_standard_deviation), 6),
        "assumptions": {
            "home_court_points": cfg.home_court_points,
            "margin_standard_deviation": cfg.margin_standard_deviation,
            "total_standard_deviation": cfg.total_standard_deviation,
            "distribution": "normal_approximation",
            "calibration_required": not cfg.calibrated,
        },
    }
    if market_total is not None:
        result["market_total"] = market_total
        result["over_probability"] = round(
            1.0 - _normal_cdf(market_total, total, cfg.total_standard_deviation), 6
        )
        result["under_probability"] = round(
            _normal_cdf(market_total, total, cfg.total_standard_deviation), 6
        )
    if market_home_handicap is not None:
        result["market_home_handicap"] = market_home_handicap
        # Cover when home margin is greater than -the home handicap.
        result["home_cover_probability"] = round(
            1.0 - _normal_cdf(-market_home_handicap, margin, cfg.margin_standard_deviation), 6
        )
        result["away_cover_probability"] = round(1.0 - result["home_cover_probability"], 6)
    return result


