"""XyraSpeech Language Router Package."""

from xyraspeech.router.enums import (
    AudioFormat,
    Gender,
    ScriptType,
    SupportedLanguage,
    TaskType,
)
from xyraspeech.router.errors import (
    InvalidCombinationError,
    LanguageDetectionError,
    LanguageMismatchError,
    LanguageRoutingError,
    ModelLanguageMismatchError,
    UnsupportedLanguageError,
    UnsupportedScriptError,
    UnsupportedTranslationPairError,
    VoiceLanguageMismatchError,
)
from xyraspeech.router.detector import LanguageDetector, DetectionResult
from xyraspeech.router.voice_registry import VoiceInfo, VoiceRegistry, voice_registry
from xyraspeech.router.model_registry import ModelInfo, ModelRegistry, model_registry
from xyraspeech.router.schemas import (
    LanguageDetectionResult,
    STTRoutingDecision,
    TTSRoutingDecision,
    TextPrepRoutingDecision,
    TranslationRoutingDecision,
    ValidationResult,
)
from xyraspeech.router.language_router import LanguageRouter, language_router

__all__ = [
    "SupportedLanguage",
    "TaskType",
    "Gender",
    "ScriptType",
    "AudioFormat",
    "LanguageRoutingError",
    "UnsupportedLanguageError",
    "LanguageDetectionError",
    "UnsupportedScriptError",
    "LanguageMismatchError",
    "VoiceLanguageMismatchError",
    "ModelLanguageMismatchError",
    "UnsupportedTranslationPairError",
    "InvalidCombinationError",
    "LanguageDetector",
    "DetectionResult",
    "VoiceInfo",
    "VoiceRegistry",
    "voice_registry",
    "ModelInfo",
    "ModelRegistry",
    "model_registry",
    "LanguageDetectionResult",
    "TTSRoutingDecision",
    "STTRoutingDecision",
    "TranslationRoutingDecision",
    "TextPrepRoutingDecision",
    "ValidationResult",
    "LanguageRouter",
    "language_router",
]
