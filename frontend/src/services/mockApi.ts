import { LeagueApiError } from "../types";
import type { LeagueApi, Match, StandingRow, Team } from "../types";

type Memory = {
  teams: Team[];
  matches: Match[];
};

function newId(): string {
  return crypto.randomUUID();
}

function computeStandings(memory: Memory): StandingRow[] {
  const rows = new Map<string, StandingRow>();
  for (const team of memory.teams) {
    rows.set(team.id, {
      team_id: team.id,
      team_name: team.name,
      played: 0,
      won: 0,
      drawn: 0,
      lost: 0,
      goals_for: 0,
      goals_against: 0,
      goal_difference: 0,
      points: 0,
    });
  }

  const apply = (teamId: string, scored: number, conceded: number) => {
    const row = rows.get(teamId);
    if (!row) return;
    row.played += 1;
    row.goals_for += scored;
    row.goals_against += conceded;
    row.goal_difference = row.goals_for - row.goals_against;
    if (scored > conceded) {
      row.won += 1;
      row.points += 3;
    } else if (scored === conceded) {
      row.drawn += 1;
      row.points += 1;
    } else {
      row.lost += 1;
    }
  };

  for (const match of memory.matches) {
    apply(match.home_team_id, match.home_score, match.away_score);
    apply(match.away_team_id, match.away_score, match.home_score);
  }

  return [...rows.values()].sort((a, b) => {
    if (b.points !== a.points) return b.points - a.points;
    if (b.goal_difference !== a.goal_difference) return b.goal_difference - a.goal_difference;
    if (b.goals_for !== a.goals_for) return b.goals_for - a.goals_for;
    return a.team_name.localeCompare(b.team_name);
  });
}

export function createMockApi(seed?: Partial<Memory>): LeagueApi {
  const memory: Memory = {
    teams: seed?.teams ? [...seed.teams] : [],
    matches: seed?.matches ? [...seed.matches] : [],
  };

  return {
    async listTeams() {
      return [...memory.teams].sort((a, b) => a.name.localeCompare(b.name));
    },
    async createTeam(name) {
      const trimmed = name.trim();
      if (!trimmed || trimmed.length > 40) {
        throw new LeagueApiError("validation_error", "Team name must be 1–40 characters.");
      }
      if (memory.teams.some((team) => team.name === trimmed)) {
        throw new LeagueApiError(
          "duplicate_team",
          "A team with this name already exists in the league.",
        );
      }
      const team = { id: newId(), name: trimmed };
      memory.teams.push(team);
      return team;
    },
    async listMatches() {
      return [...memory.matches].sort((a, b) => b.created_at.localeCompare(a.created_at));
    },
    async createMatch(input) {
      if (input.home_team_id === input.away_team_id) {
        throw new LeagueApiError("same_team", "A match must be between two different teams.");
      }
      if (input.home_score < 0 || input.away_score < 0) {
        throw new LeagueApiError("validation_error", "Scores must be non-negative integers.");
      }
      const home = memory.teams.find((team) => team.id === input.home_team_id);
      const away = memory.teams.find((team) => team.id === input.away_team_id);
      if (!home || !away) {
        throw new LeagueApiError("team_not_found", "One or both teams do not exist in the league.");
      }
      const match: Match = {
        id: newId(),
        ...input,
        created_at: new Date().toISOString(),
      };
      memory.matches.push(match);
      return match;
    },
    async getStandings() {
      return computeStandings(memory);
    },
  };
}

export const mockApi = createMockApi();
