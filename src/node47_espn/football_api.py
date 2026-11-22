"""REST endpoints for football probability, backtesting, EV and U staking."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .football_model import (
    backtest_football, calculate_edge_ev, calculate_stake_u,
    no_vig_probabilities, predict_football,
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
    model_validated: bool = False


class StakeInput(EdgeInput):
    bankroll_units: float = Field(gt=0)
    kelly_fraction: float = Field(default=0.25, gt=0, le=1)
    max_stake_u: float = Field(default=1.0, gt=0)


class BacktestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rows: list[dict]
    test_fraction: float = Field(default=0.2, gt=0, lt=1)


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
                market_probability_no_vig=market[key], model_validated=False,
            )
            for key in market
        }
        return {
            "status": "market_comparison_only",
            "overround_percent": round((sum(1 / x for x in payload.decimal_odds.values()) - 1) * 100, 3),
            "no_vig_probabilities": market,
            "outcomes": rows,
            "warning": "comparaison descriptive uniquement : le modèle football V0.0.24 reste non validé",
        }
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/markets/edge-ev")
async def market_edge_ev(payload: EdgeInput):
    try:
        return calculate_edge_ev(
            payload.model_probability, payload.decimal_odds,
            market_probability_no_vig=payload.market_probability_no_vig,
            model_validated=payload.model_validated,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/staking/u")
async def staking_u(payload: StakeInput):
    try:
        return calculate_stake_u(
            model_probability=payload.model_probability,
            decimal_odds=payload.decimal_odds,
            bankroll_units=payload.bankroll_units,
            model_validated=payload.model_validated,
            kelly_fraction=payload.kelly_fraction,
            max_stake_u=payload.max_stake_u,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/backtests/football")
async def football_backtest(payload: BacktestInput):
    try:
        return backtest_football(payload.rows, test_fraction=payload.test_fraction)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
