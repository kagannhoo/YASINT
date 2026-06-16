"""DuckDuckGo dork araması — kullanıcı adı/e-posta için açık web taraması."""

import re

import httpx
from bs4 import BeautifulSoup

from .base import BaseModule, FindingResult

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


class DorkSearcher(BaseModule):
    @property
    def module_name(self) -> str:
        return "dork"

    async def run(self, inputs: dict) -> list[FindingResult]:
        queries: list[tuple[str, str]] = []

        if inputs.get("username"):
            u = inputs["username"].strip().lstrip("@")
            queries.extend([
                (f'"{u}"', "exact_username"),
                (f'"{u}" site:linkedin.com OR site:instagram.com', "social_dork"),
            ])

        if inputs.get("email"):
            e = inputs["email"]
            queries.append((f'"{e}"', "exact_email"))

        for name_key in ("real_name",):
            for f in inputs.get("all_findings", []):
                if isinstance(f, dict) and f.get("key") == name_key:
                    queries.append((f'"{f.get("value")}"', "real_name_search"))

        if not queries:
            return []

        findings: list[FindingResult] = []
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=HEADERS) as client:
            for q, qtype in queries[:4]:
                results = await self._duckduckgo(client, q)
                if results:
                    findings.append(
                        FindingResult(
                            module="dork",
                            category="identity",
                            key=f"web_results_{qtype}",
                            value=len(results),
                            confidence=0.7,
                            source="DuckDuckGo OSINT dork",
                            raw_data={"query": q, "results": results[:10]},
                        )
                    )
                    for res in results[:5]:
                        findings.append(
                            FindingResult(
                                module="dork",
                                category="social",
                                key="web_mention",
                                value=res["url"],
                                confidence=0.65,
                                source=f"Dork: {res.get('title', '')[:50]}",
                                raw_data=res,
                            )
                        )
        return findings

    async def _duckduckgo(self, client: httpx.AsyncClient, query: str) -> list[dict]:
        try:
            r = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
            )
            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            results: list[dict] = []
            for result in soup.select(".result")[:10]:
                link = result.select_one("a.result__a")
                snippet = result.select_one(".result__snippet")
                if link and link.get("href"):
                    url = link["href"]
                    if "uddg=" in url:
                        m = re.search(r"uddg=([^&]+)", url)
                        if m:
                            from urllib.parse import unquote
                            url = unquote(m.group(1))
                    results.append({
                        "title": link.get_text(strip=True),
                        "url": url,
                        "snippet": snippet.get_text(strip=True) if snippet else "",
                    })
            return results
        except Exception:
            return []
