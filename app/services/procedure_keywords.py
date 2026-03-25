"""
Dicionários de keywords por categoria de procedimento veterinário.
Usado por `procedure_matcher.detect_category` e por keyword match.

Apenas dados (sem lógica de negócio).
"""

from __future__ import annotations

# Ordem de verificação (primeira categoria que bater vence)
CATEGORY_ORDER = [
    "CONSULTAS",
    "VACINA_RAIVA",
    "VACINA_GIARDIA",
    "VACINA_GRIPE",
    "EXAMES_LABORATORIAIS",
    "EXAMES_IMAGEM",
    "EXAMES_GERAIS",
    "INTERNACAO",
    "CIRURGIA",
    "TELEVET_24H",
]

PROCEDURE_KEYWORDS: dict[str, list[str]] = {
    # Consultas gerais e especialistas em consultório e domicílio
    "CONSULTAS": [
        "consulta",
        "clinica",
        "clínica",
        "veterinaria",
        "veterinária",
        "atendimento",
        "atendimento clinico",
        "atendimento clínico",
        "domicilio",
        "domicílio",
        "especialista",
    ],
    # Vacinas obrigatórias (ex.: raiva / antirrabica / v8 / v10)
    "VACINA_RAIVA": [
        "raiva",
        "antirrabica",
        "antirrábica",
        "antirrabica",
        "antirrabica",
        "vacina",
        "imunizacao",
        "imunização",
        "v8",
        "v10",
        "v3",
        "v4",
        "v5",
        "vacinação",
        "vacinacao",
    ],
    "VACINA_GIARDIA": [
        "giardia",
        "giárdia",
        "giardi",
    ],
    "VACINA_GRIPE": [
        "gripe",
        "influenza",
        "vacinacao gripe",
    ],
    "EXAMES_GERAIS": [
        "exame",
        "análise",
        "analise",
        "laboratorial",
        "laboratoriais",
        "imagem",
        "imagem diagnostica",
    ],
    "EXAMES_LABORATORIAIS": [
        "hemograma",
        "bioquimico",
        "bioquímico",
        "sanguinea",
        "sanguínea",
        "urina",
        "fezes",
        "copro",
        "parasitologico",
        "parasitológico",
        "laboratorial",
        "laboratoriais",
    ],
    "EXAMES_IMAGEM": [
        "raio",
        "radiografia",
        "ultrassom",
        "ultra-som",
        "ecg",
        "eletrocardiograma",
    ],
    "INTERNACAO": [
        "internacao",
        "internação",
        "hospitalizacao",
        "hospitalização",
        "diaria",
        "diária",
        "permanencia",
        "permanência",
    ],
    "CIRURGIA": [
        "cirurgia",
        "cirurgico",
        "cirúrgico",
        "castracao",
        "castração",
        "sutura",
        "tumor",
        "remoção",
        "remocao",
        "ovariohisterectomia",
        "ovario-histerectomia",
    ],
    "TELEVET_24H": [
        "televet",
        "televet",
        "24h",
        "24 h",
        "24horas",
    ],
}
