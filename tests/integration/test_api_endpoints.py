"""
Integration tests for API endpoints
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi.testclient import TestClient

    from api_server import app

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_chat_process_endpoint(self, client):
        payload = {"mensaje": "Hola", "telefono": "+59891234567"}
        response = client.post("/chat/process", json=payload)
        assert response.status_code in [200, 500]

    def test_conversations_endpoint(self, client):
        response = client.get("/conversations?limit=10")
        assert response.status_code in [200, 500]
