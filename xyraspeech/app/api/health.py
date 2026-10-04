"""Health and Model Readiness API."""

from typing import Any, Dict
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from xyrabrain.app.services.ollama_client import ollama_client
from xyraspeech.app.core.config import settings
from xyraspeech.app.engines.stt.whisper_engine import whisper_engine
from xyraspeech.app.engines.tts.registry import voice_registry

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    """Application status check."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/models")
async def health_models():
    """Comprehensive readiness for STT, TTS, Translation, and Ollama models."""
    ollama_status = await ollama_client.check_health()
    stt_available = whisper_engine.is_available()
    voices = voice_registry.list_voices()

    all_ready = ollama_status.get("reachable", False) and stt_available and len(voices) > 0

    return JSONResponse(
        status_code=status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if all_ready else "degraded",
            "engines": {
                "stt": {
                    "engine": "faster-whisper",
                    "model": settings.WHISPER_MODEL_SIZE,
                    "available": stt_available,
                    "languages": ["ta", "en", "ta-en"],
                },
                "tts": {
                    "engine": "mac_native",
                    "available": True,
                    "voice_count": len(voices),
                    "languages": ["ta", "en"],
                },
                "brain_llm": {
                    "engine": "ollama",
                    "target_url": settings.OLLAMA_BASE_URL,
                    "model": settings.OLLAMA_MODEL,
                    "reachable": ollama_status.get("reachable", False),
                    "model_available": ollama_status.get("model_available", False),
                    "installed_models": ollama_status.get("installed_models", []),
                },
                "translation": {
                    "engine": "ollama_neural_translator",
                    "available": ollama_status.get("reachable", False),
                    "pairs": ["ta->en", "en->ta"],
                },
            },
        },
    )


@router.get("/health/ollama")
async def health_ollama():
    """Ollama-specific health check."""
    result = await ollama_client.check_health()
    http_status = status.HTTP_200_OK if result.get("reachable") else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=http_status, content=result)
