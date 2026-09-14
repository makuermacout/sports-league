# Product Spec: Sports-League Scoreboard

## 1. Overview

Sports-League Scoreboard is a small web app for tracking a single league:
teams, match results, and a standings table computed from those results.
Someone (a league organizer) records match results as they happen; anyone
viewing the app sees an up-to-date standings table ranked by points. The app
exercises a full system end to end: frontend, an OpenAPI contract, a
backend, and a database — not just a static table.

This spec keeps scope small enough to build in one module while still
touching every layer of a real system.

## 2. Goals

- Maintain a list of teams in one league.
- Record match results (two teams, their scores) for that league.
- Compute and display a standings table (played, won, drawn, lost, points,
  goal difference) derived from recorded results.
- View a simple match history/log.
- A clean OpenAPI contract between frontend and backend.

## 3. Non-Goals

- **No multi-league / multi-season support.** One league, one ongoing set of
  results, for this version.
- **No fixture scheduling.** Matches are only ever recorded after they
  happen; there is no "upcoming matches" calendar.
- **No authentication or roles.** Anyone using the app can add teams and
  record results; no login, no admin-vs-viewer distinction.
- **No playoffs, brackets, or knockout logic.** Standings are a simple
  round-robin-style points table only.
- **No editing/deleting match results in v1** (recording is append-only);
  correcting a mistake is a known limitation, not solved here.
- **No live/real-time updates** (e.g. WebSockets); the standings table is
  fetched on load/refresh, not pushed.
- **No sport-specific rule variants** (e.g. different points-for-a-win
  conventions across sports) — fixed at 3 points for a win, 1 for a draw,
  0 for a loss, regardless of sport.

## 4. User Stories

### US-1: Add a team
As an organizer, I want to add a team to the league so that it can appear in
match results and standings.
- A team has a name (1–40 characters) and must be unique within the league.
- A newly added team appears in the standings table with all-zero stats.

### US-2: View the team list
As a visitor, I want to see the list of teams in the league so that I know
who's participating.
- Team list is fetched from the backend.

### US-3: Record a match result
As an organizer, I want to record the result of a match between two teams so
that the standings reflect it.
- A result consists of two distinct existing teams and a non-negative
  integer score for each.
- On submission, the match is stored and the standings table updates to
  reflect it (win/draw/loss, points, goal difference, games played).

### US-4: View the standings table
As a visitor, I want to see a standings table ranked by points so that I can
see who's leading the league.
- Table shows, per team: played, won, drawn, lost, goals for, goals against,
  goal difference, points.
- Sorted by points descending; ties broken by goal difference descending,
  then goals for descending.
- Table is fetched from the backend, not computed client-side.

### US-5: View match history
As a visitor, I want to see a log of recorded matches so that I can review
what's happened so far.
- List of matches shown most-recent-first: the two teams and the final
  score.

## 5. Acceptance Criteria (summary, testable)

| ID | Criterion |
|----|-----------|
| AC-1 | Given a league with no teams, adding a team with a valid unique name succeeds and it appears in the team list with zeroed standings. |
| AC-2 | Given a team name that already exists in the league, adding it again is rejected with a clear error. |
| AC-3 | Given two existing distinct teams and two non-negative scores, recording a match succeeds and appears in match history immediately. |
| AC-4 | Given a match result where team A's score > team B's score, team A's "won" count and team B's "lost" count each increase by 1, and points update accordingly (3/0). |
| AC-5 | Given a match result with equal scores, both teams' "drawn" count increases by 1 and each gains 1 point. |
| AC-6 | Given a match referencing a team that doesn't exist in the league, or the same team on both sides, the API rejects it with a validation error. |
| AC-7 | Given multiple recorded matches, the standings table is sorted by points descending, with goal difference then goals-for as tiebreakers. |
| AC-8 | Given the backend is unreachable, the frontend shows an error state on fetch/submit without crashing. |

## 6. Rough Data Model

`Team`
- `id`: server-generated identifier
- `name`: string, 1–40 chars, unique within the league

`Match`
- `id`: server-generated identifier
- `home_team_id`, `away_team_id`: references to `Team`, must differ
- `home_score`, `away_score`: non-negative integers
- `created_at`: timestamp, server-generated

Standings are a derived view over `Match` + `Team`, not stored directly.

## 7. Rough API Surface (to be formalized in `openapi.yaml`)

- `POST /teams` — create `{ name }`, returns the created `Team`.
- `GET /teams` — list all teams.
- `POST /matches` — record `{ home_team_id, away_team_id, home_score, away_score }`, returns the created `Match`.
- `GET /matches` — list matches, most-recent-first.
- `GET /standings` — computed standings table, sorted per US-4.

(Exact request/response shapes, validation rules, and error formats are
defined in the OpenAPI contract, not here — this section only bounds scope.)

## 8. Out-of-Scope Risks / Known Limitations

- No way to correct a mis-entered match result without direct DB access
  (append-only in v1).
- No pagination on match history or team list.
- No concurrency handling beyond what the database gives for free (no
  explicit locking on standings computation).
