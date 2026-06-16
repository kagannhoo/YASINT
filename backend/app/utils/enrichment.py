"""Bulgulardan yeni araştırma tohumları çıkarır — tek ipucu → zincirleme keşif."""

import json
import re
from typing import Any
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def normalize_username(username: str) -> str:
    return username.strip().lstrip("@").lower()


def _parse_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def extract_seeds(findings: list[dict], current: dict) -> dict:
    """Mevcut bulgulardan ve kullanıcı girdisinden araştırma tohumları topla."""
    emails: set[str] = set()
    usernames: set[str] = set()
    urls: set[str] = set()
    ips: set[str] = set()

    if current.get("email"):
        emails.add(current["email"].strip().lower())
    if current.get("username"):
        usernames.add(normalize_username(current["username"]))
    if current.get("ip"):
        ips.add(current["ip"].strip())
    if current.get("url"):
        urls.add(current["url"].strip())

    for f in findings:
        key = f.get("key", "")
        value = _parse_value(f.get("value"))
        raw = f.get("raw_data") or {}

        if key == "email_found" and isinstance(value, str):
            emails.add(value.lower())
        elif key == "gravatar" and current.get("email"):
            pass  # zaten biliniyor
        elif key.startswith("account_") and isinstance(value, str) and value.startswith("http"):
            urls.add(value)
            _username_from_url(value, usernames)
        elif key == "platforms_found" and isinstance(raw, dict):
            for plat in raw.get("platforms", []):
                url = plat.get("url")
                if url:
                    urls.add(url)
                    _username_from_url(url, usernames)
        elif key in ("reverse_dns", "hostname") and isinstance(value, str):
            if "." in value and not value[0].isdigit():
                urls.add(f"https://{value}")
        elif key == "resolved_ip" and isinstance(value, str):
            ips.add(value)
        elif key == "ip_geolocation" and isinstance(raw, dict):
            host = raw.get("hostname")
            if host:
                urls.add(f"https://{host}")

        if isinstance(value, str):
            for email in EMAIL_RE.findall(value):
                if not email.endswith(".png") and not email.endswith(".jpg"):
                    emails.add(email.lower())

    return {
        "emails": sorted(emails),
        "usernames": sorted(usernames),
        "urls": sorted(urls),
        "ips": sorted(ips),
    }


def _username_from_url(url: str, usernames: set[str]) -> None:
    try:
        path = urlparse(url).path.strip("/")
        if not path:
            return
        parts = path.split("/")
        candidate = parts[0] if parts else ""
        if candidate and len(candidate) > 2 and candidate not in (
            "user", "users", "profile", "in", "channel", "c"
        ):
            usernames.add(candidate.lower())
        elif len(parts) > 1:
            usernames.add(parts[-1].lower())
    except Exception:
        pass


def merge_into_inputs(base: dict, seeds: dict) -> dict:
    """Tohumları modül girdilerine dönüştür."""
    merged = dict(base)

    if seeds["emails"]:
        existing = merged.get("email", "")
        for e in seeds["emails"]:
            if not existing:
                merged["email"] = e
                break
        merged["discovered_emails"] = seeds["emails"]

    if seeds["usernames"]:
        if not merged.get("username") and seeds["usernames"]:
            merged["username"] = seeds["usernames"][0]
        merged["discovered_usernames"] = seeds["usernames"]

    if seeds["urls"]:
        merged["profile_urls"] = seeds["urls"]
        if not merged.get("url") and seeds["urls"]:
            merged["url"] = seeds["urls"][0]

    if seeds["ips"]:
        if not merged.get("ip") and seeds["ips"]:
            merged["ip"] = seeds["ips"][0]
        merged["discovered_ips"] = seeds["ips"]

    return merged


def has_new_seeds(old: dict, new: dict) -> bool:
    """İkinci tur için yeni keşif var mı?"""
    for key in ("discovered_emails", "discovered_usernames", "profile_urls", "discovered_ips"):
        old_vals = set(old.get(key) or [])
        new_vals = set(new.get(key) or [])
        if new_vals - old_vals:
            return True
    if not old.get("email") and new.get("email"):
        return True
    if not old.get("username") and new.get("username"):
        return True
    if not old.get("url") and new.get("url"):
        return True
    if not old.get("ip") and new.get("ip"):
        return True
    return False


def build_discovery_summary(initial: dict, final: dict, seeds: dict) -> dict:
    """Kullanıcıya ne verdi vs ne bulundu özeti."""
    provided = {
        k: v
        for k, v in {
            "username": initial.get("username"),
            "email": initial.get("email"),
            "ip": initial.get("ip"),
            "url": initial.get("url"),
            "photo": bool(initial.get("images")),
        }.items()
        if v
    }

    discovered = {
        "emails": [e for e in seeds.get("emails", []) if e != (initial.get("email") or "").lower()],
        "usernames": [
            u for u in seeds.get("usernames", [])
            if u != normalize_username(initial.get("username") or "")
        ],
        "platform_urls": seeds.get("urls", []),
        "ips": [ip for ip in seeds.get("ips", []) if ip != initial.get("ip")],
    }

    discovered = {k: v for k, v in discovered.items() if v}

    return {
        "you_provided": provided,
        "we_found": discovered,
        "message": _discovery_message(provided, discovered),
    }


def _discovery_message(provided: dict, discovered: dict) -> str:
    parts = []
    if not provided:
        return "Analiz tamamlandı."
    if discovered.get("emails"):
        parts.append(f"{len(discovered['emails'])} e-posta")
    if discovered.get("platform_urls"):
        parts.append(f"{len(discovered['platform_urls'])} sosyal medya profili")
    if discovered.get("usernames"):
        parts.append(f"{len(discovered['usernames'])} kullanıcı adı")
    if discovered.get("ips"):
        parts.append(f"{len(discovered['ips'])} IP adresi")
    if not parts:
        return "Girdiğiniz ipucu doğrulandı; ek açık kaynak bulgusu sınırlı."
    return f"Verdiğiniz ipucundan otomatik keşfedildi: {', '.join(parts)}."
