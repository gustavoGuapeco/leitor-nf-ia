"""Constantes do provedor de IA (identificadores, defaults e tuning numérico)."""

from __future__ import annotations

# --- Identificadores de provedor (valores estáveis da API / debug) ---
AI_PROVIDER_OPENAI = "openai"

# --- Variáveis de ambiente (documentação / mensagens; a chave continua OPENAI_API_KEY) ---
ENV_OPENAI_API_KEY = "OPENAI_API_KEY"

# --- Defaults alinhados ao .env.example (quando o env não define) ---
DEFAULT_AI_MODEL = "gpt-4.1-mini"
DEFAULT_AI_TIMEOUT_SECONDS = 120.0

# --- Cliente OpenAI (adapter) ---
OPENAI_DEFAULT_TEMPERATURE = 0.2
OPENAI_CLIENT_MAX_RETRIES = 0

# --- Harmonização pós-modelo (analysis_service) ---
ANALYSIS_CONFIDENCE_CAP_WHEN_UNCERTAIN = 0.35
ANALYSIS_CONFIDENCE_FLOOR_WHEN_APPROVED = 0.75

# --- Debug: truncagem da resposta bruta ---
ANALYSIS_DEBUG_TRUNCATE_MAX_LEN = 2000
