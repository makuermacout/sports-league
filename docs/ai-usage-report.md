# AI usage report

This file records how AI assistance was used to build the Sports-League
Scoreboard in this stage of the project.

## What the human specified

- Product scope, user stories, and acceptance criteria in `product-spec.md`
- Project shape in `project-overview.md`: frontend, OpenAPI, FastAPI, SQLite,
  tests, `AGENTS.md`, README

## What the assistant generated

- `openapi.yaml` from the spec’s API surface
- React (Vite + TypeScript) UI with a single services layer, mock client, and
  HTTP client
- FastAPI app with SQLAlchemy, SQLite via `DATABASE_URL`, and standings math
  isolated from the database engine
- Backend pytest coverage for AC-1–AC-7 and frontend tests for add-team,
  record-match, and unreachable-backend (AC-8)

## What still needs a human pass

- Click through add-team, duplicate-name error, win/draw results, and refresh
  after restarting the API (SQLite persistence)
- Confirm the generated FastAPI `/docs` matches `openapi.yaml` closely enough
- Decide whether local default should be mock UI or live API (currently
  `npm run dev` = mock, `npm run dev:api` = live)

## Boundaries kept from the spec

No auth, no match edits, no multi-league, no live push updates, no sport-specific
points variants.
