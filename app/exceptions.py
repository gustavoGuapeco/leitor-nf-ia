from __future__ import annotations


class AppError(Exception):
    """Erro base da aplicação."""


class AnalysisValidationError(AppError):
    """Entrada inválida ou resposta do modelo que não passa na validação."""


class AIProviderError(AppError):
    """Falha ao falar com o provedor de IA (rede, quota, 4xx/5xx)."""


class AIRateLimitError(AppError):
    """Cota/rate limit esgotada no provedor de IA."""


class AITimeoutError(AppError):
    """Timeout na chamada ao provedor de IA."""
