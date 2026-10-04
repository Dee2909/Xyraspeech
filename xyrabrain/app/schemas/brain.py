"""Pydantic Schemas for XyraBrain Speech Intelligence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from xyrabrain.app.models.enums import (
    Emotion,
    ProcessingMode,
    SpeakingStyle,
    SupportedLanguage,
)


class SpeechSegment(BaseModel):
    """An individual spoken segment with fine-grained performance metadata."""

    text: str = Field(..., description="The segment text to speak")
    emotion: Emotion = Field(
        default=Emotion.NEUTRAL,
        description="Emotion for this specific segment",
    )
    style: SpeakingStyle = Field(
        default=SpeakingStyle.NEUTRAL,
        description="Speaking delivery style for this segment",
    )
    energy: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Energy level: 0.0 (very low) to 1.0 (maximum)",
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="Speech rate factor: 0.5 (slow) to 1.5 (fast)",
    )
    pitch: float = Field(
        default=1.0,
        ge=0.8,
        le=1.2,
        description="Pitch modifier: 0.8 (low) to 1.2 (high)",
    )
    emphasis: List[str] = Field(
        default_factory=list,
        description="Words or short phrases requiring emphasis (max 3)",
    )
    pause_before_ms: int = Field(
        default=0,
        ge=0,
        le=3000,
        description="Pre-segment pause in milliseconds (0 to 3000)",
    )
    pause_after_ms: int = Field(
        default=0,
        ge=0,
        le=3000,
        description="Post-segment pause in milliseconds (0 to 3000)",
    )
    pronunciation_hint: Optional[str] = Field(
        default=None,
        description="Optional phonetic or IPA pronunciation guidance",
    )

    @field_validator("emphasis", mode="after")
    @classmethod
    def limit_emphasis_items(cls, val: List[str]) -> List[str]:
        return val[:3] if val else []


class DirectionMetadata(BaseModel):
    """Metadata detailing the inference run."""

    model: str = Field(..., description="Ollama model or internal engine used")
    processing_mode: ProcessingMode = Field(..., description="Processing mode utilized")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 generation timestamp",
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    schema_version: str = Field(default="1.0", description="Schema version")
    retry_count: int = Field(default=0, description="Number of Ollama validation retries")


class SpeechDirection(BaseModel):
    """The master speech-direction instruction object produced by XyraBrain."""

    language: SupportedLanguage = Field(..., description="Language code: ta, en, or ta-en")
    speech_text: str = Field(..., description="Full spoken text")
    overall_style: SpeakingStyle = Field(
        default=SpeakingStyle.NEUTRAL,
        description="Global speaking delivery style",
    )
    overall_emotion: Emotion = Field(
        default=Emotion.NEUTRAL,
        description="Global emotional tone",
    )
    segments: List[SpeechSegment] = Field(
        default_factory=list,
        description="Logical speech segments with delivery parameters",
    )
    metadata: DirectionMetadata = Field(..., description="Execution and engine metadata")


# --- Request Schemas ---

class BaseTextRequest(BaseModel):
    """Base request payload with validation."""
    text: str = Field(..., min_length=1, max_length=12000, description="Input text to process")
    language: Optional[SupportedLanguage] = Field(
        default=None,
        description="Optional explicit language code: ta, en, or ta-en. Auto-detected if omitted.",
    )


class AnalyzeRequest(BaseTextRequest):
    """Generic analysis request allowing custom processing mode."""
    mode: ProcessingMode = Field(
        default=ProcessingMode.EXPRESSIVE,
        description="Processing mode: raw, enhanced, or expressive",
    )


class EnhanceRequest(BaseTextRequest):
    """Request for text enhancement (punctuation, capitalization, flow)."""
    pass


class ExpressRequest(BaseTextRequest):
    """Request for expressive speech direction generation."""
    pass


# --- Capabilities Response ---

class CapabilitiesResponse(BaseModel):
    """Information on supported languages, emotions, styles, and hardware limits."""
    service_name: str
    version: str
    supported_languages: List[str]
    supported_emotions: List[str]
    supported_styles: List[str]
    processing_modes: List[str]
    limits: Dict[str, Any]


# --- Expression Adapter & TTS Dispatch Schemas ---

class TTSInstruction(BaseModel):
    """Engine-neutral speech instruction ready for a downstream TTS adapter."""
    text: str
    language: str
    voice_id: Optional[str] = None
    speed: Optional[float] = None
    pitch: Optional[float] = None
    energy: Optional[float] = None
    emotion: Optional[str] = None
    style: Optional[str] = None
    pause_after_ms: Optional[int] = None
    emphasis: List[str] = Field(default_factory=list)
    ssml: Optional[str] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class AdapterDispatchResult(BaseModel):
    """Result of mapping SpeechDirection through a specific TTS adapter's capabilities."""
    adapter_name: str
    applied_capabilities: List[str]
    dropped_capabilities: List[str]
    instructions: List[TTSInstruction]
