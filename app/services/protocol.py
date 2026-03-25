from __future__ import annotations

from typing import Protocol

from app.schemas.analysis import ModelAnalysisOutput


class MultimodalAnalyzer(Protocol):
    """Contrato para analisadores multimodais de documentos."""

    def analyze(
        self,
        *,
        file_content: bytes,
        mime_type: str,
        procedimento_solicitado: str,
    ) -> ModelAnalysisOutput: ...
