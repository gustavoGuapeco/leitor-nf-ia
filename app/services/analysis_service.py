from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from app.config.ai_constants import (
    ANALYSIS_CONFIDENCE_CAP_WHEN_UNCERTAIN,
    ANALYSIS_CONFIDENCE_FLOOR_WHEN_APPROVED,
)
from app.config.settings import Settings
from app.exceptions import AnalysisValidationError
from app.schemas.analysis import (
    AnalysisDebugPayload,
    AnalysisResponse,
    AnalyzerRunResult,
    ModelAnalysisOutput,
)
from app.services.procedure_matcher import detect_category, line_matches_category
from app.services.protocol import MultimodalAnalyzer


def _harmonize_public_output(model_out: ModelAnalysisOutput) -> AnalysisResponse:
    """
    Alinha com o legado: aprovado exige ao menos uma linha em procedimentos_aprovados
    (derivado do JSON do modelo: procedimentos_encontrados).
    """
    items = list(model_out.procedimentos_encontrados)
    todos = list(model_out.procedimentos_nota) or items
    aprovado = bool(model_out.aprovado) and len(items) > 0
    confidence = float(model_out.confidence)
    if model_out.aprovado and not items:
        confidence = min(confidence, ANALYSIS_CONFIDENCE_CAP_WHEN_UNCERTAIN)
    return AnalysisResponse(
        aprovado=aprovado,
        confidence=confidence,
        procedimentos_aprovados=items,
        todos_procedimentos=todos,
        prestador=model_out.prestador,
        tomador=model_out.tomador,
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
            run = await asyncio.to_thread(
                self._analyzer.analyze,
                file_content=file_content,
                mime_type=mime_type,
                procedimento_solicitado=procedimento.strip(),
                include_debug=include_debug,
            )
        except ValueError as e:
            raise AnalysisValidationError(str(e)) from e

        elapsed_ms = (time.perf_counter() - t0) * 1000

        if isinstance(run, ModelAnalysisOutput):
            run = AnalyzerRunResult(output=run)
        elif not isinstance(run, AnalyzerRunResult):
            run = AnalyzerRunResult.model_validate(run)

        model_out = run.output
        public = _harmonize_public_output(model_out)
        payload: dict[str, Any] = public.model_dump()

        # Refinamento por categorias/keywords: reduz falso positivo
        # e deixa a aprovação alinhada ao conjunto "aprovável".
        category = detect_category(procedimento.strip())
        todos_procedimentos = payload.get("todos_procedimentos", [])
        if category is None:
            payload["aprovado"] = False
            payload["confidence"] = min(
                float(payload.get("confidence", 0.0)),
                ANALYSIS_CONFIDENCE_CAP_WHEN_UNCERTAIN,
            )
            payload["procedimentos_aprovados"] = []
        else:
            matched_lines: list[dict[str, Any]] = []
            for item in todos_procedimentos:
                descricao = (item or {}).get("descricao", "")
                if line_matches_category(descricao=descricao, category=category):
                    matched_lines.append(item)
            payload["procedimentos_aprovados"] = matched_lines
            payload["aprovado"] = len(matched_lines) > 0
            if payload["aprovado"]:
                payload["confidence"] = max(
                    float(payload.get("confidence", 0.0)),
                    ANALYSIS_CONFIDENCE_FLOOR_WHEN_APPROVED,
                )
            else:
                payload["confidence"] = min(
                    float(payload.get("confidence", 0.0)),
                    ANALYSIS_CONFIDENCE_CAP_WHEN_UNCERTAIN,
                )

        if include_debug:
            texto_ocr = model_out.texto_extraido_completo
            payload["debug"] = AnalysisDebugPayload(
                modelo=self._settings.ai_model,
                provedor=self._settings.ai_provider,
                provider_latency_ms=round(elapsed_ms, 2),
                tokens_entrada=run.tokens_entrada,
                tokens_saida=run.tokens_saida,
                tokens_total=run.tokens_total,
                texto_extraido_completo=texto_ocr,
                resposta_modelo_truncada=None,
                request_id=rid,
            ).model_dump()

        return payload
