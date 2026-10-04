"""Master Conversation Orchestrator."""

import base64
import time
from typing import Dict, Optional
from fastapi import WebSocket

from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import log_event, logger
from xyraspeech.app.engines.stt.whisper_engine import whisper_engine
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.orchestration.context_manager import ConversationContext, context_manager
from xyraspeech.app.orchestration.session import ConversationSession
from xyraspeech.app.schemas.conversation import (
    ConversationMessageResponse,
    LatencyBreakdown,
)
from xyraspeech.app.services.brain_service import enhanced_brain_service


class ConversationOrchestrator:
    """Orchestrates conversations across REST and WebSocket interfaces."""

    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def create_session(self, websocket: WebSocket, session_id: Optional[str] = None) -> ConversationSession:
        """Creates and registers an active WebSocket session."""
        session = ConversationSession(websocket=websocket, session_id=session_id)
        self._sessions[session.session_id] = session
        return session

    def remove_session(self, session_id: str) -> None:
        """Removes an ended session."""
        if session_id in self._sessions:
            self._sessions[session_id].is_closed = True
            del self._sessions[session_id]

    async def process_text_message(
        self,
        text: str,
        conversation_id: Optional[str] = None,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> ConversationMessageResponse:
        """Processes a single text turn through Brain -> TTS with audio generation."""
        total_start = time.perf_counter()
        context = context_manager.get_or_create(conversation_id)

        # 1. Cognitive Brain Intelligence
        brain_start = time.perf_counter()
        response_text, lang_code, intent, speech_dir = await enhanced_brain_service.generate_conversational_response(
            user_input=text,
            context=context,
            forced_language=language,
        )
        brain_elapsed = (time.perf_counter() - brain_start) * 1000.0

        # 2. Real Local TTS Audio Synthesis
        tts_start = time.perf_counter()
        voice = voice_registry.get_voice(voice_id) if voice_id else voice_registry.get_default_voice(lang_code)

        first_seg = speech_dir.segments[0] if speech_dir.segments else None
        speed = first_seg.speed if first_seg else 1.0
        pitch = first_seg.pitch if first_seg else 1.0
        energy = first_seg.energy if first_seg else 0.5

        wav_bytes = await mac_tts_engine.synthesize(
            text=response_text,
            language=lang_code,
            voice_id=voice.id if voice else None,
            speed=speed,
            pitch=pitch,
            energy=energy,
            emotion=speech_dir.overall_emotion.value,
            style=speech_dir.overall_style.value,
        )
        tts_elapsed = (time.perf_counter() - tts_start) * 1000.0
        total_elapsed = (time.perf_counter() - total_start) * 1000.0

        b64_audio = base64.b64encode(wav_bytes).decode("utf-8")

        return ConversationMessageResponse(
            conversation_id=context.conversation_id,
            user_input=text,
            response_text=response_text,
            language=lang_code,
            intent=intent.value,
            speech_direction=speech_dir,
            audio_base64=b64_audio,
            latency_metrics=LatencyBreakdown(
                brain_ms=round(brain_elapsed, 2),
                tts_first_audio_ms=round(tts_elapsed, 2),
                total_ms=round(total_elapsed, 2),
            ),
        )


orchestrator = ConversationOrchestrator()
