"""Voice Registry: Discoverable real voices for Tamil and English."""

from typing import Dict, List, Optional
from xyraspeech.app.core.config import settings
from xyraspeech.app.models.enums import TTSCapability
from xyraspeech.app.schemas.voices import VoiceItem


class VoiceRegistry:
    """Registry of genuine available local & neural voices."""

    def __init__(self):
        self._voices: Dict[str, VoiceItem] = {
            "ta_pallavi": VoiceItem(
                id="ta_pallavi",
                name="Xyra Tamil (Pallavi Neural)",
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
                description="Ultra-natural, human-expressive Indian Tamil female neural voice.",
            ),
            "ta_valluvar": VoiceItem(
                id="ta_valluvar",
                name="Xyra Tamil (Valluvar Neural)",
                language="ta",
                gender="Male",
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
                is_default=False,
                description="Deep, authentic Indian Tamil male neural voice with natural cadence.",
            ),
            "en_neerja": VoiceItem(
                id="en_neerja",
                name="Xyra Indian English (Neerja Neural)",
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
                description="Warm, melodic Indian English expressive female neural voice.",
            ),
            "en_prabhat": VoiceItem(
                id="en_prabhat",
                name="Xyra Indian English (Prabhat Neural)",
                language="en",
                gender="Male",
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
                is_default=False,
                description="Clear, confident Indian English male neural voice.",
            ),
            "en_samantha": VoiceItem(
                id="en_samantha",
                name="Xyra English (Samantha US)",
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
                name="Xyra British English (Daniel UK)",
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
            "ta_vani": VoiceItem(
                id="ta_vani",
                name="Xyra Tamil (Vani - Local)",
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
                is_default=False,
                description="Local offline Indian Tamil female voice.",
            ),
            "en_rishi": VoiceItem(
                id="en_rishi",
                name="Xyra Indian English (Rishi - Local)",
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
                description="Local offline Indian English male voice.",
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
            return self._voices["ta_pallavi"]
        return self._voices["en_neerja"]


voice_registry = VoiceRegistry()

