from __future__ import annotations

from io import BytesIO

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["services"]["api"] == "ready"


def test_ready_com_chave(client: TestClient) -> None:
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True


def test_analisar_stub_vacina(client: TestClient) -> None:
    files = {"arquivo": ("nota.pdf", BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
    data = {"procedimento": "Aplicar vacina antirrábica"}
    r = client.post("/analisar", files=files, data=data)
    assert r.status_code == 200
    out = r.json()
    assert out["aprovado"] is True
    assert out["confidence"] > 0
    assert len(out["procedimentos_encontrados"]) >= 1
    assert len(out["procedimentos_nota"]) >= len(out["procedimentos_encontrados"])
    assert "pet" in out["procedimentos_nota"][0]


def test_analisar_stub_sem_match(client: TestClient) -> None:
    files = {"arquivo": ("x.png", BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")}
    data = {"procedimento": "consulta simples"}
    r = client.post("/analisar", files=files, data=data)
    assert r.status_code == 200
    out = r.json()
    assert out["aprovado"] is False
    assert len(out["procedimentos_nota"]) >= 1
    assert "pet" in out["procedimentos_nota"][0]


def test_analisar_arquivo_grande(client: TestClient) -> None:
    big = BytesIO(b"x" * (11 * 1024 * 1024))
    files = {"arquivo": ("big.pdf", big, "application/pdf")}
    r = client.post("/analisar", files=files, data={"procedimento": "x"})
    assert r.status_code == 422


def test_analisar_extensao_invalida(client: TestClient) -> None:
    files = {"arquivo": ("a.exe", BytesIO(b"abc"), "application/octet-stream")}
    r = client.post("/analisar", files=files, data={"procedimento": "x"})
    assert r.status_code == 422


def test_request_id_header(client: TestClient) -> None:
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers.get("X-Request-ID") == "abc-123"
