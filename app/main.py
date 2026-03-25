from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.exceptions import (
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
    AnalysisValidationError,
    AppError,
)
from app.middleware.request_id import RequestIdMiddleware
from app.routers import analysis, health

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        logging.getLogger().setLevel(settings.log_level.upper())
    except ValueError:
        logging.getLogger().setLevel(logging.INFO)
    yield


app = FastAPI(
    title="API Análise NF Veterinária",
    description=(
        "Analisa notas fiscais (PDF/imagem) com OpenAI e verifica se o "
        "procedimento solicitado consta na nota."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.include_router(health.router)
app.include_router(analysis.router)


@app.exception_handler(AnalysisValidationError)
async def analysis_validation_handler(_: Request, exc: AnalysisValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(AIProviderError)
async def provider_handler(_: Request, exc: AIProviderError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": "Falha ao consultar o provedor de IA.", "error": str(exc)},
    )


@app.exception_handler(AIRateLimitError)
async def provider_rate_limit_handler(_: Request, exc: AIRateLimitError) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Cota ou limite de requisições da IA foi atingido.",
            "error": str(exc),
        },
    )


@app.exception_handler(AITimeoutError)
async def provider_timeout_handler(_: Request, exc: AITimeoutError) -> JSONResponse:
    return JSONResponse(
        status_code=504,
        content={"detail": "Tempo esgotado ao consultar o provedor de IA.", "error": str(exc)},
    )


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Erro interno.", "error": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.exception("Erro não tratado request_id=%s", getattr(request.state, "request_id", None))
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno ao processar a solicitação."},
    )
