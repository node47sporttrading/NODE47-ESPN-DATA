"""NODE.47 market calculations and robot-native risk sizing.

The stake algorithm mirrors robot/src/55-risque.mjs::miseDe.
There is no independent model-validation registry or gate.
"""
from __future__ import annotations
from math import floor, isfinite
from typing import Any

PROFILE_STAKE_MAX = {"PRUDENT": 2.0, "STANDARD": 3.0, "FREQUENT": 3.0}
MODULES = {"football", "basketball", "tennis", "corners_cartons"}

def no_vig_probabilities(decimal_odds: dict[str, float]) -> dict[str, float]:
    if len(decimal_odds) < 2:
        raise ValueError("at least two mutually exclusive outcomes are required")
    implied = {}
    for outcome, odd in decimal_odds.items():
        if isinstance(odd, bool) or not isinstance(odd, (int, float)) or not isfinite(float(odd)) or odd <= 1:
            raise ValueError(f"decimal odds for {outcome} must be greater than 1")
        implied[outcome] = 1.0 / float(odd)
    total = sum(implied.values())
    return {key: value / total for key, value in implied.items()}

def edge_ev(sport: str, model_probability: float, decimal_odds: float,
            market_probability_no_vig: float | None = None) -> dict[str, Any]:
    if not 0 < model_probability < 1 or not isfinite(model_probability):
        raise ValueError("model_probability must be strictly between 0 and 1")
    if decimal_odds <= 1 or not isfinite(decimal_odds):
        raise ValueError("decimal_odds must be greater than 1")
    if market_probability_no_vig is not None and not 0 <= market_probability_no_vig <= 1:
        raise ValueError("market_probability_no_vig must be between 0 and 1")
    ev = model_probability * decimal_odds - 1.0
    edge = model_probability - market_probability_no_vig if market_probability_no_vig is not None else None
    return {
        "sport": sport, "model_probability": round(model_probability, 6),
        "decimal_odds": round(decimal_odds, 4),
        "market_probability_no_vig": round(market_probability_no_vig, 6) if market_probability_no_vig is not None else None,
        "edge_probability_points": round(edge * 100, 3) if edge is not None else None,
        "ev_per_unit": round(ev, 6), "ev_percent": round(ev * 100, 3),
        "decision": "VALUE_CANDIDATE" if ev > 0 else "NO VALUE",
        "bet_eligible": ev > 0, "block_reason": None if ev > 0 else "non_positive_ev",
    }

def _js_round(value: float) -> int:
    return floor(value + 0.5)

def robot_stake(module: str, p_final: float, confidence: float | None,
                decimal_odds: float, p_push: float = 0.0,
                profile: str = "STANDARD",
                confidence_penalty_points: float = 5.0,
                stake_scale: float = 25.0,
                stake_max: float | None = None,
                stake_min: float = 0.5) -> dict[str, Any]:
    """Exact mirror of miseDe(pFinal, confidence, cote, cfg, pPush)."""
    module = str(module).strip().lower()
    if module not in MODULES:
        raise ValueError(f"module must be one of {sorted(MODULES)}")
    profile = str(profile).strip().upper()
    if profile not in {*PROFILE_STAKE_MAX, "CUSTOM"}:
        raise ValueError("profile must be PRUDENT, STANDARD, FREQUENT or CUSTOM")
    for label, value in (("p_final", p_final), ("decimal_odds", decimal_odds),
                         ("confidence_penalty_points", confidence_penalty_points),
                         ("stake_scale", stake_scale), ("stake_min", stake_min)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
            raise ValueError(f"{label} must be a finite number")
    if not 0 < p_final < 1:
        raise ValueError("p_final must be strictly between 0 and 1")
    if decimal_odds <= 1:
        raise ValueError("decimal_odds must be greater than 1")
    if confidence is not None:
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not isfinite(float(confidence)):
            raise ValueError("confidence must be a finite number or null")
        confidence = min(100.0, max(0.0, float(confidence)))
    if isinstance(p_push, bool) or not isinstance(p_push, (int, float)) or not isfinite(float(p_push)) or not 0 <= p_push <= 1:
        raise ValueError("p_push must be between 0 and 1")
    if confidence_penalty_points < 0 or stake_scale < 0 or stake_min < 0:
        raise ValueError("risk parameters must be non-negative")
    if stake_max is None:
        if profile == "CUSTOM":
            raise ValueError("CUSTOM profile requires an explicit stake_max")
        stake_max = PROFILE_STAKE_MAX[profile]
    if isinstance(stake_max, bool) or not isinstance(stake_max, (int, float)) or not isfinite(float(stake_max)) or stake_max < 0:
        raise ValueError("stake_max must be a finite non-negative number")
    if stake_min > stake_max:
        raise ValueError("stake_min cannot exceed stake_max")
    confidence_factor = 1.0 if confidence is None else (100.0 - confidence) / 100.0
    p_cons = max(0.01, float(p_final) - confidence_factor * float(confidence_penalty_points) / 100.0)
    push = max(0.0, float(p_push))
    ev = p_cons * float(decimal_odds) + push - 1.0
    f_star = ev / (float(decimal_odds) - 1.0)
    params = {"profile": profile, "confidence_penalty_points": float(confidence_penalty_points),
              "stake_scale": float(stake_scale), "stake_max_u": float(stake_max),
              "stake_min_u": float(stake_min), "rounding": "0.25 U"}
    base = {"module": module, "profile": profile, "p_final": round(float(p_final), 6),
            "confidence": confidence, "decimal_odds": round(float(decimal_odds), 4),
            "p_push": round(push, 6), "p_cons": round(p_cons, 6), "f_star": round(f_star, 8),
            "risk_parameters": params, "stake_u": 0.0, "mise": 0.0}
    if not isfinite(f_star) or f_star <= 0:
        return {**base, "decision": "NO BET", "reason": "conservative_probability_edge_non_positive"}
    raw = float(stake_scale) * f_star
    capped = min(raw, float(stake_max))
    rounded = _js_round(capped * 4.0) / 4.0
    if rounded < stake_min:
        return {**base, "decision": "NO BET", "uncapped_stake_u": round(raw, 4),
                "rounded_stake_u": round(rounded, 2), "reason": "stake_below_profile_minimum"}
    amount = _js_round(rounded * 100.0) / 100.0
    return {**base, "decision": "BET", "stake_u": amount, "mise": amount,
            "uncapped_stake_u": round(raw, 4), "rounded_stake_u": amount,
            "reason": "robot_native_conservative_kelly"}
