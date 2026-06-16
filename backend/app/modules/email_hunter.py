import re

import httpx

from .base import BaseModule, FindingResult


class EmailHunter(BaseModule):
    """E-posta doğrulama ve gravatar araması."""

    @property
    def module_name(self) -> str:
        return "email"

    async def run(self, inputs: dict) -> list[FindingResult]:
        emails_to_check: list[str] = []
        if inputs.get("email"):
            emails_to_check.append(inputs["email"])
        for e in inputs.get("discovered_emails", []):
            if e not in emails_to_check:
                emails_to_check.append(e)

        findings: list[FindingResult] = []
        for email in emails_to_check[:5]:
            findings.extend(await self._analyze(email))
        return findings

    async def _analyze(self, email: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            findings.append(
                FindingResult(
                    module="email",
                    category="identity",
                    key="validation",
                    value="invalid_format",
                    confidence=0.99,
                    source="Email validation",
                )
            )
            return findings

        domain = email.split("@")[1]
        findings.append(
            FindingResult(
                module="email",
                category="identity",
                key="domain",
                value=domain,
                confidence=0.95,
                source="Email parsing",
            )
        )

        try:
            import hashlib

            hash_val = hashlib.md5(email.lower().encode()).hexdigest()
            gravatar_url = f"https://www.gravatar.com/avatar/{hash_val}?d=404"
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.head(gravatar_url)
                if r.status_code == 200:
                    findings.append(
                        FindingResult(
                            module="email",
                            category="identity",
                            key="gravatar",
                            value=gravatar_url,
                            confidence=0.85,
                            source="Gravatar",
                        )
                    )
        except Exception:
            pass

        return findings
