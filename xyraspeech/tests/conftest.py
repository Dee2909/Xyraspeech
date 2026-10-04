"""Pytest configuration and test client fixtures for XyraSpeech."""

import io
import wave
import numpy as np
import pytest
from fastapi.testclient import TestClient

from xyraspeech.app.main import app


@pytest.fixture
def test_client():
    """FastAPI TestClient instance for XyraSpeech Gateway."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_wav_bytes():
    """Generates a real 1-second 16kHz mono sine-wave WAV buffer for audio tests."""
    sample_rate = 16000
    duration_sec = 1.0
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # 440 Hz standard concert pitch A tone
    audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)

    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    return bio.getvalue()
