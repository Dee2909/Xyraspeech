"""Schemas for Voice Library."""

from typing import List, Optional
from pydantic import BaseModel


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
