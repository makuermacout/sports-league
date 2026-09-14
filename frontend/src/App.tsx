import { FormEvent, useEffect, useMemo, useState } from "react";
import { getApi } from "./services";
import { LeagueApiError } from "./types";
import type { LeagueApi, Match, StandingRow, Team } from "./types";

type Props = {
  api?: LeagueApi;
};

function formatGd(value: number): string {
  if (value > 0) return `+${value}`;
  return String(value);
}

function teamName(teams: Team[], id: string): string {
  return teams.find((team) => team.id === id)?.name ?? "Unknown club";
}

export function App({ api = getApi() }: Props) {
  const [teams, setTeams] = useState<Team[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [standings, setStandings] = useState<StandingRow[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [teamNameInput, setTeamNameInput] = useState("");
  const [homeId, setHomeId] = useState("");
  const [awayId, setAwayId] = useState("");
  const [homeScore, setHomeScore] = useState("0");
  const [awayScore, setAwayScore] = useState("0");
  const [busy, setBusy] = useState(false);

  const canRecord = teams.length >= 2;

  async function refresh() {
    const [nextTeams, nextMatches, nextStandings] = await Promise.all([
      api.listTeams(),
      api.listMatches(),
      api.getStandings(),
    ]);
    setTeams(nextTeams);
    setMatches(nextMatches);
    setStandings(nextStandings);
    setLoadError(null);
  }

  useEffect(() => {
    refresh().catch((error: unknown) => {
      const message =
        error instanceof LeagueApiError
          ? error.message
          : "Could not load the league. Try refreshing the page.";
      setLoadError(message);
    });
  }, [api]);

  const leader = standings[0];

  const homeOptions = useMemo(
    () => teams.filter((team) => team.id !== awayId),
    [teams, awayId],
  );
  const awayOptions = useMemo(
    () => teams.filter((team) => team.id !== homeId),
    [teams, homeId],
  );

  async function onAddTeam(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    setBusy(true);
    try {
      await api.createTeam(teamNameInput);
      setTeamNameInput("");
      await refresh();
    } catch (error) {
      setFormError(error instanceof LeagueApiError ? error.message : "Could not add team.");
    } finally {
      setBusy(false);
    }
  }

  async function onRecordMatch(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    setBusy(true);
    try {
      await api.createMatch({
        home_team_id: homeId,
        away_team_id: awayId,
        home_score: Number(homeScore),
        away_score: Number(awayScore),
      });
      setHomeScore("0");
      setAwayScore("0");
      await refresh();
    } catch (error) {
      setFormError(error instanceof LeagueApiError ? error.message : "Could not record match.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="masthead">
        <p className="kicker">One league · one table</p>
        <h1>Matchday Table</h1>
        <p className="lede">
          Record results as they happen. The table is computed on the server: 3 for a
          win, 1 for a draw, 0 for a loss.
        </p>
        {leader && leader.played > 0 ? (
          <p className="leader">
            Top of the table: <strong>{leader.team_name}</strong> · {leader.points} pts
          </p>
        ) : (
          <p className="leader">Add clubs, then post a result to fill the table.</p>
        )}
      </header>

      {loadError ? (
        <div className="banner error" role="alert">
          {loadError}
        </div>
      ) : null}
      {formError ? (
        <div className="banner warn" role="alert">
          {formError}
        </div>
      ) : null}

      <section className="panel table-panel" aria-labelledby="standings-heading">
        <div className="panel-head">
          <h2 id="standings-heading">Standings</h2>
          <span className="meta">{standings.length} clubs</span>
        </div>
        {standings.length === 0 ? (
          <p className="empty">No teams yet. Enroll a club to open the table.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th className="pos">#</th>
                  <th className="club">Club</th>
                  <th>P</th>
                  <th>W</th>
                  <th>D</th>
                  <th>L</th>
                  <th>GF</th>
                  <th>GA</th>
                  <th>GD</th>
                  <th>Pts</th>
                </tr>
              </thead>
              <tbody>
                {standings.map((row, index) => (
                  <tr key={row.team_id}>
                    <td className="pos">{index + 1}</td>
                    <td className="club">{row.team_name}</td>
                    <td>{row.played}</td>
                    <td>{row.won}</td>
                    <td>{row.drawn}</td>
                    <td>{row.lost}</td>
                    <td>{row.goals_for}</td>
                    <td>{row.goals_against}</td>
                    <td>{formatGd(row.goal_difference)}</td>
                    <td className="pts">{row.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="grid">
        <section className="panel" aria-labelledby="add-team-heading">
          <h2 id="add-team-heading">Enroll a club</h2>
          <form onSubmit={onAddTeam}>
            <label htmlFor="team-name">Team name</label>
            <input
              id="team-name"
              maxLength={40}
              value={teamNameInput}
              onChange={(event) => setTeamNameInput(event.target.value)}
              placeholder="e.g. Harbor United"
              required
            />
            <button type="submit" disabled={busy}>
              Add team
            </button>
          </form>
          <ul className="team-list" aria-label="Teams in the league">
            {teams.map((team) => (
              <li key={team.id}>{team.name}</li>
            ))}
          </ul>
        </section>

        <section className="panel" aria-labelledby="record-match-heading">
          <h2 id="record-match-heading">Post a result</h2>
          {canRecord ? (
            <form onSubmit={onRecordMatch}>
              <div className="score-row">
                <div>
                  <label htmlFor="home-team">Home</label>
                  <select
                    id="home-team"
                    value={homeId}
                    onChange={(event) => setHomeId(event.target.value)}
                    required
                  >
                    <option value="">Select club</option>
                    {homeOptions.map((team) => (
                      <option key={team.id} value={team.id}>
                        {team.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="home-score">Home score</label>
                  <input
                    id="home-score"
                    type="number"
                    min={0}
                    step={1}
                    value={homeScore}
                    onChange={(event) => setHomeScore(event.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="score-row">
                <div>
                  <label htmlFor="away-team">Away</label>
                  <select
                    id="away-team"
                    value={awayId}
                    onChange={(event) => setAwayId(event.target.value)}
                    required
                  >
                    <option value="">Select club</option>
                    {awayOptions.map((team) => (
                      <option key={team.id} value={team.id}>
                        {team.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="away-score">Away score</label>
                  <input
                    id="away-score"
                    type="number"
                    min={0}
                    step={1}
                    value={awayScore}
                    onChange={(event) => setAwayScore(event.target.value)}
                    required
                  />
                </div>
              </div>
              <button type="submit" disabled={busy || !homeId || !awayId}>
                Record match
              </button>
            </form>
          ) : (
            <p className="empty">Need two clubs before a match can be recorded.</p>
          )}
        </section>
      </div>

      <section className="panel" aria-labelledby="history-heading">
        <h2 id="history-heading">Match log</h2>
        {matches.length === 0 ? (
          <p className="empty">No results posted yet.</p>
        ) : (
          <ol className="history">
            {matches.map((match) => (
              <li key={match.id}>
                <span className="history-clubs">
                  {teamName(teams, match.home_team_id)} vs {teamName(teams, match.away_team_id)}
                </span>
                <span className="history-score">
                  {match.home_score}–{match.away_score}
                </span>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
