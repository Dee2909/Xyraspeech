"""Health check endpoints for application and Ollama connectivity."""

from typing import Any, Dict
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from xyrabrain.app.core.config import settings
from xyrabrain.app.services.ollama_client import ollama_client

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint reporting application readiness."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "configured_model": settings.OLLAMA_MODEL,
    }


@router.get("/health/ollama")
async def ollama_health_check():
    """Detailed health check validating connection to the local Ollama instance."""
    result = await ollama_client.check_health()
    if not result.get("reachable"):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "reachable": False,
                "error": result.get("error"),
                "configured_model": result.get("configured_model"),
                "model_available": False,
                "installed_models": [],
                "help": "Ensure Ollama is running (`ollama serve`) and model is pulled.",
            },
        )

    http_status = status.HTTP_200_OK if result.get("model_available") else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=http_status,
        content={
            "status": "healthy" if result.get("model_available") else "model_not_found",
            "reachable": True,
            "configured_model": result.get("configured_model"),
            "model_available": result.get("model_available"),
            "installed_models": result.get("installed_models", []),
            "help": None if result.get("model_available") else f"Pull model via: 'ollama pull {result.get('configured_model')}'",
        },
    )
