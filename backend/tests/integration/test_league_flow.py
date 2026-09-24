"""End-to-end flow through the real app and a real database."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.integration


def _standings_by_team(client: TestClient) -> dict[str, dict]:
    return {row["team_name"]: row for row in client.get("/standings").json()["rows"]}


def _play_small_league(add_team, record_match) -> None:
    a = add_team("Team A")
    b = add_team("Team B")
    c = add_team("Team C")
    record_match(a, b, 2, 0)  # A beats B
    record_match(b, c, 1, 1)  # B and C draw
    record_match(c, a, 0, 3)  # A beats C away


def test_small_league_produces_exact_standings(client, add_team, record_match) -> None:
    _play_small_league(add_team, record_match)

    rows = client.get("/standings").json()["rows"]
    assert [row["team_name"] for row in rows] == ["Team A", "Team B", "Team C"]

    by_team = {row["team_name"]: row for row in rows}
    expected = {
        "Team A": dict(played=2, won=2, drawn=0, lost=0, goals_for=5, goals_against=0,
                       goal_difference=5, points=6),
        "Team B": dict(played=2, won=0, drawn=1, lost=1, goals_for=1, goals_against=3,
                       goal_difference=-2, points=1),
        "Team C": dict(played=2, won=0, drawn=1, lost=1, goals_for=1, goals_against=4,
                       goal_difference=-3, points=1),
    }
    for name, fields in expected.items():
        for field, value in fields.items():
            assert by_team[name][field] == value, f"{name}.{field}"

    assert len(client.get("/matches").json()["matches"]) == 3


def test_data_survives_an_app_restart(client, add_team, record_match) -> None:
    _play_small_league(add_team, record_match)
    before = client.get("/standings").json()["rows"]

    # A second app instance starts against the same, already-populated database.
    # Startup runs init_db() again and must not wipe or duplicate anything.
    with TestClient(create_app()) as restarted:
        assert restarted.get("/standings").json()["rows"] == before
        assert len(restarted.get("/teams").json()["teams"]) == 3
        assert len(restarted.get("/matches").json()["matches"]) == 3


def test_rejected_requests_leave_no_rows(client, add_team) -> None:
    team = add_team("Solo")
    ghost = "00000000-0000-0000-0000-000000000000"

    def post_match(home: str, away: str, home_score: int, away_score: int):
        return client.post(
            "/matches",
            json={
                "home_team_id": home,
                "away_team_id": away,
                "home_score": home_score,
                "away_score": away_score,
            },
        )

    assert post_match(team["id"], ghost, 1, 0).status_code == 404
    assert post_match(team["id"], team["id"], 1, 0).status_code == 422
    assert post_match(team["id"], ghost, -1, 0).status_code == 400

    assert client.get("/matches").json()["matches"] == []
    solo = _standings_by_team(client)["Solo"]
    assert solo["played"] == 0
    assert solo["points"] == 0


def test_duplicate_team_with_extra_whitespace_is_rejected(client, add_team) -> None:
    add_team("Rovers")
    response = client.post("/teams", json={"name": "  Rovers  "})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_team"
    assert len(client.get("/teams").json()["teams"]) == 1


def test_overlong_team_name_is_rejected_without_creating_a_team(client) -> None:
    response = client.post("/teams", json={"name": "x" * 41})
    assert 400 <= response.status_code < 500
    assert response.json()["error"]["code"] == "validation_error"
    assert client.get("/teams").json()["teams"] == []


def test_match_history_is_newest_first(client, engine, add_team, record_match) -> None:
    if engine.dialect.name == "sqlite":
        pytest.skip(
            "created_at has 1-second resolution on SQLite, so two matches recorded "
            "in the same second tie and fall back to random UUID order."
        )
    a = add_team("Team A")
    b = add_team("Team B")
    first = record_match(a, b, 1, 0)
    second = record_match(b, a, 2, 2)

    history = client.get("/matches").json()["matches"]
    assert [m["id"] for m in history] == [second["id"], first["id"]]
