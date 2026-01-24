from __future__ import annotations

from ai_accel_api_platform.api.v1 import routes_health


def test_health_endpoint(client, monkeypatch):
    async def fake_db_ping():
        return True

    monkeypatch.setattr(routes_health, "db_ping", fake_db_ping)
    response = client.get("/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["db_ok"] is True
    assert "device" in payload
