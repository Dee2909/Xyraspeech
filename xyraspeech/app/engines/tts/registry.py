"""Voice Registry: Discoverable real voices for Tamil and English including Bark Voice Clones."""

import os
import json
from typing import Dict, List, Optional
from xyraspeech.app.core.config import settings
from xyraspeech.app.models.enums import TTSCapability
from xyraspeech.app.schemas.voices import VoiceItem


class VoiceRegistry:
    """Registry of genuine available voices & custom cloned Bark voice profiles."""

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
            "bark_expressive_ta": VoiceItem(
                id="bark_expressive_ta",
                name="Bark Tamil Expressive",
                language="ta",
                gender="Neutral",
                engine="bark_cloned",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_EMOTION.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                    TTSCapability.SUPPORTS_STYLE.value,
                ],
                is_default=False,
                description="Bark neural voice synthesizer for Tamil with acoustic emotion & laughter cues.",
            ),
            "bark_expressive_en": VoiceItem(
                id="bark_expressive_en",
                name="Bark English Expressive",
                language="en",
                gender="Neutral",
                engine="bark_cloned",
                sample_rate=24000,
                capabilities=[
                    TTSCapability.SUPPORTS_EMOTION.value,
                    TTSCapability.SUPPORTS_PAUSE.value,
                    TTSCapability.SUPPORTS_STYLE.value,
                ],
                is_default=False,
                description="Bark neural voice synthesizer for English with dynamic non-speech sound effects.",
            ),
        }
        self.reload_cloned_voices()

    def reload_cloned_voices(self):
        """Discovers custom cloned voice files in storage/voices/ metadata JSON files."""
        storage_dir = os.path.join(os.getcwd(), "storage", "voices")
        if not os.path.exists(storage_dir):
            return

        for filename in os.listdir(storage_dir):
            if filename.endswith(".json"):
                json_path = os.path.join(storage_dir, filename)
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        voice_item = VoiceItem(**data)
                        self._voices[voice_item.id] = voice_item
                except Exception:
                    pass

    def register_custom_voice(self, voice_item: VoiceItem, metadata_json_path: Optional[str] = None):
        """Registers a newly cloned Bark voice into registry and persists metadata."""
        self._voices[voice_item.id] = voice_item
        if metadata_json_path:
            with open(metadata_json_path, "w", encoding="utf-8") as f:
                json.dump(voice_item.model_dump(), f, indent=2)

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
