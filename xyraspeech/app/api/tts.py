"""Real Text-to-Speech (TTS) API Endpoint."""

from fastapi import APIRouter, HTTPException, Response, status

from xyrabrain.app.services.language_service import language_service
from xyraspeech.app.engines.tts.mac_tts import mac_tts_engine
from xyraspeech.app.engines.tts.registry import voice_registry
from xyraspeech.app.schemas.tts import TTSRequest

router = APIRouter(prefix="/api/v1", tags=["Text-to-Speech"])


@router.post("/tts")
async def synthesize_speech(request: TTSRequest) -> Response:
    """Synthesizes text into real, playable 24kHz WAV audio stream."""
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
