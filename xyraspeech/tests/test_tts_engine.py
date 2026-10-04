"""Unit tests for Real Mac Native TTS Engine."""

import pytest
from xyraspeech.app.core.audio import audio_processor
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry


@pytest.mark.asyncio
async def test_mac_tts_english_synthesis():
    text = "Hello! This is a real speech synthesis test."
    wav_bytes = await mac_tts_engine.synthesize(
        text=text,
        language="en",
        voice_id="en_rishi",
        speed=1.0,
        pitch=1.0,
        energy=0.5,
    )
    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 1000
    info = audio_processor.inspect_audio(wav_bytes)
    assert info["samplerate"] == 24000
    assert info["duration_seconds"] > 0.5


@pytest.mark.asyncio
async def test_mac_tts_tamil_synthesis():
    text = "வணக்கம்! இது உண்மையான தமிழ் குரல் பரிசோதனை."
    wav_bytes = await mac_tts_engine.synthesize(
        text=text,
        language="ta",
        voice_id="ta_vani",
        speed=1.0,
        pitch=1.0,
        energy=0.6,
    )
    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 1000
    info = audio_processor.inspect_audio(wav_bytes)
    assert info["samplerate"] == 24000
    assert info["duration_seconds"] > 0.5


def test_voice_registry_lookups():
    voices = voice_registry.list_voices()
    assert len(voices) >= 2

    ta_voice = voice_registry.get_default_voice("ta")
    assert ta_voice.id in ["ta_pallavi", "ta_vani"]
    assert ta_voice.language == "ta"

    en_voice = voice_registry.get_default_voice("en")
    assert en_voice.id in ["en_neerja", "en_rishi"]
    assert en_voice.language == "en"
