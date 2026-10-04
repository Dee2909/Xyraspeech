"""Language detection, script analysis, and validation service."""

import re
from typing import Tuple
from xyrabrain.app.models.enums import SupportedLanguage


class LanguageService:
    """Detects and validates supported languages (Tamil, English, Tamil-English mixed)."""

    TAMIL_CHAR_PATTERN = re.compile(r"[\u0B80-\u0BFF]")
    LATIN_CHAR_PATTERN = re.compile(r"[a-zA-Z]")
    DEVANAGARI_OR_OTHER_INDIC = re.compile(r"[\u0900-\u097F\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F]")

    @classmethod
    def analyze_script(cls, text: str) -> Tuple[int, int, int]:
        """Counts Tamil, Latin, and other script characters in input."""
        tamil_chars = len(cls.TAMIL_CHAR_PATTERN.findall(text))
        latin_chars = len(cls.LATIN_CHAR_PATTERN.findall(text))
        other_indic = len(cls.DEVANAGARI_OR_OTHER_INDIC.findall(text))
        return tamil_chars, latin_chars, other_indic

    @classmethod
    def detect_language(cls, text: str) -> SupportedLanguage:
        """Determines if the text is Tamil ('ta'), English ('en'), or Mixed ('ta-en').

        Raises ValueError if an explicitly unsupported non-English/Tamil script is detected predominantly.
        """
        tamil_count, latin_count, other_indic = cls.analyze_script(text)
        total_chars = tamil_count + latin_count + other_indic

        if total_chars == 0:
            # Default to English if only numbers/punctuation
            return SupportedLanguage.ENGLISH

        if other_indic > (tamil_count + latin_count) * 0.5 and other_indic > 5:
            raise ValueError("Unsupported script detected. Only Tamil and English are supported.")

        if tamil_count > 0 and latin_count > 0:
            # Check ratio for code-switching
            tamil_ratio = tamil_count / (tamil_count + latin_count)
            if 0.15 <= tamil_ratio <= 0.85:
                return SupportedLanguage.MIXED
            elif tamil_ratio > 0.85:
                return SupportedLanguage.TAMIL
            else:
                return SupportedLanguage.ENGLISH

        if tamil_count > 0:
            return SupportedLanguage.TAMIL

        return SupportedLanguage.ENGLISH

    @classmethod
    def validate_or_detect(cls, text: str, requested_lang: str | SupportedLanguage | None) -> SupportedLanguage:
        """Validates requested language against detected language and ensures it's supported."""
        if isinstance(requested_lang, str):
            try:
                lang_enum = SupportedLanguage(requested_lang.lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported language '{requested_lang}'. Only 'ta' (Tamil), 'en' (English), or 'ta-en' are supported."
                )
        elif requested_lang is not None:
            lang_enum = requested_lang
        else:
            lang_enum = cls.detect_language(text)

        # Sanity check if user requested Tamil but supplied Latin-only text or vice-versa
        detected = cls.detect_language(text)
        tamil_count, latin_count, _ = cls.analyze_script(text)

        if lang_enum == SupportedLanguage.TAMIL and tamil_count == 0 and latin_count > 10:
            # Text is entirely English but user asked for Tamil
            # We don't fail hard if it's transliterated/Tanglish, but we tag as MIXED or log warning
            return SupportedLanguage.MIXED

        return lang_enum


language_service = LanguageService()
