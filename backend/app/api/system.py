"""Sistem araçlarının kurulu olup olmadığını kontrol eder."""

import asyncio
import shutil
import subprocess
import sys

import httpx

from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/tools")
async def check_tools():
    """Hangi OSINT araçlarının hazır olduğunu gösterir."""
    results: dict = {"python": sys.version, "tools": {}}

    # Sistem araçları
    for name, cmd in [("nmap", ["nmap", "--version"]), ("exiftool", ["exiftool", "-ver"])]:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            results["tools"][name] = {
                "installed": proc.returncode == 0,
                "version": (proc.stdout or proc.stderr).strip().split("\n")[0][:80],
            }
        except FileNotFoundError:
            results["tools"][name] = {"installed": False, "version": None}

    # Python paketleri (hafif import)
    packages = ["httpx", "anthropic", "dns", "bs4", "reportlab", "celery", "redis", "PIL"]
    for pkg in packages:
        try:
            __import__(pkg)
            results["tools"][pkg] = {"installed": True}
        except ImportError:
            results["tools"][pkg] = {"installed": False}

    for heavy in ["deepface", "cv2"]:
        try:
            __import__(heavy)
            results["tools"][heavy] = {"installed": True}
        except ImportError:
            results["tools"][heavy] = {"installed": False, "note": "opsiyonel — yüz analizi için"}

    # OSINT CLI araçları
    for tool, cmd in [
        ("maigret", [sys.executable, "-m", "maigret", "--help"]),
        ("holehe", [sys.executable, "-m", "holehe", "--help"]),
        ("sherlock", [sys.executable, "-m", "sherlock", "--help"]),
        ("phonenumbers", [sys.executable, "-c", "import phonenumbers"]),
    ]:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            results["tools"][tool] = {"installed": proc.returncode == 0}
        except Exception:
            results["tools"][tool] = {"installed": False}

    # Platform taraması canlı test
    try:
        from ..utils.platform_checker import scan_username
        test = await scan_username("torvalds")  # Bilinen GitHub hesabı
        results["tools"]["platform_scanner"] = {
            "installed": True,
            "self_test": f"torvalds → {len(test)} doğrulanmış platform",
            "working": any(p["platform"] == "GitHub" for p in test),
        }
    except Exception as e:
        results["tools"]["platform_scanner"] = {"installed": False, "error": str(e)}

    # Dış API erişimi
    apis = {}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get("https://api.github.com/zen")
            apis["github_api"] = r.status_code == 200
            r2 = await client.get("https://api.github.com/users/torvalds")
            apis["github_users_api"] = r2.status_code == 200
            r3 = await client.get("https://decapi.me/twitch/username/torvalds")
            apis["decapi_twitch"] = r3.status_code == 200
    except Exception:
        pass
    results["external_apis"] = apis

    installed_count = sum(1 for t in results["tools"].values() if t.get("installed"))
    results["summary"] = {
        "installed": installed_count,
        "total": len(results["tools"]),
        "platform_scanner_accurate": results["tools"].get("platform_scanner", {}).get("working", False),
    }

    return results
