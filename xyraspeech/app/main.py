"""Main FastAPI Production Application Gateway for XyraSpeech."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from xyrabrain.app.api.brain import router as brain_router
from xyrabrain.app.schemas.errors import ErrorDetail, ErrorResponse
from xyrabrain.app.services.ollama_client import ollama_client
from xyraspeech.app.api.cloning import router as cloning_router
from xyraspeech.app.api.conversation import router as conversation_router
from xyraspeech.app.api.elevenlabs_compat import router as elevenlabs_router
from xyraspeech.app.api.health import router as health_router
from xyraspeech.app.api.realtime import router as realtime_router
from xyraspeech.app.api.stt import router as stt_router
from xyraspeech.app.api.translate import router as translate_router
from xyraspeech.app.api.tts import router as tts_router
from xyraspeech.app.api.voices import router as voices_router
from xyraspeech.app.core.config import settings
from xyraspeech.app.core.logging import RequestLoggingMiddleware, logger
from xyraspeech.app.engines.stt.whisper_engine import whisper_engine
from xyraspeech.app.engines.tts.registry import voice_registry


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup & shutdown lifecycle."""
    logger.info(f"============================================================")
    logger.info(f"Starting {settings.APP_NAME} Production Gateway v{settings.APP_VERSION}")
    logger.info(f"Ollama Target: {settings.OLLAMA_BASE_URL} (model: {settings.OLLAMA_MODEL})")
    logger.info(f"STT Engine: faster-whisper (model: {settings.WHISPER_MODEL_SIZE})")
    logger.info(f"Available Voices: {[v.id for v in voice_registry.list_voices()]}")
    logger.info(f"============================================================")
    yield
    logger.info("Shutting down XyraSpeech, releasing resources...")
    await ollama_client.close()


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=f"{settings.APP_NAME} Production Gateway",
        version=settings.APP_VERSION,
        description="Local-First Real-Time Multilingual AI Speech Platform (Tamil & English)",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Timing Tracing Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Exception Handlers
    @app.exception_handler(StarletteHTTPException)
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            code = exc.detail.get("code", f"HTTP_{exc.status_code}")
            msg = exc.detail.get("message", "An error occurred.")
            details = exc.detail.get("details")
        else:
            code = f"HTTP_{exc.status_code}"
            msg = str(exc.detail)
            details = None

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=code, message=msg, details=details)
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="VALIDATION_ERROR",
                    message="Request schema validation failed.",
                    details={"errors": exc.errors()},
                )
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, (HTTPException, StarletteHTTPException)):
            return await custom_http_exception_handler(request, exc)

        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        logger.exception(f"Unhandled server error [Request-ID: {req_id}]: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="An internal server error occurred.",
                    details={"request_id": req_id},
                )
            ).model_dump(),
        )

    # Include all API Routers
    app.include_router(health_router)
    app.include_router(stt_router)
    app.include_router(tts_router)
    app.include_router(cloning_router)
    app.include_router(elevenlabs_router)
    app.include_router(translate_router)
    app.include_router(brain_router)
    app.include_router(conversation_router)
    app.include_router(voices_router)
    app.include_router(realtime_router)

    # Mount Frontend Static Assets if built
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist_dir.exists():
        app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

        @app.get("/")
        async def serve_frontend_root():
            return FileResponse(dist_dir / "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("xyraspeech.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
