"""Unit tests for AudioProcessor."""

import numpy as np
import pytest
from xyraspeech.app.core.audio import audio_processor


def test_inspect_audio(sample_wav_bytes):
    info = audio_processor.inspect_audio(sample_wav_bytes)
    assert info["samplerate"] == 16000
    assert info["channels"] == 1
    assert info["duration_seconds"] == 1.0


def test_convert_to_wav_pcm16(sample_wav_bytes):
    out_wav, data, duration = audio_processor.convert_to_wav_pcm16(sample_wav_bytes, target_sample_rate=16000)
    assert isinstance(out_wav, bytes)
    assert len(out_wav) > 0
    assert isinstance(data, np.ndarray)
    assert round(duration, 1) == 1.0


def test_calculate_energy_and_vad():
    # Silent frame
    silent_frame = np.zeros(1600, dtype=np.float32)
    assert audio_processor.calculate_energy(silent_frame) == 0.0
    assert not audio_processor.is_speech_active(silent_frame)

    # Active loud frame
    active_frame = np.ones(1600, dtype=np.float32) * 0.5
    assert audio_processor.calculate_energy(active_frame) > 0.015
    assert audio_processor.is_speech_active(active_frame)
