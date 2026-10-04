"""Real Text-to-Speech (TTS) API Endpoint."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse

from xyrabrain.app.services.language_service import language_service
from xyraspeech.app.core.config import settings
from xyraspeech.app.core.security import verify_api_key
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.schemas.tts import TTSRequest

router = APIRouter(prefix="/api/v1", tags=["Text-to-Speech"])


@router.get("/tts")
async def get_synthesize_speech(
    text: Optional[str] = Query(default=None, description="Text to synthesize"),
    language: Optional[str] = Query(default=None, description="Language code: ta or en"),
    voice_id: Optional[str] = Query(default=None, description="Voice ID"),
    speed: float = Query(default=1.0, ge=0.5, le=1.5),
    pitch: float = Query(default=1.0, ge=0.8, le=1.2),
    energy: float = Query(default=0.5, ge=0.0, le=1.0),
    emotion: Optional[str] = Query(default="warm"),
    style: Optional[str] = Query(default="conversational"),
) -> Response:
    """GET endpoint: allows immediate playback by pasting URL in browser address bar."""
    if not text or not text.strip():
        # Provide sample default text if accessed directly in browser
        text = "வணக்கம்! நீங்கள் இப்போது கேட்பது எக்ஸ்ரா ஸ்பீச் குரல் தொழில்நுட்பம்."
        language = language or "ta"

    # 1. Determine Language
    lang_enum = language_service.validate_or_detect(text, language)
    lang_code = lang_enum.value

    # 2. Select Voice
    if voice_id:
        voice = voice_registry.get_voice(voice_id)
        if not voice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_VOICE", "message": f"Voice '{voice_id}' not found."},
            )
    else:
        voice = voice_registry.get_default_voice(lang_code)

    try:
        wav_bytes = await mac_tts_engine.synthesize(
            text=text,
            language=lang_code,
            voice_id=voice.id,
            speed=speed,
            pitch=pitch,
            energy=energy,
            emotion=emotion,
            style=style,
        )

        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'inline; filename="xyraspeech.wav"',
                "X-Voice-Id": voice.id,
                "X-Language": lang_code,
                "X-Sample-Rate": str(voice.sample_rate),
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TTS_SYNTHESIS_ERROR", "message": str(exc)},
        )


@router.post("/tts")
async def synthesize_speech(
    request: TTSRequest,
) -> Response:
    """POST endpoint: Synthesizes text into real, playable 24kHz WAV audio stream."""
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_TEXT", "message": "Text payload cannot be empty."},
        )

    # 1. Determine Language
    lang_enum = language_service.validate_or_detect(request.text, request.language)
    lang_code = lang_enum.value

    # 2. Select Voice
    voice = None
    if request.voice_id:
        voice = voice_registry.get_voice(request.voice_id)
        if not voice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_VOICE", "message": f"Voice '{request.voice_id}' not found."},
            )
    else:
        voice = voice_registry.get_default_voice(lang_code)

    try:
        # 3. Real Synthesis
        wav_bytes = await mac_tts_engine.synthesize(
            text=request.text,
            language=lang_code,
            voice_id=voice.id,
            speed=request.speed or 1.0,
            pitch=request.pitch or 1.0,
            energy=request.energy or 0.5,
            emotion=request.emotion,
            style=request.style,
        )

        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'inline; filename="xyraspeech.wav"',
                "X-Voice-Id": voice.id,
                "X-Language": lang_code,
                "X-Sample-Rate": str(voice.sample_rate),
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TTS_SYNTHESIS_ERROR", "message": str(exc)},
        )

