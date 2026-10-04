"""Real Local High-Fidelity Human-Like Synthesizer for macOS (Tamil & English)."""

import asyncio
import os
import re
import subprocess
import tempfile
import time
from typing import Optional, Set

from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import log_event, logger
from xyraspeech.app.engines.tts.base import BaseTTSEngine
from xyraspeech.app.models.enums import TTSCapability


class MacNativeTTSEngine(BaseTTSEngine):
    """Production TTS Engine with Studio Acoustic Mastering for ultra-natural human voice tone."""

    VOICE_MAP = {
        "ta_vani": "Vani",
        "en_rishi": "Rishi",
        "en_tara": "Tara",
        "en_samantha": "Samantha",
        "en_daniel": "Daniel",
        "ta": "Vani",
        "en": "Rishi",
        "ta-en": "Vani",
    }

    def get_capabilities(self) -> Set[TTSCapability]:
        """Mac native engine supports speed, pitch, energy, pause, emotion & style."""
        return {
            TTSCapability.SUPPORTS_SPEED,
            TTSCapability.SUPPORTS_PITCH,
            TTSCapability.SUPPORTS_ENERGY,
            TTSCapability.SUPPORTS_PAUSE,
            TTSCapability.SUPPORTS_EMOTION,
            TTSCapability.SUPPORTS_STYLE,
        }

    def _prepare_natural_text(self, text: str) -> str:
        """Adds natural conversational phrasing and prosodic breathing pauses."""
        cleaned = text.strip()
        # Ensure punctuation has natural breathing space for TTS engine
        cleaned = re.sub(r'([.,!?:;])([^\s])', r'\1 \2', cleaned)
        # Convert ellipses to slight pause mark
        cleaned = cleaned.replace("...", ", ")
        # Ensure em-dashes have spacing for natural clause separation
        cleaned = cleaned.replace("—", " — ").replace("--", " — ")
        return cleaned

    def _build_dsp_filter_chain(
        self,
        pitch_factor: float,
        energy_factor: float,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
    ) -> str:
        """Constructs an advanced FFmpeg DSP filter graph for warm, human broadcast-quality audio."""
        filters = []

        # 1. Pitch & Formant Shift
        if abs(pitch_factor - 1.0) > 0.02:
            target_rate = int(24000 * pitch_factor)
            tempo = 1.0 / pitch_factor
            filters.append(f"asetrate={target_rate}")
            filters.append(f"atempo={tempo:.3f}")

        # 2. Studio Acoustic Equalization (Vocal Warmth & Human Resonance Chain)
        # Highpass filter to eliminate sub-audible mic rumble and plosives
        filters.append("highpass=f=80")

        emo = (emotion or "").lower()
        sty = (style or "").lower()

        # Dynamic Emotion & Warmth Equalization
        if emo in ["warm", "empathetic", "friendly", "calm"] or sty in ["warm", "friendly", "empathetic"]:
            # Rich chest resonance + mellow high end
            filters.append("equalizer=f=220:width_type=o:width=1.2:g=2.8")
            filters.append("equalizer=f=500:width_type=o:width=1.0:g=1.2")
            filters.append("equalizer=f=3200:width_type=o:width=1.5:g=1.5")
            filters.append("equalizer=f=7500:width_type=o:width=1.0:g=-1.5")  # de-harsh
        elif emo in ["excited", "happy"] or sty in ["enthusiastic", "energetic"]:
            # Bright, articulate, energized presence
            filters.append("equalizer=f=200:width_type=o:width=1.0:g=1.5")
            filters.append("equalizer=f=3500:width_type=o:width=1.4:g=2.8")
            filters.append("equalizer=f=9000:width_type=o:width=1.2:g=1.5")
        elif emo in ["serious", "confident"] or sty in ["professional", "serious"]:
            # Crisp broadcast presence
            filters.append("equalizer=f=180:width_type=o:width=1.0:g=2.2")
            filters.append("equalizer=f=2800:width_type=o:width=1.5:g=2.2")
        else:
            # Natural balanced human vocal curve
            filters.append("equalizer=f=230:width_type=o:width=1.2:g=2.0")
            filters.append("equalizer=f=3200:width_type=o:width=1.5:g=1.8")

        # 3. Dynamic Range Compressor (Intimate human presence, prevents harsh volume spikes)
        filters.append("acompressor=threshold=-16dB:ratio=2.5:attack=15:release=120:makeup=2dB")

        # 4. Subtle Micro-Room Depth (Removes robotic dry 'mono' isolation)
        filters.append("aecho=0.85:0.88:18:0.10")

        # 5. Dynamic Gain & Volume Normalization
        vol_gain = 0.85 + (energy_factor * 0.35)
        if abs(vol_gain - 1.0) > 0.03:
            filters.append(f"volume={vol_gain:.2f}")

        # Final limiter to guarantee zero distortion
        filters.append("alimiter=limit=0.95")

        return ",".join(filters)

    async def synthesize(
        self,
        text: str,
        language: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = 1.0,
        pitch: Optional[float] = 1.0,
        energy: Optional[float] = 0.5,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
    ) -> bytes:
        """Synthesizes text into high-fidelity, studio-mastered WAV audio bytes."""
        start_time = time.perf_counter()

        # Select macOS voice
        selected_voice = "Vani" if language == "ta" else "Rishi"
        if voice_id and voice_id in self.VOICE_MAP:
            selected_voice = self.VOICE_MAP[voice_id]
        elif language in self.VOICE_MAP:
            selected_voice = self.VOICE_MAP[language]

        # Natural human baseline speaking rate: ~158 Words Per Minute
        speed_factor = float(speed or 1.0)
        speed_factor = max(0.5, min(1.5, speed_factor))

        emo = (emotion or "").lower()
        base_wpm = 158
        if emo in ["excited", "happy"]:
            base_wpm = 166
        elif emo in ["calm", "sad", "empathetic"]:
            base_wpm = 148

        wpm = int(base_wpm * speed_factor)

        # Natural pitch and energy factors
        pitch_factor = float(pitch or 1.0)
        pitch_factor = max(0.8, min(1.2, pitch_factor))
        energy_factor = float(energy or 0.5)

        # Prepare natural phrasing
        natural_text = self._prepare_natural_text(text)

        def _run_synthesis() -> bytes:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw_wav:
                raw_path = raw_wav.name
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as final_wav:
                final_path = final_wav.name

            try:
                # 1. Synthesize baseline audio with native voice
                say_cmd = [
                    "say",
                    "-v", selected_voice,
                    "-r", str(wpm),
                    "-o", raw_path,
                    "--data-format=LEF32@24000",
                    natural_text,
                ]
                proc = subprocess.run(say_cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    logger.warning(f"say command warning: {proc.stderr}")

                # 2. Apply Studio Acoustic Mastering Chain (FFmpeg DSP)
                filter_str = self._build_dsp_filter_chain(
                    pitch_factor=pitch_factor,
                    energy_factor=energy_factor,
                    emotion=emotion,
                    style=style,
                )

                ff_cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", raw_path,
                    "-af", filter_str,
                    "-ar", "24000",
                    final_path,
                ]
                ff_proc = subprocess.run(ff_cmd, capture_output=True)
                if ff_proc.returncode == 0 and os.path.exists(final_path):
                    target_file = final_path
                else:
                    target_file = raw_path

                with open(target_file, "rb") as f:
                    return f.read()

            finally:
                if os.path.exists(raw_path):
                    os.remove(raw_path)
                if os.path.exists(final_path):
                    os.remove(final_path)

        wav_bytes = await asyncio.to_thread(_run_synthesis)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        log_event(
            event="tts_completed",
            stage="tts",
            language=language,
            model=f"mac_native:{selected_voice}",
            latency_ms=elapsed_ms,
            status="SUCCESS",
            extra={"bytes": len(wav_bytes), "voice": selected_voice, "emotion": emotion, "style": style},
        )
        return wav_bytes


mac_tts_engine = MacNativeTTSEngine()

