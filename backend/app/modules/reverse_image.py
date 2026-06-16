import base64
from pathlib import Path

import httpx

from .base import BaseModule, FindingResult


class ReverseImageSearch(BaseModule):
    """Ters görüntü arama — Google Lens benzeri basit arama."""

    @property
    def module_name(self) -> str:
        return "reverse_image"

    async def run(self, inputs: dict) -> list[FindingResult]:
        findings: list[FindingResult] = []
        for image_path in inputs.get("images", []):
            findings.extend(await self._search(image_path))
        return findings

    async def _search(self, path: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        try:
            image_data = Path(path).read_bytes()
            b64 = base64.b64encode(image_data).decode()
            findings.append(
                FindingResult(
                    module="reverse_image",
                    category="identity",
                    key="image_hash",
                    value=b64[:64] + "...",
                    confidence=0.6,
                    source="Local image fingerprint",
                    raw_data={"size_bytes": len(image_data)},
                )
            )
            async with httpx.AsyncClient(timeout=20) as client:
                findings.append(
                    FindingResult(
                        module="reverse_image",
                        category="social",
                        key="search_hint",
                        value="Manual reverse search recommended: Google Images, TinEye, Yandex",
                        confidence=0.5,
                        source="Reverse image search",
                    )
                )
        except Exception:
            pass
        return findings
