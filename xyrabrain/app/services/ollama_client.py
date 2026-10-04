"""Async Ollama Client with connection pooling, timeouts, and health checks."""

import json
from typing import Any, Dict, List, Optional
import httpx

from xyrabrain.app.core.config import settings
from xyrabrain.app.core.logging import logger


class OllamaClientError(Exception):
    """Base exception for Ollama client failures."""
    pass


class OllamaConnectionError(OllamaClientError):
    """Raised when Ollama server cannot be reached."""
    pass


class OllamaTimeoutError(OllamaClientError):
    """Raised when Ollama inference exceeds configured timeout."""
    pass


class OllamaModelNotFoundError(OllamaClientError):
    """Raised when the configured model is not installed in Ollama."""
    pass


class OllamaClient:
    """Async client interacting with local Ollama daemon."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Returns or creates the shared HTTP async client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout, connect=5.0),
            )
        return self._client

    async def close(self) -> None:
        """Closes the underlying HTTP client session."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def check_health(self) -> Dict[str, Any]:
        """Checks if Ollama daemon is reachable and lists installed models."""
        client = await self.get_client()
        try:
            resp = await client.get("/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                is_configured_present = self.model in models or any(
                    m.startswith(self.model.split(":")[0]) for m in models
                )
                return {
                    "reachable": True,
                    "configured_model": self.model,
                    "model_available": is_configured_present,
                    "installed_models": models,
                }
            return {
                "reachable": False,
                "error": f"HTTP {resp.status_code}: {resp.text}",
                "configured_model": self.model,
                "model_available": False,
                "installed_models": [],
            }
        except httpx.ConnectError as exc:
            return {
                "reachable": False,
                "error": f"Cannot connect to Ollama at {self.base_url}: {str(exc)}",
                "configured_model": self.model,
                "model_available": False,
                "installed_models": [],
            }
        except Exception as exc:
            return {
                "reachable": False,
                "error": str(exc),
                "configured_model": self.model,
                "model_available": False,
                "installed_models": [],
            }

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model_override: Optional[str] = None,
        json_format: bool = True,
    ) -> Dict[str, Any]:
        """Sends chat completion request to Ollama, enforcing JSON output."""
        client = await self.get_client()
        target_model = model_override or self.model

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,  # Low temperature for stable structured output
            },
        }
        if json_format:
            payload["format"] = "json"

        try:
            resp = await client.post("/api/chat", json=payload)
        except httpx.ConnectError as exc:
            raise OllamaConnectionError(
                f"Failed to connect to Ollama server at {self.base_url}. Ensure Ollama is running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError(
                f"Ollama inference timed out after {self.timeout}s on model '{target_model}'."
            ) from exc
        except Exception as exc:
            raise OllamaClientError(f"Unexpected error communicating with Ollama: {str(exc)}") from exc

        if resp.status_code == 404:
            raise OllamaModelNotFoundError(
                f"Model '{target_model}' is not installed in Ollama. Pull it with: 'ollama pull {target_model}'"
            )

        if resp.status_code != 200:
            raise OllamaClientError(
                f"Ollama returned HTTP {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        message_content = data.get("message", {}).get("content", "")
        if not message_content:
            raise OllamaClientError("Empty response content from Ollama.")

        if not json_format:
            return {"response": message_content.strip()}

        try:
            return json.loads(message_content)
        except json.JSONDecodeError as exc:
            # Attempt simple cleanup in case of markdown fences
            cleaned = message_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            try:
                return json.loads(cleaned.strip())
            except json.JSONDecodeError:
                raise OllamaClientError(
                    f"Failed to parse Ollama output as JSON: {message_content}"
                ) from exc


ollama_client = OllamaClient()
