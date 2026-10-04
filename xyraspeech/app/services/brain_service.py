"""Enhanced Cognitive Speech Intelligence Service for XyraSpeech."""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

from xyrabrain.app.models.enums import Emotion, ProcessingMode, SpeakingStyle, SupportedLanguage
from xyrabrain.app.schemas.brain import DirectionMetadata, SpeechDirection, SpeechSegment
from xyrabrain.app.services.language_service import language_service
from xyrabrain.app.services.ollama_client import ollama_client
from xyrabrain.app.services.validation_service import validation_service
from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import log_event, logger
from xyraspeech.app.models.enums import UserIntent
from xyraspeech.app.orchestration.context_manager import ConversationContext, context_manager


class EnhancedBrainService:
    """Central Intelligence Layer: Language, Intent, Memory, Response Generation, and Speech Performance Planning."""

    def classify_intent(self, text: str) -> UserIntent:
        """Determines the user intent from text heuristics and semantics."""
        cleaned = text.strip().lower()
        if any(w in cleaned for w in ["hello", "hi", "hey", "வணக்கம்", "good morning", "good evening"]):
            return UserIntent.GREETING
        if cleaned.endswith("?") or any(w in cleaned for w in ["what", "why", "how", "when", "who", "where", "எப்படி", "என்ன", "எப்போது", "ஏன்"]):
            return UserIntent.QUESTION
        if any(w in cleaned for w in ["translate", "மொழிபெயர்", "meaning of"]):
            return UserIntent.TRANSLATION_REQUEST
        if any(w in cleaned for w in ["stop", "pause", "resume", "volume", "quiet"]):
            return UserIntent.VOICE_COMMAND
        if any(w in cleaned for w in ["i feel", "i am sad", "i am happy", "வருத்தமாக", "மகிழ்ச்சியாக"]):
            return UserIntent.EMOTIONAL_MESSAGE
        return UserIntent.CASUAL_CONVERSATION

    async def generate_conversational_response(
        self,
        user_input: str,
        context: ConversationContext,
        forced_language: Optional[str] = None,
    ) -> Tuple[str, str, UserIntent, SpeechDirection]:
        """Understands user input, generates contextual response, and produces fine-grained SpeechDirection.

        Returns: (response_text, language, intent, speech_direction)
        """
        start_time = time.perf_counter()

        # 1. Language Analysis
        detected_lang_enum = language_service.validate_or_detect(user_input, forced_language)
        lang_code = detected_lang_enum.value

        # 2. Intent Analysis
        intent = self.classify_intent(user_input)

        # 3. Context & Memory Integration
        context_snippet = context.get_context_prompt_snippet()
        lang_name = "Tamil" if lang_code == "ta" else ("Tamil-English Mixed" if lang_code == "ta-en" else "English")

        # 4. Master Prompt
        system_prompt = (
            f"You are XyraSpeech, an intelligent and empathetic real-time AI voice assistant.\n"
            f"Active Language: {lang_name} ({lang_code}).\n\n"
            f"CRITICAL RULES:\n"
            f"1. Conversational Memory: Use the user's name and previous context if available.\n"
            f"2. Language Fidelity: You MUST respond in {lang_name}.\n"
            f"   - If input is Tamil, reply strictly in fluent Tamil script.\n"
            f"   - If input is English, reply in natural conversational English.\n"
            f"   - If input is Mixed (code-switching), reply in natural conversational mixed language.\n"
            f"   - NEVER translate or Romanize Tamil text.\n"
            f"3. Brevity for Voice: Keep spoken responses natural, concise (1-3 sentences), warm, and engaging.\n"
            f"4. Controlled Speech Metadata: Infer accurate emotion, speaking style, energy (0.0-1.0), and speed (0.5-1.5).\n"
            f"5. Output Schema: Return ONLY valid JSON matching this schema:\n"
            f"{{\n"
            f'  "response_text": "Spoken reply in {lang_name}",\n'
            f'  "overall_emotion": "happy|excited|neutral|warm|curious|concerned|empathetic|calm|serious|confident",\n'
            f'  "overall_style": "conversational|friendly|warm|enthusiastic|professional|calm|instructional",\n'
            f'  "energy": 0.6,\n'
            f'  "speed": 1.0,\n'
            f'  "pitch": 1.0,\n'
            f'  "segments": [\n'
            f'    {{\n'
            f'      "text": "Segment 1 text",\n'
            f'      "emotion": "happy",\n'
            f'      "style": "conversational",\n'
            f'      "energy": 0.6,\n'
            f'      "speed": 1.0,\n'
            f'      "pitch": 1.0,\n'
            f'      "emphasis": [],\n'
            f'      "pause_after_ms": 250\n'
            f'    }}\n'
            f'  ]\n'
            f"}}"
        )

        user_prompt = f"{context_snippet}\n\nUser: {user_input}\nAssistant:"

        try:
            raw_json = await ollama_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_format=True,
            )

            response_text = raw_json.get("response_text", "").strip()
            if not response_text:
                raise ValueError("Empty response text from LLM")

            overall_emotion = validation_service.normalize_emotion(raw_json.get("overall_emotion"))
            overall_style = validation_service.normalize_style(raw_json.get("overall_style"))

            raw_segs = raw_json.get("segments", [])
            segments = []
            if isinstance(raw_segs, list) and raw_segs:
                for s in raw_segs:
                    if isinstance(s, dict) and s.get("text"):
                        segments.append(validation_service.normalize_segment(s))

            if not segments:
                segments.append(
                    SpeechSegment(
                        text=response_text,
                        emotion=overall_emotion,
                        style=overall_style,
                        energy=validation_service.clamp_numeric(raw_json.get("energy"), 0.0, 1.0, 0.5),
                        speed=validation_service.clamp_numeric(raw_json.get("speed"), 0.5, 1.5, 1.0),
                        pitch=validation_service.clamp_numeric(raw_json.get("pitch"), 0.8, 1.2, 1.0),
                        pause_after_ms=300,
                    )
                )

        except Exception as exc:
            logger.warning(f"Ollama conversational generation fallback due to: {str(exc)}")
            # Deterministic fallback response preserving language
            if lang_code == "ta":
                response_text = f"வணக்கம் {context.user_name or ''}! நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?".strip()
                overall_emotion = Emotion.WARM
                overall_style = SpeakingStyle.FRIENDLY
            else:
                response_text = f"Hello {context.user_name or ''}! How can I help you today?".strip()
                overall_emotion = Emotion.WARM
                overall_style = SpeakingStyle.FRIENDLY

            segments = [
                SpeechSegment(
                    text=response_text,
                    emotion=overall_emotion,
                    style=overall_style,
                    energy=0.6,
                    speed=1.0,
                    pitch=1.0,
                    pause_after_ms=300,
                )
            ]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        speech_direction = SpeechDirection(
            language=detected_lang_enum,
            speech_text=response_text,
            overall_style=overall_style,
            overall_emotion=overall_emotion,
            segments=segments,
            metadata=DirectionMetadata(
                model=f"ollama:{ollama_client.model}",
                processing_mode=ProcessingMode.EXPRESSIVE,
                processing_time_ms=elapsed_ms,
                schema_version="1.0",
            ),
        )

        # Update context
        context.add_user_message(user_input, lang_code)
        context.add_assistant_message(response_text, lang_code)

        log_event(
            event="brain_response_generated",
            session_id=context.conversation_id,
            stage="brain",
            language=lang_code,
            model=ollama_client.model,
            latency_ms=elapsed_ms,
            status="SUCCESS",
            extra={"intent": intent.value, "emotion": overall_emotion.value},
        )

        return response_text, lang_code, intent, speech_direction


enhanced_brain_service = EnhancedBrainService()
