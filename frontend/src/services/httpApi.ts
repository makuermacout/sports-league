import { LeagueApiError } from "../types";
import type { ApiError, LeagueApi, Match, StandingRow, Team } from "../types";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8091";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    throw new LeagueApiError(
      "unreachable",
      "Cannot reach the scoreboard server. Check that the backend is running.",
    );
  }

  if (!response.ok) {
    let payload: { error?: ApiError } | undefined;
    try {
      payload = (await response.json()) as { error?: ApiError };
    } catch {
      payload = undefined;
    }
    throw new LeagueApiError(
      payload?.error?.code ?? "request_failed",
      payload?.error?.message ?? `Request failed (${response.status}).`,
    );
  }

  return (await response.json()) as T;
}

export const httpApi: LeagueApi = {
  async listTeams() {
    const data = await request<{ teams: Team[] }>("/teams");
    return data.teams;
  },
  async createTeam(name) {
    return request<Team>("/teams", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  },
  async listMatches() {
    const data = await request<{ matches: Match[] }>("/matches");
    return data.matches;
  },
  async createMatch(input) {
    return request<Match>("/matches", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },
  async getStandings() {
    const data = await request<{ rows: StandingRow[] }>("/standings");
    return data.rows;
  },
};
