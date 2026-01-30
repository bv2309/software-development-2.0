from __future__ import annotations

from fastapi.testclient import TestClient

from ai_accel_api_platform.api.deps import get_db_session
from ai_accel_api_platform.api.v1 import routes_user
from ai_accel_api_platform.core.utils import build_full_name
from ai_accel_api_platform.main import create_app


def test_build_full_name_trims_and_joins():
    assert build_full_name(" Ada ", " Lovelace ") == "Ada Lovelace"


def test_build_full_name_missing_parts():
    assert build_full_name("", "Lovelace") == "Lovelace"
    assert build_full_name("Ada", "") == "Ada"
    assert build_full_name(None, None) == ""


def test_user_full_name_success(monkeypatch):
    app = create_app()

    async def override_get_db_session():
        yield None

    app.dependency_overrides[get_db_session] = override_get_db_session

    monkeypatch.setattr(routes_user, "decode_subject_from_token", lambda token: "user1")

    async def fake_get_user_name_parts(session, username):
        return ("Ada", "Lovelace", True)

    monkeypatch.setattr(routes_user, "get_user_name_parts", fake_get_user_name_parts)

    client = TestClient(app)
    response = client.get("/v1/user", headers={"Authorization": "Bearer test"})
    assert response.status_code == 200
    assert response.json() == {
        "message": "You've successfully fetched user object.",
        "full_name": "Ada Lovelace",
    }


def test_user_full_name_error(monkeypatch):
    app = create_app()

    async def override_get_db_session():
        yield None

    app.dependency_overrides[get_db_session] = override_get_db_session

    monkeypatch.setattr(routes_user, "decode_subject_from_token", lambda token: "user1")

    async def fake_get_user_name_parts(session, username):
        return None

    monkeypatch.setattr(routes_user, "get_user_name_parts", fake_get_user_name_parts)

    client = TestClient(app)
    response = client.get("/v1/user", headers={"Authorization": "Bearer test"})
    assert response.status_code == 400
    assert response.json() == {"message": "System failed to retrieve the data."}
