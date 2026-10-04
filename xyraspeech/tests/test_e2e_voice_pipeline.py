"""End-to-End Real Model Pipeline Test: Text -> TTS -> Audio -> STT -> Transcript."""

import pytest
from xyraspeech.app.engines.stt.whisper_engine import whisper_engine
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine


@pytest.mark.asyncio
async def test_e2e_english_audio_loopback():
    """Generates real local TTS audio and passes it to real local STT transcription."""
    original_text = "Welcome to XyraSpeech platform."

    # 1. Synthesize real audio
    wav_bytes = await mac_tts_engine.synthesize(
        text=original_text,
        language="en",
        voice_id="en_rishi",
        speed=1.0,
    )
    assert len(wav_bytes) > 2000

    # 2. Transcribe real audio using local Whisper
    stt_res = await whisper_engine.transcribe(wav_bytes, language="en")
    assert stt_res.language == "en"
    assert "xyraspeech" in stt_res.text.lower() or "welcome" in stt_res.text.lower() or "platform" in stt_res.text.lower()
