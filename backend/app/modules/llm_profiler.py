import json

from .base import BaseModule, FindingResult


class LLMProfiler(BaseModule):
    @property
    def module_name(self) -> str:
        return "llm"

    async def run(self, inputs: dict) -> list[FindingResult]:
        all_findings = inputs.get("all_findings", [])
        if not all_findings:
            return []

        discovered = [
            f"{f.get('module', '')}: {f.get('key', '')} = {str(f.get('value', ''))[:100]}"
            for f in all_findings
            if f.get("module") not in ("llm", "enrich")
        ][:15]

        modules_seen = sorted({f.get("module", "") for f in all_findings if f.get("module")})
        high_conf = [f for f in all_findings if (f.get("confidence") or 0) >= 0.8]

        return [
            FindingResult(
                module="llm",
                category="identity",
                key="profile_summary",
                value={
                    "identity_summary": (
                        f"Toplam {len(all_findings)} bulgu, {len(modules_seen)} modülden. "
                        + (
                            "Aşağıdaki bulgular otomatik keşif ile elde edildi."
                            if discovered
                            else "Henüz yeterli bulgu yok."
                        )
                    ),
                    "key_findings": discovered or ["Henüz bulgu yok"],
                    "digital_footprint": ", ".join(discovered[:5]) if discovered else "Veri yok",
                    "confidence_assessment": {
                        "overall": min(0.3 + len(high_conf) * 0.05, 0.85),
                        "location": 0.6 if any(f.get("module") == "geo" for f in all_findings) else 0.0,
                        "identity": 0.7 if discovered else 0.0,
                        "social": 0.75 if any(f.get("module") in ("username", "social") for f in all_findings) else 0.0,
                    },
                    "recommended_next_steps": [
                        "Yüksek güvenli bulguları manuel doğrulayın",
                        "Keşfedilen e-posta ve kullanıcı adlarıyla ikinci tur analiz çalıştırın",
                    ],
                },
                confidence=0.55,
                source="YASINT otomatik özet",
                raw_data={"modules": modules_seen},
            )
        ]
