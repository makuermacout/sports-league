"""Fixtures for integration tests.

Unlike tests/test_api.py (in-memory SQLite + dependency override), these tests
run the real app wiring against a real database:

* the real startup hook (create_app() -> init_db()) builds the schema
* the real get_session commit/rollback logic is used (no dependency override)
* the database is a temp SQLite file by default; set TEST_DATABASE_URL to run
  the exact same tests against Postgres.

WARNING: fixtures here call drop_all(). They refuse to run unless the database
name contains "test", so they can't wipe a real database by accident.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import make_url

from app import db as app_db
from app import main as app_main
from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.config import settings
from app.db import Base, init_db, make_engine
from app.main import create_app


@pytest.fixture(scope="session")
def database_url(tmp_path_factory) -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        path = tmp_path_factory.mktemp("integration_db") / "integration_test.db"
        return f"sqlite:///{path.as_posix()}"

    database_name = (make_url(url).database or "").lower()
    if url == settings.database_url or "test" not in database_name:
        pytest.exit(
            "Refusing to run: TEST_DATABASE_URL must point at a database whose "
            "name contains 'test' (these tests drop all tables).",
            returncode=2,
        )
    return url


@pytest.fixture(scope="session")
def engine(database_url: str):
    eng = make_engine(database_url)
    if eng.dialect.name == "sqlite":
        # SQLite ignores foreign keys unless asked; Postgres always enforces them.
        @event.listens_for(eng, "connect")
        def _enable_foreign_keys(dbapi_connection, _record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    yield eng
    eng.dispose()


@pytest.fixture
def empty_db(engine):
    """A database with no tables at all."""
    Base.metadata.drop_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def schema_db(empty_db):
    """A database with the schema created by init_db(), and no rows."""
    init_db(bind=empty_db)
    return empty_db


@pytest.fixture
def client(empty_db, monkeypatch):
    """The real app, started against an empty database.

    Startup runs the real init_db() hook (pointed at the test engine), and every
    request goes through the real get_session dependency (its sessionmaker is
    re-bound to the test engine for the duration of the test).
    """
    monkeypatch.setitem(app_db.SessionLocal.kw, "bind", empty_db)
    monkeypatch.setattr(app_main, "init_db", lambda: init_db(bind=empty_db))
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def add_team(client: TestClient):
    def _add_team(name: str) -> dict:
        response = client.post("/teams", json={"name": name})
        assert response.status_code == 201, response.text
        return response.json()

    return _add_team


@pytest.fixture
def record_match(client: TestClient):
    def _record_match(home: dict, away: dict, home_score: int, away_score: int) -> dict:
        response = client.post(
            "/matches",
            json={
                "home_team_id": home["id"],
                "away_team_id": away["id"],
                "home_score": home_score,
                "away_score": away_score,
            },
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _record_match
