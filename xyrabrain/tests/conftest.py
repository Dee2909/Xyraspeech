"""Pytest fixtures and mock configurations for XyraBrain tests."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from xyrabrain.app.main import app
from xyrabrain.app.models.enums import Emotion, SpeakingStyle, SupportedLanguage
from xyrabrain.app.schemas.brain import DirectionMetadata, SpeechDirection, SpeechSegment
from xyrabrain.app.services.brain_service import BrainService
from xyrabrain.app.services.ollama_client import OllamaClient


@pytest.fixture
def test_client():
    """FastAPI TestClient instance."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_tamil_sentences():
    return {
        "neutral": "இன்று வானிலை மிகவும் தெளிவாக இருக்கிறது.",
        "happy": "அருமை! இந்த வெற்றி எனக்கு மிகுந்த மகிழ்ச்சியை தருகிறது!",
        "question": "நாளை நீங்கள் அலுவலகத்திற்கு வருகிறீர்களா?",
        "sad": "இந்த செய்தி எனக்கு மிகவும் வருத்தத்தை அளிக்கிறது.",
        "formal": "தங்களின் மேலான கவனத்திற்கு இந்த அறிக்கை சமர்ப்பிக்கப்படுகிறது.",
        "conversational": "எப்படி இருக்கீங்க? இன்னைக்கு என்ன விஷயம்?",
        "mixed": "Today meeting ரொம்ப important, please attend பண்ணுங்க.",
    }


@pytest.fixture
def sample_english_sentences():
    return {
        "neutral": "The meeting is scheduled for ten in the morning.",
        "excited": "Wow! You actually did it! I'm really proud of you!",
        "question": "Could you please explain how this model works?",
        "concerned": "I'm really worried about the system performance under load.",
        "formal": "Please find attached the quarterly speech analytics report.",
    }


@pytest.fixture
def mock_ollama_client():
    """Mocked Ollama client returning standard structured speech direction."""
    client = AsyncMock(spec=OllamaClient)
    client.model = "mock-model:latest"
    client.base_url = "http://localhost:11434"
    client.timeout = 30

    client.check_health.return_value = {
        "reachable": True,
        "configured_model": "mock-model:latest",
        "model_available": True,
        "installed_models": ["mock-model:latest"],
    }

    client.chat.return_value = {
        "language": "en",
        "speech_text": "Wow! You actually did it! I'm really proud of you!",
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
                "pause_before_ms": 0,
                "pause_after_ms": 300,
            },
            {
                "text": "You actually did it!",
                "emotion": "excited",
                "style": "enthusiastic",
                "energy": 0.9,
                "speed": 1.08,
                "pitch": 1.02,
                "emphasis": ["actually", "did it"],
                "pause_before_ms": 0,
                "pause_after_ms": 350,
            },
            {
                "text": "I'm really proud of you!",
                "emotion": "warm",
                "style": "friendly",
                "energy": 0.75,
                "speed": 0.95,
                "pitch": 0.98,
                "emphasis": ["really proud"],
                "pause_before_ms": 0,
                "pause_after_ms": 0,
            },
        ],
    }
    return client
