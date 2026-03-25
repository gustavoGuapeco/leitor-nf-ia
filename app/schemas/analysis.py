from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.config.ai_constants import ANALYSIS_DEBUG_TRUNCATE_MAX_LEN


class ProcedimentoLinha(BaseModel):
    descricao: str
    valor: str
    pet: str | None = None


class AnalysisResponse(BaseModel):
    """Contrato público da API."""

    aprovado: bool
    confidence: float = Field(ge=0.0, le=1.0)
    procedimentos_aprovados: list[ProcedimentoLinha]
    todos_procedimentos: list[ProcedimentoLinha]

    model_config = {"extra": "forbid"}


class ModelAnalysisOutput(BaseModel):
    """JSON esperado do modelo (antes de harmonizar com regras de negócio)."""

    aprovado: bool
    confidence: float = Field(ge=0.0, le=1.0)
    procedimentos_encontrados: list[ProcedimentoLinha]
    procedimentos_nota: list[ProcedimentoLinha] = Field(default_factory=list)
    justificativa_curta: str | None = None
    texto_extraido_completo: str | None = Field(
        default=None,
        description="Transcrição completa do documento (pedida só em modo debug).",
    )

    model_config = {"extra": "ignore"}


class AnalysisDebugPayload(BaseModel):
    """Campos opcionais de debug (sem dados sensíveis completos)."""

    modelo: str | None = None
    provedor: str
    provider_latency_ms: float | None = None
    tokens_entrada: int | None = Field(
        default=None,
        description="Tokens de entrada conforme retorno do provedor (ex.: API OpenAI).",
    )
    tokens_saida: int | None = Field(
        default=None,
        description="Tokens de saída conforme retorno do provedor.",
    )
    tokens_total: int | None = Field(
        default=None,
        description="Total de tokens conforme retorno do provedor.",
    )
    texto_extraido_completo: str | None = Field(
        default=None,
        description="Texto integral extraído/transcrito do documento (estilo OCR).",
    )
    resposta_modelo_truncada: str | None = Field(
        default=None,
        description="Trecho da resposta bruta do modelo (truncado).",
    )
    request_id: str | None = None

    model_config = {"extra": "allow"}

    @field_validator("resposta_modelo_truncada", mode="before")
    @classmethod
    def truncate_raw(cls, v: Any) -> Any:
        if v is None or not isinstance(v, str):
            return v
        max_len = ANALYSIS_DEBUG_TRUNCATE_MAX_LEN
        if len(v) <= max_len:
            return v
        return v[:max_len] + "… [truncado]"


class AnalyzerRunResult(BaseModel):
    """Resultado bruto do analisador (modelo + metadados do provedor)."""

    output: ModelAnalysisOutput
    tokens_entrada: int | None = None
    tokens_saida: int | None = None
    tokens_total: int | None = None

    model_config = {"extra": "forbid"}
