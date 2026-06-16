"""Holehe — e-postanın hangi servislerde kayıtlı olduğunu tespit eder."""

import asyncio
import json
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


async def run_holehe(email: str, timeout: int = 90) -> list[dict[str, Any]]:
    if not email or "@" not in email:
        return []

    found: list[dict[str, Any]] = []

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "holehe",
            email,
            "--only-used",
            "--no-color",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = (stdout or b"").decode(errors="ignore") + (stderr or b"").decode(errors="ignore")

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            # holehe çıktı: [+] spotify.com veya JSON satırları
            if line.startswith("[+]"):
                service = line[3:].strip().split()[0] if line[3:].strip() else "unknown"
                found.append({
                    "service": service,
                    "detail": "Hesap kayıtlı",
                    "confidence": 0.9,
                    "source": "Holehe",
                })
            try:
                data = json.loads(line)
                if isinstance(data, dict) and data.get("exists"):
                    found.append({
                        "service": data.get("name", data.get("domain", "unknown")),
                        "detail": "Hesap kayıtlı",
                        "confidence": 0.9,
                        "source": "Holehe",
                    })
            except json.JSONDecodeError:
                pass

    except FileNotFoundError:
        logger.debug("Holehe yüklü değil")
    except asyncio.TimeoutError:
        logger.warning("Holehe timeout: %s", email)
    except Exception as e:
        logger.debug("Holehe hatası: %s", e)

    return found
