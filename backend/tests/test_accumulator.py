from app.standings import StandingAccumulator


def test_goal_difference_and_points() -> None:
    row = StandingAccumulator(team_id="1", team_name="X")
    row.apply(2, 1)
    row.apply(0, 0)
    row.apply(1, 4)
    assert row.played == 3
    assert row.won == 1
    assert row.drawn == 1
    assert row.lost == 1
    assert row.goals_for == 3
    assert row.goals_against == 5
    assert row.goal_difference == -2
    assert row.points == 4
