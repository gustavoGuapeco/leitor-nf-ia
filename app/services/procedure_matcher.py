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


def _token_matches_keyword(token: str, keyword_norm: str) -> bool:
    """
    Compara token (da nota ou do pedido) com uma keyword, sem igualdade literal rígida.

    Cobre singular/plural simples em PT (ex.: consulta/consultas, exame/exames) e
    pequenas diferenças de sufixo, desde que o radical compartilhado tenha tamanho mínimo
    (evita falso positivo em palavras muito curtas).
    """
    if not token or not keyword_norm:
        return False
    if token == keyword_norm:
        return True

    min_root = 4
    a, b = token, keyword_norm
    if len(a) > len(b):
        a, b = b, a
    # a é o mais curto
    if len(a) < min_root:
        return False
    return bool(b.startswith(a) and len(b) - len(a) <= 2)


def _multi_keyword_parts_match(parts: list[str], tokens: list[str]) -> bool:
    """Partes da frase-chave aparecem em ordem, com match flexível por token."""
    if not parts:
        return True
    first, rest = parts[0], parts[1:]
    for i, tok in enumerate(tokens):
        if _token_matches_keyword(tok, first) and _multi_keyword_parts_match(rest, tokens[i + 1 :]):
            return True
    return False


def _keyword_in_text(*, keyword: str, text_norm: str, keyword_norm: str) -> bool:
    if not keyword_norm:
        return False

    tokens = text_norm.split()

    if " " in keyword_norm:
        if keyword_norm in text_norm:
            return True
        parts = [p for p in keyword_norm.split() if p]
        return _multi_keyword_parts_match(parts, tokens)

    for tok in tokens:
        if _token_matches_keyword(tok, keyword_norm):
            return True

    # Códigos curtos (ex.: v8, 24h): boundary exato sobre o texto inteiro.
    if len(keyword_norm) < 4:
        pattern = r"\b" + re.escape(keyword_norm) + r"\b"
        return re.search(pattern, text_norm) is not None

    return False


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
