"""REST adapter for the transparent basketball baseline model."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .prediction import ModelConfig, TeamForm, predict_matchup

router = APIRouter(tags=["predictions"])


class TeamInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    points_for_per_game: float = Field(gt=0)
    points_against_per_game: float = Field(gt=0)
    pace: float = Field(gt=0)


class BasketballPredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    home: TeamInput
    away: TeamInput
    home_court_points: float = 2.0
    margin_standard_deviation: float = Field(default=12.0, gt=0)
    total_standard_deviation: float = Field(default=18.0, gt=0)
    market_total: float | None = Field(default=None, gt=0)
    market_home_handicap: float | None = None


@router.post("/v1/predictions/basketball")
async def basketball_prediction(payload: BasketballPredictionInput):
    """Calculate a baseline projection from user-supplied team aggregates.

    This endpoint does not fetch or infer missing team statistics. The caller
    must supply values available at the prediction timestamp.
    """
    try:
        result = predict_matchup(
            TeamForm(**payload.home.model_dump()),
            TeamForm(**payload.away.model_dump()),
            config=ModelConfig(
                home_court_points=payload.home_court_points,
                margin_standard_deviation=payload.margin_standard_deviation,
                total_standard_deviation=payload.total_standard_deviation,
            ),
            market_total=payload.market_total,
            market_home_handicap=payload.market_home_handicap,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result
