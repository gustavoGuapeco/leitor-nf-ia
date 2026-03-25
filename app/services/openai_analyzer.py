from __future__ import annotations

import base64
import logging
from pathlib import Path

import httpx
from openai import OpenAI, RateLimitError

from app.config.ai_constants import (
    OPENAI_CLIENT_MAX_RETRIES,
    OPENAI_DEFAULT_TEMPERATURE,
)
from app.config.settings import Settings
from app.exceptions import AIProviderError, AIRateLimitError, AITimeoutError
from app.schemas.analysis import ModelAnalysisOutput
from app.services.json_extract import extract_json_object

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "analisar_nf.md"


def _load_system_prompt() -> str:
    if not _PROMPT_PATH.is_file():
        msg = f"Arquivo de prompt não encontrado: {_PROMPT_PATH}"
        raise RuntimeError(msg)
    return _PROMPT_PATH.read_text(encoding="utf-8")


class OpenAIMultimodalAnalyzer:
    """Adapter OpenAI (multimodal) com saída JSON validada."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._system_prompt = _load_system_prompt()
        self._client = OpenAI(
            api_key=settings.ai_api_key,
            timeout=settings.ai_timeout_seconds,
            max_retries=OPENAI_CLIENT_MAX_RETRIES,
        )

    def analyze(
        self,
        *,
        file_content: bytes,
        mime_type: str,
        procedimento_solicitado: str,
    ) -> ModelAnalysisOutput:
        if mime_type == "application/octet-stream":
            msg = "MIME type não suportado ou indeterminado para este provedor de IA."
            raise ValueError(msg)

        user_text = (
            "Procedimento solicitado pelo usuário (texto livre):\n"
            f"{procedimento_solicitado.strip()}\n\n"
            "Analise o documento anexado e responda somente com o JSON exigido nas instruções."
        )
        file_b64 = base64.b64encode(file_content).decode("ascii")
        file_data = f"data:{mime_type};base64,{file_b64}"

        try:
            response = self._client.responses.create(
                model=self._settings.ai_model,
                temperature=OPENAI_DEFAULT_TEMPERATURE,
                text={"format": {"type": "json_object"}},
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": self._system_prompt}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": user_text},
                            {
                                "type": "input_file",
                                "filename": "nota",
                                "file_data": file_data,
                            },
                        ],
                    },
                ],
            )
        except (TimeoutError, httpx.TimeoutException) as e:
            logger.warning("Timeout na chamada ao OpenAI: %s", e)
            raise AITimeoutError(str(e)) from e
        except RateLimitError as e:
            logger.warning("Rate limit/cota na OpenAI: %s", e)
            raise AIRateLimitError(str(e)) from e
        except Exception as e:
            logger.exception("Falha na chamada ao OpenAI")
            raise AIProviderError(str(e)) from e

        raw_text = response.output_text
        if not raw_text:
            msg = "Resposta do OpenAI sem texto utilizável."
            raise AIProviderError(msg)

        try:
            return ModelAnalysisOutput.model_validate_json(raw_text)
        except Exception:
            try:
                data = extract_json_object(raw_text)
                return ModelAnalysisOutput.model_validate(data)
            except Exception as e2:
                logger.warning("JSON do modelo inválido: %s", e2)
                msg = "O modelo retornou JSON em formato inválido."
                raise ValueError(msg) from e2
