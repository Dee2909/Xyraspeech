"""Standardized Error Schemas for XyraBrain."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error body."""
    code: str = Field(..., description="Machine-readable uppercase error code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional diagnostic details")


class ErrorResponse(BaseModel):
    """Standard top-level error response envelope."""
    error: ErrorDetail
