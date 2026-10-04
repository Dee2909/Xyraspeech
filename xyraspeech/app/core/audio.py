"""Real Audio Processing Engine: Normalization, VAD, Resampling, and Format Conversion."""

import io
import math
import subprocess
import wave
from typing import AsyncGenerator, Optional, Tuple
import numpy as np
import soundfile as sf

from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import logger


class AudioProcessingError(Exception):
    """Raised when audio conversion or format validation fails."""
    pass


class AudioProcessor:
    """Production audio processing utilities."""

    @classmethod
    def inspect_audio(cls, audio_bytes: bytes) -> dict:
        """Inspects sample rate, channels, duration, and format of audio buffer."""
        try:
            with sf.SoundFile(io.BytesIO(audio_bytes)) as f:
                duration_sec = len(f) / f.samplerate
                return {
                    "samplerate": f.samplerate,
                    "channels": f.channels,
                    "format": f.format,
                    "subtype": f.subtype,
                    "frames": len(f),
                    "duration_seconds": round(duration_sec, 2),
                }
        except Exception as exc:
            # Fallback to wave if soundfile fails
            try:
                with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                    channels = wf.getnchannels()
                    rate = wf.getframerate()
                    frames = wf.getnframes()
                    return {
                        "samplerate": rate,
                        "channels": channels,
                        "format": "WAV",
                        "subtype": "PCM",
                        "frames": frames,
                        "duration_seconds": round(frames / rate, 2),
                    }
            except Exception:
                raise AudioProcessingError(f"Could not inspect audio format: {str(exc)}")

    @classmethod
    def convert_to_wav_pcm16(
        cls,
        audio_bytes: bytes,
        target_sample_rate: int = 16000,
    ) -> Tuple[bytes, np.ndarray, float]:
        """Converts arbitrary audio bytes (WAV, MP3, WebM, Ogg, AAC) into mono 16-bit PCM WAV.

        Returns: (wav_bytes, numpy_float32_array, duration_seconds)
        """
        # First try soundfile / numpy direct load
        try:
            with io.BytesIO(audio_bytes) as bio:
                data, samplerate = sf.read(bio, dtype="float32")

                # Convert to mono if stereo
                if data.ndim > 1:
                    data = np.mean(data, axis=1)

                # Resample if sample rate doesn't match
                if samplerate != target_sample_rate:
                    # High quality resampling via ffmpeg
                    return cls._convert_via_ffmpeg(audio_bytes, target_sample_rate)

                duration_sec = len(data) / target_sample_rate

                # Produce clean WAV bytes
                out_bio = io.BytesIO()
                sf.write(out_bio, data, target_sample_rate, format="WAV", subtype="PCM_16")
                return out_bio.getvalue(), data, duration_sec

        except Exception:
            # Use ffmpeg for formats like WebM from browser MediaRecorder
            return cls._convert_via_ffmpeg(audio_bytes, target_sample_rate)

    @classmethod
    def _convert_via_ffmpeg(cls, input_bytes: bytes, target_sample_rate: int = 16000) -> Tuple[bytes, np.ndarray, float]:
        """Invokes ffmpeg subprocess to normalize audio into clean 16kHz mono WAV."""
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i", "pipe:0",
                "-f", "wav",
                "-acodec", "pcm_s16le",
                "-ac", "1",
                "-ar", str(target_sample_rate),
                "pipe:1",
            ]
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out_wav, err = proc.communicate(input=input_bytes)
            if proc.returncode != 0:
                raise AudioProcessingError(f"FFmpeg conversion failed: {err.decode('utf-8', errors='ignore')}")

            with io.BytesIO(out_wav) as bio:
                data, _ = sf.read(bio, dtype="float32")
                duration_sec = len(data) / target_sample_rate
                return out_wav, data, duration_sec
        except Exception as exc:
            raise AudioProcessingError(f"Audio conversion failed: {str(exc)}")

    @classmethod
    def calculate_energy(cls, pcm_chunk: np.ndarray) -> float:
        """Calculates Root-Mean-Square (RMS) energy of an audio frame."""
        if len(pcm_chunk) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(pcm_chunk))))

    @classmethod
    def is_speech_active(cls, pcm_chunk: np.ndarray, threshold: Optional[float] = None) -> bool:
        """Determines if the given audio chunk contains active speech based on energy threshold."""
        thresh = threshold if threshold is not None else settings.VAD_ENERGY_THRESHOLD
        energy = cls.calculate_energy(pcm_chunk)
        return energy >= thresh

    @classmethod
    async def stream_audio_chunks(
        cls,
        wav_bytes: bytes,
        chunk_size_bytes: int = 4096,
    ) -> AsyncGenerator[bytes, None]:
        """Generates streaming byte chunks for WebSocket transmission."""
        bio = io.BytesIO(wav_bytes)
        while True:
            chunk = bio.read(chunk_size_bytes)
            if not chunk:
                break
            yield chunk


audio_processor = AudioProcessor()
