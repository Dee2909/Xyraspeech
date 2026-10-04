"""Schemas for Text-to-Speech (TTS)."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Request payload to synthesize speech from text."""
    text: str = Field(..., min_length=1, max_length=12000, description="Text to synthesize")
    language: Optional[str] = Field(default=None, description="Language code: ta, en, or ta-en")
    voice_id: Optional[str] = Field(default=None, description="Specific voice ID (e.g. ta_vani, en_rishi)")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=1.5, description="Speech rate factor")
    pitch: Optional[float] = Field(default=1.0, ge=0.8, le=1.2, description="Pitch factor")
    energy: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Energy level")
    emotion: Optional[str] = Field(default=None, description="Target emotion if supported")
    style: Optional[str] = Field(default=None, description="Target style if supported")
    format: str = Field(default="wav", description="Audio container format: wav")


class TTSMetadata(BaseModel):
    """Metadata describing generated audio."""
    voice_id: str
    language: str
    duration_seconds: float
    sample_rate: int
    engine: str
