from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import CreateTeamRequest, TeamList, TeamOut
from app import store

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=TeamList)
def list_teams(session: Session = Depends(get_session)) -> TeamList:
    return TeamList(teams=store.list_teams(session))


@router.post("", response_model=TeamOut, status_code=201)
def create_team(payload: CreateTeamRequest, session: Session = Depends(get_session)) -> TeamOut:
    return store.create_team(session, payload)
