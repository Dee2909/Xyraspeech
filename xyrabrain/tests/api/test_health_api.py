"""API tests for health check endpoints."""

from unittest.mock import AsyncMock, patch


def test_get_health(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "configured_model" in data


def test_get_health_ollama_online(test_client):
    with patch("xyrabrain.app.api.health.ollama_client.check_health", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = {
            "reachable": True,
            "configured_model": "mistral:latest",
            "model_available": True,
            "installed_models": ["mistral:latest"],
        }
        response = test_client.get("/health/ollama")
        assert response.status_code == 200
        data = response.json()
        assert data["reachable"] is True
        assert data["model_available"] is True


def test_get_health_ollama_offline(test_client):
    with patch("xyrabrain.app.api.health.ollama_client.check_health", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = {
            "reachable": False,
            "error": "Connection refused",
            "configured_model": "mistral:latest",
            "model_available": False,
            "installed_models": [],
        }
        response = test_client.get("/health/ollama")
        assert response.status_code == 503
        data = response.json()
        assert data["reachable"] is False
        assert data["model_available"] is False
