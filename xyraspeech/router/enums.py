"""Controlled Enums and Vocabularies for XyraSpeech Language Router."""

from enum import Enum
from typing import Set


class SupportedLanguage(str, Enum):
    """Explicitly supported languages in XyraSpeech.
    
    ONLY:
    - 'ta' (Tamil)
    - 'en' (English)
    - 'ta-en' (Tamil-English code-mixed)
    
    No other language is supported. Never silently fallback.
    """
    TAMIL = "ta"
    ENGLISH = "en"
    MIXED = "ta-en"

    @classmethod
    def all_codes(cls) -> Set[str]:
        """Returns the set of all valid language code strings."""
        return {item.value for item in cls}

    @classmethod
    def is_supported(cls, code: str | None) -> bool:
        """Checks whether a given language string is supported."""
        if not code or not isinstance(code, str):
            return False
        normalized = code.strip().lower().replace("_", "-")
        # Handle variations like "ta-in", "tamil", "en-us", "en-in", "english"
        aliases = {
            "ta": "ta",
            "tam": "ta",
            "tamil": "ta",
            "ta-in": "ta",
            "en": "en",
            "eng": "en",
            "english": "en",
            "en-in": "en",
            "en-us": "en",
            "en-gb": "en",
            "ta-en": "ta-en",
            "en-ta": "ta-en",
            "tanglish": "ta-en",
            "mixed": "ta-en",
            "code-mixed": "ta-en",
        }
        return aliases.get(normalized) in cls.all_codes()

    @classmethod
    def normalize(cls, code: str | None) -> "SupportedLanguage":
        """Normalizes and returns SupportedLanguage enum.
        
        Raises ValueError if unsupported.
        """
        if not code or not isinstance(code, str):
            raise ValueError(f"Language code cannot be empty. Supported languages: {list(cls.all_codes())}")
        
        normalized = code.strip().lower().replace("_", "-")
        aliases = {
            "ta": cls.TAMIL,
            "tam": cls.TAMIL,
            "tamil": cls.TAMIL,
            "ta-in": cls.TAMIL,
            "en": cls.ENGLISH,
            "eng": cls.ENGLISH,
            "english": cls.ENGLISH,
            "en-in": cls.ENGLISH,
            "en-us": cls.ENGLISH,
            "en-gb": cls.ENGLISH,
            "ta-en": cls.MIXED,
            "en-ta": cls.MIXED,
            "tanglish": cls.MIXED,
            "mixed": cls.MIXED,
            "code-mixed": cls.MIXED,
        }
        if normalized in aliases:
            return aliases[normalized]
        
        raise ValueError(
            f"Unsupported language '{code}'. XyraSpeech supports ONLY: "
            f"{', '.join(sorted(cls.all_codes()))}."
        )


class TaskType(str, Enum):
    """Speech and language processing tasks in XyraSpeech."""
    TTS = "tts"
    STT = "stt"
    TRANSLATION = "translation"
    TEXT_PREPARATION = "text_preparation"
    VOICE_CLONING = "voice_cloning"


class Gender(str, Enum):
    """Voice gender categories."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class ScriptType(str, Enum):
    """Identified script classification in text."""
    TAMIL = "tamil"
    LATIN = "latin"
    MIXED = "mixed"
    UNSUPPORTED = "unsupported"


class AudioFormat(str, Enum):
    """Supported audio container formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
