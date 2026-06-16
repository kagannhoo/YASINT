"""Maigret — 3000+ site kullanıcı adı taraması (açık kaynak OSINT)."""

import asyncio
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def run_maigret(username: str, timeout: int = 120) -> list[dict[str, Any]]:
    clean = username.strip().lstrip("@")
    if not clean:
        return []

    found: list[dict[str, Any]] = []

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "maigret",
                clean,
                "--json", "simple",
                "--folderoutput", tmpdir,
                "--top-sites", "80",
                "--timeout", "12",
                "--no-color",
                "--no-progressbar",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                logger.warning("Maigret timeout: %s", username)

            # Maigret çıktı: reports/report_<username>.json veya benzeri
            for json_file in Path(tmpdir).rglob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    found.extend(_parse_maigret_json(data, clean))
                except Exception:
                    continue

            # reports/ klasörü altında txt/csv de olabilir
            for json_file in Path(tmpdir).rglob("report_*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    found.extend(_parse_maigret_json(data, clean))
                except Exception:
                    continue

    except FileNotFoundError:
        logger.debug("Maigret yüklü değil")
    except Exception as e:
        logger.debug("Maigret hatası: %s", e)

    return _dedupe(found)


def _parse_maigret_json(data: Any, username: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    if isinstance(data, dict):
        # { "site_name": { "status": {...}, "url_user": "...", ... } }
        for site, info in data.items():
            if not isinstance(info, dict):
                continue
            status = info.get("status", {})
            if isinstance(status, dict):
                status_val = status.get("status")
            else:
                status_val = str(status)

            url = info.get("url_user") or info.get("url") or ""
            if status_val in ("Claimed", "FOUND", "found", "Available") and url:
                results.append({
                    "platform": site,
                    "url": url,
                    "verified": True,
                    "confidence": 0.88,
                    "source": "Maigret",
                })
            elif info.get("http_status") == 200 and url and "not found" not in str(info).lower():
                # Bazı siteler farklı format
                ids = info.get("ids", {})
                if ids or info.get("status") == "Claimed":
                    results.append({
                        "platform": site,
                        "url": url,
                        "verified": True,
                        "confidence": 0.8,
                        "source": "Maigret",
                    })

    return results


def _dedupe(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for item in items:
        url = item.get("url", "")
        if url and url not in seen:
            seen.add(url)
            out.append(item)
    return out
