from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/league.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Folder containing the built frontend. Empty = API only (local dev, tests).
    static_dir: str = ""

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, value: str) -> str:
        # Hosting platforms hand out "postgres://..." or "postgresql://...".
        # SQLAlchemy would pick the psycopg2 driver for those; we ship psycopg 3.
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value.removeprefix(prefix)
        return value


settings = Settings()
