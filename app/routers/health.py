from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, Any]:
    """Status da API e se OPENAI_API_KEY está definida."""
    openai_ready = bool(settings.openai_api_key.strip())
    return {
        "status": "ok",
        "services": {
            "api": "ready",
            "openai": "configured" if openai_ready else "missing_api_key",
        },
    }


@router.get("/ready")
def ready(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, Any]:
    """
    Indica se a API está apta a processar /analisar (OPENAI_API_KEY presente).
    Não chama a API do provedor (evita consumo de quota).
    """
    if not settings.openai_api_key.strip():
        return {"ready": False, "reason": "OPENAI_API_KEY ausente"}
    return {"ready": True}
