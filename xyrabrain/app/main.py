"""Main FastAPI application entry point for XyraBrain."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from xyrabrain.app.api.brain import router as brain_router
from xyrabrain.app.api.health import router as health_router
from xyrabrain.app.core.config import settings
from xyrabrain.app.core.logging import RequestLoggingMiddleware, logger
from xyrabrain.app.schemas.errors import ErrorDetail, ErrorResponse
from xyrabrain.app.services.ollama_client import ollama_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup & shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Configured Ollama Target: {settings.OLLAMA_BASE_URL} (model: {settings.OLLAMA_MODEL})")
    yield
    logger.info("Shutting down XyraBrain, closing HTTP clients...")
    await ollama_client.close()


def create_app() -> FastAPI:
    """Factory function for FastAPI application."""
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        description="Ollama-Powered Speech Intelligence Engine for XyraSpeech",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS Configuration
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

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="BAD_REQUEST",
                    message=str(exc),
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

    # Include API Routers
    app.include_router(health_router)
    app.include_router(brain_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("xyrabrain.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
