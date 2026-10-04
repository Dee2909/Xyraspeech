"""Unified Production Configuration for XyraSpeech."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings loaded from environment or .env."""

    APP_NAME: str = "XyraSpeech"
    APP_VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # Ollama Local Service
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:latest"
    OLLAMA_TIMEOUT: int = 90

    # STT Whisper Local Engine
    WHISPER_MODEL_SIZE: str = "tiny"  # 'tiny', 'base', 'small'
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    # Default Voices
    DEFAULT_VOICE_TA: str = "ta_vani"
    DEFAULT_VOICE_EN: str = "en_rishi"

    # Audio Engine & VAD
    AUDIO_SAMPLE_RATE: int = 24000
    STT_SAMPLE_RATE: int = 16000
    VAD_ENERGY_THRESHOLD: float = 0.015
    VAD_SILENCE_DURATION_MS: int = 600
    MAX_AUDIO_DURATION_SECONDS: int = 300
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB

    # Bounded Conversation Context
    MAX_CONTEXT_MESSAGES: int = 20
    MAX_CONTEXT_TOKENS: int = 6000

    # Speech Control Limits
    MIN_ENERGY: float = 0.0
    MAX_ENERGY: float = 1.0
    MIN_SPEED: float = 0.5
    MAX_SPEED: float = 1.5
    MIN_PITCH: float = 0.8
    MAX_PITCH: float = 1.2
    MIN_PAUSE_MS: int = 0
    MAX_PAUSE_MS: int = 3000
    MAX_SEGMENTS: int = 50
    MAX_RETRIES: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
