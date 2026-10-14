"""Acoustic Sound Effects Engine: Vocal Laughter, Breath Pauses & Audio Splicer."""

import os
import io
import re
import wave
import numpy as np
import soundfile as sf
from typing import List, Tuple, Optional, Callable


class SoundEffectsEngine:
    """Generates vocal acoustic sound effects (laughter, sighs, gasps) and splices them into TTS streams."""

    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self.fx_cache = {}
        self.storage_dir = os.path.join(os.getcwd(), "storage", "fx")
        os.makedirs(self.storage_dir, exist_ok=True)
        self._ensure_sample_files()

    def _ensure_sample_files(self):
        """Creates soft, natural warm acoustic sound effect files if they do not exist."""
        laughter_file = os.path.join(self.storage_dir, "laughter.wav")
        if not os.path.exists(laughter_file):
            sr = self.sample_rate
            duration = 0.45  # Short, subtle, natural chuckle
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            
            # Soft warm breathy chuckle: pink noise + low-pass warmth (subtle, non-robotic)
            noise = np.random.normal(0, 0.05, len(t))
            # Smooth bell-curve envelope for natural breath decay
            env = np.sin(np.pi * (t / duration)) ** 2.0 * np.exp(-1.8 * (t / duration))
            
            # Low pitch vocal warmth pulse (160 Hz)
            pitch_pulse = 0.02 * np.sin(2 * np.pi * 160 * t) * env
            
            audio = (noise * env + pitch_pulse).astype(np.float32)
            max_v = np.max(np.abs(audio))
            if max_v > 0:
                audio = audio / max_v * 0.15  # Gentle volume
            
            sf.write(laughter_file, audio, sr, format="WAV", subtype="PCM_16")

    def get_laughter_waveform(self) -> np.ndarray:
        """Loads or generates warm, natural acoustic laughter waveform."""
        if "laughter" in self.fx_cache:
            return self.fx_cache["laughter"]

        laughter_file = os.path.join(self.storage_dir, "laughter.wav")
        if os.path.exists(laughter_file):
            try:
                data, sr = sf.read(laughter_file, dtype="float32")
                if data.ndim > 1:
                    data = np.mean(data, axis=1)
                self.fx_cache["laughter"] = data.astype(np.float32)
                return self.fx_cache["laughter"]
            except Exception:
                pass

        # Gentle short breath pause fallback (0.3s)
        duration = 0.35
        sr = self.sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        env = np.sin(np.pi * (t / duration)) ** 2.0
        audio = (np.random.normal(0, 0.03, len(t)) * env).astype(np.float32)
        self.fx_cache["laughter"] = audio
        return audio

    def get_sound_effect(self, tag_name: str) -> np.ndarray:
        """Returns waveform array for a specified tag name."""
        tag = tag_name.lower().strip("[] ")
        if tag in ["laughter", "laughs", "chuckle"]:
            return self.get_laughter_waveform()
        else:
            # Default soft natural pause (0.25s)
            return np.zeros(int(self.sample_rate * 0.25), dtype=np.float32)

    def splice_audio_segments(
        self,
        audio_segments: List[Tuple[str, np.ndarray]],
        crossfade_ms: int = 15
    ) -> np.ndarray:
        """Splices text audio segments and sound effect arrays with smooth crossfading."""
        if not audio_segments:
            return np.array([], dtype=np.float32)

        fade_samples = int(self.sample_rate * (crossfade_ms / 1000.0))
        result = []

        for kind, arr in audio_segments:
            if len(arr) == 0:
                continue
            if not result:
                result = list(arr)
            else:
                prev_arr = np.array(result, dtype=np.float32)
                if len(prev_arr) >= fade_samples and len(arr) >= fade_samples:
                    fade_out = np.linspace(1.0, 0.0, fade_samples)
                    fade_in = np.linspace(0.0, 1.0, fade_samples)
                    overlap = prev_arr[-fade_samples:] * fade_out + arr[:fade_samples] * fade_in
                    result = list(prev_arr[:-fade_samples]) + list(overlap) + list(arr[fade_samples:])
                else:
                    result.extend(arr)

        return np.array(result, dtype=np.float32)


sound_effects_engine = SoundEffectsEngine()
