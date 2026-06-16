import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ..config import get_settings


def get_upload_dir(analysis_id: str) -> Path:
    settings = get_settings()
    path = Path(settings.upload_dir) / analysis_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_file_size(file: UploadFile) -> None:
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Dosya boyutu {settings.max_upload_size_mb}MB limitini aşıyor",
        )


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


def save_upload(file: UploadFile, analysis_id: str) -> str:
    validate_file_size(file)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen dosya türü: {ext}")

    upload_dir = get_upload_dir(analysis_id)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = upload_dir / safe_name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return str(dest)


def delete_uploads_older_than(hours: int = 24) -> int:
    settings = get_settings()
    upload_root = Path(settings.upload_dir)
    if not upload_root.exists():
        return 0

    import time

    cutoff = time.time() - (hours * 3600)
    deleted = 0
    for item in upload_root.iterdir():
        if item.is_dir() and item.stat().st_mtime < cutoff:
            shutil.rmtree(item, ignore_errors=True)
            deleted += 1
    return deleted
