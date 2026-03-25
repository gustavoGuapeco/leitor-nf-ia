from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.config.ai_constants import AI_PROVIDER_OPENAI, ENV_OPENAI_API_KEY
from app.config.settings import Settings, get_settings

router = APIRouter(tags=["health"])


def _ai_configured(settings: Settings) -> bool:
    if settings.ai_provider != AI_PROVIDER_OPENAI:
        return False
    return bool(settings.ai_api_key.strip())


@router.get("/health")
def health(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, Any]:
    """Status da API e se a chave do provedor de IA atual está definida."""
    ai_ok = _ai_configured(settings)
    return {
        "status": "ok",
        "services": {
            "api": "ready",
            "ai": "configured" if ai_ok else "missing_api_key",
        },
        "ai_provider": settings.ai_provider,
    }


@router.get("/ready")
def ready(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, Any]:
    """
    Indica se a API está apta a processar /analisar (configuração local do provedor).
    Não chama a API do provedor (evita consumo de quota).
    """
    if settings.ai_provider != AI_PROVIDER_OPENAI:
        return {
            "ready": False,
            "reason": f"Provedor de IA não suportado: {settings.ai_provider!r}.",
        }
    if not settings.ai_api_key.strip():
        return {"ready": False, "reason": f"{ENV_OPENAI_API_KEY} ausente"}
    return {"ready": True}
