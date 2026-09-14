import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import create_app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(engine)

    def override_session():
        session = TestingSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app = create_app(init_database=False)
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(engine)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ac1_add_team_appears_with_zero_standings(client: TestClient) -> None:
    created = client.post("/teams", json={"name": "River FC"})
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "River FC"
    assert body["id"]

    teams = client.get("/teams").json()["teams"]
    assert any(team["name"] == "River FC" for team in teams)

    standings = client.get("/standings").json()["rows"]
    row = next(item for item in standings if item["team_name"] == "River FC")
    assert row["played"] == 0
    assert row["won"] == 0
    assert row["drawn"] == 0
    assert row["lost"] == 0
    assert row["goals_for"] == 0
    assert row["goals_against"] == 0
    assert row["goal_difference"] == 0
    assert row["points"] == 0


def test_ac2_duplicate_team_rejected(client: TestClient) -> None:
    first = client.post("/teams", json={"name": "Harbor United"})
    assert first.status_code == 201
    second = client.post("/teams", json={"name": "Harbor United"})
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "duplicate_team"
    assert "already exists" in second.json()["error"]["message"]


def test_ac3_record_match_appears_in_history(client: TestClient) -> None:
    home = client.post("/teams", json={"name": "North End"}).json()
    away = client.post("/teams", json={"name": "South Side"}).json()
    recorded = client.post(
        "/matches",
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "home_score": 2,
            "away_score": 1,
        },
    )
    assert recorded.status_code == 201
    history = client.get("/matches").json()["matches"]
    assert history[0]["id"] == recorded.json()["id"]
    assert history[0]["home_score"] == 2
    assert history[0]["away_score"] == 1


def test_ac4_win_updates_won_lost_and_points(client: TestClient) -> None:
    home = client.post("/teams", json={"name": "Alpha"}).json()
    away = client.post("/teams", json={"name": "Beta"}).json()
    client.post(
        "/matches",
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "home_score": 3,
            "away_score": 0,
        },
    )
    rows = {row["team_name"]: row for row in client.get("/standings").json()["rows"]}
    assert rows["Alpha"]["won"] == 1
    assert rows["Alpha"]["lost"] == 0
    assert rows["Alpha"]["points"] == 3
    assert rows["Alpha"]["goal_difference"] == 3
    assert rows["Beta"]["lost"] == 1
    assert rows["Beta"]["won"] == 0
    assert rows["Beta"]["points"] == 0


def test_ac5_draw_gives_one_point_each(client: TestClient) -> None:
    home = client.post("/teams", json={"name": "Cedar"}).json()
    away = client.post("/teams", json={"name": "Maple"}).json()
    client.post(
        "/matches",
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "home_score": 1,
            "away_score": 1,
        },
    )
    rows = {row["team_name"]: row for row in client.get("/standings").json()["rows"]}
    assert rows["Cedar"]["drawn"] == 1
    assert rows["Maple"]["drawn"] == 1
    assert rows["Cedar"]["points"] == 1
    assert rows["Maple"]["points"] == 1


def test_ac6_unknown_or_same_team_rejected(client: TestClient) -> None:
    team = client.post("/teams", json={"name": "Solo"}).json()
    missing = client.post(
        "/matches",
        json={
            "home_team_id": team["id"],
            "away_team_id": "00000000-0000-0000-0000-000000000000",
            "home_score": 1,
            "away_score": 0,
        },
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "team_not_found"

    same = client.post(
        "/matches",
        json={
            "home_team_id": team["id"],
            "away_team_id": team["id"],
            "home_score": 1,
            "away_score": 0,
        },
    )
    assert same.status_code == 422
    assert same.json()["error"]["code"] == "same_team"


def test_ac7_standings_sort_points_then_gd_then_gf(client: TestClient) -> None:
    names = ["Winners", "GoalDiff", "GoalsFor", "AlsoGoals"]
    teams = {name: client.post("/teams", json={"name": name}).json() for name in names}

    def play(home: str, away: str, hs: int, as_: int) -> None:
        client.post(
            "/matches",
            json={
                "home_team_id": teams[home]["id"],
                "away_team_id": teams[away]["id"],
                "home_score": hs,
                "away_score": as_,
            },
        )

    play("Winners", "GoalDiff", 3, 0)
    play("Winners", "GoalsFor", 3, 1)
    play("Winners", "AlsoGoals", 2, 0)
    play("GoalDiff", "GoalsFor", 3, 0)
    play("GoalDiff", "AlsoGoals", 3, 0)
    play("GoalsFor", "AlsoGoals", 1, 1)

    rows = client.get("/standings").json()["rows"]
    order = [row["team_name"] for row in rows]
    assert order[0] == "Winners"
    assert order[1] == "GoalDiff"
    assert rows[2]["points"] == rows[3]["points"]
    assert rows[2]["goal_difference"] == rows[3]["goal_difference"]
    assert rows[2]["goals_for"] >= rows[3]["goals_for"]
    assert order[2] == "GoalsFor"
    assert order[3] == "AlsoGoals"


def test_negative_score_rejected(client: TestClient) -> None:
    home = client.post("/teams", json={"name": "One"}).json()
    away = client.post("/teams", json={"name": "Two"}).json()
    response = client.post(
        "/matches",
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "home_score": -1,
            "away_score": 0,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"