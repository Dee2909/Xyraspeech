"""Real Speech-to-Text (STT) API Endpoint."""

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from xyraspeech.app.core.config import settings
from xyraspeech.app.engines.stt.whisper_engine import whisper_engine
from xyraspeech.app.schemas.stt import STTResponse

router = APIRouter(prefix="/api/v1", tags=["Speech-to-Text"])


@router.post("/stt", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, WebM, Ogg)"),
    language: Optional[str] = Form(default=None, description="Optional forced language: 'ta' or 'en'"),
) -> STTResponse:
    """Transcribes an uploaded speech recording using real local faster-whisper."""
    if language and language not in ["ta", "en", "ta-en", "auto"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "UNSUPPORTED_LANGUAGE", "message": f"Language '{language}' is not supported."},
        )

    try:
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "EMPTY_AUDIO", "message": "Uploaded audio payload is empty."},
            )

        if len(audio_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={"code": "FILE_TOO_LARGE", "message": "Audio file exceeds 25MB limit."},
            )

        target_lang = None if (not language or language == "auto") else language
        return await whisper_engine.transcribe(audio_bytes, language=target_lang)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "STT_INFERENCE_ERROR", "message": str(exc)},
        )
