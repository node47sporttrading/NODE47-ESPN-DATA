"""Shared market comparison and U staking with independent sport gates."""
from __future__ import annotations
import os
from typing import Any

SPORTS = {"football", "basketball", "tennis"}
DEFAULT_KELLY_FRACTION = 0.25
DEFAULT_MAX_STAKE_U = 1.0


def validation_state(sport: str) -> tuple[bool, str | None]:
    sport = sport.strip().lower()
    if sport not in SPORTS:
        raise ValueError(f"sport must be one of {sorted(SPORTS)}")
    prefix = f"NODE47_{sport.upper()}_"
    enabled = os.getenv(prefix + "MODEL_VALIDATED", "0").strip() == "1"
    validation_id = os.getenv(prefix + "VALIDATION_ID", "").strip() or None
    return bool(enabled and validation_id), validation_id


def no_vig_probabilities(decimal_odds: dict[str, float]) -> dict[str, float]:
    if len(decimal_odds) < 2:
        raise ValueError("at least two mutually exclusive outcomes are required")
    implied = {}
    for outcome, odd in decimal_odds.items():
        if isinstance(odd, bool) or not isinstance(odd, (int, float)) or odd <= 1:
            raise ValueError(f"decimal odds for {outcome} must be greater than 1")
        implied[outcome] = 1.0 / float(odd)
    total = sum(implied.values())
    return {key: value / total for key, value in implied.items()}


def edge_ev(sport: str, model_probability: float, decimal_odds: float,
            market_probability_no_vig: float | None = None) -> dict[str, Any]:
    if not 0 < model_probability < 1 or decimal_odds <= 1:
        raise ValueError("model_probability must be in (0,1) and decimal_odds > 1")
    if market_probability_no_vig is not None and not 0 <= market_probability_no_vig <= 1:
        raise ValueError("market_probability_no_vig must be in [0,1]")
    validated, validation_id = validation_state(sport)
    ev = model_probability * decimal_odds - 1.0
    edge = model_probability - market_probability_no_vig if market_probability_no_vig is not None else None
    eligible = validated and ev > 0
    return {
        "sport": sport,
        "model_probability": round(model_probability, 6),
        "decimal_odds": round(decimal_odds, 4),
        "market_probability_no_vig": round(market_probability_no_vig, 6) if market_probability_no_vig is not None else None,
        "edge_probability_points": round(edge * 100, 3) if edge is not None else None,
        "ev_per_unit": round(ev, 6),
        "ev_percent": round(ev * 100, 3),
        "model_validated": validated,
        "validation_id": validation_id,
        "decision": "VALUE_CANDIDATE" if eligible else "NO BET",
        "bet_eligible": eligible,
        "block_reason": None if eligible else ("model_not_validated" if not validated else "non_positive_ev"),
    }


def stake_u(sport: str, model_probability: float, decimal_odds: float,
            bankroll_units: float, kelly_fraction: float = DEFAULT_KELLY_FRACTION,
            max_stake_u: float = DEFAULT_MAX_STAKE_U) -> dict[str, Any]:
    if bankroll_units <= 0:
        raise ValueError("bankroll_units must be greater than zero")
    if not 0 < kelly_fraction <= DEFAULT_KELLY_FRACTION:
        raise ValueError("kelly_fraction must be in (0, 0.25]; quarter Kelly is the maximum")
    if not 0 < max_stake_u <= DEFAULT_MAX_STAKE_U:
        raise ValueError("max_stake_u must be in (0, 1.0]; 1 U is the per-selection cap")
    value = edge_ev(sport, model_probability, decimal_odds)
    common = {
        "sport": sport, "bankroll_u": round(bankroll_units, 4),
        "validation_id": value["validation_id"],
        "unit_definition": "1 U is a user-defined risk unit; bankroll_units is expressed in U",
        "kelly_fraction": kelly_fraction, "max_stake_u": max_stake_u,
    }
    if not value["bet_eligible"]:
        return {**common, "decision": "NO BET", "stake_u": 0.0, "reason": value["block_reason"]}
    b = decimal_odds - 1.0
    full_kelly = max(0.0, (b * model_probability - (1.0 - model_probability)) / b)
    raw = bankroll_units * full_kelly * kelly_fraction
    return {
        **common, "decision": "BET", "stake_u": round(min(raw, max_stake_u), 4),
        "uncapped_stake_u": round(raw, 4),
        "full_kelly_fraction_of_bankroll": round(full_kelly, 6),
        "reason": "validated_model_and_positive_ev",
    }
