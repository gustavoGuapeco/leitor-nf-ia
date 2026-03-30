from __future__ import annotations

import os

# Antes de importar a app: chave fictícia para health/ready; /analisar usa stub (override).
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ["OPENAI_API_KEY"] = "test-key-stub-only"

import pytest
from app.config.settings import get_settings
from app.deps import get_analyzer
from app.schemas.analysis import (
    AnalyzerRunResult,
    ModelAnalysisOutput,
    PartePrestadorNfse,
    ProcedimentoLinha,
)
from fastapi.testclient import TestClient


class _StubOpenAIAnalyzer:
    """Substitui o cliente OpenAI nos testes (sem HTTP)."""

    def analyze(
        self,
        *,
        file_content: bytes,
        mime_type: str,
        procedimento_solicitado: str,
        include_debug: bool = False,
    ) -> AnalyzerRunResult:
        _ = (file_content, mime_type)
        proc = procedimento_solicitado.strip().lower()
        if "vacina" in proc:
            out = ModelAnalysisOutput(
                aprovado=True,
                confidence=0.9,
                procedimentos_encontrados=[
                    ProcedimentoLinha(descricao="Vacina antirrábica", valor="R$ 80,00", pet="Zeus"),
                ],
                procedimentos_nota=[
                    ProcedimentoLinha(descricao="Consulta clínica", valor="R$ 150,00", pet="Zeus"),
                    ProcedimentoLinha(descricao="Vacina antirrábica", valor="R$ 80,00", pet="Zeus"),
                ],
                prestador=PartePrestadorNfse(
                    razao_social="CLÍNICA STUB LTDA",
                    cnpj_ou_cpf="00.000.000/0001-00",
                    municipio="SÃO PAULO - SP",
                ),
                tomador=None,
                justificativa_curta="Item de vacina (stub de teste).",
                texto_extraido_completo=(
                    "NOTA STUB\nVacina antirrábica R$ 80,00" if include_debug else None
                ),
            )
            return AnalyzerRunResult(
                output=out,
                tokens_entrada=100 if include_debug else None,
                tokens_saida=50 if include_debug else None,
                tokens_total=150 if include_debug else None,
            )
        out = ModelAnalysisOutput(
            aprovado=False,
            confidence=0.3,
            procedimentos_encontrados=[],
            procedimentos_nota=[
                ProcedimentoLinha(descricao="Banho", valor="R$ 60,00", pet="Aruna"),
                ProcedimentoLinha(descricao="Tosa", valor="R$ 70,00", pet="Aruna"),
            ],
            justificativa_curta="Sem correspondência no stub de teste.",
            texto_extraido_completo="NOTA STUB\nBanho e tosa" if include_debug else None,
        )
        return AnalyzerRunResult(
            output=out,
            tokens_entrada=80 if include_debug else None,
            tokens_saida=40 if include_debug else None,
            tokens_total=120 if include_debug else None,
        )


@pytest.fixture(autouse=True)
def _refresh_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    app.dependency_overrides[get_analyzer] = lambda: _StubOpenAIAnalyzer()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
