"""Veri ihlali kontrolü — ücretsiz kaynaklar (XposedOrNot, emailrep.io)."""

import httpx

from .base import BaseModule, FindingResult

USER_AGENT = "YASINT/1.0"


class BreachChecker(BaseModule):
    @property
    def module_name(self) -> str:
        return "breach"

    async def run(self, inputs: dict) -> list[FindingResult]:
        emails: list[str] = []
        if inputs.get("email"):
            emails.append(inputs["email"])
        emails.extend(inputs.get("discovered_emails", []))
        emails = list(dict.fromkeys(e.lower() for e in emails if e))[:3]

        if not emails:
            return []

        findings: list[FindingResult] = []
        for email in emails:
            findings.extend(await self._check_xposedornot(email))
            findings.extend(await self._check_email_rep(email))
        return findings

    async def _check_xposedornot(self, email: str) -> list[FindingResult]:
        """XposedOrNot — ücretsiz, API anahtarı gerektirmez."""
        findings: list[FindingResult] = []
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"https://api.xposedornot.com/v1/check-email/{email}",
                    headers={"User-Agent": USER_AGENT},
                    params={"details": "true"},
                )
                if r.status_code != 200:
                    return findings

                data = r.json()
                if data.get("Error") == "Not found":
                    findings.append(
                        FindingResult(
                            module="breach",
                            category="identity",
                            key="breach_status",
                            value="Bu e-posta XposedOrNot veritabanında ihlal kaydı YOK",
                            confidence=0.9,
                            source="XposedOrNot",
                            raw_data={"email": email},
                        )
                    )
                    return findings

                if data.get("status") != "success":
                    return findings

                raw_breaches = data.get("breaches") or []
                names: list[str] = []
                for item in raw_breaches:
                    if isinstance(item, list):
                        names.extend(str(n) for n in item if n)
                    elif isinstance(item, str):
                        names.append(item)
                names = list(dict.fromkeys(names))

                if not names:
                    return findings

                findings.append(
                    FindingResult(
                        module="breach",
                        category="identity",
                        key="breaches_found",
                        value=len(names),
                        confidence=0.95,
                        source="XposedOrNot",
                        raw_data={"breaches": names[:20], "email": email},
                    )
                )
                for name in names[:5]:
                    findings.append(
                        FindingResult(
                            module="breach",
                            category="timeline",
                            key=f"breach_{name.lower().replace(' ', '_')}",
                            value=name,
                            confidence=0.95,
                            source="XposedOrNot",
                        )
                    )
        except Exception:
            pass
        return findings

    async def _check_email_rep(self, email: str) -> list[FindingResult]:
        """emailrep.io — ücretsiz itibar ve ihlal referans skoru."""
        findings: list[FindingResult] = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://emailrep.io/{email}",
                    headers={"User-Agent": USER_AGENT},
                )
                if r.status_code == 200:
                    data = r.json()
                    findings.append(
                        FindingResult(
                            module="breach",
                            category="identity",
                            key="email_reputation",
                            value={
                                "reputation": data.get("reputation"),
                                "suspicious": data.get("suspicious"),
                                "references": data.get("references", 0),
                                "details": data.get("details", {}),
                            },
                            confidence=0.8,
                            source="emailrep.io",
                            raw_data=data,
                        )
                    )
        except Exception:
            pass
        return findings
