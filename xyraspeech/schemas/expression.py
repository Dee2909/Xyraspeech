"""Expression and Segment Input Schemas for XyraSpeech."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SegmentInput(BaseModel):
    """Individual segment specification from XyraBrain or caller."""
    text: str = Field(..., description="Segment text content")
    speed: Optional[float] = Field(default=None, ge=0.5, le=2.0, description="Segment-specific speed factor")
    pitch: Optional[float] = Field(default=None, ge=0.5, le=1.5, description="Segment-specific pitch factor")
    energy: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Segment-specific energy factor")
    pause_after_ms: int = Field(default=0, ge=0, le=5000, description="Silence pause after segment in milliseconds")
    emotion: Optional[str] = Field(default=None, description="Segment emotion")
    style: Optional[str] = Field(default=None, description="Segment speaking style")
    emphasis: Optional[List[str]] = Field(default=None, description="Words/phrases to emphasize")


class ExpressionInput(BaseModel):
    """Expression controls accepted from XyraBrain."""
    emotion: Optional[str] = Field(default="neutral", description="Overall emotion")
    style: Optional[str] = Field(default="conversational", description="Overall speaking style")
    energy: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Energy / loudness factor")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech rate / speed factor")
    pitch: Optional[float] = Field(default=1.0, ge=0.5, le=1.5, description="Voice pitch factor")
    pause: Optional[int] = Field(default=0, ge=0, le=5000, description="Global pause in milliseconds")
    emphasis: Optional[List[str]] = Field(default=None, description="Words or tokens to emphasize")
    segments: Optional[List[SegmentInput]] = Field(default=None, description="Ordered speech segments for multi-segment generation")
