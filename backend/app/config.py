from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    stt_google_project_id: str | None = None
    stt_google_credentials_json: str | None = None
    stt_language_code: str = "en-US"

    chunk_size_words: int = 1200
    cache_ttl_seconds: int = 60 * 60 * 24

    allow_origins: list[str] = ["*"]

    @property
    def mock_mode(self) -> bool:
        return not bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
