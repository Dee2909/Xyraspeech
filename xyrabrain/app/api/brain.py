"""XyraBrain Intelligence API endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, status

from xyrabrain.app.core.config import settings
from xyrabrain.app.models.enums import (
    Emotion,
    ProcessingMode,
    SpeakingStyle,
    SupportedLanguage,
)
from xyrabrain.app.schemas.brain import (
    AnalyzeRequest,
    CapabilitiesResponse,
    EnhanceRequest,
    ExpressRequest,
    SpeechDirection,
)
from xyrabrain.app.services.brain_service import brain_service
from xyrabrain.app.services.ollama_client import (
    OllamaClientError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)
from xyrabrain.app.services.validation_service import TextPreservationError

router = APIRouter(prefix="/api/v1/brain", tags=["Speech Intelligence"])


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities() -> CapabilitiesResponse:
    """Returns supported languages, emotions, styles, and hardware limits."""
    return CapabilitiesResponse(
        service_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        supported_languages=[l.value for l in SupportedLanguage],
        supported_emotions=[e.value for e in Emotion],
        supported_styles=[s.value for s in SpeakingStyle],
        processing_modes=[m.value for m in ProcessingMode],
        limits={
            "max_text_length": settings.MAX_TEXT_LENGTH,
            "max_segments": settings.MAX_SEGMENTS,
            "energy_range": [settings.MIN_ENERGY, settings.MAX_ENERGY],
            "speed_range": [settings.MIN_SPEED, settings.MAX_SPEED],
            "pitch_range": [settings.MIN_PITCH, settings.MAX_PITCH],
            "pause_range_ms": [settings.MIN_PAUSE_MS, settings.MAX_PAUSE_MS],
        },
    )


@router.post("/analyze", response_model=SpeechDirection)
async def analyze_text(request: AnalyzeRequest, req: Request) -> SpeechDirection:
    """Generic text analysis accepting raw, enhanced, or expressive mode."""
    request_id = getattr(req.state, "request_id", None)
    try:
        return await brain_service.process(
            text=request.text,
            language=request.language,
            mode=request.mode,
            request_id=request_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_INPUT", "message": str(exc)},
        )
    except TextPreservationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "TEXT_PRESERVATION_ERROR", "message": str(exc)},
        )
    except OllamaConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "OLLAMA_UNAVAILABLE", "message": str(exc)},
        )
    except OllamaModelNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "MODEL_NOT_FOUND", "message": str(exc)},
        )
    except OllamaTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "INFERENCE_TIMEOUT", "message": str(exc)},
        )
    except OllamaClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "OLLAMA_ERROR", "message": str(exc)},
        )


@router.post("/enhance", response_model=SpeechDirection)
async def enhance_text(request: EnhanceRequest, req: Request) -> SpeechDirection:
    """Enhances text for spoken delivery (punctuation, flow, capitalization)."""
    request_id = getattr(req.state, "request_id", None)
    try:
        return await brain_service.process(
            text=request.text,
            language=request.language,
            mode=ProcessingMode.ENHANCED,
            request_id=request_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_INPUT", "message": str(exc)},
        )
    except (OllamaConnectionError, OllamaModelNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": str(exc)},
        )
    except OllamaTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "INFERENCE_TIMEOUT", "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(exc)},
        )


@router.post("/express", response_model=SpeechDirection)
async def express_text(request: ExpressRequest, req: Request) -> SpeechDirection:
    """Main XyraBrain capability: generates speech-performance instructions."""
    request_id = getattr(req.state, "request_id", None)
    try:
        return await brain_service.process(
            text=request.text,
            language=request.language,
            mode=ProcessingMode.EXPRESSIVE,
            request_id=request_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_INPUT", "message": str(exc)},
        )
    except TextPreservationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "TEXT_PRESERVATION_FAILED", "message": str(exc)},
        )
    except (OllamaConnectionError, OllamaModelNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": str(exc)},
        )
    except OllamaTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "INFERENCE_TIMEOUT", "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(exc)},
        )
