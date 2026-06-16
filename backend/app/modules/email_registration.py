"""E-posta kayıt tespiti — Holehe (120+ site) + yedek API kontrolleri."""

import asyncio

import httpx

from ..utils.holehe_runner import run_holehe
from .base import BaseModule, FindingResult

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
}


class EmailRegistrationChecker(BaseModule):
    @property
    def module_name(self) -> str:
        return "email_reg"

    async def run(self, inputs: dict) -> list[FindingResult]:
        emails: list[str] = []
        if inputs.get("email"):
            emails.append(inputs["email"])
        emails.extend(inputs.get("discovered_emails", []))
        emails = list(dict.fromkeys(e.lower() for e in emails if e))[:2]

        if not emails:
            return []

        findings: list[FindingResult] = []
        for email in emails:
            holehe_results = await run_holehe(email)
            if holehe_results:
                findings.append(FindingResult(
                    module="email_reg",
                    category="identity",
                    key="registered_services",
                    value=len(holehe_results),
                    confidence=0.92,
                    source="Holehe (120+ site)",
                    raw_data={"services": holehe_results, "email": email},
                ))
                for svc in holehe_results:
                    svc_name = svc["service"].lower().replace(".", "_")
                    findings.append(FindingResult(
                        module="email_reg",
                        category="social",
                        key=f"registered_{svc_name}",
                        value=svc.get("detail", svc["service"]),
                        confidence=svc.get("confidence", 0.9),
                        source=f"Holehe — {svc['service']}",
                    ))
            else:
                findings.extend(await self._fallback_checks(email))
        return findings

    async def _fallback_checks(self, email: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            try:
                r = await client.get(
                    "https://api.github.com/search/users",
                    params={"q": f"{email} in:email"},
                    headers={**HEADERS, "Accept": "application/vnd.github+json"},
                )
                if r.status_code == 200 and r.json().get("total_count", 0) > 0:
                    user = r.json()["items"][0]
                    findings.append(FindingResult(
                        module="email_reg", category="social",
                        key="registered_github", value=user.get("html_url"),
                        confidence=0.95, source="GitHub API",
                    ))
            except Exception:
                pass

            try:
                import hashlib
                h = hashlib.md5(email.lower().encode()).hexdigest()
                r = await client.head(f"https://www.gravatar.com/avatar/{h}?d=404")
                if r.status_code == 200:
                    findings.append(FindingResult(
                        module="email_reg", category="identity",
                        key="registered_gravatar", value=f"https://gravatar.com/{h}",
                        confidence=0.85, source="Gravatar",
                    ))
            except Exception:
                pass
        return findings
