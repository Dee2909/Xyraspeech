"""Real Translation API Endpoint."""

from fastapi import APIRouter, HTTPException, status
from xyraspeech.app.engines.translation.translation_engine import translation_engine
from xyraspeech.app.schemas.translation import TranslationRequest, TranslationResponse

router = APIRouter(prefix="/api/v1", tags=["Translation"])


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest) -> TranslationResponse:
    """Translates text between Tamil and English."""
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_TEXT", "message": "Text payload cannot be empty."},
        )

    try:
        return await translation_engine.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_LANGUAGE_PAIR", "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TRANSLATION_ERROR", "message": str(exc)},
        )
