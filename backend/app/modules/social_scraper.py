import re

import httpx
from bs4 import BeautifulSoup

from .base import BaseModule, FindingResult


class SocialScraper(BaseModule):
    """Sosyal medya profil kazıma — bulunan URL'lerden otomatik veri çeker."""

    @property
    def module_name(self) -> str:
        return "social"

    async def run(self, inputs: dict) -> list[FindingResult]:
        username = inputs.get("username")
        url = inputs.get("url")
        profile_urls = inputs.get("profile_urls", [])

        if not username and not url and not profile_urls:
            return []

        findings: list[FindingResult] = []
        seen_urls: set[str] = set()

        if username:
            clean = username.strip().lstrip("@")
            findings.extend(await self._scrape_github(clean))

        for profile_url in profile_urls[:15]:
            if profile_url in seen_urls:
                continue
            seen_urls.add(profile_url)
            findings.extend(await self._scrape_profile(profile_url))

        if url and url not in seen_urls:
            findings.extend(await self._scrape_profile(url))

        return findings

    async def _scrape_github(self, username: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                # GitHub API — HTML kazımaktan çok daha güvenilir
                r = await client.get(
                    f"https://api.github.com/users/{username}",
                    headers={"User-Agent": "YASINT/1.0", "Accept": "application/vnd.github+json"},
                )
                if r.status_code == 200:
                    data = r.json()
                    if data.get("name"):
                        findings.append(FindingResult(
                            module="social", category="identity", key="real_name",
                            value=data["name"], confidence=0.95, source="GitHub API",
                        ))
                    if data.get("bio"):
                        findings.append(FindingResult(
                            module="social", category="identity", key="bio",
                            value=data["bio"], confidence=0.9, source="GitHub API",
                        ))
                    if data.get("location"):
                        findings.append(FindingResult(
                            module="social", category="location", key="location",
                            value=data["location"], confidence=0.8, source="GitHub API",
                        ))
                    if data.get("company"):
                        findings.append(FindingResult(
                            module="social", category="identity", key="company",
                            value=data["company"], confidence=0.85, source="GitHub API",
                        ))
                    if data.get("blog"):
                        findings.append(FindingResult(
                            module="social", category="social", key="website",
                            value=data["blog"], confidence=0.85, source="GitHub API",
                        ))
                    if data.get("twitter_username"):
                        findings.append(FindingResult(
                            module="social", category="social", key="twitter",
                            value=f"https://x.com/{data['twitter_username']}",
                            confidence=0.9, source="GitHub API",
                        ))
                    if data.get("email"):
                        findings.append(FindingResult(
                            module="social", category="identity", key="email_found",
                            value=data["email"], confidence=0.95, source="GitHub API",
                        ))
                    if data.get("avatar_url"):
                        findings.append(FindingResult(
                            module="social", category="identity", key="profile_photo_url",
                            value=data["avatar_url"], confidence=0.9, source="GitHub API",
                        ))
                    return findings

                # Fallback: HTML scrape
                r = await client.get(
                    f"https://github.com/{username}",
                    headers={"User-Agent": "YASINT/1.0"},
                )
                if r.status_code != 200:
                    return findings

                soup = BeautifulSoup(r.text, "html.parser")
                name_el = soup.select_one('[itemprop="name"]')
                bio_el = soup.select_one(".user-profile-bio")
                avatar = soup.select_one(".avatar-user")

                if name_el:
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="real_name",
                            value=name_el.get_text(strip=True),
                            confidence=0.9,
                            source="GitHub (otomatik keşif)",
                        )
                    )
                if bio_el:
                    bio = bio_el.get_text(strip=True)
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="bio",
                            value=bio,
                            confidence=0.85,
                            source="GitHub (otomatik keşif)",
                        )
                    )
                    for link in bio_el.find_all("a", href=True):
                        href = link["href"]
                        if href.startswith("http"):
                            findings.append(
                                FindingResult(
                                    module="social",
                                    category="social",
                                    key="bio_link",
                                    value=href,
                                    confidence=0.8,
                                    source="GitHub bio",
                                )
                            )

                if avatar and avatar.get("src"):
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="profile_photo_url",
                            value=avatar["src"],
                            confidence=0.85,
                            source="GitHub avatar",
                        )
                    )

                for email in set(re.findall(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r.text
                )[:5]):
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="email_found",
                            value=email,
                            confidence=0.75,
                            source="GitHub (otomatik keşif)",
                        )
                    )
        except Exception:
            pass
        return findings

    async def _scrape_profile(self, url: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "YASINT/1.0"})
                if r.status_code != 200:
                    return findings

                soup = BeautifulSoup(r.text, "html.parser")
                domain = url.split("/")[2] if "/" in url else url

                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                if title:
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="page_title",
                            value=title,
                            confidence=0.8,
                            source=f"{domain} (otomatik keşif)",
                        )
                    )

                og_desc = soup.find("meta", property="og:description")
                if og_desc and og_desc.get("content"):
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="profile_description",
                            value=og_desc["content"],
                            confidence=0.75,
                            source=f"{domain} (otomatik keşif)",
                        )
                    )

                og_image = soup.find("meta", property="og:image")
                if og_image and og_image.get("content"):
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="profile_photo_url",
                            value=og_image["content"],
                            confidence=0.7,
                            source=f"{domain} profil fotoğrafı",
                        )
                    )

                for email in set(re.findall(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r.text
                )[:3]):
                    findings.append(
                        FindingResult(
                            module="social",
                            category="identity",
                            key="email_found",
                            value=email,
                            confidence=0.65,
                            source=f"{domain} (otomatik keşif)",
                        )
                    )
        except Exception:
            pass
        return findings
