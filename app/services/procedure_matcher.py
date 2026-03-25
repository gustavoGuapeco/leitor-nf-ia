from __future__ import annotations

import re
import unicodedata

from app.services.procedure_keywords import CATEGORY_ORDER, PROCEDURE_KEYWORDS


def _normalize_text(text: str) -> str:
    # Remove acentos/diacríticos para facilitar matching.
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    # Troca pontuação por espaço para não “colar” palavras.
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _keyword_in_text(*, keyword: str, text_norm: str, keyword_norm: str) -> bool:
    if not keyword_norm:
        return False

    # Quando a keyword tiver espaços, fazemos match por substring.
    if " " in keyword_norm:
        return keyword_norm in text_norm

    # Caso contrário, usamos boundary pra reduzir falsos positivos.
    pattern = r"\b" + re.escape(keyword_norm) + r"\b"
    return re.search(pattern, text_norm) is not None


def detect_category(procedimento: str) -> str | None:
    """
    Detecta a categoria aprovável com base no texto do procedimento solicitado.

    Retorna o ID da categoria (conforme `CATEGORY_ORDER`) ou `None` se não bater em nenhuma.
    """
    proc_norm = _normalize_text(procedimento)
    for category in CATEGORY_ORDER:
        for keyword in PROCEDURE_KEYWORDS.get(category, []):
            kw_norm = _normalize_text(keyword)
            if _keyword_in_text(keyword=keyword, text_norm=proc_norm, keyword_norm=kw_norm):
                return category
    return None


def line_matches_category(*, descricao: str, category: str) -> bool:
    """Retorna True se a linha da nota (descricao) contiver alguma keyword da categoria."""
    if category not in PROCEDURE_KEYWORDS:
        return False
    desc_norm = _normalize_text(descricao)
    for keyword in PROCEDURE_KEYWORDS[category]:
        kw_norm = _normalize_text(keyword)
        if _keyword_in_text(keyword=keyword, text_norm=desc_norm, keyword_norm=kw_norm):
            return True
    return False
