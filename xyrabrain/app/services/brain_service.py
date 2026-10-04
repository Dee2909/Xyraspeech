"""Core Brain Service orchestrating RAW, ENHANCED, and EXPRESSIVE modes."""

import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from xyrabrain.app.core.config import settings
from xyrabrain.app.core.logging import logger, log_structured_event
from xyrabrain.app.models.enums import (
    Emotion,
    ProcessingMode,
    SpeakingStyle,
    SupportedLanguage,
)
from xyrabrain.app.schemas.brain import (
    DirectionMetadata,
    SpeechDirection,
    SpeechSegment,
)
from xyrabrain.app.services.language_service import language_service
from xyrabrain.app.services.ollama_client import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    ollama_client,
)
from xyrabrain.app.services.validation_service import (
    TextPreservationError,
    validation_service,
)


class BrainService:
    """Orchestrates speech intelligence analysis across RAW, ENHANCED, and EXPRESSIVE modes."""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or ollama_client
        self._prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self._system_prompt = self._load_prompt("system_prompt.txt")
        self._expressive_prompt = self._load_prompt("expressive_prompt.txt")
        self._enhancement_prompt = self._load_prompt("enhancement_prompt.txt")

    def _load_prompt(self, filename: str) -> str:
        prompt_path = self._prompts_dir / filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        logger.warning(f"Prompt file {filename} not found at {prompt_path}. Using fallback.")
        return ""

    async def process(
        self,
        text: str,
        language: Optional[SupportedLanguage] = None,
        mode: ProcessingMode = ProcessingMode.EXPRESSIVE,
        request_id: Optional[str] = None,
    ) -> SpeechDirection:
        """Entrypoint for processing speech intelligence on input text."""
        start_time = time.perf_counter()

        # 1. Validate & Detect Language
        validated_lang = language_service.validate_or_detect(text, language)

        # 2. Dispatch according to Processing Mode
        if mode == ProcessingMode.RAW:
            result = self._process_raw(text, validated_lang, start_time)
        elif mode == ProcessingMode.ENHANCED:
            result = await self._process_enhanced(text, validated_lang, start_time)
        elif mode == ProcessingMode.EXPRESSIVE:
            result = await self._process_expressive(text, validated_lang, start_time)
        else:
            raise ValueError(f"Unsupported processing mode: {mode}")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        log_structured_event(
            event="brain_processing_completed",
            request_id=request_id,
            mode=mode.value,
            language=validated_lang.value,
            model=result.metadata.model,
            processing_time_ms=elapsed_ms,
            status="SUCCESS",
        )
        return result

    def _process_raw(
        self,
        text: str,
        language: SupportedLanguage,
        start_time: float,
    ) -> SpeechDirection:
        """Processes text in RAW mode without calling Ollama. Exact preservation."""
        # Simple punctuation-aware segmentation that preserves exact words
        # Split on sentence boundaries (. ! ? \n)
        raw_parts = re.split(r"(?<=[.!?\n])\s+", text)
        segments: List[SpeechSegment] = []

        for part in raw_parts:
            part_str = part.strip()
            if not part_str:
                continue

            # Determine pause based on ending punctuation
            pause_after = 250
            if part_str.endswith("..."):
                pause_after = 500
            elif part_str.endswith("?") or part_str.endswith("!"):
                pause_after = 350
            elif part_str.endswith("."):
                pause_after = 300

            segments.append(
                SpeechSegment(
                    text=part_str,
                    emotion=Emotion.NEUTRAL,
                    style=SpeakingStyle.NEUTRAL,
                    energy=0.5,
                    speed=1.0,
                    pitch=1.0,
                    emphasis=[],
                    pause_before_ms=0,
                    pause_after_ms=pause_after,
                    pronunciation_hint=None,
                )
            )

        if not segments:
            segments.append(
                SpeechSegment(
                    text=text,
                    emotion=Emotion.NEUTRAL,
                    style=SpeakingStyle.NEUTRAL,
                    energy=0.5,
                    speed=1.0,
                    pitch=1.0,
                    emphasis=[],
                    pause_before_ms=0,
                    pause_after_ms=0,
                )
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metadata = DirectionMetadata(
            model="internal:raw_passthrough",
            processing_mode=ProcessingMode.RAW,
            processing_time_ms=elapsed_ms,
            schema_version="1.0",
            retry_count=0,
        )

        return SpeechDirection(
            language=language,
            speech_text=text,
            overall_style=SpeakingStyle.NEUTRAL,
            overall_emotion=Emotion.NEUTRAL,
            segments=segments[: settings.MAX_SEGMENTS],
            metadata=metadata,
        )

    async def _process_enhanced(
        self,
        text: str,
        language: SupportedLanguage,
        start_time: float,
    ) -> SpeechDirection:
        """Uses Ollama to enhance punctuation and flow without altering semantics."""
        user_prompt = self._enhancement_prompt.format(
            language=language.value,
            text=text,
        )

        response_json = await self.client.chat(
            system_prompt=self._system_prompt,
            user_prompt=user_prompt,
        )

        speech_text = response_json.get("speech_text", text).strip()
        overall_style = validation_service.normalize_style(response_json.get("overall_style", "conversational"))
        overall_emotion = validation_service.normalize_emotion(response_json.get("overall_emotion", "neutral"))

        raw_segments = response_json.get("segments", [])
        segments: List[SpeechSegment] = []
        if isinstance(raw_segments, list) and raw_segments:
            for s in raw_segments:
                if isinstance(s, dict) and s.get("text"):
                    segments.append(validation_service.normalize_segment(s))

        if not segments:
            # Fallback segment if model omitted segments
            segments.append(
                SpeechSegment(
                    text=speech_text,
                    emotion=overall_emotion,
                    style=overall_style,
                    energy=0.5,
                    speed=1.0,
                    pitch=1.0,
                    pause_after_ms=250,
                )
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metadata = DirectionMetadata(
            model=f"ollama:{self.client.model}",
            processing_mode=ProcessingMode.ENHANCED,
            processing_time_ms=elapsed_ms,
            schema_version="1.0",
            retry_count=0,
        )

        return SpeechDirection(
            language=language,
            speech_text=speech_text,
            overall_style=overall_style,
            overall_emotion=overall_emotion,
            segments=segments[: settings.MAX_SEGMENTS],
            metadata=metadata,
        )

    async def _process_expressive(
        self,
        text: str,
        language: SupportedLanguage,
        start_time: float,
    ) -> SpeechDirection:
        """Performs full expressive speech-performance analysis with validation retries."""
        last_error: Optional[Exception] = None
        retries = 0

        user_prompt = self._expressive_prompt.format(
            language=language.value,
            text=text,
        )

        while retries <= settings.MAX_RETRIES:
            try:
                response_json = await self.client.chat(
                    system_prompt=self._system_prompt,
                    user_prompt=user_prompt,
                )

                speech_text = response_json.get("speech_text", text).strip()

                # Verify text preservation (no hallucinations, translations, or missing numbers)
                validation_service.verify_text_preservation(text, speech_text, language)

                overall_style = validation_service.normalize_style(response_json.get("overall_style"))
                overall_emotion = validation_service.normalize_emotion(response_json.get("overall_emotion"))

                raw_segments = response_json.get("segments", [])
                segments: List[SpeechSegment] = []
                if isinstance(raw_segments, list) and raw_segments:
                    for s in raw_segments:
                        if isinstance(s, dict) and s.get("text"):
                            segments.append(validation_service.normalize_segment(s))

                if not segments:
                    segments.append(
                        SpeechSegment(
                            text=speech_text,
                            emotion=overall_emotion,
                            style=overall_style,
                            energy=0.5,
                            speed=1.0,
                            pitch=1.0,
                            pause_after_ms=300,
                        )
                    )

                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                metadata = DirectionMetadata(
                    model=f"ollama:{self.client.model}",
                    processing_mode=ProcessingMode.EXPRESSIVE,
                    processing_time_ms=elapsed_ms,
                    schema_version="1.0",
                    retry_count=retries,
                )

                return SpeechDirection(
                    language=language,
                    speech_text=speech_text,
                    overall_style=overall_style,
                    overall_emotion=overall_emotion,
                    segments=segments[: settings.MAX_SEGMENTS],
                    metadata=metadata,
                )

            except (OllamaConnectionError, OllamaModelNotFoundError):
                # Immediate exit without useless retries if Ollama server is unreachable or model not found
                raise
            except (TextPreservationError, OllamaTimeoutError, OllamaClientError, KeyError, ValueError) as exc:
                last_error = exc
                retries += 1
                logger.warning(
                    f"Expressive analysis attempt {retries} failed: {str(exc)}. Retrying..."
                )
                # Adjust prompt on retry to emphasize strict language & text preservation
                user_prompt = (
                    f"{self._expressive_prompt.format(language=language.value, text=text)}\n\n"
                    f"CRITICAL REMINDER FOR RETRY: Do NOT translate. Keep exact original {language.value} words. Return exact JSON."
                )

        # If retries exceeded, propagate original specific exception if present
        if last_error:
            if isinstance(last_error, (OllamaConnectionError, OllamaTimeoutError, OllamaModelNotFoundError, TextPreservationError)):
                raise last_error
            raise OllamaClientError(
                f"Failed to produce valid speech directions after {settings.MAX_RETRIES} attempts. Reason: {str(last_error)}"
            ) from last_error

        raise OllamaClientError(
            f"Failed to produce valid speech directions after {settings.MAX_RETRIES} attempts."
        )


brain_service = BrainService()
