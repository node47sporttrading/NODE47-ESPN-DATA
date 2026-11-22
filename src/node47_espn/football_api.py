"""REST endpoints for football probability and market comparison."""
from __future__ import annotations


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .football_model import (
    calculate_edge_ev, no_vig_probabilities, predict_football,
)

router = APIRouter(tags=["football-model"])


class SplitInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goals_for_per_match: float = Field(ge=0)
    goals_against_per_match: float = Field(ge=0)
    sample_matches: int = Field(ge=1)


class FootballPredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    home: SplitInput
    away: SplitInput
    max_goals: int = Field(default=10, ge=4, le=15)
    min_sample_matches: int = Field(default=5, ge=1)


class OddsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decimal_odds: dict[str, float]
    model_probabilities: dict[str, float]


class EdgeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model_probability: float = Field(gt=0, lt=1)
    decimal_odds: float = Field(gt=1)
    market_probability_no_vig: float | None = Field(default=None, ge=0, le=1)


@router.post("/v1/predictions/football")
async def football_prediction(payload: FootballPredictionInput):
    try:
        return predict_football(
            payload.home.model_dump(), payload.away.model_dump(),
            max_goals=payload.max_goals,
            min_sample_matches=payload.min_sample_matches,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/markets/no-vig")
async def market_no_vig(payload: OddsInput):
    try:
        market = no_vig_probabilities(payload.decimal_odds)
        missing = set(market) - set(payload.model_probabilities)
        if missing:
            raise ValueError(f"missing model probabilities for outcomes: {sorted(missing)}")
        if abs(sum(float(payload.model_probabilities[k]) for k in market) - 1.0) > 0.02:
            raise ValueError("model probabilities must sum to 1 within 0.02")
        rows = {
            key: calculate_edge_ev(
                float(payload.model_probabilities[key]), float(payload.decimal_odds[key]),
                market_probability_no_vig=market[key],
            )
            for key in market
        }
        return {
            "status": "market_comparison_only",
            "overround_percent": round((sum(1 / x for x in payload.decimal_odds.values()) - 1) * 100, 3),
            "no_vig_probabilities": market,
            "outcomes": rows,
            "warning": "comparaison descriptive uniquement ; utiliser le moteur de mise robot-native /v1/decision/staking/robot pour calculer la mise",
        }
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/markets/edge-ev")
async def market_edge_ev(payload: EdgeInput):
    try:
        return calculate_edge_ev(
            payload.model_probability, payload.decimal_odds,
            market_probability_no_vig=payload.market_probability_no_vig,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
