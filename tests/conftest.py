from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ai_accel_api_platform.main import create_app


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)
