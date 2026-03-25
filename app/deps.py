from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException

from app.config.settings import Settings, get_settings
from app.services.analysis_service import AnalysisService
from app.services.openai_analyzer import OpenAIMultimodalAnalyzer
from app.services.protocol import MultimodalAnalyzer


def get_settings_dep() -> Settings:
    return get_settings()


def get_analyzer(settings: Annotated[Settings, Depends(get_settings_dep)]) -> MultimodalAnalyzer:
    if not settings.openai_api_key.strip():
        raise HTTPException(
            status_code=503,
            detail="Serviço de análise indisponível: defina OPENAI_API_KEY no ambiente.",
        )
    return OpenAIMultimodalAnalyzer(settings)


def get_analysis_service(
    settings: Annotated[Settings, Depends(get_settings_dep)],
    analyzer: Annotated[MultimodalAnalyzer, Depends(get_analyzer)],
) -> AnalysisService:
    return AnalysisService(analyzer=analyzer, settings=settings)
