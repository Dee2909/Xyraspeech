"""Base TTS Engine Interface."""

from abc import ABC, abstractmethod
from typing import Optional, Set
from xyraspeech.app.models.enums import TTSCapability


class BaseTTSEngine(ABC):
    """Abstract Base Class for TTS engines."""

    @abstractmethod
    def get_capabilities(self) -> Set[TTSCapability]:
        """Returns capabilities genuinely supported by this engine."""
        pass

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        language: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = 1.0,
        pitch: Optional[float] = 1.0,
        energy: Optional[float] = 0.5,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
    ) -> bytes:
        """Synthesizes input text into real, playable WAV audio bytes."""
        pass
