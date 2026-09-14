# Agent notes

For backend work, use `uv` for dependency management:

```
uv sync --extra dev
uv add <PACKAGE-NAME>
uv run pytest
uv run uvicorn app.main:app --reload --port 8091
```

`product-spec.md` is the product source of truth. `openapi.yaml` is the API
contract. Do not invent extra endpoints, auth, or match editing.

Keep HTTP access in `frontend/src/services/`. Standings are computed on the
server, never in the React UI except inside the mock client.

Regularly commit only when the user asks.
