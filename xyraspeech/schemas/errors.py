"""Standardized Error Schemas and Error Codes for XyraSpeech."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorCode:
    """Predefined error codes for XyraSpeech."""
    EMPTY_TEXT = "EMPTY_TEXT"
    UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
    UNSUPPORTED_VOICE = "UNSUPPORTED_VOICE"
    LANGUAGE_VOICE_MISMATCH = "LANGUAGE_VOICE_MISMATCH"
    INVALID_VOICE_ID = "INVALID_VOICE_ID"
    INVALID_SPEED = "INVALID_SPEED"
    INVALID_PITCH = "INVALID_PITCH"
    INVALID_ENERGY = "INVALID_ENERGY"
    INVALID_EMOTION = "INVALID_EMOTION"
    INVALID_STYLE = "INVALID_STYLE"
    TEXT_TOO_LARGE = "TEXT_TOO_LARGE"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    SYNTHESIS_ERROR = "SYNTHESIS_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"


class ErrorDetail(BaseModel):
    """Structured error body."""
    code: str = Field(..., description="Machine-readable uppercase error code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional diagnostic details")


class ErrorResponse(BaseModel):
    """Standard top-level error response envelope."""
    error: ErrorDetail
