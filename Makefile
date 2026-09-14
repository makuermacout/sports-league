.PHONY: backend frontend test test-backend test-frontend

backend:
	cd backend && uv sync --extra dev && uv run uvicorn app.main:app --reload --port 8091

frontend:
	cd frontend && npm install && npm run dev:api

test: test-backend test-frontend

test-backend:
	cd backend && uv sync --extra dev && uv run pytest

test-frontend:
	cd frontend && npm install && npm test
