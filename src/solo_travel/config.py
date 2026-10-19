"""Configuration settings for Solo Travel Intelligence Platform."""
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class LLMProviderType(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Central typed settings loaded from environment or .env file."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # LLM Settings
    DEFAULT_PROVIDER: LLMProviderType = LLMProviderType.OLLAMA
    DEFAULT_MODEL: str = "llama3.1:8b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_TEMPERATURE: float = Field(default=0.3, ge=0.0, le=1.0)
    LLM_TIMEOUT: int = Field(default=120, description="Timeout in seconds for LLM calls")

    # API Keys (Optional, never mandatory for local Ollama mode)
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    RAILRADAR_API_KEY: Optional[str] = None

    # Search & Tool Limits
    SEARCH_MAX_RESULTS: int = 3
    AGENT_MAX_ITER: int = 3
    LOG_LEVEL: str = "INFO"


# Lazy loaded singleton
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retrieve global cached settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
