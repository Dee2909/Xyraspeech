"""Voice Library API Endpoints with Bark Voice Cloning Support."""

import os
import re
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.engines.tts.voice_cloner import voice_cloner_engine
from xyraspeech.app.models.enums import TTSCapability
from xyraspeech.app.schemas.voices import VoiceItem, VoiceListResponse, VoiceCloneResponse
from xyraspeech.app.services.voice_cloner import voice_cloner_service

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


@router.post("/voices/clone", response_model=VoiceCloneResponse)
async def clone_voice(
    file: UploadFile = File(...),
    voice_name: str = Form(...),
    language: str = Form(default="ta"),
    gender: str = Form(default="Neutral"),
    description: Optional[str] = Form(default=None),
) -> VoiceCloneResponse:
    """
    Clones a voice from an uploaded reference audio clip (5-15s WAV/MP3).
    Extracts Bark discrete acoustic and semantic prompt tensors and registers cloned voice.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_FILE", "message": "An audio sample file must be uploaded."},
        )

    audio_bytes = await file.read()
    if len(audio_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_AUDIO", "message": "Uploaded audio file is empty or corrupted."},
        )

    # Sanitize voice ID
    slug_name = re.sub(r"[^a-zA-Z0-9_]", "_", voice_name.lower().strip())
    voice_id = f"cloned_{slug_name}"

    try:
        # Extract Bark 3-part prompt numpy dictionary
        prompt_dict = voice_cloner_service.extract_voice_prompt(
            audio_bytes=audio_bytes,
            voice_id=voice_id,
            sample_rate=24000,
        )

        # Save .npz preset in storage/voices/
        npz_path = voice_cloner_service.save_voice_preset(voice_id, prompt_dict)

        # Create VoiceItem and register dynamically
        voice_item = VoiceItem(
            id=voice_id,
            name=voice_name.strip(),
            language=language,
            gender=gender,
            engine="bark_cloned",
            sample_rate=24000,
            capabilities=[
                TTSCapability.SUPPORTS_SPEED.value,
                TTSCapability.SUPPORTS_EMOTION.value,
                TTSCapability.SUPPORTS_PAUSE.value,
                TTSCapability.SUPPORTS_STYLE.value,
            ],
            is_default=False,
            description=description or f"Custom cloned Bark voice profile from sample '{file.filename}'.",
        )

        storage_dir = os.path.join(os.getcwd(), "storage", "voices")
        os.makedirs(storage_dir, exist_ok=True)
        metadata_json_path = os.path.join(storage_dir, f"{voice_id}.json")

        voice_registry.register_custom_voice(voice_item, metadata_json_path=metadata_json_path)

        return VoiceCloneResponse(
            status="SUCCESS",
            voice=voice_item,
            npz_path=npz_path,
            message=f"Voice '{voice_name}' successfully cloned and registered into Voice Library.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "VOICE_CLONE_ERROR", "message": str(exc)},
        )


@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Deletes a custom cloned voice."""
    if not voice_id.startswith("clone_") and not voice_id.startswith("cloned_"):
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
