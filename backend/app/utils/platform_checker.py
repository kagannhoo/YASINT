"""Platform taraması — yalnızca doğrulanmış sonuçlar döner."""

import asyncio
import re
from typing import Any, Callable

import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


async def _api_check(
    client: httpx.AsyncClient,
    platform: str,
    url: str,
    exists_fn: Callable[[httpx.Response], bool],
    profile_fn: Callable[[httpx.Response, str], str | None],
    username: str,
) -> dict[str, Any] | None:
    try:
        r = await client.get(url, headers=HEADERS)
        if exists_fn(r):
            profile = profile_fn(r, username)
            return {
                "platform": platform,
                "url": profile or url,
                "verified": True,
                "confidence": 0.95,
            }
    except Exception:
        pass
    return None


# ── API doğrulamalı platformlar ──────────────────────────────────────────────

def _github_exists(r: httpx.Response) -> bool:
    return r.status_code == 200 and '"login"' in r.text


def _reddit_exists(r: httpx.Response) -> bool:
    if r.status_code != 200:
        return False
    try:
        return r.json().get("data", {}).get("name") is not None
    except Exception:
        return False


def _keybase_exists(r: httpx.Response) -> bool:
    try:
        return r.json().get("status", {}).get("code") == 0
    except Exception:
        return False


def _gitlab_exists(r: httpx.Response) -> bool:
    try:
        data = r.json()
        return isinstance(data, list) and len(data) > 0
    except Exception:
        return False


def _hn_exists(r: httpx.Response) -> bool:
    try:
        data = r.json()
        return data.get("id") is not None
    except Exception:
        return False


def _devto_exists(r: httpx.Response) -> bool:
    try:
        return r.json().get("id") is not None
    except Exception:
        return False


# ── Katı HTML doğrulama (platforma özel) ────────────────────────────────────

def _steam_exists(r: httpx.Response) -> bool:
    if r.status_code != 200:
        return False
    text = r.text
    return (
        "steamID64" in text
        and "The specified profile could not be found" not in text
        and "profile_flagged" not in text
    )


def _telegram_exists(r: httpx.Response) -> bool:
    if r.status_code != 200:
        return False
    text = r.text
    # Gerçek kanal/kullanıcıda tgme_page_extra veya özel başlık var
    if "tgme_page_title" not in text:
        return False
    if "If you have <strong>Telegram</strong>" in text:
        return False
    if 'content="Telegram – a new era of messaging"' in text:
        return False
    return bool(re.search(r'class="tgme_page_title"[^>]*>[\s\S]*?</div>', text))


def _twitch_exists(r: httpx.Response) -> bool:
  # decapi düz metin döner: kullanıcı adı veya hata
    if r.status_code != 200:
        return False
    body = r.text.strip().lower()
    invalid = ("invalid", "not found", "does not exist", "error", "unknown")
    return body and not any(x in body for x in invalid) and len(body) < 50


def _soundcloud_exists(r: httpx.Response) -> bool:
    if r.status_code != 200:
        return False
    text = r.text
    return (
        "We can't find that user" not in text
        and "soundcloud.com" in str(r.url)
        and ("soundcloud://" in text or "profile:username" in text.lower() or 'property="og:url"' in text)
    )


def _linktree_exists(r: httpx.Response) -> bool:
    if r.status_code != 200:
        return False
    text = r.text.lower()
    return "linktr.ee" in text and "page not found" not in text and "404" not in text[:500]


def _gist_exists(r: httpx.Response) -> bool:
    return r.status_code == 200 and '"login"' in r.text


async def scan_username(username: str) -> list[dict[str, Any]]:
    """Sadece doğrulanmış platformları döndürür — sahte pozitif yok."""
    clean = username.strip().lstrip("@").lower()
    if not clean or len(clean) < 2:
        return []

    found: list[dict[str, Any]] = []

    async with httpx.AsyncClient(
        timeout=15,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=8),
    ) as client:
        # API tabanlı — güvenilir
        api_checks = [
            ("GitHub", f"https://api.github.com/users/{clean}", _github_exists,
             lambda r, u: r.json().get("html_url")),
            ("Reddit", f"https://www.reddit.com/user/{clean}/about.json", _reddit_exists,
             lambda r, u: f"https://www.reddit.com/user/{clean}"),
            ("Keybase", f"https://keybase.io/_/api/1.0/user/lookup.json?username={clean}",
             _keybase_exists, lambda r, u: f"https://keybase.io/{clean}"),
            ("GitLab", f"https://gitlab.com/api/v4/users?username={clean}", _gitlab_exists,
             lambda r, u: r.json()[0].get("web_url")),
            ("HackerNews", f"https://hacker-news.firebaseio.com/v0/user/{clean}.json",
             _hn_exists, lambda r, u: f"https://news.ycombinator.com/user?id={clean}"),
            ("Dev.to", f"https://dev.to/api/users/by_username?url={clean}", _devto_exists,
             lambda r, u: f"https://dev.to/{clean}"),
        ]

        api_results = await asyncio.gather(*[
            _api_check(client, p, u, fn, pfn, clean)
            for p, u, fn, pfn in api_checks
        ])
        found.extend(r for r in api_results if r)

        # Katı HTML / özel API
        strict_checks = [
            ("Twitch", f"https://decapi.me/twitch/username/{clean}", _twitch_exists,
             lambda r, u: f"https://www.twitch.tv/{u}"),
            ("Steam", f"https://steamcommunity.com/id/{clean}?xml=1", _steam_exists,
             lambda r, u: f"https://steamcommunity.com/id/{u}"),
            ("Telegram", f"https://t.me/{clean}", _telegram_exists,
             lambda r, u: f"https://t.me/{u}"),
            ("SoundCloud", f"https://soundcloud.com/{clean}", _soundcloud_exists,
             lambda r, u: f"https://soundcloud.com/{u}"),
            ("Linktree", f"https://linktr.ee/{clean}", _linktree_exists,
             lambda r, u: f"https://linktr.ee/{u}"),
        ]

        strict_results = await asyncio.gather(*[
            _api_check(client, p, u, fn, pfn, clean)
            for p, u, fn, pfn in strict_checks
        ])
        found.extend(r for r in strict_results if r)

    # Duplike URL kaldır
    seen: set[str] = set()
    unique = []
    for item in found:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique
