"""REST API for tennis baseline and robot-native risk sizing."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .tennis_model import predict_tennis
from .multisport_decision import edge_ev, robot_stake, no_vig_probabilities

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

class EdgeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sport: str
    model_probability: float = Field(gt=0, lt=1)
    decimal_odds: float = Field(gt=1)
    market_probability_no_vig: float | None = Field(default=None, ge=0, le=1)

class RobotStakeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module: str = Field(pattern="^(football|basketball|tennis|corners_cartons)$")
    p_final: float = Field(gt=0, lt=1)
    confidence: float | None = Field(default=None, ge=0, le=100)
    decimal_odds: float = Field(gt=1)
    p_push: float = Field(default=0, ge=0, le=1)
    profile: str = Field(default="STANDARD")
    confidence_penalty_points: float = Field(default=5, ge=0)
    stake_scale: float = Field(default=25, ge=0)
    stake_max: float | None = Field(default=None, ge=0)
    stake_min: float = Field(default=0.5, ge=0)

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

@router.post("/v1/decision/staking/robot")
async def shared_robot_staking(payload: RobotStakeInput):
    try:
        return robot_stake(module=payload.module, p_final=payload.p_final,
            confidence=payload.confidence, decimal_odds=payload.decimal_odds,
            p_push=payload.p_push, profile=payload.profile,
            confidence_penalty_points=payload.confidence_penalty_points,
            stake_scale=payload.stake_scale, stake_max=payload.stake_max,
            stake_min=payload.stake_min)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
