import httpx

from .base import BaseModule, FindingResult


class GeoEstimator(BaseModule):
    """Görsel içerikten konum tahmini (placeholder + basit heuristics)."""

    @property
    def module_name(self) -> str:
        return "geo"

    async def run(self, inputs: dict) -> list[FindingResult]:
        findings: list[FindingResult] = []
        for image_path in inputs.get("images", []):
            findings.extend(await self._estimate(image_path))
        return findings

    async def _estimate(self, path: str) -> list[FindingResult]:
        try:
            from PIL import Image

            with Image.open(path) as img:
                width, height = img.size
                findings = [
                    FindingResult(
                        module="geo",
                        category="location",
                        key="image_dimensions",
                        value=f"{width}x{height}",
                        confidence=0.5,
                        source="Image analysis",
                    )
                ]
                return findings
        except Exception:
            return []
