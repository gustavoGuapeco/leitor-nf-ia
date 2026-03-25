from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile

from app.deps import get_analysis_service
from app.services.analysis_service import AnalysisService
from app.services.mime import guess_mime_type

router = APIRouter(tags=["análise"])

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _validate_upload(filename: str, content: bytes) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Formato não permitido. Use: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE_MB} MB",
        )


@router.post("/analisar")
async def analisar(
    request: Request,
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    procedimento: Annotated[str, Form(description="Procedimento a ser verificado na nota")],
    arquivo: Annotated[UploadFile, File(description="Nota fiscal (PDF ou imagem)")],
    debug: Annotated[bool, Query(description="Incluir informações de debug na resposta")] = False,
) -> dict[str, Any]:
    """
    Analisa a nota fiscal e verifica se o procedimento informado consta na nota.
    """
    if not arquivo.filename:
        raise HTTPException(status_code=422, detail="Arquivo é obrigatório")

    content = await arquivo.read()
    _validate_upload(arquivo.filename, content)

    mime = guess_mime_type(arquivo.filename, arquivo.content_type)
    if mime == "application/octet-stream":
        raise HTTPException(
            status_code=422,
            detail="Não foi possível determinar o tipo do arquivo. Use PDF ou imagem comum.",
        )

    rid = getattr(request.state, "request_id", None)

    return await service.analisar(
        file_content=content,
        mime_type=mime,
        procedimento=procedimento,
        include_debug=debug,
        request_id=rid,
    )
