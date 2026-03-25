from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Extrai um objeto JSON da resposta do modelo.
    Aceita cercas ```json ... ``` ou o primeiro objeto `{...}` balanceado.
    """
    if not text or not text.strip():
        msg = "Resposta do modelo vazia."
        raise ValueError(msg)

    cleaned = text.strip()

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()

    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = _parse_balanced_object(cleaned)

    if not isinstance(parsed, dict):
        msg = "JSON do modelo não é um objeto."
        raise TypeError(msg)
    return parsed


def _parse_balanced_object(s: str) -> Any:
    start = s.find("{")
    if start == -1:
        msg = "Nenhum objeto JSON encontrado na resposta."
        raise ValueError(msg)

    depth = 0
    in_string = False
    escape = False
    quote = ""

    for i in range(start, len(s)):
        ch = s[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_string = False
            continue

        if ch in "\"'":
            in_string = True
            quote = ch
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                chunk = s[start : i + 1]
                return json.loads(chunk)

    msg = "JSON incompleto na resposta do modelo."
    raise ValueError(msg)
