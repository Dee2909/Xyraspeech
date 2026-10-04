"""API Key Authentication & Security for XyraSpeech."""

from typing import Optional
from fastapi import Header, HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader

from xyraspeech.app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
    api_key: Optional[str] = Query(default=None, description="Optional API key as query parameter"),
    authorization: Optional[str] = Header(default=None, description="Optional Bearer token"),
) -> str:
    """Verifies that a valid API key was supplied via header or query parameter."""
    if not settings.API_KEY_ENABLED:
        return "authentication_disabled"

    # Extract key from X-API-Key header, query param, or Authorization Bearer
    provided_key = x_api_key or api_key
    if not provided_key and authorization and authorization.lower().startswith("bearer "):
        provided_key = authorization[7:].strip()

    valid_keys = set(settings.API_KEYS)
    if settings.DEFAULT_API_KEY:
        valid_keys.add(settings.DEFAULT_API_KEY)

    if not provided_key or provided_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": (
                    "Invalid or missing API key. Please provide a valid 'X-API-Key' header, "
                    f"query param '?api_key={settings.DEFAULT_API_KEY}', or 'Authorization: Bearer <key>'."
                ),
                "hint": f"Default API key: '{settings.DEFAULT_API_KEY}'",
            },
        )

    return provided_key
