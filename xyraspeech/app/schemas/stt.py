"""Schemas for Speech-to-Text (STT)."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    """Timestamped segment of transcribed speech."""
    id: int = Field(..., description="Segment index")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(default=1.0, description="Confidence score 0.0 to 1.0")


class STTResponse(BaseModel):
    """Complete STT transcription output."""
    text: str = Field(..., description="Full transcribed text")
    language: str = Field(..., description="Detected or specified language code (ta, en, etc.)")
    duration_seconds: float = Field(..., description="Duration of processed audio in seconds")
    confidence: float = Field(default=1.0, description="Overall transcription confidence")
    segments: List[TranscriptionSegment] = Field(default_factory=list, description="Timestamped segments")
    model: str = Field(..., description="STT Model identifier")
