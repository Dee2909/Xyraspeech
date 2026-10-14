"""Schemas for Voice Library and Bark Voice Cloning."""

from typing import List, Optional
from pydantic import BaseModel, Field


class VoiceItem(BaseModel):
    """A real voice entry in the Voice Registry."""
    id: str
    name: str
    language: str
    gender: str
    engine: str
    sample_rate: int
    capabilities: List[str]
    is_default: bool = False
    description: Optional[str] = None


class VoiceListResponse(BaseModel):
    """List of all available real voices."""
    voices: List[VoiceItem]


class VoiceCloneRequest(BaseModel):
    """Request payload metadata to clone a voice from audio."""
    voice_name: str = Field(..., min_length=2, max_length=50, description="Name for the cloned voice")
    language: str = Field(default="ta", description="Target primary language: ta or en")
    gender: str = Field(default="Neutral", description="Gender tag")
    description: Optional[str] = Field(default=None, description="Optional description of voice prompt")


class VoiceCloneResponse(BaseModel):
    """Response returned upon successfully extracting and registering cloned voice."""
    status: str
    voice: VoiceItem
    npz_path: str
    message: str
