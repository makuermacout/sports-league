from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import StandingRow, Standings
from app.standings import compute_standings
from app import store

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("", response_model=Standings)
def get_standings(session: Session = Depends(get_session)) -> Standings:
    teams = store.list_teams(session)
    matches = store.list_matches(session)
    rows = compute_standings(teams, matches)
    return Standings(
        rows=[
            StandingRow(
                team_id=row.team_id,
                team_name=row.team_name,
                played=row.played,
                won=row.won,
                drawn=row.drawn,
                lost=row.lost,
                goals_for=row.goals_for,
                goals_against=row.goals_against,
                goal_difference=row.goal_difference,
                points=row.points,
            )
            for row in rows
        ]
    )
