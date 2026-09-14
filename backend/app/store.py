from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.errors import duplicate_team, same_team, team_not_found, validation_error
from app.schemas import CreateMatchRequest, CreateTeamRequest


def list_teams(session: Session) -> list[models.Team]:
    return list(session.scalars(select(models.Team).order_by(models.Team.name)).all())


def create_team(session: Session, payload: CreateTeamRequest) -> models.Team:
    name = payload.name.strip()
    if not name:
        raise validation_error("Team name cannot be empty.")
    if len(name) > 40:
        raise validation_error("Team name must be 1–40 characters.")
    existing = session.scalar(select(models.Team).where(models.Team.name == name))
    if existing is not None:
        raise duplicate_team()
    team = models.Team(name=name)
    session.add(team)
    try:
        session.flush()
    except IntegrityError as exc:
        raise duplicate_team() from exc
    return team


def list_matches(session: Session) -> list[models.Match]:
    stmt = select(models.Match).order_by(models.Match.created_at.desc(), models.Match.id.desc())
    return list(session.scalars(stmt).all())


def create_match(session: Session, payload: CreateMatchRequest) -> models.Match:
    if payload.home_team_id == payload.away_team_id:
        raise same_team()
    home = session.get(models.Team, payload.home_team_id)
    away = session.get(models.Team, payload.away_team_id)
    if home is None or away is None:
        raise team_not_found()
    match = models.Match(
        home_team_id=payload.home_team_id,
        away_team_id=payload.away_team_id,
        home_score=payload.home_score,
        away_score=payload.away_score,
    )
    session.add(match)
    session.flush()
    return match
