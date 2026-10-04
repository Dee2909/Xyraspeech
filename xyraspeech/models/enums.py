"""Controlled Enums and Vocabularies for XyraSpeech TTS Engine."""

from enum import Enum


class SupportedLanguage(str, Enum):
    """Explicitly and strictly supported languages in XyraSpeech.
    Do NOT add other languages.
    """
    TAMIL = "ta"
    ENGLISH = "en"


class Emotion(str, Enum):
    """Controlled emotion vocabulary compatible with XyraBrain."""
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
    """Controlled speaking styles vocabulary compatible with XyraBrain."""
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


class AudioFormat(str, Enum):
    """Audio formats supported for output."""
    WAV = "wav"
    MP3 = "mp3"


class Gender(str, Enum):
    """Voice gender classifications."""
    FEMALE = "female"
    MALE = "male"
    NEUTRAL = "neutral"


class AdapterType(str, Enum):
    """TTS adapter types."""
    TAMIL = "tamil"
    ENGLISH = "english"
    GENERIC_LOCAL = "generic_local"
    EDGE_TTS = "edge_tts"
