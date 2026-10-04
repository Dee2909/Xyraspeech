"""Voice Library API Endpoints."""

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.engines.tts.voice_cloner import voice_cloner_engine
from xyraspeech.app.schemas.voices import VoiceItem, VoiceListResponse

router = APIRouter(prefix="/api/v1", tags=["Voice Library"])


@router.get("/voices", response_model=VoiceListResponse)
async def list_voices(language: Optional[str] = None) -> VoiceListResponse:
    """Lists all available genuine local voices including cloned voices."""
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


@router.post("/voices/clone", response_model=VoiceItem)
async def clone_voice(
    file: UploadFile = File(...),
    name: str = Form(...),
    language: str = Form(default="ta"),
    gender: Optional[str] = Form(default="Auto"),
    description: Optional[str] = Form(default=None),
) -> VoiceItem:
    """Clones a custom voice from a short reference audio clip."""
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_NAME", "message": "Speaker name cannot be empty."},
        )

    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_AUDIO", "message": "Uploaded audio sample is empty or too short."},
        )

    try:
        voice_item, _ = await voice_cloner_engine.create_cloned_voice(
            name=name.strip(),
            audio_bytes=audio_bytes,
            language=language,
            gender=gender,
            description=description,
        )
        return voice_item
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "VOICE_CLONE_ERROR", "message": str(exc)},
        )


@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Deletes a custom cloned voice."""
    if not voice_id.startswith("clone_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_DELETE_BUILTIN", "message": "Built-in voices cannot be deleted."},
        )

    deleted = voice_cloner_engine.delete_cloned_voice(voice_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "VOICE_NOT_FOUND", "message": f"Cloned voice '{voice_id}' not found."},
        )

    return {"status": "success", "message": f"Cloned voice '{voice_id}' deleted successfully."}

