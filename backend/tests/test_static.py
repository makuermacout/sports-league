from fastapi.testclient import TestClient

from app.config import settings
from app.main import create_app


def test_built_frontend_is_served_and_api_routes_still_win(tmp_path, monkeypatch) -> None:
    (tmp_path / "index.html").write_text("<h1>Scoreboard UI</h1>")
    monkeypatch.setattr(settings, "static_dir", str(tmp_path))

    with TestClient(create_app(init_database=False)) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Scoreboard UI" in page.text
        assert client.get("/health").json() == {"status": "ok"}


def test_no_ui_is_mounted_when_static_dir_is_unset(monkeypatch) -> None:
    monkeypatch.setattr(settings, "static_dir", "")

    with TestClient(create_app(init_database=False)) as client:
        assert client.get("/").status_code == 404
        assert client.get("/health").status_code == 200
