"""Unit tests for Bark Voice Cloning & Prompt Extraction."""

import os
import pytest
import numpy as np
from fastapi.testclient import TestClient
from xyraspeech.app.main import app
from xyraspeech.app.services.voice_cloner import voice_cloner_service
from xyraspeech.app.engines.tts.bark_tts import bark_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry

client = TestClient(app)


def test_voice_cloner_extract_prompt():
    """Tests extracting 3-part Bark prompt numpy array dictionary from audio bytes."""
    # Create 1 second dummy float PCM WAV bytes
    sample_rate = 24000
    t = np.linspace(0, 1, sample_rate, dtype=np.float32)
    dummy_signal = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    import io
    import soundfile as sf
    bio = io.BytesIO()
    sf.write(bio, dummy_signal, sample_rate, format="WAV", subtype="PCM_16")
    audio_bytes = bio.getvalue()

    prompt = voice_cloner_service.extract_voice_prompt(
        audio_bytes=audio_bytes,
        voice_id="test_voice_unit",
        sample_rate=24000,
    )

    assert "semantic_prompt" in prompt
    assert "coarse_prompt" in prompt
    assert "fine_prompt" in prompt
    assert isinstance(prompt["semantic_prompt"], np.ndarray)
    assert isinstance(prompt["coarse_prompt"], np.ndarray)
    assert isinstance(prompt["fine_prompt"], np.ndarray)
    assert prompt["coarse_prompt"].shape[0] == 2
    assert prompt["fine_prompt"].shape[0] == 8


def test_voice_cloner_save_and_load_preset(tmp_path):
    """Tests saving and loading .npz preset files."""
    service = voice_cloner_service
    prompt = {
        "semantic_prompt": np.array([1, 2, 3, 4], dtype=np.int64),
        "coarse_prompt": np.zeros((2, 4), dtype=np.int64),
        "fine_prompt": np.zeros((8, 4), dtype=np.int64),
    }

    npz_path = service.save_voice_preset("test_preset", prompt)
    assert os.path.exists(npz_path)

    loaded = service.load_voice_preset("test_preset")
    assert loaded is not None
    assert np.array_equal(loaded["semantic_prompt"], prompt["semantic_prompt"])


@pytest.mark.asyncio
async def test_bark_tts_synthesis():
    """Tests synthesizing speech using BarkTTSEngine with expressive tags."""
    text = "Hello! [laughter] This is a test of Bark voice cloning. [sighs]"
    wav_bytes = await bark_tts_engine.synthesize(
        text=text,
        language="en",
        voice_id="bark_expressive_en",
    )
    assert len(wav_bytes) > 1000
    assert wav_bytes.startswith(b"RIFF") or len(wav_bytes) > 2000


def test_api_clone_voice_endpoint():
    """Tests POST /api/v1/voices/clone API endpoint."""
    sample_rate = 24000
    t = np.linspace(0, 1, sample_rate, dtype=np.float32)
    dummy_signal = 0.3 * np.sin(2 * np.pi * 500 * t)
    
    import io
    import soundfile as sf
    bio = io.BytesIO()
    sf.write(bio, dummy_signal, sample_rate, format="WAV", subtype="PCM_16")
    audio_bytes = bio.getvalue()

    files = {
        "file": ("sample.wav", audio_bytes, "audio/wav")
    }
    data = {
        "voice_name": "Test Cloned Voice",
        "language": "en",
        "gender": "Female",
        "description": "Cloned voice test profile"
    }

    response = client.post("/api/v1/voices/clone", files=files, data=data)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "SUCCESS"
    assert json_resp["voice"]["name"] == "Test Cloned Voice"
    assert json_resp["voice"]["engine"] == "bark_cloned"

    # Verify voice appears in GET /api/v1/voices
    list_resp = client.get("/api/v1/voices")
    assert list_resp.status_code == 200
    voice_ids = [v["id"] for v in list_resp.json()["voices"]]
    assert json_resp["voice"]["id"] in voice_ids
