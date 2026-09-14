export type ApiError = {
  code: string;
  message: string;
};

export type Team = {
  id: string;
  name: string;
};

export type Match = {
  id: string;
  home_team_id: string;
  away_team_id: string;
  home_score: number;
  away_score: number;
  created_at: string;
};

export type StandingRow = {
  team_id: string;
  team_name: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
};

export type LeagueApi = {
  listTeams: () => Promise<Team[]>;
  createTeam: (name: string) => Promise<Team>;
  listMatches: () => Promise<Match[]>;
  createMatch: (input: {
    home_team_id: string;
    away_team_id: string;
    home_score: number;
    away_score: number;
  }) => Promise<Match>;
  getStandings: () => Promise<StandingRow[]>;
};

export class LeagueApiError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.name = "LeagueApiError";
    this.code = code;
  }
}
