"""Configuration settings for XyraSpeech TTS Engine."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class TTSSettings(BaseSettings):
    """Application Settings for XyraSpeech TTS Engine."""

    APP_NAME: str = "XyraSpeech TTS Engine"
    APP_VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8002
    DEBUG: bool = False

    # Supported Languages (Strictly Tamil and English only)
    SUPPORTED_LANGUAGES: List[str] = ["ta", "en"]

    # Text Length Limits
    MAX_TEXT_LENGTH: int = 15000
    MAX_SEGMENTS: int = 50

    # Speech Control Bounds
    MIN_SPEED: float = 0.5
    MAX_SPEED: float = 2.0
    MIN_PITCH: float = 0.5
    MAX_PITCH: float = 1.5
    MIN_ENERGY: float = 0.0
    MAX_ENERGY: float = 1.0
    MIN_PAUSE_MS: int = 0
    MAX_PAUSE_MS: int = 5000

    # Default Voices
    DEFAULT_TAMIL_VOICE: str = "ta-IN-PallaviNeural"
    DEFAULT_ENGLISH_VOICE: str = "en-US-JennyNeural"

    # Audio Processing Defaults
    DEFAULT_SAMPLE_RATE: int = 24000
    NORMALIZE_AUDIO: bool = True
    TARGET_PEAK_AMPLITUDE: float = 0.95

    # Timeout for synthesis in seconds
    SYNTHESIS_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = TTSSettings()
