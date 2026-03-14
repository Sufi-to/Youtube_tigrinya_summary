from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    use_mock_summary: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:27b"

    whisper_model: str = "base"
    whisper_language: str = "en"

    stt_google_project_id: str | None = None
    stt_google_credentials_json: str | None = None
    stt_language_code: str = "en-US"

    chunk_size_words: int = 1200
    cache_ttl_seconds: int = 60 * 60 * 24

    allow_origins: list[str] = ["*"]

    @property
    def mock_mode(self) -> bool:
        return self.use_mock_summary


@lru_cache
def get_settings() -> Settings:
    return Settings()
