from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
        # Variável de ambiente vazia (ex.: OPENAI_API_KEY= no IDE) não sobrescreve o ficheiro .env
        env_ignore_empty=True,
        extra="ignore",
    )

    app_env: str = Field(default="development", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", validation_alias="OPENAI_MODEL")
    openai_timeout_seconds: float = Field(default=120.0, validation_alias="OPENAI_TIMEOUT_SECONDS")

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def strip_openai_api_key(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
