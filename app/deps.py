from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException

from app.config.ai_constants import AI_PROVIDER_OPENAI, ENV_OPENAI_API_KEY
from app.config.settings import Settings, get_settings
from app.services.analysis_service import AnalysisService
from app.services.openai_analyzer import OpenAIMultimodalAnalyzer
from app.services.protocol import MultimodalAnalyzer


def get_settings_dep() -> Settings:
    return get_settings()


def get_analyzer(settings: Annotated[Settings, Depends(get_settings_dep)]) -> MultimodalAnalyzer:
    if settings.ai_provider != AI_PROVIDER_OPENAI:
        raise HTTPException(
            status_code=501,
            detail=f"Provedor de IA não suportado: {settings.ai_provider!r}.",
        )
    if not settings.ai_api_key.strip():
        raise HTTPException(
            status_code=503,
            detail=f"Serviço de análise indisponível: defina {ENV_OPENAI_API_KEY} no ambiente.",
        )
    return OpenAIMultimodalAnalyzer(settings)


def get_analysis_service(
    settings: Annotated[Settings, Depends(get_settings_dep)],
    analyzer: Annotated[MultimodalAnalyzer, Depends(get_analyzer)],
) -> AnalysisService:
    return AnalysisService(analyzer=analyzer, settings=settings)
