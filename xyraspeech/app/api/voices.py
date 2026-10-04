"""Voice Library API Endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, status

from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.schemas.voices import VoiceItem, VoiceListResponse

router = APIRouter(prefix="/api/v1", tags=["Voice Library"])


@router.get("/voices", response_model=VoiceListResponse)
async def list_voices(language: Optional[str] = None) -> VoiceListResponse:
    """Lists all available genuine local voices."""
    voices = voice_registry.list_voices(language=language)
    return VoiceListResponse(voices=voices)


@router.get("/voices/{voice_id}", response_model=VoiceItem)
async def get_voice(voice_id: str) -> VoiceItem:
    """Retrieves metadata and capabilities for a specific voice."""
    voice = voice_registry.get_voice(voice_id)
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "VOICE_NOT_FOUND", "message": f"Voice '{voice_id}' not found."},
        )
    return voice
