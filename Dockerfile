# syntax=docker/dockerfile:1
#
# One image serves both the API and the built React UI.
# Build context is the repo root:  docker build -t sports-league .

# ---- Stage 1: build the React frontend -------------------------------------
FROM node:22-slim AS frontend
WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# The UI must talk to the real API (not the in-memory mock) and use relative
# URLs, because the API and the UI are served from the same address.
# An empty VITE_API_URL makes requests go to "/teams", "/matches", ...
ARG VITE_USE_MOCK=false
ARG VITE_API_URL=
ENV VITE_USE_MOCK=$VITE_USE_MOCK \
    VITE_API_URL=$VITE_API_URL

RUN npm run build


# ---- Stage 2: install backend dependencies ---------------------------------
FROM python:3.13-slim AS backend-build
ENV UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv

WORKDIR /app
# Only the dependency files first, so this layer is cached until they change.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --extra postgres


# ---- Stage 3: runtime image -------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    STATIC_DIR=/app/static

WORKDIR /app

# Run as a normal user, not root.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data \
    && chown appuser /app/data

COPY --from=backend-build /app/.venv /app/.venv
COPY backend/app ./app
COPY --from=frontend /build/dist ./static

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT', '8000'))"

# PORT is set by platforms like Cloud Run and Render; default 8000 locally.
# --factory because the app is built by create_app().
CMD ["sh", "-c", "uvicorn --factory app.main:create_app --host 0.0.0.0 --port ${PORT:-8000}"]
