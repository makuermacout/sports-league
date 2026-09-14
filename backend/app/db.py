from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

Base = declarative_base()


def _ensure_sqlite_dir(url: str) -> None:
    if not url.startswith("sqlite:///"):
        return
    path = url.removeprefix("sqlite:///")
    if path in {":memory:", ""} or path.startswith("file:"):
        return
    parent = Path(path).parent
    if str(parent) not in {".", ""}:
        parent.mkdir(parents=True, exist_ok=True)


def make_engine(url: str | None = None):
    db_url = url or settings.database_url
    _ensure_sqlite_dir(db_url)
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(db_url, connect_args=connect_args, future=True)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(bind=None) -> None:
    Base.metadata.create_all(bind or engine)
