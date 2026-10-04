"""Expression Adapter and Engine-Neutral TTS Dispatch System."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from xyrabrain.app.models.enums import TTSCapability
from xyrabrain.app.schemas.brain import (
    AdapterDispatchResult,
    SpeechDirection,
    SpeechSegment,
    TTSInstruction,
)


class ExpressionAdapter:
    """Transforms XyraBrain SpeechDirection into engine-neutral instructions filtered by TTS capabilities."""

    @classmethod
    def to_neutral_instructions(
        cls,
        direction: SpeechDirection,
        voice_id: Optional[str] = None,
        capabilities: Optional[Set[TTSCapability]] = None,
    ) -> List[TTSInstruction]:
        """Maps each SpeechSegment into a TTSInstruction, stripping unsupported capabilities."""
        caps = capabilities if capabilities is not None else set(TTSCapability)
        instructions: List[TTSInstruction] = []

        for seg in direction.segments:
            # Build raw debug metadata
            raw_meta = {
                "original_emotion": seg.emotion.value,
                "original_style": seg.style.value,
                "original_energy": seg.energy,
                "original_speed": seg.speed,
                "original_pitch": seg.pitch,
                "pause_before_ms": seg.pause_before_ms,
                "pause_after_ms": seg.pause_after_ms,
            }

            # Filter fields according to capabilities
            speed = seg.speed if TTSCapability.SUPPORTS_SPEED in caps else None
            pitch = seg.pitch if TTSCapability.SUPPORTS_PITCH in caps else None
            energy = seg.energy if TTSCapability.SUPPORTS_ENERGY in caps else None
            emotion = seg.emotion.value if TTSCapability.SUPPORTS_EMOTION in caps else None
            style = seg.style.value if TTSCapability.SUPPORTS_STYLE in caps else None
            pause_after = seg.pause_after_ms if TTSCapability.SUPPORTS_PAUSE in caps else None

            # SSML generation if supported
            ssml: Optional[str] = None
            if TTSCapability.SUPPORTS_SSML in caps:
                prosody_attrs = []
                if speed:
                    prosody_attrs.append(f'rate="{int(speed * 100)}%"')
                if pitch:
                    pitch_percent = int((pitch - 1.0) * 100)
                    prosody_attrs.append(f'pitch="{"+" if pitch_percent >= 0 else ""}{pitch_percent}%"')

                prosody_str = " ".join(prosody_attrs)
                break_tag = f'<break time="{pause_after}ms"/>' if pause_after else ""
                ssml = f"<speak><prosody {prosody_str}>{seg.text}</prosody>{break_tag}</speak>"

            instructions.append(
                TTSInstruction(
                    text=seg.text,
                    language=direction.language.value,
                    voice_id=voice_id,
                    speed=speed,
                    pitch=pitch,
                    energy=energy,
                    emotion=emotion,
                    style=style,
                    pause_after_ms=pause_after,
                    emphasis=seg.emphasis,
                    ssml=ssml,
                    raw_metadata=raw_meta,
                )
            )

        return instructions

    @classmethod
    def dispatch_for_engine(
        cls,
        adapter_name: str,
        direction: SpeechDirection,
        supported_capabilities: Set[TTSCapability],
        voice_id: Optional[str] = None,
    ) -> AdapterDispatchResult:
        """Dispatches and documents applied vs dropped capabilities."""
        all_caps = set(TTSCapability)
        applied = [c.value for c in all_caps if c in supported_capabilities]
        dropped = [c.value for c in all_caps if c not in supported_capabilities]

        instructions = cls.to_neutral_instructions(
            direction=direction,
            voice_id=voice_id,
            capabilities=supported_capabilities,
        )

        return AdapterDispatchResult(
            adapter_name=adapter_name,
            applied_capabilities=applied,
            dropped_capabilities=dropped,
            instructions=instructions,
        )


class BaseTTSAdapter(ABC):
    """Abstract Base Class for downstream TTS Adapters."""

    def __init__(self, name: str, capabilities: Set[TTSCapability]):
        self.name = name
        self.capabilities = capabilities

    def adapt(self, direction: SpeechDirection, voice_id: Optional[str] = None) -> AdapterDispatchResult:
        """Adapts SpeechDirection to this specific adapter's capabilities."""
        return ExpressionAdapter.dispatch_for_engine(
            adapter_name=self.name,
            direction=direction,
            supported_capabilities=self.capabilities,
            voice_id=voice_id,
        )

    @abstractmethod
    async def synthesize(
        self,
        instruction: TTSInstruction,
    ) -> bytes:
        """Synthesize audio bytes for the given instruction."""
        pass


class IndicTTSAdapter(BaseTTSAdapter):
    """Sample adapter for AI4Bharat Indic-TTS (supports speed, pitch, pause)."""

    def __init__(self):
        super().__init__(
            name="IndicTTSAdapter",
            capabilities={
                TTSCapability.SUPPORTS_SPEED,
                TTSCapability.SUPPORTS_PITCH,
                TTSCapability.SUPPORTS_PAUSE,
            },
        )

    async def synthesize(self, instruction: TTSInstruction) -> bytes:
        # Downstream engine bridge
        return b"INDIC_TTS_AUDIO_BYTES_PLACEHOLDER"


class OpenVoiceAdapter(BaseTTSAdapter):
    """Sample adapter for OpenVoice (supports speed, energy, emotion, style)."""

    def __init__(self):
        super().__init__(
            name="OpenVoiceAdapter",
            capabilities={
                TTSCapability.SUPPORTS_SPEED,
                TTSCapability.SUPPORTS_ENERGY,
                TTSCapability.SUPPORTS_EMOTION,
                TTSCapability.SUPPORTS_STYLE,
            },
        )

    async def synthesize(self, instruction: TTSInstruction) -> bytes:
        return b"OPENVOICE_AUDIO_BYTES_PLACEHOLDER"


class MockTTSAdapter(BaseTTSAdapter):
    """Adapter with 100% capability support for unit and system testing."""

    def __init__(self):
        super().__init__(
            name="MockTTSAdapter",
            capabilities=set(TTSCapability),
        )

    async def synthesize(self, instruction: TTSInstruction) -> bytes:
        return b"MOCK_SYNTHESIZED_AUDIO_DATA"
