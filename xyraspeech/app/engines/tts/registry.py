"""Voice Registry: Discoverable real voices for Tamil and English."""

from typing import Dict, List, Optional
from xyraspeech.app.core.config import settings
from xyraspeech.app.models.enums import TTSCapability
from xyraspeech.app.schemas.voices import VoiceItem


class VoiceRegistry:
    """Registry of genuine available local voices."""

    def __init__(self):
        self._voices: Dict[str, VoiceItem] = {
            "ta_vani": VoiceItem(
                id="ta_vani",
                name="Xyra Tamil (Vani)",
                language="ta",
                gender="Female",
                engine="mac_native",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                ],
                is_default=True,
                description="Natural Indian Tamil voice with clear phonetic articulation.",
            ),
            "en_rishi": VoiceItem(
                id="en_rishi",
                name="Xyra Indian English (Rishi)",
                language="en",
                gender="Male",
                engine="mac_native",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                ],
                is_default=True,
                description="Indian-accented English voice tuned for natural conversation.",
            ),
            "en_tara": VoiceItem(
                id="en_tara",
                name="Xyra Indian English (Tara)",
                language="en",
                gender="Female",
                engine="mac_native",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                ],
                is_default=False,
                description="Warm, melodic Indian English female voice for natural conversations.",
            ),
            "en_samantha": VoiceItem(
                id="en_samantha",
                name="Xyra English (Samantha)",
                language="en",
                gender="Female",
                engine="mac_native",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                ],
                is_default=False,
                description="Standard US English voice with warm, friendly tone.",
            ),
            "en_daniel": VoiceItem(
                id="en_daniel",
                name="Xyra British English (Daniel)",
                language="en",
                gender="Male",
                engine="mac_native",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_SPEED.value,
                    TTSCapability.SUPPORTS_PITCH.value,
                    TTSCapability.SUPPORTS_ENERGY.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                ],
                is_default=False,
                description="British English voice tuned for professional narration.",
            ),
        }

    def list_voices(self, language: Optional[str] = None) -> List[VoiceItem]:
        """Lists all registered voices or filters by language."""
        if language:
            return [v for v in self._voices.values() if v.language == language or (language == "ta-en")]
        return list(self._voices.values())

    def get_voice(self, voice_id: str) -> Optional[VoiceItem]:
        """Fetches voice item by ID."""
        return self._voices.get(voice_id)

    def get_default_voice(self, language: str) -> VoiceItem:
        """Returns the default voice for a given language."""
        if language in ["ta", "ta-en"]:
            return self._voices["ta_vani"]
        return self._voices["en_rishi"]


voice_registry = VoiceRegistry()
