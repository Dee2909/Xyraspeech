"""Schemas for Realtime WebSocket Events."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from xyraspeech.app.models.enums import WebSocketEventType


class WSInboundEvent(BaseModel):
    """Client-to-Server WebSocket Event."""
    event: WebSocketEventType
    session_id: Optional[str] = None
    audio_base64: Optional[str] = None
    text: Optional[str] = None
    language: Optional[str] = None
    voice_id: Optional[str] = None


class WSOutboundEvent(BaseModel):
    """Server-to-Client WebSocket Event."""
    event: WebSocketEventType
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
