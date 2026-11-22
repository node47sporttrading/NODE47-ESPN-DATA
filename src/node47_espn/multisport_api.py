"""REST API for tennis baseline and shared multisport EV/U decisions."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .tennis_model import predict_tennis, backtest_tennis
from .multisport_decision import edge_ev, stake_u, no_vig_probabilities

router = APIRouter(tags=["multisport-decision"])

class PlayerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    overall_elo: float = Field(ge=0)
    matches_played: int = Field(ge=0)
    surface_elo: float | None = Field(default=None, ge=0)

class TennisInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    player_a: PlayerInput
    player_b: PlayerInput
    surface: str = "unknown"
    best_of: int = Field(default=3, description="3 or 5 sets")

class TennisBacktestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rows: list[dict[str, Any]]
    test_fraction: float = Field(default=0.2, gt=0, lt=1)

class EdgeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sport: str
    model_probability: float = Field(gt=0, lt=1)
    decimal_odds: float = Field(gt=1)
    market_probability_no_vig: float | None = Field(default=None, ge=0, le=1)

class StakeInput(EdgeInput):
    bankroll_units: float = Field(gt=0)
    kelly_fraction: float = Field(default=0.25, gt=0, le=0.25)
    max_stake_u: float = Field(default=1.0, gt=0, le=1.0)

class NoVigInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decimal_odds: dict[str, float]

@router.post("/v1/predictions/tennis")
async def tennis_prediction(payload: TennisInput):
    try:
        return predict_tennis(payload.player_a.model_dump(), payload.player_b.model_dump(),
                              surface=payload.surface, best_of=payload.best_of)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/v1/backtests/tennis")
async def tennis_backtest(payload: TennisBacktestInput):
    try:
        return backtest_tennis(payload.rows, test_fraction=payload.test_fraction)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/v1/decision/no-vig")
async def shared_no_vig(payload: NoVigInput):
    try:
        odds = no_vig_probabilities(payload.decimal_odds)
        return {"status": "market_comparison_only", "no_vig_probabilities": odds,
                "overround_percent": round((sum(1 / x for x in payload.decimal_odds.values()) - 1) * 100, 3)}
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/v1/decision/edge-ev")
async def shared_edge_ev(payload: EdgeInput):
    try:
        return edge_ev(payload.sport, payload.model_probability, payload.decimal_odds,
                       payload.market_probability_no_vig)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/v1/decision/staking/u")
async def shared_staking_u(payload: StakeInput):
    try:
        return stake_u(payload.sport, payload.model_probability, payload.decimal_odds,
                       payload.bankroll_units, payload.kelly_fraction, payload.max_stake_u)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
