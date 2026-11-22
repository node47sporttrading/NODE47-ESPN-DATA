"""Transparent football Poisson baseline, market value and U-based staking.

This module deliberately separates probability generation from validation.
A model output is never considered calibrated merely because its inputs exist.
"""
from __future__ import annotations

from math import exp, factorial, log
from typing import Any


def _poisson_pmf(k: int, lam: float) -> float:
    return exp(-lam) * (lam ** k) / factorial(k)


def _poisson_grid(lam: float, max_goals: int) -> list[float]:
    return [_poisson_pmf(k, lam) for k in range(max_goals + 1)]


def predict_football(
    home: dict[str, Any],
    away: dict[str, Any],
    *,
    max_goals: int = 10,
    min_sample_matches: int = 5,
) -> dict[str, Any]:
    """Estimate 1X2, totals and BTTS from home/away scoring and conceding rates.

    Required home fields: goals_for_per_match, goals_against_per_match,
    sample_matches. Away fields use the same names and refer to away matches.
    Lambda is the arithmetic mean of one team's scoring rate and the opponent's
    conceding rate. This is a transparent baseline, not a fitted/calibrated model.
    """
    for label, team in (("home", home), ("away", away)):
        for key in ("goals_for_per_match", "goals_against_per_match", "sample_matches"):
            if key not in team:
                raise ValueError(f"{label}.{key} is required")
        for key in ("goals_for_per_match", "goals_against_per_match"):
            value = team[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{label}.{key} must be a non-negative number")
        if isinstance(team["sample_matches"], bool) or int(team["sample_matches"]) < 1:
            raise ValueError(f"{label}.sample_matches must be a positive integer")
    if not 4 <= int(max_goals) <= 15:
        raise ValueError("max_goals must be between 4 and 15")
    if min_sample_matches < 1:
        raise ValueError("min_sample_matches must be positive")

    lam_home = (float(home["goals_for_per_match"]) +
                float(away["goals_against_per_match"])) / 2.0
    lam_away = (float(away["goals_for_per_match"]) +
                float(home["goals_against_per_match"])) / 2.0
    if lam_home <= 0 or lam_away <= 0:
        raise ValueError("derived expected goals must be greater than zero")

    hp = _poisson_grid(lam_home, max_goals)
    ap = _poisson_grid(lam_away, max_goals)
    mass = sum(hp) * sum(ap)
    p_home = p_draw = p_away = p_btts = p_over25 = 0.0
    for h, ph in enumerate(hp):
        for a, pa in enumerate(ap):
            probability = ph * pa / mass
            if h > a:
                p_home += probability
            elif h == a:
                p_draw += probability
            else:
                p_away += probability
            if h > 0 and a > 0:
                p_btts += probability
            if h + a >= 3:
                p_over25 += probability

    sample_ok = (
        int(home["sample_matches"]) >= min_sample_matches
        and int(away["sample_matches"]) >= min_sample_matches
    )
    return {
        "model": "independent_poisson_home_away_rates",
        "model_version": "football-poisson-baseline-0.1",
        "model_status": "baseline_uncalibrated",
        "betting_eligible": False,
        "validation_status": "not_validated",
        "sample_adequacy": "minimum_met" if sample_ok else "insufficient",
        "sample_matches": {
            "home_home_split": int(home["sample_matches"]),
            "away_away_split": int(away["sample_matches"]),
            "minimum_required": min_sample_matches,
        },
        "lambda_home": round(lam_home, 4),
        "lambda_away": round(lam_away, 4),
        "probabilities": {
            "home_win": round(p_home, 6),
            "draw": round(p_draw, 6),
            "away_win": round(p_away, 6),
            "over_2_5": round(p_over25, 6),
            "under_2_5": round(1.0 - p_over25, 6),
            "btts_yes": round(p_btts, 6),
            "btts_no": round(1.0 - p_btts, 6),
        },
        "assumptions": [
            "Poisson indépendant pour les buts des deux équipes",
            "Lambda = moyenne du taux offensif de l'équipe et du taux de buts concédés adverse",
            "Pas de correction Dixon-Coles, blessures, compositions ou ajustement de force",
            "La suffisance d'échantillon ne vaut pas calibration statistique",
            "Probabilités non autorisées pour les mises tant que la validation hors échantillon n'est pas acquise",
        ],
    }


def no_vig_probabilities(decimal_odds: dict[str, float]) -> dict[str, float]:
    """Normalize reciprocal decimal odds for a complete mutually-exclusive market."""
    if len(decimal_odds) < 2:
        raise ValueError("at least two mutually exclusive outcomes are required")
    implied = {}
    for outcome, odd in decimal_odds.items():
        if not isinstance(odd, (int, float)) or isinstance(odd, bool) or odd <= 1:
            raise ValueError(f"decimal odds for {outcome} must be greater than 1")
        implied[outcome] = 1.0 / float(odd)
    overround = sum(implied.values())
    return {key: value / overround for key, value in implied.items()}


def calculate_edge_ev(
    model_probability: float,
    decimal_odds: float,
    *,
    market_probability_no_vig: float | None = None,
    model_validated: bool = False,
) -> dict[str, Any]:
    """Calculate value metrics; block betting conclusions unless validation is explicit."""
    if not 0 < model_probability < 1:
        raise ValueError("model_probability must be strictly between 0 and 1")
    if decimal_odds <= 1:
        raise ValueError("decimal_odds must be greater than 1")
    if market_probability_no_vig is not None and not 0 <= market_probability_no_vig <= 1:
        raise ValueError("market_probability_no_vig must be between 0 and 1")
    ev = model_probability * decimal_odds - 1.0
    edge = (model_probability - market_probability_no_vig
            if market_probability_no_vig is not None else None)
    eligible = bool(model_validated and ev > 0)
    return {
        "model_probability": round(model_probability, 6),
        "decimal_odds": round(decimal_odds, 4),
        "market_probability_no_vig": (round(market_probability_no_vig, 6)
                                      if market_probability_no_vig is not None else None),
        "edge_probability_points": round(edge * 100, 3) if edge is not None else None,
        "ev_per_unit": round(ev, 6),
        "ev_percent": round(ev * 100, 3),
        "model_validated": bool(model_validated),
        "bet_eligible": eligible,
        "decision": "VALUE_CANDIDATE" if eligible else "NO BET",
        "block_reason": None if eligible else (
            "model_not_validated" if not model_validated else "non_positive_ev"
        ),
    }


def calculate_stake_u(
    *,
    model_probability: float,
    decimal_odds: float,
    bankroll_units: float,
    model_validated: bool,
    kelly_fraction: float = 0.25,
    max_stake_u: float = 1.0,
) -> dict[str, Any]:
    """Quarter-Kelly default, capped in U. No stake without validated positive EV.

    bankroll_units is the user's total bankroll expressed in U; it is not money.
    """
    if bankroll_units <= 0:
        raise ValueError("bankroll_units must be greater than zero")
    if not 0 < kelly_fraction <= 1:
        raise ValueError("kelly_fraction must be in (0, 1]")
    if max_stake_u <= 0:
        raise ValueError("max_stake_u must be greater than zero")
    value = calculate_edge_ev(
        model_probability, decimal_odds, model_validated=model_validated
    )
    if not value["bet_eligible"]:
        return {
            "decision": "NO BET",
            "stake_u": 0.0,
            "bankroll_u": round(bankroll_units, 4),
            "kelly_fraction": kelly_fraction,
            "max_stake_u": max_stake_u,
            "reason": value["block_reason"],
        }
    b = decimal_odds - 1.0
    q = 1.0 - model_probability
    full_kelly = max(0.0, (b * model_probability - q) / b)
    raw_stake = bankroll_units * full_kelly * kelly_fraction
    stake = min(raw_stake, max_stake_u)
    return {
        "decision": "BET",
        "stake_u": round(stake, 4),
        "bankroll_u": round(bankroll_units, 4),
        "full_kelly_fraction_of_bankroll": round(full_kelly, 6),
        "applied_kelly_fraction": kelly_fraction,
        "uncapped_stake_u": round(raw_stake, 4),
        "max_stake_u": max_stake_u,
        "reason": "validated_model_and_positive_ev",
    }


def backtest_football(rows: list[dict[str, Any]], *, test_fraction: float = 0.2) -> dict[str, Any]:
    """Chronological holdout evaluation of caller-supplied pre-match snapshots.

    Each row needs prediction_time, home, away, actual_home_goals and
    actual_away_goals. Optional decimal_odds_home/draw/away enable paper ROI.
    The function does not train parameters or declare calibration automatically.
    """
    from .evaluation import chronological_split

    train, test = chronological_split(rows, timestamp_key="prediction_time",
                                      test_fraction=test_fraction)
    predictions = []
    brier_terms = []
    log_losses = []
    paper_profit = 0.0
    paper_bets = 0
    for row in test:
        pred = predict_football(row["home"], row["away"])
        probs = pred["probabilities"]
        actual_h, actual_a = int(row["actual_home_goals"]), int(row["actual_away_goals"])
        outcome = "home_win" if actual_h > actual_a else "draw" if actual_h == actual_a else "away_win"
        pvec = [probs["home_win"], probs["draw"], probs["away_win"]]
        yvec = [1 if outcome == x else 0 for x in ("home_win", "draw", "away_win")]
        brier_terms.append(sum((p - y) ** 2 for p, y in zip(pvec, yvec)) / 3.0)
        log_losses.append(-log(max(probs[outcome], 1e-15)))
        odds_keys = ("decimal_odds_home", "decimal_odds_draw", "decimal_odds_away")
        if all(k in row and row[k] is not None for k in odds_keys):
            candidates = [
                (probs["home_win"], float(row[odds_keys[0]]), "home_win"),
                (probs["draw"], float(row[odds_keys[1]]), "draw"),
                (probs["away_win"], float(row[odds_keys[2]]), "away_win"),
            ]
            probability, odd, selection = max(candidates, key=lambda x: x[0])
            paper_profit += odd - 1.0 if selection == outcome else -1.0
            paper_bets += 1
        predictions.append({
            "prediction_time": row["prediction_time"],
            "outcome": outcome,
            "probabilities": probs,
            "actual_score": f"{actual_h}-{actual_a}",
        })
    result = {
        "status": "evaluation_only_not_model_validation",
        "training_rows": len(train),
        "out_of_sample_rows": len(test),
        "multiclass_brier_score": round(sum(brier_terms) / len(brier_terms), 6),
        "multiclass_log_loss": round(sum(log_losses) / len(log_losses), 6),
        "paper_flat_1u": {
            "bets": paper_bets,
            "profit_u": round(paper_profit, 4),
            "roi_percent": round(100 * paper_profit / paper_bets, 3) if paper_bets else None,
            "warning": "simulation historique, sans validation du modèle ni preuve de rentabilité future",
        },
        "predictions": predictions,
        "validation_status": "not_validated",
    }
    return result
