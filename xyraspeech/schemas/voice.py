"""Voice Schemas for XyraSpeech."""

from typing import List, Optional
from pydantic import BaseModel, Field


class VoiceInfo(BaseModel):
    """Voice metadata representation according to XyraSpeech voice registry."""
    voice_id: str = Field(..., description="Unique voice identifier")
    name: str = Field(..., description="Display name of the voice")
    language: str = Field(..., description="Language code ('ta' or 'en')")
    gender: str = Field(..., description="Gender ('female', 'male', 'neutral')")
    style: str = Field(default="conversational", description="Default speaking style")
    model_id: str = Field(..., description="Underlying model identifier")
    enabled: bool = Field(default=True, description="Whether this voice is active")
    adapter_type: Optional[str] = Field(default=None, description="Adapter type handling this voice")
    description: Optional[str] = Field(default=None, description="Voice description")


class VoiceListResponse(BaseModel):
    """Response envelope for listing voices."""
    voices: List[VoiceInfo]
    total: int
