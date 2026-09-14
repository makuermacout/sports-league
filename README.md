# Sports-League Scoreboard

Single-league scoreboard: add teams, record match results, and view a standings
table computed on the server (3 points for a win, 1 for a draw, 0 for a loss).

Product behavior is defined in `product-spec.md`. The HTTP contract is
`openapi.yaml`.

## Layout

- `frontend/` — React + Vite UI
- `backend/` — FastAPI + SQLAlchemy
- `openapi.yaml` — frontend/backend contract
- `docs/ai-usage-report.md` — how AI was used on this project

## Prerequisites

- Node.js 20+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for backend deps (`pip` also works)

## Run locally

Terminal 1 — API (SQLite file at `backend/data/league.db`):

```powershell
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8091
```

Open http://localhost:8091/docs for the generated API explorer.

Terminal 2 — UI talking to that API:

```powershell
cd frontend
npm install
npm run dev:api
```

Open http://localhost:5173.

`npm run dev` (without `:api`) uses an in-memory mock so the UI can be exercised
without the backend.

Equivalent Make targets if you have `make`: `make backend`, `make frontend`,
`make test`.

## Tests

```powershell
cd backend
uv run pytest

cd ..\frontend
npm test
```

## Configuration

| Variable | Where | Default |
|---|---|---|
| `DATABASE_URL` | backend process env | `sqlite:///./data/league.db` |
| `CORS_ORIGINS` | backend process env | `http://localhost:5173,http://127.0.0.1:5173` |
| `VITE_USE_MOCK` | frontend (see `.env.api`) | unset = mock |
| `VITE_API_URL` | frontend | `http://localhost:8091` |

`DATABASE_URL` is a SQLAlchemy URL. SQLite is the local default; Postgres can
replace it later without changing route or standings logic.

## Known v1 limits

See `product-spec.md` section 8: append-only results, no auth, no pagination.
