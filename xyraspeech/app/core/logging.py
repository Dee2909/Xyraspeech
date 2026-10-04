"""Structured Observability and Tracing for XyraSpeech."""

import logging
import sys
import time
import uuid
from typing import Any, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from xyraspeech.app.core.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("xyraspeech")


def log_event(
    event: str,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    stage: Optional[str] = None,
    language: Optional[str] = None,
    model: Optional[str] = None,
    latency_ms: Optional[float] = None,
    status: str = "SUCCESS",
    error: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Logs structured telemetry event."""
    log_dict: Dict[str, Any] = {
        "event": event,
        "status": status,
    }
    if session_id:
        log_dict["session_id"] = session_id
    if request_id:
        log_dict["request_id"] = request_id
    if stage:
        log_dict["stage"] = stage
    if language:
        log_dict["language"] = language
    if model:
        log_dict["model"] = model
    if latency_ms is not None:
        log_dict["latency_ms"] = round(latency_ms, 2)
    if error:
        log_dict["error"] = error
    if extra:
        log_dict.update(extra)

    if status == "ERROR":
        logger.error(f"[VOICE] {log_dict}")
    else:
        logger.info(f"[VOICE] {log_dict}")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware capturing request timing and attaching X-Request-ID."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

            if request.url.path.startswith("/api") or request.url.path.startswith("/health"):
                log_event(
                    event="http_request",
                    request_id=request_id,
                    stage="http_gateway",
                    latency_ms=elapsed_ms,
                    status="SUCCESS" if response.status_code < 400 else "ERROR",
                    extra={"path": request.url.path, "status_code": response.status_code, "method": request.method},
                )
            return response
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            log_event(
                event="http_request_exception",
                request_id=request_id,
                stage="http_gateway",
                latency_ms=elapsed_ms,
                status="ERROR",
                error=str(exc),
                extra={"path": request.url.path, "method": request.method},
            )
            raise exc
