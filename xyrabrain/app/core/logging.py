"""Structured logging configuration for XyraBrain."""

import logging
import sys
import time
import uuid
from typing import Any, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from xyrabrain.app.core.config import settings

# Configure standard logger
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("xyrabrain")


def log_structured_event(
    event: str,
    request_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    mode: Optional[str] = None,
    language: Optional[str] = None,
    model: Optional[str] = None,
    processing_time_ms: Optional[float] = None,
    status: str = "SUCCESS",
    error_detail: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Log structured event without exposing sensitive user text."""
    log_data: Dict[str, Any] = {
        "event": event,
        "request_id": request_id or str(uuid.uuid4()),
        "status": status,
    }
    if endpoint:
        log_data["endpoint"] = endpoint
    if mode:
        log_data["mode"] = mode
    if language:
        log_data["language"] = language
    if model:
        log_data["model"] = model
    if processing_time_ms is not None:
        log_data["elapsed_ms"] = round(processing_time_ms, 2)
    if error_detail:
        log_data["error"] = error_detail
    if extra:
        log_data.update(extra)

    if status == "ERROR":
        logger.error(f"EVENT: {log_data}")
    else:
        logger.info(f"EVENT: {log_data}")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Request-ID and record elapsed request timing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

            # Only log API requests, avoid spamming static or internal paths
            if request.url.path.startswith("/api") or request.url.path.startswith("/health"):
                log_structured_event(
                    event="http_request_completed",
                    request_id=request_id,
                    endpoint=request.url.path,
                    processing_time_ms=elapsed_ms,
                    status="SUCCESS" if response.status_code < 400 else "ERROR",
                    extra={"http_status": response.status_code, "method": request.method},
                )
            return response
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            log_structured_event(
                event="http_request_exception",
                request_id=request_id,
                endpoint=request.url.path,
                processing_time_ms=elapsed_ms,
                status="ERROR",
                error_detail=str(exc),
                extra={"method": request.method},
            )
            raise exc
