from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.config.ai_constants import ANALYSIS_DEBUG_TRUNCATE_MAX_LEN


class ProcedimentoLinha(BaseModel):
    descricao: str
    valor: str
    pet: str | None = None


class PartePrestadorNfse(BaseModel):
    """Prestador de serviços (NFS-e): emitente / quem presta o serviço."""

    razao_social: str | None = Field(
        default=None,
        description="Razão social ou nome conforme o documento.",
    )
    nome_fantasia: str | None = Field(default=None, description="Nome fantasia, se houver.")
    cnpj_ou_cpf: str | None = Field(
        default=None,
        description="CNPJ ou CPF como impresso na nota (pode manter pontuação).",
    )
    inscricao_municipal: str | None = None
    municipio: str | None = Field(
        default=None,
        description="Município/UF ou localização cadastral (ex.: SANTO ANDRÉ - SP).",
    )
    endereco: str | None = Field(
        default=None,
        description="Logradouro, número, bairro e CEP como na nota (texto único se vier assim).",
    )
    telefone: str | None = None
    email: str | None = None

    model_config = {"extra": "ignore"}


class ParteTomadorNfse(BaseModel):
    """Tomador / cliente (pessoa física ou jurídica): nome e endereço unificado (inclui cidade)."""

    nome: str | None = Field(
        default=None,
        description="Nome da pessoa ou razão social do cliente conforme a nota.",
    )
    endereco: str | None = Field(
        default=None,
        description="Endereço completo em um texto: logradouro, bairro, CEP e cidade/UF.",
    )
    cnpj_ou_cpf: str | None = Field(
        default=None,
        description="CPF ou CNPJ como impresso na nota (pode manter pontuação).",
    )
    telefone: str | None = None
    email: str | None = None

    model_config = {"extra": "ignore"}


class AnalysisResponse(BaseModel):
    """Contrato público da API."""

    aprovado: bool
    confidence: float = Field(ge=0.0, le=1.0)
    procedimentos_aprovados: list[ProcedimentoLinha]
    todos_procedimentos: list[ProcedimentoLinha]
    prestador: PartePrestadorNfse | None = Field(
        default=None,
        description=(
            "Quem presta o serviço / emite a NFS-e. null se não houver bloco identificável."
        ),
    )
    tomador: ParteTomadorNfse | None = Field(
        default=None,
        description="Cliente / tomador do serviço. null se não houver bloco identificável.",
    )

    model_config = {"extra": "forbid"}


class ModelAnalysisOutput(BaseModel):
    """JSON esperado do modelo (antes de harmonizar com regras de negócio)."""

    aprovado: bool
    confidence: float = Field(ge=0.0, le=1.0)
    procedimentos_encontrados: list[ProcedimentoLinha]
    procedimentos_nota: list[ProcedimentoLinha] = Field(default_factory=list)
    prestador: PartePrestadorNfse | None = None
    tomador: ParteTomadorNfse | None = None
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
