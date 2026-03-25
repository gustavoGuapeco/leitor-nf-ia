from __future__ import annotations

import mimetypes
from pathlib import Path


def guess_mime_type(filename: str, upload_content_type: str | None) -> str:
    """Define MIME a partir do content-type do upload ou da extensão."""
    if upload_content_type and upload_content_type not in ("application/octet-stream", ""):
        return upload_content_type.split(";")[0].strip().lower()

    ext = Path(filename).suffix.lower()
    mapping = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    if ext in mapping:
        return mapping[ext]

    guessed, _ = mimetypes.guess_type(filename)
    if guessed:
        return guessed
    return "application/octet-stream"
