"""Validation, Clamping, and Text-Preservation Verification Service."""

import re
from typing import Any, Dict, List, Optional
from xyrabrain.app.core.config import settings
from xyrabrain.app.core.logging import logger
from xyrabrain.app.models.enums import Emotion, SpeakingStyle, SupportedLanguage
from xyrabrain.app.schemas.brain import SpeechSegment
from xyrabrain.app.services.language_service import language_service


class TextPreservationError(Exception):
    """Raised when generated speech_text violates text-preservation constraints."""
    pass


class ValidationService:
    """Provides value clamping, controlled vocabulary normalization, and semantic faithfulness checks."""

    @classmethod
    def clamp_numeric(cls, val: Any, min_val: float, max_val: float, default: float) -> float:
        """Clamps a floating point value to the configured range."""
        try:
            num = float(val)
            return max(min_val, min(num, max_val))
        except (ValueError, TypeError):
            return default

    @classmethod
    def clamp_int(cls, val: Any, min_val: int, max_val: int, default: int) -> int:
        """Clamps an integer value to the configured range."""
        try:
            num = int(val)
            return max(min_val, min(num, max_val))
        except (ValueError, TypeError):
            return default

    @classmethod
    def normalize_emotion(cls, raw_emotion: Any) -> Emotion:
        """Normalizes raw string to valid Emotion enum, defaulting to NEUTRAL."""
        if isinstance(raw_emotion, Emotion):
            return raw_emotion
        if not raw_emotion or not isinstance(raw_emotion, str):
            return Emotion.NEUTRAL
        cleaned = raw_emotion.strip().lower()
        try:
            return Emotion(cleaned)
        except ValueError:
            logger.warning(f"Unrecognized emotion '{raw_emotion}', falling back to 'neutral'")
            return Emotion.NEUTRAL

    @classmethod
    def normalize_style(cls, raw_style: Any) -> SpeakingStyle:
        """Normalizes raw string to valid SpeakingStyle enum, defaulting to NEUTRAL."""
        if isinstance(raw_style, SpeakingStyle):
            return raw_style
        if not raw_style or not isinstance(raw_style, str):
            return SpeakingStyle.NEUTRAL
        cleaned = raw_style.strip().lower()
        try:
            return SpeakingStyle(cleaned)
        except ValueError:
            logger.warning(f"Unrecognized style '{raw_style}', falling back to 'neutral'")
            return SpeakingStyle.NEUTRAL

    @classmethod
    def normalize_segment(cls, raw_seg: Dict[str, Any]) -> SpeechSegment:
        """Normalizes and clamps all properties of a single speech segment."""
        text = str(raw_seg.get("text", "")).strip()
        emotion = cls.normalize_emotion(raw_seg.get("emotion"))
        style = cls.normalize_style(raw_seg.get("style"))
        energy = cls.clamp_numeric(
            raw_seg.get("energy"), settings.MIN_ENERGY, settings.MAX_ENERGY, 0.5
        )
        speed = cls.clamp_numeric(
            raw_seg.get("speed"), settings.MIN_SPEED, settings.MAX_SPEED, 1.0
        )
        pitch = cls.clamp_numeric(
            raw_seg.get("pitch"), settings.MIN_PITCH, settings.MAX_PITCH, 1.0
        )
        pause_before = cls.clamp_int(
            raw_seg.get("pause_before_ms"), settings.MIN_PAUSE_MS, settings.MAX_PAUSE_MS, 0
        )
        pause_after = cls.clamp_int(
            raw_seg.get("pause_after_ms"), settings.MIN_PAUSE_MS, settings.MAX_PAUSE_MS, 0
        )

        raw_emphasis = raw_seg.get("emphasis", [])
        if isinstance(raw_emphasis, list):
            emphasis = [str(item).strip() for item in raw_emphasis if item][: settings.MAX_EMPHASIS_PER_SEGMENT]
        else:
            emphasis = []

        hint = raw_seg.get("pronunciation_hint")
        pronunciation_hint = str(hint).strip() if hint else None

        return SpeechSegment(
            text=text,
            emotion=emotion,
            style=style,
            energy=energy,
            speed=speed,
            pitch=pitch,
            emphasis=emphasis,
            pause_before_ms=pause_before,
            pause_after_ms=pause_after,
            pronunciation_hint=pronunciation_hint,
        )

    @classmethod
    def verify_text_preservation(
        cls,
        original_text: str,
        speech_text: str,
        expected_lang: SupportedLanguage,
    ) -> None:
        """Checks that expressive mode has not altered numbers, translated text, or omitted major parts."""
        if not speech_text or not speech_text.strip():
            raise TextPreservationError("Generated speech_text is empty.")

        # 1. Script & Translation Check
        orig_tamil, orig_latin, _ = language_service.analyze_script(original_text)
        speech_tamil, speech_latin, _ = language_service.analyze_script(speech_text)

        if expected_lang == SupportedLanguage.TAMIL and orig_tamil > 0:
            if speech_tamil == 0 and speech_latin > 0:
                raise TextPreservationError(
                    "Translation detected: Tamil original text was converted to English/Latin script."
                )

        if expected_lang == SupportedLanguage.ENGLISH and orig_latin > 0:
            if speech_latin == 0 and speech_tamil > 0:
                raise TextPreservationError(
                    "Translation detected: English original text was converted to Tamil script."
                )

        # 2. Number preservation check
        orig_digits = re.findall(r"\d+", original_text)
        speech_digits = re.findall(r"\d+", speech_text)
        for digit in orig_digits:
            if digit not in speech_text:
                raise TextPreservationError(
                    f"Number preservation failure: original digit '{digit}' missing from speech text."
                )

        # 3. Basic length ratio sanity check
        len_ratio = len(speech_text) / max(1, len(original_text))
        if len_ratio < 0.4:
            raise TextPreservationError(
                f"Severe text truncation detected (length ratio: {len_ratio:.2f})."
            )
        if len_ratio > 2.5 and len(original_text) > 20:
            raise TextPreservationError(
                f"Excessive text hallucination detected (length ratio: {len_ratio:.2f})."
            )


validation_service = ValidationService()
