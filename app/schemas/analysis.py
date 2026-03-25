from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProcedimentoLinha(BaseModel):
    descricao: str
    valor: str
    pet: str | None = None


class AnalysisResponse(BaseModel):
    """Contrato público da API (alinhado ao projeto legado)."""

    aprovado: bool
    confidence: float = Field(ge=0.0, le=1.0)
    procedimentos_encontrados: list[ProcedimentoLinha]
    procedimentos_nota: list[ProcedimentoLinha]

    model_config = {"extra": "forbid"}


class ModelAnalysisOutput(BaseModel):
    """JSON esperado do modelo (antes de harmonizar com regras de negócio)."""

    aprovado: bool
    confidence: float = Field(ge=0.0, le=1.0)
    procedimentos_encontrados: list[ProcedimentoLinha]
    procedimentos_nota: list[ProcedimentoLinha] = Field(default_factory=list)
    justificativa_curta: str | None = None

    model_config = {"extra": "ignore"}


class AnalysisDebugPayload(BaseModel):
    """Campos opcionais de debug (sem dados sensíveis completos)."""

    modelo: str | None = None
    provedor: str = "openai"
    provider_latency_ms: float | None = None
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
        max_len = 2000
        if len(v) <= max_len:
            return v
        return v[:max_len] + "… [truncado]"
