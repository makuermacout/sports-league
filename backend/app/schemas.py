from datetime import datetime

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class Health(BaseModel):
    status: str = "ok"


class TeamOut(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class TeamList(BaseModel):
    teams: list[TeamOut]


class CreateTeamRequest(BaseModel):
    name: str = Field(min_length=1, max_length=40)


class MatchOut(BaseModel):
    id: str
    home_team_id: str
    away_team_id: str
    home_score: int
    away_score: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchList(BaseModel):
    matches: list[MatchOut]


class CreateMatchRequest(BaseModel):
    home_team_id: str
    away_team_id: str
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class StandingRow(BaseModel):
    team_id: str
    team_name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class Standings(BaseModel):
    rows: list[StandingRow]
