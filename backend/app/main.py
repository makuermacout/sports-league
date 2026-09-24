from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import init_db
from app.errors import ApiError
from app.routers import matches, standings, teams
from app.schemas import ErrorBody, ErrorResponse, Health


def create_app(*, init_database: bool = True) -> FastAPI:
    app = FastAPI(
        title="Sports-League Scoreboard API",
        version="1.0.0",
        description="Single-league teams, append-only match results, and computed standings.",
    )
    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(teams.router)
    app.include_router(matches.router)
    app.include_router(standings.router)

    @app.get("/health", response_model=Health)
    def health() -> Health:
        return Health()

    @app.exception_handler(ApiError)
    async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
        body = ErrorResponse(error=ErrorBody(code=exc.code, message=exc.message))
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorBody(code="validation_error", message=_first_validation_message(exc))
        )
        return JSONResponse(status_code=400, content=body.model_dump())

    if init_database:
        @app.on_event("startup")
        def on_startup() -> None:
            init_db()

    # Serve the built frontend (Docker image). This must stay LAST: the "/"
    # mount matches every path, so the API routes above have to be registered
    # first to take priority.
    if settings.static_dir:
        static_dir = Path(settings.static_dir)
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=static_dir, html=True), name="ui")

    return app


def _first_validation_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Request validation failed."
    err = errors[0]
    loc = ".".join(str(part) for part in err.get("loc", []) if part != "body")
    msg = err.get("msg", "Invalid request.")
    return f"{loc}: {msg}" if loc else msg
