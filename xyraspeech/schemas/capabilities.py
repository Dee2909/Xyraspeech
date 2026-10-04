"""TTS Capabilities Schemas for XyraSpeech."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TTSCapabilities(BaseModel):
    """Granular capability flags describing what a TTS adapter/model genuinely supports.
    Do NOT pretend every TTS model supports every parameter.
    """
    supports_speed: bool = Field(default=True, description="Whether speed adjustment is supported natively")
    supports_pitch: bool = Field(default=False, description="Whether pitch adjustment is supported natively")
    supports_emotion: bool = Field(default=False, description="Whether emotion conditioning is supported natively")
    supports_pause: bool = Field(default=True, description="Whether pause duration between segments is supported")
    supports_style: bool = Field(default=False, description="Whether speaking style conditioning is supported natively")
    supports_energy: bool = Field(default=False, description="Whether energy/volume control is supported natively")
    supports_ssml: bool = Field(default=False, description="Whether raw SSML input is supported natively")
    supported_languages: List[str] = Field(default_factory=lambda: ["ta", "en"], description="List of supported languages ('ta', 'en')")
    sample_rates: List[int] = Field(default_factory=lambda: [24000], description="Supported output sample rates in Hz")


class CapabilitiesResponse(BaseModel):
    """Top-level capabilities response."""
    engine: str = Field(default="XyraSpeech TTS Engine", description="Engine name")
    version: str = Field(default="1.0.0", description="Engine version")
    supported_languages: List[str] = Field(default_factory=lambda: ["ta", "en"])
    adapters: Dict[str, TTSCapabilities] = Field(default_factory=dict, description="Capabilities per adapter")
    default_capabilities: TTSCapabilities
