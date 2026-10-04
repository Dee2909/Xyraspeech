"""Schemas for Interactive Conversation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from xyrabrain.app.schemas.brain import SpeechDirection


class ConversationMessageRequest(BaseModel):
    """Message request to conversational pipeline."""
    text: str = Field(..., min_length=1, max_length=12000, description="User spoken or typed input")
    conversation_id: Optional[str] = Field(default=None, description="Existing session ID to preserve context")
    language: Optional[str] = Field(default=None, description="Optional forced language: ta, en, ta-en")
    voice_id: Optional[str] = Field(default=None, description="Optional voice ID")


class LatencyBreakdown(BaseModel):
    """Measured latencies in milliseconds."""
    stt_ms: Optional[float] = None
    brain_ms: float
    tts_first_audio_ms: float
    total_ms: float


class ConversationMessageResponse(BaseModel):
    """Complete response from conversational pipeline."""
    conversation_id: str
    user_input: str
    response_text: str
    language: str
    intent: str
    speech_direction: SpeechDirection
    audio_base64: Optional[str] = None
    latency_metrics: LatencyBreakdown
