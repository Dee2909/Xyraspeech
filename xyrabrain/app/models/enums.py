"""Controlled Enums and Vocabularies for XyraBrain."""

from enum import Enum


class SupportedLanguage(str, Enum):
    """Explicitly supported languages in XyraBrain."""
    TAMIL = "ta"
    ENGLISH = "en"
    MIXED = "ta-en"


class ProcessingMode(str, Enum):
    """Processing modes for XyraBrain."""
    RAW = "raw"
    ENHANCED = "enhanced"
    EXPRESSIVE = "expressive"


class Emotion(str, Enum):
    """Controlled emotion vocabulary.
    Do NOT invent arbitrary emotion names. Defaults to NEUTRAL if uncertain.
    """
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    EMPATHETIC = "empathetic"
    CALM = "calm"
    WARM = "warm"
    SERIOUS = "serious"
    CONFIDENT = "confident"
    PLAYFUL = "playful"
    APOLOGETIC = "apologetic"
    ENCOURAGING = "encouraging"
    DISAPPOINTED = "disappointed"
    FEARFUL = "fearful"


class SpeakingStyle(str, Enum):
    """Controlled speaking styles vocabulary."""
    NEUTRAL = "neutral"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    WARM = "warm"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    SERIOUS = "serious"
    STORYTELLING = "storytelling"
    INSTRUCTIONAL = "instructional"
    EMPATHETIC = "empathetic"
    ENERGETIC = "energetic"


class TTSCapability(str, Enum):
    """Features potentially supported by downstream TTS engines."""
    SUPPORTS_SPEED = "supports_speed"
    SUPPORTS_PITCH = "supports_pitch"
    SUPPORTS_ENERGY = "supports_energy"
    SUPPORTS_EMOTION = "supports_emotion"
    SUPPORTS_PAUSE = "supports_pause"
    SUPPORTS_SSML = "supports_ssml"
    SUPPORTS_STYLE = "supports_style"
