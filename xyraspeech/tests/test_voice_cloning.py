"""Tests for Voice Cloning Engine and Voice Library Cloning API endpoints."""

import io
import wave
import pytest
from fastapi.testclient import TestClient

from xyraspeech.app.main import app
from xyraspeech.app.engines.tts.voice_cloner import voice_cloner_engine
from xyraspeech.app.engines.tts.registry import voice_registry


@pytest.fixture
def client():
    return TestClient(app)


def create_dummy_wav_bytes(duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generates synthetic test WAV audio bytes."""
    buf = io.BytesIO()
    num_samples = int(duration_sec * sample_rate)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # 440 Hz sine wave audio signal
        import math
        samples = bytearray()
        for i in range(num_samples):
            val = int(10000 * math.sin(2 * math.pi * 440 * i / sample_rate))
            samples.extend(val.to_bytes(2, byteorder="little", signed=True))
        wf.writeframes(samples)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_extract_acoustic_features():
    wav_data = create_dummy_wav_bytes(duration_sec=1.5)
    features = voice_cloner_engine.extract_acoustic_features(wav_data)
    assert "estimated_pitch_hz" in features
    assert "inferred_gender" in features
    assert "rms_energy" in features
    assert features["duration"] > 0


@pytest.mark.asyncio
async def test_create_and_delete_cloned_voice():
    wav_data = create_dummy_wav_bytes(duration_sec=2.0)
    voice_item, profile = await voice_cloner_engine.create_cloned_voice(
        name="Test Speaker",
        audio_bytes=wav_data,
        language="ta",
    )
    assert voice_item.id.startswith("clone_")
    assert "Test Speaker" in voice_item.name
    assert voice_item.engine == "voice_cloner"

    # Verify present in voice registry
    voices = voice_registry.list_voices()
    found = any(v.id == voice_item.id for v in voices)
    assert found is True

    # Test synthesis with cloned voice
    synthesized_wav = await voice_cloner_engine.synthesize(
        text="வணக்கம் இது குரல் சோதனையாகும்",
        language="ta",
        voice_id=voice_item.id,
    )
    assert len(synthesized_wav) > 1000

    # Delete cloned voice
    deleted = voice_cloner_engine.delete_cloned_voice(voice_item.id)
    assert deleted is True


def test_api_voice_cloning_flow(client):
    wav_data = create_dummy_wav_bytes(duration_sec=2.0)
    
    # 1. Clone voice via API
    response = client.post(
        "/api/v1/voices/clone",
        data={"name": "Karthik Voice", "language": "ta", "description": "Test clone"},
        files={"file": ("sample.wav", wav_data, "audio/wav")},
    )
    assert response.status_code == 200
    data = response.json()
    voice_id = data["id"]
    assert voice_id.startswith("clone_")
    assert "Karthik Voice" in data["name"]

    # 2. Check list voices includes cloned voice
    list_res = client.get("/api/v1/voices")
    assert list_res.status_code == 200
    all_voices = list_res.json()["voices"]
    assert any(v["id"] == voice_id for v in all_voices)

    # 3. Synthesize speech using cloned voice
    tts_res = client.post(
        "/api/v1/tts",
        json={"text": "Hello this is cloned voice testing.", "voice_id": voice_id, "language": "en"},
    )
    assert tts_res.status_code == 200
    assert tts_res.headers["content-type"] == "audio/wav"
    assert len(tts_res.content) > 1000

    # 4. Delete cloned voice via API
    del_res = client.delete(f"/api/v1/voices/{voice_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
