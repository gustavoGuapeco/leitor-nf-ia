from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.ai_constants import (
    AI_PROVIDER_OPENAI,
    DEFAULT_AI_MODEL,
    DEFAULT_AI_TIMEOUT_SECONDS,
)

# Raiz do repositório (app/config/settings.py → parents[2] = leitor-nf-ia/)
# Ficheiros são lidos daqui, independentemente do cwd do Uvicorn.
# Ordem: ficheiros posteriores sobrescrevem anteriores (último ganha).
#  .env.example → valores de exemplo / dev local
#  .env          → segredos (preferido)
#  .env.local    → overrides locais (ex.: máquina específica)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(_PROJECT_ROOT / ".env.example"),
            str(_PROJECT_ROOT / ".env"),
            str(_PROJECT_ROOT / ".env.local"),
        ),
        env_file_encoding="utf-8",
        # Variável vazia no ambiente (ex.: OPENAI_API_KEY= no IDE) não sobrescreve o ficheiro .env
        env_ignore_empty=True,
        extra="ignore",
    )

    app_env: str = Field(default="development", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    ai_provider: str = Field(default=AI_PROVIDER_OPENAI, validation_alias="AI_PROVIDER")
    ai_model: str = Field(
        default=DEFAULT_AI_MODEL,
        validation_alias=AliasChoices("AI_MODEL", "OPENAI_MODEL"),
    )
    ai_timeout_seconds: float = Field(
        default=DEFAULT_AI_TIMEOUT_SECONDS,
        validation_alias=AliasChoices("AI_TIMEOUT_SECONDS", "OPENAI_TIMEOUT_SECONDS"),
    )
    ai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")

    @field_validator("ai_provider", "ai_model", mode="before")
    @classmethod
    def strip_ai_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("ai_provider", mode="after")
    @classmethod
    def ai_provider_fallback(cls, v: str) -> str:
        return v if v else AI_PROVIDER_OPENAI

    @field_validator("ai_model", mode="after")
    @classmethod
    def ai_model_fallback(cls, v: str) -> str:
        return v if v else DEFAULT_AI_MODEL

    @field_validator("ai_api_key", mode="before")
    @classmethod
    def strip_ai_api_key(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
