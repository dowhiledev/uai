from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from unified_agent_interface.app import get_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(get_app())

