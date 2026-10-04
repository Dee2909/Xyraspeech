"""Production High-Fidelity Human Neural Synthesizer with Studio Mastering (Tamil & English)."""

import asyncio
import io
import os
import re
import subprocess
import tempfile
import time
from typing import Optional, Set

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import log_event, logger
from xyraspeech.app.engines.tts.base import BaseTTSEngine
from xyraspeech.app.models.enums import TTSCapability


class MacNativeTTSEngine(BaseTTSEngine):
    """Production TTS Engine featuring Neural Human Voices for Tamil and English with Studio Acoustic Mastering."""

    # High-quality neural voices mapped to IDs
    NEURAL_VOICE_MAP = {
        "ta_pallavi": "ta-IN-PallaviNeural",
        "ta_valluvar": "ta-IN-ValluvarNeural",
        "en_neerja": "en-IN-NeerjaExpressiveNeural",
        "en_prabhat": "en-IN-PrabhatNeural",
        "ta": "ta-IN-PallaviNeural",
        "en": "en-IN-NeerjaExpressiveNeural",
        "ta-en": "ta-IN-PallaviNeural",
    }

    # macOS native fallback voices
    MAC_VOICE_MAP = {
        "ta_vani": "Vani",
        "en_rishi": "Rishi",
        "en_tara": "Tara",
        "en_samantha": "Samantha",
        "en_daniel": "Daniel",
        "ta_pallavi": "Vani",
        "ta_valluvar": "Vani",
        "en_neerja": "Tara",
        "en_prabhat": "Rishi",
        "ta": "Vani",
        "en": "Rishi",
        "ta-en": "Vani",
    }

    def get_capabilities(self) -> Set[TTSCapability]:
        """Engine supports speed, pitch, energy, pause, emotion & style."""
        return {
            TTSCapability.SUPPORTS_SPEED,
            TTSCapability.SUPPORTS_PITCH,
            TTSCapability.SUPPORTS_ENERGY,
            TTSCapability.SUPPORTS_PAUSE,
            TTSCapability.SUPPORTS_EMOTION,
            TTSCapability.SUPPORTS_STYLE,
        }

    def _prepare_natural_text(self, text: str) -> str:
        """Cleans and formats text for natural human cadence."""
        cleaned = text.strip()
        cleaned = re.sub(r'([.,!?:;])([^\s])', r'\1 \2', cleaned)
        cleaned = cleaned.replace("...", ", ")
        cleaned = cleaned.replace("—", " — ").replace("--", " — ")
        return cleaned

    def _build_dsp_filter_chain(
        self,
        energy_factor: float,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
    ) -> str:
        """Constructs an FFmpeg DSP filter graph for warm, human broadcast-quality audio."""
        filters = []
        filters.append("highpass=f=75")

        emo = (emotion or "").lower()
        sty = (style or "").lower()

        if emo in ["warm", "empathetic", "friendly", "calm"] or sty in ["warm", "friendly", "empathetic"]:
            filters.append("equalizer=f=220:width_type=o:width=1.2:g=2.2")
            filters.append("equalizer=f=3200:width_type=o:width=1.5:g=1.5")
            filters.append("equalizer=f=8000:width_type=o:width=1.0:g=-1.0")
        elif emo in ["excited", "happy"] or sty in ["enthusiastic", "energetic"]:
            filters.append("equalizer=f=200:width_type=o:width=1.0:g=1.2")
            filters.append("equalizer=f=3500:width_type=o:width=1.4:g=2.5")
        else:
            filters.append("equalizer=f=230:width_type=o:width=1.2:g=1.8")
            filters.append("equalizer=f=3200:width_type=o:width=1.5:g=1.5")

        # Studio Dynamic Compressor
        filters.append("acompressor=threshold=-16dB:ratio=2.5:attack=15:release=120:makeup=1.5dB")
        # Gentle Room Ambience
        filters.append("aecho=0.85:0.88:15:0.08")

        # Gain
        vol_gain = 0.90 + (energy_factor * 0.30)
        if abs(vol_gain - 1.0) > 0.03:
            filters.append(f"volume={vol_gain:.2f}")

        filters.append("alimiter=limit=0.95")
        return ",".join(filters)

    async def _synthesize_neural(
        self,
        text: str,
        voice_name: str,
        speed_factor: float,
        pitch_factor: float,
        energy_factor: float,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
    ) -> bytes:
        """Synthesizes high-fidelity speech using Edge Neural TTS."""
        rate_pct = int((speed_factor - 1.0) * 100)
        rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

        pitch_hz = int((pitch_factor - 1.0) * 50)
        pitch_str = f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"

        vol_pct = int((energy_factor - 0.5) * 40)
        vol_str = f"+{vol_pct}%" if vol_pct >= 0 else f"{vol_pct}%"

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_name,
            rate=rate_str,
            pitch=pitch_str,
            volume=vol_str,
        )

        mp3_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_buffer.extend(chunk["data"])

        if not mp3_buffer:
            raise ValueError(f"Neural TTS returned 0 audio bytes for voice '{voice_name}'.")

        # Master to pristine 24kHz WAV with FFmpeg DSP
        dsp_filter = self._build_dsp_filter_chain(energy_factor, emotion, style)

        def _master_audio() -> bytes:
            proc = subprocess.Popen(
                [
                    "ffmpeg",
                    "-y",
                    "-i", "pipe:0",
                    "-af", dsp_filter,
                    "-ar", "24000",
                    "-f", "wav",
                    "pipe:1",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            wav_out, err = proc.communicate(input=bytes(mp3_buffer))
            if proc.returncode != 0 or not wav_out:
                logger.warning(f"FFmpeg mastering warning: {err.decode('utf-8', errors='ignore')}")
                # Fallback to direct conversion without filters
                proc2 = subprocess.Popen(
                    ["ffmpeg", "-y", "-i", "pipe:0", "-ar", "24000", "-f", "wav", "pipe:1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                wav_out, _ = proc2.communicate(input=bytes(mp3_buffer))
            return wav_out

        return await asyncio.to_thread(_master_audio)

    async def _synthesize_mac_fallback(
        self,
        text: str,
        mac_voice: str,
        speed_factor: float,
        pitch_factor: float,
        energy_factor: float,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
    ) -> bytes:
        """Fallback synthesis using macOS native TTS."""
        base_wpm = 158
        wpm = int(base_wpm * speed_factor)

        def _run_mac() -> bytes:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw_wav:
                raw_path = raw_wav.name
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as final_wav:
                final_path = final_wav.name

            try:
                say_cmd = [
                    "say",
                    "-v", mac_voice,
                    "-r", str(wpm),
                    "-o", raw_path,
                    "--data-format=LEF32@24000",
                    text,
                ]
                subprocess.run(say_cmd, capture_output=True, text=True)

                filter_str = self._build_dsp_filter_chain(energy_factor, emotion, style)
                ff_cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", raw_path,
                    "-af", filter_str,
                    "-ar", "24000",
                    final_path,
                ]
                subprocess.run(ff_cmd, capture_output=True)
                target_file = final_path if os.path.exists(final_path) else raw_path

                with open(target_file, "rb") as f:
                    return f.read()
            finally:
                if os.path.exists(raw_path):
                    os.remove(raw_path)
                if os.path.exists(final_path):
                    os.remove(final_path)

        return await asyncio.to_thread(_run_mac)

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

        speed_factor = max(0.5, min(1.5, float(speed or 1.0)))
        pitch_factor = max(0.8, min(1.2, float(pitch or 1.0)))
        energy_factor = float(energy or 0.5)

        natural_text = self._prepare_natural_text(text)
        vid = (voice_id or "").lower()

        # Try Neural synthesis first if available
        if HAS_EDGE_TTS:
            neural_voice = None
            if vid in self.NEURAL_VOICE_MAP:
                neural_voice = self.NEURAL_VOICE_MAP[vid]
            elif language in self.NEURAL_VOICE_MAP:
                neural_voice = self.NEURAL_VOICE_MAP[language]

            if neural_voice:
                try:
                    wav_bytes = await self._synthesize_neural(
                        text=natural_text,
                        voice_name=neural_voice,
                        speed_factor=speed_factor,
                        pitch_factor=pitch_factor,
                        energy_factor=energy_factor,
                        emotion=emotion,
                        style=style,
                    )
                    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                    log_event(
                        event="tts_completed",
                        stage="tts",
                        language=language,
                        model=f"neural:{neural_voice}",
                        latency_ms=elapsed_ms,
                        status="SUCCESS",
                        extra={"bytes": len(wav_bytes), "voice": neural_voice, "emotion": emotion},
                    )
                    return wav_bytes
                except Exception as exc:
                    logger.warning(f"Neural TTS failed for voice '{neural_voice}', falling back to Mac native: {str(exc)}")

        # Fallback to macOS native
        mac_voice = self.MAC_VOICE_MAP.get(vid, self.MAC_VOICE_MAP.get(language, "Vani" if language == "ta" else "Rishi"))
        wav_bytes = await self._synthesize_mac_fallback(
            text=natural_text,
            mac_voice=mac_voice,
            speed_factor=speed_factor,
            pitch_factor=pitch_factor,
            energy_factor=energy_factor,
            emotion=emotion,
            style=style,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        log_event(
            event="tts_completed",
            stage="tts",
            language=language,
            model=f"mac_native:{mac_voice}",
            latency_ms=elapsed_ms,
            status="SUCCESS",
            extra={"bytes": len(wav_bytes), "voice": mac_voice, "emotion": emotion},
        )
        return wav_bytes


mac_tts_engine = MacNativeTTSEngine()


