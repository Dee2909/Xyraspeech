"""ElevenLabs Drop-in Compatibility Layer for XyraSpeech."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response, status
from pydantic import BaseModel, Field

from xyrabrain.app.services.language_service import language_service
from xyraspeech.app.core.config import settings
from xyraspeech.app.core.security import verify_api_key
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry

router = APIRouter(tags=["ElevenLabs Compatibility API"])


class VoiceSettings(BaseModel):
    stability: Optional[float] = Field(default=0.75, ge=0.0, le=1.0)
    similarity_boost: Optional[float] = Field(default=0.75, ge=0.0, le=1.0)
    style: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    use_speaker_boost: Optional[bool] = Field(default=True)


class ElevenLabsTTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to synthesize")
    model_id: Optional[str] = Field(default="eleven_multilingual_v2")
    voice_settings: Optional[VoiceSettings] = None
    pronunciation_dictionary_locators: Optional[List[Any]] = None


@router.get("/v1/voices")
async def list_elevenlabs_voices(
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """ElevenLabs compatible GET /v1/voices endpoint."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)

    voices_list = []
    for v in voice_registry.list_voices():
        voices_list.append({
            "voice_id": v.id,
            "name": v.name,
            "category": "neural",
            "description": v.description,
            "labels": {
                "language": v.language,
                "gender": v.gender.lower(),
                "accent": "Indian" if "ta" in v.language or "rishi" in v.id or "neerja" in v.id or "prabhat" in v.id or "tara" in v.id else "Western",
            },
            "preview_url": f"http://{settings.HOST}:{settings.PORT}/api/v1/tts?voice_id={v.id}&text=Sample",
            "settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
            },
        })

    return {"voices": voices_list}


@router.post("/v1/text-to-speech/{voice_id}")
@router.post("/v1/text-to-speech/{voice_id}/stream")
async def elevenlabs_text_to_speech(
    voice_id: str = Path(..., description="The voice ID (e.g. ta_pallavi, ta_valluvar, en_neerja, en_prabhat)"),
    request: ElevenLabsTTSRequest = ...,
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Response:
    """ElevenLabs compatible POST /v1/text-to-speech/{voice_id} endpoint."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)

    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_TEXT", "message": "Text parameter cannot be empty."},
        )

    # 1. Determine Language
    lang_enum = language_service.validate_or_detect(text, None)
    lang_code = lang_enum.value

    # 2. Lookup Voice
    voice = voice_registry.get_voice(voice_id)
    if not voice:
        # Fallback to default for detected language
        voice = voice_registry.get_default_voice(lang_code)

    # 3. Map settings
    speed = 1.0
    emotion = "warm"
    if request.voice_settings:
        if request.voice_settings.style and request.voice_settings.style > 0.4:
            emotion = "excited"

    try:
        wav_bytes = await mac_tts_engine.synthesize(
            text=text,
            language=lang_code,
            voice_id=voice.id,
            speed=speed,
            emotion=emotion,
        )

        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'inline; filename="{voice.id}.wav"',
                "X-Voice-Id": voice.id,
                "X-Engine": "xyraspeech_neural",
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TTS_SYNTHESIS_ERROR", "message": str(exc)},
        )


@router.get("/v1/user/subscription")
async def get_user_subscription(
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """ElevenLabs compatible subscription endpoint."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)
    return {
        "tier": "xyraspeech_unlimited_local",
        "character_count": 0,
        "character_limit": 100_000_000,
        "can_extend_character_limit": True,
        "allowed_to_extend_character_limit": True,
        "status": "active",
    }
