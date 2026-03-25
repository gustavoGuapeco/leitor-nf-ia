from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from app.config.settings import Settings
from app.exceptions import AnalysisValidationError
from app.schemas.analysis import AnalysisDebugPayload, AnalysisResponse, ModelAnalysisOutput
from app.services.procedure_matcher import detect_category, line_matches_category
from app.services.protocol import MultimodalAnalyzer


def _harmonize_public_output(model_out: ModelAnalysisOutput) -> AnalysisResponse:
    """
    Alinha com o legado: aprovado exige ao menos uma linha em procedimentos_encontrados.
    """
    items = list(model_out.procedimentos_encontrados)
    procedimentos_nota = list(model_out.procedimentos_nota) or items
    aprovado = bool(model_out.aprovado) and len(items) > 0
    confidence = float(model_out.confidence)
    if model_out.aprovado and not items:
        confidence = min(confidence, 0.35)
    return AnalysisResponse(
        aprovado=aprovado,
        confidence=confidence,
        procedimentos_encontrados=items,
        procedimentos_nota=procedimentos_nota,
    )


class AnalysisService:
    def __init__(self, analyzer: MultimodalAnalyzer, settings: Settings) -> None:
        self._analyzer = analyzer
        self._settings = settings

    async def analisar(
        self,
        *,
        file_content: bytes,
        mime_type: str,
        procedimento: str,
        include_debug: bool,
        request_id: str | None,
    ) -> dict[str, Any]:
        if not procedimento.strip():
            raise AnalysisValidationError("Procedimento é obrigatório")

        rid = request_id or str(uuid.uuid4())
        t0 = time.perf_counter()

        try:
            raw = await asyncio.to_thread(
                self._analyzer.analyze,
                file_content=file_content,
                mime_type=mime_type,
                procedimento_solicitado=procedimento.strip(),
            )
        except ValueError as e:
            raise AnalysisValidationError(str(e)) from e

        elapsed_ms = (time.perf_counter() - t0) * 1000

        if not isinstance(raw, ModelAnalysisOutput):
            raw = ModelAnalysisOutput.model_validate(raw)

        public = _harmonize_public_output(raw)
        payload: dict[str, Any] = public.model_dump()

        # Refinamento por categorias/keywords: reduz falso positivo
        # e deixa a aprovação alinhada ao conjunto "aprovável".
        category = detect_category(procedimento.strip())
        procedimentos_nota = payload.get("procedimentos_nota", [])
        if category is None:
            payload["aprovado"] = False
            payload["confidence"] = min(float(payload.get("confidence", 0.0)), 0.35)
            payload["procedimentos_encontrados"] = []
        else:
            matched_lines: list[dict[str, Any]] = []
            for item in procedimentos_nota:
                descricao = (item or {}).get("descricao", "")
                if line_matches_category(descricao=descricao, category=category):
                    matched_lines.append(item)
            payload["procedimentos_encontrados"] = matched_lines
            payload["aprovado"] = len(matched_lines) > 0
            if payload["aprovado"]:
                payload["confidence"] = max(float(payload.get("confidence", 0.0)), 0.75)
            else:
                payload["confidence"] = min(float(payload.get("confidence", 0.0)), 0.35)

        if include_debug:
            payload["debug"] = AnalysisDebugPayload(
                modelo=self._settings.openai_model,
                provedor="openai",
                provider_latency_ms=round(elapsed_ms, 2),
                resposta_modelo_truncada=None,
                request_id=rid,
            ).model_dump()

        return payload
