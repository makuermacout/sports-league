from app.models import Match, Team
from app.standings import compute_standings


def test_empty_league_has_zero_rows() -> None:
    assert compute_standings([], []) == []


def test_team_with_no_matches_is_zeroed() -> None:
    team = Team(id="t1", name="Idle")
    rows = compute_standings([team], [])
    assert len(rows) == 1
    assert rows[0].played == 0
    assert rows[0].points == 0


def test_away_win_awards_points_to_away_side() -> None:
    home = Team(id="h", name="Home")
    away = Team(id="a", name="Away")
    match = Match(id="m1", home_team_id="h", away_team_id="a", home_score=0, away_score=2)
    rows = {row.team_id: row for row in compute_standings([home, away], [match])}
    assert rows["a"].won == 1
    assert rows["a"].points == 3
    assert rows["h"].lost == 1
    assert rows["h"].points == 0
