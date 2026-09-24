import pytest

from app.config import Settings


@pytest.mark.parametrize(
    "raw",
    ["postgres://u:p@host:5432/db", "postgresql://u:p@host:5432/db"],
)
def test_platform_postgres_urls_use_the_psycopg_driver(raw: str) -> None:
    assert Settings(database_url=raw).database_url == "postgresql+psycopg://u:p@host:5432/db"


def test_explicit_driver_and_sqlite_urls_are_left_alone() -> None:
    explicit = "postgresql+psycopg://u:p@host:5432/db"
    assert Settings(database_url=explicit).database_url == explicit
    assert Settings(database_url="sqlite:///./x.db").database_url == "sqlite:///./x.db"
