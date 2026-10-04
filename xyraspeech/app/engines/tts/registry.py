"""Voice Registry: Discoverable real voices for Tamil and English."""

from typing import Dict, List, Optional
from xyraspeech.app.core.config import settings
from xyraspeech.app.models.enums import TTSCapability
from xyraspeech.app.schemas.voices import VoiceItem


class VoiceRegistry:
    """Registry of genuine available voices: 1 Tamil voice and 1 English voice."""

    def __init__(self):
        self._voices: Dict[str, VoiceItem] = {
            "ta_pallavi": VoiceItem(
                id="ta_pallavi",
                name="Xyra Tamil",
                language="ta",
                gender="Female",
                engine="neural_expressive",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                    TTSCapability.SUPPORTS_EMOTION.value,
                    TTSCapability.SUPPORTS_STYLE.value,
                ],
                is_default=True,
                description="Ultra-natural, human-expressive Tamil neural voice.",
            ),
            "en_neerja": VoiceItem(
                id="en_neerja",
                name="Xyra English",
                language="en",
                gender="Female",
                engine="neural_expressive",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                    TTSCapability.SUPPORTS_EMOTION.value,
                    TTSCapability.SUPPORTS_STYLE.value,
                ],
                is_default=True,
                description="Warm, melodic English expressive neural voice.",
            ),
        }

    def list_voices(self, language: Optional[str] = None) -> List[VoiceItem]:
        """Lists all registered static and cloned voices."""
        from xyraspeech.app.engines.tts.voice_cloner import voice_cloner_engine
        all_voices = list(self._voices.values()) + voice_cloner_engine.list_cloned_voices()
        if language:
            return [v for v in all_voices if v.language == language or (language == "ta-en")]
        return all_voices

    def get_voice(self, voice_id: str) -> Optional[VoiceItem]:
        """Fetches voice item by ID."""
        if voice_id in self._voices:
            return self._voices[voice_id]
        from xyraspeech.app.engines.tts.voice_cloner import voice_cloner_engine
        for v in voice_cloner_engine.list_cloned_voices():
            if v.id == voice_id:
                return v
        return None

    def get_default_voice(self, language: str) -> VoiceItem:
        """Returns the default voice for a given language."""
        if language in ["ta", "ta-en"]:
            return self._voices["ta_pallavi"]
        return self._voices["en_neerja"]


voice_registry = VoiceRegistry()


