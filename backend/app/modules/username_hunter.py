import asyncio

from ..utils.holehe_runner import run_holehe
from ..utils.maigret_runner import run_maigret
from ..utils.platform_checker import scan_username
from ..utils.username_variants import generate_variants
from .base import BaseModule, FindingResult


class UsernameHunter(BaseModule):
    """Maigret + API doğrulamalı tarama."""

    @property
    def module_name(self) -> str:
        return "username"

    async def run(self, inputs: dict) -> list[FindingResult]:
        username = inputs.get("username", "").strip().lstrip("@")
        if not username:
            return []

        findings: list[FindingResult] = []
        seen_urls: set[str] = set()

        async def add_platform(plat: dict) -> None:
            url = plat.get("url", "")
            if not url or url in seen_urls:
                return
            seen_urls.add(url)
            name = plat["platform"].lower().replace(" ", "_").replace(".", "")
            findings.append(FindingResult(
                module="username",
                category="social",
                key=f"account_{name}",
                value=url,
                confidence=plat.get("confidence", 0.9),
                source=f"✓ {plat.get('source', 'Doğrulandı')} — {plat['platform']}",
            ))

        for variant in generate_variants(username)[:3]:
            for plat in await scan_username(variant):
                await add_platform({**plat, "source": "API"})

        for plat in await run_maigret(username):
            await add_platform(plat)

        if findings:
            accounts = [f for f in findings if f.key.startswith("account_")]
            findings.insert(0, FindingResult(
                module="username",
                category="social",
                key="platforms_found",
                value=len(accounts),
                confidence=0.92,
                source="Maigret + API",
                raw_data={
                    "platforms": [
                        {"platform": f.key.replace("account_", ""), "url": f.value}
                        for f in accounts
                    ]
                },
            ))
        else:
            findings.append(FindingResult(
                module="username",
                category="social",
                key="scan_result",
                value=f"'{username}' için doğrulanmış profil bulunamadı",
                confidence=0.75,
                source="Maigret + API taraması",
            ))

        return findings
