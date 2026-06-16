import time
from collections import defaultdict

from fastapi import Request, HTTPException

from ..config import get_settings

_rate_store: dict[str, list[float]] = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    if not request.url.path.startswith("/api/analysis/start"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    settings = get_settings()
    now = time.time()
    window = settings.rate_limit_window_seconds

    _rate_store[client_ip] = [
        t for t in _rate_store[client_ip] if now - t < window
    ]

    if len(_rate_store[client_ip]) >= settings.rate_limit_max:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit aşıldı. {window // 60} dakikada en fazla {settings.rate_limit_max} analiz.",
        )

    _rate_store[client_ip].append(now)
    return await call_next(request)
