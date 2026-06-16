from fastapi import APIRouter, UploadFile, File, HTTPException

from ..utils.file_handler import validate_file_size, ALLOWED_EXTENSIONS
from pathlib import Path

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/validate")
async def validate_upload(file: UploadFile = File(...)):
    validate_file_size(file)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen dosya türü: {ext}")
    return {"valid": True, "filename": file.filename, "content_type": file.content_type}
