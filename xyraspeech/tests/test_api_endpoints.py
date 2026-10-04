"""API Integration Tests for XyraSpeech."""

import io
from unittest.mock import AsyncMock, patch
from xyraspeech.app.schemas.stt import STTResponse


def test_get_health(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_voices(test_client):
    response = test_client.get("/api/v1/voices")
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) == 2
    assert any(v["id"] == "ta_pallavi" for v in data["voices"])
    assert any(v["id"] == "en_neerja" for v in data["voices"])


def test_post_tts_english(test_client):
    payload = {
        "text": "Hello, welcome to XyraSpeech voice studio!",
        "language": "en",
        "voice_id": "en_neerja",
    }
    response = test_client.post("/api/v1/tts", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 1000


def test_post_tts_tamil(test_client):
    payload = {
        "text": "வணக்கம்! XyraSpeech தளத்திற்கு தங்களை வரவேற்கிறோம்!",
        "language": "ta",
        "voice_id": "ta_pallavi",
    }
    response = test_client.post("/api/v1/tts", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 1000


def test_post_stt(test_client, sample_wav_bytes):
    with patch("xyraspeech.app.api.stt.whisper_engine.transcribe", new_callable=AsyncMock) as mock_stt:
        mock_stt.return_value = STTResponse(
            text="Hello world test",
            language="en",
            duration_seconds=1.0,
            confidence=0.98,
            segments=[],
            model="faster-whisper:tiny",
        )
        files = {"file": ("audio.wav", io.BytesIO(sample_wav_bytes), "audio/wav")}
        response = test_client.post("/api/v1/stt", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello world test"
        assert data["language"] == "en"


def test_post_conversation_message(test_client):
    payload = {
        "text": "My name is Arun. What is my name?",
        "conversation_id": "conv_test_1",
    }
    response = test_client.post("/api/v1/conversation/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response_text" in data
    assert "speech_direction" in data
    assert "audio_base64" in data
    assert len(data["audio_base64"]) > 100
