"""Açık kaynaklarda kullanıcı adı/e-posta araması — GitHub, paste siteleri."""

import httpx

from .base import BaseModule, FindingResult

HEADERS = {"User-Agent": "YASINT/1.0", "Accept": "application/json"}


class PasteSearcher(BaseModule):
    @property
    def module_name(self) -> str:
        return "paste"

    async def run(self, inputs: dict) -> list[FindingResult]:
        queries: list[str] = []
        if inputs.get("username"):
            queries.append(inputs["username"].strip().lstrip("@"))
        if inputs.get("email"):
            queries.append(inputs["email"])
        for e in inputs.get("discovered_emails", [])[:2]:
            queries.append(e)

        if not queries:
            return []

        findings: list[FindingResult] = []
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            for q in list(dict.fromkeys(queries))[:3]:
                findings.extend(await self._github_code_search(client, q))
                findings.extend(await self._grep_app_search(client, q))
        return findings

    async def _github_code_search(self, client: httpx.AsyncClient, query: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        try:
            r = await client.get(
                "https://api.github.com/search/code",
                params={"q": f'"{query}"', "per_page": 5},
            )
            if r.status_code == 200:
                data = r.json()
                total = data.get("total_count", 0)
                if total > 0:
                    findings.append(
                        FindingResult(
                            module="paste",
                            category="identity",
                            key="github_code_exposure",
                            value=total,
                            confidence=0.9,
                            source="GitHub Code Search",
                            raw_data={
                                "matches": [
                                    {
                                        "repo": item.get("repository", {}).get("full_name"),
                                        "path": item.get("path"),
                                        "url": item.get("html_url"),
                                    }
                                    for item in data.get("items", [])[:5]
                                ]
                            },
                        )
                    )
                    for item in data.get("items", [])[:3]:
                        findings.append(
                            FindingResult(
                                module="paste",
                                category="timeline",
                                key="code_leak",
                                value=item.get("html_url"),
                                confidence=0.85,
                                source="GitHub — açık kodda geçiyor",
                            )
                        )
            elif r.status_code == 403:
                findings.append(
                    FindingResult(
                        module="paste",
                        category="identity",
                        key="github_rate_limit",
                        value="GitHub API limiti — daha sonra tekrar deneyin",
                        confidence=0.3,
                        source="GitHub",
                    )
                )
        except Exception:
            pass
        return findings

    async def _grep_app_search(self, client: httpx.AsyncClient, query: str) -> list[FindingResult]:
        """grep.app — public GitHub grep."""
        findings: list[FindingResult] = []
        try:
            r = await client.get(
                f"https://grep.app/api/search",
                params={"q": query, "regexp": "false"},
            )
            if r.status_code == 200:
                data = r.json()
                hits = data.get("hits", {}).get("hits", [])
                if hits:
                    findings.append(
                        FindingResult(
                            module="paste",
                            category="identity",
                            key="public_code_mentions",
                            value=len(hits),
                            confidence=0.8,
                            source="grep.app",
                            raw_data={
                                "hits": [
                                    {
                                        "repo": h.get("repo", {}).get("raw"),
                                        "path": h.get("path", {}).get("raw"),
                                    }
                                    for h in hits[:5]
                                ]
                            },
                        )
                    )
        except Exception:
            pass
        return findings
