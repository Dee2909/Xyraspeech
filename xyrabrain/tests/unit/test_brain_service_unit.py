"""Unit tests for BrainService processing logic."""

import pytest
from unittest.mock import AsyncMock
from xyrabrain.app.models.enums import Emotion, ProcessingMode, SpeakingStyle, SupportedLanguage
from xyrabrain.app.services.brain_service import BrainService
from xyrabrain.app.services.ollama_client import OllamaClient


@pytest.mark.asyncio
async def test_raw_mode_bypasses_ollama():
    mock_client = AsyncMock(spec=OllamaClient)
    service = BrainService(client=mock_client)

    raw_text = "Hello world! This is a test. How are you?"
    result = await service.process(
        text=raw_text,
        language=SupportedLanguage.ENGLISH,
        mode=ProcessingMode.RAW,
    )

    # Assert Ollama was never called in RAW mode
    mock_client.chat.assert_not_called()

    assert result.speech_text == raw_text
    assert result.language == SupportedLanguage.ENGLISH
    assert result.metadata.processing_mode == ProcessingMode.RAW
    assert len(result.segments) >= 3
    assert result.segments[0].text == "Hello world!"
    assert result.segments[1].text == "This is a test."
    assert result.segments[2].text == "How are you?"


@pytest.mark.asyncio
async def test_enhanced_mode_with_mock(mock_ollama_client):
    mock_ollama_client.chat.return_value = {
        "language": "en",
        "speech_text": "Hello, how are you today?",
        "overall_style": "conversational",
        "overall_emotion": "neutral",
        "segments": [
            {
                "text": "Hello, how are you today?",
                "emotion": "neutral",
                "style": "conversational",
                "energy": 0.5,
                "speed": 1.0,
                "pitch": 1.0,
                "pause_after_ms": 250,
            }
        ],
    }
    service = BrainService(client=mock_ollama_client)

    result = await service.process(
        text="hello how are you today",
        language=SupportedLanguage.ENGLISH,
        mode=ProcessingMode.ENHANCED,
    )

    assert mock_ollama_client.chat.called
    assert result.speech_text == "Hello, how are you today?"
    assert result.overall_style == SpeakingStyle.CONVERSATIONAL
    assert result.overall_emotion == Emotion.NEUTRAL


@pytest.mark.asyncio
async def test_expressive_mode_with_mock(mock_ollama_client):
    service = BrainService(client=mock_ollama_client)
    result = await service.process(
        text="Wow! You actually did it! I'm really proud of you!",
        language=SupportedLanguage.ENGLISH,
        mode=ProcessingMode.EXPRESSIVE,
    )

    assert result.language == SupportedLanguage.ENGLISH
    assert result.overall_emotion == Emotion.EXCITED
    assert len(result.segments) == 3
    assert result.segments[0].emotion == Emotion.SURPRISED
    assert result.segments[1].emphasis == ["actually", "did it"]
