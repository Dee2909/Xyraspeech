"""Live integration test against local Ollama instance (skipped if Ollama offline)."""

import pytest
from xyrabrain.app.core.config import settings
from xyrabrain.app.models.enums import ProcessingMode, SupportedLanguage
from xyrabrain.app.services.brain_service import brain_service
from xyrabrain.app.services.ollama_client import ollama_client


@pytest.mark.asyncio
async def test_live_ollama_expressive_english():
    health = await ollama_client.check_health()
    if not health.get("reachable") or not health.get("model_available"):
        pytest.skip(f"Ollama or model '{settings.OLLAMA_MODEL}' not available on machine.")

    text = "Wow! You actually did it! I'm really proud of you!"
    direction = await brain_service.process(
        text=text,
        language=SupportedLanguage.ENGLISH,
        mode=ProcessingMode.EXPRESSIVE,
    )

    assert direction.language == SupportedLanguage.ENGLISH
    assert len(direction.segments) >= 1
    assert direction.metadata.processing_mode == ProcessingMode.EXPRESSIVE
    assert direction.overall_emotion is not None
    assert direction.overall_style is not None


@pytest.mark.asyncio
async def test_live_ollama_expressive_tamil():
    health = await ollama_client.check_health()
    if not health.get("reachable") or not health.get("model_available"):
        pytest.skip(f"Ollama or model '{settings.OLLAMA_MODEL}' not available on machine.")

    text = "அருமை! நீங்கள் உண்மையிலேயே அருமையாக செய்துள்ளீர்கள்!"
    direction = await brain_service.process(
        text=text,
        language=SupportedLanguage.TAMIL,
        mode=ProcessingMode.EXPRESSIVE,
    )

    assert direction.language == SupportedLanguage.TAMIL
    assert len(direction.segments) >= 1
    # Verify Tamil characters are in the output speech_text
    assert "அருமை" in direction.speech_text or "செய்துள்ளீர்கள்" in direction.speech_text
