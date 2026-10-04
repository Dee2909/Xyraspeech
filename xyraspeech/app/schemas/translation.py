"""Schemas for Translation."""

from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Translation request payload."""
    text: str = Field(..., min_length=1, max_length=12000, description="Source text to translate")
    source_language: str = Field(..., description="Source language: ta or en")
    target_language: str = Field(..., description="Target language: ta or en")


class TranslationResponse(BaseModel):
    """Translation response payload."""
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    model: str
