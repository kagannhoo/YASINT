import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.analysis import Analysis, Finding, Target
from ..schemas.analysis import (
    AnalysisListItem,
    AnalysisResponse,
    AnalysisStartResponse,
    DashboardStats,
)
from ..tasks.analysis_tasks import run_analysis
from ..utils.file_handler import save_upload
from ..utils.pdf_generator import generate_pdf

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/start", response_model=AnalysisStartResponse)
async def start_analysis(
    images: Optional[List[UploadFile]] = File(None),
    username: Optional[str] = Form(None),
    ip_address: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    target_name: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if not any([images, username, ip_address, email, url, phone]):
        raise HTTPException(
            status_code=400,
            detail="En az bir veri girişi gerekli (fotoğraf, kullanıcı adı, IP, e-posta, telefon veya URL)",
        )

    analysis_id = str(uuid.uuid4())
    inputs: dict = {}

    if images:
        saved_paths = []
        for img in images:
            if img.filename:
                path = save_upload(img, analysis_id)
                saved_paths.append(path)
                target = Target(
                    analysis_id=UUID(analysis_id),
                    data_type="image",
                    value=img.filename,
                    file_path=path,
                )
                db.add(target)
        if saved_paths:
            inputs["images"] = saved_paths

    if username:
        clean_username = username.strip().lstrip("@")
        inputs["username"] = clean_username
        db.add(
            Target(
                analysis_id=UUID(analysis_id),
                data_type="username",
                value=clean_username,
            )
        )

    if ip_address:
        inputs["ip"] = ip_address.strip()
        db.add(
            Target(
                analysis_id=UUID(analysis_id),
                data_type="ip",
                value=ip_address.strip(),
            )
        )

    if email:
        inputs["email"] = email.strip()
        db.add(
            Target(
                analysis_id=UUID(analysis_id),
                data_type="email",
                value=email.strip(),
            )
        )

    if phone:
        inputs["phone"] = phone.strip()
        db.add(
            Target(
                analysis_id=UUID(analysis_id),
                data_type="phone",
                value=phone.strip(),
            )
        )

    if url:
        inputs["url"] = url.strip()
        db.add(
            Target(
                analysis_id=UUID(analysis_id),
                data_type="url",
                value=url.strip(),
            )
        )

    analysis = Analysis(
        id=UUID(analysis_id),
        target_name=target_name,
        notes=notes,
        status="pending",
    )
    db.add(analysis)
    db.commit()

    run_analysis.delay(analysis_id, inputs)

    return AnalysisStartResponse(analysis_id=analysis_id, status="started")


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Analysis.id)).scalar() or 0
    now = datetime.now(timezone.utc)
    this_month = (
        db.query(func.count(Analysis.id))
        .filter(
            extract("month", Analysis.created_at) == now.month,
            extract("year", Analysis.created_at) == now.year,
        )
        .scalar()
        or 0
    )
    avg = db.query(func.avg(Analysis.confidence_score)).scalar() or 0.0
    return DashboardStats(
        total_analyses=total,
        this_month=this_month,
        avg_confidence=float(avg),
    )


@router.get("/history", response_model=list[AnalysisListItem])
async def get_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    try:
        aid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz analiz ID")

    analysis = db.query(Analysis).filter(Analysis.id == aid).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
    return analysis


@router.get("/{analysis_id}/report/pdf")
async def download_report(analysis_id: str):
    from ..config import get_settings

    settings = get_settings()
    pdf_path = os.path.join(settings.reports_dir, f"{analysis_id}.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = generate_pdf(analysis_id)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"yasint_report_{analysis_id[:8]}.pdf",
    )


@router.get("/{analysis_id}/export/json")
async def export_json(analysis_id: str, db: Session = Depends(get_db)):
    try:
        aid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz analiz ID")

    analysis = db.query(Analysis).filter(Analysis.id == aid).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")

    findings = db.query(Finding).filter(Finding.analysis_id == aid).all()
    data = {
        "analysis": {
            "id": str(analysis.id),
            "target_name": analysis.target_name,
            "status": analysis.status,
            "confidence_score": analysis.confidence_score,
            "created_at": analysis.created_at.isoformat(),
        },
        "findings": [
            {
                "module": f.module,
                "category": f.category,
                "key": f.key,
                "value": f.value,
                "confidence": f.confidence,
                "source": f.source,
            }
            for f in findings
        ],
    }
    return JSONResponse(content=data)
