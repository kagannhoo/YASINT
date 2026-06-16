import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import redis

from ..config import get_settings
from ..database import SessionLocal
from ..models.analysis import Analysis, Finding, Location


def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.from_url(settings.redis_url, decode_responses=True)


def broadcast_update(
    analysis_id: str,
    module: str,
    findings: list[Any],
    error: str | None = None,
    status: str = "completed",
) -> None:
    r = get_redis()
    channel = f"analysis:{analysis_id}"

    serialized = []
    for f in findings:
        if hasattr(f, "__dict__"):
            d = f.__dict__.copy()
            if isinstance(d.get("value"), (dict, list)):
                d["value"] = d["value"]
            serialized.append(d)
        elif isinstance(f, dict):
            serialized.append(f)

    message = {
        "event": "module_complete" if not error else "module_error",
        "module": module,
        "status": status,
        "findings_count": len(serialized),
        "findings": serialized,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    r.publish(channel, json.dumps(message, default=str))


def _serialize_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def save_findings(analysis_id: str, findings: list[Any]) -> None:
    db = SessionLocal()
    try:
        for f in findings:
            finding = Finding(
                analysis_id=UUID(analysis_id),
                module=f.module if hasattr(f, "module") else f.get("module"),
                category=f.category if hasattr(f, "category") else f.get("category"),
                key=f.key if hasattr(f, "key") else f.get("key"),
                value=_serialize_value(
                    f.value if hasattr(f, "value") else f.get("value")
                ),
                confidence=f.confidence if hasattr(f, "confidence") else f.get("confidence"),
                source=f.source if hasattr(f, "source") else f.get("source"),
                raw_data=f.raw_data if hasattr(f, "raw_data") else f.get("raw_data"),
            )
            db.add(finding)

            val = f.value if hasattr(f, "value") else f.get("value")
            module = f.module if hasattr(f, "module") else f.get("module")
            key = f.key if hasattr(f, "key") else f.get("key")

            if module in ("exif", "ip") and key in ("gps_coordinates", "ip_geolocation"):
                if isinstance(val, dict) and "lat" in val and "lon" in val:
                    loc = Location(
                        analysis_id=UUID(analysis_id),
                        latitude=float(val["lat"]),
                        longitude=float(val["lon"]),
                        source="exif_gps" if module == "exif" else "ip_geo",
                        confidence=f.confidence if hasattr(f, "confidence") else f.get("confidence"),
                    )
                    db.add(loc)

        db.commit()
    finally:
        db.close()


def mark_analysis_status(
    analysis_id: str,
    status: str,
    confidence_score: float = 0.0,
) -> None:
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == UUID(analysis_id)).first()
        if analysis:
            analysis.status = status
            analysis.confidence_score = confidence_score
            db.commit()
    finally:
        db.close()


def calculate_confidence(findings: list[dict]) -> float:
    if not findings:
        return 0.0
    scores = [f.get("confidence", 0) for f in findings if f.get("confidence")]
    return sum(scores) / len(scores) if scores else 0.0
