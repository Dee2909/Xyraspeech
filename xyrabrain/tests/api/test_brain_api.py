"""API tests for XyraBrain speech intelligence routes."""

from unittest.mock import AsyncMock, patch
from xyrabrain.app.services.ollama_client import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)


from xyrabrain.app.services.brain_service import brain_service


def test_get_capabilities(test_client):
    response = test_client.get("/api/v1/brain/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "supported_languages" in data
    assert "ta" in data["supported_languages"]
    assert "en" in data["supported_languages"]
    assert "ta-en" in data["supported_languages"]
    assert "supported_emotions" in data
    assert "excited" in data["supported_emotions"]
    assert "supported_styles" in data
    assert "limits" in data


def test_analyze_raw_mode(test_client):
    payload = {
        "text": "Hello world! This is raw mode.",
        "mode": "raw",
        "language": "en",
    }
    response = test_client.post("/api/v1/brain/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert data["speech_text"] == "Hello world! This is raw mode."
    assert data["metadata"]["processing_mode"] == "raw"
    assert len(data["segments"]) == 2


def test_enhance_endpoint(test_client):
    with patch.object(brain_service.client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {
            "language": "en",
            "speech_text": "Good morning! How are you today?",
            "overall_style": "conversational",
            "overall_emotion": "neutral",
            "segments": [
                {
                    "text": "Good morning! How are you today?",
                    "emotion": "neutral",
                    "style": "conversational",
                    "energy": 0.5,
                    "speed": 1.0,
                    "pitch": 1.0,
                    "pause_after_ms": 250,
                }
            ],
        }
        payload = {"text": "good morning how are you today", "language": "en"}
        response = test_client.post("/api/v1/brain/enhance", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["speech_text"] == "Good morning! How are you today?"
        assert data["metadata"]["processing_mode"] == "enhanced"


def test_express_endpoint(test_client):
    with patch.object(brain_service.client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {
            "language": "en",
            "speech_text": "Wow! You actually did it!",
            "overall_style": "enthusiastic",
            "overall_emotion": "excited",
            "segments": [
                {
                    "text": "Wow!",
                    "emotion": "surprised",
                    "style": "enthusiastic",
                    "energy": 0.9,
                    "speed": 1.1,
                    "pitch": 1.05,
                    "emphasis": ["Wow"],
                    "pause_after_ms": 300,
                },
                {
                    "text": "You actually did it!",
                    "emotion": "excited",
                    "style": "enthusiastic",
                    "energy": 0.9,
                    "speed": 1.08,
                    "pitch": 1.02,
                    "emphasis": ["actually"],
                    "pause_after_ms": 0,
                },
            ],
        }
        payload = {"text": "Wow! You actually did it!", "language": "en"}
        response = test_client.post("/api/v1/brain/express", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["overall_emotion"] == "excited"
        assert len(data["segments"]) == 2


def test_empty_text_validation_error(test_client):
    response = test_client.post("/api/v1/brain/express", json={"text": ""})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_unsupported_language_rejection(test_client):
    response = test_client.post(
        "/api/v1/brain/express",
        json={"text": "Bonjour tout le monde", "language": "fr"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_ollama_unavailable_503(test_client):
    with patch.object(brain_service.client, "chat", side_effect=OllamaConnectionError("Connection refused")):
        response = test_client.post(
            "/api/v1/brain/express",
            json={"text": "Hello world", "language": "en"},
        )
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_ollama_timeout_504(test_client):
    with patch.object(brain_service.client, "chat", side_effect=OllamaTimeoutError("Timeout")):
        response = test_client.post(
            "/api/v1/brain/express",
            json={"text": "Hello world", "language": "en"},
        )
        assert response.status_code == 504
        data = response.json()
        assert data["error"]["code"] == "INFERENCE_TIMEOUT"
