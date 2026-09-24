"""Schema tests: the database is built correctly from nothing, and the database
itself (not just the Python code) enforces the rules."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.db import init_db

pytestmark = pytest.mark.integration


def test_startup_builds_schema_from_empty_database(client: TestClient, empty_db) -> None:
    assert set(inspect(empty_db).get_table_names()) >= {"teams", "matches"}

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/teams").json()["teams"] == []
    assert client.get("/matches").json()["matches"] == []
    assert client.get("/standings").json()["rows"] == []


def test_init_db_is_idempotent(empty_db) -> None:
    init_db(bind=empty_db)
    init_db(bind=empty_db)
    assert set(inspect(empty_db).get_table_names()) >= {"teams", "matches"}


def test_table_columns_match_the_models(schema_db) -> None:
    inspector = inspect(schema_db)
    assert {c["name"] for c in inspector.get_columns("teams")} == {"id", "name"}
    assert {c["name"] for c in inspector.get_columns("matches")} == {
        "id",
        "home_team_id",
        "away_team_id",
        "home_score",
        "away_score",
        "created_at",
    }


def test_team_name_is_unique_in_the_database(schema_db) -> None:
    with Session(schema_db) as session:
        session.add_all([models.Team(name="Dup FC"), models.Team(name="Dup FC")])
        with pytest.raises(IntegrityError):
            session.flush()


def test_match_needs_existing_teams_in_the_database(schema_db) -> None:
    with Session(schema_db) as session:
        session.add(
            models.Match(
                home_team_id=str(uuid.uuid4()),
                away_team_id=str(uuid.uuid4()),
                home_score=1,
                away_score=0,
            )
        )
        with pytest.raises(IntegrityError):
            session.flush()


def test_match_created_at_is_filled_by_the_database(schema_db) -> None:
    with Session(schema_db) as session:
        home = models.Team(name="Home")
        away = models.Team(name="Away")
        session.add_all([home, away])
        session.flush()
        match = models.Match(
            home_team_id=home.id, away_team_id=away.id, home_score=1, away_score=1
        )
        session.add(match)
        session.commit()
        session.refresh(match)
        assert match.created_at is not None
