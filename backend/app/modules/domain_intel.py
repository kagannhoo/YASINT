"""Alan adı istihbaratı — crt.sh, DNS, WHOIS."""

import asyncio

import httpx

from ..utils.network_scanner import whois_lookup
from .base import BaseModule, FindingResult


class DomainIntel(BaseModule):
    @property
    def module_name(self) -> str:
        return "domain"

    async def run(self, inputs: dict) -> list[FindingResult]:
        domains: set[str] = set()

        for email in [inputs.get("email")] + inputs.get("discovered_emails", []):
            if email and "@" in email:
                domains.add(email.split("@")[1].lower())

        for url in inputs.get("profile_urls", []) + ([inputs.get("url")] if inputs.get("url") else []):
            if url:
                try:
                    from urllib.parse import urlparse
                    host = urlparse(url).netloc
                    if host and "." in host:
                        domains.add(host.replace("www.", ""))
                except Exception:
                    pass

        if not domains:
            return []

        findings: list[FindingResult] = []
        for domain in list(domains)[:3]:
            findings.extend(await self._analyze_domain(domain))
        return findings

    async def _analyze_domain(self, domain: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        crt_task = self._crt_sh(domain)
        dns_task = self._dns_records(domain)
        whois_task = whois_lookup(domain)

        crt, dns, whois_data = await asyncio.gather(crt_task, dns_task, whois_task)

        if crt:
            findings.append(
                FindingResult(
                    module="domain",
                    category="network",
                    key="ssl_certificates",
                    value=len(crt),
                    confidence=0.9,
                    source="crt.sh",
                    raw_data={"subdomains": crt[:30], "domain": domain},
                )
            )
            for sub in crt[:10]:
                if sub != domain:
                    findings.append(
                        FindingResult(
                            module="domain",
                            category="network",
                            key="subdomain",
                            value=sub,
                            confidence=0.85,
                            source="crt.sh (Certificate Transparency)",
                        )
                    )

        if dns:
            findings.append(
                FindingResult(
                    module="domain",
                    category="network",
                    key="dns_records",
                    value=dns,
                    confidence=0.9,
                    source="DNS sorgusu",
                )
            )

        if whois_data:
            findings.append(
                FindingResult(
                    module="domain",
                    category="identity",
                    key="whois",
                    value=whois_data,
                    confidence=0.85,
                    source=f"WHOIS — {domain}",
                )
            )

        return findings

    async def _crt_sh(self, domain: str) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(
                    "https://crt.sh/",
                    params={"q": f"%.{domain}", "output": "json"},
                )
                if r.status_code == 200:
                    data = r.json()
                    names: set[str] = set()
                    for entry in data:
                        for name in entry.get("name_value", "").split("\n"):
                            name = name.strip().lstrip("*.")
                            if name and domain in name:
                                names.add(name)
                    return sorted(names)
        except Exception:
            pass
        return []

    async def _dns_records(self, domain: str) -> dict:
        try:
            import dns.resolver
            records: dict = {}
            for rtype in ["A", "MX", "NS", "TXT"]:
                try:
                    answers = dns.resolver.resolve(domain, rtype)
                    records[rtype] = [str(r) for r in answers][:10]
                except Exception:
                    pass
            return records
        except Exception:
            return {}
