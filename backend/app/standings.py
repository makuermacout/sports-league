from dataclasses import dataclass, field

from app.models import Match, Team

POINTS_WIN = 3
POINTS_DRAW = 1
POINTS_LOSS = 0


@dataclass
class StandingAccumulator:
    team_id: str
    team_name: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.won * POINTS_WIN + self.drawn * POINTS_DRAW + self.lost * POINTS_LOSS

    def apply(self, scored: int, conceded: int) -> None:
        self.played += 1
        self.goals_for += scored
        self.goals_against += conceded
        if scored > conceded:
            self.won += 1
        elif scored == conceded:
            self.drawn += 1
        else:
            self.lost += 1


def compute_standings(teams: list[Team], matches: list[Match]) -> list[StandingAccumulator]:
    rows = {team.id: StandingAccumulator(team_id=team.id, team_name=team.name) for team in teams}
    for match in matches:
        home = rows.get(match.home_team_id)
        away = rows.get(match.away_team_id)
        if home is None or away is None:
            continue
        home.apply(match.home_score, match.away_score)
        away.apply(match.away_score, match.home_score)
    return sorted(
        rows.values(),
        key=lambda row: (-row.points, -row.goal_difference, -row.goals_for, row.team_name.lower()),
    )
