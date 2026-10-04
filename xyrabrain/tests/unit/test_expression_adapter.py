"""Unit tests for ExpressionAdapter and TTS capability filtering."""

import pytest
from xyrabrain.app.models.enums import (
    Emotion,
    ProcessingMode,
    SpeakingStyle,
    SupportedLanguage,
    TTSCapability,
)
from xyrabrain.app.schemas.brain import DirectionMetadata, SpeechDirection, SpeechSegment
from xyrabrain.app.services.expression_adapter import (
    ExpressionAdapter,
    IndicTTSAdapter,
    MockTTSAdapter,
    OpenVoiceAdapter,
)


@pytest.fixture
def sample_direction():
    return SpeechDirection(
        language=SupportedLanguage.ENGLISH,
        speech_text="Great job! Keep it up!",
        overall_style=SpeakingStyle.ENTHUSIASTIC,
        overall_emotion=Emotion.EXCITED,
        segments=[
            SpeechSegment(
                text="Great job!",
                emotion=Emotion.EXCITED,
                style=SpeakingStyle.ENTHUSIASTIC,
                energy=0.9,
                speed=1.1,
                pitch=1.05,
                emphasis=["Great"],
                pause_after_ms=300,
            ),
            SpeechSegment(
                text="Keep it up!",
                emotion=Emotion.ENCOURAGING,
                style=SpeakingStyle.FRIENDLY,
                energy=0.8,
                speed=1.0,
                pitch=1.0,
                emphasis=["Keep"],
                pause_after_ms=0,
            ),
        ],
        metadata=DirectionMetadata(
            model="test-model",
            processing_mode=ProcessingMode.EXPRESSIVE,
            processing_time_ms=12.5,
            schema_version="1.0",
        ),
    )


def test_indic_tts_adapter_capabilities(sample_direction):
    adapter = IndicTTSAdapter()
    result = adapter.adapt(sample_direction)

    assert result.adapter_name == "IndicTTSAdapter"
    # IndicTTS supports speed, pitch, pause but NOT emotion/energy directly
    assert TTSCapability.SUPPORTS_SPEED.value in result.applied_capabilities
    assert TTSCapability.SUPPORTS_EMOTION.value in result.dropped_capabilities

    inst1 = result.instructions[0]
    assert inst1.speed == 1.1
    assert inst1.pitch == 1.05
    assert inst1.pause_after_ms == 300
    assert inst1.emotion is None  # Dropped from engine payload
    assert inst1.raw_metadata["original_emotion"] == "excited"  # Preserved in debug meta


def test_openvoice_adapter_capabilities(sample_direction):
    adapter = OpenVoiceAdapter()
    result = adapter.adapt(sample_direction)

    assert result.adapter_name == "OpenVoiceAdapter"
    assert TTSCapability.SUPPORTS_EMOTION.value in result.applied_capabilities
    assert TTSCapability.SUPPORTS_PITCH.value in result.dropped_capabilities

    inst1 = result.instructions[0]
    assert inst1.emotion == "excited"
    assert inst1.pitch is None  # Dropped for engine payload


@pytest.mark.asyncio
async def test_mock_tts_adapter_synthesis(sample_direction):
    adapter = MockTTSAdapter()
    result = adapter.adapt(sample_direction)
    audio_bytes = await adapter.synthesize(result.instructions[0])
    assert audio_bytes == b"MOCK_SYNTHESIZED_AUDIO_DATA"


def test_ssml_generation(sample_direction):
    instructions = ExpressionAdapter.to_neutral_instructions(
        direction=sample_direction,
        capabilities={TTSCapability.SUPPORTS_SSML, TTSCapability.SUPPORTS_SPEED, TTSCapability.SUPPORTS_PITCH, TTSCapability.SUPPORTS_PAUSE},
    )
    inst = instructions[0]
    assert inst.ssml is not None
    assert "<speak><prosody" in inst.ssml
    assert 'rate="110%"' in inst.ssml
    assert '<break time="300ms"/>' in inst.ssml
