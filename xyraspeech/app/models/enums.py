"""Controlled Vocabularies, Enums, and Constants for XyraSpeech."""

from enum import Enum


class SupportedLanguage(str, Enum):
    """Explicitly supported languages in XyraSpeech."""
    TAMIL = "ta"
    ENGLISH = "en"
    MIXED = "ta-en"


class UserIntent(str, Enum):
    """Classified conversational user intent."""
    GREETING = "GREETING"
    QUESTION = "QUESTION"
    COMMAND = "COMMAND"
    REQUEST = "REQUEST"
    EXPLANATION = "EXPLANATION"
    EMOTIONAL_MESSAGE = "EMOTIONAL_MESSAGE"
    CASUAL_CONVERSATION = "CASUAL_CONVERSATION"
    TECHNICAL_QUESTION = "TECHNICAL_QUESTION"
    TRANSLATION_REQUEST = "TRANSLATION_REQUEST"
    VOICE_COMMAND = "VOICE_COMMAND"


class ProcessingMode(str, Enum):
    """Processing modes for XyraBrain."""
    RAW = "raw"
    ENHANCED = "enhanced"
    EXPRESSIVE = "expressive"


class Emotion(str, Enum):
    """Controlled emotion vocabulary."""
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
    """Controlled speaking styles."""
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
    """Capabilities supported by downstream TTS engines."""
    SUPPORTS_SPEED = "supports_speed"
    SUPPORTS_PITCH = "supports_pitch"
    SUPPORTS_ENERGY = "supports_energy"
    SUPPORTS_EMOTION = "supports_emotion"
    SUPPORTS_PAUSE = "supports_pause"
    SUPPORTS_SSML = "supports_ssml"
    SUPPORTS_STYLE = "supports_style"


class WebSocketEventType(str, Enum):
    """Realtime WebSocket event types."""
    SESSION_START = "session_start"
    AUDIO_CHUNK = "audio_chunk"
    SPEECH_START = "speech_start"
    SPEECH_END = "speech_end"
    TRANSCRIPT_PARTIAL = "transcript_partial"
    TRANSCRIPT_FINAL = "transcript_final"
    BRAIN_STARTED = "brain_started"
    BRAIN_RESPONSE = "brain_response"
    SPEECH_STARTED = "speech_started"
    AUDIO_OUT_CHUNK = "audio_out_chunk"
    SPEECH_FINISHED = "speech_finished"
    INTERRUPT = "interrupt"
    ERROR = "error"
    SESSION_END = "session_end"
