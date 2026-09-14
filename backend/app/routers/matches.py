from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import CreateMatchRequest, MatchList, MatchOut
from app import store

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchList)
def list_matches(session: Session = Depends(get_session)) -> MatchList:
    return MatchList(matches=store.list_matches(session))


@router.post("", response_model=MatchOut, status_code=201)
def create_match(payload: CreateMatchRequest, session: Session = Depends(get_session)) -> MatchOut:
    return store.create_match(session, payload)
