"""Real-Time Interactive Voice Session with Barge-in Interruption."""

import asyncio
import base64
import time
import uuid
from typing import Any, Dict, Optional
from fastapi import WebSocket

from xyrabrain.app.services.expression_adapter import ExpressionAdapter
from xyraspeech.app.core.audio import audio_processor
from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import log_event, logger
from xyraspeech.app.engines.stt.whisper_engine import whisper_engine
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.models.enums import WebSocketEventType
from xyraspeech.app.orchestration.context_manager import ConversationContext, context_manager
from xyraspeech.app.schemas.events import WSOutboundEvent
from xyraspeech.app.services.brain_service import enhanced_brain_service


class ConversationSession:
    """Manages an active WebSocket streaming voice conversation session."""

    def __init__(self, websocket: WebSocket, session_id: Optional[str] = None):
        self.websocket = websocket
        self.session_id = session_id or str(uuid.uuid4())
        self.context: ConversationContext = context_manager.get_or_create(self.session_id)
        self.active_task: Optional[asyncio.Task] = None
        self.audio_buffer = bytearray()
        self.is_speaking = False
        self.silence_frames_count = 0
        self.is_closed = False

    async def send_event(self, event_type: WebSocketEventType, data: Dict[str, Any], error: Optional[str] = None):
        """Sends structured event payload to the connected WebSocket client."""
        if self.is_closed:
            return
        payload = WSOutboundEvent(
            event=event_type,
            session_id=self.session_id,
            data=data,
            error=error,
        )
        try:
            await self.websocket.send_json(payload.model_dump())
        except Exception as exc:
            logger.warning(f"Failed to send WS event to {self.session_id}: {exc}")

    async def interrupt(self) -> None:
        """Barge-in: Immediately cancels active speech generation and audio playback."""
        if self.active_task and not self.active_task.done():
            logger.info(f"[INTERRUPT] Cancelling active speech task for session {self.session_id}")
            self.active_task.cancel()
            try:
                await self.active_task
            except asyncio.CancelledError:
                pass
            self.active_task = None

        await self.send_event(
            WebSocketEventType.INTERRUPT,
            {"status": "speech_interrupted", "message": "Playback cancelled due to user interruption."},
        )

    async def process_user_audio_buffer(self) -> None:
        """Dispatches buffered audio through the complete STT -> Brain -> TTS pipeline."""
        if len(self.audio_buffer) < 4000:  # Ignore tiny clicks/noise (<0.25s)
            self.audio_buffer.clear()
            return

        raw_audio = bytes(self.audio_buffer)
        self.audio_buffer.clear()

        # Cancel any ongoing output before processing new speech
        await self.interrupt()

        self.active_task = asyncio.create_task(self._pipeline_task(raw_audio))

    async def _pipeline_task(self, raw_audio: bytes) -> None:
        """Executes the full pipeline with timing telemetry."""
        total_start = time.perf_counter()
        try:
            # 1. STT Transcription
            stt_start = time.perf_counter()
            await self.send_event(WebSocketEventType.SPEECH_START, {"status": "transcribing"})
            stt_result = await whisper_engine.transcribe(raw_audio)
            stt_elapsed = (time.perf_counter() - stt_start) * 1000.0

            if not stt_result.text.strip():
                await self.send_event(WebSocketEventType.SPEECH_FINISHED, {"message": "No speech detected."})
                return

            await self.send_event(
                WebSocketEventType.TRANSCRIPT_FINAL,
                {
                    "text": stt_result.text,
                    "language": stt_result.language,
                    "duration_sec": stt_result.duration_seconds,
                    "stt_latency_ms": round(stt_elapsed, 2),
                },
            )

            # 2. Cognitive Brain Intelligence
            brain_start = time.perf_counter()
            await self.send_event(WebSocketEventType.BRAIN_STARTED, {"status": "thinking"})
            response_text, lang_code, intent, speech_dir = await enhanced_brain_service.generate_conversational_response(
                user_input=stt_result.text,
                context=self.context,
                forced_language=stt_result.language,
            )
            brain_elapsed = (time.perf_counter() - brain_start) * 1000.0

            await self.send_event(
                WebSocketEventType.BRAIN_RESPONSE,
                {
                    "response_text": response_text,
                    "language": lang_code,
                    "intent": intent.value,
                    "overall_emotion": speech_dir.overall_emotion.value,
                    "overall_style": speech_dir.overall_style.value,
                    "brain_latency_ms": round(brain_elapsed, 2),
                    "segments": [s.model_dump() for s in speech_dir.segments],
                },
            )

            # 3. Real Local TTS Synthesis & Audio Streaming
            tts_start = time.perf_counter()
            await self.send_event(WebSocketEventType.SPEECH_STARTED, {"status": "generating_audio"})

            # Select real voice
            voice = voice_registry.get_default_voice(lang_code)

            # Synthesize entire response or segments
            first_seg = speech_dir.segments[0] if speech_dir.segments else None
            speed = first_seg.speed if first_seg else 1.0
            pitch = first_seg.pitch if first_seg else 1.0
            energy = first_seg.energy if first_seg else 0.5

            wav_bytes = await mac_tts_engine.synthesize(
                text=response_text,
                language=lang_code,
                voice_id=voice.id,
                speed=speed,
                pitch=pitch,
                energy=energy,
                emotion=speech_dir.overall_emotion.value,
                style=speech_dir.overall_style.value,
            )
            tts_elapsed = (time.perf_counter() - tts_start) * 1000.0

            # Stream audio chunk to client as base64
            b64_audio = base64.b64encode(wav_bytes).decode("utf-8")
            await self.send_event(
                WebSocketEventType.AUDIO_OUT_CHUNK,
                {
                    "audio_base64": b64_audio,
                    "format": "wav",
                    "sample_rate": voice.sample_rate,
                    "tts_latency_ms": round(tts_elapsed, 2),
                },
            )

            total_elapsed = (time.perf_counter() - total_start) * 1000.0
            await self.send_event(
                WebSocketEventType.SPEECH_FINISHED,
                {
                    "total_latency_ms": round(total_elapsed, 2),
                    "stt_ms": round(stt_elapsed, 2),
                    "brain_ms": round(brain_elapsed, 2),
                    "tts_ms": round(tts_elapsed, 2),
                },
            )

        except asyncio.CancelledError:
            logger.info(f"Pipeline task for session {self.session_id} was cancelled cleanly.")
        except Exception as exc:
            logger.exception(f"Session pipeline error: {exc}")
            await self.send_event(WebSocketEventType.ERROR, {}, error=str(exc))
