import asyncio

from .base import BaseModule, FindingResult
from ..utils.enrichment import build_discovery_summary, extract_seeds


class EnrichmentModule(BaseModule):
    """Keşif özeti — kullanıcının verdiği vs sistemin bulduğu."""

    @property
    def module_name(self) -> str:
        return "enrich"

    async def run(self, inputs: dict) -> list[FindingResult]:
        findings_list = inputs.get("all_findings", [])
        initial = inputs.get("initial_inputs", {})
        seeds = extract_seeds(findings_list, inputs)

        summary = build_discovery_summary(initial, inputs, seeds)

        results = [
            FindingResult(
                module="enrich",
                category="identity",
                key="discovery_summary",
                value=summary,
                confidence=0.9,
                source="Otomatik korelasyon motoru",
                raw_data=seeds,
            )
        ]

        if summary.get("we_found"):
            for email in summary["we_found"].get("emails", []):
                results.append(
                    FindingResult(
                        module="enrich",
                        category="identity",
                        key="discovered_email",
                        value=email,
                        confidence=0.8,
                        source="Zincirleme keşif",
                    )
                )
            for plat_url in summary["we_found"].get("platform_urls", []):
                results.append(
                    FindingResult(
                        module="enrich",
                        category="social",
                        key="discovered_profile",
                        value=plat_url,
                        confidence=0.85,
                        source="Sherlock → otomatik keşif",
                    )
                )

        return results
