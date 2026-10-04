"""Base STT Engine Interface."""

from abc import ABC, abstractmethod
from typing import Optional
from xyraspeech.app.schemas.stt import STTResponse


class BaseSTTEngine(ABC):
    """Abstract Base Class for STT engines."""

    @abstractmethod
    async def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
    ) -> STTResponse:
        """Transcribes raw audio bytes into text and timestamped segments."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the STT model weights and runtime are available."""
        pass
