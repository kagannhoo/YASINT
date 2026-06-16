"""Maigret, Holehe, Sherlock, PhoneInfoga CLI sarmalayıcıları."""

import asyncio
import json
import logging
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def _run_cmd(cmd: list[str], timeout: int = 180) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode or 0, stdout.decode(errors="ignore"), stderr.decode(errors="ignore")
    except asyncio.TimeoutError:
        proc.kill()
        return -1, "", "timeout"


async def run_maigret(username: str, timeout: int = 120) -> list[dict[str, Any]]:
    """Maigret — 3000+ sitede kullanıcı adı (OSINT endüstri standardı)."""
    clean = username.strip().lstrip("@")
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        code, stdout, stderr = await _run_cmd(
            [
                sys.executable, "-m", "maigret",
                clean,
                "--json", "simple",
                "--folderoutput", str(out_dir),
                "--timeout", "12",
                "--no-progressbar",
                "--no-color",
            ],
            timeout=timeout,
        )

        # JSON dosyasından oku
        for jf in out_dir.glob("**/*.json"):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    for site, info in data.items():
                        if isinstance(info, dict) and info.get("status") == "Claimed":
                            results.append({
                                "platform": site,
                                "url": info.get("url_user") or info.get("url"),
                                "verified": True,
                                "source": "Maigret",
                                "confidence": 0.9,
                            })
            except Exception as e:
                logger.debug("Maigret JSON parse: %s", e)

        # stdout'tan da dene
        if not results and stdout.strip().startswith("{"):
            try:
                data = json.loads(stdout)
                for site, info in data.items():
                    if isinstance(info, dict) and info.get("status") == "Claimed":
                        results.append({
                            "platform": site,
                            "url": info.get("url_user"),
                            "verified": True,
                            "source": "Maigret",
                            "confidence": 0.9,
                        })
            except json.JSONDecodeError:
                pass

        if code != 0 and not results:
            logger.info("Maigret exit %s: %s", code, stderr[:200])

    return results


async def run_sherlock(username: str, timeout: int = 90) -> list[dict[str, Any]]:
    """Sherlock — klasik username hunter."""
    clean = username.strip().lstrip("@")
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / f"{clean}.json"
        code, _, _ = await _run_cmd(
            [
                sys.executable, "-m", "sherlock",
                clean,
                "--timeout", "10",
                "--json", str(out_file),
                "--folderoutput", tmpdir,
                "--print-found",
            ],
            timeout=timeout,
        )

        target = out_file if out_file.exists() else None
        if not target:
            jsons = list(Path(tmpdir).glob("*.json"))
            target = jsons[0] if jsons else None

        if target and target.exists():
            try:
                data = json.loads(target.read_text())
                for platform, info in data.items():
                    if info.get("status") == "Claimed":
                        results.append({
                            "platform": platform,
                            "url": info.get("url_user"),
                            "verified": True,
                            "source": "Sherlock",
                            "confidence": 0.88,
                        })
            except Exception:
                pass
    return results


async def run_holehe(email: str, timeout: int = 60) -> list[dict[str, Any]]:
    """Holehe — e-postanın kayıtlı olduğu servisler."""
    results: list[dict[str, Any]] = []
    code, stdout, stderr = await _run_cmd(
        [sys.executable, "-m", "holehe", email, "--only-used", "--no-color"],
        timeout=timeout,
    )
    combined = stdout + stderr
    # Holehe çıktısı: [+] site.com veya site.com kullanılıyor
    for line in combined.splitlines():
        line = line.strip()
        if "[+]" in line or "used" in line.lower():
            site = re.sub(r"\[\+\]\s*", "", line).split()[0] if line else ""
            site = site.strip(":,")
            if site and "." in site:
                results.append({
                    "service": site,
                    "email": email,
                    "confidence": 0.88,
                    "source": "Holehe",
                })
    return results


async def run_phoneinfoga(phone: str, timeout: int = 45) -> dict[str, Any]:
    """PhoneInfoga — pasif telefon OSINT."""
    result: dict[str, Any] = {"phone": phone, "findings": []}
    code, stdout, stderr = await _run_cmd(
        ["phoneinfoga", "scan", "-n", phone, "--output", "json"],
        timeout=timeout,
    )
    if not stdout.strip():
        # Eski sürüm düz çıktı
        combined = stdout + stderr
        for line in combined.splitlines():
            if ":" in line:
                result["findings"].append(line.strip())
        return result

    try:
        data = json.loads(stdout)
        result["raw"] = data
    except json.JSONDecodeError:
        result["raw_text"] = stdout[:2000]
    return result


def is_tool_available(module: str) -> bool:
    """Modül import edilebilir mi?"""
    try:
        __import__(module)
        return True
    except ImportError:
        return False
