from __future__ import annotations

from app.services.procedure_matcher import detect_category, line_matches_category


def test_detect_category_consultas_plural_no_pedido() -> None:
    assert detect_category("Consultas") == "CONSULTAS"
    assert detect_category("consultas de rotina") == "CONSULTAS"


def test_line_matches_consulta_veterinaria_com_pedido_consultas() -> None:
    assert line_matches_category(descricao="Consulta veterinária", category="CONSULTAS") is True
    assert line_matches_category(descricao="Consultas e retorno", category="CONSULTAS") is True


def test_exame_exames_flexivel() -> None:
    assert (
        line_matches_category(descricao="Exames laboratoriais", category="EXAMES_LABORATORIAIS")
        is True
    )
    # "exames" casa antes em EXAMES_GERAIS; hemogramas/hemograma cobrem o match flexível.
    assert detect_category("Hemogramas de rotina") == "EXAMES_LABORATORIAIS"
    assert line_matches_category(descricao="Hemogramas", category="EXAMES_LABORATORIAIS") is True


def test_v8_codigo_curto_boundary() -> None:
    assert line_matches_category(descricao="Aplicação V8", category="VACINA_RAIVA") is True
    assert line_matches_category(descricao="Aplicação V80", category="VACINA_RAIVA") is False
