"""Independent model-validation registry; legacy owner flags are deliberately ignored."""
from __future__ import annotations
import json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPORTS = {"football", "basketball", "tennis"}
DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / "config" / "model_validation.json"

def validation_record(sport: str) -> dict[str, Any]:
    sport = sport.strip().lower()
    if sport not in SPORTS:
        raise ValueError(f"sport must be one of {sorted(SPORTS)}")
    try:
        path = Path(os.getenv("NODE47_MODEL_VALIDATION_PATH", str(DEFAULT_REGISTRY)))
        record = json.loads(path.read_text(encoding="utf-8")).get("sports", {}).get(sport, {})
    except (OSError, ValueError, AttributeError):
        return {"status": "not_validated", "reason": "validation_registry_unavailable"}
    if not isinstance(record, dict):
        return {"status": "not_validated", "reason": "independent_validation_missing"}
    reviewer = record.get("reviewer")
    valid = (
        record.get("status") == "validated"
        and isinstance(record.get("validation_id"), str) and bool(record["validation_id"].strip())
        and isinstance(reviewer, dict) and bool(str(reviewer.get("name", "")).strip())
        and reviewer.get("independence") == "independent"
        and isinstance(record.get("report_url"), str) and record["report_url"].startswith("https://")
        and isinstance(record.get("report_sha256"), str)
        and re.fullmatch(r"[0-9a-fA-F]{64}", record["report_sha256"]) is not None
        and record.get("protocol") == "out_of_sample"
        and isinstance(record.get("validated_at_utc"), str)
    )
    if valid:
        try:
            stamp = datetime.fromisoformat(record["validated_at_utc"].replace("Z", "+00:00"))
            valid = stamp.tzinfo is not None and stamp.utcoffset() == timezone.utc.utcoffset(stamp)
        except ValueError:
            valid = False
    return ({**record, "status": "validated", "reason": None} if valid else
            {"status": "not_validated", "reason": "independent_validation_missing"})

def validation_state(sport: str) -> tuple[bool, str | None]:
    record = validation_record(sport)
    return record["status"] == "validated", record.get("validation_id")

def no_vig_probabilities(decimal_odds: dict[str, float]) -> dict[str, float]:
    if len(decimal_odds) < 2: raise ValueError("at least two mutually exclusive outcomes are required")
    implied = {}
    for outcome, odd in decimal_odds.items():
        if isinstance(odd, bool) or not isinstance(odd, (int, float)) or odd <= 1:
            raise ValueError(f"decimal odds for {outcome} must be greater than 1")
        implied[outcome] = 1.0 / float(odd)
    total = sum(implied.values())
    return {key: value / total for key, value in implied.items()}

def edge_ev(sport: str, model_probability: float, decimal_odds: float,
            market_probability_no_vig: float | None = None) -> dict[str, Any]:
    if not 0 < model_probability < 1 or decimal_odds <= 1: raise ValueError("invalid probability or odds")
    if market_probability_no_vig is not None and not 0 <= market_probability_no_vig <= 1:
        raise ValueError("market_probability_no_vig must be in [0,1]")
    record = validation_record(sport)
    valid = record["status"] == "validated"
    ev = model_probability * decimal_odds - 1.0
    edge = model_probability - market_probability_no_vig if market_probability_no_vig is not None else None
    eligible = valid and ev > 0
    return {"sport": sport, "model_probability": round(model_probability, 6),
        "decimal_odds": round(decimal_odds, 4),
        "market_probability_no_vig": round(market_probability_no_vig, 6) if market_probability_no_vig is not None else None,
        "edge_probability_points": round(edge * 100, 3) if edge is not None else None,
        "ev_per_unit": round(ev, 6), "ev_percent": round(ev * 100, 3),
        "model_validated": valid, "validation_status": record["status"],
        "validation_id": record.get("validation_id"), "validation_report_url": record.get("report_url"),
        "validation_report_sha256": record.get("report_sha256"),
        "decision": "VALUE_CANDIDATE" if eligible else "NO BET", "bet_eligible": eligible,
        "block_reason": None if eligible else ("model_not_independently_validated" if not valid else "non_positive_ev")}

def stake_u(sport: str, model_probability: float, decimal_odds: float, bankroll_units: float,
            kelly_fraction: float = 0.25, max_stake_u: float = 1.0) -> dict[str, Any]:
    if bankroll_units <= 0: raise ValueError("bankroll_units must be greater than zero")
    if not 0 < kelly_fraction <= 0.25: raise ValueError("kelly_fraction must be in (0, 0.25]")
    if not 0 < max_stake_u <= 1.0: raise ValueError("max_stake_u must be in (0, 1.0]")
    value = edge_ev(sport, model_probability, decimal_odds)
    common = {"sport": sport, "bankroll_u": round(bankroll_units, 4),
        "validation_id": value["validation_id"], "validation_status": value["validation_status"],
        "validation_report_url": value["validation_report_url"],
        "unit_definition": "1 U is a user-defined risk unit; bankroll_units is expressed in U",
        "kelly_fraction": kelly_fraction, "max_stake_u": max_stake_u}
    if not value["bet_eligible"]:
        return {**common, "decision": "NO BET", "stake_u": 0.0, "reason": value["block_reason"]}
    b = decimal_odds - 1.0
    full = max(0.0, (b * model_probability - (1.0 - model_probability)) / b)
    raw = bankroll_units * full * kelly_fraction
    return {**common, "decision": "BET", "stake_u": round(min(raw, max_stake_u), 4),
        "uncapped_stake_u": round(raw, 4), "full_kelly_fraction_of_bankroll": round(full, 6),
        "reason": "independently_validated_model_and_positive_ev"}
