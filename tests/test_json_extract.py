from __future__ import annotations

import pytest
from app.services.json_extract import extract_json_object


def test_extract_plain_json() -> None:
    data = extract_json_object('{"aprovado": true, "x": 1}')
    assert data["aprovado"] is True
    assert data["x"] == 1


def test_extract_from_markdown_fence() -> None:
    text = """Aqui está:
```json
{"aprovado": false, "confidence": 0.5}
```
fim."""
    data = extract_json_object(text)
    assert data["aprovado"] is False


def test_extract_balanced_inner() -> None:
    text = 'Prefix {"aprovado": true, "nested": {"a": 1}} suffix'
    data = extract_json_object(text)
    assert data["aprovado"] is True
    assert data["nested"]["a"] == 1


def test_empty_raises() -> None:
    with pytest.raises(ValueError, match="vazia"):
        extract_json_object("")
