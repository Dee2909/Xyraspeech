"""Configuration settings for XyraBrain."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings loaded from environment or .env file."""

    APP_NAME: str = "XyraBrain"
    APP_VERSION: str = "0.1.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # Ollama Local Service Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:latest"
    OLLAMA_TIMEOUT: int = 90

    # Operational Limits & Safety
    MAX_TEXT_LENGTH: int = 12000
    MAX_SEGMENTS: int = 50
    MAX_RETRIES: int = 2

    # Speech Control Clamping Bounds
    MIN_ENERGY: float = 0.0
    MAX_ENERGY: float = 1.0
    MIN_SPEED: float = 0.5
    MAX_SPEED: float = 1.5
    MIN_PITCH: float = 0.8
    MAX_PITCH: float = 1.2
    MIN_PAUSE_MS: int = 0
    MAX_PAUSE_MS: int = 3000
    MAX_EMPHASIS_PER_SEGMENT: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
